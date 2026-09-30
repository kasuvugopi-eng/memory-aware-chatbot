Markdown<div align="center">

# 🧠 Memory-Aware Conversational AI

**Production-grade FastAPI chatbot with a 3-layer persistent memory architecture powered by LangChain, Google Gemini, and PostgreSQL.**

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Vertex%20AI-8E75B2.svg?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Package Manager](https://img.shields.io/badge/uv-Astral-purple.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#memory-architecture">Memory Architecture</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#roadmap">Roadmap</a>
</p>

</div>

---

## 💡 Overview

Standard chatbots forget who you are the second a session ends or token limits truncate past turns. 

This project implements a **Hierarchical 3-Layer Memory Engine** that separates short-term conversational context from persistent user identity. By combining recent interactions, rolling summaries, and cross-session entity extraction, it delivers ultra-personalized responses while keeping token consumption and latency strictly bounded.

---

## ⚡ Key Features

- **🧠 3-Tier Layered Memory**
  - **Tier 1 (Buffer):** Sliding window of the last $N$ messages for immediate conversational flow.
  - **Tier 2 (Rolling Summary):** Background summarization of the current session triggered incrementally.
  - **Tier 3 (User Profile Core):** Cross-session semantic memory storing user goals, skills, names, and preferences.
- **⚡ Dual-Path Processing (Low Latency)**
  - **Fast Path:** Builds context, invokes Gemini, and returns the response immediately to the client.
  - **Slow Path (Background):** Extracts facts and updates summaries asynchronously via background worker tasks.
- **🔒 Race-Condition Safe**
  - Implements row-level locking (`SELECT ... FOR UPDATE`) in PostgreSQL to guarantee atomic profile updates across concurrent requests.
- **🛡️ Self-Limiting Context**
  - Hard bounds on sliding history ($N=10$) and capped entity sets (up to 5 recent values per key) to eliminate context window bloat and runaway LLM costs.

---

## 🏛️ System Architecture

```text
 ┌────────────────┐
 │ Client Request │ (User ID, Session ID, Message)
 └───────┬────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ FastAPI Fast-Path Router (/chat)                       │
│                                                        │
│  1. Fetch sliding window (chat_messages)               │
│  2. Fetch user profile (user_memories)                 │
│  3. Fetch active summary (conversation_summaries)      │
│  4. Assemble prompt context -> Stream to Gemini        │
└────────┬───────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────► Returns Response to Client 🚀
         │
         ▼ (Spawns Background Task)
┌────────────────────────────────────────────────────────┐
│ Async Background Pipeline (Slow Path)                  │
│                                                        │
│  • Pydantic fact-extraction from user input            │
│  • Atomic merge with user_memories (FOR UPDATE)        │
│  • Incrementally update conversation_summaries         │
└────────────────────────────────────────────────────────┘
🛠️ Tech StackDomainTechnologyDescriptionRuntimePython 3.11High-performance async runtimePackage ManageruvUltra-fast Python package installer & resolverWeb LayerFastAPI + UvicornAsynchronous REST endpointsOrchestrationLangChainPrompt templates and chain orchestrationLLM ProviderGoogle Gemini via Vertex AICost-effective, high-context inferenceDatabasePostgreSQLACID-compliant relation store with row-lockingORM / QuerySQLAlchemy CoreLightweight, explicit query executionValidationPydantic v2Strict data validation & structured extraction📂 Project StructureBashchatbot_application/
└── app/
    ├── main.py                  # API routes & lifespan setup
    ├── chat_service.py          # Fast-path controller & background dispatcher
    ├── chat_history.py          # Raw chat persistence layer
    ├── memory_db.py             # Memory writes with atomic locks & caps
    ├── getmemory_db.py          # Memory read/lookup utilities
    ├── memory_extractor.py      # LLM structured extraction pipeline
    ├── memory_schema.py         # Pydantic schemas for extracted entities
    ├── conversation_db.py       # Session summaries persistence
    ├── summarizer_memory.py     # Rolling summarization chains
    ├── context_builder.py       # Context fusion engine (History + Profile + Summary)
    ├── llm.py                   # Gemini client factory
    ├── database.py              # Engine pooling & session management
    └── logger_config.py         # Structured logging configuration
🚀 Getting StartedPrerequisitesPython 3.11+uv package managerRunning PostgreSQL instanceGoogle Cloud Project with Vertex AI enabled1. InstallationBashgit clone <your-repo-url>
cd chatbot_application/app
uv sync
2. Environment SetupCreate a .env file from the template:Bashcp .env.example .env
Set the required environment variables:Ini, TOMLDATABASE_URL="postgresql://username:password@localhost:5432/chatbot_db"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
3. Database InitializationExecute the schema in PostgreSQL:SQLCREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_memories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    memory_key VARCHAR(100) NOT NULL,
    memory_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, memory_key)
);

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    summary TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, session_id)
);
4. Run ApplicationBashuv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
API Base: http://127.0.0.1:8000Swagger Docs: http://127.0.0.1:8000/docs📡 API ReferenceSend Chat MessagePOST /chatBashcurl -X POST [http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat) \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_9981",
    "session_id": "sess_102",
    "message": "Hi, my name is Gopi and I am working with agentic AI workflows."
  }'
Sample ResponseJSON{
  "status": "success",
  "reply": "Hello Gopi! Great to meet you. What kind of agentic AI workflows are you building?",
  "session_id": "sess_102"
}
🗺️ Roadmap[ ] Vector Memory Integration: Add pgvector for semantic similarity-based memory lookups.[ ] Adaptive Inactivity Summaries: Periodic worker for sessions inactive $> 30$ mins.[ ] Rate Limiting & Auth: Add Redis-based token bucket rate limiting.[ ] Interactive Web UI: Next.js / Streamlit playground for interactive testing.📄 LicenseDistributed under the MIT License. See LICENSE for more information.