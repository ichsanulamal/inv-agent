from openai import OpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
llm = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

openai_client = wrap_openai(llm)


def retriever(query: str):
    results = ["Harrison worked at Kensho"]
    return results


@traceable
def rag(question):
    docs = retriever(question)
    system_message = """Answer the users question using only the provided information below:
    
    {docs}""".format(docs="\n".join(docs))

    return openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        model="mistralai/mistral-small-3.2-24b-instruct:free",
    )


rag("where did harrison work")
