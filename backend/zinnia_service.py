"""
Zinnia SmartOffice Integration Service
- Connects to SmartOffice API (XML-based REST)
- Pulls contacts, production/policy data, activity data
- Saves to MongoDB Atlas with bulk upserts
- Background sync for large datasets (260K+ contacts)
- Incremental sync after initial load
- Scheduled automatic sync every 3 hours
"""

import os
import re
import math
import httpx
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from difflib import SequenceMatcher
from dotenv import load_dotenv
import uuid
import xml.etree.ElementTree as ET
from pymongo import UpdateOne
from email_service import send_sync_failure_email

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Zinnia API Config ────────────────────────────────────────────────────────
ZINNIA_API_URL = "https://api.sandbox.smartofficecrm.com/bwm/v1/send"
ZINNIA_SITE_NAME = os.environ.get("ZINNIA_SITE_NAME", "PREPRODNEW")
ZINNIA_USERNAME = os.environ.get("ZINNIA_USERNAME", "PREPRODNEW_SDC_UAT_bbrandon")
ZINNIA_API_KEY = os.environ.get("ZINNIA_API_KEY", "")
ZINNIA_API_SECRET = os.environ.get("ZINNIA_API_SECRET", "")

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "breeze_atlas")

# DB instance (will be set from server.py)
db = None

# Sync locks to prevent concurrent syncs of same type
_sync_locks = {
    "agents": asyncio.Lock(),
    "production": asyncio.Lock(),
    "cases": asyncio.Lock(),
}

# Track running background tasks
_background_tasks = {}

# Matching progress state
_matching_progress = {
    "status": "idle",          # idle | running | complete | failed
    "total_processed": 0,
    "matched_by_npn": 0,
    "matched_by_name": 0,
    "unmatched": 0,
    "started_at": None,
    "completed_at": None,
    "error": None,
}

# Per-type sync progress (updated live during _paginated_sync)
_sync_progress = {
    "agents":     {"current_page": 0, "total_pages": 0, "api_total": 0, "percent": 0},
    "production": {"current_page": 0, "total_pages": 0, "api_total": 0, "percent": 0},
    "cases":      {"current_page": 0, "total_pages": 0, "api_total": 0, "percent": 0},
}

MAX_RETRIES = 3
PAGE_SIZE = 100
PAGE_DELAY = 0.3  # seconds between API pages


def set_db(database):
    """Set MongoDB database instance from server.py"""
    global db
    db = database


# ─── Data Normalization Utilities ─────────────────────────────────────────────

def normalize_name(name: str) -> str:
    """Capitalize name properly: 'john doe' -> 'John Doe'"""
    if not name or not name.strip():
        return ""
    return name.strip().title()


def normalize_phone(phone: str) -> str:
    """Standardize phone to E.164-ish format: (555) 123-4567 -> +15551234567"""
    if not phone or not phone.strip():
        return ""
    digits = re.sub(r"\D", "", phone.strip())
    if not digits:
        return ""
    if len(digits) == 10:
        digits = "1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}"


def normalize_date(date_str: str) -> str:
    """Convert common date formats to ISO 8601. Returns original if unparseable."""
    if not date_str or not date_str.strip():
        return ""
    date_str = date_str.strip()

    formats = [
        "%m/%d/%Y",          # 01/15/2024
        "%m-%d-%Y",          # 01-15-2024
        "%Y-%m-%d",          # 2024-01-15
        "%m/%d/%Y %H:%M:%S", # 01/15/2024 14:30:00
        "%Y-%m-%dT%H:%M:%S", # 2024-01-15T14:30:00
        "%m/%d/%y",          # 01/15/24
        "%B %d, %Y",        # January 15, 2024
        "%b %d, %Y",        # Jan 15, 2024
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        except ValueError:
            continue

    # Already ISO 8601
    if re.match(r"\d{4}-\d{2}-\d{2}T", date_str):
        return date_str

    return date_str


# ─── Agent Matching ──────────────────────────────────────────────────────────

FUZZY_MATCH_THRESHOLD = 0.85


async def run_agent_matching(limit: int = 0) -> dict:
    """Bulk matching orchestrator — scales to any number of agents.
    Strategy:
    1. Load ALL Atlas users into memory once (small set, never millions)
    2. Build O(1) NPN and exact-name lookup dicts in Python
    3. Use a server-side MongoDB cursor to stream zinnia_agents without skip()
    4. Accumulate batches of 1000, bulk write per batch — no per-document queries
    """
    global _matching_progress

    if db is None:
        return {"error": "Database not initialized"}

    _matching_progress.update({
        "status": "running",
        "total_processed": 0,
        "matched_by_npn": 0,
        "matched_by_name": 0,
        "unmatched": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "error": None,
    })

    now_ts = datetime.now(timezone.utc).isoformat()

    # ── Load all Atlas users into memory once ────────────────────────────────
    all_users = await db.users.find({}, {"_id": 0}).to_list(None)

    npn_lookup: dict = {}
    name_lookup: dict = {}
    name_list: list = []  # [(normalized_full_name, user), ...] for fuzzy

    for u in all_users:
        npn = (u.get("npn") or "").strip()
        if npn:
            npn_lookup[npn] = u

        raw = (u.get("name") or "").strip().lower()
        parts = raw.split()
        if len(parts) >= 2:
            key = f"{parts[0]} {parts[-1]}"
            name_lookup[key] = u
            name_list.append((raw, u))

    # ── Stream zinnia_agents via cursor, process in batches ──────────────────
    matched_npn = 0
    matched_name = 0
    unmatched = 0
    total_agents = 0
    batch_num = 0

    await db.zinnia_unmatched.delete_many({})

    BATCH_SIZE = 1000
    agent_updates: list = []
    unmatched_inserts: list = []

    query = db.zinnia_agents.find({}, {"_id": 0})
    if limit > 0:
        query = query.limit(limit)

    async for agent in query:
        so_id = agent.get("smartoffice_id", "")
        npn = (agent.get("npn") or "").strip()
        first = (agent.get("first_name") or "").strip().lower()
        last = (agent.get("last_name") or "").strip().lower()
        name_key = f"{first} {last}" if first and last else ""

        matched = False

        # NPN match
        if npn and npn in npn_lookup:
            user = npn_lookup[npn]
            agent_updates.append(UpdateOne(
                {"smartoffice_id": so_id},
                {"$set": {"atlas_user_id": user.get("id"), "match_type": "npn", "matched_at": now_ts}}
            ))
            matched_npn += 1
            matched = True

        # Exact name match
        elif name_key and name_key in name_lookup:
            user = name_lookup[name_key]
            agent_updates.append(UpdateOne(
                {"smartoffice_id": so_id},
                {"$set": {"atlas_user_id": user.get("id"), "match_type": "name_exact", "matched_at": now_ts}}
            ))
            matched_name += 1
            matched = True

        # Fuzzy name match
        elif name_key and name_list:
            best_ratio = 0.0
            best_user = None
            for candidate_name, candidate_user in name_list:
                ratio = SequenceMatcher(None, name_key, candidate_name).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_user = candidate_user
            if best_user and best_ratio >= FUZZY_MATCH_THRESHOLD:
                agent_updates.append(UpdateOne(
                    {"smartoffice_id": so_id},
                    {"$set": {
                        "atlas_user_id": best_user.get("id"),
                        "match_type": f"name_fuzzy:{best_ratio:.2f}",
                        "matched_at": now_ts,
                    }}
                ))
                matched_name += 1
                matched = True

        if not matched:
            reason_parts = ["no_npn" if not npn else "npn_not_found"]
            reason_parts.append("name_not_matched" if name_key else "no_name")
            unmatched_inserts.append({
                "smartoffice_id": so_id,
                "first_name": agent.get("first_name", ""),
                "last_name": agent.get("last_name", ""),
                "npn": npn,
                "contact_type": agent.get("contact_type", ""),
                "reason": ", ".join(reason_parts),
                "reviewed": False,
                "created_at": now_ts,
            })
            unmatched += 1

        total_agents += 1

        # Flush batch every BATCH_SIZE records
        if total_agents % BATCH_SIZE == 0:
            if agent_updates:
                await db.zinnia_agents.bulk_write(agent_updates, ordered=False)
                agent_updates = []
            if unmatched_inserts:
                await db.zinnia_unmatched.insert_many(unmatched_inserts, ordered=False)
                unmatched_inserts = []
            batch_num += 1
            _matching_progress.update({
                "total_processed": total_agents,
                "matched_by_npn": matched_npn,
                "matched_by_name": matched_name,
                "unmatched": unmatched,
            })
            logger.info(
                f"Matching batch {batch_num}: {total_agents} processed — "
                f"npn:{matched_npn} name:{matched_name} unmatched:{unmatched}"
            )

    # Flush remaining records
    if agent_updates:
        await db.zinnia_agents.bulk_write(agent_updates, ordered=False)
    if unmatched_inserts:
        await db.zinnia_unmatched.insert_many(unmatched_inserts, ordered=False)

    result = {
        "status": "success",
        "total_agents": total_agents,
        "matched_by_npn": matched_npn,
        "matched_by_name": matched_name,
        "unmatched": unmatched,
        "matched_at": now_ts,
    }

    _matching_progress.update({
        "status": "complete",
        "total_processed": total_agents,
        "matched_by_npn": matched_npn,
        "matched_by_name": matched_name,
        "unmatched": unmatched,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })

    await log_sync("agent_matching", "success", result)
    logger.info(f"Agent matching complete: {matched_npn} NPN, {matched_name} name, {unmatched} unmatched")
    return result


async def match_agents_background() -> dict:
    """Fire-and-forget agent matching — returns immediately, runs in background."""
    if _matching_progress.get("status") == "running":
        return {"status": "already_running", "message": "Agent matching is already in progress"}

    task = asyncio.create_task(run_agent_matching())
    _background_tasks["matching"] = task
    return {"status": "started", "message": "Agent matching started in background"}


def get_matching_status() -> dict:
    """Return current matching progress snapshot."""
    return dict(_matching_progress)


# ─── XML Request Builder ─────────────────────────────────────────────────────

def build_headers():
    """Build SmartOffice API headers"""
    api_key = os.environ.get("ZINNIA_API_KEY") or "328ab6e47a8044e38153c0b808a552db"
    api_secret = os.environ.get("ZINNIA_API_SECRET") or "ioOOq96XPkRkV1JejgWOkPAt54cg9ZRm"
    site_name = os.environ.get("ZINNIA_SITE_NAME") or "PREPRODNEW"
    username = os.environ.get("ZINNIA_USERNAME") or "PREPRODNEW_SDC_UAT_bbrandon"

    return {
        "sitename": site_name,
        "username": username,
        "api-key": api_key,
        "api-secret": api_secret,
        "Content-Type": "application/xml"
    }


def build_agent_search_xml(page: int = 0, pagesize: int = 100, searchid: str = "") -> str:
    return f"""<?xml version="1.0"?>
<request version="1.0">
    <header>
        <office></office>
        <user></user>
        <password></password>
        <keepsession>true</keepsession>
    </header>
    <search searchid="{searchid}" total="true" pagesize="{pagesize}" page="{page}">
        <object>
            <Contact>
                <LastName/>
                <FirstName/>
                <NPN/>
                <ContactType/>
            </Contact>
        </object>
    </search>
</request>"""


def build_production_search_xml(page: int = 0, pagesize: int = 100, searchid: str = "") -> str:
    """Build XML request to fetch production/policy data"""
    return f"""<?xml version="1.0"?>
<request version="1.0">
    <header>
        <office></office>
        <user></user>
        <password></password>
        <keepsession>true</keepsession>
    </header>
    <search searchid="{searchid}" total="true" pagesize="{pagesize}" page="{page}">
        <object>
            <Policy>
                <PolicyNumber/>
                <CarrierName/>
                <AnnualPremium/>
                <InsuredName/>
            </Policy>
        </object>
    </search>
</request>"""


def build_case_status_xml(page: int = 0, pagesize: int = 100, searchid: str = "") -> str:
    """Build XML request to fetch activity/case status data"""
    return f"""<?xml version="1.0"?>
<request version="1.0">
    <header>
        <office></office>
        <user></user>
        <password></password>
        <keepsession>true</keepsession>
    </header>
    <search searchid="{searchid}" total="true" pagesize="{pagesize}" page="{page}">
        <object>
            <Activity>
                <Subject/>
                <ActivityType/>
            </Activity>
        </object>
    </search>
</request>"""


# ─── API Call ────────────────────────────────────────────────────────────────

async def call_smartoffice_api(xml_body: str) -> Optional[ET.Element]:
    """Make a POST request to SmartOffice API and return parsed XML.
    Returns (root_element, is_network_error) — caller uses is_network_error
    to decide whether to use long or short retry delays.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                ZINNIA_API_URL,
                headers=build_headers(),
                content=xml_body.encode("utf-8")
            )
            response.raise_for_status()
            raw = response.content
            # Strip UTF-8 BOM if present
            if raw.startswith(b'\xef\xbb\xbf'):
                raw = raw[3:]
            root = ET.fromstring(raw)
            return root, False

    except httpx.HTTPStatusError as e:
        logger.error(f"SmartOffice API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        return None, False
    except httpx.RequestError as e:
        # Network errors (DNS failure, connection reset) — need longer wait to recover
        logger.error(f"SmartOffice API network error: {str(e)}")
        return None, True
    except ET.ParseError as e:
        logger.error(f"SmartOffice XML parse error: {str(e)}")
        return None, False


async def call_smartoffice_api_with_retry(xml_body: str) -> Optional[ET.Element]:
    """Call SmartOffice API with smart retry logic.
    - Network errors (DNS/connection): up to 8 retries, 30s-120s backoff
    - API/parse errors: up to 3 retries, 2s-6s backoff
    """
    network_retries = 0
    api_retries = 0
    max_network_retries = 8
    max_api_retries = 3

    while True:
        result, is_network_error = await call_smartoffice_api(xml_body)
        if result is not None:
            return result

        if is_network_error:
            network_retries += 1
            if network_retries > max_network_retries:
                logger.error(f"Network error: gave up after {max_network_retries} retries")
                return None
            # Wait 30s, 60s, 60s, 60s... for DNS/connection recovery
            wait = 30 if network_retries == 1 else 60
            logger.warning(f"Network error, retrying in {wait}s (network attempt {network_retries}/{max_network_retries})")
            await asyncio.sleep(wait)
        else:
            api_retries += 1
            if api_retries > max_api_retries:
                logger.error(f"API error: gave up after {max_api_retries} retries")
                return None
            wait = api_retries * 2  # 2s, 4s, 6s
            logger.warning(f"API error, retrying in {wait}s (api attempt {api_retries}/{max_api_retries})")
            await asyncio.sleep(wait)


# ─── Data Parsers ─────────────────────────────────────────────────────────────

def _find_search_element(xml_root: ET.Element) -> Optional[ET.Element]:
    """Find the <search> element in the response, handling edge cases."""
    search_elem = xml_root.find("search")
    if search_elem is not None:
        return search_elem
    search_elem = xml_root.find(".//search")
    if search_elem is not None:
        return search_elem
    children = [child.tag for child in xml_root]
    logger.warning(f"Could not find <search> element. Root tag: {xml_root.tag}, children: {children}")
    return None


def parse_agents(xml_root: ET.Element) -> list:
    """Parse agent XML response into list of dicts"""
    agents = []
    try:
        search_elem = _find_search_element(xml_root)
        if search_elem is None:
            return agents

        for contact in search_elem.findall("Contact"):
            raw_id = contact.get("id", "")
            smartoffice_id = raw_id.split(".")[-1] if raw_id else ""
            if not smartoffice_id:
                continue

            agents.append({
                "smartoffice_id": smartoffice_id,
                "smartoffice_raw_id": raw_id,
                "last_name": normalize_name(contact.findtext("LastName", "")),
                "first_name": normalize_name(contact.findtext("FirstName", "")),
                "npn": contact.findtext("NPN", "").strip(),
                "contact_type": contact.findtext("ContactType", ""),
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "source": "smartoffice"
            })

    except Exception as e:
        logger.error(f"Error parsing agents: {str(e)}")

    return agents


def parse_production(xml_root: ET.Element) -> list:
    """Parse production/policy XML response into list of dicts"""
    policies = []
    try:
        search_elem = _find_search_element(xml_root)
        if search_elem is None:
            return policies

        for policy in search_elem.findall("Policy"):
            raw_id = policy.get("id", "")
            smartoffice_id = raw_id.split(".")[-1] if raw_id else ""
            if not smartoffice_id:
                continue

            policies.append({
                "smartoffice_id": smartoffice_id,
                "smartoffice_raw_id": raw_id,
                "policy_number": policy.findtext("PolicyNumber", "").strip(),
                "carrier_name": normalize_name(policy.findtext("CarrierName", "")),
                "annual_premium": policy.findtext("AnnualPremium", "0").strip(),
                "insured_name": normalize_name(policy.findtext("InsuredName", "")),
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "source": "smartoffice"
            })

    except Exception as e:
        logger.error(f"Error parsing production data: {str(e)}")

    return policies


def parse_case_status(xml_root: ET.Element) -> list:
    """Parse activity/case status XML response into list of dicts"""
    cases = []
    try:
        search_elem = _find_search_element(xml_root)
        if search_elem is None:
            return cases

        for activity in search_elem.findall("Activity"):
            raw_id = activity.get("id", "")
            smartoffice_id = raw_id.split(".")[-1] if raw_id else ""
            if not smartoffice_id:
                continue

            cases.append({
                "smartoffice_id": smartoffice_id,
                "smartoffice_raw_id": raw_id,
                "subject": activity.findtext("Subject", "").strip(),
                "activity_type": activity.findtext("ActivityType", ""),
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "source": "smartoffice"
            })

    except Exception as e:
        logger.error(f"Error parsing case status: {str(e)}")

    return cases


# ─── Database Save (Bulk Upsert) ─────────────────────────────────────────────

async def bulk_upsert(collection_name: str, records: list, match_field: str = "smartoffice_id") -> dict:
    """Bulk upsert records into MongoDB using bulk_write for performance.
    Each record is matched by match_field and upserted (insert if new, update if exists).
    """
    if not records or db is None:
        return {"upserted": 0, "modified": 0}

    collection = db[collection_name]
    operations = []

    for record in records:
        if not record.get(match_field):
            continue
        # Ensure each record has a UUID id for new inserts
        operations.append(
            UpdateOne(
                {match_field: record[match_field]},
                {"$set": record, "$setOnInsert": {"id": str(uuid.uuid4())}},
                upsert=True
            )
        )

    if not operations:
        return {"upserted": 0, "modified": 0}

    try:
        result = await collection.bulk_write(operations, ordered=False)
        return {
            "upserted": result.upserted_count,
            "modified": result.modified_count
        }
    except Exception as e:
        logger.error(f"Bulk upsert error on {collection_name}: {str(e)}")
        return {"upserted": 0, "modified": 0, "error": str(e)}


async def log_sync(sync_type: str, status: str, details: dict):
    """Log sync activity to MongoDB"""
    if db is None:
        return

    log_entry = {
        "id": str(uuid.uuid4()),
        "sync_type": sync_type,
        "status": status,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        await db.zinnia_sync_logs.insert_one(log_entry)
    except Exception as e:
        logger.error(f"Error logging sync: {str(e)}")

    if status == "failed":
        try:
            asyncio.create_task(send_sync_failure_email(
                to="kyle@breezewealthmanagement.com",
                sync_type=sync_type,
                error=details.get("error", "Unknown error"),
                timestamp=log_entry["timestamp"]
            ))
        except Exception as e:
            logger.error(f"Error sending sync failure email: {str(e)}")


async def get_sync_state(sync_type: str) -> Optional[dict]:
    """Get the sync state for a given type from MongoDB"""
    if db is None:
        return None
    return await db.zinnia_sync_state.find_one({"sync_type": sync_type}, {"_id": 0})


async def update_sync_state(sync_type: str, state: dict):
    """Update sync state in MongoDB"""
    if db is None:
        return
    await db.zinnia_sync_state.update_one(
        {"sync_type": sync_type},
        {"$set": {**state, "sync_type": sync_type}},
        upsert=True
    )


# ─── Main Sync Functions ──────────────────────────────────────────────────────

async def _paginated_sync(
    sync_type: str,
    build_xml_fn,
    parse_fn,
    collection_name: str,
) -> dict:
    """Generic paginated sync: fetches all pages from SmartOffice API,
    saves each page to MongoDB immediately via bulk upsert.
    Memory-efficient — never holds more than 1 page (100 records) in memory.
    """
    logger.info(f"Starting {sync_type} sync from SmartOffice...")

    # Reset progress
    if sync_type in _sync_progress:
        _sync_progress[sync_type] = {"current_page": 0, "total_pages": 0, "api_total": 0, "percent": 0}

    total_fetched = 0
    total_upserted = 0
    total_modified = 0
    page = 0
    searchid = ""

    while True:
        xml_body = build_xml_fn(page=page, pagesize=PAGE_SIZE, searchid=searchid)
        xml_root = await call_smartoffice_api_with_retry(xml_body)

        if xml_root is None:
            error_msg = f"API call failed on page {page} after {MAX_RETRIES} retries"
            logger.error(f"{sync_type}: {error_msg}")
            await log_sync(sync_type, "failed", {
                "error": error_msg,
                "pages_completed": page,
                "total_fetched": total_fetched,
            })
            return {
                "status": "failed",
                "error": error_msg,
                "pages_completed": page,
                "total_fetched": total_fetched,
                "upserted": total_upserted,
                "modified": total_modified,
            }

        search_elem = _find_search_element(xml_root)
        if search_elem is None:
            break

        if page == 0:
            searchid = search_elem.get("searchid", "")

        # Parse this page's records
        records = parse_fn(xml_root)
        page_count = len(records)
        total_fetched += page_count

        # Save immediately — don't accumulate in memory
        if records:
            result = await bulk_upsert(collection_name, records)
            total_upserted += result.get("upserted", 0)
            total_modified += result.get("modified", 0)

        more = search_elem.get("more", "false")
        api_total_str = search_elem.get("total", "0")

        # Update live progress
        if sync_type in _sync_progress:
            try:
                api_total_int = int(api_total_str) if api_total_str != "?" else 0
                total_pages_est = math.ceil(api_total_int / PAGE_SIZE) if api_total_int > 0 else 0
                pct = round((page / total_pages_est) * 100, 1) if total_pages_est > 0 else 0
                _sync_progress[sync_type] = {
                    "current_page": page,
                    "total_pages": total_pages_est,
                    "api_total": api_total_int,
                    "percent": pct,
                }
            except Exception:
                pass

        if page % 50 == 0 or more != "true":
            logger.info(
                f"{sync_type} page {page}: +{page_count} records, "
                f"total fetched: {total_fetched}/{api_total_str}, more: {more}"
            )

        if more != "true" or page_count == 0:
            break

        page += 1
        await asyncio.sleep(PAGE_DELAY)

    # Update sync state
    await update_sync_state(sync_type, {
        "initial_sync_done": True,
        "last_sync_time": datetime.now(timezone.utc).isoformat(),
        "total_records": total_fetched,
        "pages": page + 1,
    })

    await log_sync(sync_type, "success", {
        "total_fetched": total_fetched,
        "upserted": total_upserted,
        "modified": total_modified,
        "pages": page + 1,
    })

    logger.info(
        f"{sync_type} sync complete: {total_fetched} records across {page + 1} pages "
        f"(upserted: {total_upserted}, modified: {total_modified})"
    )

    return {
        "status": "success",
        "total_fetched": total_fetched,
        "upserted": total_upserted,
        "modified": total_modified,
        "pages": page + 1,
    }


async def sync_agents() -> dict:
    """Pull ALL agents from SmartOffice with pagination and save to MongoDB.
    Uses lock to prevent concurrent agent syncs.
    """
    if _sync_locks["agents"].locked():
        return {"status": "already_running", "message": "Agent sync is already in progress"}

    async with _sync_locks["agents"]:
        result = await _paginated_sync(
            sync_type="agents",
            build_xml_fn=build_agent_search_xml,
            parse_fn=parse_agents,
            collection_name="zinnia_agents",
        )

        # Auto-run matching after successful agent sync
        if result.get("status") == "success":
            try:
                match_result = await run_agent_matching()
                result["matching"] = match_result
            except Exception as e:
                logger.error(f"Auto-matching failed after agent sync: {e}")
                result["matching"] = {"status": "failed", "error": str(e)}

        return result


async def sync_production() -> dict:
    """Pull ALL production data from SmartOffice with pagination and save to MongoDB"""
    if _sync_locks["production"].locked():
        return {"status": "already_running", "message": "Production sync is already in progress"}

    async with _sync_locks["production"]:
        return await _paginated_sync(
            sync_type="production",
            build_xml_fn=build_production_search_xml,
            parse_fn=parse_production,
            collection_name="zinnia_production",
        )


async def sync_case_status() -> dict:
    """Pull ALL case/activity status from SmartOffice with pagination and save to MongoDB"""
    if _sync_locks["cases"].locked():
        return {"status": "already_running", "message": "Case sync is already in progress"}

    async with _sync_locks["cases"]:
        return await _paginated_sync(
            sync_type="cases",
            build_xml_fn=build_case_status_xml,
            parse_fn=parse_case_status,
            collection_name="zinnia_cases",
        )


async def sync_agents_background() -> dict:
    """Fire-and-forget agent sync — returns immediately, runs in background"""
    if _sync_locks["agents"].locked():
        return {"status": "already_running", "message": "Agent sync is already in progress"}

    task = asyncio.create_task(sync_agents())
    _background_tasks["agents"] = task
    return {"status": "started", "message": "Agent sync started in background"}


async def sync_all() -> dict:
    """Run all syncs.
    Production & cases run first (fast, sequential to avoid SmartOffice session conflicts).
    Agents start in background only after production & cases are complete.
    """
    logger.info("=== Starting Full Zinnia Sync ===")

    # Production & cases first — sequential, fast (~15 seconds total)
    production_result = await sync_production()
    cases_result = await sync_case_status()

    # Agents last — fire in background after others finish (no concurrent API calls)
    agents_result = await sync_agents_background()

    results = {
        "agents": agents_result,
        "production": production_result,
        "cases": cases_result,
        "sync_time": datetime.now(timezone.utc).isoformat()
    }

    logger.info("=== Sync triggered: production & cases done, agents running in background ===")
    return results


async def get_sync_status() -> dict:
    """Get current sync status for all types including live progress."""
    collection_map = {
        "agents": "zinnia_agents",
        "production": "zinnia_production",
        "cases": "zinnia_cases",
    }
    status = {}
    for sync_type, collection_name in collection_map.items():
        state = await get_sync_state(sync_type)
        is_running = _sync_locks[sync_type].locked()
        # estimated_document_count is O(1) — uses collection metadata, not a full scan
        db_count = await db[collection_name].estimated_document_count() if db is not None else 0
        status[sync_type] = {
            "is_running": is_running,
            "initial_sync_done": state.get("initial_sync_done", False) if state else False,
            "last_sync_time": state.get("last_sync_time") if state else None,
            "total_records": db_count,
            "last_sync_fetched": state.get("total_records", 0) if state else 0,
            "progress": _sync_progress.get(sync_type, {}) if is_running else {},
        }
    return status


# ─── Scheduler ───────────────────────────────────────────────────────────────

async def _run_with_retry(sync_fn, sync_type: str, max_attempts: int = 3):
    """Run a sync function with exponential-backoff retry.
    Attempt 1: immediate
    Attempt 2: wait 5 min
    Attempt 3: wait 10 min
    All attempts failed → log + email alert.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = await sync_fn()
            if result.get("status") in ("success", "already_running"):
                return result
            raise Exception(result.get("error", "Sync returned non-success status"))
        except Exception as e:
            logger.error(f"{sync_type} cron attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                wait_min = attempt * 5
                logger.info(f"Retrying {sync_type} cron in {wait_min} min...")
                await asyncio.sleep(wait_min * 60)
            else:
                logger.error(f"{sync_type} cron failed after {max_attempts} attempts — alerting admin")
                await log_sync(f"{sync_type}_cron", "failed", {
                    "error": str(e), "attempts": max_attempts
                })
                try:
                    asyncio.create_task(send_sync_failure_email(
                        to="kyle@breezewealthmanagement.com",
                        sync_type=f"{sync_type} (cron — all {max_attempts} retries failed)",
                        error=str(e),
                        timestamp=datetime.now(timezone.utc).isoformat()
                    ))
                except Exception:
                    pass


async def _seconds_until_next_3am_utc() -> float:
    """Seconds until the next 3:00 AM UTC."""
    now = datetime.now(timezone.utc)
    target = now.replace(hour=3, minute=0, second=0, microsecond=0)
    if now >= target:
        target = target.replace(day=target.day + 1)
    return (target - now).total_seconds()


async def _agents_scheduler():
    """Agents sync every 6 hours (with retry)."""
    logger.info("Agents scheduler started — every 6 hours")
    while True:
        await _run_with_retry(sync_agents, "agents")
        await asyncio.sleep(6 * 60 * 60)


async def _production_scheduler():
    """Production sync every 1 hour (with retry). Staggered 2 min after server start."""
    logger.info("Production scheduler started — every 1 hour")
    await asyncio.sleep(2 * 60)
    while True:
        await _run_with_retry(sync_production, "production")
        await asyncio.sleep(60 * 60)


async def _cases_scheduler():
    """Cases sync every 30 minutes (with retry). Staggered 4 min after server start."""
    logger.info("Cases scheduler started — every 30 minutes")
    await asyncio.sleep(4 * 60)
    while True:
        await _run_with_retry(sync_case_status, "cases")
        await asyncio.sleep(30 * 60)


async def _reconciliation_scheduler():
    """Full reconciliation sync daily at 3 AM UTC."""
    logger.info("Reconciliation scheduler started — daily at 3 AM UTC")
    while True:
        wait = await _seconds_until_next_3am_utc()
        logger.info(f"Reconciliation: next run in {wait/3600:.1f} hours")
        await asyncio.sleep(wait)
        await _run_with_retry(sync_all, "reconciliation")


async def start_all_schedulers():
    """Start all per-type cron schedulers concurrently."""
    logger.info("Starting all Zinnia cron schedulers")
    await asyncio.gather(
        _agents_scheduler(),
        _production_scheduler(),
        _cases_scheduler(),
        _reconciliation_scheduler(),
    )


# Keep for backward compatibility
async def start_scheduler(interval_minutes: int = 180):
    await start_all_schedulers()
