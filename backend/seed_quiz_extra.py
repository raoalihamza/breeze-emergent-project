"""
Extra Quiz Questions - Final push to 250
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

EXTRA_QUESTIONS = [
    # IUL
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What is a 'buyer's guide' in life insurance?",
        "options": {
            "A": "A shopping catalog",
            "B": "A document explaining life insurance basics that must be provided to applicants",
            "C": "The policy contract",
            "D": "A list of agents"
        },
        "correct_answer": "B",
        "explanation": "A buyer's guide is a state-required document that explains life insurance concepts to help consumers make informed decisions."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens if an IUL policyholder dies while the policy is in force?",
        "options": {
            "A": "Nothing happens",
            "B": "The death benefit is paid tax-free to the beneficiary",
            "C": "Cash value is forfeited",
            "D": "Premiums are refunded"
        },
        "correct_answer": "B",
        "explanation": "When the insured dies, the death benefit is paid income tax-free to the named beneficiary, providing financial protection for loved ones."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client asks why they need life insurance when they have savings. What do you say?",
        "options": {
            "A": "You don't need insurance then",
            "B": "Savings may not replace years of lost income; insurance provides immediate protection while preserving savings for other goals",
            "C": "Insurance is always better than savings",
            "D": "Savings and insurance are the same"
        },
        "correct_answer": "B",
        "explanation": "Life insurance provides immediate, substantial protection that would take years to build through savings. It protects existing assets while providing income replacement."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "A client wants to use IUL for premium financing. What risks should you discuss?",
        "options": {
            "A": "No risks exist",
            "B": "Interest rate risk, policy performance risk, collateral calls, and potential for negative arbitrage",
            "C": "Premium financing is always profitable",
            "D": "Only loan terms matter"
        },
        "correct_answer": "B",
        "explanation": "Premium financing carries multiple risks: rising interest rates, underperforming policy returns, potential collateral calls, and the strategy may not work as projected."
    },
    # FIA
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Who typically buys Fixed Indexed Annuities?",
        "options": {
            "A": "Only millionaires",
            "B": "People in or near retirement seeking growth with principal protection",
            "C": "Only people under 30",
            "D": "People seeking maximum risk"
        },
        "correct_answer": "B",
        "explanation": "FIAs typically appeal to those in or approaching retirement who want growth potential but need to protect their nest egg from market losses."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What's the first question to ask someone interested in a FIA?",
        "options": {
            "A": "How much money do you have?",
            "B": "What are your goals for these funds and when might you need access?",
            "C": "Do you want the highest interest rate?",
            "D": "What's your favorite index?"
        },
        "correct_answer": "B",
        "explanation": "Understanding goals and liquidity timeline is essential to determine if a FIA with its surrender period is appropriate for the client's situation."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "Why might a FIA NOT be suitable for a 45-year-old?",
        "options": {
            "A": "They're too young",
            "B": "It could be suitable if time horizon aligns; but if they need aggressive growth or full liquidity, other options may be better",
            "C": "FIAs are only for retirees",
            "D": "All 45-year-olds should buy FIAs"
        },
        "correct_answer": "B",
        "explanation": "Age alone doesn't determine suitability. A 45-year-old might benefit from a FIA, but if they need aggressive growth or immediate liquidity, it may not be the best choice."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What documentation must typically be obtained before selling a FIA under best interest regulations?",
        "options": {
            "A": "Just a signature",
            "B": "Financial profile, investment objectives, risk tolerance, time horizon, liquidity needs, and existing coverage",
            "C": "Only the application",
            "D": "No documentation required"
        },
        "correct_answer": "B",
        "explanation": "Best interest regulations require comprehensive documentation of the client's financial situation, goals, and needs to demonstrate the recommendation is in their best interest."
    },
    # Term
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "A young parent with a limited budget needs maximum protection. What's usually the best choice?",
        "options": {
            "A": "Whole life insurance",
            "B": "Term life insurance for maximum coverage per dollar",
            "C": "No insurance until they have more money",
            "D": "Final expense only"
        },
        "correct_answer": "B",
        "explanation": "Term insurance provides the highest death benefit for the lowest premium, making it ideal for young parents who need significant protection on a tight budget."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "If you buy a 20-year term policy at age 30, when does it expire?",
        "options": {
            "A": "At age 40",
            "B": "At age 50",
            "C": "It never expires",
            "D": "At age 65"
        },
        "correct_answer": "B",
        "explanation": "A 20-year term purchased at age 30 expires when you turn 50 (30 + 20 = 50), unless you renew or convert it."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'underwriting class' in term insurance?",
        "options": {
            "A": "A training course for agents",
            "B": "Risk categories (Preferred Plus, Preferred, Standard, etc.) that determine premium rates",
            "C": "The type of term policy",
            "D": "How the policy is distributed"
        },
        "correct_answer": "B",
        "explanation": "Underwriting classes categorize applicants by risk level. Better health and lifestyle earn better classes (Preferred Plus, Preferred) with lower premiums."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client owns their own business and wants coverage that decreases as business debt is paid off. What product might suit them?",
        "options": {
            "A": "Level term only",
            "B": "Decreasing term designed for declining debt obligations",
            "C": "Permanent insurance only",
            "D": "No insurance needed for business debt"
        },
        "correct_answer": "B",
        "explanation": "Decreasing term aligns coverage with declining debt balances, providing appropriate protection at a lower cost than maintaining level coverage throughout."
    },
    # Final Expense
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "George, 70, is in good health but worried about funeral costs. What type of final expense might he qualify for?",
        "options": {
            "A": "Only guaranteed issue",
            "B": "Level (immediate coverage) final expense due to good health",
            "C": "He can't get any coverage at 70",
            "D": "Only graded coverage"
        },
        "correct_answer": "B",
        "explanation": "Good health at 70 likely qualifies George for Level final expense, which provides immediate full death benefit from day one."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How long does coverage last with final expense insurance?",
        "options": {
            "A": "Only 10 years",
            "B": "For your entire lifetime as long as premiums are paid",
            "C": "Until age 85",
            "D": "Only until the funeral"
        },
        "correct_answer": "B",
        "explanation": "Final expense is whole life insurance, providing permanent coverage that lasts your entire lifetime as long as premiums are paid."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is 'replacement' in final expense sales?",
        "options": {
            "A": "Getting a new agent",
            "B": "When new coverage causes existing coverage to be terminated or reduced",
            "C": "Replacing the application",
            "D": "Nothing specific"
        },
        "correct_answer": "B",
        "explanation": "Replacement occurs when purchasing new insurance causes existing insurance to lapse, be surrendered, or reduced. Special disclosure and documentation are required."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "An 80-year-old client with multiple health conditions wants final expense. How do you proceed?",
        "options": {
            "A": "Decline to help them",
            "B": "Find guaranteed issue options, clearly explain graded benefits, ensure suitability and comprehension",
            "C": "Promise full immediate coverage",
            "D": "Tell them they're too old"
        },
        "correct_answer": "B",
        "explanation": "Guaranteed issue products exist for those who can't qualify elsewhere. Ensure the client fully understands graded benefit restrictions and that the purchase is suitable for their situation."
    },
    # Mixed additional
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What must be included when delivering an IUL policy to a client?",
        "options": {
            "A": "Just the policy",
            "B": "The policy, a delivery receipt, and explanation of free look rights",
            "C": "Only the premium statement",
            "D": "Nothing in particular"
        },
        "correct_answer": "B",
        "explanation": "Policy delivery should include the contract, signed delivery receipt, explanation of the free look period, and review of key policy provisions with the client."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "Can you lose money in a FIA due to market declines?",
        "options": {
            "A": "Yes, significant losses are possible",
            "B": "No, the floor (typically 0%) protects principal from market losses",
            "C": "Only in the first year",
            "D": "Depends on the index"
        },
        "correct_answer": "B",
        "explanation": "The floor (typically 0%) ensures you don't lose principal due to negative index returns. Your worst outcome is zero credit for that period, not a loss."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "When might term insurance NOT be the best recommendation?",
        "options": {
            "A": "When the client needs temporary coverage",
            "B": "When the client needs permanent protection, wants cash value, or has estate planning needs",
            "C": "Term is always the best choice",
            "D": "When the client is young"
        },
        "correct_answer": "B",
        "explanation": "Term isn't ideal when permanent coverage is needed (estate planning, business succession), when cash value accumulation is a goal, or when coverage must last beyond a specific term."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "Do final expense premiums increase over time?",
        "options": {
            "A": "Yes, annually",
            "B": "No, premiums are typically level for life",
            "C": "Only after age 80",
            "D": "They decrease over time"
        },
        "correct_answer": "B",
        "explanation": "Final expense whole life policies typically have level premiums that stay the same for life, providing predictable costs for seniors on fixed incomes."
    },
    # More Expert level
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client with a National Life Group IUL wants to compare their policy to a new IUL with better caps. What should you analyze?",
        "options": {
            "A": "Only compare cap rates",
            "B": "Compare total policy costs, current vs. new underwriting, surrender charges, features, and net illustrated values",
            "C": "Always recommend the new policy",
            "D": "Caps are the only factor"
        },
        "correct_answer": "B",
        "explanation": "A complete comparison requires analyzing total costs, health reclassification risk, new surrender charges, all features, and projected values, not just one metric like caps."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A 70-year-old client with an Athene FIA is taking RMDs from their IRA-funded annuity. What should they understand about taxation?",
        "options": {
            "A": "Withdrawals are tax-free",
            "B": "RMDs from an IRA-funded FIA are taxed as ordinary income",
            "C": "Only gains are taxed",
            "D": "Taxes don't apply to annuities"
        },
        "correct_answer": "B",
        "explanation": "RMDs from IRA-funded FIAs are fully taxable as ordinary income since the original contributions were tax-deferred. This differs from non-qualified annuity taxation."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "A client's term policy has a suicide exclusion. How does this typically work?",
        "options": {
            "A": "No death benefit is ever paid for suicide",
            "B": "If death by suicide occurs within the exclusion period (often 2 years), only premiums are returned",
            "C": "Suicide isn't excluded in term policies",
            "D": "Double benefit is paid"
        },
        "correct_answer": "B",
        "explanation": "Most policies exclude suicide deaths within the first 1-2 years. If suicide occurs during this period, only premiums paid are typically returned, not the death benefit."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "How do you evaluate if a premium amount is appropriate for a senior on Social Security?",
        "options": {
            "A": "Any amount is fine",
            "B": "Assess total income, essential expenses, existing coverage, and ensure premium doesn't compromise basic needs",
            "C": "Sell the maximum they qualify for",
            "D": "Social Security recipients shouldn't buy insurance"
        },
        "correct_answer": "B",
        "explanation": "Evaluate their complete financial picture. Premium should be affordable after essential expenses, not strain their budget, and coverage amount should match actual needs."
    },
]

# Add unique IDs to all questions
for q in EXTRA_QUESTIONS:
    q['id'] = str(uuid.uuid4())
    q['created_at'] = datetime.now(timezone.utc).isoformat()


async def seed_extra_questions():
    """Add extra questions"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    if EXTRA_QUESTIONS:
        await db.quiz_questions.insert_many(EXTRA_QUESTIONS)
        
        total = await db.quiz_questions.count_documents({})
        print(f"Added {len(EXTRA_QUESTIONS)} more questions. Total now: {total}")
        
        print("\nFinal question breakdown:")
        for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
            product_total = 0
            for difficulty in ['Easy', 'Intermediate', 'Expert']:
                count = await db.quiz_questions.count_documents({
                    'product': product,
                    'difficulty': difficulty
                })
                product_total += count
                print(f"  {product} - {difficulty}: {count} questions")
            print(f"  {product} TOTAL: {product_total}\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_extra_questions())
