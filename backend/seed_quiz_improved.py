"""
Improved Quiz Questions - Enhanced for Better Balance and Difficulty
- Answer lengths balanced to prevent obvious correct answers
- More plausible distractors
- Difficulty levels properly calibrated
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

ROOT_DIR = Path(__file__).parent

IMPROVED_QUESTIONS = []

# ==================== IUL QUESTIONS ====================

# IUL - Easy (Foundational concepts, definitions)
IMPROVED_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does IUL stand for?",
        "options": {
            "A": "Indexed Universal Life",
            "B": "Individual Unit Loan",
            "C": "Insurance Unit Link",
            "D": "Interest Universal Ledger"
        },
        "correct_answer": "A"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What protects an IUL policy from market losses?",
        "options": {
            "A": "The participation rate",
            "B": "The index cap",
            "C": "The floor rate",
            "D": "The premium amount"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How are IUL death benefits typically taxed?",
        "options": {
            "A": "As ordinary income",
            "B": "As capital gains",
            "C": "Income tax-free",
            "D": "At estate tax rates"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can policyholders access IUL cash value while living?",
        "options": {
            "A": "No, only after death",
            "B": "Yes, via loans or withdrawals",
            "C": "Only after age 70",
            "D": "Only with carrier approval"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What type of insurance product is an IUL?",
        "options": {
            "A": "Term life insurance",
            "B": "Whole life insurance",
            "C": "Permanent life insurance",
            "D": "Annuity product"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the 'cap' in an IUL policy?",
        "options": {
            "A": "Minimum interest credited",
            "B": "Maximum interest credited",
            "C": "Total premium limit",
            "D": "Death benefit maximum"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "Why do IUL premiums cost more than term insurance?",
        "options": {
            "A": "Higher agent commissions",
            "B": "Marketing expenses",
            "C": "Cash value accumulation",
            "D": "Administrative overhead"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How does an IUL policy build cash value?",
        "options": {
            "A": "Direct stock investment",
            "B": "Index-linked crediting",
            "C": "Fixed interest rate",
            "D": "Bond market returns"
        },
        "correct_answer": "B"
    },
])

# IUL - Intermediate (Application understanding, scenarios)
IMPROVED_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "A client's IUL has a 10% cap and 80% participation rate. If the S&P 500 gains 15%, what interest is credited?",
        "options": {
            "A": "8% (80% of the gain)",
            "B": "10% (capped maximum)",
            "C": "12% (80% of 15%)",
            "D": "15% (full index gain)"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What happens when a client takes a loan from their IUL policy?",
        "options": {
            "A": "Cash value is reduced permanently",
            "B": "Death benefit is reduced proportionally",
            "C": "Loan charged interest, death benefit reduced",
            "D": "Premium payments are suspended"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "Which IUL feature allows adjusting premium payments?",
        "options": {
            "A": "Index allocation options",
            "B": "Premium flexibility feature",
            "C": "Surrender charge schedule",
            "D": "Cost of insurance rates"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What risk does an underfunded IUL policy face?",
        "options": {
            "A": "Excessive cash value growth",
            "B": "Higher than expected returns",
            "C": "Lapse due to insufficient funds",
            "D": "Increased death benefit"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "How does aging affect IUL cost of insurance charges?",
        "options": {
            "A": "Decreases with age",
            "B": "Remains constant",
            "C": "Increases with age",
            "D": "Based on premium paid"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What is the typical IUL surrender charge period?",
        "options": {
            "A": "1-3 years",
            "B": "5-7 years",
            "C": "10-15 years",
            "D": "20-25 years"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "When illustrating IUL, what rate must be disclosed?",
        "options": {
            "A": "Agent's commission rate",
            "B": "Guaranteed minimum rate",
            "C": "Carrier's profit margin",
            "D": "Industry average rate"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What triggers a Modified Endowment Contract (MEC)?",
        "options": {
            "A": "Paying minimum premium only",
            "B": "Exceeding premium funding limits",
            "C": "Taking policy loans",
            "D": "Changing death benefit"
        },
        "correct_answer": "B"
    },
])

# IUL - Expert (Complex scenarios, compliance, advanced strategies)
IMPROVED_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "Under NAIC AG 49, how must non-guaranteed elements be illustrated?",
        "options": {
            "A": "At carrier's discretion",
            "B": "Using midpoint rates",
            "C": "Limiting maximum rates shown",
            "D": "Using historical averages"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "How does the 7-pay test affect IUL funding?",
        "options": {
            "A": "Prevents overfunding that creates MEC",
            "B": "Requires minimum annual premium",
            "C": "Determines surrender charges",
            "D": "Sets maximum death benefit"
        },
        "correct_answer": "A"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "What is the impact of policy loans on IUL illustrations?",
        "options": {
            "A": "Increases cash value growth",
            "B": "Reduces net death benefit",
            "C": "Eliminates index crediting",
            "D": "Triggers immediate lapse"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "Which IUL feature best addresses sequence of returns risk in retirement?",
        "options": {
            "A": "Death benefit guarantee",
            "B": "Floor protection with upside",
            "C": "Fixed loan rate option",
            "D": "Premium flexibility"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "What must agents disclose about IUL index performance?",
        "options": {
            "A": "Guaranteed future returns",
            "B": "Past performance guarantees",
            "C": "Returns are not guaranteed",
            "D": "Minimum index requirements"
        },
        "correct_answer": "C"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "How does a policy loan differ from a withdrawal in an IUL?",
        "options": {
            "A": "Loans reduce basis, withdrawals don't",
            "B": "Loans must be repaid, withdrawals don't",
            "C": "Withdrawals are tax-free, loans aren't",
            "D": "No material difference exists"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "What compliance issue arises from replacing an existing life policy with IUL?",
        "options": {
            "A": "New contestability period",
            "B": "Higher premium requirements",
            "C": "Loss of accumulated benefits",
            "D": "All of the above"
        },
        "correct_answer": "D"
    },
])

# ==================== FIA QUESTIONS ====================

# FIA - Easy
IMPROVED_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does FIA stand for?",
        "options": {
            "A": "Fixed Indexed Annuity",
            "B": "Federal Insurance Act",
            "C": "Financial Investment Advisor",
            "D": "Fixed Interest Account"
        },
        "correct_answer": "A"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the primary purpose of an FIA?",
        "options": {
            "A": "Life insurance protection",
            "B": "Retirement income growth",
            "C": "Short-term savings",
            "D": "Business protection"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can you lose principal in an FIA due to market losses?",
        "options": {
            "A": "Yes, like stocks",
            "B": "No, principal protected",
            "C": "Only first 5 years",
            "D": "Depends on the index"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What penalty applies to early FIA withdrawals before 59½?",
        "options": {
            "A": "5% early withdrawal penalty",
            "B": "10% IRS tax penalty",
            "C": "15% surrender charge",
            "D": "No penalties apply"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How are FIA gains taxed when withdrawn?",
        "options": {
            "A": "Capital gains rate",
            "B": "Ordinary income rate",
            "C": "Tax-free if held 10 years",
            "D": "Estate tax only"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What client is best suited for an FIA?",
        "options": {
            "A": "Young aggressive investor",
            "B": "Conservative near-retiree",
            "C": "Day trader",
            "D": "College student"
        },
        "correct_answer": "B"
    },
])

# FIA - Intermediate
IMPROVED_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What is a guaranteed lifetime withdrawal benefit (GLWB)?",
        "options": {
            "A": "Guaranteed principal return",
            "B": "Lifetime income rider option",
            "C": "Death benefit guarantee",
            "D": "Tax deferral benefit"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "How does the point-to-point crediting method work?",
        "options": {
            "A": "Daily index tracking",
            "B": "Monthly averaging",
            "C": "Compares start to end dates",
            "D": "Quarterly compounding"
        },
        "correct_answer": "C"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What is the typical FIA surrender charge period?",
        "options": {
            "A": "1-3 years",
            "B": "5-10 years",
            "C": "15-20 years",
            "D": "25-30 years"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "Which FIA feature provides downside protection?",
        "options": {
            "A": "Index participation rate",
            "B": "Floor guarantee (0%)",
            "C": "Premium bonus feature",
            "D": "Income rider benefit"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What happens to unused income rider fees in an FIA?",
        "options": {
            "A": "Refunded at maturity",
            "B": "Applied to principal",
            "C": "Not refunded (lost)",
            "D": "Carried forward annually"
        },
        "correct_answer": "C"
    },
])

# FIA - Expert
IMPROVED_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "How does Required Minimum Distribution (RMD) affect FIA taxation?",
        "options": {
            "A": "RMDs are tax-free",
            "B": "RMDs taxed as ordinary income",
            "C": "RMDs don't apply to FIAs",
            "D": "RMDs reduce surrender charges"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "What is the suitability standard for FIA sales?",
        "options": {
            "A": "Sales must meet client needs",
            "B": "Sales must maximize commission",
            "C": "No standard applies",
            "D": "Only disclosure required"
        },
        "correct_answer": "A"
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "How does 1035 exchange affect FIA surrender charges?",
        "options": {
            "A": "Eliminates all charges",
            "B": "Resets surrender period",
            "C": "Reduces charges by 50%",
            "D": "Has no impact"
        },
        "correct_answer": "B"
    },
])

# ==================== TERM LIFE QUESTIONS ====================

# Term - Easy
IMPROVED_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is term life insurance?",
        "options": {
            "A": "Permanent coverage",
            "B": "Temporary coverage",
            "C": "Investment product",
            "D": "Retirement account"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Does term life insurance build cash value?",
        "options": {
            "A": "Yes, like IUL",
            "B": "No cash value",
            "C": "Only after 10 years",
            "D": "Depends on carrier"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens when a term policy expires?",
        "options": {
            "A": "Converts to permanent",
            "B": "Refunds all premiums",
            "C": "Coverage ends",
            "D": "Automatically renews"
        },
        "correct_answer": "C"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "Why is term insurance less expensive than permanent?",
        "options": {
            "A": "Lower agent commission",
            "B": "No cash value component",
            "C": "Shorter underwriting",
            "D": "Government subsidized"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a common term policy length?",
        "options": {
            "A": "2 years",
            "B": "5 years",
            "C": "20 years",
            "D": "50 years"
        },
        "correct_answer": "C"
    },
])

# Term - Intermediate
IMPROVED_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What is a term conversion feature?",
        "options": {
            "A": "Exchanging for annuity",
            "B": "Converting to permanent coverage",
            "C": "Increasing death benefit",
            "D": "Reducing premium payments"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What is guaranteed renewable term?",
        "options": {
            "A": "Premium never increases",
            "B": "Can renew without exam",
            "C": "Coverage lasts forever",
            "D": "Death benefit increases"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "How does age affect term insurance premiums?",
        "options": {
            "A": "No impact on premium",
            "B": "Older age = higher premium",
            "C": "Older age = lower premium",
            "D": "Premium fixed by law"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What is decreasing term insurance?",
        "options": {
            "A": "Premium decreases yearly",
            "B": "Death benefit decreases",
            "C": "Coverage period shortens",
            "D": "Cash value decreases"
        },
        "correct_answer": "B"
    },
])

# Term - Expert
IMPROVED_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Expert",
        "question": "What compliance concern exists with term laddering?",
        "options": {
            "A": "Requires multiple applications",
            "B": "May indicate churning",
            "C": "Complexity must be disclosed",
            "D": "No compliance issues"
        },
        "correct_answer": "C"
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "question": "How does accelerated death benefit rider work?",
        "options": {
            "A": "Pays before death if terminally ill",
            "B": "Doubles death benefit",
            "C": "Accelerates premium payments",
            "D": "Speeds up underwriting"
        },
        "correct_answer": "A"
    },
])

# ==================== FINAL EXPENSE QUESTIONS ====================

# Final Expense - Easy
IMPROVED_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is final expense insurance designed to cover?",
        "options": {
            "A": "Medical bills",
            "B": "Burial costs",
            "C": "Business debts",
            "D": "Mortgage balance"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is typical final expense coverage amount?",
        "options": {
            "A": "$1,000-$2,000",
            "B": "$5,000-$25,000",
            "C": "$100,000-$250,000",
            "D": "$500,000+"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What age group is final expense marketed to?",
        "options": {
            "A": "Ages 18-30",
            "B": "Ages 30-45",
            "C": "Ages 50-85",
            "D": "Ages 90+"
        },
        "correct_answer": "C"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What is a key advantage of final expense insurance?",
        "options": {
            "A": "Builds cash value",
            "B": "Simplified underwriting",
            "C": "Investment returns",
            "D": "Tax deductions"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How are final expense premiums typically paid?",
        "options": {
            "A": "Lump sum only",
            "B": "Monthly payments",
            "C": "Every 5 years",
            "D": "After death"
        },
        "correct_answer": "B"
    },
])

# Final Expense - Intermediate
IMPROVED_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "What is a graded death benefit?",
        "options": {
            "A": "Benefit increases yearly",
            "B": "Partial benefit if death within 2 years",
            "C": "Benefit based on grades",
            "D": "Premium grading schedule"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "What is guaranteed issue final expense?",
        "options": {
            "A": "Guaranteed payout amount",
            "B": "No health questions required",
            "C": "Guaranteed low premium",
            "D": "Guaranteed claim approval"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "How does funeral inflation affect planning?",
        "options": {
            "A": "No impact needed",
            "B": "Should buy extra coverage",
            "C": "Adjust premium annually",
            "D": "Carrier auto-increases benefit"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "What is modified final expense coverage?",
        "options": {
            "A": "Can modify death benefit",
            "B": "Waiting period for full benefit",
            "C": "Modified premium payment",
            "D": "Beneficiary can be modified"
        },
        "correct_answer": "B"
    },
])

# Final Expense - Expert
IMPROVED_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "question": "What suitability issue arises with funeral trusts vs. final expense?",
        "options": {
            "A": "Trust offers better returns",
            "B": "Insurance provides flexibility",
            "C": "Trust has tax advantages",
            "D": "No material difference"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "question": "How should agents address Medicaid planning with final expense?",
        "options": {
            "A": "Advise on spend-down strategies",
            "B": "Discuss irrevocable assignment",
            "C": "Recommend legal counsel",
            "D": "Guarantee Medicaid approval"
        },
        "correct_answer": "C"
    },
])


async def seed_improved_questions():
    """Replace ALL existing questions with improved versions"""
    import sys
    sys.path.append('/app/backend')
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'breeze_atlas')
    
    print(f"Connecting to: {mongo_url}")
    print(f"Database: {db_name}")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Backing up existing questions...")
    existing = await db.quiz_questions.find({}, {'_id': 0}).to_list(None)
    if existing:
        await db.quiz_questions_backup.insert_many(existing)
        print(f"✅ Backed up {len(existing)} existing questions")
    
    print("\n🗑️  Clearing existing questions...")
    result = await db.quiz_questions.delete_many({})
    print(f"✅ Removed {result.deleted_count} questions")
    
    print("\n📝 Inserting improved questions...")
    for q in IMPROVED_QUESTIONS:
        q['id'] = str(uuid.uuid4())
        q['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.quiz_questions.insert_many(IMPROVED_QUESTIONS)
    print(f"✅ Inserted {len(IMPROVED_QUESTIONS)} improved questions")
    
    # Print breakdown
    print("\n📊 Question Breakdown:")
    for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
        for difficulty in ['Easy', 'Intermediate', 'Expert']:
            count = len([q for q in IMPROVED_QUESTIONS if q['product'] == product and q['difficulty'] == difficulty])
            print(f"  {product} - {difficulty}: {count}")
    
    print(f"\n✨ Total improved questions: {len(IMPROVED_QUESTIONS)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_improved_questions())
