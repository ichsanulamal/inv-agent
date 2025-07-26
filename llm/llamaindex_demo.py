import logging
from datetime import datetime
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.llms.openai import OpenAI
from llama_index.llms.google_genai import GoogleGenAI

from llama_index.llms.ollama import Ollama


# from llama_index.llms.anthropic import Anthropic

# === Setup Plaintext Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("blog_debug.log"), logging.StreamHandler()],
)

# === Setup Markdown Logging ===
md_log_path = "blog_insights.md"
with open(md_log_path, "w") as f:
    f.write(
        f"# Blog Insights Report\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )


def log_markdown(question, answer):
    with open(md_log_path, "a") as f:
        f.write(f"### ❓ {question}\n")
        f.write(f"**Answered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("```\n")
        f.write(f"{str(answer)}\n")
        f.write("```\n\n")


def main():
    logging.info("Starting blog loading from Obsidian vault...")

    reader = SimpleDirectoryReader(
        input_dir="/home/al/projects/digital-graveyard/content/Write", recursive=True
    )
    docs = reader.load_data()
    logging.info(f"Loaded {len(docs)} markdown files.")

    parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=100)
    nodes = parser.get_nodes_from_documents(docs)
    logging.info(f"Parsed into {len(nodes)} content chunks.")

    # llm = OpenAI(model="gpt-4")  # or gpt-3.5-turbo
    # llm = Anthropic(model="claude-3-haiku-20240307")
    llm = GoogleGenAI(model="gemini-2.0-flash")
    # llm = Ollama(model="gemma3:1b")

    index = VectorStoreIndex(
        nodes,
        embed_model=HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        ),
    )
    logging.info("Vector index created.")

    index.storage_context.persist("index_storage")

    query_engine = RetrieverQueryEngine.from_args(index.as_retriever(), llm=llm)
    logging.info("Retriever query engine ready.")

    questions = [
        "Summarize the main topics of my blog.",
        "What values or beliefs do I express most often?",
        "How would you describe my writing tone and style?",
        "What themes do I revisit across different posts?",
        "What does my writing say about my view of work and creativity?",
    ]

    for q in questions:
        logging.info(f"✨ Querying: {q}")
        resp = query_engine.query(q)
        log_markdown(q, resp)
        print(f"\n--- Question: {q} ---\n{resp}\n")

    logging.info("All queries complete. Results saved to blog_insights.md.")


if __name__ == "__main__":
    main()
