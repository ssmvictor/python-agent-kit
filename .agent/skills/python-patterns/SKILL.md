---
name: python-patterns
description: Python development principles and decision-making. OOP-first architecture, strict type hints, async patterns, project structure. Teaches thinking, not copying.
tier: lite
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Python Patterns

> Python development principles and decision-making for 2025.
> **Learn to THINK, not memorize patterns.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles**, not fixed code to copy.

- ASK user for framework preference when unclear
- Choose async vs sync based on CONTEXT
- Don't default to same framework every time

This skill also enforces two defaults:

- Write solutions in an OOP style (classes for business logic, free functions mostly for wiring)
- Use strict type hints (treat static typing as a build gate)

---

## 0. Defaults: OOP + Strong Typing

This skill assumes Python is written like a strongly-typed OOP language.

Non-negotiables:

- Prefer classes for business logic (services/use-cases/repositories); keep free functions for wiring (entrypoints, route handlers)
- Type everything public: parameters, returns, attributes, and exported module symbols
- Avoid `Any` and untyped `dict`/`list`; prefer generics, `Protocol`, `TypedDict`, dataclasses, and Pydantic models
- Validate at boundaries (I/O) and keep the domain core pure and typed
- Treat static typing as a gate: run `pyright` (strict) or `mypy --strict` in CI

---

## 1. Framework Selection (2025)

### Decision Tree

```
What are you building?
│
├── API-first / Microservices
│   └── FastAPI (async, modern, fast)
│
├── Full-stack web / CMS / Admin
│   └── Django (batteries-included)
│
├── Simple / Script / Learning
│   └── Flask (minimal, flexible)
│
├── AI/ML API serving
│   └── FastAPI (Pydantic, async, uvicorn)
│
└── Background workers
    └── Celery + any framework
```

### Comparison Principles

| Factor | FastAPI | Django | Flask |
|--------|---------|--------|-------|
| **Best for** | APIs, microservices | Full-stack, CMS | Simple, learning |
| **Async** | Native | Django 5.0+ | Via extensions |
| **Admin** | Manual | Built-in | Via extensions |
| **ORM** | Choose your own | Django ORM | Choose your own |
| **Learning curve** | Low | Medium | Low |

### Selection Questions to Ask:
1. Is this API-only or full-stack?
2. Need admin interface?
3. Team familiar with async?
4. Existing infrastructure?

---

## 2. Async vs Sync Decision

### When to Use Async

```
async def is better when:
├── I/O-bound operations (database, HTTP, file)
├── Many concurrent connections
├── Real-time features
├── Microservices communication
└── FastAPI/Starlette/Django ASGI

def (sync) is better when:
├── CPU-bound operations
├── Simple scripts
├── Legacy codebase
├── Team unfamiliar with async
└── Blocking libraries (no async version)
```

### The Golden Rule

```
I/O-bound → async (waiting for external)
CPU-bound → sync + multiprocessing (computing)

Don't:
├── Mix sync and async carelessly
├── Use sync libraries in async code
└── Force async for CPU work
```

### Async Library Selection

| Need | Async Library |
|------|---------------|
| HTTP client | httpx |
| PostgreSQL | asyncpg |
| Redis | aioredis / redis-py async |
| File I/O | aiofiles |
| Database ORM | SQLAlchemy 2.0 async, Tortoise |

---

## 3. Type Hints Strategy

### Strong Typing Defaults

```
Type hints are mandatory for this skill.

Always type:
├── Function/method parameters (including *args/**kwargs when used)
├── Return types
├── Class attributes
├── Public APIs + I/O boundaries

Prefer inference only for simple locals; annotate anything non-obvious.

Avoid:
├── Any (unless isolated behind a boundary with a clear reason)
├── dict/list without type parameters
└── "stringly-typed" data (use Enums/Literals/NewType)
```

### Common Type Patterns

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, NewType, Protocol, TypedDict

UserId = NewType("UserId", int)

@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    email: str

# Optional/union
def find_user(user_id: UserId) -> User | None: ...

# Avoid untyped dicts: use TypedDict for dict-shaped data
class UserPayload(TypedDict):
    id: int
    email: str

def process(payload: UserPayload) -> None: ...

# Generic collections
def get_users() -> list[User]: ...
def get_counts() -> dict[str, int]: ...

# Callable
def apply(fn: Callable[[User], str], user: User) -> str: ...

# OOP + typing (services + repository interface)
class UserRepository(Protocol):
    def get(self, user_id: UserId) -> User | None: ...

class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def find_user(self, user_id: UserId) -> User | None:
        return self._repo.get(user_id)
```

### Pydantic for Validation

```
When to use Pydantic:
├── API request/response models
├── Configuration/settings
├── Data validation
├── Serialization

Benefits:
├── Runtime validation
├── Auto-generated JSON schema
├── Works with FastAPI natively
└── Clear error messages

Rule of thumb:
├── Pydantic models at boundaries (HTTP, env/config, message queues)
└── Typed domain models (dataclasses/classes) inside the core
```

---

## 4. Project Structure Principles

### Structure Selection

```
Small project / Script:
├── main.py
├── utils.py
└── requirements.txt

Medium API:
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── schemas/
├── tests/
└── pyproject.toml

Large application:
├── src/
│   └── myapp/
│       ├── core/
│       ├── api/
│       ├── services/
│       ├── models/
│       └── ...
├── tests/
└── pyproject.toml
```

### FastAPI Structure Principles

```
Organize by feature or layer:

By layer:
├── routes/ (API endpoints)
├── services/ (business logic)
├── models/ (database models)
├── schemas/ (Pydantic models)
└── dependencies/ (shared deps)

By feature:
├── users/
│   ├── routes.py
│   ├── service.py
│   └── schemas.py
└── products/
    └── ...
```

---

## 5. Django Principles (2025)

### Django Async (Django 5.0+)

```
Django supports async:
├── Async views
├── Async middleware
├── Async ORM (limited)
└── ASGI deployment

When to use async in Django:
├── External API calls
├── WebSocket (Channels)
├── High-concurrency views
└── Background task triggering
```

### Django Best Practices

```
Model design:
├── Fat models, thin views
├── Use managers for common queries
├── Abstract base classes for shared fields

Views:
├── Class-based for complex CRUD
├── Function-based for simple endpoints
├── Use viewsets with DRF

Queries:
├── select_related() for FKs
├── prefetch_related() for M2M
├── Avoid N+1 queries
└── Use .only() for specific fields
```

---

## 6. FastAPI Principles

### async def vs def in FastAPI

```
Use async def when:
├── Using async database drivers
├── Making async HTTP calls
├── I/O-bound operations
└── Want to handle concurrency

Use def when:
├── Blocking operations
├── Sync database drivers
├── CPU-bound work
└── FastAPI runs in threadpool automatically
```

### Dependency Injection

```
Use dependencies for:
├── Database sessions
├── Current user / Auth
├── Configuration
├── Shared resources

Benefits:
├── Testability (mock dependencies)
├── Clean separation
├── Automatic cleanup (yield)
```

### Pydantic v2 Integration

```python
# FastAPI + Pydantic are tightly integrated:

# Request validation
@app.post("/users")
async def create(user: UserCreate) -> UserResponse:
    # user is already validated
    ...

# Response serialization
# Return type becomes response schema
```

---

## 7. Background Tasks

### Selection Guide

| Solution | Best For |
|----------|----------|
| **BackgroundTasks** | Simple, in-process tasks |
| **Celery** | Distributed, complex workflows |
| **ARQ** | Async, Redis-based |
| **RQ** | Simple Redis queue |
| **Dramatiq** | Actor-based, simpler than Celery |

### When to Use Each

```
FastAPI BackgroundTasks:
├── Quick operations
├── No persistence needed
├── Fire-and-forget
└── Same process

Celery/ARQ:
├── Long-running tasks
├── Need retry logic
├── Distributed workers
├── Persistent queue
└── Complex workflows
```

---

## 8. Error Handling Principles

### Exception Strategy

```
In FastAPI:
├── Create custom exception classes
├── Register exception handlers
├── Return consistent error format
└── Log without exposing internals

Pattern:
├── Raise domain exceptions in services
├── Catch and transform in handlers
└── Client gets clean error response
```

### Error Response Philosophy

```
Include:
├── Error code (programmatic)
├── Message (human readable)
├── Details (field-level when applicable)
└── NOT stack traces (security)
```

---

## 9. Testing Principles

### Testing Strategy

| Type | Purpose | Tools |
|------|---------|-------|
| **Unit** | Business logic | pytest |
| **Integration** | API endpoints | pytest + httpx/TestClient |
| **E2E** | Full workflows | pytest + DB |

### Async Testing

```python
# Use pytest-asyncio for async tests

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users")
        assert response.status_code == 200
```

### Fixtures Strategy

```
Common fixtures:
├── db_session → Database connection
├── client → Test client
├── authenticated_user → User with token
└── sample_data → Test data setup
```

---

## 10. Decision Checklist

Before implementing:

- [ ] **Asked user about framework preference?**
- [ ] **Chosen framework for THIS context?** (not just default)
- [ ] **Decided async vs sync?**
- [ ] **Designed OOP boundaries?** (wiring/routes → services/use-cases → repos/adapters)
- [ ] **Enforced strict typing?** (pyright strict or `mypy --strict`; minimal `Any`)
- [ ] **Defined project structure?**
- [ ] **Planned error handling?**
- [ ] **Considered background tasks?**

---

## 11. Anti-Patterns to Avoid

### ❌ DON'T:
- Default to Django for simple APIs (FastAPI may be better)
- Use sync libraries in async code
- Skip type hints for public APIs
- Use `Any` as an escape hatch (hide type errors)
- Pass raw `dict`/JSON through the domain layer (use Pydantic/TypedDict at boundaries, domain classes inside)
- Put business logic in routes/views
- Ignore N+1 queries
- Mix async and sync carelessly

### ✅ DO:
- Choose framework based on context
- Ask about async requirements
- Use Pydantic for validation
- Use `Protocol` interfaces for deps + DI (repos/clients)
- Separate concerns (routes → services → repos)
- Run a strict type checker in CI (pyright or mypy)
- Test critical paths

---

> **Remember**: Python patterns are about decision-making for YOUR specific context. Don't copy code—think about what serves your application best.
