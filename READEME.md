# Finako AI

> AI-Native Enterprise Account Discovery & Knowledge Platform

Finako AI is an enterprise AI platform designed to help Enterprise Account Managers discover new business opportunities and recommend the right ICT solutions using trusted enterprise knowledge.

This project intentionally focuses on only two core capabilities:

- Enterprise Account Discovery
- Enterprise Knowledge Platform

Everything else is postponed until these two capabilities are production-ready.

---

# Vision

Build an enterprise AI platform that can:

- Discover high-quality enterprise accounts
- Understand enterprise documents
- Match customer needs with the correct IOH products
- Always provide explainable recommendations backed by evidence

The goal is not to build another chatbot.

The goal is to build an AI system that helps Enterprise Account Managers make better decisions.

---

# Current Scope

Only two capabilities are included in this repository.

## 1. Scout AI

Scout AI discovers potential enterprise customers from public information.

Responsibilities:

- Search public companies
- Detect buying signals
- Evaluate opportunity score
- Explain the reasoning
- Recommend relevant IOH products
- Recommend next actions

Every recommendation must include supporting evidence.

---

## 2. Enterprise Knowledge Platform

The Enterprise Knowledge Platform is the corporate knowledge engine.

Responsibilities:

- Store enterprise documents
- Parse documents
- Generate embeddings
- Retrieve relevant knowledge
- Match customer needs with IOH products

Every answer must reference trusted sources.

---

# Out of Scope

The following modules are intentionally excluded from this repository.

- CRM Dashboard
- Proposal Generator
- Meeting Assistant
- Opportunity Management
- Voice AI
- Multi-Agent System

These modules will only be developed after the two core capabilities are stable.

---

# Technology Stack

- **Database**: Supabase (PostgreSQL + pgvector)
- **Backend API & Chatbot**: FastAPI (Python) + python-telegram-bot (Polling Mode)
- **AI Models**: Google Vertex AI (Gemini 1.5 Pro)
- **Search Engine**: Tavily Search API
- **Web Scraper**: Firecrawl
- **Background Orchestrator**: n8n (CRON Jobs & Integrations)

---

# Repository Structure

```
finako-ai/

├── backend/
│
├── scout/
│
├── knowledge/
│
├── docs/
│
├── tests/
│
├── docker/
│
├── .env.example
│
├── docker-compose.yml
│
└── README.md
```

---

# Documentation

The architecture is intentionally documented using only three documents.

```
docs/

01_PROJECT_VISION.md

02_SYSTEM_ARCHITECTURE.md

03_ENGINEERING_GUIDE.md
```

All implementation decisions must follow these documents.

---

# Design Principles

## Simplicity

Keep the architecture simple.

Avoid unnecessary abstractions.

---

## Truth

Never invent company facts.

Every recommendation must be supported by evidence.

---

## Security

Secrets are never stored inside:

- Source code
- Workflow files
- Prompts
- Documentation
- Git history

Secrets must only be loaded from environment variables.

---

## Human First

AI recommends.

Humans decide.

---

# Development Status

| Capability | Status |
|------------|--------|
| Scout AI | 🚧 In Progress |
| Enterprise Knowledge Platform | 🚧 In Progress |

---

# License

Private Repository

Copyright © Teguh Prasetyo