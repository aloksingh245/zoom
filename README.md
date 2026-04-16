# 🗓️ Zoom Class Scheduler POC

A sophisticated, full-stack Class Scheduling system featuring real-time **Zoom Integration**, **AI-Powered Scheduling**, and **Secure Multi-User Authentication**. Built with a professional event-driven architecture.

---

## 🚀 Key Features

- **🔐 Multi-User Authentication**: Complete Signup/Login flow with real-world **Email OTP Verification** (Gmail SMTP).
- **🛡️ Ownership Protection**: Shared visibility calendar where users can see all classes but **only the creator** can edit or delete them.
- **📹 Zoom Integration**: Automatic creation, updating, and deletion of Zoom Meetings synchronized with the app.
- **🤖 AI Scheduler**: LLaMA 3.1 powered assistant that understands natural language to schedule classes instantly.
- **📅 Visual Calendar**: Beautiful week-view grid with real-time status indicators (Live, Upcoming, Completed).
- **🔄 Google Sync**: Background synchronization with Google Calendar and Google Sheets via an internal Event Bus.

---

## 🏗️ Technical Architecture

### **Backend (FastAPI)**
The backend follows a decoupled, event-driven design:
- **Core Path**: Synchronous CRUD operations and Zoom API communication.
- **Event Bus**: An internal publisher-subscriber system that triggers side effects (GCal/Sheets sync) without blocking the main request.
- **Security**: JWT (JSON Web Token) based stateless authentication with Bcrypt password hashing.

### **Frontend (React + Vite + Tailwind)**
- **State Management**: Custom React hooks (`useClasses`, `useCourses`) for clean logic separation.
- **UI Components**: Framer Motion animations, Lucide icons, and a responsive glassmorphic design.

---

## 🗄️ Database Schema (SQLite)

The system uses SQLAlchemy with `aiosqlite` for asynchronous database operations.

### **Users Table**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (String) | Primary Key |
| `name` | String | User's full name |
| `email` | String | Unique email address |
| `hashedPassword` | String | Bcrypt hashed password |
| `isVerified` | Boolean | True after OTP success |

### **Classes Table**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (String) | Primary Key |
| `topic_name` | String | Title of the class |
| `zoom_join_url` | String | Direct link to Zoom |
| `owner_id` | String | Foreign Key to User ID |
| `mentor_email` | String | Optional guest email |
| `date / start_time` | String | ISO formatted timing |

---

## 🔌 Integrations & API Keys

To run this project, configure the following keys in `backend/.env`:

| Service | Key Needed | Purpose |
| :--- | :--- | :--- |
| **Zoom** | `ZOOM_CLIENT_ID`, `SECRET` | Server-to-Server OAuth for meetings |
| **Groq** | `GROQ_API_KEY` | Powers the LLaMA 3.1 AI Assistant |
| **Gmail** | `SMTP_PASSWORD` | Sends real OTP emails (App Password) |
| **Google** | `credentials.json` | Google Calendar & Sheets API access |

---

## 🛠️ Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Configure .env with your keys
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📝 Demo Example: AI Scheduling

**User Chat:**
> "Hey, schedule a Physics class for tomorrow at 5 PM. Mentor email is alok@example.com"

**AI Action (Internal JSON):**
```json
{
  "course_name": "Physics",
  "topic_name": "Introduction",
  "date": "2026-04-15",
  "start_time": "17:00",
  "mentor_email": "alok@example.com",
  "AUTO_EXECUTE": true
}
```
**Result:**
1. User receives a 200 OK.
2. Zoom Meeting is created instantly.
3. Google Calendar invite is sent to `alok@example.com` in the background.
4. Meeting appears on the visual calendar for all users.

---

## 📂 Project Structure
```text
├── backend/
│   ├── core/           # Security, Database config, Event Bus
│   ├── integrations/   # Zoom, GCal, Google Sheets clients
│   ├── modules/        # Auth, Classes, Courses, AI logic
│   ├── tests/          # Automated test suite
│   └── main.py         # Entry point
└── frontend/
    ├── src/
    │   ├── components/ # Atomic UI components (Calendar, Auth, AI)
    │   ├── hooks/      # Business logic hooks
    │   └── services/   # API communication layer
```

---
*Created as a professional POC for high-efficiency educational scheduling.*
