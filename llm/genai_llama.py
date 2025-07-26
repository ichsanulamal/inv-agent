from llama_index.core.llms import ChatMessage
from llama_index.llms.google_genai import GoogleGenAI

messages = [
    ChatMessage(role="system", content="You are a pirate with a colorful personality"),
    ChatMessage(role="user", content="Tell me a story"),
]
llm = GoogleGenAI(model="gemini-2.0-flash")
resp = llm.chat(messages)

print(resp)
