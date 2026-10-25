# 🤖 Local Agentic AI Suite

A 100% local, offline, and privacy-first Agentic AI suite running without any API keys or cloud dependencies. Powered by **Ollama**, **LlamaIndex**, and **LangChain**, this repository hosts two full-stack, autonomous intelligent systems with terminal and web-based interfaces:

1. **🎓 University Student Helpdesk** — An intelligent RAG assistant answering academic queries, campus policies, grading rules, and administrative checklists with grounded citations.
2. **🏢 Enterprise HR Policy Agent** — A 4-step multi-stage agent that retrieves policy documents, checks eligibility and sensitive contexts, provides grounded answers, or automatically escalates complex queries to human HR specialists.

---

## 🌟 Key Features

- **🔒 100% Local & Privacy-Preserving**: Runs completely offline using local models via Ollama (`qwen2.5` & `nomic-embed-text`). Zero API costs, zero data leakage.
- **⚡ Two Complete Intelligent Systems**:
  - **Student Helpdesk**: Handles student handbook, academic FAQs, and university regulations.
  - **HR Policy Agent**: Implements a 4-step triaging and escalation workflow (Retrieve → Check → Answer / Escalate).
- **💻 Minimalist & Modern Web Portals**: Responsive glassmorphic web dashboards with live agent telemetry, source inspection, dark mode, and latency monitoring.
- **📊 Built-in Evaluation Engines**: Automated verification suites for both projects calculating factual accuracy, hallucination rates, chained reliability, and cost-benefit analysis.

---

## 🏗️ Architecture

### 1. Student Helpdesk Architecture
```
Student Query 
      ↓
LlamaIndex Retriever (nomic-embed-text) → Top-3 Context Chunks
      ↓
LangChain ChatOllama (qwen2.5) + Grounded System Prompt
      ↓
Response with Source File Citations & Actionable Next Steps
```

### 2. HR Policy Agent 4-Step Workflow
```
Employee Query
      ↓
[Step 1: Retrieve]   Semantic vector search over HR policies (Top-2 chunks)
      ↓
[Step 2: Check]      LLM Triaging: Routine policy check vs. Custom / Sensitive case
      ↓
     ┌───────────────────────┴───────────────────────┐
     ▼                                               ▼
[Step 3: Answer]                               [Step 4: Escalate]
Grounded response generated                    Escalated to human HR specialist
with exact policy clause citations             with structured priority ticket
```

---

## 📁 Repository Structure

```
local-agentic-ai-suite/
│
├── requirements.txt                    # Unified Python dependencies
├── README.md                           # Project documentation
├── STUDENT_HELPDESK_COMPLETE.txt       # Helpdesk full specifications & evaluation
├── HR_POLICY_AGENT_COMPLETE.txt        # HR Agent full specifications & evaluation
│
├── student_helpdesk/
│   ├── cli.py                          # Interactive terminal chatbot
│   ├── web.py                          # Web server portal (Port 8000)
│   ├── indexing.py                     # Vector index builder
│   ├── evaluation.py                   # Automated test suite (4 benchmark tests)
│   ├── run.bat                         # One-click Windows launcher
│   ├── data/                           # Source documents (rules, FAQs, handbook)
│   ├── storage/                        # Persisted local vector store
│   └── static/                         # Web UI (HTML, CSS, JS)
│
└── hr_agent/
    ├── agent.py                        # 4-step agent core logic
    ├── web.py                          # Web server portal (Port 8050)
    ├── indexing.py                     # Vector index builder
    ├── evaluation.py                   # Scenario metrics calculator (Scenarios 1–6)
    ├── run.bat                         # One-click Windows launcher
    ├── policy.txt                      # Official company HR policy document
    ├── storage/                        # Persisted local vector store
    └── static/                         # Web UI (HTML, CSS, JS)
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **Ollama**: Download and install from [ollama.com](https://ollama.com)

Pull the required local models:
```bash
ollama pull qwen2.5
ollama pull nomic-embed-text
```

Ensure the Ollama service is active:
```bash
ollama serve
```

### 2. Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/VikasKushwaha5424/local-agentic-ai-suite.git
cd local-agentic-ai-suite
pip install -r requirements.txt
```

---

## 🖥️ Running the Applications

### 🎓 1. Student Helpdesk (Port 8000)

- **One-Click Launch**: Double-click `student_helpdesk/run.bat`
- **Manual Launch**:
  ```bash
  # Step A: Build vector index (first time only)
  python student_helpdesk/indexing.py

  # Step B: Launch Web Portal
  python student_helpdesk/web.py
  # Access at http://127.0.0.1:8000

  # (Optional) Run CLI Terminal Chatbot
  python student_helpdesk/cli.py

  # (Optional) Run Evaluation Tests
  python student_helpdesk/evaluation.py
  ```

### 🏢 2. HR Policy Agent (Port 8050)

- **One-Click Launch**: Double-click `hr_agent/run.bat`
- **Manual Launch**:
  ```bash
  # Step A: Build vector index (first time only)
  python hr_agent/indexing.py

  # Step B: Launch Web Portal
  python hr_agent/web.py
  # Access at http://127.0.0.1:8050

  # (Optional) Test Core Agent Logic
  python hr_agent/agent.py

  # (Optional) Run Evaluation Scenarios
  python hr_agent/evaluation.py
  ```

---

## 📈 Evaluation & Benchmark Metrics

### HR Policy Agent (Quantitative Scenarios)
| Scenario | Metric Description | Value |
|:---|:---|:---|
| **Scenario 1** | Baseline Task Success Rate | **92.0%** (184/200 queries) |
| **Scenario 2** | Target Success Rate (+6 wins) | **95.0%** (190/200 queries) |
| **Scenario 3** | Factual Hallucination Rate | **3.2%** (8 false claims / 250) |
| **Scenario 4** | Token Processing Cost | **$0.00 Local Ollama** vs. $3.00 Commercial API |
| **Scenario 5** | Multi-Step Chained Reliability | **81.45%** ($0.95^4$) |
| **Scenario 6** | Operational Corrective Action | Target hallucination < 2.0% threshold |

### Student Helpdesk (Evaluation Suite)
- **Keyword Grounding Accuracy**: **100% (4/4 test cases pass)**
- Tests cover: *Bonafide certificate procedures*, *Library timings & borrowing rules*, *Attendance debarment criteria*, and *Grading / CGPA policies*.

---

## 🛠️ Technology Stack

- **LLM Engine**: [Ollama](https://ollama.com/) (Local `qwen2.5`)
- **Embedding Model**: `nomic-embed-text` (Local 768-dim embeddings)
- **RAG & Indexing**: [LlamaIndex](https://www.llamaindex.ai/) & [LangChain](https://www.langchain.com/)
- **Backend Server**: [Starlette](https://www.starlette.io/) & [Uvicorn](https://www.uvicorn.org/) (Async Python)
- **Frontend**: Vanilla HTML5, CSS3 (Modern Glassmorphism & Micro-animations), and Vanilla JavaScript

---

## 📄 License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.
