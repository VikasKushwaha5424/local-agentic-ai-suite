"""
HR Policy Agent - Knowledge Base Indexing
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
POLICY_FILE = os.path.join(BASE_DIR, "policy.txt")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen2.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def setup_ollama():
    print("[1/3] Configuring Local Ollama Engine...")
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
    Settings.llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, request_timeout=120.0, temperature=0.1)
    Settings.node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    print("      [OK] Ollama configured.\n")


def build_index(force_rebuild=False):
    print("[2/3] Building Vector Store Index...")
    if not force_rebuild and os.path.exists(STORAGE_DIR) and os.path.exists(os.path.join(STORAGE_DIR, "index_store.json")):
        print(f"      - Loading existing index from {STORAGE_DIR}")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        print("      [OK] Index loaded.\n")
        return index

    reader = SimpleDirectoryReader(input_files=[POLICY_FILE])
    documents = reader.load_data()
    print(f"      - Generating embeddings for {len(documents)} document section(s)...")
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=STORAGE_DIR)
    print("      [OK] Index persisted to ./storage.\n")
    return index


def verify_retrieval(index):
    print("[3/3] Running Retrieval Verification Test...")
    test_query = "Is medical documentation required for sick leave?"
    print(f'      Query: "{test_query}"\n')
    retriever = index.as_retriever(similarity_top_k=2)
    nodes = retriever.retrieve(test_query)
    for i, n in enumerate(nodes, 1):
        print(f"      [Chunk {i} | Score: {n.score:.4f}]")
        print("      " + n.node.text[:200].replace("\n", " ") + "...\n")
    print("      [OK] Retrieval test completed successfully.\n")


if __name__ == "__main__":
    setup_ollama()
    idx = build_index(force_rebuild="--rebuild" in sys.argv)
    verify_retrieval(idx)
