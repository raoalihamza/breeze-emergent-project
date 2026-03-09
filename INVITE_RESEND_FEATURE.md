# Invite Resend Feature Documentation

## Overview
Added ability to resend recruiting invite links with proper authorization controls.

## API Endpoint

### POST /api/invites/{invite_id}/resend

**Authorization Rules:**
1. **Regular Users (Agents):**
   - Can only resend invites they created (inviter_id matches)
   - Can ONLY resend if the invite has expired
   - Cannot resend accepted invites

2. **Admins:**
   - Can resend ANY invite in the system
   - Can resend even if invite hasn't expired yet
   - Cannot resend accepted invites

**Request:**
```bash
POST /api/invites/{invite_id}/resend
Authorization: Bearer {token}
Content-Type: application/json
```

**Response:**
```json
{
  "id": "invite-id",
  "token": "new-token-uuid",
  "recruit_email": "recruit@example.com",
  "recruit_first_name": "John",
  "recruit_last_name": "Doe",
  "recruit_npn": "123456",
  "inviter_id": "inviter-id",
  "inviter_name": "Jane Smith",
  "comp_percentage": 75.0,
  "message": "Welcome message",
  "status": "pending",
  "created_at": "2026-02-14T...",
  "expires_at": "2026-02-21T...",
  "resent_at": "2026-02-14T...",
  "resent_by": "admin-id",
  "resent_by_name": "Admin Name"
}
```

**Error Responses:**
- `404`: Invite not found
- `403`: Unauthorized (not your invite and not admin)
- `400`: Invite already accepted
- `400`: Invite not expired yet (for non-admins)
- `400`: User already signed up
- `500`: Failed to send email

## Features

### 1. New Token Generation
- Generates fresh UUID token
- Extends expiration by 7 days from resend time
- Preserves all original invite data (email, NPN, comp %, etc.)

### 2. Email Notification
- Sends new invite email with updated token
- Uses same email template as original invite
- Includes upline name and personalized message

### 3. Audit Trail
- Logs who resent the invite
- Tracks whether invite was expired
- Records if resent by admin (even if not expired)
- Preserves original inviter information

### 4. Status Management
- Resets status to 'pending' on resend
- Adds `resent_at`, `resent_by`, `resent_by_name` fields
- Prevents resending accepted invites

## Use Cases

### Use Case 1: Expired Invite
**Scenario:** A recruit didn't sign up within 7 days and the invite expired.
**Action:** The inviter (or admin) can resend the invite.
**Result:** Recruit receives a new invite email with a fresh 7-day window.

### Use Case 2: Admin Override
**Scenario:** A recruit lost the original email before the invite expired.
**Action:** Admin can immediately resend the invite without waiting for expiration.
**Result:** Recruit receives a new invite email with a new token.

### Use Case 3: Non-Admin Blocked
**Scenario:** A regular agent wants to resend a non-expired invite.
**Action:** System blocks the request with error message.
**Result:** Agent must wait for expiration or contact admin.

## Testing

```bash
# Test as Admin (can resend anytime)
curl -X POST "https://your-api.com/api/invites/{invite_id}/resend" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json"

# Test as Regular User (only expired invites)
curl -X POST "https://your-api.com/api/invites/{invite_id}/resend" \
  -H "Authorization: Bearer {user_token}" \
  -H "Content-Type: application/json"
```

## Database Schema Updates

**New fields added to `invites` collection:**
```json
{
  "resent_at": "2026-02-14T...",
  "resent_by": "user-id",
  "resent_by_name": "Name of person who resent"
}
```

## Security Considerations

1. **Authorization:** Strictly enforced - users can only resend their own invites
2. **Admin Privilege:** Clearly separated and audited
3. **Accepted Invites:** Cannot be resent to prevent conflicts
4. **Duplicate Prevention:** Checks if user already signed up
5. **Audit Trail:** Complete history of who resent what and when
