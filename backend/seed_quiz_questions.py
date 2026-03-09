"""
Quiz Question Seeder for Breeze Matrix
Generates ~250 questions across 4 products (IUL, FIA, Term, Final Expense)
and 3 difficulty levels (Easy, Intermediate, Expert)
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

# Carriers referenced in questions
CARRIERS = [
    "Fidelity & Guaranty Life", "National Life Group", "Ethos", "Aflac",
    "Kansas City Life", "United Home Life", "American Amicable", "Americo"
]

# Question bank organized by product, difficulty, and category
QUESTIONS = []

# ==================== IUL QUESTIONS ====================

# IUL - Easy
QUESTIONS.extend([
    # Product Knowledge
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does IUL stand for?",
        "options": {
            "A": "Indexed Universal Life",
            "B": "Individual Unified Loan",
            "C": "Insurance Unlimited Liability",
            "D": "Interest Utility Ledger"
        },
        "correct_answer": "A",
        "explanation": "IUL stands for Indexed Universal Life, a type of permanent life insurance that links cash value growth to a market index."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does the death benefit in an IUL policy provide?",
        "options": {
            "A": "Tax-free income during retirement",
            "B": "Tax-free money to beneficiaries upon the insured's death",
            "C": "A guaranteed rate of return",
            "D": "Protection against market losses"
        },
        "correct_answer": "B",
        "explanation": "The death benefit in an IUL policy provides tax-free money to beneficiaries when the insured passes away, which is one of the core features of life insurance."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How does an IUL policy accumulate cash value?",
        "options": {
            "A": "Through direct stock market investments",
            "B": "By linking growth to a market index like the S&P 500",
            "C": "Through fixed interest rates only",
            "D": "By investing in real estate"
        },
        "correct_answer": "B",
        "explanation": "IUL policies accumulate cash value by crediting interest based on the performance of a market index, not through direct investment in the market."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a 'floor' in an IUL policy?",
        "options": {
            "A": "The maximum interest rate you can earn",
            "B": "The minimum guaranteed interest rate (often 0%)",
            "C": "The surrender charge",
            "D": "The cost of insurance"
        },
        "correct_answer": "B",
        "explanation": "The floor is the minimum guaranteed interest rate in an IUL, typically 0%, which protects the policy from negative returns when the index performs poorly."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a 'cap' in an IUL policy?",
        "options": {
            "A": "The minimum interest credited",
            "B": "The maximum interest rate that can be credited",
            "C": "The premium amount",
            "D": "The death benefit limit"
        },
        "correct_answer": "B",
        "explanation": "The cap is the maximum interest rate that can be credited to your cash value in any given period, even if the index performs better."
    },
    # Client Scenarios
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Tom, age 35, wants life insurance that can also help him save for retirement. Which product would BEST suit his needs?",
        "options": {
            "A": "Term life insurance",
            "B": "Indexed Universal Life (IUL)",
            "C": "Final Expense insurance",
            "D": "Short-term disability insurance"
        },
        "correct_answer": "B",
        "explanation": "An IUL would best suit Tom because it provides both a death benefit and cash value accumulation that can supplement retirement income."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Maria wants life insurance but is worried about losing money in the stock market. What IUL feature would address her concern?",
        "options": {
            "A": "The cap rate",
            "B": "The participation rate",
            "C": "The floor (typically 0%)",
            "D": "The premium flexibility"
        },
        "correct_answer": "C",
        "explanation": "The floor protects against market losses. With a 0% floor, Maria's cash value won't decrease due to market downturns."
    },
    # Compliance
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "When selling an IUL policy, what must always be provided to the client?",
        "options": {
            "A": "A verbal promise of returns",
            "B": "A policy illustration showing potential outcomes",
            "C": "A guarantee of future performance",
            "D": "Your personal investment advice"
        },
        "correct_answer": "B",
        "explanation": "A policy illustration must be provided to show the client how the policy may perform under different scenarios. This is a regulatory requirement."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "Can an agent guarantee specific returns on an IUL policy?",
        "options": {
            "A": "Yes, based on historical index performance",
            "B": "Yes, if they use conservative estimates",
            "C": "No, future performance cannot be guaranteed",
            "D": "Only if the carrier approves"
        },
        "correct_answer": "C",
        "explanation": "Agents cannot guarantee specific returns because IUL performance depends on index performance, which is unpredictable."
    },
    # Suitability
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "For which client would an IUL NOT typically be suitable?",
        "options": {
            "A": "Someone seeking permanent coverage and cash accumulation",
            "B": "Someone who only needs coverage for 10 years",
            "C": "Someone looking for tax-advantaged growth",
            "D": "A business owner wanting key person protection"
        },
        "correct_answer": "B",
        "explanation": "If someone only needs coverage for 10 years, term life insurance would be more cost-effective. IUL is designed for long-term, permanent needs."
    },
    # Sales Process
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What should be the FIRST step when meeting with a potential IUL client?",
        "options": {
            "A": "Show them the product illustration",
            "B": "Conduct a thorough needs analysis",
            "C": "Discuss premium payments",
            "D": "Compare IUL to other products"
        },
        "correct_answer": "B",
        "explanation": "A thorough needs analysis should always come first to understand the client's goals, financial situation, and insurance needs before recommending any product."
    },
])

# IUL - Intermediate
QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'participation rate' in an IUL policy?",
        "options": {
            "A": "The percentage of clients who keep their policy",
            "B": "The percentage of the index gain credited to your policy",
            "C": "The premium amount as a percentage of income",
            "D": "The percentage of death benefit paid out"
        },
        "correct_answer": "B",
        "explanation": "The participation rate determines what percentage of the index's gains are credited to your cash value. A 75% participation rate means you receive 75% of the index gains."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What happens to an IUL policy if the policyholder stops paying premiums?",
        "options": {
            "A": "The policy immediately lapses",
            "B": "The cash value can be used to pay premiums",
            "C": "The insurance company covers the premiums",
            "D": "The death benefit doubles"
        },
        "correct_answer": "B",
        "explanation": "If sufficient cash value has accumulated, it can be used to pay policy costs, keeping the policy in force. However, this depletes the cash value over time."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "How are policy loans from an IUL typically taxed?",
        "options": {
            "A": "As ordinary income",
            "B": "As capital gains",
            "C": "They are generally tax-free if the policy stays in force",
            "D": "At a flat 15% rate"
        },
        "correct_answer": "C",
        "explanation": "Policy loans from an IUL are generally tax-free as long as the policy remains in force and doesn't become a Modified Endowment Contract (MEC)."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a Modified Endowment Contract (MEC)?",
        "options": {
            "A": "A policy with increased death benefits",
            "B": "A policy that has been over-funded, losing some tax advantages",
            "C": "A policy that has lapsed",
            "D": "A policy with no cash value"
        },
        "correct_answer": "B",
        "explanation": "A MEC is a life insurance policy that has been over-funded relative to its death benefit. MECs lose the tax-free loan and withdrawal benefits of regular life insurance."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "Jennifer, 45, has maxed out her 401(k) and IRA contributions and wants additional tax-advantaged savings for retirement. Which IUL feature would be most relevant to discuss?",
        "options": {
            "A": "The death benefit",
            "B": "Tax-free policy loans for supplemental retirement income",
            "C": "The surrender charges",
            "D": "The premium flexibility"
        },
        "correct_answer": "B",
        "explanation": "For someone who has maxed out traditional retirement accounts, IUL's ability to provide tax-free income through policy loans is a key benefit for supplemental retirement planning."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "Robert owns a National Life Group IUL and wants to know why his cash value didn't grow much last year despite good market performance. What's the most likely explanation?",
        "options": {
            "A": "The insurance company kept his money",
            "B": "His gains were limited by the cap rate",
            "C": "IULs never grow",
            "D": "He forgot to pay his premium"
        },
        "correct_answer": "B",
        "explanation": "Even in years with strong index performance, IUL growth is limited by the cap rate. If the S&P returned 20% but his cap is 10%, he would only be credited 10%."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client with a Fidelity & Guaranty Life IUL asks about the difference between annual point-to-point and monthly sum crediting strategies. What's the key difference?",
        "options": {
            "A": "Point-to-point measures growth from start to end of period; monthly sum adds each month's changes",
            "B": "They are exactly the same",
            "C": "Monthly sum always performs better",
            "D": "Point-to-point has no cap"
        },
        "correct_answer": "A",
        "explanation": "Annual point-to-point compares the index at the start and end of a period, while monthly sum adds up each month's gains/losses (usually with monthly caps). They can perform differently in various market conditions."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What documentation is required when replacing an existing life insurance policy with a new IUL?",
        "options": {
            "A": "No special documentation needed",
            "B": "Replacement forms and comparison disclosure",
            "C": "Only a verbal acknowledgment",
            "D": "A letter from the previous carrier"
        },
        "correct_answer": "B",
        "explanation": "Policy replacements require specific documentation including replacement forms and disclosure comparing the existing policy with the new one to ensure the client understands the implications."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "When illustrating an IUL policy, what illustrated rate does NAIC regulations typically require as the maximum?",
        "options": {
            "A": "Any rate the agent chooses",
            "B": "The rate must follow NAIC Actuarial Guideline 49 (AG49) rules",
            "C": "A guaranteed 10% rate",
            "D": "Historical S&P 500 returns"
        },
        "correct_answer": "B",
        "explanation": "NAIC Actuarial Guideline 49 (AG49) regulates the maximum illustrated rates for IUL policies to prevent unrealistic projections and ensure consumer protection."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A 62-year-old client wants to purchase a new IUL to access cash value in 3 years. What's the primary suitability concern?",
        "options": {
            "A": "They are too old for life insurance",
            "B": "Surrender charges and insufficient time for cash value growth",
            "C": "IULs don't work for seniors",
            "D": "The premium would be too low"
        },
        "correct_answer": "B",
        "explanation": "IULs need time for cash value to accumulate. A 3-year horizon may not allow sufficient growth, and early access could result in surrender charges and minimal cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "When determining if an IUL is suitable, which factor is MOST important?",
        "options": {
            "A": "The client's favorite color",
            "B": "The client's long-term financial goals and time horizon",
            "C": "The agent's commission rate",
            "D": "The carrier's office location"
        },
        "correct_answer": "B",
        "explanation": "Suitability is determined by matching the product to the client's financial goals, time horizon, risk tolerance, and overall financial situation."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client objects: 'I've heard IULs have high fees.' What's the best NEPQ-style response?",
        "options": {
            "A": "That's not true, ignore what you've heard.",
            "B": "What have you heard specifically? Let's look at the actual costs in this illustration.",
            "C": "All insurance has fees, don't worry about it.",
            "D": "You should buy term instead."
        },
        "correct_answer": "B",
        "explanation": "Using NEPQ methodology, you should seek to understand the client's specific concern and then address it with facts from the illustration, not dismiss or deflect."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What's the purpose of showing both guaranteed and non-guaranteed columns in an IUL illustration?",
        "options": {
            "A": "To confuse the client",
            "B": "To show worst-case and potential scenarios for informed decision-making",
            "C": "It's just a regulatory requirement with no real purpose",
            "D": "To make the sale easier"
        },
        "correct_answer": "B",
        "explanation": "Both columns help clients understand the range of outcomes - the guaranteed column shows minimum performance while non-guaranteed shows potential growth based on illustrated rates."
    },
])

# IUL - Expert
QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does a multiplier or bonus crediting strategy in an IUL work, and what's the trade-off?",
        "options": {
            "A": "Free money with no downside",
            "B": "Enhanced credits in early years funded by higher ongoing policy costs",
            "C": "Guaranteed 2x returns every year",
            "D": "Lower death benefit in exchange for higher cash value"
        },
        "correct_answer": "B",
        "explanation": "Multiplier/bonus strategies provide enhanced crediting (often in later years) but typically come with higher policy charges that fund these bonuses. The long-term net effect depends on policy performance."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Explain how spread or asset fees differ from caps in an IUL crediting strategy.",
        "options": {
            "A": "They are exactly the same mechanism",
            "B": "Spread deducts a fixed percentage from returns; caps limit maximum crediting",
            "C": "Spread applies to death benefit; caps apply to cash value",
            "D": "Spread only affects policy loans"
        },
        "correct_answer": "B",
        "explanation": "A spread subtracts a fixed percentage from the index return (e.g., index returns 8%, minus 2% spread = 6% credited). Caps limit the maximum credit regardless of index performance."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the significance of the 'segment date' or 'sweep date' in an IUL policy?",
        "options": {
            "A": "The date when premiums are due",
            "B": "The date when index crediting calculations are performed and new segments begin",
            "C": "The policy anniversary",
            "D": "The date loans must be repaid"
        },
        "correct_answer": "B",
        "explanation": "The segment/sweep date is when the carrier calculates crediting for the ending segment and allocates money to new segments. Understanding this timing is crucial for policy management."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A high-net-worth client, age 50, wants to use an IUL for estate planning. Their estate is $15 million. What strategy might you discuss?",
        "options": {
            "A": "Simply buy the largest death benefit possible",
            "B": "Discuss using an Irrevocable Life Insurance Trust (ILIT) to remove death benefit from taxable estate",
            "C": "Recommend they don't need life insurance",
            "D": "Suggest they wait until age 65"
        },
        "correct_answer": "B",
        "explanation": "For estates potentially subject to estate taxes, placing life insurance in an ILIT removes the death benefit from the taxable estate while providing liquidity for estate taxes or wealth transfer."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A business owner with a National Life Group IUL wants to use it for executive bonus planning (Section 162). What's a key consideration?",
        "options": {
            "A": "The employee cannot be the policy owner",
            "B": "The business deducts the bonus; the executive owns the policy and is taxed on the bonus",
            "C": "Section 162 plans are illegal",
            "D": "Only term insurance qualifies"
        },
        "correct_answer": "B",
        "explanation": "In a Section 162 Executive Bonus plan, the employer pays bonuses that the executive uses for IUL premiums. The employer deducts the bonus, and the executive owns the policy outright but is taxed on the bonus."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client's IUL is approaching MEC status. What strategies might prevent it from becoming a MEC?",
        "options": {
            "A": "Cancel the policy immediately",
            "B": "Reduce future premiums, request a death benefit increase, or use a 1035 exchange",
            "C": "Nothing can be done once approaching MEC",
            "D": "Pay more premium to fix it"
        },
        "correct_answer": "B",
        "explanation": "To avoid MEC status, options include reducing premiums, increasing the death benefit (which raises the 7-pay threshold), or a 1035 exchange to a new policy with an appropriate premium structure."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "Under AG49-A regulations, what additional disclosure is required for IUL illustrations with bonus/multiplier features?",
        "options": {
            "A": "No additional disclosure needed",
            "B": "A side-by-side comparison showing policy performance with and without the bonus",
            "C": "Only verbal disclosure is required",
            "D": "Disclosure that bonuses are guaranteed"
        },
        "correct_answer": "B",
        "explanation": "AG49-A requires additional disclosure for policies with bonuses/multipliers, including a comparison showing how the policy would perform with and without the bonus feature to ensure transparency."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What are the penalties for an agent who uses misleading illustrations to sell an IUL?",
        "options": {
            "A": "A small fine",
            "B": "Potential license revocation, fines, E&O claims, and possible criminal charges",
            "C": "No penalty if the client signs",
            "D": "Only the carrier is liable"
        },
        "correct_answer": "B",
        "explanation": "Using misleading illustrations can result in serious consequences including license suspension/revocation, regulatory fines, E&O insurance claims, civil liability, and in egregious cases, criminal charges."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "A client wants to fully fund an IUL to maximize cash value. What's the primary risk you should discuss?",
        "options": {
            "A": "The policy will perform better",
            "B": "Over-funding could create a MEC, losing tax advantages on loans and withdrawals",
            "C": "There's no risk to maximum funding",
            "D": "The death benefit will decrease"
        },
        "correct_answer": "B",
        "explanation": "Aggressive funding can cause the policy to become a MEC, which means loans and withdrawals would be taxed (and possibly penalized), negating key IUL tax benefits."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "A sophisticated client asks about the carrier's general account vs. separate account. How would you explain IUL's placement?",
        "options": {
            "A": "IUL cash value is in a separate account like variable life",
            "B": "IUL cash value is in the carrier's general account, protected from market loss but subject to carrier solvency",
            "C": "It's in a client-controlled investment account",
            "D": "IUL doesn't have cash value"
        },
        "correct_answer": "B",
        "explanation": "IUL cash value is held in the insurance company's general account. The index-linked crediting is a formula applied to this account, not actual market investment, which provides downside protection."
    },
])

# ==================== FIA QUESTIONS ====================

# FIA - Easy
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does FIA stand for?",
        "options": {
            "A": "Fixed Interest Account",
            "B": "Fixed Indexed Annuity",
            "C": "Financial Investment Annuity",
            "D": "Future Income Arrangement"
        },
        "correct_answer": "B",
        "explanation": "FIA stands for Fixed Indexed Annuity, a type of annuity that offers growth linked to a market index while protecting principal."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the primary purpose of a Fixed Indexed Annuity?",
        "options": {
            "A": "To provide immediate income",
            "B": "To accumulate money for retirement with principal protection",
            "C": "To invest directly in stocks",
            "D": "To provide life insurance"
        },
        "correct_answer": "B",
        "explanation": "FIAs are designed to accumulate money for retirement by linking growth to market indices while protecting the principal from market losses."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "If the market index goes down, what happens to the principal in a typical FIA?",
        "options": {
            "A": "You lose money proportionally",
            "B": "Your principal is protected from market losses",
            "C": "The insurance company covers half the loss",
            "D": "You must add more money"
        },
        "correct_answer": "B",
        "explanation": "One of the key features of FIAs is principal protection. If the index declines, your principal remains intact (though you won't earn interest that period)."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a 'surrender period' in a Fixed Indexed Annuity?",
        "options": {
            "A": "The time you must wait before receiving benefits",
            "B": "The period during which early withdrawals may incur penalties",
            "C": "The time it takes to process your application",
            "D": "The waiting period before death benefits pay"
        },
        "correct_answer": "B",
        "explanation": "The surrender period is the time frame (often 5-10 years) during which withdrawals beyond the free withdrawal amount may be subject to surrender charges."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Dorothy, age 60, has $100,000 in savings and is terrified of losing money in the stock market. She wants growth potential but safety. What product might suit her?",
        "options": {
            "A": "Variable Annuity",
            "B": "Fixed Indexed Annuity",
            "C": "Aggressive growth mutual fund",
            "D": "Cryptocurrency"
        },
        "correct_answer": "B",
        "explanation": "A FIA offers Dorothy growth potential linked to market indices while protecting her principal from market losses, matching her desire for safety with growth opportunity."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "James, age 55, wants to start saving for retirement but wants to defer taxes on growth. Would a FIA help?",
        "options": {
            "A": "No, FIAs are fully taxable",
            "B": "Yes, FIA growth is tax-deferred until withdrawal",
            "C": "No, only 401(k)s offer tax deferral",
            "D": "Yes, but only for the first year"
        },
        "correct_answer": "B",
        "explanation": "FIAs provide tax-deferred growth, meaning you don't pay taxes on gains until you withdraw money, making them effective retirement savings vehicles."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "When selling a FIA, what must you disclose about the surrender period?",
        "options": {
            "A": "Nothing, it's in the fine print",
            "B": "The length of the surrender period and any applicable charges",
            "C": "Only if the client asks",
            "D": "Just tell them it's 'a few years'"
        },
        "correct_answer": "B",
        "explanation": "Full disclosure of the surrender period length and charges is required. Clients must understand the liquidity constraints before purchasing."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "For which client would a FIA with a 10-year surrender period NOT be suitable?",
        "options": {
            "A": "Someone age 55 planning for retirement at 65",
            "B": "Someone who may need access to all their funds within 2 years",
            "C": "Someone looking for tax-deferred growth",
            "D": "Someone wanting principal protection"
        },
        "correct_answer": "B",
        "explanation": "A 10-year surrender period is not suitable for someone who needs liquidity within 2 years, as early withdrawals would incur surrender charges."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What question should you ask before recommending a FIA?",
        "options": {
            "A": "What's your favorite stock?",
            "B": "How soon might you need access to these funds?",
            "C": "Do you like paperwork?",
            "D": "What's your favorite color?"
        },
        "correct_answer": "B",
        "explanation": "Understanding the client's liquidity needs is essential before recommending a FIA, given the surrender period restrictions."
    },
])

# FIA - Intermediate  
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is an 'income rider' on a FIA?",
        "options": {
            "A": "A person who receives income",
            "B": "An optional benefit providing guaranteed lifetime income, usually with additional fees",
            "C": "A required part of all FIAs",
            "D": "A one-time bonus payment"
        },
        "correct_answer": "B",
        "explanation": "An income rider is an optional add-on that provides guaranteed lifetime income payments, typically for an additional fee, regardless of how the account value performs."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the difference between the 'accumulation value' and 'income account value' in a FIA with a rider?",
        "options": {
            "A": "They are the same thing",
            "B": "Accumulation value is the cash value; income account value is a calculation used to determine income payments",
            "C": "Income account value is always higher",
            "D": "Accumulation value is only for death benefits"
        },
        "correct_answer": "B",
        "explanation": "The accumulation value is what you could walk away with (minus surrender charges). The income account value is a separate calculation used solely to determine your guaranteed income payments."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "How does a 'bonus' on a FIA typically work?",
        "options": {
            "A": "Free money with no strings attached",
            "B": "An upfront credit often offset by lower caps/rates or longer surrender periods",
            "C": "A guaranteed annual return",
            "D": "Cash you can withdraw immediately"
        },
        "correct_answer": "B",
        "explanation": "FIA bonuses are typically offset by lower crediting rates, longer surrender periods, or higher fees. The bonus may also be subject to vesting schedules."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "Regarding Americo FIAs, what does the 'roll-up rate' on an income rider refer to?",
        "options": {
            "A": "The rate at which your cash value grows",
            "B": "The guaranteed growth rate of the income account value during the deferral period",
            "C": "The interest rate on policy loans",
            "D": "The annual fee percentage"
        },
        "correct_answer": "B",
        "explanation": "The roll-up rate is the guaranteed rate at which your income account value grows each year during the deferral period, which determines your future income payments."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "Susan, 58, has $200,000 in CDs earning 2%. She wants growth but fears market losses. She needs access to funds in 3-5 years for a business investment. What's the primary concern with a 10-year surrender FIA?",
        "options": {
            "A": "Insufficient growth potential",
            "B": "Liquidity constraints don't match her timeline",
            "C": "She's too young for an annuity",
            "D": "Tax implications on gains"
        },
        "correct_answer": "B",
        "explanation": "A 10-year surrender period doesn't align with her 3-5 year timeline for needing funds. She could face significant surrender charges if she needs her money."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client has an Athene FIA and asks why their statement shows two different values. How do you explain this?",
        "options": {
            "A": "It's an error on the statement",
            "B": "One is the accumulation value (actual cash), and one is the income benefit base (for income calculations)",
            "C": "One is before tax, one is after",
            "D": "One is guaranteed, one is projected"
        },
        "correct_answer": "B",
        "explanation": "FIAs with income riders often show both values: the accumulation value (what you could withdraw) and the income benefit base (used to calculate guaranteed income payments)."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What suitability requirements apply when selling a FIA to a senior client?",
        "options": {
            "A": "No special requirements for seniors",
            "B": "Enhanced suitability review considering age, liquidity needs, and financial situation",
            "C": "You cannot sell to anyone over 65",
            "D": "Only verbal disclosure is needed"
        },
        "correct_answer": "B",
        "explanation": "Most states have enhanced suitability requirements for senior clients, including consideration of their age, liquidity needs, existing assets, and ensuring the product matches their situation."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is the 'free look' period for a FIA, and what does it allow?",
        "options": {
            "A": "A period to look at the policy before buying",
            "B": "A period (often 10-30 days) after purchase to cancel for a full refund",
            "C": "Free consultation with a financial advisor",
            "D": "A preview of expected returns"
        },
        "correct_answer": "B",
        "explanation": "The free look period (typically 10-30 days, depending on state) allows clients to review the contract after receipt and cancel for a full refund if it doesn't meet their needs."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A client age 78 wants to put their entire $500,000 savings into a FIA with a 10-year surrender. What's your suitability concern?",
        "options": {
            "A": "No concern, proceed with the sale",
            "B": "Age-related liquidity risk and surrendering all assets into one illiquid product",
            "C": "They should put in more money",
            "D": "FIAs don't accept large premiums"
        },
        "correct_answer": "B",
        "explanation": "Putting all savings into an illiquid product at age 78 raises serious suitability concerns. The client may need funds for healthcare or emergencies before the surrender period ends."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client says, 'I've heard annuities are bad.' Using NEPQ, what's your response?",
        "options": {
            "A": "That's wrong, annuities are great.",
            "B": "Help me understand what concerns you about them specifically?",
            "C": "You're right, don't buy this.",
            "D": "Ignore the comment and continue your presentation."
        },
        "correct_answer": "B",
        "explanation": "NEPQ methodology encourages understanding the client's specific concerns. By asking what they've heard, you can address actual concerns rather than assumed objections."
    },
])

# FIA - Expert
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Explain how a 'volatility control index' in a FIA differs from a traditional market index like the S&P 500.",
        "options": {
            "A": "They perform identically",
            "B": "Volatility control indices actively manage exposure to reduce volatility, often allowing higher participation rates but potentially lower returns",
            "C": "Volatility control indices guarantee higher returns",
            "D": "Only S&P 500 indices are used in FIAs"
        },
        "correct_answer": "B",
        "explanation": "Volatility control indices automatically adjust exposure between equities and fixed income based on volatility levels. This reduced volatility allows carriers to offer higher participation rates, but may result in lower returns in strong bull markets."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'trigger' crediting strategy in a FIA?",
        "options": {
            "A": "Automatic annual payments",
            "B": "If the index is flat or positive, you receive a stated rate; if negative, you receive 0%",
            "C": "A penalty for early withdrawal",
            "D": "A one-time bonus"
        },
        "correct_answer": "B",
        "explanation": "A trigger strategy pays a predetermined rate if the index return is zero or positive at the end of the crediting period. It's a win/no-lose proposition but the trigger rate may be lower than potential point-to-point gains."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does a 'buffer' or 'floor and cap' FIA strategy differ from standard 0% floor FIAs?",
        "options": {
            "A": "They are the same",
            "B": "Buffer strategies may expose you to some downside (e.g., losses beyond -10%) in exchange for higher upside potential",
            "C": "Buffer strategies guarantee higher returns",
            "D": "Buffer strategies have no upside cap"
        },
        "correct_answer": "B",
        "explanation": "Buffer strategies provide protection up to a certain level (e.g., first 10% of losses) but expose you to losses beyond that. In exchange, they typically offer higher caps or participation rates."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client wants to use a FIA for pension maximization strategy. Their pension offers $3,000/month single life or $2,400/month joint. How might a FIA help?",
        "options": {
            "A": "FIAs can't be used for pension planning",
            "B": "Take the higher single-life option and use FIA income rider to provide survivor income for spouse",
            "C": "Always take joint option, no strategy needed",
            "D": "Use FIA to replace the pension entirely"
        },
        "correct_answer": "B",
        "explanation": "Pension maximization uses the higher single-life pension option while funding a life insurance or FIA with income rider to provide survivor income, potentially resulting in higher overall benefits."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client age 59 wants to do a 1035 exchange from a variable annuity to a Fidelity & Guaranty Life FIA. Their VA has a $50,000 gain and $150,000 total value. What's a key consideration?",
        "options": {
            "A": "1035 exchanges are not allowed",
            "B": "The gain transfers tax-free but new surrender charges apply; ensure the FIA benefits outweigh the change",
            "C": "They will pay taxes on the $50,000 gain",
            "D": "The FIA will have no surrender period"
        },
        "correct_answer": "B",
        "explanation": "A 1035 exchange preserves the tax-deferred status of gains, but the new FIA will have its own surrender period. Ensure the benefits (safety, features, rates) justify giving up the VA and starting new surrender charges."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "Under the DOL fiduciary rule considerations, what standard applies when recommending a FIA for IRA funds?",
        "options": {
            "A": "No special standard applies",
            "B": "You must act in the client's best interest when providing investment advice for retirement accounts",
            "C": "Only suitability standard applies",
            "D": "FIAs cannot be used in IRAs"
        },
        "correct_answer": "B",
        "explanation": "When advising on retirement accounts, a fiduciary standard may apply, requiring recommendations to be in the client's best interest, not just suitable. This includes understanding fees, alternatives, and fit."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is the purpose of 'best interest' state regulations (based on NAIC model) for annuity sales?",
        "options": {
            "A": "To increase agent commissions",
            "B": "To require agents to act in the consumer's best interest when making recommendations",
            "C": "To eliminate annuity sales",
            "D": "To reduce paperwork"
        },
        "correct_answer": "B",
        "explanation": "Best interest regulations require producers to make recommendations that are in the consumer's best interest based on their needs, objectives, and financial situation, with enhanced documentation requirements."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "A client wants to annuitize their FIA vs. use an income rider. What factors should drive this decision?",
        "options": {
            "A": "Always annuitize for highest income",
            "B": "Consider control of principal, legacy goals, income guarantee, and flexibility needs",
            "C": "Income riders always provide more income",
            "D": "There is no difference between the options"
        },
        "correct_answer": "B",
        "explanation": "Annuitization typically provides higher income but gives up control of principal. Income riders maintain access to account value but may provide lower income. The choice depends on legacy goals, liquidity needs, and income requirements."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "A CPA referral comes to you concerned about Required Minimum Distributions (RMDs) from their IRA. How might a Qualified Longevity Annuity Contract (QLAC) within a FIA help?",
        "options": {
            "A": "QLACs don't exist",
            "B": "A QLAC can defer up to $200,000 (or 25% of IRA) from RMD calculations until age 85",
            "C": "QLACs eliminate all taxes",
            "D": "QLACs are only for non-qualified funds"
        },
        "correct_answer": "B",
        "explanation": "A QLAC is a deferred income annuity that can exclude up to $200,000 (or 25% of aggregate IRA balance) from RMD calculations, with income starting as late as age 85."
    },
])

# ==================== TERM LIFE QUESTIONS ====================

# Term - Easy
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is term life insurance?",
        "options": {
            "A": "Insurance that lasts your entire lifetime",
            "B": "Insurance that provides coverage for a specific period (term) of time",
            "C": "Insurance for your car",
            "D": "A savings account with a death benefit"
        },
        "correct_answer": "B",
        "explanation": "Term life insurance provides coverage for a specific period (e.g., 10, 20, or 30 years). If you die during the term, your beneficiaries receive the death benefit."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens when a term life insurance policy expires?",
        "options": {
            "A": "You automatically get your money back",
            "B": "The coverage ends unless renewed (usually at higher rates)",
            "C": "It converts to whole life automatically",
            "D": "The death benefit doubles"
        },
        "correct_answer": "B",
        "explanation": "When a term policy expires, coverage ends. Many policies offer renewal options, but typically at significantly higher rates based on your current age."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Why is term life insurance generally less expensive than permanent insurance?",
        "options": {
            "A": "It provides less death benefit",
            "B": "It provides coverage for a limited time with no cash value accumulation",
            "C": "It's lower quality insurance",
            "D": "The insurance company loses money"
        },
        "correct_answer": "B",
        "explanation": "Term insurance is less expensive because it's temporary coverage with no cash value component. Most term policies never pay a death benefit because people outlive the term."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does 'level term' mean?",
        "options": {
            "A": "The death benefit and premium stay the same throughout the term",
            "B": "The premium increases each year",
            "C": "The death benefit decreases over time",
            "D": "Coverage level depends on your health"
        },
        "correct_answer": "A",
        "explanation": "Level term means both the death benefit and premium remain constant throughout the policy term, providing predictable coverage and costs."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Mike, age 30, just had his first child and wants to protect his family. He has a limited budget. What type of insurance would provide the most death benefit for his money?",
        "options": {
            "A": "Whole Life Insurance",
            "B": "Term Life Insurance",
            "C": "Final Expense Insurance",
            "D": "Disability Insurance"
        },
        "correct_answer": "B",
        "explanation": "Term life insurance provides the highest death benefit per premium dollar, making it ideal for young families on a budget who need maximum protection."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Sarah has a 30-year mortgage and wants to ensure her family can pay it off if she dies. What term length makes the most sense?",
        "options": {
            "A": "10-year term",
            "B": "15-year term",
            "C": "30-year term",
            "D": "Annual renewable term"
        },
        "correct_answer": "C",
        "explanation": "A 30-year term aligns with her mortgage length, ensuring coverage for the full duration of her debt obligation."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "When does a term life insurance policy begin providing coverage?",
        "options": {
            "A": "Immediately upon signing the application",
            "B": "When the policy is issued and the first premium is paid",
            "C": "30 days after the application",
            "D": "Only after a 6-month waiting period"
        },
        "correct_answer": "B",
        "explanation": "Coverage typically begins when the policy is issued by the carrier and the first premium has been paid. Some carriers may provide conditional coverage earlier."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "For whom is term life insurance MOST suitable?",
        "options": {
            "A": "Someone wanting lifelong coverage with cash value",
            "B": "Someone needing affordable coverage for a specific time period",
            "C": "Someone wanting to build retirement savings",
            "D": "Someone with no dependents or debts"
        },
        "correct_answer": "B",
        "explanation": "Term life is most suitable for those needing maximum coverage during a specific period, such as while raising children or paying off a mortgage."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "When determining the right term length for a client, what should you consider?",
        "options": {
            "A": "Only the client's age",
            "B": "How long their financial obligations and dependents will need protection",
            "C": "What term is cheapest",
            "D": "The agent's preference"
        },
        "correct_answer": "B",
        "explanation": "The term length should match the duration of the client's financial obligations (mortgage, children's dependency, etc.) and protection needs."
    },
])

# Term - Intermediate
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'conversion privilege' in a term life policy?",
        "options": {
            "A": "The ability to cancel the policy",
            "B": "The option to convert to permanent insurance without proof of insurability",
            "C": "Converting payments from monthly to annual",
            "D": "Changing the beneficiary"
        },
        "correct_answer": "B",
        "explanation": "The conversion privilege allows policyholders to convert their term policy to permanent insurance without medical underwriting, protecting their insurability even if health declines."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'Return of Premium' (ROP) term life insurance?",
        "options": {
            "A": "A policy that returns premiums to beneficiaries at death",
            "B": "A term policy that returns paid premiums if you outlive the term",
            "C": "A refund if you cancel early",
            "D": "Premium payments returned each year"
        },
        "correct_answer": "B",
        "explanation": "ROP term policies return your premium payments if you outlive the term. They cost more than standard term but provide a 'money back' feature."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "With Ethos term policies, what does 'accelerated death benefit' rider typically provide?",
        "options": {
            "A": "Faster claim processing",
            "B": "Access to a portion of the death benefit if diagnosed with a terminal illness",
            "C": "Higher death benefit",
            "D": "Reduced premiums"
        },
        "correct_answer": "B",
        "explanation": "An accelerated death benefit rider allows the insured to access a portion of their death benefit early if diagnosed with a terminal illness, providing living benefits."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What happens if an Aflac term policyholder misses a premium payment?",
        "options": {
            "A": "The policy cancels immediately",
            "B": "A grace period (usually 30-31 days) allows payment without losing coverage",
            "C": "The death benefit reduces",
            "D": "Interest accumulates on the missed payment"
        },
        "correct_answer": "B",
        "explanation": "Most term policies include a grace period (typically 30-31 days) during which a missed premium can be paid without policy lapse. Coverage continues during this period."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A couple, both age 35, has two children and wants life insurance. They're debating whether to get individual policies or a joint policy. What's a key consideration?",
        "options": {
            "A": "Joint policies are always cheaper",
            "B": "Individual policies provide separate coverage; joint 'first-to-die' only pays once",
            "C": "Insurance companies don't offer joint term",
            "D": "There is no difference"
        },
        "correct_answer": "B",
        "explanation": "Individual policies provide separate death benefits for each person. A joint first-to-die policy pays only once when the first spouse dies, leaving the survivor without coverage."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client with Kansas City Life term insurance is 5 years into a 20-year term and just got diagnosed with diabetes. They're worried about losing coverage. What do you tell them?",
        "options": {
            "A": "Their coverage will be cancelled",
            "B": "Their coverage continues as long as premiums are paid; consider conversion option",
            "C": "Their premium will increase immediately",
            "D": "They must apply for new insurance"
        },
        "correct_answer": "B",
        "explanation": "Once a term policy is in force, coverage continues regardless of health changes as long as premiums are paid. The conversion privilege becomes especially valuable since they can convert without proving insurability."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "An agent replaces a client's whole life policy with a 20-year term to 'free up cash flow.' The client is 62. What's the primary regulatory concern?",
        "options": {
            "A": "Replacement forms weren't filed",
            "B": "Suitability - client may outlive term coverage and be uninsurable",
            "C": "Agent didn't disclose commission difference",
            "D": "Term policies aren't appropriate for seniors"
        },
        "correct_answer": "B",
        "explanation": "The primary concern is suitability. At 62, the client may outlive a 20-year term (age 82) and be uninsurable or face prohibitive rates. The replacement eliminates permanent coverage."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is the 'contestability period' in a term life policy?",
        "options": {
            "A": "A period where you can contest the premium",
            "B": "Typically 2 years during which the insurer can investigate and deny claims for misrepresentation",
            "C": "The term of the policy",
            "D": "30 days to cancel"
        },
        "correct_answer": "B",
        "explanation": "The contestability period (typically 2 years) allows insurers to investigate claims and potentially deny them if material misrepresentation is found on the application."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A 55-year-old client wants 30-year term insurance. What suitability factors should you discuss?",
        "options": {
            "A": "No concerns, sell them what they want",
            "B": "Coverage would end at 85, cost increases with age; ensure 30-year term aligns with actual needs",
            "C": "30-year terms aren't available at age 55",
            "D": "Recommend a shorter term to save money"
        },
        "correct_answer": "B",
        "explanation": "At 55, a 30-year term takes coverage to age 85. Consider if this aligns with their needs, and note that premiums are higher at this age. Might permanent coverage be more suitable?"
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "How do you calculate the appropriate death benefit amount for a term policy?",
        "options": {
            "A": "Use the highest amount available",
            "B": "Consider income replacement, debts, education needs, and final expenses",
            "C": "Use 5x their salary for everyone",
            "D": "Ask what they can afford"
        },
        "correct_answer": "B",
        "explanation": "A proper needs analysis considers income replacement (10-12x income common), outstanding debts (mortgage, loans), children's education costs, and final expenses."
    },
])

# Term - Expert
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'decreasing term' policy and when might it be appropriate?",
        "options": {
            "A": "A policy with increasing premiums",
            "B": "Coverage where the death benefit decreases over time, often used for mortgage protection",
            "C": "A policy that decreases in cost each year",
            "D": "Term insurance that converts to less coverage"
        },
        "correct_answer": "B",
        "explanation": "Decreasing term has a death benefit that declines over the policy period, mirroring a declining debt like a mortgage. It's typically less expensive than level term."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Explain the difference between 'annual renewable term' (ART) and 'level term' insurance.",
        "options": {
            "A": "They are the same product",
            "B": "ART renews annually with increasing premiums based on attained age; level term has fixed premiums for the full term",
            "C": "ART is permanent insurance",
            "D": "Level term has increasing premiums"
        },
        "correct_answer": "B",
        "explanation": "ART renews each year without medical underwriting but premiums increase annually based on your attained age. Level term locks in a premium for the entire term (10, 20, 30 years)."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client owns a business valued at $2 million with three equal partners. They want 'buy-sell' protection. How would term insurance be structured?",
        "options": {
            "A": "Each partner buys a $2 million policy on their own life",
            "B": "Each partner buys policies on the other two partners, or use a cross-purchase or entity agreement",
            "C": "The business buys one policy on all partners",
            "D": "Life insurance isn't used for buy-sell"
        },
        "correct_answer": "B",
        "explanation": "Buy-sell agreements can be funded with life insurance through cross-purchase (partners own policies on each other) or entity (company owns policies). Each partner's share is funded by appropriate coverage amounts."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A high-income earner, age 45, with $3M net worth wants a $5M term policy for wealth transfer purposes. What strategy might you discuss?",
        "options": {
            "A": "Simply buy the policy in their name",
            "B": "Consider ownership by an Irrevocable Life Insurance Trust (ILIT) to exclude death benefit from estate",
            "C": "They don't need insurance with $3M net worth",
            "D": "Only permanent policies work for estate planning"
        },
        "correct_answer": "B",
        "explanation": "For clients with potential estate tax exposure, owning life insurance in an ILIT removes the death benefit from the taxable estate while providing liquidity for estate taxes or equalization among heirs."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is 'STOLI' (Stranger-Originated Life Insurance) and why is it illegal?",
        "options": {
            "A": "Life insurance sold by a stranger",
            "B": "Insurance obtained with intent to transfer to an investor who lacks insurable interest",
            "C": "Term insurance sold by unlicensed agents",
            "D": "A type of group life insurance"
        },
        "correct_answer": "B",
        "explanation": "STOLI involves obtaining insurance with the intent to sell or transfer the policy to someone without insurable interest (usually investors). It's illegal because it violates insurable interest requirements and is viewed as wagering on lives."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "A client wants to 'ladder' term policies. What is laddering and when is it appropriate?",
        "options": {
            "A": "Buying multiple small policies from different companies",
            "B": "Purchasing multiple term policies of different lengths to match declining coverage needs over time",
            "C": "Adding riders to a single policy",
            "D": "Converting term to permanent in stages"
        },
        "correct_answer": "B",
        "explanation": "Laddering involves buying multiple term policies with different term lengths (e.g., 10, 20, and 30-year) so coverage declines as financial obligations decrease, optimizing cost and coverage."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "A business owner wants 'key person' coverage on their irreplaceable sales director. What factors determine the appropriate amount?",
        "options": {
            "A": "The sales director's salary only",
            "B": "Loss of revenue, replacement costs, training time, and impact on business relationships",
            "C": "Whatever the business can afford",
            "D": "Standard 10x salary formula"
        },
        "correct_answer": "B",
        "explanation": "Key person coverage should account for lost revenue attributable to that person, cost of recruiting and training a replacement, transition period losses, and potential impact on customer/supplier relationships."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "A client has a substantial net worth but poor health. They need coverage but face high premiums. What strategy might help?",
        "options": {
            "A": "Lie on the application",
            "B": "Explore 'graded' or 'guaranteed issue' products, or impaired risk carriers specializing in hard-to-place cases",
            "C": "Tell them they can't get insurance",
            "D": "Wait until their health improves"
        },
        "correct_answer": "B",
        "explanation": "Options include guaranteed issue products (no medical questions), graded benefit policies, or carriers specializing in impaired risks who may offer better rates for specific conditions."
    },
])

# ==================== FINAL EXPENSE QUESTIONS ====================

# Final Expense - Easy
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is final expense insurance primarily designed to cover?",
        "options": {
            "A": "Income replacement for 20 years",
            "B": "Funeral costs, burial expenses, and final medical bills",
            "C": "College education for grandchildren",
            "D": "Business debts"
        },
        "correct_answer": "B",
        "explanation": "Final expense insurance is designed to cover end-of-life costs such as funeral expenses, burial/cremation, final medical bills, and small debts left behind."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a typical death benefit range for final expense policies?",
        "options": {
            "A": "$500,000 - $1,000,000",
            "B": "$2,000 - $50,000",
            "C": "$100 - $500",
            "D": "$1,000,000 - $5,000,000"
        },
        "correct_answer": "B",
        "explanation": "Final expense policies typically offer coverage between $2,000 and $50,000, designed to cover funeral costs and small final expenses, not income replacement."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Final expense insurance is a type of what kind of life insurance?",
        "options": {
            "A": "Term life insurance",
            "B": "Whole life insurance (permanent coverage)",
            "C": "Variable life insurance",
            "D": "Disability insurance"
        },
        "correct_answer": "B",
        "explanation": "Final expense is typically a form of whole life insurance, meaning it provides permanent coverage that lasts your entire lifetime with level premiums."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does 'simplified issue' mean in final expense insurance?",
        "options": {
            "A": "No questions asked",
            "B": "Approval based on health questions only, no medical exam required",
            "C": "Only simple people can apply",
            "D": "Coverage is simplified to burial only"
        },
        "correct_answer": "B",
        "explanation": "Simplified issue means approval is based on answering health questions without requiring a medical exam, making coverage more accessible for seniors."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Martha, age 68, wants to ensure her funeral doesn't burden her children financially. She's on a fixed income. What product might help?",
        "options": {
            "A": "A $500,000 IUL policy",
            "B": "Final expense insurance with affordable premiums",
            "C": "A 30-year term policy",
            "D": "A variable annuity"
        },
        "correct_answer": "B",
        "explanation": "Final expense insurance offers affordable premiums designed for seniors on fixed incomes, covering funeral costs without the high premiums of larger policies."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "John, 72, has health issues and thinks he can't get life insurance. What should you tell him about final expense options?",
        "options": {
            "A": "He's right, no insurance is available",
            "B": "Final expense often has guaranteed acceptance options for seniors with health issues",
            "C": "He must wait until he's healthier",
            "D": "Only term insurance is available to him"
        },
        "correct_answer": "B",
        "explanation": "Final expense insurance often includes guaranteed issue options that accept applicants regardless of health, making coverage available to seniors with health conditions."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What must you ensure when selling final expense to seniors?",
        "options": {
            "A": "Sell the largest policy possible",
            "B": "Ensure they understand the product and it's suitable for their needs and budget",
            "C": "Get family approval first",
            "D": "Only sell during business hours"
        },
        "correct_answer": "B",
        "explanation": "When selling to seniors, ensuring they fully understand what they're buying and that it's appropriate for their situation is critical for compliance and ethics."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "Final expense insurance is MOST suitable for someone who:",
        "options": {
            "A": "Needs $500,000 income replacement",
            "B": "Wants to ensure funeral costs don't burden family",
            "C": "Is looking for investment growth",
            "D": "Needs coverage for only 10 years"
        },
        "correct_answer": "B",
        "explanation": "Final expense is designed for those who want to ensure their end-of-life expenses are covered without burdening family members financially."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "When discussing final expense with a senior client, what should be your first focus?",
        "options": {
            "A": "Commissions",
            "B": "Understanding their concerns about being a burden to family",
            "C": "The application paperwork",
            "D": "Comparing to other products"
        },
        "correct_answer": "B",
        "explanation": "Understanding the client's emotional concern about burdening family with funeral costs creates connection and demonstrates you're focused on their needs."
    },
])

# Final Expense - Intermediate
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'graded death benefit' in final expense insurance?",
        "options": {
            "A": "Death benefit based on your grade level",
            "B": "Reduced death benefit in early years (typically 2-3 years), then full benefit after",
            "C": "A benefit that increases each year",
            "D": "Death benefit paid in installments"
        },
        "correct_answer": "B",
        "explanation": "Graded policies pay reduced benefits (often return of premium plus interest) if death occurs in the first 2-3 years. After the waiting period, the full death benefit is payable."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "How does 'modified' final expense differ from 'graded'?",
        "options": {
            "A": "They are the same thing",
            "B": "Modified typically returns premiums plus interest in year 1, graded may return only premiums; both transition to full benefit",
            "C": "Modified has higher death benefits",
            "D": "Graded has no waiting period"
        },
        "correct_answer": "B",
        "explanation": "While similar, modified and graded policies differ in exact benefits during the waiting period. Carriers define these terms differently, so always check specific policy provisions."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "United Home Life offers final expense products. What makes their 'Level' product different from their 'Graded' product?",
        "options": {
            "A": "No difference",
            "B": "Level provides immediate full death benefit; Graded has a waiting period before full benefits",
            "C": "Level is only for healthy applicants",
            "D": "Graded has higher premiums"
        },
        "correct_answer": "B",
        "explanation": "Level final expense provides full death benefit from day one for applicants who qualify medically. Graded is for those with health issues who don't qualify for Level, with restricted benefits initially."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "Why might American Amicable's final expense have different underwriting 'tiers'?",
        "options": {
            "A": "To confuse agents",
            "B": "Different tiers (Preferred, Standard, Graded) allow pricing based on health profile",
            "C": "All applicants get the same rate",
            "D": "Tiers only affect cash value"
        },
        "correct_answer": "B",
        "explanation": "Underwriting tiers allow carriers to offer better rates to healthier applicants while still providing coverage options (often graded) for those with health conditions."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client age 70 with diabetes and heart medication wants final expense. What product type is most likely available?",
        "options": {
            "A": "Level immediate coverage",
            "B": "Graded or modified benefit product with waiting period",
            "C": "No coverage available",
            "D": "Only term insurance"
        },
        "correct_answer": "B",
        "explanation": "With diabetes and heart medication, this client would likely qualify for a graded or modified final expense product with a waiting period before full benefits, not immediate level coverage."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A 75-year-old client already has a small whole life policy from 30 years ago but wants more coverage. What do you recommend?",
        "options": {
            "A": "Replace the old policy with a new one",
            "B": "Keep the existing policy (already past contestability, level premium); add final expense as supplemental coverage",
            "C": "Cancel both policies",
            "D": "Wait until they're older"
        },
        "correct_answer": "B",
        "explanation": "The existing policy has value (past contestability, likely low premium from younger age). Adding a supplemental final expense policy increases total coverage without losing existing benefits."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "When selling final expense, what's a common 'red flag' that might indicate an unsuitable sale?",
        "options": {
            "A": "Client understands the product",
            "B": "Premium consumes excessive percentage of fixed income or client shows confusion",
            "C": "Client has named beneficiaries",
            "D": "Premium is affordable"
        },
        "correct_answer": "B",
        "explanation": "Red flags include premiums that would strain the client's budget, client confusion about what they're buying, or pressure tactics. Suitability requires the product to be affordable and understood."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What special considerations apply when a senior has a caregiver present during the sale?",
        "options": {
            "A": "Ignore the caregiver",
            "B": "Ensure the senior independently understands and consents; watch for undue influence",
            "C": "Have the caregiver sign instead",
            "D": "Only speak to the caregiver"
        },
        "correct_answer": "B",
        "explanation": "The applicant must independently understand and consent to the purchase. Be alert to situations where a caregiver may be exerting undue influence over a vulnerable senior."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A client wants to name their favorite charity as beneficiary of their final expense policy. Is this suitable?",
        "options": {
            "A": "No, beneficiaries must be family",
            "B": "Yes, if the client's funeral costs are otherwise covered; any beneficiary is allowed",
            "C": "Only with court approval",
            "D": "Charities cannot receive insurance proceeds"
        },
        "correct_answer": "B",
        "explanation": "Clients can name any beneficiary they choose. If their funeral is otherwise provided for (prepaid, family will cover, etc.), naming a charity is perfectly acceptable."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client says, 'My kids will just pay for my funeral.' How do you respond?",
        "options": {
            "A": "Okay, you don't need insurance then.",
            "B": "Have you discussed this with them? Do they have $10,000-$15,000 readily available? How would you feel if that burden fell on them?",
            "C": "Your kids should buy you a policy.",
            "D": "That's not possible."
        },
        "correct_answer": "B",
        "explanation": "This response prompts reflection on whether this assumption is realistic and explores the emotional aspect of burdening children, using questions rather than assertions."
    },
])

# Final Expense - Expert
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Explain 'accidental death benefit' riders common in final expense products.",
        "options": {
            "A": "Pays double for any death",
            "B": "Pays additional benefit (often double) if death results from an accident",
            "C": "Only pays if death is accidental",
            "D": "Reduces premium for safe behavior"
        },
        "correct_answer": "B",
        "explanation": "The accidental death benefit rider pays an additional amount (often equal to the base death benefit, effectively doubling it) if the insured dies as a result of an accident."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Some final expense carriers offer 'nursing home waiver' riders. What does this provide?",
        "options": {
            "A": "Free nursing home care",
            "B": "Premiums are waived if the insured is confined to a nursing home for a specified period",
            "C": "Death benefit increases in nursing homes",
            "D": "Coverage only applies in nursing homes"
        },
        "correct_answer": "B",
        "explanation": "A nursing home waiver rider waives premium payments if the insured becomes confined to a nursing home for a specified period (often 90+ days), keeping the policy in force without payment."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does 'guaranteed issue' final expense underwriting work, and what's the trade-off?",
        "options": {
            "A": "Full coverage immediately for anyone",
            "B": "No health questions, but typically graded benefits and higher premiums",
            "C": "Same as fully underwritten policies",
            "D": "Requires extensive medical records"
        },
        "correct_answer": "B",
        "explanation": "Guaranteed issue accepts all applicants without health questions, but typically comes with graded benefits (waiting period for full death benefit) and higher premiums to account for increased risk."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client with end-stage COPD wants coverage. They understand they may not survive the graded period. Is this sale ethical?",
        "options": {
            "A": "No, never sell if they might not survive",
            "B": "If they understand the graded benefits, want the coverage anyway, and can afford it, it can be ethical",
            "C": "Only with doctor approval",
            "D": "The carrier would never approve this"
        },
        "correct_answer": "B",
        "explanation": "If the client fully understands they may only receive return of premium plus interest if dying during the graded period, and they still want the coverage for peace of mind or the possibility of surviving, this can be an informed, ethical decision."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client receives SSI (Supplemental Security Income). How might final expense proceeds affect their benefits?",
        "options": {
            "A": "No effect on any benefits",
            "B": "If naming estate or direct payment, proceeds could affect SSI eligibility; consider assignment or irrevocable beneficiary",
            "C": "SSI recipients can't have life insurance",
            "D": "All proceeds are automatically exempt"
        },
        "correct_answer": "B",
        "explanation": "SSI has asset limits. Insurance proceeds paid to the estate or beneficiary could affect eligibility. Assigning the policy to a funeral home or using proper planning can help protect benefits."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is 'churning' and why is it especially problematic in the final expense market?",
        "options": {
            "A": "Rapid product development",
            "B": "Replacing existing policies for commission purposes, especially harmful as seniors lose insurability and face new waiting periods",
            "C": "Selling too many policies",
            "D": "A type of policy loan"
        },
        "correct_answer": "B",
        "explanation": "Churning involves replacing policies primarily for new commissions. In final expense, this is particularly harmful because seniors may restart graded/waiting periods and won't live long enough to benefit from the new policy."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "Your state has specific 'senior protection' regulations for insurance sales. What typically must you do?",
        "options": {
            "A": "No special requirements",
            "B": "Enhanced suitability documentation, possibly recording conversations or additional disclosures",
            "C": "Only sell to people under 65",
            "D": "Get family approval for all sales"
        },
        "correct_answer": "B",
        "explanation": "Many states have enhanced requirements for selling to seniors including additional suitability documentation, possible recording of presentations, extended free look periods, and special disclosures."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "A client wants $30,000 in final expense coverage. Average funeral costs are $10,000-$15,000. How do you assess suitability?",
        "options": {
            "A": "Sell them $30,000 - client is always right",
            "B": "Explore their reasoning - additional debts, legacy goals, or over-insurance? Match coverage to actual needs",
            "C": "Tell them they're wrong",
            "D": "Refuse the sale"
        },
        "correct_answer": "B",
        "explanation": "Understand why they want $30,000. There may be legitimate reasons (debts, legacy wishes) or they may not realize funeral costs are lower. Ensure coverage matches actual needs and budget."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "A client's adult child is present and keeps answering questions for the parent. How should you handle this?",
        "options": {
            "A": "Continue with the child answering",
            "B": "Politely redirect questions to the applicant; ensure the applicant understands and is making independent decisions",
            "C": "Have the child become the applicant",
            "D": "Leave immediately"
        },
        "correct_answer": "B",
        "explanation": "The applicant must demonstrate understanding and independent decision-making. Politely ensure the senior is responding to questions themselves and comprehends the product."
    },
])

# Add unique IDs to all questions
for q in QUESTIONS:
    q['id'] = str(uuid.uuid4())
    q['created_at'] = datetime.now(timezone.utc).isoformat()


async def seed_questions():
    """Seed the quiz questions database"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check if questions already exist
    existing_count = await db.quiz_questions.count_documents({})
    
    if existing_count > 0:
        print(f"Database already has {existing_count} questions. Skipping seed.")
        print("To re-seed, manually clear the quiz_questions collection first.")
        client.close()
        return
    
    # Insert all questions
    if QUESTIONS:
        await db.quiz_questions.insert_many(QUESTIONS)
        print(f"Successfully seeded {len(QUESTIONS)} quiz questions!")
        
        # Print breakdown
        for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
            for difficulty in ['Easy', 'Intermediate', 'Expert']:
                count = len([q for q in QUESTIONS if q['product'] == product and q['difficulty'] == difficulty])
                print(f"  {product} - {difficulty}: {count} questions")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_questions())
