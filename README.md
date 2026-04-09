# 🚀 Zoom Scheduler CRM & AI Assistant

A modern, high-performance Class Scheduler CRM designed for educators, mentors, and administrators. This application acts as a centralized command center to schedule sessions, automatically generate Zoom meetings, invite mentors via Google Calendar, and log records into Google Sheets—all powered by a decoupled, event-driven backend and a gorgeous, animated React frontend. 

Additionally, it features an integrated **AI Assistant** (powered by Groq & LLaMA 3.1) capable of natural language processing to automatically schedule and resolve timeline conflicts.

![UI-Modern & Animated](https://img.shields.io/badge/UI-Modern%20%26%20Animated-blue)
![Theme-Light & Dark Mode](https://img.shields.io/badge/Theme-Light%20%26%20Dark%20Mode-blueviolet)
![Architecture-Event Driven](https://img.shields.io/badge/Architecture-Event%20Driven-success)

---

## ✨ Key Features

### 🤖 AI-Powered Scheduling
*   **Integrated Groq AI (LLaMA 3.1):** A floating AI chat assistant helps you manage schedules through natural language.
*   **Auto-Execution:** The AI can extract entities (Course, Topic, Date, Time) from conversational text, check for scheduling conflicts, and automatically dispatch a creation payload to the backend without manual form filling.

### ⚙️ Event-Driven Backend Architecture
*   **Decoupled Integrations:** Core business logic is isolated from third-party APIs using an asynchronous `EventBus`. When a class is created, `class_created` events fire off background tasks.
*   **Automated Zoom Sync:** Creates, updates, and deletes Zoom meetings dynamically via Server-to-Server OAuth. Includes a bidirectional sync endpoint to fetch manually created Zoom meetings.
*   **Google Ecosystem Integrations:**
    *   **Google Calendar:** Automatically sends invites/updates to assigned mentors based on timezone-aware scheduling.
    *   **Google Sheets:** Automatically appends scheduled class logs for administrative auditing.
*   **Resilience:** API calls to external services are fortified with custom async retry decorators and exponential backoff mechanisms.

### 🎨 Premium Frontend Experience
*   **Fluid Animations:** Built with `framer-motion` for staggered list rendering, smooth page transitions, and interactive hover states.
*   **Custom Calendar View:** A bespoke, timezone-aware week-view calendar grid that visualizes class durations, overlaps, and current time blocks.
*   **Theming:** Full dark/light mode persistence with automatic Tailwind v4 styling integration.

---

## 🛠️ Tech Stack

### Frontend (`@frontend`)
*   **Framework:** React 19 + Vite
*   **Styling:** Tailwind CSS v4 + Tailwind Merge + clsx
*   **Animations:** Framer Motion
*   **Icons:** Lucide React
*   **Routing & State:** Custom React Hooks (`useClasses`, `useCourses`)

### Backend (`@backend`)
*   **Framework:** FastAPI (Python 3.11+)
*   **Database:** SQLite + `aiosqlite` + SQLAlchemy 2.0 (Async Session paradigm)
*   **AI:** Groq Cloud API (`llama-3.1-8b-instant`)
*   **Integrations:** Zoom API v2, Google API Client (`aiogoogle`, `google-auth`)
*   **Validation:** Pydantic V2

---

## 🚀 Installation & Setup

### Prerequisites
*   Node.js 20+
*   Python 3.10+
*   [uv](https://github.com/astral-sh/uv) (optional but recommended for fast Python package installation)

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory using `.env.example` as a template:
```env
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_USER_ID=your_zoom_email@domain.com
TIMEZONE_DEFAULT=Asia/Kolkata
CORS_ALLOW_ORIGINS=http://localhost:5173
GROQ_API_KEY=your_groq_api_key
```

**Google Credentials (OAuth & Service Account):**
1. Ensure you have your `oauth_client.json` (Desktop App format) for Google Calendar inside the `backend/` folder.
2. Run the manual auth script once to generate `token.json`:
   ```bash
   python google_auth.py
   ```
3. *(Optional)* Add `credentials.json` (Service Account) to the backend root to enable Google Sheets logging.

**Start the Backend Server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
npm install
```

**Start the Frontend Server:**
```bash
npm run dev
```

Your frontend should now be running on `http://localhost:5173`.

---

## 🧪 Testing

The backend includes a suite of tests for ensuring integration reliability and checking conflict resolution algorithms.
```bash
cd backend
pytest -v
```
Included tests cover: Timezone overlaps (`test_timezone_conflicts.py`), Google Calendar rollbacks (`test_rollback.py`), Event Bus behavior (`test_event_bus.py`), and API credentials (`test_zoom_creds.py`).

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
