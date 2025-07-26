import os
import logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
from google.genai import types

# --- Configuration and Setup ---
# Load environment variables from .env file
load_dotenv()

# Setup basic logging to provide more context during execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Environment Variables ---
# Get required environment variables and provide a default or raise an error
# This makes the script fail early if a critical variable is missing.
MODEL_NAME = os.getenv("MODEL")
if not MODEL_NAME:
    logging.error("MODEL environment variable not set. Please check your .env file.")
    raise ValueError("MODEL environment variable is required.")

# Optional: Log the model being used
logging.info(f"Using model: {MODEL_NAME}")

# --- Tool Definitions ---
# Define tool parameters in a clear, separate section
# This improves readability and makes it easier to manage multiple tools.

# Filesystem Tool (MCPToolset)
filesystem_tool_params = StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        # Use a more robust way to specify the path.
        # This prevents issues if the path isn't a directory.
        os.path.abspath(os.getenv("FILESYSTEM_ROOT", "/home/al/Projects")),
    ],
)

# KSEI Tool (MCPToolset)
# Check for required environment variables for the KSEI tool
ksei_env = {
    "KSEI_USERNAME": os.getenv("KSEI_USERNAME"),
    "KSEI_PASSWORD": os.getenv("KSEI_PASSWORD"),
    "KSEI_AUTH_PATH": os.getenv("KSEI_AUTH_PATH")
}

# It's good practice to ensure all necessary env vars are present before creating the tool.
if not all(ksei_env.values()):
    logging.warning("KSEI environment variables are not fully set. KSEI tool may not function correctly.")

ksei_tool_params = StdioConnectionParams(
            server_params=StdioServerParameters(
            command="uvx",
            args=["ksei-mcp"],
            env=ksei_env,
        ),
            timeout=60,
        )


# --- Agent Definition ---
# Define the agent with a clearer, more descriptive instruction set
root_agent = Agent(
    name="file_and_ksei_agent",  # A more descriptive name
    model=MODEL_NAME,
    description="An agent that can perform filesystem operations and interact with the KSEI system.",
    instruction="""
    You are an expert filesystem and KSEI agent. Use the provided tools to fulfill user requests.

    **Instructions for filesystem tasks:**
    - Use the filesystem tool to read, write, and manage files and directories.
    - The root directory for filesystem operations is at '/home/al/Projects'.

    **Instructions for KSEI tasks:**
    - Use the KSEI tool to interact with the KSEI system.
    - This tool can perform actions such as fetching data, logging in, or managing securities.

    **General instructions:**
    - Prioritize using the appropriate tool for the task.
    - If a request involves both filesystem and KSEI actions, use both tools as needed.
    - Always respond concisely and directly, reporting on the status of the requested action.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,  # A temperature of 0 is good for deterministic tool use
    ),
    tools=[
        MCPToolset(connection_params=filesystem_tool_params),
        MCPToolset(connection_params=ksei_tool_params),
    ],
)