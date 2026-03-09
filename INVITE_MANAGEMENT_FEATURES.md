# Invite Management Features Documentation

## Overview
Complete invite lifecycle management with resend and cancel capabilities.

---

## Feature 1: Resend Invite

### API Endpoint
**POST /api/invites/{invite_id}/resend**

### Authorization Rules
- **Regular Users:** Can resend their own expired invites only
- **Admins:** Can resend any invite, even if not expired

### Features
- Generates new UUID token
- Extends expiration by 7 days
- Sends new invite email
- Tracks resend history
- Cannot resend accepted invites

### Response
```json
{
  "id": "invite-id",
  "token": "new-token",
  "recruit_email": "recruit@example.com",
  "status": "pending",
  "expires_at": "2026-02-21T...",
  "resent_at": "2026-02-14T...",
  "resent_by": "user-id",
  "resent_by_name": "User Name"
}
```

---

## Feature 2: Cancel Invite (NEW)

### API Endpoint
**DELETE /api/invites/{invite_id}**

### Authorization Rules
- **Regular Users:** Can cancel invites they created
- **Admins:** Can cancel any invite
- **Restrictions:** Cannot cancel accepted invites

### Features
- Updates status to 'cancelled'
- Adds cancellation metadata
- Creates audit trail
- Prevents signup with cancelled invite token
- Cancelled invites can be resent (generates new token)

### Response
```json
{
  "success": true,
  "message": "Invite cancelled successfully",
  "invite_id": "invite-id",
  "recruit_email": "recruit@example.com",
  "cancelled_at": "2026-02-14T...",
  "cancelled_by": "User Name"
}
```

### Error Responses
- `404`: Invite not found
- `403`: Unauthorized (not your invite and not admin)
- `400`: Invite already accepted
- `400`: Invite already cancelled

---

## Use Cases

### Use Case 1: Invite Sent to Wrong Email
**Scenario:** Agent realizes they sent invite to incorrect email address.
**Action:** Cancel the wrong invite and create a new one with correct email.
**Result:** Wrong invite becomes invalid, new invite sent to correct address.

### Use Case 2: Recruit No Longer Interested
**Scenario:** Recruit declines opportunity before accepting invite.
**Action:** Cancel the pending invite to clean up invite list.
**Result:** Invite marked as cancelled, token becomes invalid.

### Use Case 3: Duplicate Invites
**Scenario:** Agent accidentally creates multiple invites for same recruit.
**Action:** Cancel duplicate invites, keep only one active.
**Result:** Only one valid invite remains, others cancelled.

### Use Case 4: Cancelled Invite Needs Reactivation
**Scenario:** Recruit changes mind after invite was cancelled.
**Action:** Admin (or original inviter) resends the cancelled invite.
**Result:** New token generated, fresh 7-day window, invite reactivated.

---

## Invite Status Flow

```
[Created] → [pending]
    ↓
    ├─→ [User Signs Up] → [accepted] (FINAL - cannot cancel/resend)
    ├─→ [Cancelled] → [cancelled] (can be resent to reactivate)
    ├─→ [Expires] → [pending] (can be resent with new token)
    └─→ [Resent] → [pending] (new token, extended expiration)
```

---

## Database Schema

### Fields Added to `invites` Collection

**Resend Fields:**
```json
{
  "resent_at": "2026-02-14T...",
  "resent_by": "user-id",
  "resent_by_name": "User Name"
}
```

**Cancel Fields:**
```json
{
  "cancelled_at": "2026-02-14T...",
  "cancelled_by": "user-id",
  "cancelled_by_name": "User Name"
}
```

---

## Testing Examples

### Test Cancel Invite
```bash
# Cancel as invite creator
curl -X DELETE "https://your-api.com/api/invites/{invite_id}" \
  -H "Authorization: Bearer {user_token}"

# Cancel as admin (can cancel any invite)
curl -X DELETE "https://your-api.com/api/invites/{invite_id}" \
  -H "Authorization: Bearer {admin_token}"
```

### Test Resend Cancelled Invite
```bash
# Resend a cancelled invite (reactivates it)
curl -X POST "https://your-api.com/api/invites/{invite_id}/resend" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"
```

---

## Audit Trail

All invite actions are logged:
- **invite_sent** - Initial invite creation
- **invite_resent** - Invite resent with new token
- **invite_cancelled** - Invite cancelled
- **invite_accepted** - User signed up using invite

Each audit log includes:
- Who performed the action
- When it was performed
- Target invite details
- Additional context (was_expired, cancelled_by_admin, etc.)

---

## Security Features

✅ **Authorization Enforcement**
- Users can only manage their own invites
- Admin privilege clearly separated
- All actions audited

✅ **State Validation**
- Cannot cancel accepted invites
- Cannot use cancelled invite tokens
- Duplicate cancellation prevented

✅ **Data Integrity**
- Complete audit trail
- Metadata preservation
- Status history tracking

✅ **Flexibility**
- Cancelled invites can be resent
- Admin override capabilities
- Clean error messages

---

## Frontend Integration Guide

### Display Invite Status
```javascript
// Show appropriate badge based on status
const getStatusBadge = (invite) => {
  switch(invite.status) {
    case 'pending':
      return <Badge color="yellow">Pending</Badge>;
    case 'accepted':
      return <Badge color="green">Accepted</Badge>;
    case 'cancelled':
      return <Badge color="gray">Cancelled</Badge>;
    default:
      return <Badge color="blue">{invite.status}</Badge>;
  }
};
```

### Action Buttons
```javascript
// Show appropriate actions based on status and user role
const getInviteActions = (invite, currentUser) => {
  const isAdmin = currentUser.role === 'admin';
  const isOwner = invite.inviter_id === currentUser.id;
  
  if (invite.status === 'accepted') {
    return null; // No actions for accepted invites
  }
  
  if (invite.status === 'cancelled') {
    // Only show resend for cancelled invites
    return (isAdmin || isOwner) && (
      <Button onClick={() => resendInvite(invite.id)}>Resend</Button>
    );
  }
  
  if (invite.status === 'pending') {
    const isExpired = new Date(invite.expires_at) < new Date();
    return (
      <>
        {(isAdmin || (isOwner && isExpired)) && (
          <Button onClick={() => resendInvite(invite.id)}>Resend</Button>
        )}
        {(isAdmin || isOwner) && (
          <Button variant="danger" onClick={() => cancelInvite(invite.id)}>
            Cancel
          </Button>
        )}
      </>
    );
  }
};
```

---

## Best Practices

1. **Cancel vs Delete**: Use cancel (not delete) to preserve audit history
2. **Admin Review**: Admins should review cancelled invites periodically
3. **Email Communication**: Consider notifying recruits when invites are cancelled
4. **Duplicate Prevention**: Check for pending invites before creating new ones
5. **Expiration Handling**: Automatically cancel very old expired invites (optional cleanup)

---

## Migration Notes

No database migration required - new fields are added dynamically when actions are performed.

Existing invites will work as before. New fields (`cancelled_at`, `cancelled_by`, etc.) are only added when the respective action is taken.

