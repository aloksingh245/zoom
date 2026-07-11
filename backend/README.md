# ⚡ Zoom Scheduler Backend API

A production-ready FastAPI service orchestrating virtual class sessions, integrating Zoom meetings, synchronizing events with Google Calendar, logging logs to Google Sheets, and pushing data to CRM webhooks. Powered by SQLite and fully async.

---

## 🛠️ Technology Stack

* **Framework**: FastAPI (Python 3.12+)
* **Asynchronous ORM**: SQLAlchemy (async session model via `aiosqlite`)
* **Package Management**: `uv` (ultra-fast dependency resolver)
* **Auth**: JWT Bearer token generation (HS256) & bcrypt password hashing
* **Event Dispatching**: Asyncio-based in-memory Publish/Subscribe Event Bus
* **AI Parser**: Google Gemini API via async clients
* **Testing**: `pytest` + `pytest-asyncio` + SMTP testing mocks

---

## 🚀 Getting Started

### 1. Installation & Dependency Setup
We use `uv` for python environment and dependency resolution.

```bash
# Install uv package manager if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync packages and create virtual environment
uv sync
```

### 2. Configuration Setup
Copy the example environment configuration file and populate your credentials:

```bash
cp .env.example .env
```

Open `.env` and configure:
* **Zoom API credentials** (S2S OAuth details: Account ID, Client ID, Client Secret, User ID)
* **Google credentials** (Sheets Spreadsheet ID, Calendar ID)
* **Gmail SMTP credentials** (App passwords for verification emails)
* **Gemini API Key** (for parsing natural language schedule strings)

### 3. Running the Server Locally
To start the FastAPI development server with hot reloading enabled:

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The OpenAPI interactive documentation will be available at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing

The backend includes a comprehensive suite of unit and integration tests (validating oauth, auth lifecycles, event bus, database rollbacks, agent guardrails, and timezone conversions).

To execute the test suite:

```bash
uv run python -m pytest tests/ -v
```

---

## 📁 Directory Architecture

```
backend/
├── core/
│   ├── base.py          # SQLAlchemy declarative base metadata
│   ├── database.py      # Async database connection and session factories
│   ├── events.py        # Custom asyncio Publish/Subscribe EventBus
│   ├── config.py        # Pydantic Settings env reader
│   └── utils.py         # Retry utilities (exponential backoff)
├── modules/
│   ├── auth/            # JWT validation, signup, login, password reset
│   ├── classes/         # CRUD endpoints, sync controls, calendar OAuth handlers
│   ├── courses/         # CRUD endpoints for courses & batches
│   ├── settings/        # Endpoint to modify config .env fields live
│   └── agent/           # SSE RAG agent workspace with ADK logic
├── integrations/
│   ├── zoom/            # Zoom API Client (Server-to-Server)
│   ├── google_calendar/ # Google Calendar API Client
│   ├── google_sheets/   # Google Sheets Client (Service Account)
│   └── crm/             # Partner CRM Sync Client
├── tests/
│   ├── conftest.py      # Global pytest SMTP mocks
│   ├── unit/            # Isolated unit tests
│   ├── integration/     # Service integrations and DB/OAuth tests
│   └── agent/           # Agent flow and loop iteration tests
└── main.py              # Application lifecycle, startup registrations, routing
```
