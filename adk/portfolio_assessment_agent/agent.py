from google.adk import Agent
from google.adk.tools import google_search  # The Google Search tool

import sys

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response

portfolio_assessment_agent = Agent(
    # name: A unique name for the agent.
    name="portfolio_assessment_agent",
    # description: A short description of the agent's purpose, so
    # other agents in a multi-agent system know when to call it.
    description="Assess given investment portfolio.",
    # model: The LLM model that the agent will use:
    model="gemini-2.0-flash-001",
    # instruction: Instructions (or the prompt) for the agent.
    instruction="""
    INSTRUCTIONS:
    Your role is an investment portfolio assessment agent.
    You will receive information about a user's investment portfolio.
    Answer the user's question about their portfolio. Be specific and concise.

    PORTFOLIO:
    {{ portfolio? }}
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    output_key="pa_answer",
    # Add the google_search tool below.
    # tools=[google_search],
)
