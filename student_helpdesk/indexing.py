"""
AI Student Helpdesk - Knowledge Base Indexing
Course: 24CSEN4121 - Building Agentic AI Systems
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DATA_DIR = os.path.join(BASE_DIR, "data")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = "qwen2.5"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def setup_ollama():
    print("[1/3] Configuring local Ollama models...")
    Settings.llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, request_timeout=120.0, temperature=0.1)
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
    Settings.node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    print("      [OK] LLM: qwen2.5 | Embedding: nomic-embed-text\n")


def build_index(force_rebuild=False):
    print("[2/3] Building local vector store...")
    if not force_rebuild and os.path.exists(STORAGE_DIR) and os.path.exists(os.path.join(STORAGE_DIR, "index_store.json")):
        print(f"      - Loading existing index from {STORAGE_DIR}")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        print("      [OK] Index loaded from storage.\n")
        return index

    documents = SimpleDirectoryReader(input_dir=DATA_DIR).load_data()
    print(f"      - Generating embeddings for {len(documents)} document section(s)...")
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=STORAGE_DIR)
    print("      [OK] Index persisted successfully to ./storage.\n")
    return index


def verify_index(index):
    print("[3/3] Running verification retrieval test...")
    query = "What is the attendance requirement and what happens below 65%?"
    print(f'      Query: "{query}"\n')
    retriever = index.as_retriever(similarity_top_k=2)
    nodes = retriever.retrieve(query)
    for i, n in enumerate(nodes, 1):
        print(f"      [Excerpt {i} | Score: {n.score:.4f}]")
        print("      " + n.node.text[:200].replace("\n", " ") + "...\n")
    print("      [OK] Retrieval verified.\n")


if __name__ == "__main__":
    setup_ollama()
    idx = build_index(force_rebuild="--rebuild" in sys.argv)
    verify_index(idx)
