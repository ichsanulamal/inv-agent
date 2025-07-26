from ollama import chat

# stream = chat(
#     model='gemma3:1b',
#     messages=[{'role': 'user', 'content': 'what's the weather?'}],
#     stream=True,
# )

# for chunk in stream:
#   print(chunk['message']['content'], end='', flush=True)


# from ollama import ChatResponse

# response: ChatResponse = chat(model='moondream:latest', messages=[
#   {
#     'role': 'user',
#     'content': 'Why always me?',
#   },
# ])
# print(response['message']['content'])
# print(response.message.content)


# from ollama import Client
# client = Client(
#   host='http://localhost:11434',
#   # headers={'x-some-header': 'some-value'}
# )
# response = client.chat(model='llama3.2:1b', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])


# open ai compatible

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model="llama3.2:1b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
)

return response.choices[0].message.content.strip()
