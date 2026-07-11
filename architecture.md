# 🏛️ Class Scheduler System Architecture

This document describes the technical architecture and component relationships for the Zoom Class Scheduler application, detailing the data flow, synchronization strategies, API endpoints, and design decisions.

---

## 🎯 Architectural Goals

The Zoom Scheduler coordinates automated Zoom hosting, Google Calendar syncing, Google Sheets reporting, and CRM hooks into a clean, week-view dashboard. 

Key architectural goals include:
1. **Critical Path Isolation**: Synchronous API dependency on Zoom API (v2) only; failure at the Zoom layer rolls back DB transactions and fails the request immediately.
2. **Event-Driven Asynchrony**: Offloading secondary sync tasks (Google Calendar, Google Sheets, CRM) to a local async event bus to prevent HTTP request delays for users.
3. **Graceful Degradation (Stub Mode)**: Secondary integrations auto-degrade into log-only mock stubs if credentials are missing or expired, preventing system crashes.
4. **Timezone Integrity**: Managing IANA timezone string conversions cleanly in UTC to prevent calendar shifting and conflict overlapping.

---

## ⚡ Integration Topology

```
                  ┌───────────────────────────────┐
                  │   Vite React SPA Dashboard    │
                  └───────────────┬───────────────┘
                                  │ HTTP API requests (Bearer JWT)
                                  ▼
                  ┌───────────────────────────────┐
                  │    FastAPI Application Core   │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │ Sync Writes            │ Event Bus (Async)      │ Event Bus (Async)
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ SQLite DB       │      │ Google Calendar │      │ Google Sheets   │
│ (sql_app.db)    │      │ Event Sync      │      │ Logging         │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         ▲                        ▲                        
         │ Rollback on error      │ OAuth PKCE Flow        
         ▼                        ▼                        
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Zoom API (v2)   │      │ token.json      │      │ Partner CRM     │
│ S2S OAuth       │      │ Credentials     │      │ CRM Client      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 🗄️ Core Schema Specifications

### `User` (SQL Table: `users`)
Identifies authenticated administrators, mentors, and student accounts.
* `id`: String (UUID Primary Key)
* `email`: Unique String (indexed)
* `hashed_password`: String (Bcrypt encrypted)
* `role`: Enum String (`"admin"` | `"mentor"` | `"student"`)
* `is_verified`: Boolean (email verification indicator)
* `verification_token`: Optional String (UUID)
* `reset_token`: Optional String (UUID)
* `reset_token_expires`: Optional DateTime (15-minute expiration)

### `ClassSession` (SQL Table: `classes`)
Maintains scheduled sessions mapping directly to Zoom meeting IDs.
* `id`: String (UUID Primary Key)
* `course_id`: Foreign Key (`courses.id`)
* `course_name`: Denormalized String (for high-speed list display)
* `topic_name`: String (non-empty)
* `assignment_name`: Optional String
* `date`: String (`YYYY-MM-DD` representation)
* `start_time`: String (`HH:MM` 24-hr representation)
* `duration_minutes`: Integer (default 90)
* `timezone`: IANA Timezone String (e.g., `Asia/Kolkata`)
* `zoom_meeting_id`: String (Zoom identifier)
* `zoom_join_url`: String (Direct Zoom link)
* `calendar_event_id`: Optional String (Google Calendar Event ID)
* `sheet_row_id`: Optional String (Google Sheet spreadsheet row identifier)
* `mentor_email`: Optional String (Mentor assigned)

---

## 🌐 API Routing Layout

### 1. Authentication Router (`/auth`)
* `POST /auth/signup`: User register (unverified by default).
* `POST /auth/verify-email`: Activates user via email token.
* `POST /auth/login`: Generates 24-hour expiration JWT bearer tokens.
* `GET /auth/me`: Decodes JWT payload and returns user context.
* `POST /auth/forgot-password` / `POST /auth/reset-password`: Manages secure token-based password reset lifecycles.

### 2. Classes CRUD & Sync (`/api/classes`)
* `GET /api/classes`: Returns upcoming scheduled sessions (filtered based on roles).
* `POST /api/classes` (Admin Only): Synchronously creates Zoom meeting, saves class, and triggers event bus.
* `PUT /api/classes/{id}` (Admin Only): Updates class and pushes edits to Zoom.
* `DELETE /api/classes/{id}` (Admin Only): Cancels Zoom meeting and removes DB record.
* `POST /api/classes/sync`: Syncs local database with Zoom API.
* `POST /api/classes/sync/calendar`: Pulls updates from Google Calendar.

### 3. Settings Router (`/api/settings` - Admin Only)
* `GET /api/settings`: Reads environment values (masks confidential credentials).
* `POST /api/settings`: Rewrites `.env` live and touches `main.py` to trigger Uvicorn reload.
