import os
import logging
import google.cloud.logging
from google.adk.tools import exit_loop
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool  # import
from google.adk.tools.crewai_tool import CrewaiTool
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from crewai_tools import FileWriterTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# cloud_logging_client = google.cloud.logging.Client()
# cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)

# model_name = LiteLlm(
#     model="openrouter/google/gemini-2.0-flash-exp:free",
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     api_base="https://openrouter.ai/api/v1",
# )

# Tools


def append_to_state(
    tool_context: ToolContext, field: str, response: str
) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
        field (str): a field name to append to
        response (str): a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")
    return {"status": "success"}


# Agents
critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
    INSTRUCTIONS:
    Consider these questions about the PLOT_OUTLINE:
    - Does it meet a satisfying three-act cinematic structure?
    - Do the characters' struggles seem engaging?
    - Does it feel grounded in a real time period in history?
    - Does it sufficiently incorporate historical details from the RESEARCH?
    If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.

    If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
    Explain your decision and briefly summarize the feedback you have provided.

    PLOT_OUTLINE:
    {{ PLOT_OUTLINE? }}

    RESEARCH:
    {{ research? }}
    """,
    # tools=[append_to_state],
    tools=[append_to_state, exit_loop],
)

file_writer = Agent(
    name="file_writer",
    model=model_name,
    description="Creates marketing details and saves a pitch document.",
    instruction="""
    PLOT_OUTLINE:
    {{ PLOT_OUTLINE? }}

    INSTRUCTIONS:
    - Create a marketable, contemporary movie title suggestion for the movie described in the PLOT_OUTLINE. If a title has been suggested in PLOT_OUTLINE, you can use it, or replace it with a better one.
    - Use your 'file_writer_tool' to create a new txt file with the following arguments:
        - for a file name, use the movie title
        - Write to the "/home/al/Projects/ai-agents-with-langchain-langgraph-udacity" directory
        - If the function takes an 'overwrite' parameter, set it to 'true'. 
        - For the 'content' to write, extract the following from the PLOT_OUTLINE:
            - A logline
            - Synopsis or plot outline
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[
        # CrewaiTool(
        #     name="file_writer_tool",
        #     description=("Writes a file to disk"),
        #     tool=FileWriterTool(),
        # ),
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-filesystem",
                    # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                    # npx process can access.
                    # Replace with a valid absolute path on your system.
                    # For example: "/Users/youruser/accessible_mcp_files"
                    # or use a dynamically constructed absolute path:
                    os.path.abspath(
                        "/home/al/Projects"
                    ),
                ],
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)

screenwriter = Agent(
    name="screenwriter",
    model=model_name,
    description="As a screenwriter, write a logline and plot outline for a biopic about a historical character.",
    instruction="""
    INSTRUCTIONS:
    Your goal is to write a logline and three-act plot outline for an inspiring movie about the historical character(s) described by the PROMPT: {{ PROMPT? }}
    
    - If there is CRITICAL_FEEDBACK, use those thoughts to improve upon the outline.
    - If there is RESEARCH provided, feel free to use details from it, but you are not required to use it all.
    - If there is a PLOT_OUTLINE, improve upon it.
    - Use the 'append_to_state' tool to write your logline and three-act plot outline to the field 'PLOT_OUTLINE'.
    - Summarize what you focused on in this pass.

    PLOT_OUTLINE:
    {{ PLOT_OUTLINE? }}

    RESEARCH:
    {{ research? }}

    CRITICAL_FEEDBACK:
    {{ CRITICAL_FEEDBACK? }}
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[append_to_state],
)

researcher = Agent(
    name="researcher",
    model=model_name,
    description="Answer research questions using Wikipedia.",
    instruction="""
    PROMPT:
    {{ PROMPT? }}
    
    PLOT_OUTLINE:
    {{ PLOT_OUTLINE? }}

    CRITICAL_FEEDBACK:
    {{ CRITICAL_FEEDBACK? }}

    INSTRUCTIONS:
    - If there is a CRITICAL_FEEDBACK, use your wikipedia tool to do research to solve those suggestions
    - If there is a PLOT_OUTLINE, use your wikipedia tool to do research to add more historical detail
    - If these are empty, use your Wikipedia tool to gather facts about the person in the PROMPT
    - Use the 'append_to_state' tool to add your research to the field 'research'.
    - Summarize what you have learned.
    Now, use your Wikipedia tool to do research.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[
        LangchainTool(tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())),
        append_to_state,
    ],
)
writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[researcher, screenwriter, critic],
    max_iterations=2,
)
film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[writers_room, file_writer],
)
root_agent = Agent(
    name="greeter",
    model=model_name,
    description="Guides the user in crafting a movie plot.",
    instruction="""
    - Let the user know you will help them write a pitch for a hit movie. Ask them for   
      a historical figure to create a movie about.
    - When they respond, use the 'append_to_state' tool to store the user's response
      in the 'PROMPT' state key and transfer to the 'film_concept_team' agent
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[append_to_state],
    sub_agents=[film_concept_team],
)
