# Finako AI — Engineering Guide

> Version: 1.0

---

# Engineering Philosophy

Build less.

Build better.

Every component must have a single responsibility.

---

# Project Structure

```
finako-ai/

backend/

    api/

    core/

    scout/

    knowledge/

    models/

    services/

    repositories/

    prompts/

    config/

    main.py

docs/

tests/

docker/

.env.example

docker-compose.yml

README.md
```

---

# Backend Responsibilities

## API

HTTP endpoints.

No business logic.

---

## Core

Configuration.

Environment.

Logging.

Security.

---

## Scout

Enterprise account discovery.

Buying signal analysis.

Opportunity scoring.

---

## Knowledge

Document ingestion.

Document parsing.

Embedding.

Retrieval.

---

## Services

Business logic.

All decision making belongs here.

---

## Repositories

Database access only.

No business logic.

---

## Prompts

Prompt templates.

No secrets.

No hardcoded values.

---

# Coding Standards

Keep functions small.

Prefer composition.

Avoid duplication.

Return typed objects.

Use async where appropriate.

---

# Security Rules

Never commit:

- API Keys
- Tokens
- Passwords
- Credentials
- Service Keys

Always use:

```
.env
```

Never read secrets from code.

---

# Logging

Every request receives:

```
Correlation ID
```

Example

```
FIN-20260722-000001
```

The Correlation ID follows the request across:

- Telegram
- n8n
- FastAPI
- Scout AI
- Knowledge Engine
- Database

---

# AI Rules

Scout AI never invents facts.

Knowledge Platform never generates answers.

LLM only answers using:

- Tavily Search
- Enterprise Knowledge

If evidence is unavailable:

```
I don't know.
```

---

# Development Workflow

```
Feature

↓

Branch

↓

Implementation

↓

Testing

↓

Review

↓

Merge

↓

Deploy
```

---

# Testing Checklist

Before every merge verify:

- API works
- Workflow works
- Database migration works
- Knowledge retrieval works
- Product matching works
- No secrets committed

---

# Definition of Done

A feature is complete only if:

- Code implemented
- Tests passed
- Documentation updated
- No hardcoded secrets
- Docker build successful
- End-to-end verification completed

---

# Final Principle

Keep the architecture simple.

Make the implementation robust.

Optimize only after the system is working.