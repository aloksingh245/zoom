# Zoom Scheduler CRM

A high-performance, professional Class Scheduler CRM designed for educational batches and mentors. This application seamlessly integrates with **Zoom** for automated meeting creation and **Google Calendar** for mentor invites, all wrapped in a premium, animated dashboard.

![Redesigned UI](https://img.shields.io/badge/UI-Modern%20%26%20Animated-blue)
![Theme](https://img.shields.io/badge/Theme-Light%20%26%20Dark%20Mode-blueviolet)

## 🚀 Key Features

- **Automated Zoom Integration:** Automatically creates and updates Zoom meetings with unique join links.
- **Google Calendar Sync:** Sends calendar invites and email notifications directly to mentors.
- **Premium UI/UX:** Built with React and Framer Motion for smooth, staggered animations and fluid transitions.
- **Dark Mode Support:** Fully integrated dark and light themes with persistence.
- **Real-time Schedule:** Interactive dashboard and weekly calendar view to manage sessions efficiently.
- **Course Management:** Organize sessions by batches and tracks.

## 🛠️ Tech Stack

**Frontend:**
- React 19 (TypeScript/JSX)
- Tailwind CSS v4
- Framer Motion (Animations)
- Lucide React (Icons)
- Vite

**Backend:**
- FastAPI (Python)
- SQLAlchemy (Async)
- SQLite
- Zoom Server-to-Server OAuth API
- Google Calendar API v3

---

## ⚙️ Installation & Setup

### 1. Backend Setup
```bash
cd backend
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # Or 'uv sync' if using uv
```

**Configuration:**
Create a `.env` file in the `backend/` folder:
```env
ZOOM_ACCOUNT_ID="your_account_id"
ZOOM_CLIENT_ID="your_client_id"
ZOOM_CLIENT_SECRET="your_client_secret"
ZOOM_USER_ID="your_zoom_email"
TIMEZONE_DEFAULT="Asia/Kolkata"
```

**External Integrations:**
1. **Google Calendar:** Place your `oauth_client.json` (Desktop App type) in the `backend/` folder and run `python google_auth.py` to generate `token.json`.
2. **Zoom:** Create a **Server-to-Server OAuth** app in the [Zoom App Marketplace](https://marketplace.zoom.us/) and enable `meeting:write:admin` scopes.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🏃 Running the Application

**Start Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

## 📝 License
MIT
