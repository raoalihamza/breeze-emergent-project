"""
Email Service for Atlas using Resend
Handles all transactional emails with templates
"""

import os
import asyncio
import logging
import resend
import base64
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Atlas <support@mail.breezeatlas.com>')
APP_DOMAIN = os.environ.get('APP_DOMAIN', 'https://breezeatlas.com')

# Path to static files
STATIC_FILES_DIR = Path(__file__).parent / 'static_files'
BREEZE_GUIDE_PATH = STATIC_FILES_DIR / 'Breeze_Advizor_Guide.pdf'

# ============================================
# Core Email Helper Function
# ============================================

async def send_transactional_email(
    to: str | List[str],
    subject: str,
    html: str,
    text: Optional[str] = None,
    tags: Optional[List[Dict[str, str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Send a transactional email using Resend.
    Non-blocking async implementation.
    
    Args:
        to: Recipient email(s)
        subject: Email subject
        html: HTML content
        text: Plain text fallback (optional)
        tags: Resend tags for tracking (optional)
        metadata: Additional metadata (optional)
        attachments: List of attachment dicts with 'filename', 'content' (base64), 'content_type'
    
    Returns:
        Dict with status and email_id or error
    """
    if not resend.api_key:
        logger.error("RESEND_API_KEY not configured")
        return {"status": "error", "message": "Email service not configured"}
    
    # Ensure 'to' is a list
    recipients = [to] if isinstance(to, str) else to
    
    params = {
        "from": SENDER_EMAIL,
        "to": recipients,
        "subject": subject,
        "html": html,
    }
    
    if text:
        params["text"] = text
    if tags:
        params["tags"] = tags
    if metadata:
        params["headers"] = {"X-Metadata": str(metadata)}
    if attachments:
        params["attachments"] = attachments
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent successfully to {recipients}, id: {email.get('id')}")
        return {
            "status": "success",
            "message": f"Email sent to {', '.join(recipients)}",
            "email_id": email.get("id")
        }
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================
# Email Templates
# ============================================

def get_base_template(content: str, preview_text: str = "") -> str:
    """Base HTML email template with Atlas branding"""
    return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlas</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <!-- Preview text -->
    <div style="display: none; max-height: 0; overflow: hidden;">{preview_text}</div>
    
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 2px;">ATLAS</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; color: #64748b; font-size: 12px;">
                                &copy; {datetime.now().year} Breeze Wealth Management. All rights reserved.
                            </p>
                            <p style="margin: 10px 0 0; color: #94a3b8; font-size: 11px;">
                                This is an automated message from Atlas.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''


def get_button_html(text: str, url: str, color: str = "#0891b2") -> str:
    """Generate a styled button for emails"""
    return f'''
    <table role="presentation" style="margin: 25px auto;">
        <tr>
            <td style="background-color: {color}; border-radius: 8px;">
                <a href="{url}" target="_blank" style="display: inline-block; padding: 14px 32px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 14px;">
                    {text}
                </a>
            </td>
        </tr>
    </table>
'''


# ============================================
# Template A: Welcome / Verify Email
# ============================================

def build_welcome_email(
    first_name: str,
    verify_token: str,
    login_url: Optional[str] = None
) -> Dict[str, str]:
    """Build welcome/verification email for new agents"""
    verify_url = f"{APP_DOMAIN}/verify-email?token={verify_token}"
    login_link = login_url or f"{APP_DOMAIN}/login"
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">Welcome to Atlas, {first_name}!</h2>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Your account has been created successfully. You're now part of the Breeze Wealth Management team!
        </p>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Please verify your email address to get started:
        </p>
        
        {get_button_html("Verify Email", verify_url)}
        
        <p style="margin: 25px 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Once verified, you can log in to access your dashboard:
        </p>
        
        <p style="margin: 0; text-align: center;">
            <a href="{login_link}" style="color: #0891b2; text-decoration: none; font-weight: 500;">Go to Login →</a>
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">
            If you didn't create this account, please ignore this email.
        </p>
    '''
    
    return {
        "subject": "Welcome to Atlas - Verify Your Email",
        "html": get_base_template(content, f"Welcome to Atlas, {first_name}! Please verify your email."),
        "text": f"Welcome to Atlas, {first_name}! Please verify your email by visiting: {verify_url}"
    }


# ============================================
# Template B: Password Reset
# ============================================

def build_password_reset_email(
    first_name: str,
    reset_token: str,
    expires_minutes: int = 60
) -> Dict[str, str]:
    """Build password reset email"""
    reset_url = f"{APP_DOMAIN}/reset-password?token={reset_token}"
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">Reset Your Password</h2>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Hi {first_name},
        </p>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            We received a request to reset your password. Click the button below to create a new password:
        </p>
        
        {get_button_html("Reset Password", reset_url)}
        
        <p style="margin: 25px 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            This link will expire in <strong>{expires_minutes} minutes</strong>.
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">
            If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
        </p>
    '''
    
    return {
        "subject": "Reset Your Atlas Password",
        "html": get_base_template(content, "Reset your Atlas password"),
        "text": f"Hi {first_name}, Reset your password by visiting: {reset_url}. This link expires in {expires_minutes} minutes."
    }


# ============================================
# Template C: Recruiting Invite
# ============================================

def build_recruit_invite_email(
    recruit_email: str,
    upline_name: str,
    invite_token: str,
    expires_days: int = 7
) -> Dict[str, str]:
    """Build recruiting invite email"""
    invite_url = f"{APP_DOMAIN}/signup/{invite_token}"
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">You're Invited to Join Atlas!</h2>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            <strong>{upline_name}</strong> has invited you to join Breeze Wealth Management's Atlas platform.
        </p>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Atlas is our agency management system where you'll access training, resources, track your production, and connect with your team.
        </p>
        
        {get_button_html("Accept Invitation", invite_url, "#059669")}
        
        <div style="background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 12px; color: #1e293b; font-size: 14px; font-weight: 600;">What happens next?</h3>
            <ol style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.8;">
                <li>Click the button above to accept your invitation</li>
                <li>Create your account with a secure password</li>
                <li>Complete your profile setup</li>
                <li>Start exploring Atlas!</li>
            </ol>
        </div>
        
        <p style="margin: 0 0 15px; color: #dc2626; font-size: 13px;">
            ⏰ This invitation expires in <strong>{expires_days} days</strong>.
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">
            Questions? Reply to this email or contact your upline directly.
        </p>
    '''
    
    return {
        "subject": f"{upline_name} invited you to join Atlas",
        "html": get_base_template(content, f"{upline_name} has invited you to join Breeze Wealth Management"),
        "text": f"{upline_name} has invited you to join Atlas. Accept your invitation: {invite_url}. This link expires in {expires_days} days."
    }


# ============================================
# Template D: Recruit Activated (to upline)
# ============================================

def build_recruit_activated_email(
    upline_name: str,
    recruit_name: str,
    recruit_email: str,
    comp_level: float
) -> Dict[str, str]:
    """Build recruit activation notification for upline"""
    dashboard_url = f"{APP_DOMAIN}/team"
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">🎉 New Recruit Activated!</h2>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Great news, {upline_name}!
        </p>
        
        <p style="margin: 0 0 20px; color: #475569; font-size: 15px; line-height: 1.6;">
            Your recruit has accepted their invitation and created their Atlas account.
        </p>
        
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin: 0 0 15px; color: #166534; font-size: 16px; font-weight: 600;">Recruit Details</h3>
            <table style="width: 100%; font-size: 14px;">
                <tr>
                    <td style="color: #475569; padding: 5px 0;">Name:</td>
                    <td style="color: #1e293b; font-weight: 500;">{recruit_name}</td>
                </tr>
                <tr>
                    <td style="color: #475569; padding: 5px 0;">Email:</td>
                    <td style="color: #1e293b; font-weight: 500;">{recruit_email}</td>
                </tr>
                <tr>
                    <td style="color: #475569; padding: 5px 0;">Commission Level:</td>
                    <td style="color: #1e293b; font-weight: 500;">{comp_level}%</td>
                </tr>
            </table>
        </div>
        
        <p style="margin: 20px 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Log in to view your team and start onboarding your new recruit:
        </p>
        
        {get_button_html("View Your Team", dashboard_url)}
    '''
    
    return {
        "subject": f"🎉 {recruit_name} has joined your team!",
        "html": get_base_template(content, f"{recruit_name} has activated their Atlas account"),
        "text": f"Great news, {upline_name}! {recruit_name} ({recruit_email}) has joined your team at {comp_level}% commission."
    }


# ============================================
# Template E: Ticket Status Update
# ============================================

def build_ticket_status_email(
    recipient_name: str,
    ticket_id: str,
    ticket_type: str,
    old_status: str,
    new_status: str,
    affected_agent_name: str,
    resolution_notes: Optional[str] = None
) -> Dict[str, str]:
    """Build ticket status update email"""
    ticket_url = f"{APP_DOMAIN}/my-tickets"
    
    # Status color mapping
    status_colors = {
        "APPROVED": "#059669",
        "DENIED": "#dc2626",
        "RESOLVED": "#0891b2",
        "UNDER_REVIEW": "#d97706"
    }
    status_color = status_colors.get(new_status, "#475569")
    
    # Friendly ticket type names
    type_names = {
        "COMMISSION_CHANGE": "Commission Change",
        "HIERARCHY_MOVE": "Hierarchy Move",
        "REINSTATEMENT": "Reinstatement"
    }
    ticket_type_display = type_names.get(ticket_type, ticket_type)
    
    resolution_section = ""
    if resolution_notes:
        resolution_section = f'''
        <div style="background-color: #f8fafc; border-left: 4px solid {status_color}; padding: 15px; margin: 20px 0;">
            <h4 style="margin: 0 0 8px; color: #1e293b; font-size: 13px; font-weight: 600;">Resolution Notes:</h4>
            <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.6;">{resolution_notes}</p>
        </div>
        '''
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">Ticket Status Update</h2>
        
        <p style="margin: 0 0 15px; color: #475569; font-size: 15px; line-height: 1.6;">
            Hi {recipient_name},
        </p>
        
        <p style="margin: 0 0 20px; color: #475569; font-size: 15px; line-height: 1.6;">
            Your ticket has been updated:
        </p>
        
        <div style="background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <table style="width: 100%; font-size: 14px;">
                <tr>
                    <td style="color: #475569; padding: 8px 0; width: 40%;">Ticket Type:</td>
                    <td style="color: #1e293b; font-weight: 500;">{ticket_type_display}</td>
                </tr>
                <tr>
                    <td style="color: #475569; padding: 8px 0;">Affected Agent:</td>
                    <td style="color: #1e293b; font-weight: 500;">{affected_agent_name}</td>
                </tr>
                <tr>
                    <td style="color: #475569; padding: 8px 0;">Status Change:</td>
                    <td>
                        <span style="color: #64748b;">{old_status}</span>
                        <span style="color: #94a3b8;"> → </span>
                        <span style="color: {status_color}; font-weight: 600;">{new_status}</span>
                    </td>
                </tr>
            </table>
        </div>
        
        {resolution_section}
        
        {get_button_html("View Ticket", ticket_url)}
    '''
    
    return {
        "subject": f"Ticket Update: {ticket_type_display} - {new_status}",
        "html": get_base_template(content, f"Your {ticket_type_display} ticket is now {new_status}"),
        "text": f"Hi {recipient_name}, Your {ticket_type_display} ticket for {affected_agent_name} has been updated from {old_status} to {new_status}."
    }


# ============================================
# Template F: Admin Ticket Notification
# ============================================

def build_admin_ticket_notification_email(
    ticket_id: str,
    ticket_type: str,
    submitter_name: str,
    submitter_email: str,
    affected_agent_name: str,
    reason: str
) -> Dict[str, str]:
    """Build admin notification for new ticket"""
    admin_url = f"{APP_DOMAIN}/admin-tickets"
    
    # Friendly ticket type names
    type_names = {
        "COMMISSION_CHANGE": "Commission Change",
        "HIERARCHY_MOVE": "Hierarchy Move",
        "REINSTATEMENT": "Reinstatement"
    }
    ticket_type_display = type_names.get(ticket_type, ticket_type)
    
    content = f'''
        <h2 style="margin: 0 0 20px; color: #1e293b; font-size: 22px;">📋 New Ticket Submitted</h2>
        
        <p style="margin: 0 0 20px; color: #475569; font-size: 15px; line-height: 1.6;">
            A new ticket requires your attention:
        </p>
        
        <div style="background-color: #fef3c7; border: 1px solid #fcd34d; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <table style="width: 100%; font-size: 14px;">
                <tr>
                    <td style="color: #92400e; padding: 8px 0; width: 35%; font-weight: 500;">Ticket Type:</td>
                    <td style="color: #78350f; font-weight: 600;">{ticket_type_display}</td>
                </tr>
                <tr>
                    <td style="color: #92400e; padding: 8px 0; font-weight: 500;">Submitted By:</td>
                    <td style="color: #78350f;">{submitter_name} ({submitter_email})</td>
                </tr>
                <tr>
                    <td style="color: #92400e; padding: 8px 0; font-weight: 500;">Affected Agent:</td>
                    <td style="color: #78350f;">{affected_agent_name}</td>
                </tr>
            </table>
        </div>
        
        <div style="background-color: #f8fafc; border-radius: 8px; padding: 15px; margin: 20px 0;">
            <h4 style="margin: 0 0 8px; color: #1e293b; font-size: 13px; font-weight: 600;">Reason:</h4>
            <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.6;">{reason[:500]}{"..." if len(reason) > 500 else ""}</p>
        </div>
        
        {get_button_html("Review Ticket", admin_url, "#dc2626")}
    '''
    
    return {
        "subject": f"🎫 New {ticket_type_display} Ticket from {submitter_name}",
        "html": get_base_template(content, f"New {ticket_type_display} ticket submitted by {submitter_name}"),
        "text": f"New {ticket_type_display} ticket from {submitter_name} ({submitter_email}) for {affected_agent_name}. Reason: {reason[:200]}"
    }


# ============================================
# High-Level Email Sending Functions
# ============================================

async def send_welcome_email(to: str, first_name: str, verify_token: str) -> Dict[str, Any]:
    """Send welcome/verification email to new user"""
    email_data = build_welcome_email(first_name, verify_token)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "welcome"}]
    )


async def send_password_reset_email(to: str, first_name: str, reset_token: str) -> Dict[str, Any]:
    """Send password reset email"""
    email_data = build_password_reset_email(first_name, reset_token)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "password_reset"}]
    )


async def send_recruit_invite_email(to: str, upline_name: str, invite_token: str) -> Dict[str, Any]:
    """Send recruiting invite email"""
    email_data = build_recruit_invite_email(to, upline_name, invite_token)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "recruit_invite"}]
    )


async def send_recruit_activated_email(to: str, upline_name: str, recruit_name: str, recruit_email: str, comp_level: float) -> Dict[str, Any]:
    """Send recruit activation notification to upline"""
    email_data = build_recruit_activated_email(upline_name, recruit_name, recruit_email, comp_level)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "recruit_activated"}]
    )


async def send_ticket_status_email(
    to: str | List[str],
    recipient_name: str,
    ticket_id: str,
    ticket_type: str,
    old_status: str,
    new_status: str,
    affected_agent_name: str,
    resolution_notes: Optional[str] = None
) -> Dict[str, Any]:
    """Send ticket status update email"""
    email_data = build_ticket_status_email(
        recipient_name, ticket_id, ticket_type,
        old_status, new_status, affected_agent_name, resolution_notes
    )
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "ticket_update"}]
    )


async def send_admin_ticket_notification(
    admin_emails: List[str],
    ticket_id: str,
    ticket_type: str,
    submitter_name: str,
    submitter_email: str,
    affected_agent_name: str,
    reason: str
) -> Dict[str, Any]:
    """Send new ticket notification to all admins"""
    email_data = build_admin_ticket_notification_email(
        ticket_id, ticket_type, submitter_name,
        submitter_email, affected_agent_name, reason
    )
    return await send_transactional_email(
        to=admin_emails,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "admin_ticket_notification"}]
    )



# ============================================
# Client Portal Invite Email
# ============================================

def build_client_portal_invite_email(
    client_name: str,
    agent_name: str,
    portal_link: str
) -> Dict[str, str]:
    """Build client portal invite email"""
    content = f'''
    <h2 style="margin: 0 0 20px; color: #0f172a; font-size: 24px; font-weight: 700;">
        Welcome to Your Client Portal
    </h2>
    <p style="margin: 0 0 15px; color: #334155; font-size: 16px; line-height: 1.6;">
        Hi {client_name},
    </p>
    <p style="margin: 0 0 15px; color: #334155; font-size: 16px; line-height: 1.6;">
        {agent_name} has invited you to access your secure client portal with Breeze Financial Group.
    </p>
    <p style="margin: 0 0 15px; color: #334155; font-size: 16px; line-height: 1.6;">
        Your portal provides you with:
    </p>
    <ul style="margin: 0 0 20px; padding-left: 20px; color: #334155; font-size: 15px; line-height: 1.8;">
        <li>View all your policies and coverage details</li>
        <li>Access important documents and forms</li>
        <li>Track upcoming payments and renewals</li>
        <li>Contact your agent directly</li>
    </ul>
    {get_button_html("Set Up Your Portal", portal_link)}
    <p style="margin: 20px 0 0; color: #64748b; font-size: 14px; line-height: 1.6;">
        This link will expire in 7 days for your security. If you have any questions, please contact {agent_name}.
    </p>
    '''
    
    return {
        "subject": f"Welcome to Your Breeze Financial Group Client Portal",
        "html": get_base_template(content, f"Set up your secure client portal with {agent_name}"),
        "text": f'''Welcome to Your Client Portal

Hi {client_name},

{agent_name} has invited you to access your secure client portal with Breeze Financial Group.

Your portal provides you with:
- View all your policies and coverage details
- Access important documents and forms
- Track upcoming payments and renewals
- Contact your agent directly

Set up your portal here: {portal_link}

This link will expire in 7 days for your security.

If you have any questions, please contact {agent_name}.

---
© {datetime.now().year} Breeze Financial Group. All rights reserved.
'''
    }


async def send_client_portal_invite_email(
    to: str,
    client_name: str,
    agent_name: str,
    portal_link: str
) -> Dict[str, Any]:
    """Send client portal invite email"""
    email_data = build_client_portal_invite_email(client_name, agent_name, portal_link)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "client_portal_invite"}]
    )


# ============================================
# Template G: New Recruit Welcome Email (with PDF attachment)
# ============================================

def build_new_recruit_welcome_email(first_name: str) -> Dict[str, str]:
    """Build welcome email for new recruits activating their Atlas account"""
    
    content = f'''
        <p style="margin: 0 0 20px; color: #334155; font-size: 16px; line-height: 1.7;">
            Welcome to Breeze Financial Group — we're excited to have you here.
        </p>
        
        <p style="margin: 0 0 20px; color: #334155; font-size: 16px; line-height: 1.7;">
            Your ATLAS agent account is now active, which means you officially have access to the systems, tools, and infrastructure designed to help you succeed as a Breeze advisor.
        </p>
        
        <p style="margin: 0 0 20px; color: #334155; font-size: 16px; line-height: 1.7;">
            ATLAS is your central command center where you'll be able to access a multitude of resources, see production, have visibility in your hierarchy, put in support tickets, and see key updates as you grow your business.
        </p>
        
        <div style="background-color: #f0f9ff; border-left: 4px solid #0891b2; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0 0 15px; color: #0e7490; font-size: 15px; font-weight: 600;">
                Attached below is the Breeze Advizor Guide, which walks you through:
            </p>
            <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 15px; line-height: 1.8;">
                <li>Contracting instructions</li>
                <li>Carrier appointments</li>
                <li>Compensation levels</li>
                <li>Bonus structure</li>
                <li>Expectations and next steps</li>
            </ul>
        </div>
        
        <p style="margin: 0 0 25px; color: #334155; font-size: 16px; line-height: 1.7;">
            <strong>Please review and follow the contracting steps in this guide carefully.</strong> It contains everything you need to begin your onboarding and contracting process.
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <!-- Training Resources Section -->
        <h3 style="margin: 0 0 15px; color: #1e293b; font-size: 18px; font-weight: 600;">
            Get Started with Training
        </h3>
        
        <div style="background-color: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin: 0 0 20px 0;">
            <h4 style="margin: 0 0 10px; color: #065f46; font-size: 15px; font-weight: 600;">
                📚 Blitz Training Matrix
            </h4>
            <p style="margin: 0 0 12px; color: #334155; font-size: 15px; line-height: 1.7;">
                Make sure you start and complete the Blitz Training Matrix as fast as possible. This gives you the fundamentals of what we do here at Breeze and how we do it.
            </p>
            <p style="margin: 0;">
                <a href="https://start.blitztrainingmatrix.com/" style="color: #059669; font-weight: 600;">Start Blitz Training →</a>
            </p>
        </div>
        
        <div style="background-color: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 0 0 25px 0;">
            <h4 style="margin: 0 0 10px; color: #1e40af; font-size: 15px; font-weight: 600;">
                🎥 Breeze Training Hub
            </h4>
            <p style="margin: 0 0 12px; color: #334155; font-size: 15px; line-height: 1.7;">
                Be sure to request Viewer access to our Breeze Training Hub/Google Drive. This houses all of our past recorded trainings like sales training, carrier walkthroughs, top producer Q&A's, and more.
            </p>
            <p style="margin: 0;">
                <a href="https://drive.google.com/drive/folders/1hQt8n-yIcpCSwpLzbRFzszNoX7e-EHuJ?usp=drive_link" style="color: #2563eb; font-weight: 600;">Access Training Hub →</a>
            </p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <h3 style="margin: 0 0 15px; color: #1e293b; font-size: 18px; font-weight: 600;">
            What Makes Breeze Different
        </h3>
        
        <p style="margin: 0 0 15px; color: #334155; font-size: 16px; line-height: 1.7;">
            At Breeze, we provide:
        </p>
        
        <ul style="margin: 0 0 20px; padding-left: 20px; color: #334155; font-size: 15px; line-height: 1.8;">
            <li>Structured training and support</li>
            <li>Proven sales systems</li>
            <li>Access to top carriers</li>
            <li>High-level mentorship</li>
            <li>Growth opportunities as a producer or builder</li>
        </ul>
        
        <p style="margin: 0 0 25px; color: #334155; font-size: 16px; line-height: 1.7;">
            Our mission is simple:<br>
            <strong style="color: #0891b2;">Help you build a real business — not just sell policies.</strong>
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <div style="background-color: #fef3c7; border: 1px solid #fcd34d; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 12px; color: #92400e; font-size: 16px; font-weight: 600;">
                ⚡ Important Note
            </h3>
            <p style="margin: 0 0 15px; color: #78350f; font-size: 15px; line-height: 1.7;">
                Your success here will come from <strong>taking action quickly</strong>.
            </p>
            <p style="margin: 0 0 15px; color: #78350f; font-size: 15px; line-height: 1.7;">
                Agents who move fastest through contracting and begin activity early consistently see the best results.
            </p>
            <p style="margin: 0; color: #78350f; font-size: 15px; line-height: 1.7; font-weight: 600;">
                Do not wait until everything feels perfect — progress beats perfection.
            </p>
        </div>
        
        <p style="margin: 25px 0 0; color: #334155; font-size: 16px; line-height: 1.7;">
            If you have any questions, reach out to your manager/upline directly.
        </p>
        
        <p style="margin: 30px 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">
            - Breeze Financial Group
        </p>
    '''
    
    text_content = f'''Welcome to Breeze Financial Group — we're excited to have you here.

Your ATLAS agent account is now active, which means you officially have access to the systems, tools, and infrastructure designed to help you succeed as a Breeze advisor.

ATLAS is your central command center where you'll be able to access a multitude of resources, see production, have visibility in your hierarchy, put in support tickets, and see key updates as you grow your business.

Attached below is the Breeze Advizor Guide, which walks you through:

• Contracting instructions
• Carrier appointments
• Compensation levels
• Bonus structure
• Expectations and next steps

Please review and follow the contracting steps in this guide carefully. It contains everything you need to begin your onboarding and contracting process.

Get Started with Training

BLITZ TRAINING MATRIX
Make sure you start and complete the Blitz Training Matrix as fast as possible. This gives you the fundamentals of what we do here at Breeze and how we do it.
Link: https://start.blitztrainingmatrix.com/

BREEZE TRAINING HUB
Be sure to request Viewer access to our Breeze Training Hub/Google Drive. This houses all of our past recorded trainings like sales training, carrier walkthroughs, top producer Q&A's, and more.
Link: https://drive.google.com/drive/folders/1hQt8n-yIcpCSwpLzbRFzszNoX7e-EHuJ?usp=drive_link

What Makes Breeze Different

At Breeze, we provide:

• Structured training and support
• Proven sales systems
• Access to top carriers
• High-level mentorship
• Growth opportunities as a producer or builder

Our mission is simple:
Help you build a real business — not just sell policies.

Important Note

Your success here will come from taking action quickly.

Agents who move fastest through contracting and begin activity early consistently see the best results.

Do not wait until everything feels perfect — progress beats perfection.

If you have any questions, reach out to your manager/upline directly.

- Breeze Financial Group
'''
    
    return {
        "subject": "Welcome to Breeze!",
        "html": get_base_template(content, "Welcome to Breeze Financial Group - Your ATLAS account is now active"),
        "text": text_content
    }


async def send_new_recruit_welcome_email(to: str, first_name: str) -> Dict[str, Any]:
    """
    Send welcome email to new recruit when they activate their Atlas account.
    Includes the Breeze Advizor Guide PDF attachment.
    """
    email_data = build_new_recruit_welcome_email(first_name)
    
    # Prepare attachment if file exists
    attachments = None
    if BREEZE_GUIDE_PATH.exists():
        try:
            with open(BREEZE_GUIDE_PATH, 'rb') as f:
                pdf_content = base64.b64encode(f.read()).decode('utf-8')
            attachments = [{
                "filename": "Breeze_Advizor_Guide.pdf",
                "content": pdf_content,
                "content_type": "application/pdf"
            }]
            logger.info(f"Attaching Breeze Advizor Guide PDF to welcome email")
        except Exception as e:
            logger.error(f"Failed to attach PDF: {e}")
    else:
        logger.warning(f"Breeze Advizor Guide PDF not found at {BREEZE_GUIDE_PATH}")
    
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "new_recruit_welcome"}],
        attachments=attachments
    )


# ============================================
# Template H: Contracting Instructions Email
# ============================================

def build_contracting_instructions_email(first_name: str) -> Dict[str, str]:
    """Build contracting instructions email for new recruits"""
    
    breeze_link = "https://accounts.surancebay.com/oauth/authorize?redirect_uri=https:%2F%2Fsurelc.surancebay.com%2Fproducer%2Foauth%3FreturnUrl%3D%252Fprofile%252Fcontact-info%253FgaId%253D1139%2526gaId%253D1139%2526branchVisible%253Dtrue%2526branchEditable%253Dfalse%2526branchRequired%253Dtrue%2526dba%253DP%2526autoAdd%253Dfalse%2526requestMethod%253DGET&gaId=1139&client_id=surecrmweb&response_type=code"
    
    aegis_link = "https://accounts.surancebay.com/oauth/authorize?redirect_uri=https:%2F%2Fsurelc.surancebay.com%2Fproducer%2Foauth%3FreturnUrl%3D%252Fprofile%252Fcontact-info%253FgaId%253D145%2526gaId%253D145%2526branch%253DAegis%252520Financial%252520Inc.%2526branchVisible%253Dtrue%2526branchEditable%253Dfalse%2526branchRequired%253Dtrue%2526autoAdd%253Dfalse%2526requestMethod%253DGET&gaId=145&client_id=surecrmweb&response_type=code"
    
    eo_link = "https://www.nextinsurance.com/lps/errors-and-omissions-insurance/?gad_source=1&gad_campaignid=18995304646&gbraid=0AAAAADcOmvQJ5_fh-Xd4HKakK72XbbDyX&gclid=EAIaIQobChMIo5KGgIeCkwMVJDBECB3P3SqlEAAYASABEgKbzfD_BwE"
    
    aml_link = "https://aml.surancebay.com"
    
    content = f'''
        <p style="margin: 0 0 20px; color: #334155; font-size: 16px; line-height: 1.7;">
            <strong>{first_name}</strong>, there are <strong style="color: #dc2626;">TWO</strong> separate contracting links you <strong>MUST</strong> register with to submit for carriers.
        </p>
        
        <!-- First Link Section -->
        <div style="background-color: #f0f9ff; border: 1px solid #0891b2; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 15px; color: #0e7490; font-size: 16px; font-weight: 600;">
                1️⃣ Breeze Financial Group Direct Link
            </h3>
            <p style="margin: 0 0 15px; color: #334155; font-size: 14px; line-height: 1.6;">
                <a href="{breeze_link}" style="color: #0891b2; word-break: break-all;">Click here to register with Breeze Financial Group</a>
            </p>
            <p style="margin: 0 0 15px; color: #334155; font-size: 14px; line-height: 1.6;">
                Register a new account in this link to get started on contracting. Put in all of your information (banking, drivers license, personal info, etc.), have your E&O and AML ready to attach in the necessary fields.
            </p>
            <p style="margin: 0 0 10px; color: #1e293b; font-size: 14px; font-weight: 600;">
                Contracts you will request if applicable:
            </p>
            <ol style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.8;">
                <li>Aflac</li>
                <li>Americo</li>
                <li>American Amicable</li>
                <li>Kansas City Life</li>
                <li>National Life Group</li>
                <li>Royal Neighbors</li>
                <li>TransAmerica</li>
                <li>United Home Life</li>
            </ol>
        </div>
        
        <!-- Second Link Section -->
        <div style="background-color: #faf5ff; border: 1px solid #9333ea; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 15px; color: #7e22ce; font-size: 16px; font-weight: 600;">
                2️⃣ Aegis Financial (IMO Partner) Link
            </h3>
            <p style="margin: 0 0 15px; color: #334155; font-size: 14px; line-height: 1.6;">
                <a href="{aegis_link}" style="color: #9333ea; word-break: break-all;">Click here to register with Aegis Financial</a>
            </p>
            <p style="margin: 0 0 15px; color: #334155; font-size: 14px; line-height: 1.6;">
                Register a new account in this link to get started on contracting. Put in all of your information (banking, drivers license, personal info, etc.), have your E&O and AML ready to attach in the necessary fields.
            </p>
            <p style="margin: 0 0 10px; color: #1e293b; font-size: 14px; font-weight: 600;">
                Contracts you will request if applicable:
            </p>
            <ol style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.8;">
                <li>American Equity</li>
                <li>Athene (National)</li>
                <li>Fidelity &amp; Guaranty</li>
            </ol>
        </div>
        
        <!-- Important Notice -->
        <div style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 12px; color: #92400e; font-size: 15px; font-weight: 600;">
                ⚠️ IMPORTANT
            </h3>
            <p style="margin: 0 0 15px; color: #78350f; font-size: 14px; line-height: 1.7;">
                If you already have active writing numbers with <strong>ANY</strong> of the carriers listed above you will request to <strong>'Transfer'</strong> the carrier in SuranceBay, instead of requesting new contract.
            </p>
            <p style="margin: 0; color: #78350f; font-size: 14px; line-height: 1.7;">
                <strong>Additional Note:</strong> If you are coming from FFL (Family First Life) or PHP, you must wait <strong>12 months</strong> from the date of contracting with specific carrier or date of last written business with specific carrier (whichever is sooner), in order to transfer. If you are coming from another IMO that is NOT FFL or PHP, same rules apply except you must wait <strong>6 months</strong>.
            </p>
        </div>
        
        <!-- Resources Section -->
        <div style="background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <h3 style="margin: 0 0 15px; color: #1e293b; font-size: 15px; font-weight: 600;">
                📋 Required Resources
            </h3>
            <p style="margin: 0 0 10px; color: #334155; font-size: 14px; line-height: 1.7;">
                <strong>E&O Insurance (if needed):</strong><br>
                <a href="{eo_link}" style="color: #0891b2;">Get E&O Insurance from Next Insurance</a>
            </p>
            <p style="margin: 0; color: #334155; font-size: 14px; line-height: 1.7;">
                <strong>AML Training (please save the PDF when finished):</strong><br>
                <a href="{aml_link}" style="color: #0891b2;">Complete AML Training</a>
            </p>
        </div>
        
        <p style="margin: 25px 0 0; color: #334155; font-size: 16px; line-height: 1.7;">
            If you have any questions, please reach out to your manager/upline immediately.
        </p>
        
        <p style="margin: 30px 0 0; color: #1e293b; font-size: 16px;">
            Thank you,<br>
            <strong>Breeze</strong>
        </p>
    '''
    
    text_content = f'''{first_name}, there are TWO separate contracting links you MUST register with to submit for carriers.

The first link is the direct Breeze Financial Group link:
{breeze_link}

Register a new account in this link to get started on contracting. Put in all of your information (banking, drivers license, personal info, etc.), have your E&O and AML ready to attach in the necessary fields.

Contracts you will request if applicable:
1. Aflac
2. Americo
3. American Amicable
4. Kansas City Life
5. National Life Group
6. Royal Neighbors
7. TransAmerica
8. United Home Life

The second link is with our IMO partners @ Aegis Financial:
{aegis_link}

Register a new account in this link to get started on contracting. Put in all of your information (banking, drivers license, personal info, etc.), have your E&O and AML ready to attach in the necessary fields.

Contracts you will request if applicable:
1. American Equity
2. Athene (National)
3. Fidelity & Guaranty

IMPORTANT: If you already have active writing numbers with ANY of the carriers listed above you will request to 'Transfer' the carrier in SuranceBay, instead of requesting new contract.

Additional Note: If you are coming from FFL (Family First Life) or PHP, you must wait 12 months from the date of contracting with specific carrier or date of last written business with specific carrier (whichever is sooner), in order to transfer. If you are coming from another IMO that is NOT FFL or PHP, same rules apply except you must wait 6 months.

E&O if needed: {eo_link}

AML - please save the PDF when finished: {aml_link}

If you have any questions, please reach out to your manager/upline immediately.

Thank you,
Breeze
'''
    
    return {
        "subject": "Contracting Instructions (IMPORTANT)",
        "html": get_base_template(content, f"{first_name}, complete your contracting with these two links"),
        "text": text_content
    }


async def send_contracting_instructions_email(to: str, first_name: str) -> Dict[str, Any]:
    """Send contracting instructions email to new recruit"""
    email_data = build_contracting_instructions_email(first_name)
    return await send_transactional_email(
        to=to,
        subject=email_data["subject"],
        html=email_data["html"],
        text=email_data["text"],
        tags=[{"name": "category", "value": "contracting_instructions"}]
    )


# ============================================
# Zinnia Sync Failure Email
# ============================================

SYNC_ALERT_RECIPIENTS = [
    "kyle@breezewealthmanagement.com",
    "bb@breezewealthmanagement.com",
]

async def send_sync_failure_email(
    to: str,
    sync_type: str,
    error: str,
    timestamp: str
) -> Dict[str, Any]:
    """Send sync failure alert email to admins"""
    subject = f"[Atlas] Zinnia Sync Failed — {sync_type}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #e2e8f0; padding: 32px; border-radius: 12px;">
        <div style="border-left: 4px solid #ef4444; padding-left: 16px; margin-bottom: 24px;">
            <h2 style="margin: 0 0 4px; color: #f87171; font-size: 20px;">Zinnia Sync Failure Alert</h2>
            <p style="margin: 0; color: #94a3b8; font-size: 14px;">An automated sync job has failed and requires attention.</p>
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b; color: #94a3b8; font-size: 13px; width: 140px;">Sync Type</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b; color: #e2e8f0; font-size: 13px; font-weight: 600; text-transform: capitalize;">{sync_type}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b; color: #94a3b8; font-size: 13px;">Error</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b; color: #fca5a5; font-size: 13px;">{error}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #94a3b8; font-size: 13px;">Timestamp</td>
                <td style="padding: 10px 0; color: #e2e8f0; font-size: 13px;">{timestamp}</td>
            </tr>
        </table>
        <p style="margin: 24px 0 0; color: #64748b; font-size: 12px;">Log in to Atlas and navigate to the Zinnia Admin panel to review failed syncs and retry.</p>
    </div>
    """
    text = f"Zinnia Sync Failure\nSync Type: {sync_type}\nError: {error}\nTimestamp: {timestamp}"
    return await send_transactional_email(
        to=SYNC_ALERT_RECIPIENTS,
        subject=subject,
        html=html,
        text=text,
        tags=[{"name": "category", "value": "zinnia_sync_failure"}]
    )
