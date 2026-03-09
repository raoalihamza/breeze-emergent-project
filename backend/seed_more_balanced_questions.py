"""
Additional Balanced Quiz Questions
Adds more questions while maintaining answer length balance and difficulty calibration
"""

import asyncio
import os
import uuid
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append('/app/backend')

MORE_QUESTIONS = []

# ==================== MORE IUL QUESTIONS ====================

# IUL - Easy (Additional foundational questions)
MORE_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Easy",
        "question": "What is the 'floor' in an IUL policy?",
        "options": {
            "A": "Maximum interest rate",
            "B": "Minimum guaranteed rate",
            "C": "Premium payment floor",
            "D": "Death benefit minimum"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "question": "Are IUL premiums fixed or flexible?",
        "options": {
            "A": "Fixed only",
            "B": "Flexible payments allowed",
            "C": "Fixed for 10 years",
            "D": "Depends on state law"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "question": "What index is commonly used in IUL policies?",
        "options": {
            "A": "Dow Jones",
            "B": "S&P 500",
            "C": "NASDAQ",
            "D": "Russell 2000"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "question": "Can IUL cash value decrease due to market losses?",
        "options": {
            "A": "Yes, follows market",
            "B": "No, floor protects it",
            "C": "Only in first year",
            "D": "Only if cap exceeded"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "question": "What is the surrender period?",
        "options": {
            "A": "When policy matures",
            "B": "Period with exit penalties",
            "C": "Premium payment period",
            "D": "Death benefit payout time"
        },
        "correct_answer": "B"
    },
])

# IUL - Intermediate (More application scenarios)
MORE_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "How does IUL differ from traditional universal life?",
        "options": {
            "A": "IUL has no cash value",
            "B": "IUL uses index crediting",
            "C": "Traditional has no fees",
            "D": "No material difference"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What happens if IUL premiums are skipped?",
        "options": {
            "A": "Policy immediately lapses",
            "B": "Cash value covers costs",
            "C": "Death benefit doubles",
            "D": "Surrender charges increase"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "Which IUL crediting method uses annual averaging?",
        "options": {
            "A": "Point-to-point method",
            "B": "Monthly average method",
            "C": "Annual reset method",
            "D": "High watermark method"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "What drives cost of insurance increases in IUL?",
        "options": {
            "A": "Stock market performance",
            "B": "Policyholder's age",
            "C": "Premium payment history",
            "D": "Carrier's profit margins"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "question": "How are policy loans typically charged interest?",
        "options": {
            "A": "Prime rate plus 2%",
            "B": "Fixed rate set initially",
            "C": "Variable indexed rate",
            "D": "No interest charged"
        },
        "correct_answer": "B"
    },
])

# IUL - Expert (Complex regulatory and strategy questions)
MORE_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "What is TAMRA's impact on IUL funding strategies?",
        "options": {
            "A": "Limits overfunding via 7-pay test",
            "B": "Requires minimum funding",
            "C": "Eliminates surrender charges",
            "D": "Sets maximum death benefit"
        },
        "correct_answer": "A"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "How should overloan protection be explained to clients?",
        "options": {
            "A": "Prevents all policy lapses",
            "B": "Protects from excessive loans",
            "C": "Guarantees loan approval",
            "D": "Reduces loan interest rates"
        },
        "correct_answer": "B"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "What disclosure is required for non-guaranteed elements?",
        "options": {
            "A": "None if hypothetical",
            "B": "Must show worst case",
            "C": "Cannot illustrate them",
            "D": "Rates limited by AG 49"
        },
        "correct_answer": "D"
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "question": "How does Section 7702 affect IUL design?",
        "options": {
            "A": "Defines life insurance tax status",
            "B": "Sets agent commission caps",
            "C": "Regulates surrender charges",
            "D": "Controls index selection"
        },
        "correct_answer": "A"
    },
])

# ==================== MORE FIA QUESTIONS ====================

# FIA - Easy
MORE_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Easy",
        "question": "Is an FIA a life insurance or annuity product?",
        "options": {
            "A": "Life insurance",
            "B": "Annuity product",
            "C": "Mutual fund",
            "D": "Investment account"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "question": "What is the main benefit of tax deferral in FIAs?",
        "options": {
            "A": "Avoids all taxes",
            "B": "Growth compounds tax-free",
            "C": "Reduces premium cost",
            "D": "Increases death benefit"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "question": "Can you withdraw FIA funds at any time?",
        "options": {
            "A": "Yes, always penalty-free",
            "B": "Yes, with surrender charges",
            "C": "No, locked until death",
            "D": "Only after age 100"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "question": "What is annuitization?",
        "options": {
            "A": "Canceling the contract",
            "B": "Converting to income stream",
            "C": "Transferring to beneficiary",
            "D": "Increasing premium payment"
        },
        "correct_answer": "B"
    },
])

# FIA - Intermediate
MORE_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What is a premium bonus in an FIA?",
        "options": {
            "A": "Commission to agent",
            "B": "Extra credited to account",
            "C": "Tax deduction",
            "D": "Surrender charge waiver"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "How does annual reset crediting work?",
        "options": {
            "A": "Locks gains each year",
            "B": "Resets premium annually",
            "C": "Adjusts surrender charges",
            "D": "Changes index allocation"
        },
        "correct_answer": "A"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What is the free withdrawal amount typically?",
        "options": {
            "A": "5-10% annually",
            "B": "25% annually",
            "C": "50% annually",
            "D": "No free withdrawals"
        },
        "correct_answer": "A"
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "question": "What happens to FIA at owner's death?",
        "options": {
            "A": "Forfeited to carrier",
            "B": "Passes to beneficiary",
            "C": "Converts to income",
            "D": "Taxed at 50%"
        },
        "correct_answer": "B"
    },
])

# FIA - Expert
MORE_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "How does the exclusion ratio affect FIA annuitization?",
        "options": {
            "A": "Determines tax-free portion",
            "B": "Excludes poor performers",
            "C": "Limits premium amounts",
            "D": "Controls index selection"
        },
        "correct_answer": "A"
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "What is the stretch provision in FIA inheritance?",
        "options": {
            "A": "Extends surrender period",
            "B": "Allows beneficiary deferral",
            "C": "Increases death benefit",
            "D": "Reduces tax liability"
        },
        "correct_answer": "B"
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "question": "How does Best Interest Regulation affect FIA sales?",
        "options": {
            "A": "Bans all FIA sales",
            "B": "Requires suitability documentation",
            "C": "Eliminates commissions",
            "D": "No impact on sales"
        },
        "correct_answer": "B"
    },
])

# ==================== MORE TERM QUESTIONS ====================

# Term - Easy
MORE_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Easy",
        "question": "What is level term insurance?",
        "options": {
            "A": "Increasing death benefit",
            "B": "Flat death benefit amount",
            "C": "Decreasing premiums",
            "D": "Variable coverage"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "question": "Who typically needs term insurance?",
        "options": {
            "A": "Retirees with no debts",
            "B": "Young families with debt",
            "C": "Wealthy estate planners",
            "D": "Single with no dependents"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "question": "Can term insurance be renewed?",
        "options": {
            "A": "Never renewable",
            "B": "Yes, if renewable feature",
            "C": "Only with medical exam",
            "D": "Only if under 40"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "question": "What is annual renewable term (ART)?",
        "options": {
            "A": "Art insurance product",
            "B": "One-year renewable term",
            "C": "Annual payment term",
            "D": "Artistic profession coverage"
        },
        "correct_answer": "B"
    },
])

# Term - Intermediate
MORE_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What is return of premium (ROP) term?",
        "options": {
            "A": "Returns all premiums paid",
            "B": "Returns interest earned",
            "C": "Returns agent commission",
            "D": "No premium return"
        },
        "correct_answer": "A"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "How does term conversion typically work?",
        "options": {
            "A": "Requires new medical exam",
            "B": "Converts without new underwriting",
            "C": "Only available at expiry",
            "D": "Requires carrier approval"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What is mortgage protection term insurance?",
        "options": {
            "A": "Covers mortgage payments",
            "B": "Decreasing death benefit",
            "C": "Protects against foreclosure",
            "D": "Pays off entire mortgage"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "question": "What happens to premiums if you outlive term?",
        "options": {
            "A": "Fully refunded",
            "B": "Not refunded (unless ROP)",
            "C": "Applied to new policy",
            "D": "Converted to annuity"
        },
        "correct_answer": "B"
    },
])

# Term - Expert
MORE_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Expert",
        "question": "What is the human life value approach?",
        "options": {
            "A": "Calculates needs-based coverage",
            "B": "Values earnings capacity",
            "C": "Determines premium amount",
            "D": "Assesses health risks"
        },
        "correct_answer": "B"
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "question": "How does STOLI affect term insurance sales?",
        "options": {
            "A": "Increases premiums",
            "B": "Creates compliance concerns",
            "C": "Improves underwriting",
            "D": "No impact on term"
        },
        "correct_answer": "B"
    },
])

# ==================== MORE FINAL EXPENSE QUESTIONS ====================

# Final Expense - Easy
MORE_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "question": "What type of life insurance is final expense?",
        "options": {
            "A": "Term insurance",
            "B": "Permanent whole life",
            "C": "Universal life",
            "D": "Variable life"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "question": "Are medical exams required for final expense?",
        "options": {
            "A": "Always required",
            "B": "Usually not required",
            "C": "Only for large amounts",
            "D": "Only if under 50"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "question": "What is whole life insurance?",
        "options": {
            "A": "Covers entire family",
            "B": "Lifetime coverage",
            "C": "Covers all illnesses",
            "D": "Whole premium payment"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "question": "Do final expense policies build cash value?",
        "options": {
            "A": "Never builds value",
            "B": "Yes, slowly over time",
            "C": "Only after 20 years",
            "D": "Only if overfunded"
        },
        "correct_answer": "B"
    },
])

# Final Expense - Intermediate
MORE_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "What is the contestability period?",
        "options": {
            "A": "Time to contest premiums",
            "B": "2 years carrier can investigate",
            "C": "Period to change beneficiary",
            "D": "Time to cancel policy"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "How does guaranteed issue differ from simplified issue?",
        "options": {
            "A": "No difference exists",
            "B": "Guaranteed has no questions",
            "C": "Simplified costs less",
            "D": "Guaranteed requires exam"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "What is pre-need insurance?",
        "options": {
            "A": "Pre-existing condition coverage",
            "B": "Funeral home assigned policy",
            "C": "Premium paid in advance",
            "D": "Needs-based underwriting"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "question": "Why use irrevocable beneficiary designation?",
        "options": {
            "A": "Reduces premium cost",
            "B": "Protects from creditors",
            "C": "Increases death benefit",
            "D": "Speeds up claims"
        },
        "correct_answer": "B"
    },
])

# Final Expense - Expert
MORE_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "question": "How should agents handle burial trust alternatives?",
        "options": {
            "A": "Always recommend insurance",
            "B": "Discuss pros and cons",
            "C": "Never mention trusts",
            "D": "Recommend trusts only"
        },
        "correct_answer": "B"
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "question": "What is the impact of Social Security lump sum benefit?",
        "options": {
            "A": "Covers all funeral costs",
            "B": "Provides $255 death benefit",
            "C": "Replaces final expense need",
            "D": "Eliminates insurance need"
        },
        "correct_answer": "B"
    },
])

async def seed_more_questions():
    """Add additional balanced questions to existing set"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'breeze_atlas')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"📝 Adding {len(MORE_QUESTIONS)} more balanced questions...")
    
    for q in MORE_QUESTIONS:
        q['id'] = str(uuid.uuid4())
        q['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.quiz_questions.insert_many(MORE_QUESTIONS)
    print(f"✅ Successfully added questions")
    
    # Get total count
    total = await db.quiz_questions.count_documents({})
    print(f"\n✨ Total questions in database: {total}")
    
    # Print breakdown
    print("\n📊 Complete Question Breakdown:")
    for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
        product_total = 0
        print(f"\n{product}:")
        for difficulty in ['Easy', 'Intermediate', 'Expert']:
            count = await db.quiz_questions.count_documents({
                'product': product,
                'difficulty': difficulty
            })
            product_total += count
            print(f"  {difficulty}: {count}")
        print(f"  TOTAL: {product_total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_more_questions())
