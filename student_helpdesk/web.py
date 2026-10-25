"""
AI Student Helpdesk - Web Server (Port 8000)
Course: 24CSEN4121 - Building Agentic AI Systems
"""

import os
import sys
import asyncio
import threading
import webbrowser
import urllib.request
from contextlib import asynccontextmanager

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, FileResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
STATIC_DIR = os.path.join(BASE_DIR, "static")

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

helpdesk_index = None
qa_chain = None
init_lock = threading.Lock()


def init_backend():
    global helpdesk_index, qa_chain
    with init_lock:
        if helpdesk_index is not None and qa_chain is not None:
            return
        Settings.llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_URL, request_timeout=120.0, temperature=0.1)
        Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
        llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_URL, temperature=0.1)
        qa_chain = QA_TEMPLATE | llm | StrOutputParser()
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        helpdesk_index = load_index_from_storage(storage_context)


def execute_query(question: str):
    if helpdesk_index is None or qa_chain is None:
        init_backend()
    retriever = helpdesk_index.as_retriever(similarity_top_k=TOP_K)
    results = retriever.retrieve(question)

    context_parts = []
    sources = []
    for i, item in enumerate(results, 1):
        filename = item.node.metadata.get("file_name", "Campus Regulations Document")
        context_parts.append(f"[Excerpt {i} from {filename}]:\n{item.node.text}")
        sources.append({
            "source": filename,
            "score": round(float(item.score), 4) if item.score is not None else 0.85,
            "preview": item.node.text[:220].strip().replace("\n", " ") + "..."
        })

    context_text = "\n\n---\n\n".join(context_parts)
    answer = qa_chain.invoke({"context": context_text, "question": question})
    return {"answer": answer.strip(), "sources": sources}


async def serve_home(request):
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"error": "Frontend static/index.html not found."})


async def get_status(request):
    ollama_ok = False
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                ollama_ok = True
    except Exception:
        ollama_ok = False

    return JSONResponse({
        "status": "online" if ollama_ok else "offline",
        "ollama_connected": ollama_ok,
        "llm_model": LLM_MODEL,
        "embed_model": EMBED_MODEL,
        "index_ready": helpdesk_index is not None,
    })


async def handle_chat(request):
    try:
        body = await request.json()
        query = body.get("message", "").strip()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid payload."}, status_code=400)
    if not query:
        return JSONResponse({"success": False, "error": "Query cannot be empty."}, status_code=400)

    try:
        result = await asyncio.to_thread(execute_query, query)
        return JSONResponse({
            "success": True,
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"],
            "model": LLM_MODEL,
        })
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err), "sources": []}, status_code=500)


@asynccontextmanager
async def lifespan(app):
    asyncio.create_task(asyncio.to_thread(init_backend))
    yield

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
]

routes = [
    Route("/", serve_home, methods=["GET"]),
    Route("/api/status", get_status, methods=["GET"]),
    Route("/api/chat", handle_chat, methods=["POST"]),
]

if os.path.exists(STATIC_DIR):
    routes.append(Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"))

app = Starlette(routes=routes, middleware=middleware, lifespan=lifespan)


def open_browser(port: int):
    import time
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n=======================================================")
    print(f"  AI STUDENT HELPDESK WEB PORTAL")
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
