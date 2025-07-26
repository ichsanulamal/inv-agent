import logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

# Configure logging to local file (only once)
logging.basicConfig(
    filename="adk_agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    # ...existing code...
    # Remove cloud_logging_client setup
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts and "text" in llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
            logging.info(
                f"[query to {callback_context.agent_name}]: " + last_user_message
            )


def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    # ...existing code...
    # Remove cloud_logging_client setup
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(
                    f"[response from {callback_context.agent_name}]: " + part.text
                )
            elif part.function_call:
                logging.info(
                    f"[function call from {callback_context.agent_name}]: "
                    + part.function_call.name
                )
