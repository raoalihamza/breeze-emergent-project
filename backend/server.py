from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import secrets
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import random
from collections import defaultdict
import time
import aiofiles
import shutil
import asyncio

ROOT_DIR = Path(__file__).parent
KNOWLEDGE_FILES_DIR = ROOT_DIR / 'knowledge_files'
KNOWLEDGE_FILES_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT_DIR / '.env')

from uuid import uuid4

# Import email service
from email_service import (
    send_welcome_email,
    send_password_reset_email,
    send_recruit_invite_email,
    send_recruit_activated_email,
    send_ticket_status_email,
    send_admin_ticket_notification,
    send_new_recruit_welcome_email,
    send_contracting_instructions_email
)

# Import Atlas AI service
from atlas_ai_service import get_atlas_ai_response, process_uploaded_document, set_db as set_atlas_db
from zinnia_service import (
    sync_all, sync_agents, sync_production,
    sync_case_status, start_scheduler,
    get_sync_status,
    set_db as set_zinnia_db
)

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

SECRET_KEY = os.environ.get('JWT_SECRET', 'breeze-matrix-secret-key-change-in-production')
ALGORITHM = 'HS256'
JWT_SECRET = SECRET_KEY  # Alias for compatibility
JWT_ALGORITHM = ALGORITHM  # Alias for compatibility
JWT_EXPIRATION_HOURS = 168  # 7 days

security = HTTPBearer()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting for password reset (in-memory, resets on restart)
password_reset_requests = defaultdict(list)
PASSWORD_RESET_LIMIT = 3  # max requests
PASSWORD_RESET_WINDOW = 3600  # 1 hour in seconds

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "agent"
    npn: Optional[str] = None
    phone: Optional[str] = None
    comp_percentage: float = 0.0
    upline_id: Optional[str] = None
    status: str = "active"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    invite_token: str

class LicensedState(BaseModel):
    state: str
    license_number: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    role: str
    npn: Optional[str]
    phone: Optional[str] = None
    comp_percentage: float
    upline_id: Optional[str]
    upline_name: Optional[str] = None
    profile_picture: Optional[str] = None
    status: str
    created_at: str
    last_login: Optional[str] = None
    licensed_states: List[Dict[str, Optional[str]]] = []
    needs_password_reset: bool = False
    # Impersonation fields
    impersonated_by: Optional[str] = None
    impersonated_by_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class PasswordResetRequest(BaseModel):
    new_password: str

class LicensedStatesUpdate(BaseModel):
    licensed_states: List[Dict[str, Optional[str]]]

class ProfileExtendedResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    role: str
    npn: Optional[str]
    phone: Optional[str] = None
    comp_percentage: float
    upline_id: Optional[str]
    upline_name: Optional[str] = None
    profile_picture: Optional[str] = None
    status: str
    created_at: str
    last_login: Optional[str] = None
    licensed_states: List[Dict[str, Optional[str]]] = []
    last_production_date: Optional[str] = None
    needs_password_reset: bool = False

class InviteCreate(BaseModel):
    recruit_email: EmailStr
    recruit_first_name: str
    recruit_last_name: str
    recruit_npn: str
    comp_percentage: float
    message: Optional[str] = None

class InviteResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    token: str
    recruit_email: str
    recruit_first_name: Optional[str] = ""
    recruit_last_name: Optional[str] = ""
    recruit_npn: Optional[str] = None
    inviter_id: str
    inviter_name: str
    comp_percentage: float
    message: Optional[str]
    status: str
    created_at: str
    expires_at: str

class AdminInviteCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    message: Optional[str] = None

class AdminInviteResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    token: str
    email: str
    first_name: str
    last_name: str
    inviter_id: str
    inviter_name: str
    message: Optional[str]
    status: str
    created_at: str
    expires_at: str

class ResourceCreate(BaseModel):
    title: str
    category: str
    type: str
    url: Optional[str] = None
    description: Optional[str] = None

class ResourceResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    category: str
    type: str
    url: Optional[str]
    description: Optional[str]
    created_at: str
    created_by: str

class CarrierCreate(BaseModel):
    name: str
    description: Optional[str] = None
    guideline_url: Optional[str] = None
    notes: Optional[str] = None

class CarrierResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    description: Optional[str]
    guideline_url: Optional[str]
    notes: Optional[str]
    created_at: str

# Agent Carrier Settings Models
class AgentCarrierSettingsUpdate(BaseModel):
    carrier_id: str
    writing_number: Optional[str] = None
    is_appointed: bool = False

class AgentCarrierSettingsResponse(BaseModel):
    carrier_id: str
    writing_number: Optional[str] = None
    is_appointed: bool = False

class ProductionCreate(BaseModel):
    agent_id: str
    carrier: str
    policy_number: str
    submitted_ap: float
    issued_paid_ap: float
    status: str
    submission_date: str

class ProductionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    agent_id: str
    agent_name: str
    carrier: str
    policy_number: str
    submitted_ap: float
    issued_paid_ap: float
    status: str
    submission_date: str
    created_at: str

class KPIEntryCreate(BaseModel):
    date: str
    dials_made: int = 0
    contacts_made: int = 0
    appointments_set: int = 0
    presentations_given: int = 0
    sales_made: int = 0

class KPIEntryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    date: str
    dials_made: int
    contacts_made: int
    appointments_set: int
    presentations_given: int
    sales_made: int
    created_at: str
    updated_at: str

class WeeklyCEOReportResponse(BaseModel):
    week_start: str
    week_end: str
    kpi_summary: Dict[str, Any]
    improvements: List[str]
    declines: List[str]
    executive_summary: Optional[str] = None
    what_went_well: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    focus_areas: List[str]
    self_reflection_questions: List[str]

class BeneficiaryInfo(BaseModel):
    name: str
    phone_number: str

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: str
    state: str
    carrier: str
    product: str
    product_type: str  # IUL, Term, FEX, Whole Life, Annuity
    policy_number: str
    monthly_premium: Optional[float] = None  # For IUL, Term, FEX, Whole Life
    premium: Optional[float] = None  # For Annuity (lump sum)
    target_premium: Optional[float] = None  # For IUL specifically
    coverage_amount: Optional[float] = None  # Face amount / coverage amount
    status: str  # Pending Approval/Issue, Issued, Cancelled, Missed Payment
    date_submitted: Optional[str] = None
    date_issued: Optional[str] = None
    lead_source: str  # Breeze Lead, Warm Market, Referral, Self-Generated, Other
    lead_source_other: Optional[str] = None
    client_why: Optional[str] = None
    beneficiaries: Optional[List[BeneficiaryInfo]] = []
    additional_notes: Optional[str] = None

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    state: Optional[str] = None
    carrier: Optional[str] = None
    product: Optional[str] = None
    product_type: Optional[str] = None
    policy_number: Optional[str] = None
    monthly_premium: Optional[float] = None
    premium: Optional[float] = None
    target_premium: Optional[float] = None
    status: Optional[str] = None
    date_submitted: Optional[str] = None
    date_issued: Optional[str] = None
    lead_source: Optional[str] = None
    lead_source_other: Optional[str] = None
    client_why: Optional[str] = None
    beneficiaries: Optional[List[BeneficiaryInfo]] = None
    additional_notes: Optional[str] = None

class ClientResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    agent_id: str
    agent_name: Optional[str] = None  # Name of agent who owns this client
    added_by_agent_id: Optional[str] = None  # ID of agent who originally added
    added_by_agent_name: Optional[str] = None  # Name of agent who originally added
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_date: str
    state: str
    carrier: str
    product: str
    product_type: Optional[str] = None  # Made optional for backward compatibility
    policy_number: str
    monthly_premium: Optional[float] = None
    annual_premium: Optional[float] = None
    premium: Optional[float] = None
    target_premium: Optional[float] = None
    coverage_amount: Optional[float] = None
    status: Optional[str] = None  # Made optional for backward compatibility
    date_submitted: Optional[str] = None
    date_issued: Optional[str] = None
    lead_source: Optional[str] = None  # Made optional for backward compatibility
    lead_source_other: Optional[str] = None
    client_why: Optional[str] = None
    beneficiaries: List[Dict[str, str]]
    additional_notes: Optional[str] = None
    created_at: str
    updated_at: str

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str, role: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({'id': payload['user_id']}, {'_id': 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Ensure all admin users have 135% commission permanently
        if user.get('role') == 'admin':
            user['comp_percentage'] = 135
        
        # Add impersonation information from JWT token if present
        if 'impersonated_by' in payload:
            user['impersonated_by'] = payload['impersonated_by']
            user['impersonated_by_name'] = payload.get('impersonated_by_name')
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_role(user: dict, allowed_roles: List[str]):
    if user['role'] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

# Auth Endpoints
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    # Case-insensitive email lookup using regex
    user = await db.users.find_one({'email': {'$regex': f'^{data.email}$', '$options': 'i'}}, {'_id': 0})
    if not user or not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.get('status') == 'disabled':
        raise HTTPException(status_code=403, detail="Your account has been disabled. Please contact an administrator.")
    
    if user.get('status') != 'active':
        raise HTTPException(status_code=403, detail="Account inactive")
    
    # Update last login
    await db.users.update_one(
        {'id': user['id']},
        {'$set': {'last_login': datetime.now(timezone.utc).isoformat()}}
    )
    user['last_login'] = datetime.now(timezone.utc).isoformat()
    
    # Add upline name if upline exists
    if user.get('upline_id'):
        upline = await db.users.find_one({'id': user['upline_id']}, {'_id': 0, 'name': 1})
        user['upline_name'] = upline['name'] if upline else None
    
    token = create_jwt_token(user['id'], user['email'], user['role'])
    user_response = UserResponse(**user)
    return LoginResponse(token=token, user=user_response)

@api_router.post("/auth/signup", response_model=LoginResponse)
async def signup(data: UserCreate):
    existing_user = await db.users.find_one({'email': data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    invite = await db.invites.find_one({'token': data.invite_token, 'status': 'pending'}, {'_id': 0})
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite token")
    
    if invite['recruit_email'] != data.email:
        raise HTTPException(status_code=400, detail="Email does not match invite")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite token expired")
    
    # Check NPN uniqueness
    existing_npn = await db.users.find_one({'npn': invite['recruit_npn']})
    if existing_npn:
        raise HTTPException(status_code=400, detail="NPN already registered. Each agent must have a unique NPN.")
    
    user_id = str(uuid.uuid4())
    recruit_full_name = f"{invite.get('recruit_first_name', '')} {invite.get('recruit_last_name', '')}".strip()
    if not recruit_full_name and invite.get('recruit_name'):
        recruit_full_name = invite['recruit_name']
    
    user_doc = {
        'id': user_id,
        'email': data.email,
        'name': recruit_full_name or data.name,
        'password_hash': hash_password(data.password),
        'role': 'agent',
        'npn': invite.get('recruit_npn') or invite['recruit_npn'],
        'comp_percentage': invite['comp_percentage'],
        'upline_id': invite['inviter_id'],
        'status': 'active',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'needs_password_reset': False
    }
    
    await db.users.insert_one(user_doc)
    await db.invites.update_one(
        {'token': data.invite_token},
        {'$set': {'status': 'accepted', 'accepted_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create audit log for new user registration via invite
    await create_audit_log(
        admin_id=invite['inviter_id'],
        admin_name=invite['inviter_name'],
        action='user_registered_via_invite',
        target_user_id=user_id,
        target_user_name=recruit_full_name,
        details={
            'new_user_email': data.email,
            'invited_by_id': invite['inviter_id'],
            'invited_by_name': invite['inviter_name'],
            'comp_percentage': invite['comp_percentage'],
            'invite_created_at': invite.get('created_at'),
            'registration_completed_at': datetime.now(timezone.utc).isoformat()
        }
    )
    
    # Send new recruit welcome email with Breeze Advizor Guide PDF attachment
    try:
        first_name = invite.get('recruit_first_name', recruit_full_name.split()[0] if recruit_full_name else 'Agent')
        await send_new_recruit_welcome_email(
            to=data.email,
            first_name=first_name
        )
        logger.info(f"Sent new recruit welcome email with PDF to {data.email}")
    except Exception as e:
        logger.error(f"Failed to send new recruit welcome email to {data.email}: {e}")
    
    # Send contracting instructions email immediately after welcome email
    try:
        first_name = invite.get('recruit_first_name', recruit_full_name.split()[0] if recruit_full_name else 'Agent')
        await send_contracting_instructions_email(
            to=data.email,
            first_name=first_name
        )
        logger.info(f"Sent contracting instructions email to {data.email}")
    except Exception as e:
        logger.error(f"Failed to send contracting instructions email to {data.email}: {e}")
    
    # Notify upline about new recruit activation
    try:
        upline = await db.users.find_one({'id': invite['inviter_id']}, {'_id': 0})
        if upline and upline.get('email'):
            await send_recruit_activated_email(
                to=upline['email'],
                upline_name=upline['name'],
                recruit_name=recruit_full_name,
                recruit_email=data.email,
                comp_level=invite['comp_percentage']
            )
            logger.info(f"Sent recruit activation notification to {upline['email']}")
    except Exception as e:
        logger.error(f"Failed to send recruit activation notification: {e}")
    
    token = create_jwt_token(user_id, data.email, 'agent')
    user_response = UserResponse(**user_doc)
    return LoginResponse(token=token, user=user_response)

@api_router.post("/auth/change-password")
async def change_password(data: PasswordResetRequest, current_user: dict = Depends(get_current_user)):
    """Change password for logged-in user"""
    new_hash = hash_password(data.new_password)
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'password_hash': new_hash, 'needs_password_reset': False}}
    )
    return {"message": "Password updated successfully"}

# Password Reset Endpoints (for forgotten passwords)
@api_router.post("/auth/forgot-password")
async def forgot_password(data: dict):
    """Request a password reset email"""
    email = data.get('email', '').lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Rate limiting check
    current_time = time.time()
    # Clean old requests
    password_reset_requests[email] = [
        t for t in password_reset_requests[email] 
        if current_time - t < PASSWORD_RESET_WINDOW
    ]
    
    if len(password_reset_requests[email]) >= PASSWORD_RESET_LIMIT:
        raise HTTPException(
            status_code=429, 
            detail="Too many password reset requests. Please try again later."
        )
    
    # Find user
    user = await db.users.find_one({'email': email}, {'_id': 0})
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store reset token
    reset_doc = {
        'id': str(uuid4()),
        'user_id': user['id'],
        'token': reset_token,
        'expires_at': expires_at.isoformat(),
        'used_at': None,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.password_reset_tokens.insert_one(reset_doc)
    
    # Record the request for rate limiting
    password_reset_requests[email].append(current_time)
    
    # Send email (non-blocking, don't fail if email fails)
    try:
        first_name = user.get('name', '').split()[0] if user.get('name') else 'User'
        await send_password_reset_email(user['email'], first_name, reset_token)
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
    
    return {"message": "If an account exists with this email, a password reset link has been sent."}

@api_router.post("/auth/reset-password")
async def reset_password_with_token(data: dict):
    """Reset password using token"""
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and password are required")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Find token
    reset_record = await db.password_reset_tokens.find_one({'token': token}, {'_id': 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    
    # Check if already used
    if reset_record.get('used_at'):
        raise HTTPException(status_code=400, detail="This reset link has already been used")
    
    # Check expiration
    expires_at = datetime.fromisoformat(reset_record['expires_at'].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="This reset link has expired")
    
    # Update password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.users.update_one(
        {'id': reset_record['user_id']},
        {'$set': {'password_hash': hashed_password, 'needs_password_reset': False}}
    )
    
    # Mark token as used
    await db.password_reset_tokens.update_one(
        {'token': token},
        {'$set': {'used_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Password has been reset successfully"}

@api_router.get("/auth/verify-reset-token")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid"""
    reset_record = await db.password_reset_tokens.find_one({'token': token}, {'_id': 0})
    
    if not reset_record:
        return {"valid": False, "message": "Invalid reset link"}
    
    if reset_record.get('used_at'):
        return {"valid": False, "message": "This reset link has already been used"}
    
    expires_at = datetime.fromisoformat(reset_record['expires_at'].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        return {"valid": False, "message": "This reset link has expired"}
    
    return {"valid": True}

# Email Verification Endpoints
@api_router.post("/auth/verify-email")
async def verify_email(data: dict):
    """Verify email using token"""
    token = data.get('token')
    
    if not token:
        raise HTTPException(status_code=400, detail="Verification token is required")
    
    # Find token
    verify_record = await db.email_verification_tokens.find_one({'token': token}, {'_id': 0})
    
    if not verify_record:
        raise HTTPException(status_code=400, detail="Invalid verification link")
    
    if verify_record.get('used_at'):
        return {"message": "Email already verified"}
    
    # Check expiration (24 hours)
    expires_at = datetime.fromisoformat(verify_record['expires_at'].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Verification link has expired")
    
    # Mark user as verified
    await db.users.update_one(
        {'id': verify_record['user_id']},
        {'$set': {'email_verified': True, 'email_verified_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    # Mark token as used
    await db.email_verification_tokens.update_one(
        {'token': token},
        {'$set': {'used_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Email verified successfully"}

@api_router.post("/auth/resend-verification")
async def resend_verification_email(current_user: dict = Depends(get_current_user)):
    """Resend verification email"""
    if current_user.get('email_verified'):
        return {"message": "Email is already verified"}
    
    # Generate new token
    verify_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    verify_doc = {
        'id': str(uuid4()),
        'user_id': current_user['id'],
        'token': verify_token,
        'expires_at': expires_at.isoformat(),
        'used_at': None,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.email_verification_tokens.insert_one(verify_doc)
    
    # Send email
    try:
        first_name = current_user.get('name', '').split()[0] if current_user.get('name') else 'User'
        await send_welcome_email(current_user['email'], first_name, verify_token)
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")
    
    return {"message": "Verification email sent"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    # Add upline name if upline exists
    if current_user.get('upline_id'):
        upline = await db.users.find_one({'id': current_user['upline_id']}, {'_id': 0, 'name': 1})
        current_user['upline_name'] = upline['name'] if upline else None
    return UserResponse(**current_user)

@api_router.post("/auth/profile-picture")
async def update_profile_picture(data: dict, current_user: dict = Depends(get_current_user)):
    profile_picture = data.get('profile_picture')
    if not profile_picture:
        raise HTTPException(status_code=400, detail="Profile picture data required")
    
    # Store base64 image data
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'profile_picture': profile_picture}}
    )
    return {"message": "Profile picture updated successfully", "profile_picture": profile_picture}

@api_router.put("/user/licensed-states")
async def update_licensed_states(data: LicensedStatesUpdate, current_user: dict = Depends(get_current_user)):
    """Update the user's licensed states"""
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'licensed_states': data.licensed_states}}
    )
    return {"message": "Licensed states updated successfully", "licensed_states": data.licensed_states}

@api_router.put("/user/phone")
async def update_user_phone(data: dict, current_user: dict = Depends(get_current_user)):
    """Update the user's phone number"""
    phone = data.get('phone', '').strip()
    
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'phone': phone}}
    )
    
    return {"message": "Phone number updated successfully", "phone": phone}

@api_router.get("/user/profile-extended", response_model=ProfileExtendedResponse)
async def get_profile_extended(current_user: dict = Depends(get_current_user)):
    """Get extended profile information including last production date"""
    # Get user data
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'password_hash': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add upline name if upline exists
    if user.get('upline_id'):
        upline = await db.users.find_one({'id': user['upline_id']}, {'_id': 0, 'name': 1})
        user['upline_name'] = upline['name'] if upline else None
    
    # Calculate last production date from clients collection
    last_client = await db.clients.find_one(
        {'agent_id': current_user['id']},
        {'_id': 0, 'date_submitted': 1},
        sort=[('date_submitted', -1)]
    )
    
    user['last_production_date'] = last_client.get('date_submitted') if last_client else None
    
    # Ensure licensed_states field exists
    if 'licensed_states' not in user:
        user['licensed_states'] = []
    
    return ProfileExtendedResponse(**user)

# User/Hierarchy Endpoints
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(1000)
    return [UserResponse(**u) for u in users]

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if current_user['role'] == 'agent' and current_user['id'] != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # For leaders, verify the user is in their downline
    if current_user['role'] == 'leader':
        async def is_in_downline(target_id: str, leader_id: str) -> bool:
            if target_id == leader_id:
                return True
            target = await db.users.find_one({'id': target_id}, {'_id': 0})
            if not target or not target.get('upline_id'):
                return False
            if target['upline_id'] == leader_id:
                return True
            return await is_in_downline(target['upline_id'], leader_id)
        
        if not await is_in_downline(user_id, current_user['id']):
            raise HTTPException(status_code=403, detail="User not in your downline")
    
    # Add upline name
    if user.get('upline_id'):
        upline = await db.users.find_one({'id': user['upline_id']}, {'_id': 0, 'name': 1})
        user['upline_name'] = upline['name'] if upline else None
    
    return UserResponse(**user)

@api_router.get("/users/{user_id}/full-profile")
async def get_user_full_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get full profile including carrier settings and licensed states (Admin only)"""
    # Only admins can view full profiles
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add upline name
    if user.get('upline_id'):
        upline = await db.users.find_one({'id': user['upline_id']}, {'_id': 0, 'name': 1})
        user['upline_name'] = upline['name'] if upline else None
    
    # Ensure licensed_states field exists
    if 'licensed_states' not in user:
        user['licensed_states'] = []
    
    # Get carrier settings for this agent
    carrier_settings = await db.agent_carrier_settings.find(
        {'agent_id': user_id},
        {'_id': 0}
    ).to_list(100)
    
    # Get all carriers to map names
    carriers = await db.carriers.find({}, {'_id': 0}).to_list(100)
    carriers_map = {c['id']: c for c in carriers}
    
    # Enrich carrier settings with carrier info
    appointed_carriers = []
    for setting in carrier_settings:
        if setting.get('is_appointed'):
            carrier = carriers_map.get(setting['carrier_id'])
            if carrier:
                appointed_carriers.append({
                    'carrier_id': setting['carrier_id'],
                    'carrier_name': carrier.get('name', 'Unknown'),
                    'carrier_slug': carrier.get('slug', ''),
                    'primary_color': carrier.get('primary_color', '#6b7280'),
                    'writing_number': setting.get('writing_number', ''),
                    'is_appointed': True
                })
    
    return {
        **user,
        'appointed_carriers': appointed_carriers
    }


@api_router.get("/hierarchy/tree")
async def get_hierarchy_tree(current_user: dict = Depends(get_current_user)):
    async def build_tree(user_id: str) -> dict:
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0})
        if not user:
            return None
        
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0, 'password_hash': 0}).to_list(1000)
        children = []
        for agent in downline:
            child_tree = await build_tree(agent['id'])
            if child_tree:
                children.append(child_tree)
        
        return {
            **user,
            'children': children,
            'team_size': len(children)
        }
    
    if current_user['role'] == 'admin':
        top_users = await db.users.find({'upline_id': None}, {'_id': 0, 'password_hash': 0}).to_list(100)
        trees = []
        for user in top_users:
            tree = await build_tree(user['id'])
            if tree:
                trees.append(tree)
        return {'trees': trees}
    else:
        # All users (agents, leaders, etc.) can see their own downline tree
        tree = await build_tree(current_user['id'])
        return {'trees': [tree] if tree else []}

@api_router.get("/hierarchy/downline")
async def get_downline(current_user: dict = Depends(get_current_user)):
    async def get_all_downline(user_id: str) -> List[dict]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0, 'password_hash': 0}).to_list(1000)
        all_agents = downline.copy()
        for agent in downline:
            sub_downline = await get_all_downline(agent['id'])
            all_agents.extend(sub_downline)
        return all_agents
    
    if current_user['role'] == 'admin':
        users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(1000)
        return [UserResponse(**u) for u in users]
    else:
        # All users can see their downline (direct + indirect)
        downline = await get_all_downline(current_user['id'])
        downline.insert(0, current_user)
        return [UserResponse(**u) for u in downline]

@api_router.get("/hierarchy/stats")
async def get_team_stats(current_user: dict = Depends(get_current_user)):
    async def get_all_downline(user_id: str) -> List[dict]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
        all_agents = downline.copy()
        for agent in downline:
            sub_downline = await get_all_downline(agent['id'])
            all_agents.extend(sub_downline)
        return all_agents
    
    # Get direct agents (those with upline_id = current_user's id)
    direct_agents = await db.users.find({'upline_id': current_user['id']}, {'_id': 0}).to_list(1000)
    direct_count = len(direct_agents)
    
    # Get all downline (direct + indirect)
    all_downline = await get_all_downline(current_user['id'])
    total_count = len(all_downline)
    
    # For admin viewing all users in system
    if current_user['role'] == 'admin':
        all_users = await db.users.find({'id': {'$ne': current_user['id']}}, {'_id': 0}).to_list(1000)
        total_count = len(all_users)
    
    # Calculate indirect count
    indirect_count = total_count - direct_count
    
    # Calculate new agents this month
    current_month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if current_user['role'] == 'admin':
        new_this_month = await db.users.count_documents({
            'created_at': {'$gte': current_month_start.isoformat()}
        })
    else:
        # Get all downline IDs
        if current_user['role'] == 'leader':
            downline_ids = [agent['id'] for agent in all_downline]
        else:
            downline_ids = []
        
        new_this_month = await db.users.count_documents({
            'id': {'$in': downline_ids},
            'created_at': {'$gte': current_month_start.isoformat()}
        }) if downline_ids else 0
    
    return {
        'direct_agents': direct_count,
        'indirect_agents': indirect_count,
        'total_downline': total_count,
        'new_this_month': new_this_month
    }

@api_router.patch("/users/{user_id}")
async def update_user(user_id: str, updates: dict, current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin', 'leader'])
    
    allowed_fields = ['name', 'npn', 'comp_percentage', 'role', 'status']
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    result = await db.users.update_one({'id': user_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User updated successfully"}

# Invite Endpoints
@api_router.post("/invites", response_model=InviteResponse)
async def create_invite(data: InviteCreate, current_user: dict = Depends(get_current_user)):
    existing_user = await db.users.find_one({'email': data.recruit_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Account already exists with this email. Please use a different email address.")
    
    # Check if NPN is already in use
    existing_npn = await db.users.find_one({'npn': data.recruit_npn})
    if existing_npn:
        raise HTTPException(status_code=400, detail="NPN already registered. Each agent must have a unique NPN.")
    
    # Check if there's a pending invite with this NPN
    # ADMIN OVERRIDE: Admins can send invites even if an active one exists
    is_admin = current_user['role'] == 'admin'
    
    if not is_admin:
        # Regular users: check for existing pending invite
        pending_npn_invite = await db.invites.find_one({'recruit_npn': data.recruit_npn, 'status': 'pending'})
        if pending_npn_invite:
            raise HTTPException(status_code=400, detail="An active invite already exists with this NPN. Please cancel the existing invite first or contact an admin.")
        
        # Also check for pending invite by email
        pending_email_invite = await db.invites.find_one({'recruit_email': data.recruit_email, 'status': 'pending'})
        if pending_email_invite:
            raise HTTPException(status_code=400, detail="An active invite already exists for this email. Please cancel the existing invite first or contact an admin.")
    # Admins can bypass the duplicate check - no error thrown
    
    # Validate comp percentage is within allowed range
    # Comp must be between 0.75 (75%) and (inviter's comp - 5%)
    max_comp = current_user['comp_percentage'] - 5
    if data.comp_percentage < 0 or data.comp_percentage > max_comp:
        raise HTTPException(
            status_code=400, 
            detail=f"Commission percentage must be between 0% and {max_comp}% (5% below your level of {current_user['comp_percentage']}%)"
        )
    
    invite_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    recruit_full_name = f"{data.recruit_first_name} {data.recruit_last_name}"
    
    invite_doc = {
        'id': invite_id,
        'token': token,
        'recruit_email': data.recruit_email,
        'recruit_first_name': data.recruit_first_name,
        'recruit_last_name': data.recruit_last_name,
        'recruit_npn': data.recruit_npn,
        'inviter_id': current_user['id'],
        'inviter_name': current_user['name'],
        'comp_percentage': data.comp_percentage,
        'message': data.message,
        'status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'expires_at': expires_at.isoformat()
    }
    
    await db.invites.insert_one(invite_doc)
    
    # Create audit log for invite
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='invite_sent',
        target_user_id=invite_id,
        target_user_name=recruit_full_name,
        details={
            'recruit_email': data.recruit_email,
            'recruit_npn': data.recruit_npn,
            'comp_percentage': data.comp_percentage,
            'inviter_id': current_user['id'],
            'inviter_name': current_user['name']
        }
    )
    
    # Send recruit invite email
    try:
        await send_recruit_invite_email(
            to=data.recruit_email,
            upline_name=current_user['name'],
            invite_token=token
        )
        logger.info(f"Sent invite email to {data.recruit_email}")
    except Exception as e:
        logger.error(f"Failed to send invite email to {data.recruit_email}: {e}")
    
    return InviteResponse(**invite_doc)

@api_router.get("/invites", response_model=List[InviteResponse])
async def get_invites(current_user: dict = Depends(get_current_user)):
    if current_user['role'] == 'admin':
        invites = await db.invites.find({}, {'_id': 0}).to_list(1000)
    else:
        invites = await db.invites.find({'inviter_id': current_user['id']}, {'_id': 0}).to_list(1000)
    return [InviteResponse(**i) for i in invites]

@api_router.post("/invites/{invite_id}/resend", response_model=InviteResponse)
async def resend_invite(invite_id: str, current_user: dict = Depends(get_current_user)):
    """
    Resend an invite link with a new token.
    - Anyone can resend their own expired invites
    - Admins can resend any invite, even if not expired
    """
    # Find the existing invite
    invite = await db.invites.find_one({'id': invite_id}, {'_id': 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    # Check authorization
    is_admin = current_user['role'] == 'admin'
    is_inviter = invite['inviter_id'] == current_user['id']
    
    if not is_admin and not is_inviter:
        raise HTTPException(status_code=403, detail="You can only resend invites you created")
    
    # Check if invite is already accepted
    if invite['status'] == 'accepted':
        raise HTTPException(status_code=400, detail="Cannot resend an invite that has already been accepted")
    
    # Check if invite has expired (unless admin is resending)
    expires_at = datetime.fromisoformat(invite['expires_at'])
    is_expired = expires_at < datetime.now(timezone.utc)
    
    if not is_admin and not is_expired:
        raise HTTPException(
            status_code=400, 
            detail="This invite has not expired yet. Only admins can resend non-expired invites."
        )
    
    # Check if user already signed up
    existing_user = await db.users.find_one({'email': invite['recruit_email']})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email has already signed up")
    
    # Generate new token and expiration
    new_token = str(uuid.uuid4())
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Update the invite
    await db.invites.update_one(
        {'id': invite_id},
        {
            '$set': {
                'token': new_token,
                'expires_at': new_expires_at.isoformat(),
                'status': 'pending',
                'resent_at': datetime.now(timezone.utc).isoformat(),
                'resent_by': current_user['id'],
                'resent_by_name': current_user['name']
            }
        }
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='invite_resent',
        target_user_id=invite_id,
        target_user_name=f"{invite.get('recruit_first_name', '')} {invite.get('recruit_last_name', '')}",
        details={
            'recruit_email': invite['recruit_email'],
            'recruit_npn': invite.get('recruit_npn'),
            'was_expired': is_expired,
            'resent_by_admin': is_admin,
            'original_inviter': invite['inviter_name']
        }
    )
    
    # Send new invite email
    try:
        await send_recruit_invite_email(
            to=invite['recruit_email'],
            upline_name=invite['inviter_name'],
            invite_token=new_token
        )
        logger.info(f"Resent invite email to {invite['recruit_email']}")
    except Exception as e:
        logger.error(f"Failed to resend invite email to {invite['recruit_email']}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send invite email")
    
    # Get updated invite
    updated_invite = await db.invites.find_one({'id': invite_id}, {'_id': 0})
    return InviteResponse(**updated_invite)

@api_router.delete("/invites/{invite_id}")
async def cancel_invite(invite_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancel a recruiting invite.
    - Users can cancel invites they created
    - Admins can cancel any invite
    - Cannot cancel already accepted invites
    """
    # Find the existing invite
    invite = await db.invites.find_one({'id': invite_id}, {'_id': 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    # Check authorization
    is_admin = current_user['role'] == 'admin'
    is_inviter = invite['inviter_id'] == current_user['id']
    
    if not is_admin and not is_inviter:
        raise HTTPException(status_code=403, detail="You can only cancel invites you created")
    
    # Check if invite is already accepted
    if invite['status'] == 'accepted':
        raise HTTPException(status_code=400, detail="Cannot cancel an invite that has already been accepted")
    
    # Check if invite is already cancelled
    if invite['status'] == 'cancelled':
        raise HTTPException(status_code=400, detail="This invite has already been cancelled")
    
    # Update the invite status to cancelled
    await db.invites.update_one(
        {'id': invite_id},
        {
            '$set': {
                'status': 'cancelled',
                'cancelled_at': datetime.now(timezone.utc).isoformat(),
                'cancelled_by': current_user['id'],
                'cancelled_by_name': current_user['name']
            }
        }
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='invite_cancelled',
        target_user_id=invite_id,
        target_user_name=f"{invite.get('recruit_first_name', '')} {invite.get('recruit_last_name', '')}",
        details={
            'recruit_email': invite['recruit_email'],
            'recruit_npn': invite.get('recruit_npn'),
            'cancelled_by_admin': is_admin,
            'original_inviter': invite['inviter_name'],
            'was_pending': invite['status'] == 'pending'
        }
    )
    
    return {
        'success': True,
        'message': 'Invite cancelled successfully',
        'invite_id': invite_id,
        'recruit_email': invite['recruit_email'],
        'cancelled_at': datetime.now(timezone.utc).isoformat(),
        'cancelled_by': current_user['name']
    }

@api_router.get("/invites/validate/{token}")
async def validate_invite(token: str):
    invite = await db.invites.find_one({'token': token, 'status': 'pending'}, {'_id': 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or used invite token")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite token expired")
    
    return {
        'valid': True,
        'recruit_email': invite['recruit_email'],
        'recruit_first_name': invite.get('recruit_first_name', invite.get('recruit_name', '').split()[0] if invite.get('recruit_name') else ''),
        'recruit_last_name': invite.get('recruit_last_name', ' '.join(invite.get('recruit_name', '').split()[1:]) if invite.get('recruit_name') and len(invite.get('recruit_name', '').split()) > 1 else ''),
        'recruit_npn': invite.get('recruit_npn'),
        'inviter_name': invite['inviter_name']
    }

# ==================== ADMIN INVITES ====================

@api_router.post("/admin-invites", response_model=AdminInviteResponse)
async def create_admin_invite(data: AdminInviteCreate, current_user: dict = Depends(get_current_user)):
    """Create an admin invite link - Admin only"""
    await require_role(current_user, ['admin'])
    
    # Check if email already exists
    existing_user = await db.users.find_one({'email': data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    
    # Check for existing pending admin invite
    pending_invite = await db.admin_invites.find_one({'email': data.email, 'status': 'pending'})
    if pending_invite:
        raise HTTPException(status_code=400, detail="A pending invite already exists for this email")
    
    invite_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)
    
    invite_doc = {
        'id': invite_id,
        'token': token,
        'email': data.email,
        'first_name': data.first_name,
        'last_name': data.last_name,
        'inviter_id': current_user['id'],
        'inviter_name': current_user['name'],
        'message': data.message,
        'status': 'pending',
        'created_at': now.isoformat(),
        'expires_at': expires_at.isoformat()
    }
    
    await db.admin_invites.insert_one(invite_doc)
    return AdminInviteResponse(**invite_doc)

@api_router.get("/admin-invites", response_model=List[AdminInviteResponse])
async def get_admin_invites(current_user: dict = Depends(get_current_user)):
    """Get all admin invites - Admin only"""
    await require_role(current_user, ['admin'])
    invites = await db.admin_invites.find({}, {'_id': 0}).to_list(1000)
    return [AdminInviteResponse(**i) for i in invites]

@api_router.get("/admin-invites/validate/{token}")
async def validate_admin_invite(token: str):
    """Validate an admin invite token"""
    invite = await db.admin_invites.find_one({'token': token, 'status': 'pending'}, {'_id': 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or used admin invite token")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Admin invite token expired")
    
    return {
        'valid': True,
        'email': invite['email'],
        'first_name': invite['first_name'],
        'last_name': invite['last_name'],
        'inviter_name': invite['inviter_name']
    }

@api_router.post("/auth/register-admin")
async def register_admin(data: dict):
    """Register a new admin from invite token"""
    token = data.get('invite_token')
    password = data.get('password')
    phone = data.get('phone')
    
    if not token or not password:
        raise HTTPException(status_code=400, detail="Token and password are required")
    
    # Validate invite
    invite = await db.admin_invites.find_one({'token': token, 'status': 'pending'})
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or used admin invite token")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Admin invite token expired")
    
    # Check email not taken
    existing = await db.users.find_one({'email': invite['email']})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create admin user
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    now = datetime.now(timezone.utc)
    
    user_doc = {
        'id': user_id,
        'email': invite['email'],
        'password_hash': password_hash,
        'name': f"{invite['first_name']} {invite['last_name']}",
        'first_name': invite['first_name'],
        'last_name': invite['last_name'],
        'phone': phone,
        'role': 'admin',
        'comp_percentage': 135,  # Same as main admin
        'status': 'active',
        'upline_id': None,
        'created_at': now.isoformat(),
        'date_joined': now.strftime('%Y-%m-%d'),
        'licensed_states': []
    }
    
    await db.users.insert_one(user_doc)
    
    # Update invite status
    await db.admin_invites.update_one(
        {'token': token},
        {'$set': {'status': 'accepted', 'accepted_at': now.isoformat()}}
    )
    
    # Generate token
    jwt_token = jwt.encode({
        'user_id': user_id,
        'email': invite['email'],
        'role': 'admin',
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }, JWT_SECRET, algorithm='HS256')
    
    return {
        'token': jwt_token,
        'user': {
            'id': user_id,
            'email': invite['email'],
            'name': user_doc['name'],
            'role': 'admin',
            'comp_percentage': 135
        }
    }

# ==================== ADMIN MANAGEMENT ====================

async def create_audit_log(admin_id: str, admin_name: str, action: str, target_user_id: str, target_user_name: str, details: dict):
    """Create an audit log entry"""
    log_doc = {
        'id': str(uuid.uuid4()),
        'admin_id': admin_id,
        'admin_name': admin_name,
        'action': action,
        'target_user_id': target_user_id,
        'target_user_name': target_user_name,
        'details': details,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.audit_logs.insert_one(log_doc)
    return log_doc

@api_router.put("/admin/users/{user_id}/upline")
async def reassign_agent_upline(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Reassign an agent to a different upline - Admin only"""
    await require_role(current_user, ['admin'])
    
    new_upline_id = data.get('new_upline_id')
    
    # Get target user
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_upline_id = target_user.get('upline_id')
    old_upline_name = None
    new_upline_name = None
    
    # Get old upline name
    if old_upline_id:
        old_upline = await db.users.find_one({'id': old_upline_id}, {'_id': 0, 'name': 1})
        old_upline_name = old_upline['name'] if old_upline else None
    
    # Validate new upline if provided
    if new_upline_id:
        new_upline = await db.users.find_one({'id': new_upline_id}, {'_id': 0})
        if not new_upline:
            raise HTTPException(status_code=404, detail="New upline not found")
        new_upline_name = new_upline['name']
        
        # Prevent circular hierarchy
        if new_upline_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot assign user as their own upline")
        
        # Check if new upline is in the user's downline (would create circular reference)
        async def is_in_downline(check_id: str, parent_id: str) -> bool:
            downline = await db.users.find({'upline_id': parent_id}, {'_id': 0, 'id': 1}).to_list(1000)
            for agent in downline:
                if agent['id'] == check_id:
                    return True
                if await is_in_downline(check_id, agent['id']):
                    return True
            return False
        
        if await is_in_downline(new_upline_id, user_id):
            raise HTTPException(status_code=400, detail="Cannot create circular hierarchy")
    
    # Update user's upline
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'upline_id': new_upline_id}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='hierarchy_change',
        target_user_id=user_id,
        target_user_name=target_user['name'],
        details={
            'old_upline_id': old_upline_id,
            'old_upline_name': old_upline_name,
            'new_upline_id': new_upline_id,
            'new_upline_name': new_upline_name
        }
    )
    
    return {'success': True, 'message': f"Upline updated to {new_upline_name or 'None'}"}

@api_router.put("/admin/users/{user_id}/status")
async def toggle_agent_status(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Enable or disable an agent's account - Admin or upline only"""
    new_status = data.get('status')  # 'active' or 'disabled'
    if new_status not in ['active', 'disabled']:
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'disabled'")
    
    # Prevent disabling yourself
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permission: Admin can do anything, non-admin can only manage their downline
    is_admin = current_user.get('role') == 'admin'
    
    if not is_admin:
        # Check if target user is in current user's downline
        async def get_all_downline_ids(upline_id):
            """Recursively get all downline user IDs"""
            downline_ids = []
            direct_downline = await db.users.find({'upline_id': upline_id}, {'id': 1, '_id': 0}).to_list(None)
            for agent in direct_downline:
                downline_ids.append(agent['id'])
                downline_ids.extend(await get_all_downline_ids(agent['id']))
            return downline_ids
        
        downline_ids = await get_all_downline_ids(current_user['id'])
        if user_id not in downline_ids:
            raise HTTPException(status_code=403, detail="You can only manage accounts in your downline")
    
    old_status = target_user.get('status', 'active')
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'status': new_status}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='status_change',
        target_user_id=user_id,
        target_user_name=target_user['name'],
        details={
            'old_status': old_status,
            'new_status': new_status,
            'changed_by_role': current_user.get('role', 'agent')
        }
    )
    
    return {'success': True, 'message': f"Account {new_status}"}

@api_router.put("/admin/users/{user_id}/commission")
async def update_agent_commission(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update an agent's commission level - Admin only"""
    await require_role(current_user, ['admin'])
    
    new_commission = data.get('comp_percentage')
    if not isinstance(new_commission, (int, float)) or new_commission < 0 or new_commission > 200:
        raise HTTPException(status_code=400, detail="Commission must be between 0 and 200")
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent commission changes for admin users - admins are permanently at 135%
    if target_user.get('role') == 'admin':
        raise HTTPException(status_code=400, detail="Cannot change commission for admin users. Admins are permanently set at 135%.")
    
    old_commission = target_user.get('comp_percentage', 0)
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'comp_percentage': new_commission}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='commission_change',
        target_user_id=user_id,
        target_user_name=target_user['name'],
        details={
            'old_commission': old_commission,
            'new_commission': new_commission
        }
    )
    
    return {'success': True, 'message': f"Commission updated to {new_commission}%"}

@api_router.put("/admin/users/{user_id}/role")
async def update_agent_role(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update an agent's role - Admin only"""
    await require_role(current_user, ['admin'])
    
    new_role = data.get('role')
    if new_role not in ['agent', 'leader', 'admin']:
        raise HTTPException(status_code=400, detail="Role must be 'agent', 'leader', or 'admin'")
    
    # Prevent changing own role
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = target_user.get('role', 'agent')
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'role': new_role}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='role_change',
        target_user_id=user_id,
        target_user_name=target_user['name'],
        details={
            'old_role': old_role,
            'new_role': new_role
        }
    )
    
    return {'success': True, 'message': f"Role updated to {new_role}"}

@api_router.put("/admin/users/{user_id}/name")
async def update_user_name(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update a user's name - Admin only"""
    await require_role(current_user, ['admin'])
    
    new_name = data.get('name')
    if not new_name or len(new_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_name = target_user.get('name', '')
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'name': new_name.strip()}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='name_change',
        target_user_id=user_id,
        target_user_name=new_name,
        details={
            'old_name': old_name,
            'new_name': new_name
        }
    )
    
    return {'success': True, 'message': f"Name updated to {new_name}"}

@api_router.put("/admin/users/{user_id}/details")
async def update_agent_details(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update agent's name, email, and NPN - Admin only"""
    await require_role(current_user, ['admin'])
    
    # Prevent editing yourself
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot edit your own details through this endpoint")
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updates = {}
    changes = {}
    
    # Validate and prepare name update
    if 'name' in data:
        new_name = data['name'].strip()
        if len(new_name) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        if new_name != target_user.get('name'):
            changes['name'] = {'old': target_user.get('name', ''), 'new': new_name}
            updates['name'] = new_name
    
    # Validate and prepare email update
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not new_email or '@' not in new_email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Check if email is already in use by another user
        if new_email != target_user.get('email'):
            existing_email = await db.users.find_one({'email': new_email, 'id': {'$ne': user_id}})
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already in use by another user")
            
            # Check if email exists in pending invites
            pending_invite = await db.invites.find_one({'recruit_email': new_email, 'status': 'pending'})
            if pending_invite:
                raise HTTPException(status_code=400, detail="Email has a pending invite")
            
            changes['email'] = {'old': target_user.get('email', ''), 'new': new_email}
            updates['email'] = new_email
    
    # Validate and prepare NPN update
    if 'npn' in data:
        new_npn = data['npn'].strip()
        if new_npn and len(new_npn) < 4:
            raise HTTPException(status_code=400, detail="NPN must be at least 4 characters")
        
        # Check if NPN is already in use by another user
        if new_npn and new_npn != target_user.get('npn'):
            existing_npn = await db.users.find_one({'npn': new_npn, 'id': {'$ne': user_id}})
            if existing_npn:
                raise HTTPException(status_code=400, detail="NPN already in use by another user")
            
            # Check if NPN exists in pending invites
            pending_npn_invite = await db.invites.find_one({'recruit_npn': new_npn, 'status': 'pending'})
            if pending_npn_invite:
                raise HTTPException(status_code=400, detail="NPN has a pending invite")
            
            changes['npn'] = {'old': target_user.get('npn', ''), 'new': new_npn}
            updates['npn'] = new_npn
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid changes provided")
    
    # Perform the update
    await db.users.update_one(
        {'id': user_id},
        {'$set': updates}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='agent_details_update',
        target_user_id=user_id,
        target_user_name=target_user.get('name', 'Unknown'),
        details=changes
    )
    
    return {
        'success': True, 
        'message': 'Agent details updated successfully',
        'updated_fields': list(updates.keys())
    }

# Static files directory for email attachments
STATIC_FILES_DIR = ROOT_DIR / 'static_files'
STATIC_FILES_DIR.mkdir(exist_ok=True)

@api_router.post("/admin/upload-advizor-guide")
async def upload_advizor_guide(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload the Breeze Advizor Guide PDF.
    This PDF will be attached to welcome emails sent to new recruits.
    Admin only.
    """
    await require_role(current_user, ['admin'])
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # Save the file
    guide_path = STATIC_FILES_DIR / 'Breeze_Advizor_Guide.pdf'
    async with aiofiles.open(guide_path, 'wb') as f:
        await f.write(content)
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='advizor_guide_uploaded',
        target_user_id='system',
        target_user_name='System',
        details={
            'original_filename': file.filename,
            'file_size_bytes': len(content),
            'uploaded_at': datetime.now(timezone.utc).isoformat()
        }
    )
    
    logger.info(f"Breeze Advizor Guide uploaded by {current_user['name']}")
    
    return {
        'success': True,
        'message': 'Breeze Advizor Guide uploaded successfully',
        'filename': 'Breeze_Advizor_Guide.pdf',
        'size_bytes': len(content)
    }

@api_router.get("/admin/advizor-guide-status")
async def get_advizor_guide_status(current_user: dict = Depends(get_current_user)):
    """Check if the Breeze Advizor Guide PDF is uploaded. Admin only."""
    await require_role(current_user, ['admin'])
    
    guide_path = STATIC_FILES_DIR / 'Breeze_Advizor_Guide.pdf'
    
    if guide_path.exists():
        file_stat = guide_path.stat()
        return {
            'uploaded': True,
            'filename': 'Breeze_Advizor_Guide.pdf',
            'size_bytes': file_stat.st_size,
            'last_modified': datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat()
        }
    
    return {
        'uploaded': False,
        'message': 'Breeze Advizor Guide PDF not yet uploaded'
    }

@api_router.delete("/admin/advizor-guide")
async def delete_advizor_guide(current_user: dict = Depends(get_current_user)):
    """Delete the Breeze Advizor Guide PDF. Admin only."""
    await require_role(current_user, ['admin'])
    
    guide_path = STATIC_FILES_DIR / 'Breeze_Advizor_Guide.pdf'
    
    if not guide_path.exists():
        raise HTTPException(status_code=404, detail="Breeze Advizor Guide not found")
    
    guide_path.unlink()
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='advizor_guide_deleted',
        target_user_id='system',
        target_user_name='System',
        details={
            'deleted_at': datetime.now(timezone.utc).isoformat()
        }
    )
    
    logger.info(f"Breeze Advizor Guide deleted by {current_user['name']}")
    
    return {
        'success': True,
        'message': 'Breeze Advizor Guide deleted successfully'
    }

@api_router.delete("/admin/users/{user_id}")
async def delete_user_completely(user_id: str, current_user: dict = Depends(get_current_user)):
    """Completely delete a user and all their data - Admin only"""
    await require_role(current_user, ['admin'])
    
    # Prevent deleting yourself
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Find the user to delete
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_name = target_user.get('name', 'Unknown')
    user_email = target_user.get('email', '')
    
    # Reassign any downline agents to the current admin
    downline_result = await db.users.update_many(
        {'upline_id': user_id},
        {'$set': {'upline_id': current_user['id']}}
    )
    reassigned_count = downline_result.modified_count
    
    # Delete user from users collection
    await db.users.delete_one({'id': user_id})
    
    # Clean up all related data across all collections
    collections_to_clean = [
        ('clients', ['agent_id', 'added_by_agent_id']),
        ('audit_logs', ['admin_id', 'target_user_id']),
        ('invites', ['inviter_id']),
        ('kpi_entries', ['user_id']),
        ('quiz_attempts', ['user_id']),
        ('user_quiz_progress', ['user_id']),
        ('ceo_reports', ['user_id']),
        ('production', ['agent_id']),
        ('agent_carrier_settings', ['agent_id']),
    ]
    
    deleted_refs = {}
    for coll_name, fields in collections_to_clean:
        try:
            coll = db[coll_name]
            query = {'$or': [{field: user_id} for field in fields]}
            result = await coll.delete_many(query)
            if result.deleted_count > 0:
                deleted_refs[coll_name] = result.deleted_count
        except Exception as e:
            pass  # Collection might not exist
    
    # Also search for any text references to the user's name or email
    all_collections = await db.list_collection_names()
    for coll_name in all_collections:
        if coll_name == 'users':
            continue
        try:
            coll = db[coll_name]
            # Delete documents that reference this user by ID in any field
            async for doc in coll.find({}):
                doc_str = str(doc).lower()
                if user_id.lower() in doc_str or user_email.lower() in doc_str:
                    await coll.delete_one({'_id': doc['_id']})
        except Exception as e:
            pass
    
    # Create audit log for the deletion
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='user_deleted',
        target_user_id=user_id,
        target_user_name=user_name,
        details={
            'deleted_user_email': user_email,
            'reassigned_downline_count': reassigned_count,
            'deleted_references': deleted_refs
        }
    )
    
    return {
        'success': True, 
        'message': f"User {user_name} has been completely deleted",
        'reassigned_downline': reassigned_count,
        'deleted_references': deleted_refs
    }

@api_router.get("/admin/audit-logs")
async def get_audit_logs(
    action: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs - Admin only"""
    await require_role(current_user, ['admin'])
    
    query = {}
    if action:
        query['action'] = action
    
    logs = await db.audit_logs.find(query, {'_id': 0}).sort('created_at', -1).to_list(limit)
    return logs

@api_router.get("/admin/org-tree")
async def get_full_org_tree(current_user: dict = Depends(get_current_user)):
    """Get the full organization tree - Admin only"""
    await require_role(current_user, ['admin'])
    
    # Get all users
    all_users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(10000)
    
    # Build a map of users
    users_map = {u['id']: u for u in all_users}
    
    # Find root users (no upline or upline not in system)
    root_users = [u for u in all_users if not u.get('upline_id') or u.get('upline_id') not in users_map]
    
    def build_node(user):
        children = [u for u in all_users if u.get('upline_id') == user['id']]
        return {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user.get('role', 'agent'),
            'status': user.get('status', 'active'),
            'comp_percentage': user.get('comp_percentage', 0),
            'date_joined': user.get('date_joined'),
            'children': [build_node(c) for c in children]
        }
    
    trees = [build_node(u) for u in root_users]
    
    return {
        'trees': trees,
        'total_users': len(all_users),
        'total_active': len([u for u in all_users if u.get('status') == 'active']),
        'total_disabled': len([u for u in all_users if u.get('status') == 'disabled'])
    }

@api_router.get("/admin/users")
async def get_all_users_admin(current_user: dict = Depends(get_current_user)):
    """Get all users for admin management - Admin only"""
    await require_role(current_user, ['admin'])
    
    users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(10000)
    return users

@api_router.get("/admin/hierarchy-export")
async def export_hierarchy_snapshot(current_user: dict = Depends(get_current_user)):
    """Export hierarchy snapshot as JSON - Admin only"""
    await require_role(current_user, ['admin'])
    
    all_users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(10000)
    
    snapshot = {
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'exported_by': current_user['name'],
        'total_users': len(all_users),
        'users': []
    }
    
    for user in all_users:
        upline_name = None
        if user.get('upline_id'):
            upline = await db.users.find_one({'id': user['upline_id']}, {'_id': 0, 'name': 1})
            upline_name = upline['name'] if upline else None
        
        snapshot['users'].append({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user.get('role', 'agent'),
            'status': user.get('status', 'active'),
            'comp_percentage': user.get('comp_percentage', 0),
            'upline_id': user.get('upline_id'),
            'upline_name': upline_name,
            'date_joined': user.get('date_joined'),
            'npn': user.get('npn')
        })
    
    return snapshot


# Resources Endpoints
@api_router.post("/resources", response_model=ResourceResponse)
async def create_resource(data: ResourceCreate, current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    
    resource_id = str(uuid.uuid4())
    resource_doc = {
        'id': resource_id,
        'title': data.title,
        'category': data.category,
        'type': data.type,
        'url': data.url,
        'description': data.description,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': current_user['id']
    }
    
    await db.resources.insert_one(resource_doc)
    return ResourceResponse(**resource_doc)

@api_router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(category: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {'category': category} if category else {}
    resources = await db.resources.find(query, {'_id': 0}).to_list(1000)
    return [ResourceResponse(**r) for r in resources]

@api_router.delete("/resources/{resource_id}")
async def delete_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    result = await db.resources.delete_one({'id': resource_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}

# Carrier Endpoints
@api_router.post("/carriers", response_model=CarrierResponse)
async def create_carrier(data: CarrierCreate, current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    
    carrier_id = str(uuid.uuid4())
    carrier_doc = {
        'id': carrier_id,
        'name': data.name,
        'description': data.description,
        'guideline_url': data.guideline_url,
        'notes': data.notes,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.carriers.insert_one(carrier_doc)
    return CarrierResponse(**carrier_doc)

@api_router.get("/carriers")
async def get_carriers(current_user: dict = Depends(get_current_user)):
    carriers = await db.carriers.find({}, {'_id': 0}).to_list(1000)
    return carriers

@api_router.delete("/carriers/{carrier_id}")
async def delete_carrier(carrier_id: str, current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    result = await db.carriers.delete_one({'id': carrier_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return {"message": "Carrier deleted successfully"}

# Agent Carrier Settings Endpoints
@api_router.get("/carriers/my-settings")
async def get_my_carrier_settings(current_user: dict = Depends(get_current_user)):
    """Get current user's carrier settings (writing numbers and appointment status)"""
    settings = await db.agent_carrier_settings.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    
    # Convert to dict keyed by carrier_id for easy lookup
    return {s['carrier_id']: {'writing_number': s.get('writing_number'), 'is_appointed': s.get('is_appointed', False)} for s in settings}

@api_router.put("/carriers/my-settings")
async def update_my_carrier_setting(
    data: AgentCarrierSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's carrier setting"""
    await db.agent_carrier_settings.update_one(
        {'user_id': current_user['id'], 'carrier_id': data.carrier_id},
        {'$set': {
            'user_id': current_user['id'],
            'carrier_id': data.carrier_id,
            'writing_number': data.writing_number,
            'is_appointed': data.is_appointed,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": "Setting updated successfully"}

# Get single carrier by ID
@api_router.get("/carriers/{carrier_id}")
async def get_carrier(carrier_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single carrier by ID"""
    carrier = await db.carriers.find_one({'id': carrier_id}, {'_id': 0})
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier

# Production Endpoints
@api_router.post("/production/webhook")
async def production_webhook(data: dict):
    agent = await db.users.find_one({'id': data.get('agent_id')}, {'_id': 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    production_id = str(uuid.uuid4())
    production_doc = {
        'id': production_id,
        'agent_id': data['agent_id'],
        'agent_name': agent['name'],
        'carrier': data['carrier'],
        'policy_number': data['policy_number'],
        'submitted_ap': float(data.get('submitted_ap', 0)),
        'issued_paid_ap': float(data.get('issued_paid_ap', 0)),
        'status': data['status'],
        'submission_date': data['submission_date'],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.production.insert_one(production_doc)
    return {"message": "Production record created", "id": production_id}

@api_router.get("/production", response_model=List[ProductionResponse])
async def get_production(current_user: dict = Depends(get_current_user)):
    if current_user['role'] == 'admin':
        production = await db.production.find({}, {'_id': 0}).to_list(1000)
    elif current_user['role'] == 'leader':
        async def get_team_ids(user_id: str) -> List[str]:
            downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
            team_ids = [user_id]
            for agent in downline:
                sub_ids = await get_team_ids(agent['id'])
                team_ids.extend(sub_ids)
            return team_ids
        
        team_ids = await get_team_ids(current_user['id'])
        production = await db.production.find({'agent_id': {'$in': team_ids}}, {'_id': 0}).to_list(1000)
    else:
        production = await db.production.find({'agent_id': current_user['id']}, {'_id': 0}).to_list(1000)
    
    return [ProductionResponse(**p) for p in production]

@api_router.get("/production/stats")
async def get_production_stats(current_user: dict = Depends(get_current_user)):
    if current_user['role'] == 'admin':
        pipeline = [{'$group': {
            '_id': None,
            'total_submitted': {'$sum': '$submitted_ap'},
            'total_issued': {'$sum': '$issued_paid_ap'},
            'count': {'$sum': 1}
        }}]
    elif current_user['role'] == 'leader':
        async def get_team_ids(user_id: str) -> List[str]:
            downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
            team_ids = [user_id]
            for agent in downline:
                sub_ids = await get_team_ids(agent['id'])
                team_ids.extend(sub_ids)
            return team_ids
        
        team_ids = await get_team_ids(current_user['id'])
        pipeline = [
            {'$match': {'agent_id': {'$in': team_ids}}},
            {'$group': {
                '_id': None,
                'total_submitted': {'$sum': '$submitted_ap'},
                'total_issued': {'$sum': '$issued_paid_ap'},
                'count': {'$sum': 1}
            }}
        ]
    else:
        pipeline = [
            {'$match': {'agent_id': current_user['id']}},
            {'$group': {
                '_id': None,
                'total_submitted': {'$sum': '$submitted_ap'},
                'total_issued': {'$sum': '$issued_paid_ap'},
                'count': {'$sum': 1}
            }}
        ]
    
    result = await db.production.aggregate(pipeline).to_list(1)
    if result:
        return {
            'total_submitted_ap': result[0]['total_submitted'],
            'total_issued_ap': result[0]['total_issued'],
            'total_policies': result[0]['count']
        }
    return {
        'total_submitted_ap': 0,
        'total_issued_ap': 0,
        'total_policies': 0
    }

@api_router.get("/leaderboard/top-producers")
async def get_top_producers_leaderboard(current_user: dict = Depends(get_current_user)):
    """Get top 10 agents by submitted AP with upline info"""
    try:
        # Aggregate production by agent
        pipeline = [
            {
                '$group': {
                    '_id': '$agent_id',
                    'submitted_ap': {'$sum': '$submitted_ap'},
                    'policy_count': {'$sum': 1}
                }
            },
            {'$sort': {'submitted_ap': -1}},
            {'$limit': 10}
        ]
        
        top_agents = await db.production.aggregate(pipeline).to_list(10)
        
        # Enrich with agent names and upline info
        leaderboard = []
        for agent_data in top_agents:
            agent = await db.users.find_one({'id': agent_data['_id']}, {'_id': 0, 'name': 1, 'upline_id': 1})
            if agent:
                upline_name = 'N/A'
                if agent.get('upline_id'):
                    upline = await db.users.find_one({'id': agent['upline_id']}, {'_id': 0, 'name': 1})
                    if upline:
                        upline_name = upline.get('name', 'N/A')
                
                leaderboard.append({
                    'agent_id': agent_data['_id'],
                    'agent_name': agent.get('name', 'Unknown'),
                    'submitted_ap': agent_data['submitted_ap'],
                    'policy_count': agent_data['policy_count'],
                    'upline_name': upline_name
                })
        
        return leaderboard
    except Exception as e:
        logger.error(f"Failed to fetch leaderboard: {e}")
        return []

# KPI Tracking Endpoints
@api_router.post("/kpi", response_model=KPIEntryResponse)
async def create_or_update_kpi(data: KPIEntryCreate, current_user: dict = Depends(get_current_user)):
    # Check if entry exists for this date
    existing = await db.kpi_entries.find_one({
        'user_id': current_user['id'],
        'date': data.date
    }, {'_id': 0})
    
    if existing:
        # Update existing
        await db.kpi_entries.update_one(
            {'user_id': current_user['id'], 'date': data.date},
            {'$set': {
                'dials_made': data.dials_made,
                'contacts_made': data.contacts_made,
                'appointments_set': data.appointments_set,
                'presentations_given': data.presentations_given,
                'sales_made': data.sales_made,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        existing.update(data.dict())
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        return KPIEntryResponse(**existing)
    else:
        # Create new
        kpi_entry = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'date': data.date,
            'dials_made': data.dials_made,
            'contacts_made': data.contacts_made,
            'appointments_set': data.appointments_set,
            'presentations_given': data.presentations_given,
            'sales_made': data.sales_made,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        await db.kpi_entries.insert_one(kpi_entry)
        return KPIEntryResponse(**kpi_entry)

@api_router.get("/kpi", response_model=List[KPIEntryResponse])
async def get_kpi_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Admins can view any user's KPIs
    if current_user['role'] == 'admin' and user_id:
        query = {'user_id': user_id}
    else:
        query = {'user_id': current_user['id']}
    
    if start_date:
        query['date'] = {'$gte': start_date}
    if end_date:
        if 'date' in query:
            query['date']['$lte'] = end_date
        else:
            query['date'] = {'$lte': end_date}
    
    entries = await db.kpi_entries.find(query, {'_id': 0}).sort('date', -1).to_list(1000)
    return [KPIEntryResponse(**entry) for entry in entries]

@api_router.get("/kpi/weekly-report", response_model=WeeklyCEOReportResponse)
async def generate_weekly_ceo_report(current_user: dict = Depends(get_current_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    # Calculate week range (last 7 days)
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=7)
    week_end = today
    
    # Get current week's KPIs
    current_week_kpis = await db.kpi_entries.find({
        'user_id': current_user['id'],
        'date': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    # Get previous week's KPIs
    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)
    prev_week_kpis = await db.kpi_entries.find({
        'user_id': current_user['id'],
        'date': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}
    }, {'_id': 0}).to_list(1000)
    
    # Get production data (submitted AP) for current week
    current_week_clients = await db.clients.find({
        'agent_id': current_user['id'],
        '$or': [
            {'date_submitted': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}},
            {'date_issued': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}}
        ]
    }, {'_id': 0}).to_list(1000)
    
    # Get production data for previous week
    prev_week_clients = await db.clients.find({
        'agent_id': current_user['id'],
        '$or': [
            {'date_submitted': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}},
            {'date_issued': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}}
        ]
    }, {'_id': 0}).to_list(1000)
    
    # Calculate production summaries
    current_submitted_ap = sum(
        (c.get('premium', 0) or c.get('annual_premium', 0) or 0)
        for c in current_week_clients
        if c.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']
    )
    prev_submitted_ap = sum(
        (c.get('premium', 0) or c.get('annual_premium', 0) or 0)
        for c in prev_week_clients
        if c.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']
    )
    
    # Calculate product type breakdown for current week
    product_breakdown_current = {}
    for client in current_week_clients:
        if client.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
            product_type = client.get('product_type', 'Unknown')
            premium = client.get('premium', 0) or client.get('annual_premium', 0) or 0
            if product_type not in product_breakdown_current:
                product_breakdown_current[product_type] = {'count': 0, 'ap': 0}
            product_breakdown_current[product_type]['count'] += 1
            product_breakdown_current[product_type]['ap'] += premium
    
    # Calculate product type breakdown for previous week
    product_breakdown_prev = {}
    for client in prev_week_clients:
        if client.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
            product_type = client.get('product_type', 'Unknown')
            premium = client.get('premium', 0) or client.get('annual_premium', 0) or 0
            if product_type not in product_breakdown_prev:
                product_breakdown_prev[product_type] = {'count': 0, 'ap': 0}
            product_breakdown_prev[product_type]['count'] += 1
            product_breakdown_prev[product_type]['ap'] += premium
    
    # Get team production data if user has a team
    team_data = {}
    if current_user['role'] in ['admin', 'manager']:
        # Helper function to get all downline recursively
        async def get_all_downline_ids(user_id: str) -> List[str]:
            downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
            all_ids = [agent['id'] for agent in downline]
            for agent in downline:
                sub_ids = await get_all_downline_ids(agent['id'])
                all_ids.extend(sub_ids)
            return all_ids
        
        # Get all downline agents
        downline_ids = await get_all_downline_ids(current_user['id'])
        
        # Get all agents for counting
        all_agents = await db.users.find({'id': {'$in': downline_ids}}, {'_id': 0}).to_list(10000)
        
        # Get team's clients for current week
        team_clients_current = await db.clients.find({
            'agent_id': {'$in': downline_ids},
            '$or': [
                {'date_submitted': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}},
                {'date_issued': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}}
            ]
        }, {'_id': 0}).to_list(10000)
        
        # Get team's clients for previous week
        team_clients_prev = await db.clients.find({
            'agent_id': {'$in': downline_ids},
            '$or': [
                {'date_submitted': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}},
                {'date_issued': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}}
            ]
        }, {'_id': 0}).to_list(10000)
        
        current_team_production = sum(
            (c.get('premium', 0) or c.get('annual_premium', 0) or 0)
            for c in team_clients_current
            if c.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']
        )
        prev_team_production = sum(
            (c.get('premium', 0) or c.get('annual_premium', 0) or 0)
            for c in team_clients_prev
            if c.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']
        )
        
        # Count writing agents (agents who submitted this week)
        writing_agents_current = len(set(c['agent_id'] for c in team_clients_current))
        total_active_agents = len([a for a in all_agents if a['id'] in downline_ids and a.get('role') != 'admin'])
        writing_agent_percentage = (writing_agents_current / total_active_agents * 100) if total_active_agents > 0 else 0
        
        # Get direct legs
        direct_legs = await db.users.find({'upline_id': current_user['id']}, {'_id': 0}).to_list(1000)
        direct_legs_count = len(direct_legs)
        direct_legs_writing = len(set(c['agent_id'] for c in team_clients_current if c['agent_id'] in [leg['id'] for leg in direct_legs]))
        direct_legs_percentage = (direct_legs_writing / direct_legs_count * 100) if direct_legs_count > 0 else 0
        
        # Get new recruits this week
        new_recruits_current = await db.users.find({
            'upline_id': current_user['id'],
            'created_at': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        new_recruits_prev = await db.users.find({
            'upline_id': current_user['id'],
            'created_at': {'$gte': prev_week_start.isoformat(), '$lte': prev_week_end.isoformat()}
        }, {'_id': 0}).to_list(1000)
        
        team_data = {
            'current_team_production': current_team_production,
            'prev_team_production': prev_team_production,
            'writing_agents': writing_agents_current,
            'total_active_agents': total_active_agents,
            'writing_agent_percentage': round(writing_agent_percentage, 1),
            'direct_legs_count': direct_legs_count,
            'direct_legs_writing': direct_legs_writing,
            'direct_legs_percentage': round(direct_legs_percentage, 1),
            'new_recruits_current': len(new_recruits_current),
            'new_recruits_prev': len(new_recruits_prev)
        }
    
    # Calculate KPI summaries
    current_summary = {
        'dials_made': sum(k.get('dials_made', 0) for k in current_week_kpis),
        'contacts_made': sum(k.get('contacts_made', 0) for k in current_week_kpis),
        'appointments_set': sum(k.get('appointments_set', 0) for k in current_week_kpis),
        'presentations_given': sum(k.get('presentations_given', 0) for k in current_week_kpis),
        'sales_made': sum(k.get('sales_made', 0) for k in current_week_kpis),
        'submitted_ap': current_submitted_ap
    }
    
    prev_summary = {
        'dials_made': sum(k.get('dials_made', 0) for k in prev_week_kpis),
        'contacts_made': sum(k.get('contacts_made', 0) for k in prev_week_kpis),
        'appointments_set': sum(k.get('appointments_set', 0) for k in prev_week_kpis),
        'presentations_given': sum(k.get('presentations_given', 0) for k in prev_week_kpis),
        'sales_made': sum(k.get('sales_made', 0) for k in prev_week_kpis),
        'submitted_ap': prev_submitted_ap
    }
    
    # Get past 3 CEO reports for trend memory
    past_reports = await db.ceo_reports.find({
        'user_id': current_user['id']
    }, {'_id': 0}).sort('created_at', -1).limit(3).to_list(3)
    
    # Identify improvements and declines
    improvements = []
    declines = []
    
    for key in current_summary:
        if current_summary[key] > prev_summary[key]:
            label = key.replace('_', ' ').title()
            if key == 'submitted_ap':
                improvements.append(f"{label}: ${current_summary[key]:,.0f} (up from ${prev_summary[key]:,.0f})")
            else:
                improvements.append(f"{label}: {current_summary[key]} (up from {prev_summary[key]})")
        elif current_summary[key] < prev_summary[key]:
            label = key.replace('_', ' ').title()
            if key == 'submitted_ap':
                declines.append(f"{label}: ${current_summary[key]:,.0f} (down from ${prev_summary[key]:,.0f})")
            else:
                declines.append(f"{label}: {current_summary[key]} (down from {prev_summary[key]})")
    
    # Prepare trend memory context
    trend_context = ""
    if past_reports:
        trend_context = "\n\nPAST REPORT INSIGHTS (for pattern detection and trend memory):\n"
        for i, report in enumerate(past_reports, 1):
            trend_context += f"\nReport {i} ({report.get('week_start')} to {report.get('week_end')}):\n"
            trend_context += f"- Focus areas suggested: {', '.join(report.get('focus_areas', []))}\n"
            if report.get('patterns'):
                trend_context += f"- Patterns identified: {', '.join(report.get('patterns', []))}\n"
    
    # Generate comprehensive AI insights using Claude
    llm_key = os.environ.get('EMERGENT_LLM_KEY')
    chat = LlmChat(
        api_key=llm_key,
        session_id=f"ceo-report-{current_user['id']}-{today.isoformat()}",
        system_message="""You are an executive advisor and performance analyst for life insurance agents and agency leaders. Your role is to provide data-driven, actionable insights that are:

1. SPECIFIC & GROUNDED IN NUMBERS: Reference actual metrics, percentages, and trends
2. CLEAR & DIGESTIBLE: Use plain language that both new and experienced agents can understand
3. STRATEGIC: Focus on high-leverage actions, not just activity
4. IDENTITY-ALIGNED: Reinforce the 'Be, Do, Have' principle - BE an advisor, DO advisor activities, HAVE advisor results

Your tone should be:
- Direct and analytical (CEO briefing style)
- Specific with data points (cite actual numbers)
- Pattern-focused (identify what's working and what's not)
- Action-oriented (tie insights to concrete next steps)

CRITICAL ANTI-HALLUCINATION RULES:
- ONLY reference data explicitly provided in the prompt
- NEVER assume or infer product types (Term, IUL, Annuity, etc.) unless explicitly stated in PRODUCT BREAKDOWN section
- If product data is missing or shows 0 sales, DO NOT make product-related observations
- When product data is unavailable, focus on activity metrics, conversion rates, and behavioral patterns instead
- If you don't have enough data to make a specific claim, acknowledge the gap or pivot to verifiable insights"""
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    
    # Build product breakdown section
    product_section = ""
    if product_breakdown_current:
        product_section = "\nPRODUCT BREAKDOWN (Current Week):\n"
        for product_type, data in sorted(product_breakdown_current.items(), key=lambda x: x[1]['ap'], reverse=True):
            product_section += f"- {product_type}: {data['count']} sales, ${data['ap']:,.0f} AP\n"
        
        if product_breakdown_prev:
            product_section += "\nPRODUCT BREAKDOWN (Previous Week):\n"
            for product_type, data in sorted(product_breakdown_prev.items(), key=lambda x: x[1]['ap'], reverse=True):
                product_section += f"- {product_type}: {data['count']} sales, ${data['ap']:,.0f} AP\n"
    
    # Build team data section
    team_section = ""
    if team_data:
        team_section = f"""
TEAM PRODUCTION & LEADERSHIP METRICS:
- Personal Production: ${current_summary['submitted_ap']:,.0f} (prev week: ${prev_summary['submitted_ap']:,.0f})
- Team Production: ${team_data['current_team_production']:,.0f} (prev week: ${team_data['prev_team_production']:,.0f})
- Writing Agents: {team_data['writing_agents']} of {team_data['total_active_agents']} ({team_data['writing_agent_percentage']}%)
- Direct Legs: {team_data['direct_legs_count']} total, {team_data['direct_legs_writing']} writing ({team_data['direct_legs_percentage']}%)
- New Recruits: {team_data['new_recruits_current']} this week (prev week: {team_data['new_recruits_prev']})
"""
    
    prompt = f"""Analyze this week's performance for a life insurance {'leader/manager' if team_data else 'advisor'}:

ACTIVITY TRACKER (Current Week: {week_start.isoformat()} to {week_end.isoformat()}):
- Dials Made: {current_summary['dials_made']} (prev: {prev_summary['dials_made']})
- Contacts Made: {current_summary['contacts_made']} (prev: {prev_summary['contacts_made']})
- Appointments Set: {current_summary['appointments_set']} (prev: {prev_summary['appointments_set']})
- Presentations Given: {current_summary['presentations_given']} (prev: {prev_summary['presentations_given']})
- Sales Made: {current_summary['sales_made']} (prev: {prev_summary['sales_made']})
- Personal Submitted AP: ${current_summary['submitted_ap']:,.0f} (prev: ${prev_summary['submitted_ap']:,.0f})
{product_section}{team_section}{trend_context}

CRITICAL REQUIREMENTS:

1. EXECUTIVE SUMMARY (3-4 sentences max):
   - Lead with THE most important insight from the data
   - Reference specific numbers (don't be vague)
   - Make it immediately actionable
   - Use clear, plain language a new agent would understand
   
   Example: "You submitted $12,500 AP this week, down 23% from last week's $16,200. The decline traces to presentations—you gave 4 this week vs 7 last week. Your dial-to-contact ratio held steady at 22%, but appointment show rate dropped from 80% to 60%."

2. WHAT WENT WELL (3-4 specific points):
   - Cite actual numbers and percentages
   - Connect activities to outcomes (e.g., "Your 45 dials led to 10 contacts...")
   - Highlight what should be repeated
   - If team metrics exist, acknowledge team wins

3. PATTERNS (3-4 data-driven insights):
   - Identify conversion rate breakdowns (dial→contact, contact→appt, appt→presentation, presentation→sale)
   - Spot activity clustering (what days/times work best)
   - Call out dependencies or bottlenecks
   - If this is a recurring pattern from past weeks, explicitly state: "This is the [X] week in a row where..."
   
   **PRODUCT-RELATED PATTERNS:**
   - ONLY mention product types (Term, IUL, Annuity, etc.) if they appear in the PRODUCT BREAKDOWN section above
   - If PRODUCT BREAKDOWN shows data, you may compare performance by product type
   - If PRODUCT BREAKDOWN is missing or empty, DO NOT make product-related observations
   - Instead focus on conversion metrics, timing patterns, or behavioral trends

4. FOCUS AREAS (2-3 high-leverage actions):
   - Must be specific and directly tied to the numbers
   - Should address the biggest constraint or opportunity
   - Balance short-term execution with strategic positioning
   - DO NOT recommend product mix changes unless PRODUCT BREAKDOWN data clearly supports it
   
5. SELF-REFLECTION QUESTIONS (exactly 3):
   Create questions that challenge thinking around:
   - Leverage & time allocation: Where is time being spent vs where it should be?
   - Strategic clarity: What assumptions might be wrong?
   - Decision quality: What hard conversations are being avoided?
   - Constraints: What's becoming a bottleneck?
   - Mindset & resourcefulness: What emotions are driving decisions?
   - Sales training & skill gaps: Where is capability lacking?
   
   Examples:
   - "What decision or action this week had the highest long-term leverage—and why?"
   - "Where did I spend time on something that shouldn't require me anymore?"
   - "What assumption am I operating under that might be outdated?"
   - "Where did I avoid a hard conversation that would raise the standard?"
   - "What system or person became a bottleneck this week?"
   - "If this week repeated for 12 months, where would I—and my business—end up?"

Format as JSON:
{{
  "executive_summary": "string (3-4 sentences with specific numbers)",
  "what_went_well": ["point with numbers", "point with numbers", "point with numbers"],
  "patterns": ["data-driven pattern 1", "pattern 2", "pattern 3"],
  "focus_areas": ["specific action 1", "action 2"],
  "self_reflection_questions": ["strategic question 1", "question 2", "question 3"]
}}"""
    
    try:
        import json
        import re
        response = await chat.send_message(UserMessage(text=prompt))
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            ai_insights = json.loads(json_match.group())
            executive_summary = ai_insights.get('executive_summary', '')
            what_went_well = ai_insights.get('what_went_well', [])
            patterns = ai_insights.get('patterns', [])
            focus_areas = ai_insights.get('focus_areas', [])
            self_reflection_questions = ai_insights.get('self_reflection_questions', [])[:3]  # Limit to 3
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        # Fallback with specific numbers
        dial_to_contact = (current_summary['contacts_made'] / current_summary['dials_made'] * 100) if current_summary['dials_made'] > 0 else 0
        executive_summary = f"This week you made {current_summary['dials_made']} dials, reaching {current_summary['contacts_made']} contacts ({dial_to_contact:.0f}% contact rate). You submitted ${current_summary['submitted_ap']:,.0f} AP across {current_summary['sales_made']} sales. Focus on converting your {current_summary['appointments_set']} appointments into more presentations to maintain momentum."
        what_went_well = [
            f"Maintained {current_summary['dials_made']} dials showing consistent activity discipline",
            f"Generated {current_summary['contacts_made']} quality contacts from outreach efforts"
        ]
        patterns = [
            f"Your dial-to-contact ratio of {dial_to_contact:.0f}% indicates {'strong' if dial_to_contact > 20 else 'developing'} targeting",
            "Appointment-to-presentation conversion is your current constraint area"
        ]
        focus_areas = [
            "Improve appointment show rate through better confirmation and value-building",
            "Focus on presentation quality over presentation quantity"
        ]
        self_reflection_questions = [
            "What decision or action this week had the highest long-term leverage—and why?",
            "Where did I spend time or energy on something that should not require me anymore?",
            "If this week repeated for the next 12 months, where would my business—and I—end up?"
        ]
    
    # Store this report for future trend analysis
    report_doc = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'kpi_summary': current_summary,
        'improvements': improvements,
        'declines': declines,
        'executive_summary': executive_summary,
        'what_went_well': what_went_well,
        'patterns': patterns,
        'focus_areas': focus_areas,
        'self_reflection_questions': self_reflection_questions,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.ceo_reports.insert_one(report_doc)
    
    return WeeklyCEOReportResponse(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        kpi_summary=current_summary,
        improvements=improvements,
        declines=declines,
        executive_summary=executive_summary,
        what_went_well=what_went_well,
        patterns=patterns,
        focus_areas=focus_areas,
        self_reflection_questions=self_reflection_questions
    )

# Book of Business (Clients) Endpoints
@api_router.post("/clients", response_model=ClientResponse)
async def create_client(data: ClientCreate, current_user: dict = Depends(get_current_user)):
    # Calculate annual premium for non-annuity products
    annual_premium = None
    if data.product_type in ['IUL', 'Term', 'FEX', 'Whole Life'] and data.monthly_premium:
        annual_premium = data.monthly_premium * 12
    
    # Get agent's full name for the tag - try multiple fields
    agent_name = (current_user.get('name') or '').strip()  # Primary: name field
    if not agent_name:
        # Fallback: first + last name
        first_name = (current_user.get('first_name') or '').strip()
        last_name = (current_user.get('last_name') or '').strip()
        agent_name = f"{first_name} {last_name}".strip()
    if not agent_name:
        # Last resort: use email
        agent_name = current_user.get('email', 'Unknown Agent')
    
    client = {
        'id': str(uuid.uuid4()),
        'agent_id': current_user['id'],
        'agent_name': agent_name,
        'added_by_agent_id': current_user['id'],
        'added_by_agent_name': agent_name,
        'first_name': data.first_name,
        'last_name': data.last_name,
        'birth_date': data.birth_date,
        'state': data.state,
        'carrier': data.carrier,
        'product': data.product,
        'product_type': data.product_type,
        'policy_number': data.policy_number,
        'monthly_premium': data.monthly_premium,
        'annual_premium': annual_premium,
        'premium': data.premium,
        'target_premium': data.target_premium,
        'coverage_amount': data.coverage_amount,
        'status': data.status,
        'date_submitted': data.date_submitted,
        'date_issued': data.date_issued,
        'lead_source': data.lead_source,
        'lead_source_other': data.lead_source_other,
        'client_why': data.client_why,
        'beneficiaries': [b.dict() for b in data.beneficiaries] if data.beneficiaries else [],
        'additional_notes': data.additional_notes,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.clients.insert_one(client)
    return ClientResponse(**client)

@api_router.get("/clients", response_model=List[ClientResponse])
async def get_clients(current_user: dict = Depends(get_current_user)):
    # Admins see ALL clients, agents see only their own
    if current_user['role'] == 'admin':
        query = {}  # Admin sees everything
    else:
        query = {'agent_id': current_user['id']}  # Agents see only their own
    
    clients = await db.clients.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
    
    # Backfill missing agent names for existing clients
    for client in clients:
        # If added_by_agent_name is missing, populate it from the agent who owns the client
        if not client.get('added_by_agent_name') and client.get('agent_id'):
            agent = await db.users.find_one({'id': client['agent_id']}, {'_id': 0})
            if agent:
                # Try multiple name fields with proper empty string checking
                agent_name = (agent.get('name') or '').strip()  # Primary
                if not agent_name:
                    # Fallback to first + last
                    first = (agent.get('first_name') or '').strip()
                    last = (agent.get('last_name') or '').strip()
                    agent_name = f"{first} {last}".strip()
                if not agent_name:
                    # Last resort: email
                    agent_name = agent.get('email', 'Unknown Agent')
                
                client['agent_name'] = agent_name
                client['added_by_agent_id'] = client['agent_id']
                client['added_by_agent_name'] = agent_name
                
                # Update the database record
                await db.clients.update_one(
                    {'id': client['id']},
                    {'$set': {
                        'agent_name': agent_name,
                        'added_by_agent_id': client['agent_id'],
                        'added_by_agent_name': agent_name
                    }}
                )
        # Also backfill if the name is an email (legacy data)
        elif client.get('added_by_agent_name') and '@' in client.get('added_by_agent_name', ''):
            agent = await db.users.find_one({'id': client['agent_id']}, {'_id': 0})
            if agent:
                agent_name = (agent.get('name') or '').strip()
                if not agent_name:
                    first = (agent.get('first_name') or '').strip()
                    last = (agent.get('last_name') or '').strip()
                    agent_name = f"{first} {last}".strip()
                if agent_name and '@' not in agent_name:  # Only update if we have a real name
                    client['agent_name'] = agent_name
                    client['added_by_agent_name'] = agent_name
                    
                    await db.clients.update_one(
                        {'id': client['id']},
                        {'$set': {
                            'agent_name': agent_name,
                            'added_by_agent_name': agent_name
                        }}
                    )
    
    return [ClientResponse(**client) for client in clients]

@api_router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, current_user: dict = Depends(get_current_user)):
    client = await db.clients.find_one({'id': client_id}, {'_id': 0})
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check permission - agents can only view their own clients, admins can view all
    if current_user['role'] != 'admin' and client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this client")
    
    return ClientResponse(**client)

@api_router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, data: ClientUpdate, current_user: dict = Depends(get_current_user)):
    client = await db.clients.find_one({'id': client_id}, {'_id': 0})
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check permission - agents can only update their own clients
    if client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this client")
    
    # Build update dict
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    
    # Recalculate annual premium if monthly premium changed or product type changed
    if 'monthly_premium' in update_data or 'product_type' in update_data:
        product_type = update_data.get('product_type', client.get('product_type'))
        monthly_premium = update_data.get('monthly_premium', client.get('monthly_premium'))
        
        if product_type in ['IUL', 'Term', 'FEX', 'Whole Life'] and monthly_premium:
            update_data['annual_premium'] = monthly_premium * 12
        else:
            update_data['annual_premium'] = None
    
    # Convert beneficiaries to dict format if present
    if 'beneficiaries' in update_data and update_data['beneficiaries']:
        update_data['beneficiaries'] = [b.dict() if hasattr(b, 'dict') else b for b in update_data['beneficiaries']]
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.clients.update_one({'id': client_id}, {'$set': update_data})
    
    # ========== SYNC TO CLIENT PORTAL ==========
    # Check if this client has a portal account
    portal_client = await db.portal_clients.find_one({'book_client_id': client_id}, {'_id': 0})
    
    if portal_client:
        # Sync relevant changes to portal_client
        portal_updates = {}
        
        if 'first_name' in update_data:
            portal_updates['first_name'] = update_data['first_name']
        if 'last_name' in update_data:
            portal_updates['last_name'] = update_data['last_name']
        if 'email' in update_data:
            portal_updates['email'] = update_data['email']
        
        if portal_updates:
            portal_updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            await db.portal_clients.update_one({'book_client_id': client_id}, {'$set': portal_updates})
        
        # Sync policy information
        policy_updates = {}
        
        if 'carrier' in update_data:
            policy_updates['carrier'] = update_data['carrier']
        if 'product_type' in update_data:
            policy_updates['product_type'] = update_data['product_type']
        if 'policy_number' in update_data:
            policy_updates['policy_number'] = update_data['policy_number']
        if 'date_issued' in update_data:
            policy_updates['issue_date'] = update_data['date_issued']
        if 'coverage_amount' in update_data:
            policy_updates['face_amount'] = update_data['coverage_amount']
        if 'monthly_premium' in update_data:
            policy_updates['monthly_premium'] = update_data['monthly_premium']
            policy_updates['premium'] = update_data['monthly_premium'] * 12
        if 'status' in update_data:
            policy_updates['status'] = 'active' if update_data['status'] == 'Issued' else 'pending'
        if 'client_why' in update_data:
            policy_updates['short_explanation'] = update_data['client_why']
        
        if policy_updates:
            policy_updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            # Update the policy linked to this portal client
            await db.portal_policies.update_one(
                {'client_id': portal_client['id']}, 
                {'$set': policy_updates}
            )
    
    updated_client = await db.clients.find_one({'id': client_id}, {'_id': 0})
    return ClientResponse(**updated_client)

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str, current_user: dict = Depends(get_current_user)):
    client = await db.clients.find_one({'id': client_id}, {'_id': 0})
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check permission - agents can only delete their own clients
    if client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this client")
    
    await db.clients.delete_one({'id': client_id})
    return {"message": "Client deleted successfully"}

@api_router.get("/clients/export/{format}")
async def export_clients(format: str, current_user: dict = Depends(get_current_user)):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # Get only current user's clients (agent-only visibility)
    query = {'agent_id': current_user['id']}
    
    clients = await db.clients.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
    
    if format.lower() == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'First Name', 'Last Name', 'Birth Date', 'State', 'Carrier', 
            'Product', 'Product Type', 'Policy Number', 'Monthly Premium', 'Annual Premium',
            'Premium (Annuity)', 'Status', 'Date Submitted', 'Date Issued',
            'Lead Source', 'Client Why', 'Beneficiaries', 'Additional Notes', 'Created At'
        ])
        
        # Write data
        for client in clients:
            beneficiaries_str = '; '.join([f"{b.get('name', '')} ({b.get('phone_number', '')})" for b in client.get('beneficiaries', [])])
            lead_source_display = client.get('lead_source', '')
            if lead_source_display == 'Other' and client.get('lead_source_other'):
                lead_source_display = f"Other: {client.get('lead_source_other')}"
            
            writer.writerow([
                client.get('first_name', ''),
                client.get('last_name', ''),
                client.get('birth_date', ''),
                client.get('state', ''),
                client.get('carrier', ''),
                client.get('product', ''),
                client.get('product_type', ''),
                client.get('policy_number', ''),
                client.get('monthly_premium', '') if client.get('monthly_premium') else '',
                client.get('annual_premium', '') if client.get('annual_premium') else '',
                client.get('premium', '') if client.get('premium') else '',
                client.get('status', ''),
                client.get('date_submitted', ''),
                client.get('date_issued', ''),
                lead_source_display,
                client.get('client_why', ''),
                beneficiaries_str,
                client.get('additional_notes', ''),
                client.get('created_at', '')
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename=book_of_business.csv'}
        )
    
    elif format.lower() == 'xlsx':
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Book of Business"
        
        # Write header
        headers = [
            'First Name', 'Last Name', 'Birth Date', 'State', 'Carrier',
            'Product', 'Policy Number', 'Monthly Premium', 'Annual Premium',
            'Client Why', 'Beneficiaries', 'Additional Notes', 'Created At'
        ]
        ws.append(headers)
        
        # Write data
        for client in clients:
            beneficiaries_str = '; '.join([f"{b.get('name', '')} ({b.get('phone_number', '')})" for b in client.get('beneficiaries', [])])
            ws.append([
                client.get('first_name', ''),
                client.get('last_name', ''),
                client.get('birth_date', ''),
                client.get('state', ''),
                client.get('carrier', ''),
                client.get('product', ''),
                client.get('policy_number', ''),
                client.get('monthly_premium', 0),
                client.get('annual_premium', 0),
                client.get('client_why', ''),
                beneficiaries_str,
                client.get('additional_notes', ''),
                client.get('created_at', '')
            ])
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=book_of_business.xlsx'}
        )
    
    elif format.lower() == 'pdf':
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph(f"<b>Book of Business - {current_user['name']}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Create table data
        table_data = [[
            'Name', 'Birth Date', 'State', 'Carrier', 'Product',
            'Policy #', 'Monthly', 'Annual', 'Client Why'
        ]]
        
        for client in clients:
            table_data.append([
                f"{client.get('first_name', '')} {client.get('last_name', '')}",
                client.get('birth_date', ''),
                client.get('state', ''),
                client.get('carrier', ''),
                client.get('product', ''),
                client.get('policy_number', ''),
                f"${client.get('monthly_premium', 0):.2f}",
                f"${client.get('annual_premium', 0):.2f}",
                client.get('client_why', '')[:30] + '...' if client.get('client_why', '') and len(client.get('client_why', '')) > 30 else client.get('client_why', '')
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename=book_of_business.pdf'}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv, xlsx, or pdf")

@api_router.get("/production/personal")
async def get_personal_production(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get personal production data from Book of Business"""
    query = {'agent_id': current_user['id']}
    
    # Add date filtering if provided
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        
        # Check both date_submitted and date_issued
        query['$or'] = [
            {'date_submitted': date_query},
            {'date_issued': date_query}
        ]
    
    clients = await db.clients.find(query, {'_id': 0}).to_list(1000)
    
    # Calculate totals
    submitted_ap = 0
    issued_ap = 0
    
    for client in clients:
        # For annuities, use premium; for others use annual_premium
        premium_amount = client.get('premium', 0) or client.get('annual_premium', 0) or 0
        
        if client.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
            submitted_ap += premium_amount
        
        if client.get('status') == 'Issued':
            issued_ap += premium_amount
    
    return {
        'submitted_ap': submitted_ap,
        'issued_ap': issued_ap,
        'total_policies': len(clients),
        'clients': clients
    }

@api_router.get("/production/team")
async def get_team_production(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get team production data (personal + all downline agents)"""
    # Helper function to get all downline recursively
    async def get_all_downline_ids(user_id: str) -> List[str]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
        all_ids = [agent['id'] for agent in downline]
        for agent in downline:
            sub_ids = await get_all_downline_ids(agent['id'])
            all_ids.extend(sub_ids)
        return all_ids
    
    # Get all downline agents (including self)
    all_downline_ids = await get_all_downline_ids(current_user['id'])
    agent_ids = [current_user['id']] + all_downline_ids
    
    # Get all agents details
    all_agents = await db.users.find({'id': {'$in': agent_ids}}, {'_id': 0}).to_list(1000)
    total_active_agents = len([a for a in all_agents if a.get('status') == 'active'])
    
    query = {'agent_id': {'$in': agent_ids}}
    
    # Add date filtering
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        
        query['$or'] = [
            {'date_submitted': date_query},
            {'date_issued': date_query}
        ]
    
    clients = await db.clients.find(query, {'_id': 0}).to_list(5000)
    
    # Calculate totals
    submitted_ap = 0
    issued_ap = 0
    
    # Aggregate by agent
    agent_production = {}
    writing_agents = set()
    
    for client in clients:
        premium_amount = client.get('premium', 0) or client.get('annual_premium', 0) or 0
        agent_id = client.get('agent_id')
        
        if agent_id not in agent_production:
            # Get agent details
            agent = await db.users.find_one({'id': agent_id}, {'_id': 0})
            agent_name = f"{agent.get('first_name', '')} {agent.get('last_name', '')}" if agent else 'Unknown'
            
            agent_production[agent_id] = {
                'agent_id': agent_id,
                'agent_name': agent_name,
                'submitted_ap': 0,
                'issued_ap': 0,
                'policies': 0,
                'date_joined': agent.get('date_joined') if agent else None
            }
        
        agent_production[agent_id]['policies'] += 1
        
        if client.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
            submitted_ap += premium_amount
            agent_production[agent_id]['submitted_ap'] += premium_amount
            writing_agents.add(agent_id)
        
        if client.get('status') == 'Issued':
            issued_ap += premium_amount
            agent_production[agent_id]['issued_ap'] += premium_amount
    
    # Calculate metrics
    writing_agent_count = len(writing_agents)
    writing_agent_percentage = (writing_agent_count / total_active_agents * 100) if total_active_agents > 0 else 0
    avg_submitted_per_writer = submitted_ap / writing_agent_count if writing_agent_count > 0 else 0
    
    # Calculate average time to first sale
    time_to_first_sale_days = []
    for agent_id in writing_agents:
        agent_data = agent_production.get(agent_id)
        if agent_data and agent_data.get('date_joined'):
            # Get first submitted policy for this agent
            first_policy = await db.clients.find_one(
                {
                    'agent_id': agent_id,
                    'date_submitted': {'$exists': True, '$ne': None}
                },
                {'_id': 0},
                sort=[('date_submitted', 1)]
            )
            
            if first_policy and first_policy.get('date_submitted'):
                try:
                    from datetime import datetime
                    date_joined = datetime.fromisoformat(agent_data['date_joined'].replace('Z', '+00:00'))
                    date_first_sale = datetime.fromisoformat(first_policy['date_submitted'] + 'T00:00:00+00:00')
                    days_diff = (date_first_sale - date_joined).days
                    if days_diff >= 0:  # Only count positive differences
                        time_to_first_sale_days.append(days_diff)
                except:
                    pass
    
    avg_days_to_first_sale = sum(time_to_first_sale_days) / len(time_to_first_sale_days) if time_to_first_sale_days else 0
    
    # Convert to list and sort by total production
    agent_list = list(agent_production.values())
    agent_list.sort(key=lambda x: x['submitted_ap'] + x['issued_ap'], reverse=True)
    
    return {
        'submitted_ap': submitted_ap,
        'issued_ap': issued_ap,
        'total_policies': len(clients),
        'agents': agent_list,
        'clients': clients,
        'analytics': {
            'total_active_agents': total_active_agents,
            'writing_agents': writing_agent_count,
            'writing_agent_percentage': round(writing_agent_percentage, 1),
            'avg_submitted_per_writer': round(avg_submitted_per_writer, 2),
            'avg_days_to_first_sale': round(avg_days_to_first_sale, 1)
        }
    }

@api_router.get("/production/direct-legs")
async def get_direct_legs_production(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get production breakdown by direct legs (each direct report + their entire downline)"""
    
    # Helper function to get all downline recursively for a specific agent
    async def get_all_downline_ids(user_id: str) -> List[str]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
        all_ids = [agent['id'] for agent in downline]
        for agent in downline:
            sub_ids = await get_all_downline_ids(agent['id'])
            all_ids.extend(sub_ids)
        return all_ids
    
    # Calculate previous period dates for growth comparison
    from datetime import datetime, timedelta
    prev_start_date = None
    prev_end_date = None
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        period_length = (end - start).days
        prev_end_date = (start - timedelta(days=1)).isoformat().split('T')[0]
        prev_start_date = (start - timedelta(days=period_length + 1)).isoformat().split('T')[0]
    
    # Get direct legs only
    direct_legs = await db.users.find(
        {'upline_id': current_user['id'], 'status': 'active'}, 
        {'_id': 0}
    ).to_list(1000)
    
    if not direct_legs:
        return {
            'total_team_production': 0,
            'legs': []
        }
    
    # Build query for date filtering
    def build_date_query(start, end):
        if start or end:
            date_filter = {}
            if start:
                date_filter['$gte'] = start
            if end:
                date_filter['$lte'] = end
            return {
                '$or': [
                    {'date_submitted': date_filter},
                    {'date_issued': date_filter}
                ]
            }
        return {}
    
    date_query_part = build_date_query(start_date, end_date)
    prev_date_query_part = build_date_query(prev_start_date, prev_end_date)
    
    legs_data = []
    total_team_production = 0
    prev_total_team_production = 0
    
    for leg in direct_legs:
        # Get this leg + all their downline
        leg_downline_ids = await get_all_downline_ids(leg['id'])
        leg_agent_ids = [leg['id']] + leg_downline_ids
        
        # Build query for this leg's team (current period)
        leg_query = {
            'agent_id': {'$in': leg_agent_ids},
            'status': {'$in': ['Pending Approval/Issue', 'Issued', 'Missed Payment']}
        }
        if date_query_part:
            leg_query.update(date_query_part)
        
        # Get all policies for this leg's team
        leg_clients = await db.clients.find(leg_query, {'_id': 0}).to_list(5000)
        
        # Calculate production
        leg_production = 0
        for client in leg_clients:
            premium = client.get('premium', 0) or client.get('annual_premium', 0) or 0
            leg_production += premium
        
        # Calculate previous period production
        prev_leg_production = 0
        if prev_date_query_part:
            prev_leg_query = {
                'agent_id': {'$in': leg_agent_ids},
                'status': {'$in': ['Pending Approval/Issue', 'Issued', 'Missed Payment']}
            }
            prev_leg_query.update(prev_date_query_part)
            prev_leg_clients = await db.clients.find(prev_leg_query, {'_id': 0}).to_list(5000)
            
            for client in prev_leg_clients:
                premium = client.get('premium', 0) or client.get('annual_premium', 0) or 0
                prev_leg_production += premium
        
        # Calculate growth
        growth_amount = leg_production - prev_leg_production
        growth_percentage = ((leg_production - prev_leg_production) / prev_leg_production * 100) if prev_leg_production > 0 else 0
        
        total_team_production += leg_production
        prev_total_team_production += prev_leg_production
        
        legs_data.append({
            'leg_id': leg['id'],
            'leg_name': f"{leg.get('first_name', '')} {leg.get('last_name', '')}",
            'production': leg_production,
            'prev_production': prev_leg_production,
            'growth_amount': growth_amount,
            'growth_percentage': round(growth_percentage, 1),
            'team_size': len(leg_agent_ids),
            'policies': len(leg_clients)
        })
    
    # Calculate percentages
    for leg in legs_data:
        leg['percentage'] = round((leg['production'] / total_team_production * 100), 1) if total_team_production > 0 else 0
    
    # Sort by production (highest first)
    legs_data.sort(key=lambda x: x['production'], reverse=True)
    
    # Add performance tier
    if legs_data:
        top_25_threshold = legs_data[0]['production'] * 0.75 if legs_data else 0
        for leg in legs_data:
            if leg['production'] >= top_25_threshold:
                leg['tier'] = 'top'
            elif leg['production'] >= (total_team_production / len(legs_data)):
                leg['tier'] = 'middle'
            else:
                leg['tier'] = 'bottom'
    
    return {
        'total_team_production': total_team_production,
        'prev_total_team_production': prev_total_team_production,
        'total_growth_percentage': round(((total_team_production - prev_total_team_production) / prev_total_team_production * 100), 1) if prev_total_team_production > 0 else 0,
        'legs': legs_data
    }

@api_router.get("/production/leg-breakdown/{leg_id}")
async def get_leg_breakdown(
    leg_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed breakdown of a specific leg's team production"""
    
    # Verify the leg is in user's downline
    leg = await db.users.find_one({'id': leg_id}, {'_id': 0})
    if not leg:
        raise HTTPException(status_code=404, detail="Leg not found")
    
    # Helper function
    async def get_all_downline_ids(user_id: str) -> List[str]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
        all_ids = [agent['id'] for agent in downline]
        for agent in downline:
            sub_ids = await get_all_downline_ids(agent['id'])
            all_ids.extend(sub_ids)
        return all_ids
    
    # Get leg's immediate downline
    immediate_downline = await db.users.find(
        {'upline_id': leg_id, 'status': 'active'}, 
        {'_id': 0}
    ).to_list(1000)
    
    # Build date query
    date_query_part = {}
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter['$gte'] = start_date
        if end_date:
            date_filter['$lte'] = end_date
        date_query_part = {
            '$or': [
                {'date_submitted': date_filter},
                {'date_issued': date_filter}
            ]
        }
    
    agents_data = []
    
    # Add the leg themselves
    leg_query = {
        'agent_id': leg_id,
        'status': {'$in': ['Pending Approval/Issue', 'Issued', 'Missed Payment']}
    }
    if date_query_part:
        leg_query.update(date_query_part)
    
    leg_clients = await db.clients.find(leg_query, {'_id': 0}).to_list(5000)
    leg_production = sum(c.get('premium', 0) or c.get('annual_premium', 0) or 0 for c in leg_clients)
    
    agents_data.append({
        'agent_id': leg_id,
        'agent_name': f"{leg.get('first_name', '')} {leg.get('last_name', '')} (Leg)",
        'production': leg_production,
        'policies': len(leg_clients),
        'is_leg': True
    })
    
    # Add immediate downline with their teams
    for agent in immediate_downline:
        agent_downline_ids = await get_all_downline_ids(agent['id'])
        agent_team_ids = [agent['id']] + agent_downline_ids
        
        agent_query = {
            'agent_id': {'$in': agent_team_ids},
            'status': {'$in': ['Pending Approval/Issue', 'Issued', 'Missed Payment']}
        }
        if date_query_part:
            agent_query.update(date_query_part)
        
        agent_clients = await db.clients.find(agent_query, {'_id': 0}).to_list(5000)
        agent_production = sum(c.get('premium', 0) or c.get('annual_premium', 0) or 0 for c in agent_clients)
        
        agents_data.append({
            'agent_id': agent['id'],
            'agent_name': f"{agent.get('first_name', '')} {agent.get('last_name', '')}",
            'production': agent_production,
            'policies': len(agent_clients),
            'team_size': len(agent_team_ids),
            'is_leg': False
        })
    
    # Sort by production
    agents_data.sort(key=lambda x: x['production'], reverse=True)
    
    total_production = sum(a['production'] for a in agents_data)
    for agent in agents_data:
        agent['percentage'] = round((agent['production'] / total_production * 100), 1) if total_production > 0 else 0
    
    return {
        'leg_name': f"{leg.get('first_name', '')} {leg.get('last_name', '')}",
        'total_production': total_production,
        'agents': agents_data
    }

@api_router.post("/admin/impersonate/{user_id}")
async def impersonate_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Allow admin to impersonate/view as another user"""
    
    # Only admins can impersonate
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can impersonate users")
    
    # Get target user
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create audit log
    await db.audit_logs.insert_one({
        'id': str(uuid4()),
        'action': 'impersonation_start',
        'admin_id': current_user['id'],
        'admin_name': f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
        'target_user_id': user_id,
        'target_user_name': f"{target_user.get('first_name', '')} {target_user.get('last_name', '')}",
        'details': {
            'target_role': target_user.get('role'),
            'target_email': target_user.get('email')
        },
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    # Create impersonation token with special flag
    token_data = {
        'sub': target_user['email'],
        'user_id': target_user['id'],
        'role': target_user['role'],
        'impersonated_by': current_user['id'],  # Track who is impersonating
        'impersonated_by_name': f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
        'exp': datetime.now(timezone.utc) + timedelta(hours=2)  # Shorter expiry for security
    }
    impersonation_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        'token': impersonation_token,
        'user': {
            'id': target_user['id'],
            'email': target_user['email'],
            'first_name': target_user.get('first_name'),
            'last_name': target_user.get('last_name'),
            'role': target_user['role']
        },
        'impersonated_by': {
            'id': current_user['id'],
            'name': f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}"
        }
    }

@api_router.post("/admin/stop-impersonation")
async def stop_impersonation(current_user: dict = Depends(get_current_user)):
    """Stop impersonating and return to admin account"""
    
    # Check if currently impersonating
    impersonated_by = current_user.get('impersonated_by')
    if not impersonated_by:
        raise HTTPException(status_code=400, detail="Not currently impersonating")
    
    # Get the original admin user
    admin_user = await db.users.find_one({'id': impersonated_by}, {'_id': 0})
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    # Create audit log for stopping impersonation
    await db.audit_logs.insert_one({
        'id': str(uuid4()),
        'action': 'impersonation_stop',
        'admin_id': impersonated_by,
        'admin_name': current_user.get('impersonated_by_name', ''),
        'target_user_id': current_user['id'],
        'target_user_name': f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
        'details': {},
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    # Create new token for admin
    token_data = {
        'sub': admin_user['email'],
        'user_id': admin_user['id'],
        'role': admin_user['role'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    admin_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        'token': admin_token,
        'user': {
            'id': admin_user['id'],
            'email': admin_user['email'],
            'first_name': admin_user.get('first_name'),
            'last_name': admin_user.get('last_name'),
            'role': admin_user['role']
        }
    }

@api_router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user)):
    """Get company-wide leaderboard with all agents' production metrics"""
    
    # Get all users
    users = await db.users.find({'status': 'active'}, {'_id': 0, 'password_hash': 0}).to_list(1000)
    
    # Create a dict to store each agent's production
    leaderboard_data = []
    
    for user in users:
        # Get all clients for this agent
        clients = await db.clients.find({'agent_id': user['id']}, {'_id': 0}).to_list(10000)
        
        submitted_ap = 0
        issued_ap = 0
        total_apps = len(clients)
        
        for client in clients:
            premium_amount = 0
            
            if client.get('product_type') == 'Annuity':
                premium_amount = client.get('premium', 0) or 0
            elif client.get('product_type') == 'IUL':
                premium_amount = client.get('annual_premium', 0) or 0
            else:
                premium_amount = client.get('monthly_premium', 0) or 0
            
            if client.get('status') in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
                submitted_ap += premium_amount
            
            if client.get('status') == 'Issued':
                issued_ap += premium_amount
        
        leaderboard_data.append({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'submitted_ap': submitted_ap,
            'issued_ap': issued_ap,
            'total_apps': total_apps,
            'profile_picture': user.get('profile_picture')
        })
    
    # Sort by submitted AP (primary), then issued AP (secondary)
    leaderboard_data.sort(key=lambda x: (x['submitted_ap'], x['issued_ap']), reverse=True)
    
    # Add ranking
    for idx, agent in enumerate(leaderboard_data):
        agent['rank'] = idx + 1
    
    return leaderboard_data

# ==================== DASHBOARD CHARTS ====================

@api_router.get("/charts/production-trend")
async def get_production_trend(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get personal production trend data for charts (last N days)"""
    from datetime import datetime, timedelta, timezone
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get all clients submitted by this user
    clients = await db.clients.find(
        {'agent_id': current_user['id']},
        {'_id': 0, 'date_submitted': 1, 'premium': 1, 'annual_premium': 1, 'monthly_premium': 1, 'status': 1}
    ).to_list(10000)
    
    # Initialize daily data
    daily_data = {}
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data[date] = {'date': date, 'submitted_ap': 0}
    
    # Aggregate production by date
    for client in clients:
        date_submitted = client.get('date_submitted')
        if not date_submitted:
            continue
        
        # Only count submitted/issued statuses
        if client.get('status') not in ['Pending Approval/Issue', 'Issued', 'Missed Payment']:
            continue
        
        # Check if within date range
        if date_submitted >= start_date.strftime('%Y-%m-%d') and date_submitted <= end_date.strftime('%Y-%m-%d'):
            premium = client.get('premium', 0) or client.get('annual_premium', 0) or client.get('monthly_premium', 0) or 0
            if date_submitted in daily_data:
                daily_data[date_submitted]['submitted_ap'] += premium
    
    # Convert to list sorted by date
    result = sorted(daily_data.values(), key=lambda x: x['date'])
    
    # Format dates for display
    for item in result:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        item['label'] = date_obj.strftime('%b %d')
    
    return result

@api_router.get("/charts/team-growth")
async def get_team_growth(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get team growth trend data for charts (last N days)"""
    from datetime import datetime, timedelta, timezone
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Helper function to get all downline recursively
    async def get_all_downline_ids(user_id: str) -> List[str]:
        downline = await db.users.find({'upline_id': user_id}, {'_id': 0}).to_list(1000)
        all_ids = [agent['id'] for agent in downline]
        for agent in downline:
            sub_ids = await get_all_downline_ids(agent['id'])
            all_ids.extend(sub_ids)
        return all_ids
    
    # Get all downline agent IDs
    all_downline_ids = await get_all_downline_ids(current_user['id'])
    agent_ids = [current_user['id']] + all_downline_ids
    
    # Get all team members with their join dates
    team_members = await db.users.find(
        {'id': {'$in': agent_ids}},
        {'_id': 0, 'id': 1, 'date_joined': 1}
    ).to_list(1000)
    
    # Initialize daily data with cumulative count
    daily_data = {}
    
    # Count agents who joined before the start date (baseline)
    baseline_count = 0
    for member in team_members:
        join_date = member.get('date_joined', '')
        if join_date:
            # Extract just the date part
            join_date_str = join_date[:10] if len(join_date) >= 10 else join_date
            if join_date_str < start_date.strftime('%Y-%m-%d'):
                baseline_count += 1
    
    # Build daily data
    running_total = baseline_count
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Count new joins on this day
        new_joins = 0
        for member in team_members:
            join_date = member.get('date_joined', '')
            if join_date:
                join_date_str = join_date[:10] if len(join_date) >= 10 else join_date
                if join_date_str == date:
                    new_joins += 1
        
        running_total += new_joins
        daily_data[date] = {
            'date': date,
            'agents': running_total,
            'new_joins': new_joins
        }
    
    # Convert to list sorted by date
    result = sorted(daily_data.values(), key=lambda x: x['date'])
    
    # Format dates for display
    for item in result:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        item['label'] = date_obj.strftime('%b %d')
    
    return result

# ==================== QUIZ SYSTEM ====================

# Quiz Pydantic Models
class QuizQuestion(BaseModel):
    id: str
    product: str  # IUL, FIA, Term, Final Expense
    difficulty: str  # Easy, Intermediate, Expert
    category: str  # Product Knowledge, Client Scenarios, Compliance, Suitability, Sales Process
    question: str
    options: Dict[str, str]  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer: str  # A, B, C, or D
    explanation: str
    created_at: Optional[str] = None

class QuizQuestionCreate(BaseModel):
    product: str
    difficulty: str
    category: str
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str

class QuizAnswer(BaseModel):
    question_id: str
    selected_answer: str

class QuizSubmission(BaseModel):
    product: str
    difficulty: str
    answers: List[QuizAnswer]

class QuizAttempt(BaseModel):
    id: str
    user_id: str
    product: str
    difficulty: str
    score: int
    total_questions: int
    percentage: float
    passed: bool
    question_results: List[Dict]
    created_at: str

class UserQuizProgress(BaseModel):
    user_id: str
    total_quizzes_taken: int
    total_passed: int
    current_streak: int
    best_streak: int
    achievements: List[str]
    product_stats: Dict[str, Dict]  # {product: {difficulty: {attempts, best_score, passed}}}

# Get quiz questions for a specific product and difficulty
@api_router.get("/quiz/questions")
async def get_quiz_questions(
    product: str,
    difficulty: str,
    current_user: dict = Depends(get_current_user)
):
    """Get 10 random questions for a quiz"""
    
    valid_products = ['IUL', 'FIA', 'Term', 'Final Expense']
    valid_difficulties = ['Easy', 'Intermediate', 'Expert']
    
    if product not in valid_products:
        raise HTTPException(status_code=400, detail=f"Invalid product. Must be one of: {valid_products}")
    if difficulty not in valid_difficulties:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Must be one of: {valid_difficulties}")
    
    # Get all questions matching criteria
    questions = await db.quiz_questions.find(
        {'product': product, 'difficulty': difficulty},
        {'_id': 0}
    ).to_list(1000)
    
    if len(questions) < 10:
        raise HTTPException(status_code=404, detail=f"Not enough questions available. Found {len(questions)}, need 10.")
    
    # Randomly select 10 questions with category distribution
    # Target distribution: 3 Product Knowledge, 2-3 Client Scenarios, 2 Compliance, 1-2 Suitability, 1 Sales Process
    categories = {
        'Product Knowledge': 3,
        'Client Scenarios': 3,
        'Compliance': 2,
        'Suitability': 1,
        'Sales Process': 1
    }
    
    selected_questions = []
    remaining_questions = questions.copy()
    
    # Try to get questions by category distribution
    for category, count in categories.items():
        category_questions = [q for q in remaining_questions if q.get('category') == category]
        if category_questions:
            selected = random.sample(category_questions, min(count, len(category_questions)))
            selected_questions.extend(selected)
            for q in selected:
                remaining_questions.remove(q)
    
    # If we don't have 10, fill randomly from remaining
    while len(selected_questions) < 10 and remaining_questions:
        q = random.choice(remaining_questions)
        selected_questions.append(q)
        remaining_questions.remove(q)
    
    # Shuffle and return (without correct answers for security)
    random.shuffle(selected_questions)
    
    # Remove correct_answer and explanation from response for quiz taking
    quiz_questions = []
    for q in selected_questions[:10]:
        quiz_questions.append({
            'id': q['id'],
            'product': q['product'],
            'difficulty': q['difficulty'],
            'category': q['category'],
            'question': q['question'],
            'options': q['options']
        })
    
    return quiz_questions

# Verify a single answer
class SingleAnswerCheck(BaseModel):
    question_id: str
    selected_answer: str

@api_router.post("/quiz/check-answer")
async def check_single_answer(
    answer: SingleAnswerCheck,
    current_user: dict = Depends(get_current_user)
):
    """Check a single answer and return feedback"""
    
    question = await db.quiz_questions.find_one(
        {'id': answer.question_id},
        {'_id': 0}
    )
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = answer.selected_answer == question['correct_answer']
    
    return {
        'question_id': answer.question_id,
        'selected_answer': answer.selected_answer,
        'correct_answer': question['correct_answer'],
        'is_correct': is_correct,
        'explanation': question.get('explanation', '')
    }

# Submit quiz answers and get results
@api_router.post("/quiz/submit")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit quiz answers and get results"""
    
    if len(submission.answers) != 10:
        raise HTTPException(status_code=400, detail="Quiz must have exactly 10 answers")
    
    # Get question details for each answer
    question_ids = [a.question_id for a in submission.answers]
    questions = await db.quiz_questions.find(
        {'id': {'$in': question_ids}},
        {'_id': 0}
    ).to_list(10)
    
    questions_dict = {q['id']: q for q in questions}
    
    # Calculate score and build results
    correct_count = 0
    question_results = []
    category_scores = {}
    
    for answer in submission.answers:
        question = questions_dict.get(answer.question_id)
        if not question:
            continue
        
        is_correct = answer.selected_answer == question['correct_answer']
        if is_correct:
            correct_count += 1
        
        # Track category performance
        category = question.get('category', 'Unknown')
        if category not in category_scores:
            category_scores[category] = {'correct': 0, 'total': 0}
        category_scores[category]['total'] += 1
        if is_correct:
            category_scores[category]['correct'] += 1
        
        question_results.append({
            'question_id': answer.question_id,
            'question': question['question'],
            'category': category,
            'selected_answer': answer.selected_answer,
            'correct_answer': question['correct_answer'],
            'is_correct': is_correct,
            'explanation': question['explanation'],
            'options': question['options']
        })
    
    percentage = (correct_count / 10) * 100
    passed = percentage >= 70
    
    # Create quiz attempt record
    attempt_id = str(uuid.uuid4())
    attempt = {
        'id': attempt_id,
        'user_id': current_user['id'],
        'product': submission.product,
        'difficulty': submission.difficulty,
        'score': correct_count,
        'total_questions': 10,
        'percentage': percentage,
        'passed': passed,
        'question_results': question_results,
        'category_scores': category_scores,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.quiz_attempts.insert_one(attempt)
    
    # Update user progress
    await update_user_quiz_progress(current_user['id'], submission.product, submission.difficulty, passed, percentage)
    
    return {
        'id': attempt_id,
        'score': correct_count,
        'total_questions': 10,
        'percentage': percentage,
        'passed': passed,
        'question_results': question_results,
        'category_scores': category_scores
    }

async def update_user_quiz_progress(user_id: str, product: str, difficulty: str, passed: bool, percentage: float):
    """Update user's quiz progress and achievements"""
    
    # Get or create progress document
    progress = await db.user_quiz_progress.find_one({'user_id': user_id}, {'_id': 0})
    
    if not progress:
        progress = {
            'user_id': user_id,
            'total_quizzes_taken': 0,
            'total_passed': 0,
            'current_streak': 0,
            'best_streak': 0,
            'achievements': [],
            'product_stats': {}
        }
    
    # Update basic stats
    progress['total_quizzes_taken'] += 1
    
    if passed:
        progress['total_passed'] += 1
        progress['current_streak'] += 1
        if progress['current_streak'] > progress['best_streak']:
            progress['best_streak'] = progress['current_streak']
    else:
        progress['current_streak'] = 0
    
    # Update product-specific stats
    if product not in progress['product_stats']:
        progress['product_stats'][product] = {}
    if difficulty not in progress['product_stats'][product]:
        progress['product_stats'][product][difficulty] = {
            'attempts': 0,
            'passed': 0,
            'best_score': 0
        }
    
    progress['product_stats'][product][difficulty]['attempts'] += 1
    if passed:
        progress['product_stats'][product][difficulty]['passed'] += 1
    if percentage > progress['product_stats'][product][difficulty]['best_score']:
        progress['product_stats'][product][difficulty]['best_score'] = percentage
    
    # Check for achievements
    achievements = progress['achievements']
    
    # Perfect Score
    if percentage == 100 and 'Perfect Score' not in achievements:
        achievements.append('Perfect Score')
    
    # Product Expert badges (pass Expert 3x)
    for prod in ['IUL', 'FIA', 'Term', 'Final Expense']:
        badge_name = f'{prod} Expert'
        if badge_name not in achievements:
            stats = progress['product_stats'].get(prod, {}).get('Expert', {})
            if stats.get('passed', 0) >= 3:
                achievements.append(badge_name)
    
    # Well Rounded (pass all 4 products at same difficulty)
    for diff in ['Easy', 'Intermediate', 'Expert']:
        badge_name = f'Well Rounded ({diff})'
        if badge_name not in achievements:
            all_passed = True
            for prod in ['IUL', 'FIA', 'Term', 'Final Expense']:
                stats = progress['product_stats'].get(prod, {}).get(diff, {})
                if stats.get('passed', 0) < 1:
                    all_passed = False
                    break
            if all_passed:
                achievements.append(badge_name)
    
    # Streak achievements
    if progress['current_streak'] >= 5 and '5 Quiz Streak' not in achievements:
        achievements.append('5 Quiz Streak')
    if progress['current_streak'] >= 10 and '10 Quiz Streak' not in achievements:
        achievements.append('10 Quiz Streak')
    
    progress['achievements'] = achievements
    
    # Upsert progress
    await db.user_quiz_progress.update_one(
        {'user_id': user_id},
        {'$set': progress},
        upsert=True
    )

# Get user's quiz progress
@api_router.get("/quiz/progress")
async def get_quiz_progress(current_user: dict = Depends(get_current_user)):
    """Get user's quiz progress and achievements"""
    
    progress = await db.user_quiz_progress.find_one(
        {'user_id': current_user['id']},
        {'_id': 0}
    )
    
    if not progress:
        progress = {
            'user_id': current_user['id'],
            'total_quizzes_taken': 0,
            'total_passed': 0,
            'current_streak': 0,
            'best_streak': 0,
            'achievements': [],
            'product_stats': {}
        }
    
    # Get recent attempts
    recent_attempts = await db.quiz_attempts.find(
        {'user_id': current_user['id']},
        {'_id': 0, 'question_results': 0}
    ).sort('created_at', -1).limit(10).to_list(10)
    
    progress['recent_attempts'] = recent_attempts
    
    return progress

# Get quiz history
@api_router.get("/quiz/history")
async def get_quiz_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's quiz attempt history"""
    
    attempts = await db.quiz_attempts.find(
        {'user_id': current_user['id']},
        {'_id': 0, 'question_results': 0}
    ).sort('created_at', -1).limit(limit).to_list(limit)
    
    return attempts

# Admin: Get all questions
@api_router.get("/quiz/admin/questions")
async def admin_get_questions(
    product: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Admin: Get all quiz questions with filters"""
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = {}
    if product:
        query['product'] = product
    if difficulty:
        query['difficulty'] = difficulty
    
    questions = await db.quiz_questions.find(query, {'_id': 0}).to_list(10000)
    
    return questions

# Admin: Add question
@api_router.post("/quiz/admin/questions")
async def admin_add_question(
    question: QuizQuestionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Admin: Add a new quiz question"""
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    question_doc = {
        'id': str(uuid.uuid4()),
        'product': question.product,
        'difficulty': question.difficulty,
        'category': question.category,
        'question': question.question,
        'options': question.options,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.quiz_questions.insert_one(question_doc)
    
    return {'id': question_doc['id'], 'message': 'Question added successfully'}

# Admin: Update question
@api_router.put("/quiz/admin/questions/{question_id}")
async def admin_update_question(
    question_id: str,
    question: QuizQuestionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Admin: Update a quiz question"""
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.quiz_questions.update_one(
        {'id': question_id},
        {'$set': {
            'product': question.product,
            'difficulty': question.difficulty,
            'category': question.category,
            'question': question.question,
            'options': question.options,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {'message': 'Question updated successfully'}

# Admin: Delete question
@api_router.delete("/quiz/admin/questions/{question_id}")
async def admin_delete_question(
    question_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin: Delete a quiz question"""
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.quiz_questions.delete_one({'id': question_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {'message': 'Question deleted successfully'}

# Get question stats (for admin analytics)
@api_router.get("/quiz/admin/stats")
async def admin_get_quiz_stats(current_user: dict = Depends(get_current_user)):
    """Admin: Get quiz statistics"""
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Count questions by product and difficulty
    question_counts = {}
    for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
        question_counts[product] = {}
        for difficulty in ['Easy', 'Intermediate', 'Expert']:
            count = await db.quiz_questions.count_documents({
                'product': product,
                'difficulty': difficulty
            })
            question_counts[product][difficulty] = count
    
    # Get overall attempt stats
    total_attempts = await db.quiz_attempts.count_documents({})
    passed_attempts = await db.quiz_attempts.count_documents({'passed': True})
    
    return {
        'question_counts': question_counts,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'pass_rate': (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
    }

# ==================== CLIENT PORTAL SYSTEM ====================

# Client Portal Pydantic Models
class PortalClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

class PortalClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class PortalClientResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None  # Optional for clients created from Book of Business
    phone: Optional[str] = None
    agent_id: str
    agent_name: Optional[str] = None
    status: str
    last_login_at: Optional[str] = None
    created_at: str

class PortalPolicyCreate(BaseModel):
    client_id: str
    carrier: str
    product_type: str  # IUL, Term, FIA, etc.
    policy_number: Optional[str] = None
    issue_date: Optional[str] = None
    face_amount: Optional[float] = None
    premium: Optional[float] = None  # Annual premium
    monthly_premium: Optional[float] = None  # Monthly premium
    status: str = "pending"  # active, pending, lapsed
    short_explanation: Optional[str] = None
    is_visible: bool = True

class PortalPolicyUpdate(BaseModel):
    carrier: Optional[str] = None
    product_type: Optional[str] = None
    policy_number: Optional[str] = None
    issue_date: Optional[str] = None
    face_amount: Optional[float] = None
    premium: Optional[float] = None
    monthly_premium: Optional[float] = None
    status: Optional[str] = None
    short_explanation: Optional[str] = None
    is_visible: Optional[bool] = None

class PortalPolicyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    agent_id: str
    carrier: str
    product_type: str
    policy_number: Optional[str] = None
    issue_date: Optional[str] = None
    face_amount: Optional[float] = None
    premium: Optional[float] = None
    monthly_premium: Optional[float] = None
    status: str
    short_explanation: Optional[str] = None
    is_visible: bool
    created_at: str

class ClientDocumentCreate(BaseModel):
    client_id: str
    policy_id: Optional[str] = None
    document_type: str  # policy, statement, illustration, other
    file_name: str
    is_visible: bool = True

class ClientDocumentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    policy_id: Optional[str] = None
    uploaded_by: str
    uploaded_by_name: Optional[str] = None
    document_type: str
    file_url: str
    file_name: str
    is_visible: bool
    created_at: str

class ClientInviteCreate(BaseModel):
    client_id: str

class ClientInviteResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    client_id: str
    agent_id: str
    invite_token: str
    expires_at: str
    accepted_at: Optional[str] = None
    created_at: str

class PortalSettingsUpdate(BaseModel):
    show_breeze_branding: Optional[bool] = None
    show_agent_branding: Optional[bool] = None
    global_disclaimer_text: Optional[str] = None
    allow_messaging: Optional[bool] = None
    allow_document_upload_by_agent: Optional[bool] = None
    allow_document_upload_by_client: Optional[bool] = None
    retention_policy_text: Optional[str] = None

class ClientLoginRequest(BaseModel):
    email: EmailStr
    password: str

# ==================== TICKETS SYSTEM ====================
class TicketCreate(BaseModel):
    ticket_type: str  # COMMISSION_CHANGE, HIERARCHY_MOVE, REINSTATEMENT
    affected_agent_id: str
    requested_upline_id: Optional[str] = None
    requested_commission_level: Optional[float] = None
    reason_text: str

class TicketUpdate(BaseModel):
    status: str  # UNDER_REVIEW, APPROVED, DENIED, RESOLVED
    admin_resolution_notes: Optional[str] = None
    final_upline_id: Optional[str] = None
    final_commission_level: Optional[float] = None

class TicketResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    ticket_type: str
    status: str
    submitted_by_user_id: str
    submitted_by_agent_name: str
    affected_agent_id: str
    affected_agent_name: str
    requested_upline_id: Optional[str] = None
    requested_upline_name: Optional[str] = None
    requested_commission_level: Optional[float] = None
    current_commission_level: Optional[float] = None
    current_upline_name: Optional[str] = None
    reason_text: str
    admin_resolution_notes: Optional[str] = None
    final_upline_id: Optional[str] = None
    final_commission_level: Optional[float] = None
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    resolved_by_admin_id: Optional[str] = None
    resolved_by_admin_name: Optional[str] = None


class ClientSetPasswordRequest(BaseModel):
    invite_token: str
    password: str

# Helper: Get current portal client from JWT
async def get_current_portal_client(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if this is a client token
        if payload.get('type') != 'portal_client':
            raise HTTPException(status_code=401, detail="Invalid client token")
        
        client = await db.portal_clients.find_one({'id': payload['client_id']}, {'_id': 0})
        if not client:
            raise HTTPException(status_code=401, detail="Client not found")
        if client.get('status') == 'inactive':
            raise HTTPException(status_code=403, detail="Account inactive")
        
        return client
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_client_jwt_token(client_id: str, email: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        'client_id': client_id,
        'email': email,
        'type': 'portal_client',
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Helper: Check if user is agent who owns the client or admin
async def verify_client_access(client_id: str, current_user: dict) -> dict:
    portal_client = await db.portal_clients.find_one({'id': client_id}, {'_id': 0})
    if not portal_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Admins can access any client
    if current_user['role'] == 'admin':
        return portal_client
    
    # Agents can only access their own clients
    if portal_client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Access denied to this client")
    
    return portal_client

# ==================== CLIENT PORTAL SETTINGS ====================

@api_router.get("/portal/settings")
async def get_portal_settings(current_user: dict = Depends(get_current_user)):
    """Get portal settings (Admin only)"""
    await require_role(current_user, ['admin'])
    
    settings = await db.client_portal_settings.find_one({}, {'_id': 0})
    if not settings:
        # Return defaults
        return {
            'show_breeze_branding': True,
            'show_agent_branding': True,
            'global_disclaimer_text': 'This portal is provided for informational purposes only. Please consult with your advisor for specific financial advice.',
            'allow_messaging': False,
            'allow_document_upload_by_agent': True,
            'allow_document_upload_by_client': False,
            'retention_policy_text': 'Documents are retained according to regulatory requirements.'
        }
    return settings

@api_router.put("/portal/settings")
async def update_portal_settings(data: PortalSettingsUpdate, current_user: dict = Depends(get_current_user)):
    """Update portal settings (Admin only)"""
    await require_role(current_user, ['admin'])
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    update_data['updated_by'] = current_user['id']
    
    await db.client_portal_settings.update_one(
        {},
        {'$set': update_data},
        upsert=True
    )
    
    # Audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='portal_settings_update',
        target_user_id='system',
        target_user_name='Portal Settings',
        details=update_data
    )
    
    return {'message': 'Portal settings updated successfully'}

# ==================== PORTAL CLIENT MANAGEMENT (AGENT) ====================

@api_router.post("/portal/clients", response_model=PortalClientResponse)
async def create_portal_client(data: PortalClientCreate, current_user: dict = Depends(get_current_user)):
    """Create a new portal client (Agent/Admin)"""
    # Check if email already exists
    existing = await db.portal_clients.find_one({'email': data.email})
    if existing:
        raise HTTPException(status_code=400, detail="A client with this email already exists")
    
    client_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    client_doc = {
        'id': client_id,
        'first_name': data.first_name,
        'last_name': data.last_name,
        'email': data.email,
        'phone': data.phone,
        'agent_id': current_user['id'],
        'agent_name': current_user['name'],
        'status': 'invited',  # invited, active, inactive
        'password_hash': None,
        'last_login_at': None,
        'created_at': now
    }
    
    await db.portal_clients.insert_one(client_doc)
    
    # Create audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='portal_client_created',
        target_user_id=client_id,
        target_user_name=f"{data.first_name} {data.last_name}",
        details={'email': data.email}
    )
    
    return PortalClientResponse(**client_doc)

@api_router.put("/portal/clients/{client_id}", response_model=PortalClientResponse)
async def update_portal_client(client_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update portal client information (Agent/Admin)"""
    # Verify access
    client = await db.portal_clients.find_one({'id': client_id}, {'_id': 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check permissions
    if current_user['role'] != 'admin' and client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this client")
    
    # Prepare updates
    updates = {}
    if 'first_name' in data:
        updates['first_name'] = data['first_name'].strip()
    if 'last_name' in data:
        updates['last_name'] = data['last_name'].strip()
    if 'email' in data:
        email = data['email'].strip().lower()
        # Check if email is already used by another client
        existing = await db.portal_clients.find_one({'email': email, 'id': {'$ne': client_id}})
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use by another client")
        updates['email'] = email
    if 'phone' in data:
        updates['phone'] = data['phone'].strip() if data['phone'] else None
    
    if updates:
        await db.portal_clients.update_one(
            {'id': client_id},
            {'$set': updates}
        )
        
        # Create audit log
        await create_audit_log(
            admin_id=current_user['id'],
            admin_name=current_user['name'],
            action='portal_client_updated',
            target_user_id=client_id,
            target_user_name=f"{updates.get('first_name', client['first_name'])} {updates.get('last_name', client['last_name'])}",
            details=updates
        )
    
    # Return updated client
    updated_client = await db.portal_clients.find_one({'id': client_id}, {'_id': 0, 'password_hash': 0})
    return PortalClientResponse(**updated_client)

@api_router.get("/portal/clients", response_model=List[PortalClientResponse])
async def get_portal_clients(current_user: dict = Depends(get_current_user)):
    """Get portal clients (Agent sees own, Admin sees all)"""
    if current_user['role'] == 'admin':
        clients = await db.portal_clients.find({}, {'_id': 0, 'password_hash': 0}).to_list(1000)
    else:
        clients = await db.portal_clients.find(
            {'agent_id': current_user['id']}, 
            {'_id': 0, 'password_hash': 0}
        ).to_list(1000)
    
    return [PortalClientResponse(**c) for c in clients]

@api_router.get("/portal/clients/{client_id}", response_model=PortalClientResponse)
async def get_portal_client(client_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific portal client"""
    portal_client = await verify_client_access(client_id, current_user)
    return PortalClientResponse(**portal_client)

@api_router.put("/portal/clients/{client_id}", response_model=PortalClientResponse)
async def update_portal_client(client_id: str, data: PortalClientUpdate, current_user: dict = Depends(get_current_user)):
    """Update a portal client"""
    portal_client = await verify_client_access(client_id, current_user)
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.portal_clients.update_one({'id': client_id}, {'$set': update_data})
    
    updated = await db.portal_clients.find_one({'id': client_id}, {'_id': 0, 'password_hash': 0})
    return PortalClientResponse(**updated)

@api_router.delete("/portal/clients/{client_id}")
async def delete_portal_client(client_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a portal client and all associated data"""
    portal_client = await verify_client_access(client_id, current_user)
    
    # Delete all associated data
    await db.portal_policies.delete_many({'client_id': client_id})
    await db.client_documents.delete_many({'client_id': client_id})
    await db.client_invites.delete_many({'client_id': client_id})
    await db.client_messages.delete_many({'client_id': client_id})
    await db.portal_clients.delete_one({'id': client_id})
    
    # Audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='portal_client_deleted',
        target_user_id=client_id,
        target_user_name=f"{portal_client['first_name']} {portal_client['last_name']}",
        details={'email': portal_client['email']}
    )
    
    return {'message': 'Client and all associated data deleted'}

# ==================== CLIENT INVITE SYSTEM ====================

@api_router.post("/portal/clients/{client_id}/invite", response_model=ClientInviteResponse)
async def create_client_invite(client_id: str, current_user: dict = Depends(get_current_user)):
    """Generate an invite link for a client"""
    portal_client = await verify_client_access(client_id, current_user)
    
    # Check if client already has an active account
    if portal_client.get('status') == 'active' and portal_client.get('password_hash'):
        raise HTTPException(status_code=400, detail="Client already has an active account")
    
    # Invalidate any existing pending invites
    await db.client_invites.update_many(
        {'client_id': client_id, 'accepted_at': None},
        {'$set': {'accepted_at': 'invalidated'}}
    )
    
    invite_id = str(uuid.uuid4())
    invite_token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)
    
    # Calculate annual review date (1 year from now)
    annual_review_date = (now + timedelta(days=365)).isoformat()
    
    invite_doc = {
        'id': invite_id,
        'client_id': client_id,
        'agent_id': current_user['id'],
        'invite_token': invite_token,
        'expires_at': expires_at.isoformat(),
        'accepted_at': None,
        'created_at': now.isoformat()
    }
    
    await db.client_invites.insert_one(invite_doc)
    
    # Update client status and set annual review date
    await db.portal_clients.update_one(
        {'id': client_id},
        {'$set': {
            'status': 'invited',
            'annual_review_date': annual_review_date,
            'invite_sent_at': now.isoformat()
        }}
    )
    
    # Audit log
    await create_audit_log(
        admin_id=current_user['id'],
        admin_name=current_user['name'],
        action='portal_invite_sent',
        target_user_id=client_id,
        target_user_name=f"{portal_client['first_name']} {portal_client['last_name']}",
        details={'invite_id': invite_id}
    )
    
    return ClientInviteResponse(**invite_doc)

@api_router.post("/portal/clients/{client_id}/send-invite-email")
async def send_client_invite_email_endpoint(client_id: str, current_user: dict = Depends(get_current_user)):
    """Send client portal invite via email"""
    from email_service import send_client_portal_invite_email
    
    # Verify access
    portal_client = await verify_client_access(client_id, current_user)
    
    # Check if client has email
    if not portal_client.get('email'):
        raise HTTPException(status_code=400, detail="Client does not have an email address")
    
    # Get or create invite
    existing_invite = await db.client_invites.find_one(
        {'client_id': client_id, 'accepted_at': None},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    if not existing_invite:
        # Create new invite if none exists
        invite_id = str(uuid.uuid4())
        invite_token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)
        
        invite_doc = {
            'id': invite_id,
            'client_id': client_id,
            'agent_id': current_user['id'],
            'invite_token': invite_token,
            'expires_at': expires_at.isoformat(),
            'accepted_at': None,
            'created_at': now.isoformat()
        }
        
        await db.client_invites.insert_one(invite_doc)
        existing_invite = invite_doc
    
    # Build portal link
    base_url = os.environ.get('APP_DOMAIN', 'https://breezeatlas.com')
    portal_link = f"{base_url}/client-portal/setup/{existing_invite['invite_token']}"
    
    # Get agent info for email
    agent_name = current_user.get('name', 'Your Agent')
    client_name = portal_client.get('first_name', 'Valued Client')
    
    # Send email
    try:
        result = await send_client_portal_invite_email(
            to=portal_client['email'],
            client_name=client_name,
            agent_name=agent_name,
            portal_link=portal_link
        )
        
        if result.get('status') == 'success':
            # Update client record
            await db.portal_clients.update_one(
                {'id': client_id},
                {'$set': {
                    'status': 'invited',
                    'invite_sent_at': datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Audit log
            await create_audit_log(
                admin_id=current_user['id'],
                admin_name=current_user['name'],
                action='portal_invite_emailed',
                target_user_id=client_id,
                target_user_name=f"{portal_client['first_name']} {portal_client['last_name']}",
                details={'email': portal_client['email'], 'invite_id': existing_invite['id']}
            )
            
            return {
                'success': True,
                'message': f"Invite email sent to {portal_client['email']}",
                'invite_id': existing_invite['id']
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {result.get('message')}")
    except Exception as e:
        logger.error(f"Error sending client invite email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@api_router.get("/portal/invite/validate/{token}")
async def validate_client_invite(token: str):
    """Validate a client invite token (public endpoint)"""
    invite = await db.client_invites.find_one(
        {'invite_token': token, 'accepted_at': None},
        {'_id': 0}
    )
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or used invite token")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite token expired")
    
    # Get client info
    portal_client = await db.portal_clients.find_one({'id': invite['client_id']}, {'_id': 0})
    if not portal_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get agent info
    agent = await db.users.find_one({'id': invite['agent_id']}, {'_id': 0, 'password_hash': 0})
    
    return {
        'valid': True,
        'client_email': portal_client['email'],
        'client_first_name': portal_client['first_name'],
        'client_last_name': portal_client['last_name'],
        'agent_name': agent['name'] if agent else 'Your Advisor',
        'agent_email': agent['email'] if agent else None,
        'agent_phone': agent.get('phone') if agent else None
    }

@api_router.post("/portal/auth/set-password")
async def client_set_password(data: ClientSetPasswordRequest):
    """Set password for client (first-time login)"""
    invite = await db.client_invites.find_one(
        {'invite_token': data.invite_token, 'accepted_at': None},
        {'_id': 0}
    )
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or used invite token")
    
    expires_at = datetime.fromisoformat(invite['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite token expired")
    
    # Get client
    portal_client = await db.portal_clients.find_one({'id': invite['client_id']}, {'_id': 0})
    if not portal_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Hash password and update client
    password_hash = hash_password(data.password)
    now = datetime.now(timezone.utc).isoformat()
    
    await db.portal_clients.update_one(
        {'id': invite['client_id']},
        {'$set': {
            'password_hash': password_hash,
            'status': 'active',
            'last_login_at': now
        }}
    )
    
    # Mark invite as accepted
    await db.client_invites.update_one(
        {'id': invite['id']},
        {'$set': {'accepted_at': now}}
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=invite['agent_id'],
        admin_name='System',
        action='portal_invite_accepted',
        target_user_id=invite['client_id'],
        target_user_name=f"{portal_client['first_name']} {portal_client['last_name']}",
        details={'email': portal_client['email']}
    )
    
    # Generate token
    token = create_client_jwt_token(invite['client_id'], portal_client['email'])
    
    return {
        'token': token,
        'client': {
            'id': portal_client['id'],
            'first_name': portal_client['first_name'],
            'last_name': portal_client['last_name'],
            'email': portal_client['email']
        }
    }

@api_router.post("/portal/auth/login")
async def client_login(data: ClientLoginRequest):
    """Client login to portal"""
    portal_client = await db.portal_clients.find_one({'email': data.email}, {'_id': 0})
    if not portal_client:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not portal_client.get('password_hash'):
        raise HTTPException(status_code=401, detail="Account not activated. Please use your invite link.")
    
    if portal_client.get('status') == 'inactive':
        raise HTTPException(status_code=403, detail="Account is inactive. Please contact your advisor.")
    
    if not verify_password(data.password, portal_client['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    now = datetime.now(timezone.utc).isoformat()
    await db.portal_clients.update_one(
        {'id': portal_client['id']},
        {'$set': {'last_login_at': now}}
    )
    
    # Generate token
    token = create_client_jwt_token(portal_client['id'], portal_client['email'])
    
    # Get agent info for response
    agent = await db.users.find_one({'id': portal_client['agent_id']}, {'_id': 0, 'password_hash': 0})
    
    return {
        'token': token,
        'client': {
            'id': portal_client['id'],
            'first_name': portal_client['first_name'],
            'last_name': portal_client['last_name'],
            'email': portal_client['email'],
            'agent_name': agent['name'] if agent else None
        }
    }

@api_router.get("/portal/auth/me")
async def get_current_client(portal_client: dict = Depends(get_current_portal_client)):
    """Get current logged-in client info"""
    # Get agent info
    agent = await db.users.find_one({'id': portal_client['agent_id']}, {'_id': 0, 'password_hash': 0})
    
    return {
        'id': portal_client['id'],
        'first_name': portal_client['first_name'],
        'last_name': portal_client['last_name'],
        'email': portal_client['email'],
        'phone': portal_client.get('phone'),
        'agent': {
            'id': agent['id'] if agent else None,
            'name': agent['name'] if agent else 'Your Advisor',
            'email': agent.get('email') if agent else None,
            'phone': agent.get('phone') if agent else None,
            'profile_picture': agent.get('profile_picture') if agent else None
        } if agent else None
    }

# ==================== PORTAL POLICIES ====================

@api_router.post("/portal/policies", response_model=PortalPolicyResponse)
async def create_portal_policy(data: PortalPolicyCreate, current_user: dict = Depends(get_current_user)):
    """Create a policy for a portal client (Agent/Admin)"""
    # Verify access to client
    await verify_client_access(data.client_id, current_user)
    
    policy_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    policy_doc = {
        'id': policy_id,
        'client_id': data.client_id,
        'agent_id': current_user['id'],
        'carrier': data.carrier,
        'product_type': data.product_type,
        'policy_number': data.policy_number,
        'issue_date': data.issue_date,
        'face_amount': data.face_amount,
        'premium': data.premium,
        'monthly_premium': data.monthly_premium,
        'status': data.status,
        'short_explanation': data.short_explanation,
        'is_visible': data.is_visible,
        'created_at': now
    }
    
    await db.portal_policies.insert_one(policy_doc)
    return PortalPolicyResponse(**policy_doc)

@api_router.get("/portal/policies/client/{client_id}", response_model=List[PortalPolicyResponse])
async def get_client_policies(client_id: str, current_user: dict = Depends(get_current_user)):
    """Get all policies for a client (Agent/Admin)"""
    await verify_client_access(client_id, current_user)
    
    policies = await db.portal_policies.find({'client_id': client_id}, {'_id': 0}).to_list(100)
    return [PortalPolicyResponse(**p) for p in policies]

@api_router.get("/portal/my-policies", response_model=List[PortalPolicyResponse])
async def get_my_policies(portal_client: dict = Depends(get_current_portal_client)):
    """Client: Get my visible policies"""
    policies = await db.portal_policies.find(
        {'client_id': portal_client['id'], 'is_visible': True},
        {'_id': 0}
    ).to_list(100)
    return [PortalPolicyResponse(**p) for p in policies]

@api_router.put("/portal/policies/{policy_id}", response_model=PortalPolicyResponse)
async def update_portal_policy(policy_id: str, data: PortalPolicyUpdate, current_user: dict = Depends(get_current_user)):
    """Update a policy (Agent/Admin)"""
    policy = await db.portal_policies.find_one({'id': policy_id}, {'_id': 0})
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    await verify_client_access(policy['client_id'], current_user)
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.portal_policies.update_one({'id': policy_id}, {'$set': update_data})
    
    updated = await db.portal_policies.find_one({'id': policy_id}, {'_id': 0})
    return PortalPolicyResponse(**updated)

@api_router.delete("/portal/policies/{policy_id}")
async def delete_portal_policy(policy_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a policy (Agent/Admin)"""
    policy = await db.portal_policies.find_one({'id': policy_id}, {'_id': 0})
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    await verify_client_access(policy['client_id'], current_user)
    
    await db.portal_policies.delete_one({'id': policy_id})
    return {'message': 'Policy deleted'}

# ==================== CLIENT DOCUMENTS ====================

import base64
import aiofiles

# Create uploads directory
UPLOADS_DIR = ROOT_DIR / 'uploads' / 'client_documents'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@api_router.post("/portal/documents/upload")
async def upload_client_document(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Upload a document for a client (Agent/Admin)"""
    client_id = data.get('client_id')
    file_data = data.get('file_data')  # Base64 encoded
    file_name = data.get('file_name')
    document_type = data.get('document_type', 'other')
    policy_id = data.get('policy_id')
    is_visible = data.get('is_visible', True)
    
    if not client_id or not file_data or not file_name:
        raise HTTPException(status_code=400, detail="client_id, file_data, and file_name are required")
    
    await verify_client_access(client_id, current_user)
    
    # Decode and save file
    try:
        file_bytes = base64.b64decode(file_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 file data")
    
    # Generate secure filename
    doc_id = str(uuid.uuid4())
    ext = file_name.split('.')[-1] if '.' in file_name else 'pdf'
    secure_filename = f"{doc_id}.{ext}"
    file_path = UPLOADS_DIR / secure_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_bytes)
    
    now = datetime.now(timezone.utc).isoformat()
    
    doc_record = {
        'id': doc_id,
        'client_id': client_id,
        'policy_id': policy_id,
        'uploaded_by': current_user['id'],
        'uploaded_by_name': current_user['name'],
        'document_type': document_type,
        'file_url': secure_filename,  # Relative path for security
        'file_name': file_name,
        'is_visible': is_visible,
        'created_at': now
    }
    
    await db.client_documents.insert_one(doc_record)
    
    return ClientDocumentResponse(**doc_record)

@api_router.post("/portal/clients/{client_id}/documents")
async def upload_client_document_multipart(
    client_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("Policy"),
    file_name: str = Form(None),
    policy_id: str = Form(None),
    is_visible: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document for a client via multipart form (Agent/Admin)"""
    await verify_client_access(client_id, current_user)
    
    # Read file content
    file_content = await file.read()
    
    # Use provided filename or original filename
    actual_filename = file_name or file.filename
    
    # Generate secure filename
    doc_id = str(uuid.uuid4())
    ext = actual_filename.split('.')[-1] if '.' in actual_filename else 'pdf'
    secure_filename = f"{doc_id}.{ext}"
    file_path = UPLOADS_DIR / secure_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    now = datetime.now(timezone.utc).isoformat()
    
    doc_record = {
        'id': doc_id,
        'client_id': client_id,
        'policy_id': policy_id,
        'uploaded_by': current_user['id'],
        'uploaded_by_name': current_user['name'],
        'document_type': document_type,
        'file_url': secure_filename,
        'file_name': actual_filename,
        'is_visible': is_visible,
        'created_at': now
    }
    
    await db.client_documents.insert_one(doc_record)
    
    return ClientDocumentResponse(**doc_record)

@api_router.get("/portal/documents/client/{client_id}", response_model=List[ClientDocumentResponse])
async def get_client_documents(client_id: str, current_user: dict = Depends(get_current_user)):
    """Get all documents for a client (Agent/Admin)"""
    await verify_client_access(client_id, current_user)
    
    documents = await db.client_documents.find({'client_id': client_id}, {'_id': 0}).to_list(100)
    return [ClientDocumentResponse(**d) for d in documents]

@api_router.get("/portal/my-documents", response_model=List[ClientDocumentResponse])
async def get_my_documents(portal_client: dict = Depends(get_current_portal_client)):
    """Client: Get my visible documents"""
    documents = await db.client_documents.find(
        {'client_id': portal_client['id'], 'is_visible': True},
        {'_id': 0}
    ).to_list(100)
    return [ClientDocumentResponse(**d) for d in documents]

@api_router.get("/portal/documents/download/{doc_id}")
async def download_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Download a document (Agent/Admin)"""
    from fastapi.responses import FileResponse
    
    doc = await db.client_documents.find_one({'id': doc_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await verify_client_access(doc['client_id'], current_user)
    
    file_path = UPLOADS_DIR / doc['file_url']
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=doc['file_name'],
        media_type='application/octet-stream'
    )

@api_router.get("/portal/my-documents/download/{doc_id}")
async def client_download_document(doc_id: str, portal_client: dict = Depends(get_current_portal_client)):
    """Client: Download my document"""
    from fastapi.responses import FileResponse
    
    doc = await db.client_documents.find_one(
        {'id': doc_id, 'client_id': portal_client['id'], 'is_visible': True},
        {'_id': 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = UPLOADS_DIR / doc['file_url']
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=doc['file_name'],
        media_type='application/octet-stream'
    )

@api_router.put("/portal/documents/{doc_id}")
async def update_document_visibility(doc_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update document visibility (Agent/Admin)"""
    doc = await db.client_documents.find_one({'id': doc_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await verify_client_access(doc['client_id'], current_user)
    
    is_visible = data.get('is_visible')
    if is_visible is None:
        raise HTTPException(status_code=400, detail="is_visible field required")
    
    await db.client_documents.update_one(
        {'id': doc_id},
        {'$set': {'is_visible': is_visible, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    return {'message': 'Document visibility updated'}

@api_router.delete("/portal/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document (Agent/Admin)"""
    doc = await db.client_documents.find_one({'id': doc_id}, {'_id': 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await verify_client_access(doc['client_id'], current_user)
    
    # Delete file
    file_path = UPLOADS_DIR / doc['file_url']
    if file_path.exists():
        file_path.unlink()
    
    await db.client_documents.delete_one({'id': doc_id})
    return {'message': 'Document deleted'}

# ==================== PORTAL METRICS (ADMIN) ====================

@api_router.get("/portal/metrics")
async def get_portal_metrics(current_user: dict = Depends(get_current_user)):
    """Get portal metrics (Admin only)"""
    await require_role(current_user, ['admin'])
    
    total_clients = await db.portal_clients.count_documents({})
    active_clients = await db.portal_clients.count_documents({'status': 'active'})
    invited_clients = await db.portal_clients.count_documents({'status': 'invited'})
    
    # Login activity in last 30 days
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_logins = await db.portal_clients.count_documents({
        'last_login_at': {'$gte': thirty_days_ago}
    })
    
    # Policies count
    total_policies = await db.portal_policies.count_documents({})
    active_policies = await db.portal_policies.count_documents({'status': 'active'})
    
    # Documents count
    total_documents = await db.client_documents.count_documents({})
    
    return {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'invited_clients': invited_clients,
        'recent_logins_30d': recent_logins,
        'total_policies': total_policies,
        'active_policies': active_policies,
        'total_documents': total_documents
    }

# ==================== CLIENT DASHBOARD DATA ====================

@api_router.get("/portal/dashboard")
async def get_client_dashboard(portal_client: dict = Depends(get_current_portal_client)):
    """Get client dashboard data"""
    client_id = portal_client['id']
    
    # Get agent info
    agent = await db.users.find_one({'id': portal_client['agent_id']}, {'_id': 0, 'password_hash': 0})
    
    # Get visible policies
    policies = await db.portal_policies.find(
        {'client_id': client_id, 'is_visible': True},
        {'_id': 0}
    ).to_list(100)
    
    # Get visible documents
    documents = await db.client_documents.find(
        {'client_id': client_id, 'is_visible': True},
        {'_id': 0}
    ).to_list(100)
    
    # Get portal settings
    settings = await db.client_portal_settings.find_one({}, {'_id': 0})
    if not settings:
        settings = {
            'show_breeze_branding': True,
            'show_agent_branding': True,
            'global_disclaimer_text': 'This portal is provided for informational purposes only.',
            'allow_messaging': False
        }
    
    # Calculate important dates
    important_dates = []
    
    # Add annual review date if set
    if portal_client.get('annual_review_date'):
        important_dates.append({
            'type': 'annual_review',
            'date': portal_client['annual_review_date'][:10],  # Just date part
            'description': 'Annual Policy Review',
            'is_review': True
        })
    
    for policy in policies:
        if policy.get('issue_date'):
            try:
                issue_date = datetime.fromisoformat(policy['issue_date'])
                # Calculate next anniversary
                today = datetime.now(timezone.utc).date()
                this_year_anniversary = issue_date.replace(year=today.year).date()
                if this_year_anniversary < today:
                    next_anniversary = issue_date.replace(year=today.year + 1).date()
                else:
                    next_anniversary = this_year_anniversary
                
                important_dates.append({
                    'type': 'anniversary',
                    'date': next_anniversary.isoformat(),
                    'description': f"{policy['carrier']} {policy['product_type']} Anniversary",
                    'policy_id': policy['id']
                })
            except Exception:
                pass
    
    # Sort important dates
    important_dates.sort(key=lambda x: x['date'])
    
    return {
        'client': {
            'id': portal_client['id'],
            'first_name': portal_client['first_name'],
            'last_name': portal_client['last_name'],
            'email': portal_client['email']
        },
        'advisor': {
            'id': agent['id'] if agent else None,
            'name': agent['name'] if agent else 'Your Advisor',
            'email': agent.get('email') if agent else None,
            'phone': agent.get('phone') if agent else None,
            'npn': agent.get('npn') if agent else None,
            'profile_picture': agent.get('profile_picture') if agent else None
        } if agent else None,
        'policies': policies,
        'documents': documents,
        'important_dates': important_dates[:5],  # Top 5 upcoming dates
        'settings': settings
    }

# ==================== BOOK OF BUSINESS INTEGRATION ====================

@api_router.post("/portal/clients/from-book/{client_id}")
async def create_portal_client_from_book(client_id: str, current_user: dict = Depends(get_current_user)):
    """Create a portal client from existing Book of Business client"""
    # Get the book of business client
    book_client = await db.clients.find_one({'id': client_id}, {'_id': 0})
    if not book_client:
        raise HTTPException(status_code=404, detail="Client not found in Book of Business")
    
    # Verify ownership
    if current_user['role'] != 'admin' and book_client['agent_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to access this client")
    
    # Check if portal client with same name already exists for this agent
    existing = await db.portal_clients.find_one({
        'first_name': book_client['first_name'],
        'last_name': book_client['last_name'],
        'agent_id': book_client['agent_id']
    })
    
    if existing:
        # Return existing client
        return {
            'portal_client': PortalClientResponse(**existing),
            'is_new': False,
            'message': 'Client already exists in portal'
        }
    
    # Create new portal client (email will need to be provided)
    portal_client_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    portal_client_doc = {
        'id': portal_client_id,
        'first_name': book_client['first_name'],
        'last_name': book_client['last_name'],
        'email': None,  # Will be set when invite is created
        'phone': None,
        'agent_id': book_client['agent_id'],
        'agent_name': book_client.get('agent_name') or current_user['name'],
        'status': 'pending',  # Pending until email is provided
        'password_hash': None,
        'last_login_at': None,
        'created_at': now,
        'book_client_id': client_id  # Link to book of business
    }
    
    await db.portal_clients.insert_one(portal_client_doc)
    
    # Create initial policy from book of business data
    policy_doc = {
        'id': str(uuid.uuid4()),
        'client_id': portal_client_id,
        'agent_id': book_client['agent_id'],
        'carrier': book_client.get('carrier', 'Unknown'),
        'product_type': book_client.get('product_type', 'Unknown'),
        'policy_number': book_client.get('policy_number'),
        'issue_date': book_client.get('date_issued'),
        'face_amount': book_client.get('face_amount') or book_client.get('coverage_amount'),
        'premium': book_client.get('annual_premium') or book_client.get('premium') or (book_client.get('monthly_premium', 0) * 12 if book_client.get('monthly_premium') else None),
        'monthly_premium': book_client.get('monthly_premium'),
        'status': 'active' if book_client.get('status') == 'Issued' else 'pending',
        'short_explanation': book_client.get('client_why'),
        'is_visible': True,
        'created_at': now
    }
    
    await db.portal_policies.insert_one(policy_doc)
    
    return {
        'portal_client': PortalClientResponse(**portal_client_doc),
        'policy': PortalPolicyResponse(**policy_doc),
        'is_new': True,
        'message': 'Portal client created. Please provide email to send invite.'
    }

@api_router.put("/portal/clients/{client_id}/email")
async def set_portal_client_email(client_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Set email for a portal client and optionally send invite"""
    portal_client = await verify_client_access(client_id, current_user)
    
    email = data.get('email')
    send_invite = data.get('send_invite', False)
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Check if email already in use
    existing = await db.portal_clients.find_one({'email': email, 'id': {'$ne': client_id}})
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use by another client")
    
    # Update email
    await db.portal_clients.update_one(
        {'id': client_id},
        {'$set': {'email': email, 'status': 'invited' if send_invite else 'pending'}}
    )
    
    result = {'message': 'Email updated successfully'}
    
    if send_invite:
        # Create invite
        invite_id = str(uuid.uuid4())
        invite_token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)
        
        invite_doc = {
            'id': invite_id,
            'client_id': client_id,
            'agent_id': current_user['id'],
            'invite_token': invite_token,
            'expires_at': expires_at.isoformat(),
            'accepted_at': None,
            'created_at': now.isoformat()
        }
        
        await db.client_invites.insert_one(invite_doc)
        
        result['invite'] = ClientInviteResponse(**invite_doc)
        result['message'] = 'Email updated and invite created'
    
    return result

# Routes and middleware moved after all endpoint definitions

@app.on_event("startup")
async def startup_db():
    # Set the database instance for atlas_ai_service
    set_atlas_db(db)
    
    set_zinnia_db(db)
    asyncio.create_task(start_scheduler(interval_minutes=180))
    
    admin_exists = await db.users.find_one({'email': 'kyle@breezewealthmanagement.com'})
    if not admin_exists:
        admin_id = str(uuid.uuid4())
        admin_doc = {
            'id': admin_id,
            'email': 'kyle@breezewealthmanagement.com',
            'name': 'Kyle Admin',
            'password_hash': hash_password('Breeze2026!'),
            'role': 'admin',
            'npn': None,
            'comp_percentage': 100.0,
            'upline_id': None,
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'needs_password_reset': True
        }
        await db.users.insert_one(admin_doc)
        logger.info("Admin account created: kyle@breezewealthmanagement.com")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# ==================== TICKETS SYSTEM ====================

@api_router.post("/tickets", response_model=TicketResponse)
async def create_ticket(data: TicketCreate, current_user: dict = Depends(get_current_user)):
    """Submit a new ticket (Agent/Leader access)"""
    
    # Validate ticket type
    valid_types = ['COMMISSION_CHANGE', 'HIERARCHY_MOVE', 'REINSTATEMENT']
    if data.ticket_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid ticket type. Must be one of: {', '.join(valid_types)}")
    
    # Get affected agent info
    affected_agent = await db.users.find_one({'id': data.affected_agent_id}, {'_id': 0})
    if not affected_agent:
        raise HTTPException(status_code=404, detail="Affected agent not found")
    
    # Validate hierarchy move - requested upline must have higher commission
    if data.ticket_type == 'HIERARCHY_MOVE' and data.requested_upline_id:
        requested_upline = await db.users.find_one({'id': data.requested_upline_id}, {'_id': 0})
        if not requested_upline:
            raise HTTPException(status_code=404, detail="Requested upline not found")
        
        if requested_upline.get('comp_percentage', 0) <= affected_agent.get('comp_percentage', 0):
            raise HTTPException(
                status_code=400, 
                detail="Requested upline must have higher commission than the agent being moved"
            )
    
    # Create ticket
    ticket_id = str(uuid4())
    ticket_doc = {
        'id': ticket_id,
        'ticket_type': data.ticket_type,
        'status': 'SUBMITTED',
        'submitted_by_user_id': current_user['id'],
        'submitted_by_agent_name': current_user['name'],
        'affected_agent_id': data.affected_agent_id,
        'affected_agent_name': affected_agent['name'],
        'requested_upline_id': data.requested_upline_id,
        'requested_commission_level': data.requested_commission_level,
        'current_commission_level': affected_agent.get('comp_percentage'),
        'current_upline_id': affected_agent.get('upline_id'),
        'reason_text': data.reason_text,
        'admin_resolution_notes': None,
        'final_upline_id': None,
        'final_commission_level': None,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'resolved_at': None,
        'resolved_by_admin_id': None
    }
    
    # Get requested upline name if provided
    if data.requested_upline_id:
        upline = await db.users.find_one({'id': data.requested_upline_id}, {'_id': 0})
        ticket_doc['requested_upline_name'] = upline['name'] if upline else None
    
    # Get current upline name
    if affected_agent.get('upline_id'):
        current_upline = await db.users.find_one({'id': affected_agent['upline_id']}, {'_id': 0})
        ticket_doc['current_upline_name'] = current_upline['name'] if current_upline else None
    
    await db.tickets.insert_one(ticket_doc)
    
    # Create audit log
    await db.ticket_audit_logs.insert_one({
        'id': str(uuid4()),
        'ticket_id': ticket_id,
        'action': 'SUBMITTED',
        'performed_by_user_id': current_user['id'],
        'performed_by_name': current_user['name'],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'notes': None
    })
    
    # Send notification to all admins about new ticket
    try:
        admins = await db.users.find({'role': 'admin', 'status': 'active'}, {'_id': 0}).to_list(100)
        admin_emails = [admin['email'] for admin in admins if admin.get('email')]
        if admin_emails:
            await send_admin_ticket_notification(
                admin_emails=admin_emails,
                ticket_id=ticket_id,
                ticket_type=data.ticket_type,
                submitter_name=current_user['name'],
                submitter_email=current_user.get('email', ''),
                affected_agent_name=affected_agent['name'],
                reason=data.reason_text or ''
            )
            logger.info(f"Sent ticket notification to {len(admin_emails)} admins")
    except Exception as e:
        logger.error(f"Failed to send admin ticket notification: {e}")
    
    return TicketResponse(**ticket_doc)

@api_router.get("/tickets", response_model=List[TicketResponse])
async def get_tickets(
    status: Optional[str] = None,
    ticket_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get tickets (role-based access)"""
    
    query = {}
    
    # Agents can only see their own tickets
    if current_user['role'] != 'admin':
        query['submitted_by_user_id'] = current_user['id']
    
    # Apply filters
    if status:
        query['status'] = status
    if ticket_type:
        query['ticket_type'] = ticket_type
    
    tickets = await db.tickets.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
    return [TicketResponse(**t) for t in tickets]

@api_router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, current_user: dict = Depends(get_current_user)):
    """Get ticket detail"""
    
    ticket = await db.tickets.find_one({'id': ticket_id}, {'_id': 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Agents can only view their own tickets
    if current_user['role'] != 'admin' and ticket['submitted_by_user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    return TicketResponse(**ticket)

@api_router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str, 
    data: TicketUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Update ticket status (Admin only)"""
    await require_role(current_user, ['admin'])
    
    ticket = await db.tickets.find_one({'id': ticket_id}, {'_id': 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Validate status transition
    valid_statuses = ['UNDER_REVIEW', 'APPROVED', 'DENIED', 'RESOLVED']
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    # Resolution notes required for DENIED or RESOLVED
    if data.status in ['DENIED', 'RESOLVED'] and not data.admin_resolution_notes:
        raise HTTPException(status_code=400, detail="Resolution notes required for DENIED or RESOLVED status")
    
    update_data = {
        'status': data.status,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    if data.admin_resolution_notes:
        update_data['admin_resolution_notes'] = data.admin_resolution_notes
    
    # If RESOLVED, apply the changes
    if data.status == 'RESOLVED':
        update_data['resolved_at'] = datetime.now(timezone.utc).isoformat()
        update_data['resolved_by_admin_id'] = current_user['id']
        update_data['resolved_by_admin_name'] = current_user['name']
        
        # Apply commission change
        if data.final_commission_level is not None:
            update_data['final_commission_level'] = data.final_commission_level
            
            # Update affected agent's commission (except for admins)
            affected_agent = await db.users.find_one({'id': ticket['affected_agent_id']}, {'_id': 0})
            if affected_agent and affected_agent.get('role') != 'admin':
                await db.users.update_one(
                    {'id': ticket['affected_agent_id']},
                    {'$set': {'comp_percentage': data.final_commission_level}}
                )
        
        # Apply hierarchy move
        if data.final_upline_id:
            update_data['final_upline_id'] = data.final_upline_id
            await db.users.update_one(
                {'id': ticket['affected_agent_id']},
                {'$set': {'upline_id': data.final_upline_id}}
            )
    
    await db.tickets.update_one({'id': ticket_id}, {'$set': update_data})
    
    # Create audit log
    await db.ticket_audit_logs.insert_one({
        'id': str(uuid4()),
        'ticket_id': ticket_id,
        'action': data.status,
        'performed_by_user_id': current_user['id'],
        'performed_by_name': current_user['name'],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'notes': data.admin_resolution_notes
    })
    
    # Send ticket status update email to submitter
    try:
        submitter = await db.users.find_one({'id': ticket['submitted_by_user_id']}, {'_id': 0})
        if submitter and submitter.get('email'):
            await send_ticket_status_email(
                to=submitter['email'],
                recipient_name=submitter['name'],
                ticket_id=ticket_id,
                ticket_type=ticket['ticket_type'],
                old_status=ticket['status'],
                new_status=data.status,
                affected_agent_name=ticket['affected_agent_name'],
                resolution_notes=data.admin_resolution_notes
            )
            logger.info(f"Sent ticket status update email to {submitter['email']}")
    except Exception as e:
        logger.error(f"Failed to send ticket status update email: {e}")
    
    return {'success': True, 'message': f'Ticket {data.status.lower()}'}

# ==================== ATLAS AI ENDPOINTS ====================

class KnowledgeBaseDocument(BaseModel):
    """Schema for knowledge base documents"""
    id: Optional[str] = None
    title: str
    category: str  # onboarding, sales, product, recruiting, operations, general
    content: str
    tags: List[str] = []
    created_at: Optional[str] = None
    created_by_user_id: Optional[str] = None
    updated_at: Optional[str] = None

class ChatMessage(BaseModel):
    """Schema for chat messages"""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str
    session_id: str

# Knowledge Base - Get all documents (all users can view)
@api_router.get("/atlas-ai/knowledge-base")
async def get_knowledge_base(current_user: dict = Depends(get_current_user)):
    """Get all knowledge base documents"""
    documents = await db.atlas_knowledge_base.find({}, {'_id': 0}).to_list(length=1000)
    return documents

# Knowledge Base - Add document (admin only)
@api_router.post("/atlas-ai/knowledge-base")
async def add_knowledge_document(doc: KnowledgeBaseDocument, current_user: dict = Depends(get_current_user)):
    """Add a new knowledge base document (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can add knowledge base documents")
    
    doc_dict = doc.model_dump()
    doc_dict['id'] = str(uuid4())
    doc_dict['created_at'] = datetime.now(timezone.utc).isoformat()
    doc_dict['created_by_user_id'] = current_user['id']
    doc_dict['updated_at'] = doc_dict['created_at']
    
    await db.atlas_knowledge_base.insert_one(doc_dict)
    
    return {'success': True, 'document': {k: v for k, v in doc_dict.items() if k != '_id'}}

# Knowledge Base - Update document (admin only)
@api_router.put("/atlas-ai/knowledge-base/{doc_id}")
async def update_knowledge_document(doc_id: str, doc: KnowledgeBaseDocument, current_user: dict = Depends(get_current_user)):
    """Update a knowledge base document (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update knowledge base documents")
    
    existing = await db.atlas_knowledge_base.find_one({'id': doc_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = {
        'title': doc.title,
        'category': doc.category,
        'content': doc.content,
        'tags': doc.tags,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.atlas_knowledge_base.update_one({'id': doc_id}, {'$set': update_data})
    
    return {'success': True, 'message': 'Document updated'}

# Knowledge Base - Delete document (admin only)
@api_router.delete("/atlas-ai/knowledge-base/{doc_id}")
async def delete_knowledge_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a knowledge base document (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can delete knowledge base documents")
    
    result = await db.atlas_knowledge_base.delete_one({'id': doc_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {'success': True, 'message': 'Document deleted'}

# Atlas AI Chat endpoint
@api_router.post("/atlas-ai/chat", response_model=ChatResponse)
async def atlas_ai_chat(chat: ChatMessage, current_user: dict = Depends(get_current_user)):
    """Chat with Atlas AI - Enhanced with better error handling"""
    try:
        # Validate input
        if not chat.message or not chat.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate a session ID if not provided
        session_id = chat.session_id or str(uuid4())
        
        # Retrieve relevant knowledge base content based on simple keyword matching
        user_message_lower = chat.message.lower()
        
        # Search knowledge base for relevant documents
        try:
            all_docs = await db.atlas_knowledge_base.find({}, {'_id': 0}).to_list(length=100)
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge base: {e}")
            all_docs = []
        
        relevant_docs = []
        for doc in all_docs:
            try:
                # Check if any keywords from the message appear in the document
                doc_text = f"{doc.get('title', '')} {doc.get('content', '')} {' '.join(doc.get('tags', []))}".lower()
                
                # Simple relevance scoring based on keyword overlap
                message_words = set(user_message_lower.split())
                doc_words = set(doc_text.split())
                overlap = len(message_words.intersection(doc_words))
                
                if overlap > 0:
                    relevant_docs.append((overlap, doc))
            except Exception as e:
                logger.error(f"Error processing document {doc.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by relevance and take top 5
        relevant_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for _, doc in relevant_docs[:5]]
        
        # Build knowledge context
        knowledge_context = ""
        if top_docs:
            try:
                knowledge_context = "\n\n".join([
                    f"### {doc.get('title', 'Untitled')} ({doc.get('category', 'general')})\n{doc.get('content', '')}"
                    for doc in top_docs
                ])
            except Exception as e:
                logger.error(f"Error building knowledge context: {e}")
                knowledge_context = ""
        
        try:
            # Get response from Atlas AI
            response = await get_atlas_ai_response(
                user_message=chat.message,
                knowledge_context=knowledge_context,
                session_id=session_id
            )
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                raise ValueError("Invalid response from AI service")
            
            return ChatResponse(response=response, session_id=session_id)
            
        except asyncio.TimeoutError:
            logger.error(f"Atlas AI timeout for session {session_id}")
            raise HTTPException(status_code=504, detail="Request timeout. Please try again.")
        except Exception as e:
            logger.error(f"Atlas AI processing error: {e}")
            raise HTTPException(status_code=500, detail="Failed to process your request. Please try again.")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in atlas_ai_chat: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")

# Knowledge Base - Upload document file (admin only)
ALLOWED_FILE_TYPES = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xlsx',
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/webp': 'webp'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@api_router.post("/atlas-ai/knowledge-base/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),  # Comma-separated tags
    carrier: str = Form(""),  # Optional carrier name
    current_user: dict = Depends(get_current_user)
):
    """Upload a document file to the knowledge base (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can upload knowledge base documents")
    
    # Validate file type
    content_type = file.content_type
    if content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: PDF, DOCX, XLSX, PNG, JPG, WEBP"
        )
    
    file_type = ALLOWED_FILE_TYPES[content_type]
    
    # Generate unique filename
    doc_id = str(uuid4())
    file_extension = file_type
    filename = f"{doc_id}.{file_extension}"
    file_path = KNOWLEDGE_FILES_DIR / filename
    
    # Save file
    try:
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
        
        # Write to disk
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Process the document and extract content
        logger.info(f"Processing uploaded file: {file.filename} ({file_type})")
        processed = await process_uploaded_document(
            str(file_path), 
            file_type, 
            file.filename
        )
        
        # Prepare document record
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        if carrier:
            tag_list.append(carrier.lower())
        
        doc_dict = {
            'id': doc_id,
            'title': title,
            'category': category,
            'tags': tag_list,
            'carrier': carrier,
            'content': processed['extracted_text'],
            'file_path': str(file_path),
            'file_type': file_type,
            'original_filename': file.filename,
            'has_images': processed['has_images'],
            'image_analyses': processed['image_analyses'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'created_by_user_id': current_user['id'],
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'is_file_upload': True
        }
        
        await db.atlas_knowledge_base.insert_one(doc_dict)
        
        # Return without _id
        return {
            'success': True, 
            'document': {k: v for k, v in doc_dict.items() if k != '_id'},
            'message': f"Document processed successfully. Extracted {len(processed['extracted_text'])} characters."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        # Clean up file if it was created
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

# Knowledge Base - Re-analyze document with vision (admin only)
@api_router.post("/atlas-ai/knowledge-base/{doc_id}/analyze-images")
async def analyze_document_images(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Re-analyze images in a document using Claude vision (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can analyze documents")
    
    doc = await db.atlas_knowledge_base.find_one({'id': doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.get('is_file_upload') or not doc.get('file_path'):
        raise HTTPException(status_code=400, detail="Document does not have an associated file")
    
    file_path = Path(doc['file_path'])
    file_type = doc.get('file_type', '')
    
    if file_type not in ['png', 'jpg', 'jpeg', 'webp']:
        raise HTTPException(status_code=400, detail="Only image files can be analyzed with vision")
    
    try:
        # Re-process the document
        processed = await process_uploaded_document(
            str(file_path),
            file_type,
            doc.get('original_filename', 'document')
        )
        
        # Update the document with new analysis
        await db.atlas_knowledge_base.update_one(
            {'id': doc_id},
            {'$set': {
                'content': processed['extracted_text'],
                'image_analyses': processed['image_analyses'],
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            'success': True,
            'message': 'Image analysis completed',
            'analysis': processed['image_analyses']
        }
        
    except Exception as e:
        logger.error(f"Error analyzing document images: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze images: {str(e)}")

# Health check endpoint for Kubernetes (must be on app, not api_router)
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    try:
        # Check if MongoDB is accessible
        await db.command('ping')
        return {
            "status": "healthy",
            "service": "breeze-atlas-backend",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Root endpoint redirect
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Atlas Agency OS API",
        "status": "running",
        "health": "/health",
        "api": "/api"
    }

# Atlas AI Question Analytics (Admin only)
@api_router.get("/atlas-ai/question-analytics")
async def get_question_analytics(current_user: dict = Depends(get_current_user)):
    """
    Get Atlas AI question analytics for admin dashboard
    Shows most asked questions, topics, and trends (anonymous)
    """
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can view analytics")
    
    try:
        # Get top questions by frequency
        top_questions = await db.atlas_question_stats.find(
            {},
            {'_id': 0}
        ).sort('ask_count', -1).limit(50).to_list(50)
        
        # Get topic distribution
        topic_pipeline = [
            {'$group': {
                '_id': '$topic',
                'count': {'$sum': '$ask_count'},
                'unique_questions': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        topic_stats = await db.atlas_question_stats.aggregate(topic_pipeline).to_list(100)
        
        # Get complexity distribution
        complexity_pipeline = [
            {'$group': {
                '_id': '$complexity',
                'count': {'$sum': '$ask_count'}
            }}
        ]
        complexity_stats = await db.atlas_question_stats.aggregate(complexity_pipeline).to_list(10)
        
        # Get recent activity (last 7 days)
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent_activity = await db.atlas_question_log.count_documents({
            'timestamp': {'$gte': seven_days_ago}
        })
        
        # Get cache hit rate
        total_questions = await db.atlas_question_log.count_documents({})
        cached_questions = await db.atlas_question_log.count_documents({'cached': True})
        cache_hit_rate = (cached_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Get daily trend (last 30 days)
        daily_pipeline = [
            {'$group': {
                '_id': '$date',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': -1}},
            {'$limit': 30}
        ]
        daily_trend = await db.atlas_question_log.aggregate(daily_pipeline).to_list(30)
        
        return {
            'top_questions': top_questions,
            'topic_distribution': [
                {
                    'topic': t['_id'],
                    'total_asks': t['count'],
                    'unique_questions': t['unique_questions']
                }
                for t in topic_stats
            ],
            'complexity_distribution': [
                {
                    'complexity': c['_id'],
                    'count': c['count']
                }
                for c in complexity_stats
            ],
            'summary': {
                'total_questions_asked': total_questions,
                'unique_questions': len(top_questions),
                'cache_hit_rate': round(cache_hit_rate, 1),
                'questions_last_7_days': recent_activity
            },
            'daily_trend': [
                {'date': d['_id'], 'count': d['count']}
                for d in reversed(daily_trend)
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get question analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@api_router.post("/zinnia/sync")
async def trigger_zinnia_sync(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    result = await sync_all()
    return result

@api_router.get("/zinnia/sync/agents")
async def sync_zinnia_agents(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    return await sync_agents()

@api_router.get("/zinnia/sync/production")
async def sync_zinnia_production(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    return await sync_production()

@api_router.get("/zinnia/sync/cases")
async def sync_zinnia_cases(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    return await sync_case_status()

@api_router.get("/zinnia/sync/status")
async def zinnia_sync_status(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    return await get_sync_status()

@api_router.get("/zinnia/logs")
async def get_zinnia_logs(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    logs = await db.zinnia_sync_logs.find(
        {}, {'_id': 0}
    ).sort("timestamp", -1).limit(50).to_list(50)
    return logs

@api_router.get("/zinnia/agents")
async def get_zinnia_agents(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    agents = await db.zinnia_agents.find(
        {}, {'_id': 0}
    ).to_list(1000)
    return agents

@api_router.get("/zinnia/production")
async def get_zinnia_production(current_user: dict = Depends(get_current_user)):
    await require_role(current_user, ['admin'])
    data = await db.zinnia_production.find(
        {}, {'_id': 0}
    ).to_list(1000)
    return data

# Include router and middleware AFTER all routes are defined
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
