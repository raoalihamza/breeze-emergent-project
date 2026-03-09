"""
Atlas AI Service - Internal AI Operating Assistant for Breeze Financial Group
Enhanced with document processing and vision capabilities for analyzing
underwriting guides, product guides, charts, and graphics.
Enhanced with caching, hybrid model routing, and question logging.
"""

import os
import base64
import io
import asyncio
import hashlib
import re
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
import PyPDF2
from docx import Document as DocxDocument
import openpyxl
from PIL import Image

load_dotenv()

# MongoDB connection (will be set by server.py)
db = None

def set_db(database):
    """Set the MongoDB database instance"""
    global db
    db = database


def classify_question_complexity(question: str) -> str:
    """
    Classify question as 'simple' or 'complex' for model routing
    Simple questions use Haiku (cheap), complex use Sonnet (expensive)
    """
    question_lower = question.lower().strip()
    
    # Simple question patterns
    simple_patterns = [
        r'^what is (an?|the)\s+\w+\??$',  # "What is an IUL?"
        r'^define\s+\w+',  # "Define IUL"
        r'^(who|what|when|where|why|how) (is|are|do|does|can|should|would)\s+\w+\??$',  # Simple W questions
        r'^\w+\s+(stand for|mean)\??$',  # "IUL stand for?"
        r'^(yes|no)\s+or\s+(yes|no)\s+question',  # Yes/no questions
    ]
    
    # Complex question indicators
    complex_indicators = [
        'recommend', 'carrier', 'underwriting', 'placement', 'client',
        'compare', 'versus', 'vs', 'difference between',
        'strategy', 'approach', 'best way', 'how should',
        'scenario', 'case', 'situation',
        'multiple', 'several', 'various',
        'analyze', 'evaluate', 'assess',
    ]
    
    # Check simple patterns first
    for pattern in simple_patterns:
        if re.search(pattern, question_lower):
            return 'simple'
    
    # Check for complex indicators
    for indicator in complex_indicators:
        if indicator in question_lower:
            return 'complex'
    
    # Default: simple if short (< 50 chars), complex if long
    return 'simple' if len(question) < 50 else 'complex'


def generate_question_hash(question: str) -> str:
    """Generate a hash for question matching (case-insensitive, normalized)"""
    normalized = re.sub(r'[^\w\s]', '', question.lower())
    normalized = ' '.join(normalized.split())  # Normalize whitespace
    return hashlib.md5(normalized.encode()).hexdigest()


async def get_cached_response(question: str) -> Optional[str]:
    """Check if we have a cached response for this question"""
    if db is None:
        return None
    
    try:
        question_hash = generate_question_hash(question)
        cache_entry = await db.atlas_cache.find_one(
            {
                'question_hash': question_hash,
                'expires_at': {'$gt': datetime.now(timezone.utc).isoformat()}
            },
            {'_id': 0}
        )
        
        if cache_entry:
            # Update hit count
            await db.atlas_cache.update_one(
                {'question_hash': question_hash},
                {
                    '$inc': {'hit_count': 1},
                    '$set': {'last_hit_at': datetime.now(timezone.utc).isoformat()}
                }
            )
            return cache_entry['response']
        
        return None
    except Exception as e:
        print(f"Cache retrieval error: {e}")
        return None


async def cache_response(question: str, response: str, ttl_hours: int = 48):
    """Cache a question/response pair"""
    if db is None:
        return
    
    try:
        question_hash = generate_question_hash(question)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        
        await db.atlas_cache.update_one(
            {'question_hash': question_hash},
            {
                '$set': {
                    'question_hash': question_hash,
                    'question': question[:500],  # Store first 500 chars for reference
                    'response': response,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'expires_at': expires_at.isoformat(),
                    'last_hit_at': datetime.now(timezone.utc).isoformat()
                },
                '$setOnInsert': {
                    'hit_count': 0
                }
            },
            upsert=True
        )
    except Exception as e:
        print(f"Cache storage error: {e}")


async def log_question(question: str, complexity: str, model_used: str, cached: bool = False):
    """
    Log question for analytics (anonymous - no user info)
    Used for admin dashboard to see what agents are asking
    """
    if db is None:
        return
    
    try:
        # Extract topic/category from question
        topic = extract_topic(question)
        
        # Create question log entry
        log_entry = {
            'id': hashlib.sha256(f"{question}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],
            'question_hash': generate_question_hash(question),
            'question_preview': question[:200],  # First 200 chars for admin view
            'topic': topic,
            'complexity': complexity,
            'model_used': model_used,
            'cached': cached,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
        }
        
        # Update or insert question stats
        await db.atlas_question_stats.update_one(
            {'question_hash': log_entry['question_hash']},
            {
                '$set': {
                    'question_preview': log_entry['question_preview'],
                    'topic': topic,
                    'complexity': complexity,
                    'last_asked': log_entry['timestamp']
                },
                '$inc': {'ask_count': 1}
            },
            upsert=True
        )
        
        # Store individual log entry (for trending analysis)
        await db.atlas_question_log.insert_one(log_entry)
        
    except Exception as e:
        print(f"Question logging error: {e}")


def extract_topic(question: str) -> str:
    """Extract the main topic/category from a question"""
    question_lower = question.lower()
    
    # Topic keywords mapping
    topics = {
        'IUL': ['iul', 'indexed universal life', 'universal life'],
        'FIA': ['fia', 'fixed indexed annuity', 'annuity'],
        'Term Life': ['term', 'term life', 'term insurance'],
        'Final Expense': ['final expense', 'burial', 'funeral'],
        'Underwriting': ['underwriting', 'underwrite', 'medical exam', 'health questions'],
        'Carriers': ['carrier', 'transamerica', 'f&g', 'fidelity', 'national life', 'foresters', 'pacific life'],
        'Commission': ['commission', 'comp level', 'payout'],
        'Sales Process': ['sales', 'selling', 'close', 'objection', 'script'],
        'Product Comparison': ['compare', 'comparison', 'versus', 'vs', 'difference between'],
        'Compliance': ['compliance', 'regulation', 'suitability', 'disclosure'],
        'Client Scenarios': ['client', 'prospect', 'age', 'health condition', 'diabetes', 'scenario']
    }
    
    # Find matching topic
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in question_lower:
                return topic
    
    return 'General'


ATLAS_AI_SYSTEM_PROMPT = """You are Atlas AI — the official internal AI operating assistant for Breeze Financial Group. You serve staff, agents, and leaders.

## Your Core Principles
1. **Be CONCISE** - Get to the point. No fluff, no filler.
2. **Be ACTIONABLE** - Every response should tell the user exactly what to do next.
3. **Be DIRECT** - Reflect "The Breeze Way": simple, professional, execution-oriented.
4. **NEVER cite document names** - Don't mention "According to the guide..." or reference internal document titles.

## CRITICAL Response Rules

### DO NOT ask unnecessary follow-up questions
- If the user's request is clear and simple, ANSWER IT DIRECTLY
- Only ask clarifying questions when genuinely needed for accuracy
- Never ask questions just to continue conversation
- Example: If someone asks for a Calendly link → give the link, suggest they save it, done.

### When to ask clarifying questions (ONLY these cases):
- Complex underwriting scenarios (need age, health conditions, medications)
- Product placement with multiple variables
- Carrier comparisons where specifics matter
- When the request is genuinely ambiguous

### Simple Requests = Direct Answers
For simple requests like:
- "How do I book a call with Brandon?" → Give his Calendly: https://calendly.com/brandon-breeze (recommend saving it)
- "Where's the Builder SOP?" → Direct link or exact location
- "What's the contracting process?" → Clear numbered steps
- "Send me the CRM link" → Direct link

## Response Formatting (Use Markdown)

### Structure your responses like this:

**For Direct Answers:**
Brief answer in 1-2 sentences, then:
- Bullet points for steps or details
- Links formatted as clickable: [Link Text](URL)
- End with one clear next action

**For Scripts (use code blocks):**
```script
[Word-for-word script here]
Agent: "Opening line..."
[Continue script...]
```

**For Checklists:**
- [ ] Step 1
- [ ] Step 2  
- [ ] Step 3

**For Comparisons (use tables):**
| Feature | Carrier A | Carrier B |
|---------|-----------|-----------|
| Rate    | X%        | Y%        |

**For Warnings/Important Notes:**
> ⚠️ **Important:** [Critical information here]

**For Tips:**
> 💡 **Pro Tip:** [Helpful suggestion]

## Knowledge Base Usage
- Use the provided context to answer accurately
- NEVER mention document names or say "according to the guide"
- Present information as direct knowledge
- If info isn't in context, say: "This isn't in my database. Please verify with leadership."

## Quick Reference Links
When users ask for common resources, provide these directly:
- Brandon's Calendar: https://calendly.com/brandon-breeze
- CRM Signup: [Provide if in knowledge base]
- Contracting Portal: [Provide if in knowledge base]

## Compliance Guardrails
- Never give tax, legal, or investment advice
- Never promise underwriting outcomes
- Never make up carrier rules or rates
- Use safe language: "typically," "generally," "based on guidelines"

## Carrier Recommendations (CRITICAL)
**BE CARRIER-NEUTRAL** - Do NOT show bias toward specific carriers:
- When recommending carriers, provide ALL appropriate options the client qualifies for
- Present carriers alphabetically or by relevance to client profile, NOT by preference
- Include a diverse range: Fidelity & Guaranty, TransAmerica, National Life, Mutual of Omaha, Foresters, Pacific Life, American General, etc.
- For underwriting/placement, list 3-5 suitable carriers with brief rationale for each
- NEVER favor one carrier unless client specifically asks about that carrier
- Example format:
  ```
  Based on [client profile], here are suitable carriers:
  
  1. **Carrier A** - Best for [specific reason]
  2. **Carrier B** - Competitive on [specific feature]
  3. **Carrier C** - Strong option if [specific condition]
  4. **Carrier D** - Consider for [specific benefit]
  
  Recommend discussing these options with the client to find best fit.
  ```

## Response Length Guidelines
- Simple questions: 2-4 sentences max
- How-to questions: Brief intro + numbered steps
- Scripts: Just the script with minimal setup
- Complex scenarios: Concise analysis + clear recommendation

Remember: Agents are busy. Respect their time. Get to the point. Stay carrier-neutral.
"""


def extract_text_from_pdf(file_path: str) -> Tuple[str, List[int]]:
    """
    Extract text from PDF and identify pages that might have images/charts
    Returns (text_content, pages_with_potential_images)
    """
    text_content = []
    pages_with_images = []
    
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                
                # Check if page might have images (heuristic: low text density)
                if len(text.strip()) < 200:  # Likely has charts/images
                    pages_with_images.append(page_num)
                    
        return "\n\n".join(text_content), pages_with_images
    except Exception as e:
        return f"Error extracting PDF: {str(e)}", []


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from Word document"""
    try:
        doc = DocxDocument(file_path)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        # Also extract tables
        for table in doc.tables:
            table_text = []
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells]
                table_text.append(" | ".join(row_text))
            paragraphs.append("\n[TABLE]\n" + "\n".join(table_text) + "\n[/TABLE]")
        
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_text_from_xlsx(file_path: str) -> str:
    """Extract text from Excel spreadsheet"""
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        content = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            content.append(f"\n=== Sheet: {sheet_name} ===\n")
            
            rows = []
            for row in sheet.iter_rows(values_only=True):
                row_values = [str(cell) if cell is not None else "" for cell in row]
                if any(row_values):  # Skip empty rows
                    rows.append(" | ".join(row_values))
            
            content.append("\n".join(rows))
        
        return "\n".join(content)
    except Exception as e:
        return f"Error extracting XLSX: {str(e)}"


def image_to_base64(file_path: str) -> str:
    """Convert image to base64 for Claude vision"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large (max 1568px on longest side for Claude)
            max_size = 1568
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None


def pdf_page_to_base64(file_path: str, page_num: int) -> Optional[str]:
    """
    Convert a PDF page to base64 image for vision analysis
    Note: This is a simplified version - for production, use pdf2image or similar
    """
    return None


async def analyze_image_with_vision(image_base64: str, context: str = "") -> str:
    """
    Use Claude's vision to analyze an image (chart, table, graphic)
    """
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return "Vision analysis not available - API key missing"
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id="vision_analysis",
            system_message="You are an expert at analyzing insurance documents, underwriting guides, rate tables, and product comparison charts. Extract all relevant data, numbers, rates, conditions, and rules from the image. Be thorough and precise. Present the data in a clean, structured format."
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        message = UserMessage(
            text=f"Analyze this image thoroughly. Extract all data, rates, conditions, health classes, age brackets, and any other relevant information. Context: {context}",
            image_url=f"data:image/jpeg;base64,{image_base64}"
        )
        
        response = await chat.send_message(message)
        return response
    except Exception as e:
        return f"Vision analysis error: {str(e)}"


async def process_uploaded_document(file_path: str, file_type: str, original_filename: str) -> dict:
    """
    Process an uploaded document and extract content
    Returns dict with extracted_text, has_images, image_analyses
    """
    result = {
        "extracted_text": "",
        "has_images": False,
        "image_analyses": [],
        "file_type": file_type,
        "original_filename": original_filename
    }
    
    if file_type == "pdf":
        text, pages_with_images = extract_text_from_pdf(file_path)
        result["extracted_text"] = text
        result["has_images"] = len(pages_with_images) > 0
        if pages_with_images:
            result["image_analyses"].append(f"Note: Pages {pages_with_images} may contain charts/graphics that require visual review.")
            
    elif file_type == "docx":
        result["extracted_text"] = extract_text_from_docx(file_path)
        
    elif file_type == "xlsx":
        result["extracted_text"] = extract_text_from_xlsx(file_path)
        
    elif file_type in ["png", "jpg", "jpeg", "webp"]:
        result["has_images"] = True
        image_b64 = image_to_base64(file_path)
        if image_b64:
            analysis = await analyze_image_with_vision(
                image_b64, 
                "Insurance/financial document image"
            )
            result["image_analyses"].append(analysis)
            result["extracted_text"] = f"[IMAGE ANALYSIS]\n{analysis}\n[/IMAGE ANALYSIS]"
    
    return result


async def get_atlas_ai_response(
    user_message: str, 
    knowledge_context: str = "", 
    session_id: str = "default",
    image_data: Optional[str] = None
) -> str:
    """
    Get a response from Atlas AI using Claude Sonnet 4 or Haiku
    Enhanced with caching and hybrid model routing for cost optimization
    """
    import logging
    logger = logging.getLogger(__name__)
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return "⚠️ Atlas AI is not configured. Please contact your administrator to set up the EMERGENT_LLM_KEY."
    
    try:
        # Validate inputs
        if not user_message or not user_message.strip():
            return "I didn't receive a message. Please ask me a question and I'll help you."
        
        # Classify question complexity
        complexity = classify_question_complexity(user_message)
        
        # Check cache for non-image questions
        if not image_data:
            cached_response = await get_cached_response(user_message)
            if cached_response:
                # Log as cached
                await log_question(user_message, complexity, 'cached', cached=True)
                return cached_response
        
        # Select model based on complexity
        # NOTE: Using Sonnet for all queries until correct Haiku model name is confirmed
        # if complexity == 'simple':
        #     model_provider = "anthropic"
        #     model_name = "claude-haiku-4-5"  # 90% cheaper than Sonnet
        #     logger.info("Using Claude Haiku for simple question")
        # else:
        model_provider = "anthropic"
        model_name = "claude-sonnet-4-5-20250929"  # Premium model
        logger.info(f"Using Claude Sonnet for {complexity} question")
        
        # Build the system message with knowledge context
        system_message = ATLAS_AI_SYSTEM_PROMPT
        
        if knowledge_context:
            # Limit context size to prevent token overload
            truncated_context = knowledge_context[:8000] if len(knowledge_context) > 8000 else knowledge_context
            system_message += f"""

## Internal Knowledge Context
Use the following information to answer accurately. DO NOT mention document names or sources.

---
{truncated_context}
---

Remember: Present this as direct knowledge. Never say "according to..." or cite document names.
"""
        
        # Initialize the chat with selected model
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=system_message
            ).with_model(model_provider, model_name)
        except Exception as e:
            logger.error(f"Failed to initialize LlmChat: {e}")
            return "⚠️ Failed to initialize AI chat. Please try again. If the problem persists, contact support."
        
        # Create the user message (with optional image)
        try:
            if image_data:
                message = UserMessage(
                    text=user_message,
                    image_url=f"data:image/jpeg;base64,{image_data}"
                )
            else:
                message = UserMessage(text=user_message)
        except Exception as e:
            logger.error(f"Failed to create user message: {e}")
            return "⚠️ Failed to process your message. Please try again without special characters or attachments."
        
        # Get the response with timeout
        try:
            response = await asyncio.wait_for(
                chat.send_message(message),
                timeout=30.0  # 30 second timeout
            )
            
            if not response or not response.strip():
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
            # Cache the response for non-image questions
            if not image_data and len(response) < 5000:  # Don't cache huge responses
                await cache_response(user_message, response, ttl_hours=48)
            
            # Log the question
            await log_question(user_message, complexity, model_name, cached=False)
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Atlas AI timeout for session {session_id}")
            return "⚠️ The request took too long. Please try asking a more specific question or try again."
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Failed to get AI response: {e}")
            
            # Check for specific error types
            if "budget" in error_msg or "exceeded" in error_msg:
                return "⚠️ The Universal Key budget has been exceeded. Please go to Profile → Universal Key → Add Balance or enable auto top-up."
            elif "rate limit" in error_msg:
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            elif "timeout" in error_msg:
                return "⚠️ Request timeout. Please try a shorter question or try again."
            else:
                return "⚠️ I encountered an error processing your request. Please try again or contact support if this persists."
    
    except Exception as e:
        logger.error(f"Unexpected error in get_atlas_ai_response: {e}")
        return "⚠️ An unexpected error occurred. Please try again or contact support."
