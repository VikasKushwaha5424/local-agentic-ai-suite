"""
HR Policy Agent - Web Server (Port 8050)
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

from agent import HRAgentCore, STORAGE_DIR, OLLAMA_URL, LLM_MODEL, EMBED_MODEL
from evaluation import calculate_metrics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

agent_instance = None
init_lock = threading.Lock()


def get_agent():
    global agent_instance
    with init_lock:
        if agent_instance is None:
            agent_instance = HRAgentCore(storage_dir=STORAGE_DIR, ollama_url=OLLAMA_URL)
    return agent_instance


async def serve_home(request):
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"error": "static/index.html not found."}, status_code=404)


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
        "index_ready": os.path.exists(STORAGE_DIR),
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
        agent = get_agent()
        result = await asyncio.to_thread(agent.process_query, query)
        return JSONResponse({
            "success": True,
            "query": query,
            "response": result["response"],
            "escalated": result.get("escalated", False),
            "action": result.get("action", "PROVIDE_ANSWER"),
            "sources": result.get("sources", []),
            "reason": result.get("reason", ""),
            "model": LLM_MODEL,
        })
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err), "escalated": True, "sources": []}, status_code=500)


async def get_metrics(request):
    return JSONResponse(calculate_metrics())


@asynccontextmanager
async def lifespan(app):
    asyncio.create_task(asyncio.to_thread(get_agent))
    yield

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
]

routes = [
    Route("/", serve_home, methods=["GET"]),
    Route("/api/status", get_status, methods=["GET"]),
    Route("/api/chat", handle_chat, methods=["POST"]),
    Route("/api/metrics", get_metrics, methods=["GET"]),
]

if os.path.exists(STATIC_DIR):
    routes.append(Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"))

app = Starlette(routes=routes, middleware=middleware, lifespan=lifespan)


def open_browser(port: int):
    import time
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print(f"\n=======================================================")
    print(f"  ENTERPRISE HR POLICY AGENT WEB PORTAL")
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
