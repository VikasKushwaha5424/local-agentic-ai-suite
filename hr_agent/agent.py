"""
HR Policy Agent - Core Logic & Query Triaging
Course: 24CSEN4121 - Building Agentic AI Systems

Workflow: (1) Retrieve → (2) Check → (3) Answer or (4) Escalate
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
TOP_K = 2
RELEVANCE_THRESHOLD = 0.50

CHECK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert HR Policy Triaging Agent. "
        "Analyze whether an employee's inquiry can be answered strictly using ONLY the provided HR policy excerpts.\n"
        "- If routine, clear, and covered: output 'ROUTINE'.\n"
        "- If asking for contract alterations, custom sabbaticals, exceptions, or sensitive matters: output 'ESCALATE'.\n"
        "Reply with ONLY one single word: 'ROUTINE' or 'ESCALATE'."
    )),
    ("human", (
        "Official Policy Excerpts:\n"
        "{context}\n\n"
        "Employee Inquiry: {question}\n\n"
        "Decision:"
    )),
])

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are the official Enterprise HR Policy Assistant. "
        "Answer the employee inquiry accurately and politely using ONLY the provided HR policy context. "
        "Do not invent or extrapolate rules not present in the context."
    )),
    ("human", (
        "Official Context:\n"
        "{context}\n\n"
        "Employee Inquiry: {question}\n\n"
        "Official Answer:"
    )),
])


class HRAgentCore:
    def __init__(self, storage_dir=STORAGE_DIR, ollama_url=OLLAMA_URL):
        self.storage_dir = storage_dir
        self.ollama_url = ollama_url
        self._init_pipeline()

    def _init_pipeline(self):
        print("[Init] Loading HR vector storage from:", self.storage_dir)
        Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=self.ollama_url)
        Settings.llm = Ollama(model=LLM_MODEL, base_url=self.ollama_url, request_timeout=90.0, temperature=0.0)
        storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
        self.index = load_index_from_storage(storage_context)
        self.retriever = self.index.as_retriever(similarity_top_k=TOP_K)

        llm = ChatOllama(model=LLM_MODEL, base_url=self.ollama_url, temperature=0.0)
        self.check_chain = CHECK_PROMPT | llm | StrOutputParser()
        self.answer_chain = ANSWER_PROMPT | llm | StrOutputParser()
        print("       [OK] Agent pipeline ready.\n")

    def process_query(self, query: str) -> dict:
        clean_q = query.strip()
        nodes = self.retriever.retrieve(clean_q)

        context_blocks = []
        sources = []
        max_score = 0.0

        for i, n in enumerate(nodes, 1):
            score = float(n.score) if n.score is not None else 0.5
            if score > max_score:
                max_score = score
            context_blocks.append(f"[Excerpt {i}]:\n{n.node.text.strip()}")
            sources.append({
                "chunk_id": i,
                "score": round(score, 4),
                "text_snippet": n.node.text.strip()[:180].replace("\n", " ") + "..."
            })

        combined_context = "\n\n---\n\n".join(context_blocks)

        if max_score < RELEVANCE_THRESHOLD or not combined_context:
            decision = "ESCALATE"
            reason = "Inquiry topic not covered in standard HR policy documentation."
        else:
            raw_decision = self.check_chain.invoke({"context": combined_context, "question": clean_q}).strip().upper()
            if "ESCALATE" in raw_decision:
                decision = "ESCALATE"
                reason = "Inquiry involves custom exceptions, sabbatical requests, or contract evaluations."
            else:
                decision = "ROUTINE"
                reason = "Directly supported by standard HR policy."

        if decision == "ROUTINE":
            answer = self.answer_chain.invoke({"context": combined_context, "question": clean_q}).strip()
            return {
                "status": "ANSWERED",
                "action": "PROVIDE_ANSWER",
                "query": clean_q,
                "response": answer,
                "escalated": False,
                "sources": sources,
            }
        else:
            escalation_msg = (
                "[ESCALATE_TO_HR: Send to HR Specialist]\n"
                "• Status      : Escalated to People Operations & Employee Relations\n"
                f"• Reason      : {reason}\n"
                f"• Ticket Query: \"{clean_q}\"\n"
                "• Contact     : Email hr-operations@enterprise.corp or visit HR Office (Building B, Room 402)."
            )
            return {
                "status": "ESCALATED",
                "action": "[ESCALATE_TO_HR: Send to HR Specialist]",
                "query": clean_q,
                "response": escalation_msg,
                "escalated": True,
                "sources": sources,
                "reason": reason,
            }


def main():
    print("=" * 65)
    print("  ENTERPRISE HR POLICY AGENT — VERIFICATION TEST")
    print("=" * 65 + "\n")
    agent = HRAgentCore()

    q1 = "How many days of annual leave are available?"
    r1 = agent.process_query(q1)
    print(f"Query 1: {q1}\nAction: {r1['action']}\nResponse:\n{r1['response']}\n")

    q2 = "Can I apply for an extended unpaid sabbatical for personal reasons?"
    r2 = agent.process_query(q2)
    print(f"Query 2: {q2}\nAction: {r2['action']}\nResponse:\n{r2['response']}\n")


if __name__ == "__main__":
    main()
