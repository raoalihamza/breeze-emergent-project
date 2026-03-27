# Zinnia SmartOffice Integration - Technical Documentation

**Project:** Breeze Atlas CRM
**Integration:** Zinnia SmartOffice XML API
**Completed:** March 2026 (Milestones 1–4)
**Database:** MongoDB (`breeze_atlas`)
**Backend:** FastAPI + Motor (async MongoDB driver)
**Frontend:** React + Tailwind CSS

---

## Table of Contents

1. [Overview](#overview)
2. [Project Setup](#project-setup)
3. [Environment Variables](#environment-variables)
4. [MongoDB Collections](#mongodb-collections)
5. [Background Async Operations](#background-async-operations)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Agent Matching Engine](#agent-matching-engine)
8. [Scheduler System](#scheduler-system)
9. [Frontend - ZinniaAdmin Panel](#frontend--zinninadmin-panel)
10. [Production Switch Checklist](#production-switch-checklist)
11. [Data Flow Diagrams](#data-flow-diagrams)

---

## Overview

The Zinnia integration connects **Breeze Atlas CRM** to **SmartOffice** (Zinnia's agent management platform) via an XML-based REST API. It:

- Fetches **260,000+ agent contacts**, **304 policies**, and **842 activities** from SmartOffice
- Stores all data in MongoDB using memory-efficient bulk upserts (one page at a time - never holds all 260K records in RAM)
- Automatically **links SmartOffice agents to Atlas users** using NPN matching, exact name matching, and fuzzy name matching
- Runs on an **automated schedule** (agents every 6h, production every 1h, cases every 30min)
- Provides an **Admin UI** (`/zinnia-admin`) to monitor sync status, review unmatched agents, manually match them, and trigger re-syncs

---

## Project Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 6+ (running locally or Atlas)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials (see Environment Variables section)

# Start the backend
uvicorn server:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm start
# Runs on http://localhost:3000
```

### Default Admin Credentials

```
Email:    kyle@breezewealthmanagement.com
Password: Breeze2026!
```

Navigate to **Settings → Zinnia Admin** (or `/zinnia-admin`) after logging in.

---

## Environment Variables

### `backend/.env`

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=breeze_atlas

# Auth
JWT_SECRET=your-jwt-secret-key
CORS_ORIGINS=*

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxx
SENDER_EMAIL=Atlas <support@mail.breezeatlas.com>
APP_DOMAIN=https://breezeatlas.com

# ── Zinnia SmartOffice ──────────────────────────────────────
# For PRODUCTION, change ZINNIA_API_URL and credentials below
ZINNIA_API_URL=https://api.sandbox.smartofficecrm.com/bwm/v1/send
ZINNIA_API_KEY=your-api-key
ZINNIA_API_SECRET=your-api-secret
ZINNIA_SITE_NAME=PREPRODNEW
ZINNIA_USERNAME=PREPRODNEW_SDC_UAT_bbrandon
```

### `frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## MongoDB Collections

### `zinnia_agents`
Stores all SmartOffice agent/contact records.

| Field | Type | Description |
|---|---|---|
| `smartoffice_id` | string (unique) | SmartOffice internal contact ID |
| `smartoffice_raw_id` | string | Full raw ID from XML (e.g. `Contact.12345`) |
| `first_name` | string | Normalized (Title Case) |
| `last_name` | string | Normalized (Title Case) |
| `npn` | string | National Producer Number |
| `contact_type` | string | e.g. "Agent", "Broker" |
| `atlas_user_id` | string | Linked Atlas user ID (set after matching) |
| `match_type` | string | `npn` / `name_exact` / `name_fuzzy:0.92` / `manual` |
| `matched_at` | ISO timestamp | When the match was made |
| `synced_at` | ISO timestamp | Last sync time |
| `source` | string | Always `"smartoffice"` |

**Indexes:** `smartoffice_id` (unique), `npn`, `atlas_user_id` (sparse), `match_type` (sparse)

---

### `zinnia_unmatched`
Agents that could not be automatically matched to any Atlas user.

| Field | Type | Description |
|---|---|---|
| `smartoffice_id` | string (unique) | SmartOffice contact ID |
| `first_name` / `last_name` | string | Agent name |
| `npn` | string | NPN if available |
| `contact_type` | string | Contact type |
| `reason` | string | Why matching failed (e.g. `no_npn, name_not_matched`) |
| `reviewed` | boolean | Has admin reviewed this record |
| `dismissed` | boolean | Has admin dismissed this record |
| `dismissed_at` | ISO timestamp | When dismissed |
| `dismissed_by` | string | Atlas user ID of admin who dismissed |
| `created_at` | ISO timestamp | When added to unmatched |

**Indexes:** `smartoffice_id` (unique), `(reviewed, dismissed)` compound

---

### `zinnia_production`
SmartOffice policy/production records.

| Field | Type | Description |
|---|---|---|
| `smartoffice_id` | string (unique) | Policy ID |
| `policy_number` | string | Policy number |
| `carrier_name` | string | Insurance carrier |
| `annual_premium` | string | Annual premium amount |
| `insured_name` | string | Name of insured person |
| `synced_at` | ISO timestamp | Last sync time |

---

### `zinnia_cases`
SmartOffice activity/case records.

| Field | Type | Description |
|---|---|---|
| `smartoffice_id` | string (unique) | Activity ID |
| `subject` | string | Activity subject |
| `activity_type` | string | Type of activity |
| `synced_at` | ISO timestamp | Last sync time |

---

### `zinnia_sync_logs`
Audit log of every sync operation.

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique log ID |
| `sync_type` | string | `agents` / `production` / `cases` / `agent_matching` |
| `status` | string | `success` / `failed` |
| `details` | object | `{total_fetched, upserted, modified, pages, error}` |
| `timestamp` | ISO timestamp | When logged |

**Indexes:** `(timestamp DESC)`, `(status, timestamp DESC)`

---

### `zinnia_sync_state`
Tracks last successful sync metadata per data type.

| Field | Type | Description |
|---|---|---|
| `sync_type` | string | `agents` / `production` / `cases` |
| `initial_sync_done` | boolean | Has full initial sync completed |
| `last_sync_time` | ISO timestamp | Last successful sync |
| `total_records` | number | Records fetched in last run |
| `pages` | number | Pages fetched in last run |

---

## Background Async Operations

All heavy operations run **asynchronously in the background** - API requests complete immediately and return a status, while the actual work happens in a separate asyncio task.

### 1. Paginated Sync (`_paginated_sync`)

The core sync engine used by all three data types:

```
Request Page 0 → Parse XML → Bulk upsert to MongoDB → Delay 0.3s
Request Page 1 → Parse XML → Bulk upsert to MongoDB → Delay 0.3s
...
Request Page N → Parse XML → Bulk upsert to MongoDB → Done
```

**Key design decisions:**
- **Page size:** 100 records per API request
- **Memory usage:** Only 1 page (100 records) held in memory at any time - never loads all 260K into RAM
- **Delay between pages:** 0.3 seconds to avoid overwhelming SmartOffice API
- **Retry logic:** Up to 8 retries for network errors (30–60s backoff), 3 retries for API errors (2–6s backoff)
- **Concurrency locks:** `asyncio.Lock()` per data type prevents two syncs of the same type running simultaneously
- **Live progress:** `_sync_progress` dict updated after every page - frontend polls and shows progress bar

### 2. Agent Matching (`run_agent_matching`)

Runs after every agent sync, and can be triggered manually:

```
1. Load ALL Atlas users into memory (small set - never millions)
2. Build O(1) lookup dicts:
   - npn_lookup: {npn → user}
   - name_lookup: {first_last → user}
   - name_list: [(full_name, user), ...] for fuzzy matching
3. Stream zinnia_agents via MongoDB cursor (no skip() - memory safe)
4. For each agent:
   a. NPN match → exact lookup → matched
   b. Exact name match → dict lookup → matched
   c. Fuzzy name match → SequenceMatcher ratio ≥ 0.85 → matched
   d. No match → insert into zinnia_unmatched
5. Flush bulk writes every 1000 records (BATCH_SIZE)
6. Log final result to zinnia_sync_logs
```

**Matching threshold:** 0.85 (85% string similarity via `difflib.SequenceMatcher`)

**Lock behavior:** Matching runs **outside** the agent sync lock - sync releases the lock immediately after DB update, then matching starts in background. This means a new agent sync can be triggered immediately even while matching is running.

### 3. Bulk Upsert (`bulk_upsert`)

Used by all sync functions to save records to MongoDB:

- Uses `UpdateOne` with `upsert=True` - inserts new records, updates existing ones
- `$setOnInsert` ensures each new record gets a UUID `id` field
- `ordered=False` - continues on error, maximizes throughput
- Returns `{upserted, modified}` counts

### 4. Scheduler (`start_all_schedulers`)

Four concurrent schedulers run as background asyncio tasks from server startup:

| Scheduler | Frequency | Stagger |
|---|---|---|
| `_agents_scheduler` | Every 6 hours | Immediate |
| `_production_scheduler` | Every 1 hour | 2 min after start |
| `_cases_scheduler` | Every 30 minutes | 4 min after start |
| `_reconciliation_scheduler` | Daily at 3 AM UTC | Waits until 3 AM |

Each scheduler uses `_run_with_retry` - 3 attempts with 5min/10min backoff. On total failure, sends email alert to admin.

---

## API Endpoints Reference

All endpoints require **JWT authentication** and **admin role**.

Base URL: `http://localhost:8000/api`

### Sync Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/zinnia/sync` | Trigger full sync (all 3 types) |
| `POST` | `/zinnia/sync/deep` | Fire-and-forget deep re-fetch from SmartOffice |
| `POST` | `/zinnia/sync/agents` | Sync agents only |
| `POST` | `/zinnia/sync/production` | Sync production/policies only |
| `POST` | `/zinnia/sync/cases` | Sync activities/cases only |
| `GET` | `/zinnia/sync/status` | Get live sync status + progress for all types |

**`GET /zinnia/sync/status` response:**
```json
{
  "agents": {
    "is_running": false,
    "initial_sync_done": true,
    "last_sync_time": "2026-03-27T03:00:00Z",
    "total_records": 260525,
    "last_sync_fetched": 260525,
    "progress": {}
  },
  "production": { ... },
  "cases": { ... }
}
```

---

### Log Endpoints

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/zinnia/logs` | `since`, `status`, `limit` | Get sync audit logs |

**Example:** `GET /zinnia/logs?since=2025-11-01T00:00:00&status=failed&limit=50`

---

### Agent Data Endpoints

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/zinnia/agents` | - | Get all agents (up to 1000) |
| `GET` | `/zinnia/production` | - | Get production records (up to 1000) |
| `GET` | `/zinnia/matched` | `page`, `page_size`, `search` | Get matched agents (paginated) |
| `GET` | `/zinnia/unmatched` | `page`, `page_size`, `search` | Get unmatched agents (paginated) |

**Pagination response format:**
```json
{
  "data": [...],
  "total": 1250,
  "page": 1,
  "page_size": 25,
  "total_pages": 50
}
```

---

### Matching Endpoints

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/zinnia/match/agents` | - | Start agent matching in background |
| `GET` | `/zinnia/match/status` | - | Get live matching progress |
| `POST` | `/zinnia/unmatched/{id}/match` | `{atlas_user_id}` | Manually match an unmatched agent |
| `POST` | `/zinnia/unmatched/{id}/dismiss` | - | Dismiss an unmatched record |

**`GET /zinnia/match/status` response:**
```json
{
  "status": "complete",
  "total_processed": 260525,
  "matched_by_npn": 180000,
  "matched_by_name": 45000,
  "unmatched": 35525,
  "started_at": "2026-03-27T03:05:00Z",
  "completed_at": "2026-03-27T03:18:00Z",
  "error": null
}
```

---

### User Search & Health

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/zinnia/users/search` | `q` | Search Atlas users by name or NPN |
| `GET` | `/zinnia/health` | - | Verify SmartOffice API connectivity |

**`GET /zinnia/health` response:**
```json
{
  "status": "ok",
  "api_url": "https://api.sandbox.smartofficecrm.com/bwm/v1/send",
  "response_time_ms": 342,
  "http_status": 200
}
```

---

## Agent Matching Engine

### Matching Priority Order

```
Agent from SmartOffice
        │
        ▼
1. NPN Match ──────────────── Does agent NPN exist in Atlas users?
        │                              YES → match_type: "npn"
        │ NO
        ▼
2. Exact Name Match ─────────  "john doe" == Atlas user "John Doe"?
        │                              YES → match_type: "name_exact"
        │ NO
        ▼
3. Fuzzy Name Match ─────────  SequenceMatcher ratio ≥ 0.85?
        │                              YES → match_type: "name_fuzzy:0.92"
        │ NO
        ▼
4. Unmatched ────────────────  Insert into zinnia_unmatched
                                       reason: "no_npn, name_not_matched"
```

### Data Normalization

Before matching, all data is normalized:

| Input | Normalized Output |
|---|---|
| `"john doe"` | `"John Doe"` (Title Case) |
| `"(555) 123-4567"` | `"+15551234567"` (E.164) |
| `"01/15/2024"` | `"2024-01-15T00:00:00Z"` (ISO 8601) |

### Manual Override

Admin can manually match any unmatched agent via the UI:
1. Search Atlas users by name or NPN
2. Select the correct user
3. Click "Confirm Match" → `match_type` set to `"manual"`
4. Record removed from `zinnia_unmatched`

---

## Scheduler System

```
Server Startup
      │
      ├── asyncio.create_task(start_all_schedulers())
      │
      ├── _agents_scheduler()      ─── runs every 6 hours
      │         └── _run_with_retry(sync_agents, max_attempts=3)
      │                  └── Attempt 1 → wait 5min → Attempt 2 → wait 10min → Attempt 3
      │                  └── All fail → log + email alert
      │
      ├── _production_scheduler()  ─── wait 2min → runs every 1 hour
      │
      ├── _cases_scheduler()       ─── wait 4min → runs every 30 minutes
      │
      └── _reconciliation_scheduler() ─── waits until 3:00 AM UTC → runs daily
```

**Concurrency protection:** Each scheduler checks the asyncio lock before running. If a sync is already in progress (e.g., triggered manually), the scheduler skips that cycle.

**Email alerts:** On complete failure (all retries exhausted), `send_sync_failure_email` fires automatically to `kyle@breezewealthmanagement.com`.

---

## Frontend - ZinniaAdmin Panel

**Route:** `/zinnia-admin`
**File:** `frontend/src/pages/ZinniaAdmin.js`
**Access:** Admin role only

### Tab 1 - Sync Status

- **3 stat cards** - Agents / Policies / Activities with record count, last sync time
- **Live progress bar** - updates every 5 seconds during sync showing `current_page / total_pages`
- **Matching card** - shows last matching result + "Run Matching" button (DB only, no SmartOffice call)
- **Sync History table** - all sync logs since Nov 2025 with status badges
- **Refresh button** - reloads data from MongoDB (no SmartOffice call)
- **Deep Sync button** - triggers full SmartOffice re-fetch with confirmation dialog

### Tab 2 - Failed Syncs

- All `status: "failed"` logs displayed
- Badge count on tab header shows number of failures
- "Failures are retried automatically by the cron scheduler" note

### Tab 3 - Unmatched Records

- Paginated table (25 per page) of agents that could not be auto-matched
- Search by name or NPN (300ms debounce)
- **Match button** → opens modal to search Atlas users and confirm match
- **Dismiss button** → marks record as reviewed/dismissed (fades row visually)

### Tab 4 - Matched Agents

- Paginated table (25 per page) of all successfully matched agents
- Color-coded match type badges:
  - `NPN` → Cyan
  - `Name Exact` → Blue
  - `Fuzzy` → Violet (with confidence %)
  - `Manual` → Amber
- Search by name or NPN

### Polling Strategy

| State | Interval |
|---|---|
| Any sync running | Every 5 seconds |
| All syncs idle | Every 30 seconds |

---

## Production Switch Checklist

Before switching from sandbox to production SmartOffice API, update these values in `backend/.env`:

```env
# Change this URL to production:
ZINNIA_API_URL=https://api.smartofficecrm.com/bwm/v1/send

# Replace with production credentials:
ZINNIA_API_KEY=<production-api-key>
ZINNIA_API_SECRET=<production-api-secret>
ZINNIA_SITE_NAME=<production-site-name>
ZINNIA_USERNAME=<production-username>
```

Then verify with the health check:
```
GET /api/zinnia/health
```
Expected: `{"status": "ok", "api_url": "https://api.smartofficecrm.com/bwm/v1/send", ...}`

**No code changes required** - everything is environment-driven.

---

## Data Flow Diagrams

### Full Sync Flow

```
Admin clicks "Deep Sync"
        │
        ▼
POST /api/zinnia/sync/deep
        │
        ├── Check: any sync already running? → return "already_running"
        │
        └── asyncio.create_task(sync_all())
              │
              ├── sync_production() ──► zinnia_production (304 records)
              │        └── Done in ~5 seconds
              │
              ├── sync_case_status() ─► zinnia_cases (842 records)
              │        └── Done in ~10 seconds
              │
              └── sync_agents_background()
                       └── asyncio.create_task(sync_agents())
                                │
                                ├── Pages 0..2605 (100 records each)
                                │   Each page: fetch → parse → bulk upsert
                                │   260,525 records ~ 25-45 minutes
                                │
                                └── Lock released → run_agent_matching()
                                         │
                                         ├── NPN match
                                         ├── Exact name match
                                         ├── Fuzzy match (≥0.85)
                                         └── Save unmatched
```

### Manual Match Flow

```
Admin opens Unmatched tab
        │
        ▼
Click "Match" on a record
        │
        ▼
Search Atlas users (GET /zinnia/users/search?q=...)
        │
        ▼
Select user → Click "Confirm Match"
        │
        ▼
POST /api/zinnia/unmatched/{id}/match
        │
        ├── zinnia_agents.update_one() → set atlas_user_id, match_type: "manual"
        └── zinnia_unmatched.delete_one() → remove from unmatched list
```

---
