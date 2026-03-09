"""
Additional Quiz Questions for Breeze Matrix
Adds more questions to reach ~250 total
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

ADDITIONAL_QUESTIONS = []

# ==================== MORE IUL QUESTIONS ====================

ADDITIONAL_QUESTIONS.extend([
    # Easy
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the 'cost of insurance' (COI) in an IUL policy?",
        "options": {
            "A": "The total premium you pay",
            "B": "The internal charge for the death benefit protection",
            "C": "The surrender charge",
            "D": "The agent's commission"
        },
        "correct_answer": "B",
        "explanation": "The cost of insurance (COI) is the internal charge deducted from your policy for the actual death benefit protection. It increases as you age."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Lisa, 40, wants both life insurance protection and a way to supplement retirement income. Which feature of IUL addresses her retirement goal?",
        "options": {
            "A": "The death benefit",
            "B": "Tax-free policy loans from accumulated cash value",
            "C": "The surrender charges",
            "D": "The premium flexibility"
        },
        "correct_answer": "B",
        "explanation": "IUL's tax-free policy loans allow Lisa to access cash value during retirement to supplement her income, making it a dual-purpose financial tool."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What must an agent provide to every IUL client before the sale?",
        "options": {
            "A": "Their personal cell phone number",
            "B": "A policy illustration showing how the policy may perform",
            "C": "A guarantee of minimum returns",
            "D": "Comparison to competitor products"
        },
        "correct_answer": "B",
        "explanation": "Agents must provide a policy illustration that shows how the policy may perform under various scenarios, as required by state regulations."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "Which client would be the BEST fit for an IUL policy?",
        "options": {
            "A": "Someone who needs coverage for only 5 years",
            "B": "Someone seeking permanent protection with growth potential and flexibility",
            "C": "Someone who wants guaranteed fixed returns",
            "D": "Someone looking for the absolute lowest premium"
        },
        "correct_answer": "B",
        "explanation": "IUL is ideal for clients seeking permanent coverage with cash value growth potential tied to market indices, along with premium flexibility."
    },
    # Intermediate
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What happens to the cash value in an IUL if the index returns 0% for the year?",
        "options": {
            "A": "Cash value decreases significantly",
            "B": "Cash value earns 0%, but policy charges still apply",
            "C": "Cash value is guaranteed to increase",
            "D": "The policy lapses automatically"
        },
        "correct_answer": "B",
        "explanation": "With a 0% floor, the indexed account earns 0% in a flat or down market. However, policy charges (COI, fees) still apply, which can reduce total cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the 'fixed account' option in most IUL policies?",
        "options": {
            "A": "A way to fix mistakes on the application",
            "B": "An alternative allocation earning a declared fixed interest rate",
            "C": "A fixed death benefit amount",
            "D": "Fixed premium payments"
        },
        "correct_answer": "B",
        "explanation": "Most IULs offer a fixed account option where you can allocate some or all premium to earn a declared interest rate, separate from index performance."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client funded their National Life IUL heavily upfront and received notice about MEC status. What does this mean for tax purposes?",
        "options": {
            "A": "Nothing changes",
            "B": "Policy loans and withdrawals may be taxable and subject to penalties before age 59½",
            "C": "The death benefit becomes taxable",
            "D": "Premiums are now tax-deductible"
        },
        "correct_answer": "B",
        "explanation": "If a policy becomes a MEC, loans and withdrawals are taxed as income (gains first) and may incur a 10% penalty if taken before age 59½."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "When illustrating an IUL, what must be shown alongside non-guaranteed values?",
        "options": {
            "A": "Only best-case projections",
            "B": "Guaranteed values showing minimum performance",
            "C": "Historical stock market returns",
            "D": "Competitor product comparisons"
        },
        "correct_answer": "B",
        "explanation": "Regulations require showing guaranteed values alongside non-guaranteed projections so clients understand both the floor and potential outcomes."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client asks, 'What if I can't afford premiums for a while?' What IUL feature addresses this concern?",
        "options": {
            "A": "The policy automatically cancels",
            "B": "Premium flexibility allows skipping payments if sufficient cash value exists",
            "C": "The insurance company will pay premiums",
            "D": "Premiums are always fixed and must be paid"
        },
        "correct_answer": "B",
        "explanation": "IUL's premium flexibility means you can skip or reduce payments if your cash value can cover policy costs, though this uses up cash value."
    },
    # Expert
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does 'index arbitrage' or 'loan arbitrage' work in an IUL?",
        "options": {
            "A": "Buying and selling the policy",
            "B": "Taking loans at a fixed rate while collateralized cash value continues earning index credits",
            "C": "Comparing multiple indices",
            "D": "Transferring between insurance companies"
        },
        "correct_answer": "B",
        "explanation": "With certain loan types, borrowed cash value may continue earning index credits while you pay a fixed loan rate, potentially creating positive arbitrage if index returns exceed loan costs."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A business owner wants to use IUL for informal 'golden handcuffs' retention. What strategy might be employed?",
        "options": {
            "A": "Give the employee cash",
            "B": "Business owns the policy on key employee; policy cash value vests over time as retention incentive",
            "C": "Employee buys their own policy",
            "D": "Use term insurance instead"
        },
        "correct_answer": "B",
        "explanation": "The company can own an IUL on a key employee, with an agreement to transfer ownership or policy benefits as they vest over time, incentivizing retention."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is 'rebating' and why is it prohibited in life insurance sales?",
        "options": {
            "A": "Reducing the death benefit",
            "B": "Offering inducements like commission kickbacks to encourage purchase, which is illegal",
            "C": "Providing policy illustrations",
            "D": "Charging higher premiums"
        },
        "correct_answer": "B",
        "explanation": "Rebating involves giving clients part of your commission or other inducements to buy, which is illegal in most states because it can lead to unfair practices and pricing distortions."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "What key factors determine whether max-funding an IUL is appropriate?",
        "options": {
            "A": "Only the client's age",
            "B": "Time horizon, need for death benefit, risk tolerance, and understanding of MEC rules",
            "C": "The agent's commission",
            "D": "Current stock market conditions"
        },
        "correct_answer": "B",
        "explanation": "Max-funding requires considering whether the client has a long time horizon, appropriate death benefit needs, tolerance for variability, and clear understanding of MEC implications."
    },
])

# ==================== MORE FIA QUESTIONS ====================

ADDITIONAL_QUESTIONS.extend([
    # Easy
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is 'tax-deferred growth' in a FIA?",
        "options": {
            "A": "You never pay taxes",
            "B": "Taxes on gains are postponed until you withdraw money",
            "C": "The government pays your taxes",
            "D": "Taxes are calculated differently"
        },
        "correct_answer": "B",
        "explanation": "Tax-deferred growth means you don't pay taxes on FIA gains each year. Taxes are due only when you withdraw money, allowing your full balance to compound."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Bob, 58, is 7 years from retirement. He has maxed out his 401(k) and IRA. He wants more tax-advantaged savings. Could a FIA help?",
        "options": {
            "A": "No, FIAs don't provide tax advantages",
            "B": "Yes, FIA provides additional tax-deferred growth with no contribution limits",
            "C": "Only if he's over 70",
            "D": "He should just use a regular savings account"
        },
        "correct_answer": "B",
        "explanation": "FIAs offer tax-deferred growth without contribution limits, making them excellent for supplementing maxed-out retirement accounts."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What is the 'free withdrawal' provision in most FIAs?",
        "options": {
            "A": "All withdrawals are free",
            "B": "A percentage (often 10%) you can withdraw annually without surrender charges",
            "C": "Withdrawals are free after age 70",
            "D": "The first withdrawal each year is always free"
        },
        "correct_answer": "B",
        "explanation": "Most FIAs allow you to withdraw a certain percentage (typically 10%) of your account value annually without incurring surrender charges."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "What makes FIAs suitable for conservative investors?",
        "options": {
            "A": "High growth potential with high risk",
            "B": "Principal protection with growth linked to market indices",
            "C": "Guaranteed 10% annual returns",
            "D": "No fees or charges"
        },
        "correct_answer": "B",
        "explanation": "FIAs suit conservative investors because they offer principal protection (0% floor) while still providing growth opportunity linked to market indices."
    },
    # Intermediate
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'annuitization' and how does it differ from using an income rider?",
        "options": {
            "A": "They are identical",
            "B": "Annuitization converts your account to lifetime payments, giving up access to principal; income riders provide income while maintaining account access",
            "C": "Income riders provide higher payments",
            "D": "Annuitization is only for qualified funds"
        },
        "correct_answer": "B",
        "explanation": "Annuitization trades your account for guaranteed lifetime payments but you lose access to the lump sum. Income riders provide income while preserving access to your account value."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What does 'withdrawal charge' (or surrender charge) typically look like in a 10-year FIA?",
        "options": {
            "A": "Flat 10% throughout",
            "B": "Declining scale (e.g., 10%, 9%, 8%...1%, 0%) over the surrender period",
            "C": "Increasing each year",
            "D": "No charges ever apply"
        },
        "correct_answer": "B",
        "explanation": "Surrender charges typically start higher and decline each year until they reach zero at the end of the surrender period."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A 63-year-old client wants income starting at 70. Their Americo FIA has an income rider with 7% roll-up. How does this benefit them?",
        "options": {
            "A": "Their account value grows 7% annually",
            "B": "Their income benefit base grows 7% annually during deferral, increasing future income payments",
            "C": "They receive 7% payments immediately",
            "D": "The surrender charges reduce by 7%"
        },
        "correct_answer": "B",
        "explanation": "The 7% roll-up grows the income benefit base (not cash value) each year during deferral, resulting in higher lifetime income payments when they start withdrawals."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is 'suitability review' in the context of FIA sales?",
        "options": {
            "A": "Making sure the product fits what you want to sell",
            "B": "Evaluating whether the product matches the client's financial situation, needs, and objectives",
            "C": "Checking the application for errors",
            "D": "Reviewing the surrender schedule"
        },
        "correct_answer": "B",
        "explanation": "Suitability review ensures the product appropriately matches the client's age, income, financial situation, investment objectives, risk tolerance, and liquidity needs."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client mentions they have CDs earning 3%. How might you position a FIA?",
        "options": {
            "A": "FIAs always beat CDs",
            "B": "Discuss potential for higher returns linked to indices while maintaining principal safety, considering surrender period vs. CD maturity",
            "C": "Tell them CDs are worthless",
            "D": "Don't mention FIAs"
        },
        "correct_answer": "B",
        "explanation": "Position FIAs honestly: potential for better returns than CDs with similar principal safety, but explain the trade-off of longer surrender periods versus CD flexibility."
    },
    # Expert
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Explain how 'rate lock' works when renewing crediting terms in a FIA.",
        "options": {
            "A": "Your rate is locked forever",
            "B": "At renewal, you may lock in new rates or stay with declared rates, affecting future segments",
            "C": "Rate lock eliminates all fees",
            "D": "Only available at purchase"
        },
        "correct_answer": "B",
        "explanation": "When crediting terms renew (often annually), you may have options to accept new declared rates or lock in rates for your next segment. Understanding this timing helps optimize crediting strategy."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client inherits an IRA and wants to stretch distributions. Can they use a FIA and what should they know?",
        "options": {
            "A": "FIAs can't hold inherited IRA funds",
            "B": "Inherited IRAs can be placed in a FIA but must follow inherited IRA RMD rules; surrender charges could complicate required distributions",
            "C": "All inherited IRA rules are waived in FIAs",
            "D": "The FIA converts it to a regular IRA"
        },
        "correct_answer": "B",
        "explanation": "Inherited IRAs can fund a FIA, but RMD rules still apply. The surrender period must be coordinated with distribution requirements to avoid unexpected charges."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "Under best interest regulations, what documentation must typically accompany a FIA sale?",
        "options": {
            "A": "No special documentation",
            "B": "Recommendation rationale, suitability forms, product disclosure, and documentation of alternatives considered",
            "C": "Only the application",
            "D": "Just the client's signature"
        },
        "correct_answer": "B",
        "explanation": "Best interest compliance typically requires documenting why the product is in the client's best interest, alternatives considered, all material information disclosed, and how it meets their needs."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "When might a shorter surrender period FIA be more suitable even if rates are lower?",
        "options": {
            "A": "Never, longer surrender is always better",
            "B": "When the client has uncertain liquidity needs or health concerns affecting life expectancy",
            "C": "Only for younger clients",
            "D": "When rates are exactly equal"
        },
        "correct_answer": "B",
        "explanation": "Clients with uncertain liquidity needs, health issues, or shorter time horizons may benefit from shorter surrender periods despite lower rates, ensuring access to funds when needed."
    },
])

# ==================== MORE TERM LIFE QUESTIONS ====================

ADDITIONAL_QUESTIONS.extend([
    # Easy
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What are the most common term lengths available?",
        "options": {
            "A": "1, 2, and 3 years",
            "B": "10, 15, 20, 25, and 30 years",
            "C": "Only 99 years",
            "D": "6 months and 1 year"
        },
        "correct_answer": "B",
        "explanation": "The most common term lengths are 10, 15, 20, 25, and 30 years, allowing clients to match coverage to their specific needs."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "A single person with no dependents asks about life insurance. Do they need term coverage?",
        "options": {
            "A": "Everyone must have life insurance",
            "B": "They may need less or none, unless covering debts or funeral costs - assess individual needs",
            "C": "Single people can't buy insurance",
            "D": "They need more coverage than families"
        },
        "correct_answer": "B",
        "explanation": "Life insurance needs are based on financial obligations and dependents. Someone without dependents may need minimal coverage for debts or final expenses, or possibly none at all."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What information is typically required on a term life insurance application?",
        "options": {
            "A": "Only name and address",
            "B": "Personal information, health history, lifestyle questions, and beneficiary designation",
            "C": "Just a signature",
            "D": "Only financial information"
        },
        "correct_answer": "B",
        "explanation": "Term applications require comprehensive information including identity, health history, lifestyle factors (smoking, dangerous activities), and beneficiary details for underwriting."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "What is the main advantage of term life over permanent life insurance?",
        "options": {
            "A": "Cash value accumulation",
            "B": "Lower premiums for higher coverage amounts",
            "C": "Lifetime protection",
            "D": "Investment returns"
        },
        "correct_answer": "B",
        "explanation": "Term's main advantage is cost-effectiveness: you get significantly more death benefit per premium dollar compared to permanent insurance."
    },
    # Intermediate
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'guaranteed renewable' in term insurance?",
        "options": {
            "A": "Guaranteed low premiums forever",
            "B": "The right to renew coverage without proving insurability, though premiums will increase",
            "C": "Automatic renewal at the same rate",
            "D": "The policy renews every month"
        },
        "correct_answer": "B",
        "explanation": "Guaranteed renewable means you can continue coverage after the initial term without medical underwriting, but premiums will be based on your attained age (much higher)."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "Why do some term policies cost more than others for the same coverage?",
        "options": {
            "A": "All term policies cost the same",
            "B": "Differences in underwriting criteria, conversion options, riders, and carrier ratings affect pricing",
            "C": "Only agent commission differs",
            "D": "Coverage amounts are never the same"
        },
        "correct_answer": "B",
        "explanation": "Pricing varies based on the carrier's underwriting categories, included features (conversion privileges, riders), financial strength rating, and competitive positioning."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client says they want 'just enough insurance to cover the mortgage.' What else should you discuss?",
        "options": {
            "A": "That's all they need",
            "B": "Also consider income replacement, other debts, children's education, and final expenses",
            "C": "Mortgages don't require insurance",
            "D": "Only recommend final expense"
        },
        "correct_answer": "B",
        "explanation": "While mortgage coverage is important, a complete needs analysis should include income replacement, other debts, children's future needs, and final expenses."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is 'insurable interest' and why is it required for term life insurance?",
        "options": {
            "A": "Interest earned on the policy",
            "B": "A financial interest in the insured's continued life, required to prevent wagering on lives",
            "C": "The interest rate on premiums",
            "D": "Interest in buying insurance"
        },
        "correct_answer": "B",
        "explanation": "Insurable interest means the policy owner must have a genuine financial interest in the insured's life. It's required at policy inception to prevent purchasing insurance as a gambling contract."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "A client wants term insurance but is concerned about what happens when it expires. What options can you discuss?",
        "options": {
            "A": "Nothing happens, you lose everything",
            "B": "Renewal at higher rates, conversion to permanent insurance, or purchasing a new policy",
            "C": "Term insurance never expires",
            "D": "They get a refund"
        },
        "correct_answer": "B",
        "explanation": "Options at term expiration include renewing at higher rates (if guaranteed renewable), converting to permanent insurance (if conversion option exists), or applying for a new policy if still insurable."
    },
    # Expert
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'living benefit' rider and how does it work on term policies?",
        "options": {
            "A": "A benefit for healthy living",
            "B": "Allows access to death benefit funds if diagnosed with terminal, chronic, or critical illness",
            "C": "Only available on permanent policies",
            "D": "Provides monthly income while living"
        },
        "correct_answer": "B",
        "explanation": "Living benefit riders (accelerated death benefits) allow the insured to access a portion of the death benefit early if diagnosed with qualifying conditions like terminal or chronic illness."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "An attorney client asks about a 'life settlement' for their term policy. What should you know?",
        "options": {
            "A": "Term policies can't be settled",
            "B": "Convertible term policies may be eligible for life settlement; understanding this can add value for seniors",
            "C": "Life settlements are illegal",
            "D": "Settlements only apply to permanent insurance"
        },
        "correct_answer": "B",
        "explanation": "Some term policies, especially convertible ones, may qualify for life settlement if the insured is older with health changes. The term is converted to permanent and then sold."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What disclosure is required when recommending term insurance to a client who has an existing permanent policy?",
        "options": {
            "A": "No disclosure needed",
            "B": "Full replacement disclosure if surrendering permanent for term; comparison of costs, benefits, and potential gaps",
            "C": "Only verbal disclosure",
            "D": "Disclosure that term is always better"
        },
        "correct_answer": "B",
        "explanation": "Replacing permanent with term requires comprehensive replacement disclosure including comparison of both policies, potential loss of cash value, and any coverage gaps."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "When evaluating term insurance for a client, why is it important to understand their complete financial picture?",
        "options": {
            "A": "It's not important, just sell the policy",
            "B": "To ensure coverage amount, term length, and premium fit their overall financial plan and goals",
            "C": "Only to determine premium affordability",
            "D": "To sell them more products"
        },
        "correct_answer": "B",
        "explanation": "Understanding the complete financial picture ensures the term policy integrates appropriately with other assets, debts, insurance, and long-term goals rather than existing in isolation."
    },
])

# ==================== MORE FINAL EXPENSE QUESTIONS ====================

ADDITIONAL_QUESTIONS.extend([
    # Easy
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the typical age range for final expense applicants?",
        "options": {
            "A": "18-30",
            "B": "50-85",
            "C": "Under 18 only",
            "D": "Over 100 only"
        },
        "correct_answer": "B",
        "explanation": "Final expense insurance is typically marketed to seniors ages 50-85, though exact age limits vary by carrier."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Virginia, 73, wants to leave money for her church. Can final expense insurance help?",
        "options": {
            "A": "No, only family can be beneficiaries",
            "B": "Yes, she can name her church as beneficiary",
            "C": "Only if the church is a registered charity",
            "D": "Insurance companies don't allow this"
        },
        "correct_answer": "B",
        "explanation": "Policyholders can name any person or organization as beneficiary, including churches and charities."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "Why is it important to explain the policy clearly to senior clients?",
        "options": {
            "A": "It's not that important",
            "B": "To ensure they understand what they're buying and it meets their needs, avoiding misunderstandings",
            "C": "Only to meet a time requirement",
            "D": "So they buy more coverage"
        },
        "correct_answer": "B",
        "explanation": "Clear explanation ensures informed consent, meets regulatory requirements, and helps ensure the product truly fits the client's needs and budget."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "What makes final expense insurance different from traditional whole life?",
        "options": {
            "A": "Nothing, they're identical",
            "B": "Final expense has simplified underwriting, smaller face amounts, and targets end-of-life needs",
            "C": "Final expense costs more",
            "D": "Traditional whole life is for funerals only"
        },
        "correct_answer": "B",
        "explanation": "Final expense features simplified underwriting (no exams), smaller death benefits ($2,000-$50,000), and is specifically designed for burial and final expense needs."
    },
    # Intermediate
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'assignment' of a final expense policy to a funeral home?",
        "options": {
            "A": "Illegal transfer of policy",
            "B": "Directing benefits to pay the funeral home directly upon death",
            "C": "Selling the policy",
            "D": "Changing the owner to the funeral home"
        },
        "correct_answer": "B",
        "explanation": "Assignment allows death benefits to be paid directly to a funeral home, ensuring funeral costs are covered. This can also help protect benefits from affecting need-based programs."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What distinguishes American Amicable's 'Level' final expense from their 'Graded' product?",
        "options": {
            "A": "Price only",
            "B": "Level provides immediate full death benefit; Graded has limited benefits during initial years",
            "C": "Graded has higher death benefits",
            "D": "Level requires a medical exam"
        },
        "correct_answer": "B",
        "explanation": "Level products provide full death benefit from day one for those who qualify. Graded products, for those with health issues, have restricted benefits (often return of premium only) in the first 2-3 years."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client mentions they receive Medicaid. How might this affect the final expense policy?",
        "options": {
            "A": "No effect at all",
            "B": "Benefits paid to their estate could affect Medicaid eligibility; consider irrevocable beneficiary or assignment",
            "C": "Medicaid recipients can't have insurance",
            "D": "Medicaid pays for the insurance"
        },
        "correct_answer": "B",
        "explanation": "Medicaid has asset limits. Proceeds paid to the estate could affect eligibility. Using irrevocable beneficiaries or funeral home assignment can help protect benefits."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "What is 'twisting' and why is it especially concerning in final expense sales?",
        "options": {
            "A": "A sales technique",
            "B": "Using misrepresentation to convince clients to replace existing coverage, harming them financially",
            "C": "Signing up clients quickly",
            "D": "A type of policy rider"
        },
        "correct_answer": "B",
        "explanation": "Twisting involves misrepresenting facts to induce replacement of existing insurance. In final expense, this can restart waiting periods and leave seniors without full coverage they previously had."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "During a presentation, a client becomes confused about the difference between their account value and death benefit. How do you clarify?",
        "options": {
            "A": "They're the same thing",
            "B": "Death benefit is what beneficiaries receive; cash value (if any) is what you could access while living",
            "C": "Don't explain, just proceed",
            "D": "Tell them to ask their family"
        },
        "correct_answer": "B",
        "explanation": "Clearly explain that the death benefit is paid to beneficiaries upon death, while cash value (which may be minimal in final expense) is what they could access during their lifetime."
    },
    # Expert
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "Some final expense carriers offer 'terminal illness' acceleration. How does this differ from standard accelerated death benefits?",
        "options": {
            "A": "They're identical",
            "B": "Final expense terminal acceleration may have different trigger definitions and payout percentages than traditional policies",
            "C": "Only available on larger policies",
            "D": "Terminal illness isn't covered"
        },
        "correct_answer": "B",
        "explanation": "While both provide early access to death benefits, final expense terminal illness riders may have different definitions (e.g., 12 vs. 24 month life expectancy) and maximum payout amounts."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client in a nursing home wants final expense coverage. What special considerations apply?",
        "options": {
            "A": "They can't get coverage",
            "B": "Many carriers have nursing home exclusions; find carriers that will cover, verify competency, and ensure the sale is appropriate",
            "C": "Nursing homes buy coverage for residents",
            "D": "Coverage is automatic for nursing home residents"
        },
        "correct_answer": "B",
        "explanation": "Many carriers won't issue to nursing home residents. If coverage is available, ensure the client is competent to consent, the sale is appropriate, and there's no undue influence."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What documentation might be required when selling final expense in states with enhanced senior protections?",
        "options": {
            "A": "No special documentation",
            "B": "Suitability worksheets, possibly recorded presentations, disclosure forms, and enhanced free-look periods",
            "C": "Only a standard application",
            "D": "Family member co-signature"
        },
        "correct_answer": "B",
        "explanation": "States with enhanced senior protections may require additional documentation including detailed suitability forms, recorded presentations, specific disclosures, and extended free-look periods."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "How do you determine appropriate coverage amount for final expense?",
        "options": {
            "A": "Always sell the maximum available",
            "B": "Calculate expected funeral costs, small debts, medical bills, and any desired legacy minus existing resources",
            "C": "Use a standard $10,000 for everyone",
            "D": "Whatever the client can afford monthly"
        },
        "correct_answer": "B",
        "explanation": "Appropriate coverage considers estimated funeral costs, any small debts, potential final medical bills, and desired legacy, offset by existing resources or coverage."
    },
])

# Add unique IDs to all questions
for q in ADDITIONAL_QUESTIONS:
    q['id'] = str(uuid.uuid4())
    q['created_at'] = datetime.now(timezone.utc).isoformat()


async def seed_additional_questions():
    """Add more questions to reach ~250 total"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Insert additional questions
    if ADDITIONAL_QUESTIONS:
        await db.quiz_questions.insert_many(ADDITIONAL_QUESTIONS)
        
        # Count total
        total = await db.quiz_questions.count_documents({})
        print(f"Added {len(ADDITIONAL_QUESTIONS)} more questions. Total now: {total}")
        
        # Print breakdown
        for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
            for difficulty in ['Easy', 'Intermediate', 'Expert']:
                count = await db.quiz_questions.count_documents({
                    'product': product,
                    'difficulty': difficulty
                })
                print(f"  {product} - {difficulty}: {count} questions")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_additional_questions())
