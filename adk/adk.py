from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.runners import Runner
from google.adk import Agent

import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)

from google.genai import types

from portfolio_assessment_agent.agent import portfolio_assessment_agent

db_url = "sqlite:///./my_agent_data.db"
session_service_stateful = DatabaseSessionService(db_url=db_url)

import json
with open("/home/al/Projects/inv-agent/puppeteer_instance/ksei/ksei_cleaned.json", "r") as f:
    ksei_cleaned = json.load(f)
with open("/home/al/Projects/inv-agent/puppeteer_instance/debank/debank_cleaned.json", "r") as f:
    debank_cleaned = json.load(f)

combined_portfolio = {"ksei": ksei_cleaned, "debank_cleaned": debank_cleaned}


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        print(
            f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}"
        )

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )

            break

    print(f"<<< Agent Response: {final_response_text}")


async def run_stateful_conversation():
    APP_NAME = "pag_test"
    SESSION_ID_STATEFUL = "session_state_demo_001"
    USER_ID_STATEFUL = "user_state_demo"

    try:
        session_stateful_init = await session_service_stateful.create_session(
            app_name=APP_NAME,
            user_id=USER_ID_STATEFUL,
            session_id=SESSION_ID_STATEFUL,
            state={"portfolio": combined_portfolio},
        )
        print(
            f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'."
        )
    except Exception as e:
        print(f"❌ Error creating session: {e}")

    session_stateful = await session_service_stateful.get_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
    )
    print(f"Session retrieved with state: {session_stateful.state}")

    runner_root_stateful = Runner(
        agent=portfolio_assessment_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )
    await call_agent_async(query= "summarize and roast my portfolio.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # await call_agent_async(
    #     query="suggest improvements to my portfolio for long term growth.",
    #     runner=runner_root_stateful,
    #     user_id=USER_ID_STATEFUL,
    #     session_id=SESSION_ID_STATEFUL,
    # )


if __name__ == "__main__":
    try:
        asyncio.run(run_stateful_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
