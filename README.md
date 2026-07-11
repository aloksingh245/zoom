# 📅 Zoom Class Scheduler — Core Platform

An advanced scheduling platform designed to coordinate and manage virtual class sessions. The system integrates synchronously with the **Zoom API** for meeting provisioning, and utilizes an asynchronous event-driven architecture to coordinate secondary integrations: **Google Calendar** (OAuth PKCE), **Google Sheets** (Service Account logs), and **AcceleratorX CRM**. The platform also features an interactive, role-based week calendar UI and a built-in streaming **AI Agent assistant** powered by Google Gemini and ChromaDB RAG.

---

## 🚀 Key Features

*   📅 **Interactive Week-View Calendar Grid**: Drag/click slots to schedule sessions with automatic time and duration layouts.
*   🎥 **Zoom Video Conferencing (Sync Path)**: Automated creation, updating, and cancellation of Zoom meetings.
*   📅 **Google Calendar Sync (Async Path)**: Bi-directional event synchronization with user accounts via PKCE OAuth.
*   📊 **Google Sheets Logging (Async Path)**: Asynchronous reporting of class metrics using service account credentials.
*   🏢 **CRM Webhook Updates (Async Path)**: Automated class record updates pushed to AcceleratorX CRM.
*   🤖 **Gemini-Powered AI Parsing**: Extract schedule parameters from natural language prompts to auto-populate class forms.
*   💬 **Floating AI Chatbot (ZoomBot)**: A role-aware assistant answering workspace queries and scheduling classes semantically utilizing ChromaDB RAG.
*   🔐 **Role-Based JWT Authentication**: Secure access limits for Admin (full CRUD), Mentor (assigned classes view only), and Student (view only) accounts.

---

## 🏗️ Architecture & Topology

```
┌───────────────────────────────────────────────────────────┐
│              FRONTEND (React 19 + Tailwind v4)            │
│                       Port: 5173                          │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP + Bearer JWT
                              ▼
┌───────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI + uvicorn)                 │
│                       Port: 8000                          │
└──────────────┬──────────────┬──────────────┬──────────────┘
               │              │              │
        (Sync Path)     (Async Events) (Async Events) (Async Events)
               ▼              ▼              ▼              ▼
┌──────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│    SQLite    │ │  Zoom API  │ │ Google API │ │  CRM API   │
│  sql_app.db  │ │ M2M OAuth  │ │  Calendar  │ │AcceleratorX│
└──────────────┘ └────────────┘ └────────────┘ └────────────┘
```

---

## 📁 Repository Map

```
zoom-scheduler/
├── backend/               # FastAPI async application (Uvicorn)
│   ├── core/              # Database engine, config settings, and EventBus
│   ├── modules/           # Auth, classes, courses, settings, and Agent modules
│   ├── integrations/      # Zoom, Google Calendar, Google Sheets, and CRM clients
│   ├── tests/             # Structured unit, integration, and agent test suites
│   ├── main.py            # Lifecycle hooks, routers, and application startup
│   └── pyproject.toml     # Python dependencies managed via uv
├── frontend/              # Vite SPA (React 19 + Tailwind v4)
│   ├── src/               # Components (Auth, Calendar, Dashboard, Settings, Agent)
│   ├── package.json       # Node package manifest
│   └── vite.config.js     # Vite builder config
├── docker-compose.yml     # Multi-container local execution setup
├── DEEP_UNDERSTANDING.md  # Detailed system architecture deep-dive
├── architecture.md        # Technical design and schema specifications
└── README.md              # This file
```

---

## ⚙️ Setup & Local Installation

### Prerequisites
*   [Python 3.12+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)
*   [uv Package Manager](https://astral.sh/uv/)

---

### 1. Backend Setup
1. Navigate into the backend directory and synchronize dependencies:
   ```bash
   cd backend
   uv sync
   ```
2. Create your environment configuration file:
   ```bash
   cp .env.example .env
   ```
3. Open `backend/.env` and supply the required API keys (Zoom S2S OAuth details, Google Sheets ID, Google Web Client Secrets, SMTP account details, and a Gemini API Key).
4. Run the API development server:
   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```
   Interactive Swagger documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### 2. Frontend Setup
1. Navigate into the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🐳 Running with Docker Compose

To launch both the Frontend (:5173) and Backend (:8000) inside isolated containers simultaneously:

```bash
# From the project root directory
docker-compose up --build
```

---

## 🧪 Testing

The backend includes a comprehensive, structured test suite checking auth lifecycles, background event dispatches, calendar updates, and AI Agent guardrails.

To run tests:
```bash
cd backend
uv run python -m pytest tests/ -v
```

---

## 🔐 Environment Configuration Reference

The following environment variables should be set in `backend/.env`:

| Key | Description | Example / Fallback |
| :--- | :--- | :--- |
| `ZOOM_ACCOUNT_ID` | Zoom Server-to-Server Account ID | *Your Zoom account ID* |
| `ZOOM_CLIENT_ID` | Zoom Client ID | *Your Zoom Client ID* |
| `ZOOM_CLIENT_SECRET` | Zoom Client Secret | *Your Zoom Client Secret* |
| `GOOGLE_CALENDAR_ID` | Google Calendar target ID | `primary` |
| `GOOGLE_SHEET_ID` | Spreadsheet ID for reporting logs | *Your Google Sheet ID* |
| `SMTP_USERNAME` | Gmail address for sending verification emails | `example@gmail.com` |
| `SMTP_PASSWORD` | App-specific Google password | *Gmail App Password* |
| `GEMINI_API_KEY` | Gemini API access token | *Your Gemini API key* |
| `BACKEND_URL` | Base endpoint URL of the FastAPI backend | `http://localhost:8000` |
| `APP_URL` | Base URL of the React Frontend | `http://localhost:5173` |

---

## 🛡️ Security & Ignore Policy

For security, the following local files and database directories are ignored in [.gitignore](file:///.gitignore) and must never be pushed to GitHub:
*   Local database files: `backend/sql_app.db` and vector logs `backend/chroma_store/`.
*   User credential tokens: `backend/token.json` and service keys `backend/credentials.json`.
*   Private configuration values: `backend/.env`.
*   Developer logs: `*.log`.
