# Mini Class Scheduler POC Architecture

## Goal
Schedule 1.5-hour classes for courses with CRUD in a week-view calendar UI. Each class creates a Zoom meeting; edits update the Zoom meeting. Zoom meeting ID and join link are stored with the class. In-memory storage only (no DB).

## Tech Stack
- Frontend: React + Vite + Tailwind
- Backend: FastAPI + uvicorn
- External: Zoom REST API

## Key Requirements (Confirmed)
- Zoom auth: static Bearer token supplied by you (no separate auth flow).
- Single Zoom host/user (no multiple instructors).
- No recurring classes for now.
- Assignment name is optional.
- Multiple classes can exist in the same time slot (no conflict blocking).
- Calendar is week view; selecting a date shows a list of classes for that date below the calendar.

## High-Level Components
- Frontend SPA
  - Week calendar grid
  - Date selection to filter list below
  - Class create/edit modal or drawer
- Backend API (FastAPI)
  - CRUD endpoints for classes and courses
  - Zoom integration service
- In-memory store
  - Dicts for courses and classes

## Core Data Model (POC)
ClassSession
- id (uuid)
- course_id
- course_name (denormalized for UI display)
- topic_name
- assignment_name (optional)
- date (YYYY-MM-DD)
- start_time (HH:mm)
- duration_minutes = 90 (fixed)
- timezone (IANA string, e.g. America/Los_Angeles)
- zoom_meeting_id
- zoom_join_url
- created_at / updated_at

Course
- id (uuid)
- name

## Frontend UX
- Week view calendar with time slots.
- Clicking a slot opens create form with date/time prefilled.
- Clicking an existing class opens edit mode.
- Date picker or click in week header sets "selected date".
- List below calendar shows all classes on selected date (ordered by time).

## Backend API (POC)
- GET /api/courses
- POST /api/courses
- GET /api/classes
- GET /api/classes/{id}
- POST /api/classes
  - Validates duration fixed at 90 minutes
  - Creates Zoom meeting and stores meeting ID/join URL
- PUT /api/classes/{id}
  - Updates Zoom meeting
  - Updates stored class
- DELETE /api/classes/{id}
  - Deletes Zoom meeting
  - Removes class

## Zoom Integration (Minimal POC)
- Create meeting: POST /v2/users/{userId}/meetings
- Update meeting: PATCH /v2/meetings/{meetingId}
- Delete meeting: DELETE /v2/meetings/{meetingId}
- Use provided Bearer token in Authorization header.
- Store meeting id and join_url from response.

## Error Handling
- Zoom failure => return 502 with error details.
- Validation errors => 400.
- No conflict checks (overlaps allowed by requirement).

## Security (POC)
- No end-user auth.
- Bearer token stored in server env (e.g. ZOOM_BEARER_TOKEN).

## Future Enhancements (Out of Scope)
- Persistent DB storage.
- Recurring classes.
- Multi-user or per-instructor Zoom auth.
- Conflict checking.

