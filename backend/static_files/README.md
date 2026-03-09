# Static Files for Email Attachments

## Breeze Advizor Guide PDF

Place the **Breeze Advizor Guide PDF** in this folder with the exact filename:

```
Breeze_Advizor_Guide.pdf
```

This PDF will be automatically attached to the welcome email sent to new recruits when they activate their Atlas account.

### Expected Location
`/app/backend/static_files/Breeze_Advizor_Guide.pdf`

### Email Details
- **Subject:** Welcome to Breeze! (IMPORTANT)
- **Trigger:** When a recruit accepts an invite link and creates their account
- **Attachment:** Breeze_Advizor_Guide.pdf (if present)

If the PDF is not found, the welcome email will still be sent but without the attachment.
