# Admin Management Tools Documentation

## Overview
This document describes the comprehensive suite of admin management tools implemented for the Breeze Matrix Agency OS.

## Features Implemented

### 1. Visual Organization Chart
**Location:** My Team > Org Chart Tab (Admin Only)

**Description:**
An interactive, flow-chart style visualization of the entire organization hierarchy using React Flow.

**Features:**
- Displays all agents in a visual tree structure
- Each node shows:
  - Agent name
  - Role (with color-coded badges)
  - Commission percentage
  - Status (Active/Inactive)
  - Team size
- Interactive controls:
  - Zoom in/out
  - Pan around the chart
  - Click nodes to view agent details
- Animated connections between upline and downline
- Color-coded role indicators:
  - Admin: Violet/Purple gradient
  - Leader: Blue/Cyan gradient
  - Agent: Cyan/Teal gradient

**Technical Implementation:**
- Built with `@xyflow/react` (React Flow)
- Custom node components with Tailwind CSS styling
- Recursive hierarchy building algorithm
- Responsive layout with automatic positioning

---

### 2. Admin Control Modals

#### a. Reassign Agent
**Access:** Table View > Actions Menu > "Reassign Agent"

**Functionality:**
- Allows admins to change an agent's upline
- Dropdown shows all available uplines (excludes the agent themselves)
- Option to set "None" for top-level agents
- Prevents circular hierarchy references
- Creates audit log entry

**Backend Endpoint:** `PUT /api/admin/users/{user_id}/upline`

**Request Body:**
```json
{
  "new_upline_id": "string or null"
}
```

#### b. Change Commission
**Access:** Table View > Actions Menu > "Change Commission"

**Functionality:**
- Update an agent's commission percentage
- Input validation (0-200%)
- Shows current commission level
- Creates audit log entry

**Backend Endpoint:** `PUT /api/admin/users/{user_id}/commission`

**Request Body:**
```json
{
  "comp_percentage": 85.5
}
```

#### c. Toggle Agent Status
**Access:** Table View > Actions Menu > "Disable Account" or "Enable Account"

**Functionality:**
- Enable or disable agent accounts
- Disabled agents cannot log in
- Warning message shown before disabling
- Admins cannot disable their own account
- Creates audit log entry

**Backend Endpoint:** `PUT /api/admin/users/{user_id}/status`

**Request Body:**
```json
{
  "status": "active" | "disabled"
}
```

---

### 3. Audit Log System
**Location:** Sidebar > Audit Log (Admin Only)

**Description:**
Comprehensive tracking system for all administrative actions.

**Tracked Actions:**
- Hierarchy changes (agent reassignments)
- Status changes (enable/disable)
- Commission changes
- Role changes

**Information Displayed:**
- Action type with color-coded badge
- Target agent name
- Old and new values
- Admin who performed the action
- Timestamp

**Filtering:**
- Filter by action type
- "All" view to see everything
- Limit of 100 most recent logs (configurable)

**Backend Endpoint:** `GET /api/admin/audit-logs?action={action_type}&limit={limit}`

**Database Collection:** `audit_logs`

**Schema:**
```json
{
  "id": "string",
  "action": "hierarchy_change | status_change | commission_change | role_change",
  "admin_id": "string",
  "admin_name": "string",
  "target_user_id": "string",
  "target_user_name": "string",
  "details": {
    "old_value": "any",
    "new_value": "any"
  },
  "created_at": "ISO8601 timestamp"
}
```

---

### 4. Hierarchy Export
**Location:** My Team > Export Button (Top Right, Admin Only)

**Functionality:**
- Downloads complete organization snapshot as JSON
- Includes:
  - Export timestamp
  - Admin who exported
  - Total user count
  - Complete user list with hierarchy relationships

**Backend Endpoint:** `GET /api/admin/hierarchy-export`

**File Format:**
```json
{
  "exported_at": "2026-01-25T17:50:00Z",
  "exported_by": "Kyle Admin",
  "total_users": 6,
  "users": [
    {
      "id": "...",
      "name": "...",
      "email": "...",
      "role": "...",
      "status": "active",
      "comp_percentage": 135,
      "upline_id": "...",
      "upline_name": "...",
      "date_joined": "...",
      "npn": "..."
    }
  ]
}
```

---

## Technical Architecture

### Frontend Components

**New Files Created:**
1. `/app/frontend/src/pages/AuditLog.js` - Audit log page
2. `/app/frontend/src/components/OrgChart.js` - React Flow org chart component
3. `/app/frontend/src/components/AdminControlModals.js` - Three admin modals

**Modified Files:**
1. `/app/frontend/src/pages/MyTeam.js` - Added org chart tab, admin controls, export
2. `/app/frontend/src/components/Layout.js` - Added Audit Log nav item for admins
3. `/app/frontend/src/App.js` - Added /audit-log route

### Backend Endpoints

**New Endpoints (all in `/app/backend/server.py`):**
1. `GET /api/admin/org-tree` - Full organization tree for React Flow
2. `GET /api/admin/users` - All users list for reassignment dropdown
3. `PUT /api/admin/users/{user_id}/upline` - Reassign agent
4. `PUT /api/admin/users/{user_id}/status` - Enable/disable agent
5. `PUT /api/admin/users/{user_id}/commission` - Change commission
6. `GET /api/admin/audit-logs` - Fetch audit logs
7. `GET /api/admin/hierarchy-export` - Export hierarchy snapshot

**Helper Function:**
- `create_audit_log()` - Creates audit trail entries

### Database Collections

**New Collection:**
- `audit_logs` - Stores all admin action history

**Modified Collections:**
- `users` - Uses existing `status` and `upline_id` fields

---

## Security & Authorization

**Access Control:**
- All admin endpoints require `role: 'admin'`
- Backend validates admin role before processing requests
- Frontend conditionally renders admin-only UI elements
- Admins cannot disable their own accounts

**Validation:**
- Circular hierarchy prevention
- Commission range validation (0-200%)
- Status validation ('active' or 'disabled')

---

## UI/UX Design

**Design Theme:**
Follows the established "glassmorphism" aesthetic with:
- Backdrop blur effects
- Subtle shadows and borders
- Cyan accent color scheme
- Smooth animations and transitions
- Consistent spacing and typography

**Responsive Behavior:**
- Org chart is scrollable/pannable
- Table view works on all screen sizes
- Modals are centered and responsive

---

## Testing Results

**Frontend Testing Agent Results:**
✅ All 7 feature areas tested successfully:
1. Org Chart visualization working perfectly
2. Reassign Agent modal functional
3. Change Commission modal functional
4. Toggle Status modal functional
5. Audit Log page displaying correctly
6. Hierarchy Export downloading valid JSON
7. Agent Profile drawer showing admin-specific data

**Backend API Testing:**
✅ All endpoints tested with curl
✅ JWT authentication working
✅ Role-based access control enforced
✅ Audit logs being created correctly

---

## Future Enhancements

Potential improvements for future iterations:
1. **Audit Log Pagination:** Handle very large audit logs
2. **Bulk Operations:** Select and modify multiple agents at once
3. **Advanced Filtering:** Date ranges, multi-select filters
4. **Export Formats:** CSV, Excel in addition to JSON
5. **Org Chart Customization:** Save custom layouts, print view
6. **Activity Dashboard:** Visual analytics of admin actions
7. **Undo Functionality:** Revert recent changes
8. **Email Notifications:** Alert affected agents of changes

---

## Maintenance Notes

**Important Files:**
- Backend: `/app/backend/server.py` (lines 950-1226)
- Frontend: `/app/frontend/src/pages/MyTeam.js`
- Styles: Tailwind CSS classes inline

**Dependencies Added:**
- `@xyflow/react@12.10.0` - React Flow for org chart

**Configuration:**
- Audit log limit: 100 (configurable in API endpoint)
- Commission range: 0-200% (validated on backend)

---

## Support & Troubleshooting

**Common Issues:**

1. **Org Chart not displaying:**
   - Verify admin role
   - Check browser console for errors
   - Ensure React Flow styles are loaded

2. **Modals not opening:**
   - Check if user has admin role
   - Verify backend endpoints are accessible
   - Check for JavaScript errors

3. **Audit logs empty:**
   - Perform an admin action to create entries
   - Check MongoDB connection
   - Verify audit_logs collection exists

**Debugging:**
- Backend logs: `/var/log/supervisor/backend.*.log`
- Frontend logs: Browser console
- Network requests: Browser DevTools > Network tab
