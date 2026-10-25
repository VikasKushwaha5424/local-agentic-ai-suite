"""
AI Student Helpdesk - Terminal CLI
Course: 24CSEN4121 - Building Agentic AI Systems
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = "qwen2.5"
EMBED_MODEL = "nomic-embed-text"
TOP_K = 3

SYSTEM_PROMPT = (
    "You are the official University Student Helpdesk AI Assistant. "
    "Answer the student's question accurately, politely, and clearly using ONLY the provided official document context. "
    "Format your answers with bullet points and bold headers where appropriate for easy reading. "
    "If the context does not contain the answer, say: "
    "'I cannot find this specific information in the official campus regulations. "
    "Please visit Room 102 (Administrative Block) or contact the Office of Student Affairs for direct assistance.' "
    "Do NOT fabricate, guess, or assume rules not present in the official context."
)

QA_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", (
        "Official Campus Regulations Context:\n"
        "---\n"
        "{context}\n"
        "---\n\n"
        "Student Inquiry: {question}\n\n"
        "Official Answer:"
    )),
])


def init_engine():
    print("[*] Initializing Student Helpdesk offline knowledge engine...")
    Settings.llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, request_timeout=120.0, temperature=0.1)
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    index = load_index_from_storage(storage_context)
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_URL, temperature=0.1)
    qa_chain = QA_TEMPLATE | llm | StrOutputParser()
    print("    [OK] Engine ready.\n")
    return index, qa_chain


def ask(index, qa_chain, question: str):
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    results = retriever.retrieve(question)
    context_parts = []
    for i, item in enumerate(results, 1):
        filename = item.node.metadata.get("file_name", "Campus Document")
        context_parts.append(f"[Excerpt {i} from {filename}]:\n{item.node.text}")
    context_text = "\n\n---\n\n".join(context_parts)
    return qa_chain.invoke({"context": context_text, "question": question}).strip()


def main():
    print("=" * 65)
    print("  AI STUDENT HELPDESK — TERMINAL INTERFACE")
    print("  Course : 24CSEN4121 - Building Agentic AI Systems")
    print("=" * 65 + "\n")
    index, qa_chain = init_engine()
    print("Ask any question regarding campus rules, attendance, or fees (type 'exit' to quit):\n")
    while True:
        try:
            q = input("Student Query > ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Session closed. Good luck with your studies!")
                break
            print("\nSearching campus handbooks...")
            ans = ask(index, qa_chain, q)
            print("\n[Official Answer]:")
            print(ans)
            print("\n" + "-" * 65 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
