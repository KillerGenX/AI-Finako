# Finako AI — System Architecture

> Version: 1.0

---

# High-Level Architecture

```
                    Telegram

                       │

                       ▼

                     n8n

                       │

                       ▼

                  FastAPI Backend

          ┌────────────┴────────────┐

          ▼                         ▼

      Scout AI             Knowledge Engine

          ▼                         ▼

       Tavily             Document Parser

                                    ▼

                              Embedding Model

                                    ▼

                              pgvector Search

          └────────────┬────────────┘

                       ▼

                Supabase PostgreSQL
```

---

# Components

## Telegram

User interface.

Responsibilities

- Receive commands
- Upload files
- Display results
- Collect user feedback

Telegram contains no business logic.

---

## n8n

Workflow orchestration only.

Responsibilities

- Telegram webhook
- HTTP routing
- Scheduling
- Notifications

n8n must never contain business logic.

---

## FastAPI Backend

The central application.

Responsibilities

- Authentication
- Validation
- AI orchestration
- Database access
- Product matching
- Knowledge retrieval

All business logic lives here.

---

## Scout AI

Responsibilities

- Search companies
- Analyze buying signals
- Score opportunities
- Recommend products
- Explain reasoning

Scout AI never accesses Telegram directly.

---

## Enterprise Knowledge Platform

Responsibilities

- Document ingestion
- Parsing
- Chunking
- Embedding
- Retrieval

Knowledge Platform becomes the single source of truth.

---

## Supabase

Responsibilities

- PostgreSQL
- pgvector
- Authentication
- Storage

No business logic inside database.

---

# Data Flow

## Account Discovery

```
Telegram

↓

n8n

↓

FastAPI

↓

Scout AI

↓

Tavily

↓

Knowledge Platform

↓

Supabase

↓

FastAPI

↓

Telegram
```

---

## Knowledge Ingestion

```
Telegram Upload

↓

n8n

↓

FastAPI

↓

Download File

↓

Parser

↓

Chunk

↓

Embedding

↓

pgvector

↓

Supabase
```

---

# Core Rules

## Rule 1

Business logic belongs only inside FastAPI.

---

## Rule 2

n8n only orchestrates workflows.

---

## Rule 3

Telegram is only a user interface.

---

## Rule 4

Knowledge Platform never generates answers.

It only retrieves knowledge.

---

## Rule 5

Scout AI always uses retrieved knowledge before responding.

---

## Rule 6

Secrets must only come from environment variables.

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| UI | Telegram |
| Workflow | n8n |
| Backend | FastAPI |
| AI Gateway | LiteLLM |
| LLM | Gemini 2.5 |
| Search | Tavily |
| Database | PostgreSQL |
| Vector | pgvector |
| Deployment | Docker Compose |