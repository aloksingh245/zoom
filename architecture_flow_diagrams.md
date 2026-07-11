# 🧠 Zoom Class Scheduler — Architecture Flow Diagrams

This document contains detailed visual flow diagrams illustrating the high-level architecture, component interaction, state transition states, event loops, and sync fallbacks of the **Zoom Class Scheduler** project.

---

## 1. High-Level Component & Data Flow

This diagram illustrates how React frontend clients interact with FastAPI backend gateways, local database stores, and third-party APIs (Zoom, Google APIs, SMTP, CRM).

```mermaid
graph TD
    subgraph Client [Frontend React SPA]
        UI[Week Calendar / Dashboard]
        AgentBubble[RAG AI Chat Assistant]
    end

    subgraph API_Gateway [FastAPI Gateway]
        Router[Router Dispatcher]
        AuthGuard[JWT Auth Guard]
        EventBus[In-Memory Event Bus]
    end

    subgraph Local_Store [Local Storage]
        DB[(SQLite sql_app.db)]
        VectorDB[(ChromaDB RAG Index)]
    end

    subgraph Integrations [External Integration Services]
        Zoom[Zoom API v2 - Server-to-Server OAuth]
        GCal[Google Calendar API - User OAuth PKCE]
        GSheets[Google Sheets API - Service Account]
        CRM[Partner CRM API - Webhook Bearer]
        SMTP[Gmail SMTP - App Verification Mail]
    end

    UI -- HTTP JWT Requests --> Router
    AgentBubble -- SSE Stream --> Router
    Router --> AuthGuard
    AuthGuard -- Read/Write --> DB
    Router -- Embeddings Retrieval --> VectorDB
    
    %% Synchronous Paths
    Router -- "Sync CRUD (Critical Path)" --> Zoom
    Router -- "SMTP Mail dispatch" --> SMTP
    
    %% Asynchronous Event Bus Paths
    Router -- "Emit Event" --> EventBus
    EventBus -- "Task: Update Calendar" --> GCal
    EventBus -- "Task: Log Session" --> GSheets
    EventBus -- "Task: Update Webhook" --> CRM

    GCal -- "Write calendar_event_id" --> DB
    GSheets -- "Write sheet_row_id" --> DB
```

---

## 2. Ticket State Transition Flow

This state machine details how a Scheduled Class Session moves from form creation to full multi-service integration synchronization, updates, and cancellation.

```mermaid
stateDiagram-v2
    [*] --> DRAFT : Admin submits Schedule Form
    
    state DRAFT {
        [*] --> Validate_Conflict : Check Timezone overlap in DB
        Validate_Conflict --> Validate_Not_Past : Time is free
        Validate_Not_Past --> ZOOM_PROVISIONING : Date/Time is in future
    }
    
    state ZOOM_PROVISIONING {
        [*] --> Request_S2S_OAuth : Generate access_token
        Request_S2S_OAuth --> API_Create_Meeting : POST /v2/users/{id}/meetings
    }
    
    ZOOM_PROVISIONING --> ROLLBACK : Zoom API fails (4xx/5xx)
    ROLLBACK --> [*] : Transaction Aborted (502 Bad Gateway)
    
    ZOOM_PROVISIONING --> SQLite_COMMIT : Zoom Created (Meeting ID + Link)
    
    state SQLite_COMMIT {
        [*] --> Write_Class_Session : Save Zoom credentials in DB
    }
    
    SQLite_COMMIT --> SQLite_ROLLBACK_ZOOM : SQLite Commit fails
    SQLite_ROLLBACK_ZOOM --> [*] : Synchronous Delete Zoom Meeting (500 Error)
    
    SQLite_COMMIT --> EVENT_BUS_DISPATCH : SQLite Commit Success (201 Created)
    
    state EVENT_BUS_DISPATCH {
        [*] --> Emit_Class_Created : Non-blocking background workers spawn
        Emit_Class_Created --> Google_Calendar_Sync : Task 1
        Emit_Class_Created --> Google_Sheets_Sync : Task 2
        Emit_Class_Created --> CRM_Webhook_Sync : Task 3
    }
    
    state Google_Calendar_Sync {
        [*] --> GCal_UTC_Convert : Astimezone to UTC
        GCal_UTC_Convert --> GCal_Event_Create : POST /calendar/v3/events
        GCal_Event_Create --> GCal_DB_Update : Save calendar_event_id
    }
    
    state Google_Sheets_Sync {
        [*] --> Sheets_Row_Structure : Map columns
        Sheets_Row_Structure --> GSheets_Append : Append row to Sheet1
        GSheets_Append --> GSheets_DB_Update : Save sheet_row_id
    }
    
    state CRM_Webhook_Sync {
        [*] --> CRM_Map_Payload : Format CRM JSON schema
        CRM_Map_Payload --> CRM_POST_Request : POST /classes
    }
    
    Google_Calendar_Sync --> FULLY_SYNCED
    Google_Sheets_Sync --> FULLY_SYNCED
    CRM_Webhook_Sync --> FULLY_SYNCED
    
    FULLY_SYNCED --> UPDATE_PENDING : Admin edits Class Session
    UPDATE_PENDING --> SQLite_COMMIT : Sync Update Zoom -> Update DB -> Dispatch Events
    
    FULLY_SYNCED --> DELETE_PENDING : Admin deletes Class Session
    DELETE_PENDING --> SQLite_COMMIT : Zoom Delete -> DB Delete -> Dispatch Deleted Events -> [*]
```

---

## 3. Real-Time Integration Sync Loop (Event Bus)

This sequence diagram shows the precise, timeline execution of events when an Admin schedules a class session. It highlights how the Zoom API acts as the synchronous gateway, while other integrations execute in non-blocking background workers.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Admin (Frontend)
    participant API as FastAPI Router
    participant DB as SQLite Database
    participant Zoom as Zoom Service
    participant Bus as Event Bus
    participant GCal as GCal Task
    participant GSheets as GSheets Task
    participant CRM as CRM Task

    Admin->>API: POST /api/classes (JSON payload)
    Note over API: Run validation checks & database conflict checks
    API->>Zoom: create_meeting(topic, start_time, duration, timezone)
    activate Zoom
    Zoom-->>API: returns Zoom JSON (meeting_id, join_url)
    deactivate Zoom
    
    API->>DB: INSERT ClassSession details + Zoom credentials
    activate DB
    DB-->>API: commit successful
    deactivate DB
    
    API->>Bus: emit("class_created", class_session_data)
    
    %% Return immediate response to the client
    API-->>Admin: HTTP 201 Created (returns ClassSession details)
    
    Note over Bus: EventBus creates async tasks concurrently in background
    
    par Task 1: Google Calendar
        Bus->>GCal: execute GCal listener
        activate GCal
        GCal->>GCal: convert time to UTC
        GCal->>GCal: fetch token.json (OAuth)
        GCal-->>GCal: [Fallback: stub mode if token expired/missing]
        GCal->>DB: UPDATE ClassSession (set calendar_event_id)
        deactivate GCal
    and Task 2: Google Sheets
        Bus->>GSheets: execute Sheets listener
        activate GSheets
        GSheets->>GSheets: load Service Account credentials
        GSheets-->>GSheets: [Fallback: stub mode if keys missing]
        GSheets->>DB: UPDATE ClassSession (set sheet_row_id)
        deactivate GSheets
    and Task 3: CRM Webhook
        Bus->>CRM: execute CRM listener
        activate CRM
        CRM->>CRM: load settings.crm_bearer_token
        CRM-->>CRM: [Fallback: stub mode if token is empty]
        deactivate CRM
    end
```

---

## 4. Manual Sync & Surgical Fallback Flow

This flowchart illustrates the logic flow triggered when an administrator executes a manual Zoom synchronization. It highlights the automatic shift from bulk list comparisons to individual checks if Zoom permissions restrict standard listing.

```mermaid
flowchart TD
    Start([Admin triggers Zoom Sync]) --> AuthCheck{"Zoom S2S credentials present?"}
    AuthCheck -- No --> Warn[Log warning & return HTTP 401/403] --> End([Sync Finished])
    AuthCheck -- Yes --> FetchLocal[Fetch all local Classes from SQLite]
    
    FetchLocal --> AttemptBulk{"Attempt Bulk List:<br>GET /users/{userId}/meetings"}
    
    %% Bulk Path
    AttemptBulk -- Success (200 OK) --> CompareBulk[Compare local Zoom IDs with retrieved list]
    CompareBulk --> LoopBulk{"Iterate local records"}
    
    LoopBulk -- "ID exists in local DB but missing on Zoom" --> DeleteLocal[Delete Class locally + delete GCal event]
    LoopBulk -- "ID exists on Zoom but missing in local DB" --> ImportLocal[Import session into SQLite under 'Synced from Zoom']
    LoopBulk -- "IDs match" --> KeepLocal[Keep class unchanged]
    
    DeleteLocal --> CheckLoopBulk{More items?}
    ImportLocal --> CheckLoopBulk
    KeepLocal --> CheckLoopBulk
    
    CheckLoopBulk -- Yes --> LoopBulk
    CheckLoopBulk -- No --> SuccessEnd[Return status: bulk_sync successful] --> End
    
    %% Fallback Path
    AttemptBulk -- "Failure (403 Forbidden / 401)" --> WarnFallback[Log Warning: Bulk Listing blocked.<br>Switching to Surgical Sync Fallback]
    
    WarnFallback --> LoopSurgical{"Iterate each local Class session"}
    LoopSurgical --> GetMeeting{"GET /meetings/{meetingId}"}
    
    GetMeeting -- "Success (200 OK)" --> KeepSurgical[Keep class unchanged]
    GetMeeting -- "Failure (404 Not Found)" --> DeleteSurgical[Delete class from local SQLite + remove GCal event]
    GetMeeting -- "Other Error (Rate limit/Expired)" --> LogSurgical[Log error & skip class]
    
    KeepSurgical --> CheckLoopSurgical{More local classes?}
    DeleteSurgical --> CheckLoopSurgical
    LogSurgical --> CheckLoopSurgical
    
    CheckLoopSurgical -- Yes --> LoopSurgical
    CheckLoopSurgical -- No --> FallbackEnd[Return status: surgical_sync fallback completed] --> End
```
