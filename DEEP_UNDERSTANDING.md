# 🧠 Deep Project Understanding — Zoom Scheduler
> Complete architectural deep-dive — last updated July 11, 2026


---

## 🏗️ Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19 + Vite 7)                 │
│  Port: 5173                                                          │
│                                                                      │
│  App.jsx ─ Manual pathname/state-based routing (no react-router)    │
│  ├── AuthPage         → Login / Signup                               │
│  ├── VerifyEmail      → /verify-email?token=...                      │
│  ├── ResetPassword    → /reset-password?token=...                    │
│  └── Main App (authenticated):                                       │
│       ├── Sidebar     → Navigation + GCal connect status             │
│       ├── TopBar      → Search + Sync + Theme toggle                 │
│       ├── Dashboard   → Stats cards + today's class list             │
│       ├── Calendar    → Week-view grid (click-to-create)             │
│       ├── CourseList  → Course management                            │
│       ├── SettingsPanel → Runtime .env editor                        │
│       ├── ClassModal  → Create/Edit class form                       │
│       └── ChatBubble  → Floating AI agent assistant (RAG + tools)    │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ HTTP + Bearer JWT (CORS)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + uvicorn)                     │
│  Port: 8000                                                          │
│                                                                      │
│  main.py                                                             │
│  ├── Startup (@app.on_event): register listeners (RAG startup index)  │
│  ├── CORS middleware                                                  │
│  └── Routers:                                                        │
│       ├── /auth          → Auth module                               │
│       ├── /api/classes   → Classes module                            │
│       ├── /api/courses   → Courses module                            │
│       ├── /zoom          → Zoom integration (thin router)            │
│       ├── /calendar      → Google Calendar router                    │
│       ├── /api/settings  → Settings module                           │
│       └── /api/agent     → AI Agent Module (ChromaDB RAG + ADK Loop) │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
          ┌─────────────────┼──────────────────┬────────────────┐
          ▼                 ▼                  ▼                ▼
    ┌──────────┐    ┌──────────────┐  ┌──────────────────┐ ┌──────────┐
    │  SQLite  │    │  Zoom API v2 │  │  Google APIs     │ │ CRM API  │
    │sql_app.db│    │ (M2M OAuth)  │  │ Calendar, Sheets │ │PartnerCRM│
    └──────────┘    └──────────────┘  └──────────────────┘ └──────────┘
```

---

## 📁 Full Directory Map

```
zoom-scheduler/
├── backend/
│   ├── core/
│   │   ├── base.py           → SQLAlchemy declarative Base
│   │   ├── config.py         → Pydantic Settings (reads .env)
│   │   ├── database.py       → async SQLite engine + session factory
│   │   ├── events.py         → Custom asyncio EventBus (Pub/Sub)
│   │   └── utils.py          → async_retry decorator (exponential backoff)
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── models.py     → User ORM model
│   │   │   ├── schemas.py    → Pydantic schemas (UserCreate, Token, etc.)
│   │   │   ├── router.py     → Auth endpoints (signup/login/verify/reset)
│   │   │   ├── utils.py      → bcrypt, JWT, SMTP email helpers
│   │   │   └── dependencies.py → get_current_user, RoleChecker
│   │   ├── classes/
│   │   │   ├── models.py     → ClassSession ORM model
│   │   │   ├── schemas.py    → ClassCreate, ClassUpdate, ClassSession
│   │   │   ├── router.py     → CRUD + sync endpoints + PKCE OAuth flow
│   │   │   └── service.py    → Full class business logic
│   │   ├── courses/
│   │   │   └── ...           → Course CRUD (models, schemas, router, service)
│   │   ├── settings/
│   │   │   ├── router.py     → GET/POST /api/settings (reads+writes .env)
│   │   │   └── schemas.py    → SettingsRead, SettingsUpdate
│   │   └── agent/
│   │       ├── router.py     → SSE API endpoints (POST /api/agent/chat)
│   │       ├── agent.py      → ADK Agent setup + loop + streaming execution
│   │       ├── listeners.py  → Event listeners for automatic RAG syncing
│   │       ├── prompts/      → Role-based prompts (admin, mentor, student)
│   │       ├── guardrails/   → Security (input, tool permission, output, loop limit)
│   │       ├── memory/       → In-memory session store (last 20 messages)
│   │       ├── rag/          → ChromaDB vector indexer and semantic retriever
│   │       ├── tools/        → Python execution tools registry
│   │       └── voice/        → Future voice STT/TTS placeholders
│   ├── integrations/
│   │   ├── zoom/
│   │   │   ├── client.py     → ZoomService singleton (M2M OAuth + Bearer)
│   │   │   └── router.py     → Thin /zoom router
│   │   ├── google_calendar/
│   │   │   ├── client.py     → CalendarService (OAuth user token.json)
│   │   │   ├── listeners.py  → Event bus handlers for class CRUD
│   │   │   └── router.py     → /calendar router
│   │   ├── google_sheets/
│   │   │   ├── client.py     → SheetsService (Service Account / aiogoogle)
│   │   │   └── listeners.py  → Event bus handlers for sheet logging
│   │   └── crm/
│   │       ├── client.py     → CRMService (httpx POST to Partner CRM)
│   │       └── listeners.py  → Event bus handlers for CRM sync
│   ├── main.py               → FastAPI app, startup, routers
│   ├── pyproject.toml        → Python dependencies (uv-managed)
│   ├── conftest.py           → Global SMTP mock fixture for tests
│   ├── sql_app.db            → SQLite database (local only, ignored)
│   ├── token.json            → Google OAuth user credentials (local only, ignored)
│   └── test_*.py             → Test suite (23 tests, all passing)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           → Root component (routing + layout + modals)
│   │   ├── components/
│   │   │   ├── Auth/         → AuthPage, VerifyEmail, ResetPassword
│   │   │   ├── Calendar/     → Week-view calendar grid
│   │   │   ├── Courses/      → CourseList
│   │   │   ├── Dashboard/    → Stats + today's classes
│   │   │   ├── Layout/       → Sidebar, TopBar
│   │   │   ├── Modals/       → ClassModal (create/edit)
│   │   │   ├── Settings/     → SettingsPanel
│   │   │   ├── Agent/        → Floating ChatBubble, ChatWindow, ChatMessage
│   │   │   └── UI/           → Shared UI primitives
│   │   ├── hooks/
│   │   │   ├── useClasses.js    → Class CRUD + sync + calendar connect
│   │   │   ├── useCourses.js    → Course list + create
│   │   │   ├── useUsersStats.js → Admin stats
│   │   │   └── useAgentChat.js  → Streaming connection to ZoomBot Agent
│   │   ├── context/
│   │   │   └── AuthContext.jsx  → Global JWT user state
│   │   ├── services/         → API call functions (axios/fetch wrappers)
│   │   ├── utils/
│   │   │   └── dateUtils.js  → formatDate, isPastLocal, startOfWeek
│   │   └── constants/        → DEFAULT_TIMEZONE
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml        → Backend :8000 + Frontend :5173
├── DEEP_UNDERSTANDING.md     → This file (committed)
├── POC.md                    → Bug fixes, test results, change log (ignored)
├── prompt.md                 → Original setup prompt (ignored)
├── architecture.md           → Original POC design doc (committed)
└── .env                      → Root-level env vars (ignored)
```

---

## 🗄️ Data Models

### User (`auth/models.py`)
```
id                  UUID string (PK)
email               unique, indexed
hashed_password     bcrypt hash
role                "admin" | "mentor" | "student"
is_verified         bool (default False)
verification_token  UUID string (nulled after verify)
reset_token         UUID string (nulled after reset)
reset_token_expires DateTime (15 min window)
created_at          DateTime
updated_at          DateTime (auto-update)
```

### ClassSession (`classes/models.py`)
```
id                  UUID string (PK)
course_id           FK → courses.id
course_name         denormalized string (for speed)
topic_name          string
assignment_name     string? (optional)
date                "YYYY-MM-DD"
start_time          "HH:MM"
duration_minutes    int (default 90)
timezone            IANA timezone string (e.g. "Asia/Kolkata")
zoom_meeting_id     string  ← from Zoom API
zoom_join_url       string  ← from Zoom API
calendar_event_id   string? ← Google Calendar event ID (set async)
mentor_email        string? (optional)
sheet_row_id        string? ← Google Sheets updated range (set async)
created_at / updated_at
```

### Course (`courses/models.py`)
```
id        UUID string (PK)
name      unique string
classes   → relationship to ClassSession[]
```

---

## 🔐 Auth System

### Full Flow
```
Signup → hash password (bcrypt) → save user (is_verified=False)
       → generate UUID token → send email with verify link
       → POST /auth/verify-email?token=X → set is_verified=True
       → POST /auth/login → check verified → issue JWT (24h, HS256)
       → Bearer token on all protected routes
```

### JWT Payload
```json
{ "sub": "email@example.com", "role": "admin", "exp": 1234567890 }
```

### Role Guards
- `get_current_user` → validates JWT, injects User object
- `RoleChecker(["admin"])` → 403 for mentors/students
- Frontend also checks `user.role !== 'admin'` before rendering forms

### Password Reset
```
POST /auth/forgot-password → generate reset_token → valid 15 min
                           → always returns success (prevents email enumeration)
POST /auth/reset-password  → validate expiry → hash new password → clear token
```

### Email (SMTP)
- Gmail SMTP via `smtplib` with App Password
- `auth/utils.py`: `send_verification_email()`, `send_reset_password_email()`
- `conftest.py`: global `autouse` mock fixture stubs SMTP in all tests

---

## 📅 Class Lifecycle

### 1. CREATE
```
Admin fills form → frontend validates (not past, client-side)
  → POST /api/classes
  → backend: validate not-past (timezone-aware) + check conflicts
  → create Zoom meeting ← CRITICAL SYNC (fails the request if Zoom fails)
  → save to SQLite DB
  → if DB fails: rollback Zoom meeting (delete) + raise 500
  → emit "class_created" event (non-blocking background tasks):
       ├── GCal listener    → create Calendar event → save calendar_event_id to DB
       ├── Sheets listener  → append row → save sheet_row_id to DB
       └── CRM listener     → POST to Partner CRM API
```

### 2. UPDATE
```
  → update Zoom meeting (sync)
  → update DB
  → emit "class_updated":
       ├── GCal: update existing event (or create if no calendar_event_id + mentor_email exists)
       ├── Sheets: update row at sheet_row_id
       └── CRM: PUT/PATCH to CRM
```

### 3. DELETE
```
  → delete Zoom meeting (404 silently ignored)
  → delete from DB
  → emit "class_deleted":
       ├── GCal: delete event
       ├── Sheets: (remove row if applicable)
       └── CRM: delete from CRM
```

### 4. SYNC WITH ZOOM
```
Full sync (if Zoom list permitted):
  → fetch all upcoming Zoom meetings
  → local classes without matching Zoom IDs → deleted locally
  → Zoom meetings not in local DB → imported under "Synced from Zoom" course

Surgical sync (fallback, if 403/401 on list endpoint):
  → check each class individually via GET /meetings/{id}
  → 404 responses → delete local class
```

### 5. SYNC WITH GOOGLE CALENDAR
```
For each class with a valid calendar_event_id:
  → fetch GCal event
  → if deleted/cancelled → delete class locally + from Zoom
  → if time changed in GCal → update class locally + update Zoom
```

---

## ⚡ Event Bus System (`core/events.py`)

```python
# Pub/Sub using asyncio.create_task() — non-blocking
event_bus.subscribe("class_created", listener_fn)
await event_bus.emit("class_created", class_data)
# → creates asyncio.create_task() for each listener
# → errors in listeners are caught + logged — NEVER crash main flow
# → tasks are held in _background_tasks set to prevent GC
```

### Registered Listeners

| Event | Listener | Action |
|---|---|---|
| `class_created` | `google_calendar` | Create GCal event, save `calendar_event_id` |
| `class_created` | `google_sheets` | Append row, save `sheet_row_id` |
| `class_created` | `crm` | POST class data to Partner CRM |
| `class_updated` | All 3 | Update in GCal / Sheets / CRM |
| `class_deleted` | All 3 | Delete from GCal / Sheets / CRM |

---

## 🔗 Google Calendar Integration

### OAuth PKCE Flow (implemented in `classes/router.py`)
```
GET /api/classes/sync/calendar/auth
  → load oauth_client.json (must be type "web")
  → generate PKCE: code_verifier (secrets.token_urlsafe(96))
                    code_challenge (SHA256 → base64url)
  → build auth_url with code_challenge + S256 method
  → store _pkce_store[state] = code_verifier (in-memory dict)
  → return auth_url to frontend

User approves in browser → Google redirects to:
GET /api/classes/sync/calendar/callback?code=X&state=Y
  → retrieve + pop code_verifier from _pkce_store[state]
  → flow.fetch_token(code=code, code_verifier=code_verifier)
  → save credentials to token.json
  → return styled HTML success page → JS auto-redirects to frontend?gcal_success=true
```

### CalendarService (`integrations/google_calendar/client.py`)
- Loads credentials from `token.json` (auto-refreshes on expiry)
- Auto-deletes `token.json` if `invalid_grant` detected
- Converts all times to UTC before API calls (prevents timezone shift bugs)
- All methods wrapped with `@async_retry(max_retries=3, initial_delay=1.0)`
- Graceful stub: if no credentials → logs warning, returns `stub_gcal_<timestamp>`

---

## 📊 Google Sheets Integration

### SheetsService (`integrations/google_sheets/client.py`)
- Uses **Service Account** credentials (not user OAuth)
- Credentials loaded from:
  1. `GOOGLE_CREDENTIALS_B64` env var (base64 JSON, preferred for Docker)
  2. `credentials.json` file (fallback)
- Uses `aiogoogle` library for async Sheets v4 API
- Auto-initializes header row if Sheet1!A1 is empty

**Sheet Columns (13 columns):**
```
Log Timestamp | Class ID | Course/Batch | Topic | Mentor Email |
Date | Start Time | Duration (Mins) | Timezone |
Zoom Meeting ID | Zoom Link | Assignment/Agenda | Status
```

- Graceful stub: if no credentials or no `GOOGLE_SHEET_ID` → logs stub, returns fake row ID

---

## 🏢 CRM Integration (Partner CRM)

### CRMService (`integrations/crm/client.py`)
- Simple `httpx.AsyncClient` POST to `https://capi.partnercrm.org/classes`
- Bearer token from `settings.crm_bearer_token`
- Graceful stub: if token is empty or `"YOUR_TOKEN"` → logs stub, returns `"stub_crm_id"`
- Returns `CRM ID` (field: `data.Id`) on success

> ⚠️ `crm_bearer_token` is **NOT** exposed in the Settings UI — must be set directly in `.env`

---

## 🔭 Zoom Integration

### ZoomService (`integrations/zoom/client.py`)
- **Singleton pattern** (`__new__`) — one instance, cached access token
- **Auth priority:**
  1. Server-to-Server OAuth (M2M): `zoom_account_id` + `zoom_client_id` + `zoom_client_secret`
     - Tokens cached in-memory with expiry tracking
  2. Static Bearer token: `zoom_bearer_token` (legacy/fallback)
- **Timezone normalization:** `Asia/Calcutta` → `Asia/Kolkata`
- **Operations:** `create_meeting`, `update_meeting`, `delete_meeting`, `list_meetings`, `get_meeting`
- All meetings created as type `2` (scheduled), not recurring

---

## 🤖 AI Module

- **Route:** `POST /api/ai/parse` (admin only)
- **Model:** Gemini via `httpx.AsyncClient`
- **Input:** `{ prompt, current_date, current_time }`
- **Output:** Parsed class fields:
  ```json
  {
    "topic_name": "...",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "duration_minutes": 90,
    "course_name": "...",
    "mentor_email": "..."
  }
  ```
- **Used by:** `AIChatAssistant` floating chat bubble in the frontend — pre-fills the ClassModal
- **Key:** `GEMINI_API_KEY` in `.env` (editable via Settings UI but masked)

---

## ⚙️ Settings Module

- **GET `/api/settings`** → reads current `.env` values (admin only)
  - Secret fields returned as `bool` (e.g., `zoom_client_secret_set`, `smtp_password_set`, `gemini_api_key_set`)
- **POST `/api/settings`** → writes updated values to `.env` file at runtime
  - Values equal to `"••••••••"` are skipped (not overwritten)
  - After writing: touches `main.py` to trigger uvicorn `--reload` hot restart

**Editable via UI:**
```
ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_USER_ID
GOOGLE_CALENDAR_ID, GOOGLE_SHEET_ID
SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM
APP_URL, TIMEZONE_DEFAULT, GEMINI_API_KEY
```

**Not yet in Settings UI:**
```
CRM_BEARER_TOKEN, BACKEND_URL, CORS_ALLOW_ORIGINS
```

---

## 🌐 Frontend Architecture

### Tech Stack
| Layer | Tech | Version |
|---|---|---|
| Framework | React | 19.2.0 |
| Build tool | Vite | 7.x |
| Styling | TailwindCSS (via @tailwindcss/vite) | 4.x |
| Icons | Lucide React | 0.577.0 |
| State | React hooks + Context (no Redux/Zustand) | — |
| Routing | Manual pathname + state-based | — |

### Routing Strategy
```javascript
// URL-based (for external links / email redirects)
if (pathname === '/verify-email') return <VerifyEmail />
if (pathname === '/reset-password') return <ResetPassword />

// State-based (within authenticated app)
view === 'dashboard' | 'calendar' | 'courses' | 'settings'
```

### Custom Hooks
| Hook | Manages |
|---|---|
| `useClasses` | CRUD + Zoom sync + GCal sync + calendar connect |
| `useCourses` | Course list + add course |
| `useUsersStats` | Admin stats (total/mentor/student counts) |

### AuthContext
- Stores JWT + decoded user (`id`, `email`, `role`)
- Persists to `localStorage`
- Provides `login()`, `logout()` actions

### Key Frontend Features
- ✅ Dark/Light theme toggle (persisted in `localStorage` as `zoom_scheduler_theme`)
- ✅ Week-view calendar with click-to-create (opens ClassModal with date/hour pre-filled)
- ✅ Search/filter across classes (by course_name, topic_name, assignment_name)
- ✅ AI chat assistant (floating bubble → Gemini → pre-fills form)
- ✅ Role-based UI (mentors: view only; admins: create/edit/delete)
- ✅ Google Calendar connection status indicator in sidebar
- ✅ `?gcal_success=true` param detection on load → success toast

---

## 🔧 Tech Stack Summary

| Layer | Tech |
|---|---|
| **Frontend** | React 19, Vite 7, TailwindCSS v4, Lucide React |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic v2 |
| **Database** | SQLite (async via aiosqlite) |
| **Auth** | JWT (PyJWT), bcrypt (passlib), email verification |
| **Zoom** | Zoom API v2, Server-to-Server OAuth (M2M) + Bearer fallback |
| **Google Calendar** | OAuth2 PKCE (user token.json), google-auth-oauthlib |
| **Google Sheets** | Service Account, aiogoogle (async) |
| **CRM** | Partner CRM REST API (httpx) |
| **Email** | Gmail SMTP (App Password) via smtplib |
| **AI** | Gemini API (httpx async) |
| **Retry** | Custom `async_retry` decorator (exponential backoff) |
| **Testing** | pytest + pytest-asyncio + unittest.mock |
| **Containerize** | Docker + Docker Compose |
| **Package Mgr** | uv (Python), npm/pnpm (Node) |

---

## 🧪 Test Suite

All tests reside under `backend/tests/`. Run: `uv run python -m pytest tests/ -v`

| Category | File Path | Tests | What It Tests |
|---|---|---|---|
| **Agent** | `tests/agent/test_agent_flow.py` | 7 | Security Guardrails (input, tool, output, loop limit) |
| **Integration** | `tests/integration/test_auth_flow.py` | 1 | Auth full lifecycle: Signup → Verify → Login → `/me` |
| **Integration** | `tests/integration/test_calendar_sync.py` | 3 | Google Calendar sync: deleted events and time changes |
| **Integration** | `tests/integration/test_oauth_flow.py` | 4 | Google Calendar OAuth PKCE flow & callbacks |
| **Integration** | `tests/integration/test_settings_flow.py` | 1 | Settings module runtime read/write updates to `.env` |
| **Integration** | `tests/integration/test_late_mentor.py` | — | Late mentor email assignment scenarios |
| **Integration** | `tests/integration/test_rollback.py` | — | DB transaction rollback on Zoom meeting creation failures |
| **Integration** | `tests/integration/test_gcal.py` | — | Direct API integration with Google Calendar |
| **Unit** | `tests/unit/test_event_bus.py` | 2 | Async Pub/Sub dispatching and task execution isolation |
| **Unit** | `tests/unit/test_retry.py` | 2 | Exponential backoff decorator success/failure thresholds |
| **Unit** | `tests/unit/test_timezone_conflicts.py` | 3 | Timezone-aware conflict overlapping detection |

**Global fixture** (`tests/conftest.py`): `autouse=True` mock stubs `smtplib.SMTP` for all tests.

---

## 🚀 API Endpoints Summary

### Auth (`/auth`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | ❌ | Register new user |
| POST | `/auth/verify-email?token=X` | ❌ | Verify email |
| POST | `/auth/login` | ❌ | Get JWT |
| GET | `/auth/me` | ✅ | Current user info |
| POST | `/auth/forgot-password` | ❌ | Send reset email |
| POST | `/auth/reset-password` | ❌ | Reset with token |
| GET | `/auth/users/stats` | ✅ | User counts by role |

### Classes (`/api/classes`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/classes` | ✅ | List all classes |
| POST | `/api/classes` | Admin | Create class |
| GET | `/api/classes/{id}` | ✅ | Get single class |
| PUT | `/api/classes/{id}` | Admin | Update class |
| DELETE | `/api/classes/{id}` | Admin | Delete class |
| POST | `/api/classes/sync` | Admin | Sync with Zoom |
| POST | `/api/classes/sync/calendar` | Admin | Sync with GCal |
| GET | `/api/classes/sync/calendar/status` | ✅ | GCal connected? |
| GET | `/api/classes/sync/calendar/auth` | Admin | Get OAuth URL |
| GET | `/api/classes/sync/calendar/callback` | ❌ | OAuth callback |

### AI Agent (`/api/agent`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/agent/chat` | ✅ | Chat with role-based ADK Agent (SSE Stream) |

### AI (`/api/ai`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/ai/parse` | Admin | Parse natural language → class fields |

### Settings (`/api/settings`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/settings` | Admin | Read .env values |
| POST | `/api/settings` | Admin | Update .env values |

### System
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | ❌ | Health check |

---

## 🚨 Known Issues / Technical Debt

| # | Priority | Area | Issue |
|---|---|---|---|
| 1 | 🔴 High | `_pkce_store` | In-memory only — lost on server restart. Fix: Redis / DB-backed store |
| 2 | 🔴 High | Auth routes | No rate limiting — open to brute-force attacks |
| 3 | 🔴 High | SQLite | Not suitable for multi-user production load |
| 4 | 🟡 Medium | `datetime.utcnow()` | Deprecated in Python 3.12 — use `datetime.now(UTC)` |
| 5 | 🟡 Medium | `@app.on_event` | Deprecated in FastAPI — migrate to `lifespan` context manager |
| 6 | 🟡 Medium | Pydantic v1 config | Class-based `Config` deprecated — use `model_config` |
| 7 | 🟡 Medium | No pagination | `/api/classes` returns all records (no limit/offset) |
| 8 | 🟡 Medium | CRM token | `crm_bearer_token` not editable via Settings UI |
| 9 | 🟡 Medium | No JWT refresh | 24h hard expiry, no refresh token flow |
| 10 | 🟡 Medium | `OAUTHLIB_INSECURE_TRANSPORT` | Set to `"1"` at runtime — must be removed in production (HTTPS required) |
| 11 | 🟢 Low | Unverified users | 2 admin accounts stuck unverified in DB |
| 12 | 🟢 Low | Settings hot-reload | Touches `main.py` to trigger uvicorn reload — fragile for production |

---

## 🔑 Key Design Decisions

1. **Zoom is the critical path** — class creation fails immediately if Zoom API fails; the request returns a 502. GCal/Sheets/CRM are fire-and-forget.
2. **Event Bus is fire-and-forget** — all external integrations run as asyncio background tasks. Listener exceptions are swallowed and logged — they never surface to the user.
3. **Rollback on DB failure** — if DB save fails *after* Zoom meeting is created, the code attempts to delete the Zoom meeting before raising a 500.
4. **Graceful stub mode** — every integration (GCal, Sheets, CRM) checks for credentials at call time. Missing credentials → log a warning, return a stub value, never crash.
5. **Timezone-first** — conflict detection uses `zoneinfo` to compare in absolute UTC. Google Calendar API receives times in UTC (not local) to prevent the API's own timezone-shifting bugs.
6. **Denormalized `course_name`** — stored directly on `ClassSession` so the API never needs to join tables for display; updated on course rename via class update.
7. **Settings as live .env editor** — instead of a proper config DB, the settings module reads/writes the actual `.env` file and triggers uvicorn hot-reload by touching `main.py`.
8. **No react-router** — routing is intentionally manual to keep the bundle lean and avoid routing library overhead.
