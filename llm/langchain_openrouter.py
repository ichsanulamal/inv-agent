import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Any
from langgraph.graph.message import add_messages

# -----------------------------------------------------------------------------
# 1. Environment Setup
# -----------------------------------------------------------------------------
# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------------------
# 2. Initialize the OpenRouter Model with LangChain
# -----------------------------------------------------------------------------
# Define the base_url here so you can print it if desired, or just use it in ChatOpenAI
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

llm = ChatOpenAI(
    model="qwen/qwen2.5-vl-32b-instruct:free",
    base_url=os.getenv("OPENROUTER_BASE_URL"),  # Use the defined variable
    api_key=os.getenv("OPENROUTER_API_KEY"),
    # temperature=0.7,  # Adjust temperature as needed
    # max_tokens=256, # Uncomment and adjust if you need to limit response length
)

print(f"Successfully initialized LLM: {llm.model_name} from OpenRouter.")
# The problematic line. We can print the variable used for it instead.
print(f"Using OpenRouter Base URL: {OPENROUTER_BASE_URL}")  # Corrected print statement


# -----------------------------------------------------------------------------
# 3. Define LangGraph State
# -----------------------------------------------------------------------------
class AgentState(TypedDict):
    """
    Represents the state of our graph.
    Messages: A list of messages in the conversation.
    """

    messages: Annotated[list[Any], add_messages]


# -----------------------------------------------------------------------------
# 4. Define Graph Node(s)
# -----------------------------------------------------------------------------
def call_llm_node(state: AgentState):
    """
    Node that calls the LLM with the current messages and adds the AI's response.
    """
    messages = state["messages"]
    print(f"\n--- Calling LLM with messages ---")
    for msg in messages:
        print(f"  {type(msg).__name__}: {msg.content}")

    try:
        response = llm.invoke(messages)
        print(f"--- LLM Response ---")
        print(f"  AI Message: {response.content}")
        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # In a real application, you might want to handle this more gracefully,
        # e.g., by returning an error message or triggering a fallback.
        return {"messages": [AIMessage(content=f"Error: {e}")]}


# -----------------------------------------------------------------------------
# 5. Build and Compile the LangGraph Workflow
# -----------------------------------------------------------------------------
# Build the graph
workflow = StateGraph(AgentState)

# Add the main chatbot node
workflow.add_node("chatbot", call_llm_node)

# Set the entry point to the chatbot node
workflow.set_entry_point("chatbot")

# Set the exit point to the chatbot node (for simple linear flow)
workflow.set_finish_point("chatbot")

# Compile the graph
app = workflow.compile()

print("\nLangGraph workflow compiled successfully.")
print("You can now interact with the 'app' object.")

# -----------------------------------------------------------------------------
# 6. Run your LangGraph Application
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n--- Starting Conversation with Qwen2.5-VL-32B-Instruct ---")

    print("\n[User]: Hello! How are you today?")
    inputs_1 = {"messages": [HumanMessage(content="Hello! How are you today?")]}
    # Using .stream for potential partial responses, though for simple cases .invoke is also fine.
    for s in app.stream(inputs_1):
        # s will be the state dictionary at each step/node output
        if "chatbot" in s:  # Check if the 'chatbot' node's output is present
            last_message = s["chatbot"]["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"[AI]: {last_message.content}")

    # Example 2: Another text query
    print("\n[User]: Can you tell me a fun fact about cats?")
    inputs_2 = {
        "messages": [HumanMessage(content="Can you tell me a fun fact about cats?")]
    }
    for s in app.stream(inputs_2):
        if "chatbot" in s:
            last_message = s["chatbot"]["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"[AI]: {last_message.content}")

    # Example 3: Simulating a multimodal query (Qwen-VL's capability)
    # Important Note for Qwen2.5-VL:
    # While Qwen2.5-VL is multimodal, direct image input via LangChain's ChatOpenAI
    # with OpenRouter might require specific message content formatting
    # (e.g., using {"type": "image_url", "image_url": {"url": "..."}}).
    # The example below demonstrates how you *would* structure it,
    # but verify OpenRouter's current support and LangChain's parsing for image URLs.
    # For now, we'll use a textual prompt that hints at an image description task.

    print("\n--- Interaction with potential image capabilities (Conceptual) ---")
    print(
        "(Note: Direct image input via ChatOpenAI with OpenRouter for Qwen-VL requires specific formatting. "
        "This example uses a text-based prompt for a vision model.)"
    )
    print(
        "\n[User]: Describe what you see in an image depicting a red car parked on a busy city street at night."
    )

    image_conceptual_prompt = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Describe what you see in an image depicting a red car parked on a busy city street at night.",
            },
            # Uncomment and provide a real image URL if OpenRouter/LangChain's ChatOpenAI supports it directly
            # for this model in a simple way.
            # {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Red_car_on_busy_street.jpg/640px-Red_car_on_busy_street.jpg"}}
        ]
    )

    inputs_3 = {"messages": [image_conceptual_prompt]}
    for s in app.stream(inputs_3):
        if "chatbot" in s:
            last_message = s["chatbot"]["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"[AI]: {last_message.content}")

    print("\n--- Conversation End ---")
