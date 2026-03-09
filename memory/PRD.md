# Atlas - Agency OS Platform

## Original Problem Statement
Build a comprehensive agency management platform for Breeze Financial Group with the following features:
1. Phone Number Field for agent profiles
2. Email Client Portal Invites via Resend
3. Client Portal Branding with company logo
4. Mobile-friendly Recruiting Page
5. Client Info Persistence bug fix
6. Simplified Client Workflow with PDF upload and email portal link
7. My Team UI/UX improvements (mobile tree scroll, desktop search/sort)
8. Production Page activation
9. Dashboard Redesign with Top 10 Leaderboard
10. 3D Lively Navigation Icons
11. Admin Edit Agent capability
12. Cancel Invite visibility for all users
13. Atlas AI bug fix
14. CEO Report bug fix

## User Personas
- **Admin (Kyle)**: Full access to all features, team management, audit logs
- **Agents**: Access to their team, clients, production data, resources
- **Clients**: Portal access to view policies and agent contact info

## Core Requirements
- FastAPI Backend with MongoDB
- React Frontend with TailwindCSS and Shadcn UI
- JWT Authentication
- Resend for transactional emails
- Claude AI for Atlas AI chatbot and CEO Report

## What's Been Implemented

### Session: December 2025
- [x] Dashboard redesigned with Top 10 Agent Leaderboard
- [x] Admin can edit agent name, email, and NPN
- [x] Agent phone number field added to profiles (visible in client portal)
- [x] Client email/phone persistence bug fixed on Book of Business
- [x] New workflow: attach policy PDF and email portal link
- [x] Recruiting page made mobile-responsive
- [x] My Team: horizontal scroll on mobile tree view
- [x] My Team: search and alphabetical sorting on table view
- [x] 3D gradient icons for sidebar navigation (updated to brand color #23ACD5)
- [x] Client portal branded with company logo
- [x] Production page activated in navigation
- [x] Cancel Invite button visible for all users
- [x] Atlas AI bug fixed (model name correction)
- [x] CEO Report bug fixed (model name + frontend parsing)
- [x] Email-based client portal invites via Resend
- [x] **New Recruit Welcome Email** - Styled email with PDF attachment support when recruits activate accounts

## Known Blockers
1. **Production Deployment**: User must manually redeploy from Emergent dashboard
2. **Atlas AI Budget**: Emergent LLM Key budget exhausted - needs funds added

## Prioritized Backlog

### P0 (Critical)
- [ ] Backend Refactor: Decompose server.py into /routes, /models, /services

### P1 (High)
- [ ] Implement Tickets Backend Logic (create, update status, apply changes)
- [ ] Quiz Analytics (track which questions agents struggle with)

### P2 (Medium)
- [ ] Zinnia Webhook Endpoint (POST /api/webhooks/zinnia-production)
- [ ] Enhanced Dashboards for Zinnia integration data

### P3 (Future)
- [ ] Additional dashboard visualizations
- [ ] Advanced reporting features

## Technical Architecture

### Backend Structure
```
/app/backend/
├── server.py          # Main API (NEEDS REFACTORING)
├── atlas_ai_service.py
├── email_service.py
├── .env
├── requirements.txt
└── uploads/           # Policy PDFs
```

### Frontend Structure
```
/app/frontend/src/
├── App.js
├── components/
│   ├── Layout.js
│   ├── AdminControlModals.js
│   └── ui/            # Shadcn components
└── pages/
    ├── Dashboard.js
    ├── MyTeam.js
    ├── Recruiting.js
    ├── BookOfBusiness.js
    ├── MyClients.js
    ├── Profile.js
    ├── CEOReport.jsx
    └── ClientPortal/
```

### Key API Endpoints
- `PUT /api/users/{user_id}/details` - Edit agent details (admin)
- `PUT /api/users/me/phone` - Update phone number
- `POST /api/clients/{client_id}/send-portal-invite` - Send invite email
- `PUT /api/clients/{client_id}` - Update client info
- `POST /api/clients/{client_id}/documents/upload` - Upload policy PDF
- `GET /api/leaderboard/top-agents` - Dashboard leaderboard
- `POST /api/atlas-ai/chat` - AI chatbot
- `POST /api/kpi/weekly-report` - CEO Report

### Database Collections
- users, clients, knowledge_base_documents, quiz_questions, atlas_ai_question_logs

## Test Credentials
- Admin: kyle@breezewealthmanagement.com / Breeze2026!
- Agent: kcheek@breezewealthmanagement.com / KatieCheek2026!

## 3rd Party Integrations
- Claude Sonnet 4 & Haiku (via emergentintegrations)
- Resend for emails
- Recharts for charts
- React Flow for org charts
