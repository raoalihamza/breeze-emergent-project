"""
Additional Quiz Questions - 150 New Product Knowledge Questions
Tailored to product type and difficulty level
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

QUESTIONS = []

# ==================== IUL QUESTIONS (38 total) ====================

# IUL - Easy (13 questions)
QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What type of life insurance is an IUL?",
        "options": {
            "A": "Term life insurance",
            "B": "Whole life insurance",
            "C": "Permanent life insurance with flexible premiums",
            "D": "Group life insurance"
        },
        "correct_answer": "C",
        "explanation": "IUL is a type of permanent life insurance that offers flexible premiums and death benefits, with cash value growth tied to market index performance."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can policyholders access their IUL cash value while alive?",
        "options": {
            "A": "No, only beneficiaries can access it",
            "B": "Yes, through policy loans or withdrawals",
            "C": "Only after age 65",
            "D": "Only in emergencies"
        },
        "correct_answer": "B",
        "explanation": "IUL policyholders can access their cash value through policy loans or withdrawals, which is one of the living benefits of the product."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What is the primary target market for IUL products?",
        "options": {
            "A": "People only interested in term coverage",
            "B": "Individuals seeking death benefit protection AND cash accumulation",
            "C": "People who cannot qualify for any other insurance",
            "D": "Only business owners"
        },
        "correct_answer": "B",
        "explanation": "IUL is ideal for clients who want permanent death benefit protection along with tax-advantaged cash accumulation potential."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens to an IUL policy if the market index goes down?",
        "options": {
            "A": "The policy loses value",
            "B": "The policy is cancelled",
            "C": "The cash value is protected by the floor (typically 0%)",
            "D": "Premiums increase automatically"
        },
        "correct_answer": "C",
        "explanation": "The floor in an IUL policy protects the cash value from market losses. Even when the index is negative, the policy earns at least 0%."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "How should you describe the tax treatment of IUL death benefits to clients?",
        "options": {
            "A": "Taxable as ordinary income",
            "B": "Generally income tax-free to beneficiaries",
            "C": "Subject to capital gains tax",
            "D": "Taxable only if over $1 million"
        },
        "correct_answer": "B",
        "explanation": "Life insurance death benefits are generally received income tax-free by beneficiaries, which is a major advantage of IUL."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the participation rate in an IUL policy?",
        "options": {
            "A": "The percentage of premium that goes to cash value",
            "B": "The percentage of index gains credited to the policy",
            "C": "The number of policyholders in a pool",
            "D": "The percentage of agents selling the product"
        },
        "correct_answer": "B",
        "explanation": "The participation rate determines what percentage of the index's positive performance will be credited to your cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "Why is it important to review a client's existing insurance before selling IUL?",
        "options": {
            "A": "To find policies to surrender",
            "B": "To understand their current coverage and identify gaps",
            "C": "It's not important",
            "D": "To compare commission rates"
        },
        "correct_answer": "B",
        "explanation": "Reviewing existing coverage helps identify protection gaps and ensures the IUL recommendation truly fits the client's needs."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the surrender period in an IUL policy?",
        "options": {
            "A": "The time when premiums are due",
            "B": "The period when surrender charges apply if the policy is cancelled",
            "C": "The waiting period before coverage begins",
            "D": "The time to file a claim"
        },
        "correct_answer": "B",
        "explanation": "The surrender period is typically 10-15 years during which surrender charges apply if you cancel the policy and take the cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What is a common objection clients have about IUL premiums?",
        "options": {
            "A": "They're too low",
            "B": "They're higher than term insurance",
            "C": "They're paid too infrequently",
            "D": "They're tax-deductible"
        },
        "correct_answer": "B",
        "explanation": "IUL premiums are higher than term because they build cash value and provide permanent coverage. It's important to explain the additional value."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does 'cost of insurance' (COI) refer to in an IUL?",
        "options": {
            "A": "The total premium paid",
            "B": "The internal charge for the death benefit protection",
            "C": "The commission paid to agents",
            "D": "The cash value amount"
        },
        "correct_answer": "B",
        "explanation": "Cost of insurance is the internal charge deducted from the cash value to pay for the death benefit protection component."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What document shows projected cash value growth in an IUL?",
        "options": {
            "A": "The death certificate",
            "B": "The policy illustration",
            "C": "The premium notice",
            "D": "The beneficiary form"
        },
        "correct_answer": "B",
        "explanation": "The policy illustration shows projected cash value growth under different scenarios and is required to be shown to clients."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can IUL premiums be adjusted over time?",
        "options": {
            "A": "No, they are fixed for life",
            "B": "Yes, within certain limits",
            "C": "Only if the policyholder gets healthier",
            "D": "Only in the first year"
        },
        "correct_answer": "B",
        "explanation": "IUL offers flexible premiums that can be increased or decreased within policy limits, subject to keeping the policy in force."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What is the best way to explain IUL indexing to a client new to the product?",
        "options": {
            "A": "Use complex financial terminology",
            "B": "Compare it to direct stock market investing",
            "C": "Explain it earns interest linked to market performance, with downside protection",
            "D": "Don't explain it at all"
        },
        "correct_answer": "C",
        "explanation": "Simple explanations work best: IUL earns interest based on market index performance, but with a floor that protects against losses."
    },
])

# IUL - Intermediate (13 questions)
QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the difference between a point-to-point and monthly averaging crediting method?",
        "options": {
            "A": "Point-to-point measures start and end values; monthly averaging uses monthly snapshots",
            "B": "They are the same thing",
            "C": "Point-to-point is for stocks; monthly is for bonds",
            "D": "Monthly averaging always produces higher returns"
        },
        "correct_answer": "A",
        "explanation": "Point-to-point compares index values at the start and end of a period, while monthly averaging takes the average of monthly values to reduce volatility."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "How does tobacco use typically affect IUL underwriting?",
        "options": {
            "A": "No effect",
            "B": "Results in higher mortality charges and premiums",
            "C": "Policy is automatically declined",
            "D": "Only affects the cash value"
        },
        "correct_answer": "B",
        "explanation": "Tobacco users are placed in higher risk classes, resulting in higher cost of insurance charges and typically higher premiums."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'multiplier' or 'bonus' feature in some IUL policies?",
        "options": {
            "A": "A guaranteed return rate",
            "B": "An enhancement to credited interest, often in exchange for a spread",
            "C": "A sales commission bonus",
            "D": "Extra death benefit coverage"
        },
        "correct_answer": "B",
        "explanation": "Some IULs offer multipliers that increase credited interest by a factor (e.g., 1.5x), often balanced by a spread or other charges."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "Why is it important to show both guaranteed and non-guaranteed illustrations?",
        "options": {
            "A": "It's not required",
            "B": "To comply with regulations and set realistic expectations",
            "C": "To confuse clients",
            "D": "Guaranteed illustrations show better results"
        },
        "correct_answer": "B",
        "explanation": "Showing both scenarios helps clients understand best-case vs. worst-case outcomes and complies with illustration requirements."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'spread' in an IUL policy?",
        "options": {
            "A": "The difference between the premium and face amount",
            "B": "A percentage deducted from index gains before crediting",
            "C": "The agent's commission",
            "D": "The death benefit payout timing"
        },
        "correct_answer": "B",
        "explanation": "The spread is a percentage the insurance company deducts from your index gains before crediting interest to your cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How should you address a client concerned about market volatility with IUL?",
        "options": {
            "A": "Tell them the market never goes down",
            "B": "Explain the floor protection and that they don't directly invest in the market",
            "C": "Avoid discussing market performance",
            "D": "Recommend term insurance instead"
        },
        "correct_answer": "B",
        "explanation": "Emphasize that IUL provides downside protection through the floor, and the cash value is not directly invested in the stock market."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is a 'Medical Information Bureau' (MIB) check used for in IUL underwriting?",
        "options": {
            "A": "To determine commission rates",
            "B": "To verify medical history disclosed on previous insurance applications",
            "C": "To check credit scores",
            "D": "To verify employment"
        },
        "correct_answer": "B",
        "explanation": "The MIB check helps verify medical information and identify any discrepancies with previous insurance applications."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'over-funding' an IUL policy?",
        "options": {
            "A": "Paying more than required to maximize cash value growth",
            "B": "Paying premiums late",
            "C": "Exceeding the MEC limit accidentally",
            "D": "Having too much death benefit"
        },
        "correct_answer": "A",
        "explanation": "Over-funding means paying more than the minimum required premium to accelerate cash value growth, while staying within MEC limits."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is the 'premium solve' approach in IUL illustration?",
        "options": {
            "A": "Finding the minimum premium to keep the policy in force",
            "B": "Calculating commission",
            "C": "Determining the surrender value",
            "D": "Setting the death benefit"
        },
        "correct_answer": "A",
        "explanation": "Premium solve calculates the minimum premium needed to maintain the policy, though higher premiums build more cash value."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the 'segment' or 'bucket' in an IUL policy?",
        "options": {
            "A": "The death benefit portion",
            "B": "A portion of cash value allocated to a specific index crediting strategy",
            "C": "The agent's territory",
            "D": "The policyholder's age group"
        },
        "correct_answer": "B",
        "explanation": "Segments or buckets are portions of cash value allocated to different index strategies, each with its own cap, floor, and crediting method."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How do you explain the difference between IUL and variable universal life (VUL)?",
        "options": {
            "A": "They are identical products",
            "B": "IUL has downside protection; VUL cash value is directly invested and can lose value",
            "C": "VUL is always better",
            "D": "IUL is only for businesses"
        },
        "correct_answer": "B",
        "explanation": "IUL provides a floor protecting against losses, while VUL directly invests in subaccounts that can lose value in market downturns."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What does 'table rating' mean in IUL underwriting?",
        "options": {
            "A": "The policy is rated highest quality",
            "B": "The applicant is rated below standard with additional premium charges",
            "C": "The agent's rating",
            "D": "The illustration table number"
        },
        "correct_answer": "B",
        "explanation": "Table ratings (A, B, C, etc. or 1, 2, 3) indicate substandard risk with additional premium charges above standard rates."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What triggers a policy loan interest charge in an IUL?",
        "options": {
            "A": "Simply owning the policy",
            "B": "Taking a loan against the cash value",
            "C": "Missing premium payments",
            "D": "Reaching age 65"
        },
        "correct_answer": "B",
        "explanation": "When you take a policy loan, interest accrues on the borrowed amount. Many IULs offer competitive 'wash loan' or low-interest loan provisions."
    },
])

# IUL - Expert (12 questions)
QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the 'AG49' regulation's impact on IUL illustrations?",
        "options": {
            "A": "It has no impact",
            "B": "It limits the maximum illustrated rate based on the policy's options budget",
            "C": "It increases commission rates",
            "D": "It guarantees a minimum return"
        },
        "correct_answer": "B",
        "explanation": "AG49 standardizes IUL illustrations by capping the maximum illustrated rate based on the policy's hedge budget, preventing overly optimistic projections."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does the insurance company generate returns for IUL crediting?",
        "options": {
            "A": "By directly investing in the stock market",
            "B": "By purchasing options on the index while investing in fixed instruments",
            "C": "By gambling on derivatives",
            "D": "By charging excessive fees"
        },
        "correct_answer": "B",
        "explanation": "Insurers typically invest premiums in fixed instruments and use a portion to purchase index options, providing upside potential while managing risk."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is a 'conditional receipt' and its significance in IUL sales?",
        "options": {
            "A": "A receipt for cash payment only",
            "B": "Provides temporary coverage from application date if premium paid and applicant is insurable",
            "C": "A receipt for returned policies",
            "D": "A commission receipt"
        },
        "correct_answer": "B",
        "explanation": "A conditional receipt provides temporary coverage from the application date if premium is paid and the applicant meets insurability requirements."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the 'corridor' requirement in IUL policies?",
        "options": {
            "A": "The hallway in the insurance office",
            "B": "The required minimum ratio of death benefit to cash value to maintain tax-favored status",
            "C": "The sales territory",
            "D": "The time between premium payments"
        },
        "correct_answer": "B",
        "explanation": "The corridor (7702 corridor) requires a minimum death benefit relative to cash value to maintain the policy's tax-advantaged status."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "When is a 1035 exchange appropriate for moving an existing policy to IUL?",
        "options": {
            "A": "Always - it's always better to switch",
            "B": "When the new policy better serves the client's needs and the exchange is tax-neutral",
            "C": "Only for term policies",
            "D": "Never"
        },
        "correct_answer": "B",
        "explanation": "A 1035 exchange allows tax-free transfer when the new IUL better meets client needs. Suitability analysis is required to justify the exchange."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the 'lookback' feature in some IUL index crediting methods?",
        "options": {
            "A": "Reviewing past performance",
            "B": "A feature that locks in the best index value over a period rather than just the end value",
            "C": "A way to review old policies",
            "D": "A compliance requirement"
        },
        "correct_answer": "B",
        "explanation": "Lookback captures the highest index value during a period rather than just the endpoint, potentially improving crediting in volatile markets."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'jumbo' or 'high-net-worth' IUL underwriting?",
        "options": {
            "A": "Standard underwriting",
            "B": "Enhanced underwriting for large face amounts with potential better pricing",
            "C": "Simplified issue",
            "D": "Group underwriting"
        },
        "correct_answer": "B",
        "explanation": "Jumbo underwriting applies to large policies ($1M+) with more thorough underwriting but potentially better pricing due to economies of scale."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Communication",
        "question": "How do you properly discuss IUL as a retirement income strategy?",
        "options": {
            "A": "Guarantee specific income amounts",
            "B": "Explain the tax-advantaged loan strategy while noting risks and the need for proper funding",
            "C": "Avoid discussing retirement",
            "D": "Compare it directly to a 401(k)"
        },
        "correct_answer": "B",
        "explanation": "IUL can supplement retirement through tax-free policy loans, but proper funding and disclosure of risks (like lapse) are essential."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the 'options budget' in IUL product design?",
        "options": {
            "A": "The sales budget",
            "B": "The amount allocated to purchase index options that determine crediting potential",
            "C": "The premium amount",
            "D": "The marketing budget"
        },
        "correct_answer": "B",
        "explanation": "The options budget is the portion of premium used to buy index options. A higher options budget can support higher caps or participation rates."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is 'premium financing' in the context of IUL?",
        "options": {
            "A": "Paying premiums monthly",
            "B": "Using a third-party loan to fund IUL premiums, typically for large policies",
            "C": "Automatic premium payments",
            "D": "Discounted premiums"
        },
        "correct_answer": "B",
        "explanation": "Premium financing uses borrowed funds to pay large IUL premiums, often for estate planning. It's complex and suitable only for high-net-worth clients."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'volatility control' index in IUL?",
        "options": {
            "A": "A standard market index",
            "B": "An index that adjusts exposure to maintain target volatility levels",
            "C": "A fixed interest account",
            "D": "The S&P 500"
        },
        "correct_answer": "B",
        "explanation": "Volatility control indices dynamically adjust market exposure to maintain consistent volatility, potentially offering higher caps than traditional indices."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'retention' in life insurance underwriting?",
        "options": {
            "A": "Keeping agents",
            "B": "The maximum risk amount a carrier keeps before reinsuring",
            "C": "Policy persistence",
            "D": "Client retention"
        },
        "correct_answer": "B",
        "explanation": "Retention is the maximum death benefit amount an insurer retains before ceding risk to reinsurers. High face amounts often require reinsurance."
    },
])

# ==================== FIA QUESTIONS (37 total) ====================

# FIA - Easy (13 questions)
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does FIA stand for?",
        "options": {
            "A": "Fixed Interest Account",
            "B": "Fixed Indexed Annuity",
            "C": "Financial Investment Allocation",
            "D": "Federal Insurance Act"
        },
        "correct_answer": "B",
        "explanation": "FIA stands for Fixed Indexed Annuity, a tax-deferred annuity that provides principal protection with interest linked to market index performance."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the primary purpose of a Fixed Indexed Annuity?",
        "options": {
            "A": "Short-term savings",
            "B": "Safe accumulation for retirement with growth potential",
            "C": "High-risk investing",
            "D": "Checking account replacement"
        },
        "correct_answer": "B",
        "explanation": "FIAs are designed for safe, tax-deferred retirement accumulation with growth potential tied to market indices while protecting principal."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Is the principal in an FIA at risk from market losses?",
        "options": {
            "A": "Yes, it can lose value",
            "B": "No, the principal is protected from market losses",
            "C": "Only in bear markets",
            "D": "Only if you withdraw early"
        },
        "correct_answer": "B",
        "explanation": "FIAs provide principal protection - the contract value cannot decrease due to market downturns (though surrender charges may apply)."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "Who is the ideal client for an FIA?",
        "options": {
            "A": "Young aggressive investors",
            "B": "People needing immediate income",
            "C": "Conservative savers approaching or in retirement",
            "D": "Day traders"
        },
        "correct_answer": "C",
        "explanation": "FIAs are ideal for conservative clients near or in retirement who want principal protection with growth potential and tax deferral."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the 'surrender period' in an FIA?",
        "options": {
            "A": "When you can add more money",
            "B": "The time period when penalties apply for early withdrawal",
            "C": "When income begins",
            "D": "The policy term"
        },
        "correct_answer": "B",
        "explanation": "The surrender period is typically 5-10 years during which withdrawal penalties (surrender charges) apply for early access beyond free withdrawal amounts."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What is the 'free withdrawal' provision in most FIAs?",
        "options": {
            "A": "There are no withdrawals allowed",
            "B": "Allows withdrawal of a percentage annually without surrender charges",
            "C": "Free money from the insurance company",
            "D": "Withdrawals only at death"
        },
        "correct_answer": "B",
        "explanation": "Most FIAs allow 10% annual withdrawals without surrender charges, providing liquidity while keeping most funds for long-term growth."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How are earnings in an FIA taxed?",
        "options": {
            "A": "Taxed annually",
            "B": "Tax-free forever",
            "C": "Tax-deferred until withdrawal",
            "D": "Capital gains tax only"
        },
        "correct_answer": "C",
        "explanation": "FIA earnings grow tax-deferred and are taxed as ordinary income only when withdrawn, similar to traditional retirement accounts."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What is a common misconception about FIAs you should address?",
        "options": {
            "A": "That they're safe",
            "B": "That they're insurance products",
            "C": "That they directly invest in the stock market",
            "D": "That they're tax-deferred"
        },
        "correct_answer": "C",
        "explanation": "Many clients think FIAs invest directly in stocks. It's important to explain that interest is linked to an index, not direct market participation."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the 'accumulation value' in an FIA?",
        "options": {
            "A": "The death benefit",
            "B": "The total value including premium and credited interest",
            "C": "The premium only",
            "D": "The surrender charge"
        },
        "correct_answer": "B",
        "explanation": "The accumulation value is the total contract value including your premium, any interest credited, minus any withdrawals or fees."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What question should you ask to determine if an FIA is suitable?",
        "options": {
            "A": "Do you like gambling?",
            "B": "What is your time horizon and risk tolerance?",
            "C": "How much commission do you want me to earn?",
            "D": "Do you have a checking account?"
        },
        "correct_answer": "B",
        "explanation": "Understanding the client's time horizon (should match surrender period) and risk tolerance is essential for FIA suitability."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can you add additional premium to an FIA after purchase?",
        "options": {
            "A": "Never",
            "B": "Depends on whether it's a single-premium or flexible-premium product",
            "C": "Only in the first year",
            "D": "Only at age 65"
        },
        "correct_answer": "B",
        "explanation": "Single-premium FIAs accept one lump sum; flexible-premium FIAs allow additional contributions, typically within certain time limits."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What's the benefit of tax deferral in an FIA?",
        "options": {
            "A": "No benefit",
            "B": "Your money grows without annual taxation, potentially accumulating faster",
            "C": "You never pay taxes",
            "D": "Lower commission"
        },
        "correct_answer": "B",
        "explanation": "Tax deferral allows your full balance to compound without annual tax drag, potentially resulting in greater accumulation over time."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens to an FIA when the owner dies?",
        "options": {
            "A": "The money disappears",
            "B": "The beneficiary receives the proceeds, typically at least the accumulation value",
            "C": "It goes to the government",
            "D": "It's forfeited to the insurance company"
        },
        "correct_answer": "B",
        "explanation": "Upon the owner's death, the designated beneficiary receives the death benefit, typically at least the accumulation value."
    },
])

# FIA - Intermediate (12 questions)
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is an 'income rider' on an FIA?",
        "options": {
            "A": "A person who rides to collect income",
            "B": "An optional benefit that provides guaranteed lifetime income",
            "C": "The base policy",
            "D": "A surrender charge waiver"
        },
        "correct_answer": "B",
        "explanation": "An income rider is an optional benefit (with an additional fee) that guarantees lifetime income payments regardless of account value."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the difference between 'account value' and 'income base' in an FIA with an income rider?",
        "options": {
            "A": "They are the same",
            "B": "Account value is the actual cash; income base is a calculation for determining income payments",
            "C": "Account value is always higher",
            "D": "Income base is the surrender value"
        },
        "correct_answer": "B",
        "explanation": "Account value is your actual money; the income base is a separate calculation (often with bonuses) used solely to determine income rider payments."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is 'suitability' in annuity sales?",
        "options": {
            "A": "Whether the agent is suitable",
            "B": "Ensuring the product fits the client's financial situation, needs, and objectives",
            "C": "Whether the premium is large enough",
            "D": "The application process"
        },
        "correct_answer": "B",
        "explanation": "Suitability requires ensuring the FIA matches the client's financial circumstances, investment objectives, time horizon, and risk tolerance."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the '10% IRS penalty' for FIA withdrawals?",
        "options": {
            "A": "A fee charged by the insurance company",
            "B": "A tax penalty for withdrawals before age 59½",
            "C": "A bonus for early withdrawal",
            "D": "The surrender charge"
        },
        "correct_answer": "B",
        "explanation": "Withdrawals from an FIA before age 59½ may be subject to a 10% IRS early withdrawal penalty, in addition to ordinary income tax."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How do you explain the 'cap rate' to a client?",
        "options": {
            "A": "It's the maximum you'll pay",
            "B": "It's the ceiling on how much index-linked interest you can earn in a period",
            "C": "It's the minimum guarantee",
            "D": "It's the premium limit"
        },
        "correct_answer": "B",
        "explanation": "The cap rate is the maximum interest that can be credited - even if the index gains 20%, a 6% cap means you'd earn 6%."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'annuitization' of an FIA?",
        "options": {
            "A": "Buying the annuity",
            "B": "Converting the account value to a guaranteed income stream",
            "C": "Canceling the policy",
            "D": "Transferring to another annuity"
        },
        "correct_answer": "B",
        "explanation": "Annuitization converts the FIA's account value into a series of guaranteed payments, typically irrevocably, based on selected payout options."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "Do FIAs require medical underwriting?",
        "options": {
            "A": "Yes, extensive medical exams",
            "B": "Generally no, just financial suitability and age verification",
            "C": "Only for people over 70",
            "D": "Only for large premiums"
        },
        "correct_answer": "B",
        "explanation": "FIAs typically don't require medical underwriting - they're issued based on financial suitability, age limits, and premium guidelines."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'bonus' in an FIA?",
        "options": {
            "A": "Agent commission",
            "B": "An immediate credit added to your premium, often with recapture provisions",
            "C": "Interest earned",
            "D": "A sales incentive"
        },
        "correct_answer": "B",
        "explanation": "Many FIAs offer an upfront bonus (e.g., 10% of premium), though these often come with longer surrender periods or recapture provisions."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is the 'free look' period for FIAs?",
        "options": {
            "A": "Time to review before buying",
            "B": "A period after purchase (typically 10-30 days) to cancel with full refund",
            "C": "When you can view your account",
            "D": "The illustration review time"
        },
        "correct_answer": "B",
        "explanation": "The free look period allows new FIA owners to review the contract and cancel with a full refund if they're not satisfied."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'RMD' and how does it affect FIA owners?",
        "options": {
            "A": "Regular Monthly Deposit",
            "B": "Required Minimum Distribution - mandatory withdrawals from qualified accounts after age 73",
            "C": "Retirement Money Distribution",
            "D": "Rate Minimum Determination"
        },
        "correct_answer": "B",
        "explanation": "RMDs require IRA owners to take minimum distributions starting at age 73. Qualified FIA owners must comply, though most contracts allow RMDs without surrender charges."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How should you compare FIA returns to stock market returns?",
        "options": {
            "A": "Promise FIAs will match the market",
            "B": "Explain FIAs trade some upside potential for principal protection",
            "C": "Say FIAs always beat the market",
            "D": "Don't compare them"
        },
        "correct_answer": "B",
        "explanation": "FIAs provide a balance - you give up some upside potential in exchange for downside protection. It's a different value proposition than direct market investing."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'interest rate risk' in an FIA?",
        "options": {
            "A": "Risk of earning too much",
            "B": "Risk that caps or rates may be lowered when renewed at the carrier's discretion",
            "C": "Risk of the index going down",
            "D": "Risk of default"
        },
        "correct_answer": "B",
        "explanation": "While principal is protected, caps and participation rates can be adjusted by the carrier, potentially affecting future interest crediting."
    },
])

# FIA - Expert (12 questions)
QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is an 'MYGA' and how does it differ from an FIA?",
        "options": {
            "A": "They're the same product",
            "B": "MYGA is a Multi-Year Guaranteed Annuity with fixed rates, FIA links to indices",
            "C": "MYGA is for young people only",
            "D": "FIA is always better"
        },
        "correct_answer": "B",
        "explanation": "MYGAs offer guaranteed fixed rates for multiple years, while FIAs link interest to index performance. MYGAs are simpler; FIAs offer more growth potential."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'GLWB' rider?",
        "options": {
            "A": "Guaranteed Lifetime Withdrawal Benefit - provides income for life without annuitization",
            "B": "General Liability Waiver Benefit",
            "C": "Growth Linked Wealth Builder",
            "D": "Guaranteed Low Withdrawal Base"
        },
        "correct_answer": "A",
        "explanation": "A GLWB rider provides guaranteed lifetime income withdrawals while maintaining control of your account value, unlike traditional annuitization."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is a '1035 exchange' for annuities?",
        "options": {
            "A": "A tax-free exchange of one annuity for another",
            "B": "A surrender charge",
            "C": "An IRS form for taxes",
            "D": "A bonus provision"
        },
        "correct_answer": "A",
        "explanation": "A 1035 exchange allows tax-free transfer of funds from one annuity to another without triggering immediate taxation on gains."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'bonus recapture' in an FIA?",
        "options": {
            "A": "Getting extra bonuses",
            "B": "A provision allowing the insurer to recover bonuses if you surrender early",
            "C": "Reclaiming lost interest",
            "D": "Agent bonus clawback"
        },
        "correct_answer": "B",
        "explanation": "Bonus recapture allows insurers to recover a portion of upfront bonuses if the contract is surrendered within a specified period."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'MVA' (Market Value Adjustment) in an FIA?",
        "options": {
            "A": "Minimum Value Allowance",
            "B": "An adjustment that can increase or decrease surrender value based on interest rate changes",
            "C": "Maximum Value Achievement",
            "D": "The account value"
        },
        "correct_answer": "B",
        "explanation": "MVA adjusts surrender value based on changes in interest rates since purchase - if rates rise, MVA may reduce value; if rates fall, it may increase."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Communication",
        "question": "How do you explain the difference between 'income account value' and 'walk-away value'?",
        "options": {
            "A": "They're the same",
            "B": "Income account is for income calculation; walk-away value is what you'd receive if surrendering",
            "C": "Walk-away value is always higher",
            "D": "Income account is always higher"
        },
        "correct_answer": "B",
        "explanation": "The income account (often with bonuses) determines income payments; the walk-away value is the actual cash value available if surrendering the contract."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the purpose of the 'nursing home waiver' in FIAs?",
        "options": {
            "A": "Waives premiums",
            "B": "Allows penalty-free withdrawals for nursing home confinement",
            "C": "Provides nursing home coverage",
            "D": "Waives the application"
        },
        "correct_answer": "B",
        "explanation": "The nursing home waiver allows access to funds without surrender charges if the owner is confined to a nursing home for a specified period."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What documentation is required for FIA 'best interest' compliance?",
        "options": {
            "A": "Just a signature",
            "B": "Suitability forms, product comparisons, disclosure of compensation, and rationale for recommendation",
            "C": "Medical records",
            "D": "Only the application"
        },
        "correct_answer": "B",
        "explanation": "Best interest rules require documentation showing the recommendation serves the client's best interest, including suitability analysis and disclosure."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'performance lock' or 'step-up' feature in some FIAs?",
        "options": {
            "A": "Locks your premium",
            "B": "Allows locking in index gains early or stepping up the income base",
            "C": "Prevents changes to the contract",
            "D": "Locks in surrender charges"
        },
        "correct_answer": "B",
        "explanation": "Performance lock features allow policyholders to lock in positive index performance before the end of a crediting period or step up guaranteed income bases."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'age banding' in FIA pricing?",
        "options": {
            "A": "Music played at sales events",
            "B": "Different rates or features based on the age of the applicant at issue",
            "C": "The agent's age requirement",
            "D": "Surrender period lengths"
        },
        "correct_answer": "B",
        "explanation": "Age banding refers to different payout rates, caps, or features based on the owner's age - older ages often receive higher income rates but may have different caps."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'non-qualified stretch' vs. 'qualified stretch' for inherited annuities?",
        "options": {
            "A": "Exercise terms",
            "B": "Rules for how beneficiaries must withdraw inherited annuity funds",
            "C": "Surrender charge provisions",
            "D": "They're identical"
        },
        "correct_answer": "B",
        "explanation": "Stretch provisions determine how non-spouse beneficiaries withdraw inherited annuities - rules differ for qualified (IRA) vs. non-qualified annuities, especially post-SECURE Act."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Communication",
        "question": "How do you explain 'spread' vs. 'cap' vs. 'participation rate' to a sophisticated client?",
        "options": {
            "A": "They all mean the same thing",
            "B": "Cap limits gains; spread is deducted from gains; participation rate is % of gain credited",
            "C": "Only cap matters",
            "D": "Spread is always better"
        },
        "correct_answer": "B",
        "explanation": "Each affects crediting differently: caps limit maximum gains, spreads are subtracted from gains, and participation rates determine what percentage of gains are credited."
    },
])

# ==================== TERM QUESTIONS (38 total) ====================

# Term - Easy (13 questions)
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is term life insurance?",
        "options": {
            "A": "Insurance that lasts forever",
            "B": "Temporary coverage for a specific period (term)",
            "C": "Investment insurance",
            "D": "Health insurance"
        },
        "correct_answer": "B",
        "explanation": "Term life insurance provides coverage for a specific period (10, 20, 30 years) with a death benefit paid if the insured dies during the term."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Does term insurance build cash value?",
        "options": {
            "A": "Yes, significant cash value",
            "B": "No, it provides only death benefit protection",
            "C": "Only after 10 years",
            "D": "Only in certain states"
        },
        "correct_answer": "B",
        "explanation": "Term insurance is pure protection - it does not build cash value, which is why premiums are lower than permanent insurance."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "Who is the ideal client for term life insurance?",
        "options": {
            "A": "Someone who wants lifelong coverage",
            "B": "Someone with temporary needs like mortgage protection or income replacement",
            "C": "Someone looking for investment growth",
            "D": "Retired individuals only"
        },
        "correct_answer": "B",
        "explanation": "Term is ideal for temporary needs - covering a mortgage, protecting income during working years, or covering children until they're independent."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What happens when a term policy expires?",
        "options": {
            "A": "You get a refund",
            "B": "Coverage ends unless renewed or converted",
            "C": "It converts to whole life automatically",
            "D": "The death benefit is paid"
        },
        "correct_answer": "B",
        "explanation": "When the term ends, coverage expires. Some policies offer renewal (at higher rates) or conversion to permanent insurance without new underwriting."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a 'level term' policy?",
        "options": {
            "A": "A policy with increasing premiums",
            "B": "A policy with level (fixed) premiums for the entire term",
            "C": "A policy with decreasing death benefit",
            "D": "A graded benefit policy"
        },
        "correct_answer": "B",
        "explanation": "Level term means both the death benefit and premium remain constant throughout the term - the most common and straightforward type of term insurance."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What's the main advantage of term insurance compared to permanent?",
        "options": {
            "A": "Cash value",
            "B": "Lower premiums for the same death benefit",
            "C": "Investment options",
            "D": "Lifetime coverage"
        },
        "correct_answer": "B",
        "explanation": "Term's main advantage is affordability - you get more death benefit protection per dollar compared to permanent insurance."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "How much life insurance coverage should clients typically have?",
        "options": {
            "A": "As little as possible",
            "B": "Often recommended as 10-12x annual income for income replacement",
            "C": "Exactly $100,000",
            "D": "Only enough to cover funeral costs"
        },
        "correct_answer": "B",
        "explanation": "A common rule of thumb is 10-12x annual income, though a proper needs analysis considers specific debts, income replacement needs, and goals."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is a 'conversion privilege' in term insurance?",
        "options": {
            "A": "Converting to a different religion",
            "B": "The right to convert to permanent insurance without medical underwriting",
            "C": "Changing beneficiaries",
            "D": "Converting payments to annual"
        },
        "correct_answer": "B",
        "explanation": "The conversion privilege allows term policyholders to convert to permanent insurance without new medical exams, valuable if health declines."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Underwriting",
        "question": "What factors affect term insurance premiums?",
        "options": {
            "A": "Only age",
            "B": "Age, health, gender, tobacco use, and term length",
            "C": "Only the face amount",
            "D": "Only smoking status"
        },
        "correct_answer": "B",
        "explanation": "Term premiums are based on multiple factors including age, health condition, gender, tobacco use, face amount, and the length of the term."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "How should you explain the difference between term and whole life to a client?",
        "options": {
            "A": "Don't explain it",
            "B": "Term is renting coverage; whole life is owning it with equity (cash value)",
            "C": "They're exactly the same",
            "D": "Whole life is always better"
        },
        "correct_answer": "B",
        "explanation": "The rent vs. own analogy helps clients understand - term provides temporary protection (renting), while permanent builds equity (cash value) you keep."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the 'face amount' of a term policy?",
        "options": {
            "A": "The monthly premium",
            "B": "The death benefit amount paid to beneficiaries",
            "C": "The cash value",
            "D": "The application fee"
        },
        "correct_answer": "B",
        "explanation": "The face amount is the death benefit - the amount paid to beneficiaries if the insured dies during the policy term."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What is the 'incontestability period' in a term policy?",
        "options": {
            "A": "A cooling-off period",
            "B": "Typically 2 years during which the insurer can void the policy for misrepresentation",
            "C": "When the policy cannot be purchased",
            "D": "The waiting period before coverage starts"
        },
        "correct_answer": "B",
        "explanation": "The incontestability period (usually 2 years) is when the insurer can investigate and potentially void a policy for material misrepresentation on the application."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can you have multiple term life insurance policies?",
        "options": {
            "A": "No, only one is allowed",
            "B": "Yes, you can own multiple policies from different or same carriers",
            "C": "Only if you're wealthy",
            "D": "Only if you're married"
        },
        "correct_answer": "B",
        "explanation": "You can own multiple term policies - a strategy called 'laddering' uses different terms to match changing coverage needs over time."
    },
])

# Term - Intermediate (13 questions)
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'term laddering'?",
        "options": {
            "A": "Climbing a ladder",
            "B": "Buying multiple term policies with staggered end dates to match changing needs",
            "C": "A sales technique",
            "D": "Increasing premiums"
        },
        "correct_answer": "B",
        "explanation": "Laddering involves purchasing multiple term policies with different terms, optimizing coverage to decline as needs decrease (e.g., mortgage paid off, kids independent)."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is 'preferred plus' or 'super preferred' classification?",
        "options": {
            "A": "The most expensive class",
            "B": "The best health classification with lowest premiums",
            "C": "Average health",
            "D": "For smokers only"
        },
        "correct_answer": "B",
        "explanation": "Preferred plus/super preferred is the best underwriting class for applicants in excellent health, offering the lowest premium rates."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'return of premium' (ROP) term policy?",
        "options": {
            "A": "Regular term insurance",
            "B": "Term that returns premiums paid if you outlive the term",
            "C": "Term with cash value",
            "D": "Refundable term"
        },
        "correct_answer": "B",
        "explanation": "ROP term returns your paid premiums if you outlive the term, but premiums are significantly higher than regular term (typically 2-3x more)."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "When might you recommend converting term to permanent insurance?",
        "options": {
            "A": "Never",
            "B": "When the client's health has declined or permanent needs have been identified",
            "C": "Always immediately",
            "D": "Only at age 65"
        },
        "correct_answer": "B",
        "explanation": "Conversion is valuable when health declines (locks in coverage without underwriting) or when the client recognizes permanent needs like estate planning."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is 'simplified issue' term insurance?",
        "options": {
            "A": "Complex underwriting",
            "B": "Term with limited underwriting questions and no medical exam",
            "C": "Term for businesses only",
            "D": "The longest term available"
        },
        "correct_answer": "B",
        "explanation": "Simplified issue uses health questions instead of a medical exam, offering faster approval but typically higher premiums and lower face amounts."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'annual renewable term' (ART)?",
        "options": {
            "A": "Art insurance",
            "B": "Term that renews annually with increasing premiums each year",
            "C": "Term that never renews",
            "D": "Decreasing term"
        },
        "correct_answer": "B",
        "explanation": "ART provides one-year terms that renew annually with premiums increasing each year based on the insured's attained age."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How do you address a client's concern about 'wasting money' on term if they don't die?",
        "options": {
            "A": "Agree it's a waste",
            "B": "Explain it's protecting their family's financial future - like car insurance that provides peace of mind",
            "C": "Recommend no insurance",
            "D": "Don't address it"
        },
        "correct_answer": "B",
        "explanation": "Frame insurance as protection, not investment. Just like car insurance isn't 'wasted' if you don't crash, term protects your family during vulnerable years."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is a 'paramedical exam' in term underwriting?",
        "options": {
            "A": "A hospital visit",
            "B": "A basic medical exam by a licensed examiner, including blood/urine samples",
            "C": "A psychological test",
            "D": "An X-ray"
        },
        "correct_answer": "B",
        "explanation": "A paramedical exam includes height, weight, blood pressure, and blood/urine samples conducted by a licensed examiner, typically at the applicant's location."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'waiver of premium' rider on term insurance?",
        "options": {
            "A": "Free insurance",
            "B": "Waives premiums if the insured becomes disabled",
            "C": "A premium discount",
            "D": "Waives the application fee"
        },
        "correct_answer": "B",
        "explanation": "The waiver of premium rider keeps the policy in force without premium payments if the insured becomes disabled as defined in the policy."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is 'needs analysis' in term insurance sales?",
        "options": {
            "A": "Analyzing agent needs",
            "B": "A systematic approach to determine the appropriate coverage amount based on client circumstances",
            "C": "Checking credit scores",
            "D": "Medical underwriting"
        },
        "correct_answer": "B",
        "explanation": "Needs analysis calculates proper coverage considering income replacement, debts, education funding, final expenses, and existing resources."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is 'attending physician statement' (APS) in underwriting?",
        "options": {
            "A": "A prescription",
            "B": "Medical records from the applicant's doctor requested during underwriting",
            "C": "The application",
            "D": "The policy"
        },
        "correct_answer": "B",
        "explanation": "An APS is a report from the applicant's physician containing medical history, requested when health questions on the application require more detail."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What does 'guaranteed renewable' mean for term insurance?",
        "options": {
            "A": "Premiums are guaranteed not to increase",
            "B": "The policy can be renewed regardless of health changes, though premiums may increase",
            "C": "The death benefit is guaranteed",
            "D": "It cannot be cancelled"
        },
        "correct_answer": "B",
        "explanation": "Guaranteed renewable means you can renew the policy without proving insurability, though premiums will increase based on your attained age."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How much does tobacco use typically increase term premiums?",
        "options": {
            "A": "About 10%",
            "B": "Often 2-3 times higher than non-tobacco rates",
            "C": "No difference",
            "D": "About 5%"
        },
        "correct_answer": "B",
        "explanation": "Tobacco users typically pay 2-3x more for term coverage due to significantly higher mortality risk associated with smoking."
    },
])

# Term - Expert (12 questions)
QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'accelerated underwriting' in term insurance?",
        "options": {
            "A": "Faster claim payment",
            "B": "Using algorithms and data sources to make quick decisions without medical exams for qualified applicants",
            "C": "Standard underwriting done faster",
            "D": "Group underwriting"
        },
        "correct_answer": "B",
        "explanation": "Accelerated underwriting uses data analytics, electronic health records, and algorithms to approve qualified applicants quickly without traditional medical exams."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is a 'term conversion credit'?",
        "options": {
            "A": "A discount on the term premium",
            "B": "Credits applied to reduce the first-year premium when converting to permanent insurance",
            "C": "A tax credit",
            "D": "Commission credit"
        },
        "correct_answer": "B",
        "explanation": "Some carriers offer conversion credits that reduce the first-year permanent policy premium as an incentive to convert term coverage."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'flat extra' in term underwriting?",
        "options": {
            "A": "A bonus",
            "B": "An additional dollar amount per thousand of coverage for specific risks (e.g., hazardous occupation)",
            "C": "A discount",
            "D": "The base premium"
        },
        "correct_answer": "B",
        "explanation": "Flat extras are additional premium charges (e.g., $5 per $1,000) for specific temporary or unusual risks like hazardous activities or occupations."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'contestability' in the context of term insurance claims?",
        "options": {
            "A": "The insured can contest premiums",
            "B": "The insurer's right to investigate and potentially deny claims for misrepresentation during the contestable period",
            "C": "A competition between insurers",
            "D": "The beneficiary's right to contest"
        },
        "correct_answer": "B",
        "explanation": "During the contestability period (usually 2 years), insurers can investigate claims and potentially deny them if material misrepresentation is discovered."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "When is 'split dollar' arrangement used with term insurance?",
        "options": {
            "A": "Never",
            "B": "When an employer and employee share premium costs and benefits, often as an executive benefit",
            "C": "Only for individual policies",
            "D": "Only for very small policies"
        },
        "correct_answer": "B",
        "explanation": "Split dollar arrangements share premium costs and benefits between employer and employee, sometimes used with term insurance as an executive benefit."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'reinsurance' in the context of term insurance?",
        "options": {
            "A": "Buying more insurance",
            "B": "When the primary insurer transfers some risk to another insurer for large face amounts",
            "C": "Policy replacement",
            "D": "Group insurance"
        },
        "correct_answer": "B",
        "explanation": "For large policies, the primary carrier cedes some risk to reinsurers to spread liability. This affects underwriting requirements for high face amounts."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is the 'suicide exclusion' in term policies?",
        "options": {
            "A": "There is no exclusion",
            "B": "Death benefit is limited or excluded if death by suicide occurs within typically 2 years",
            "C": "Only applies to whole life",
            "D": "A state-specific rule only"
        },
        "correct_answer": "B",
        "explanation": "Most term policies exclude suicide within the first 2 years, typically returning premiums paid rather than paying the death benefit."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Communication",
        "question": "How do you explain 'insurability guarantee' riders to clients?",
        "options": {
            "A": "It guarantees a claim payment",
            "B": "It allows purchasing additional coverage at specified dates without new underwriting",
            "C": "It guarantees the premium",
            "D": "It's not important"
        },
        "correct_answer": "B",
        "explanation": "Insurability guarantee riders allow purchasing additional coverage at specific future dates (marriage, child birth) without new medical underwriting."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'knockout' underwriting?",
        "options": {
            "A": "Boxing-related insurance",
            "B": "Automatic decline for specific conditions or answers on the application",
            "C": "Manual underwriting",
            "D": "Premium calculation"
        },
        "correct_answer": "B",
        "explanation": "Knockout questions or conditions are automatic declines - certain health conditions or activities immediately disqualify applicants from coverage."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'children's term rider' on an adult term policy?",
        "options": {
            "A": "A separate policy for children",
            "B": "A rider providing small amounts of coverage on insured's children, often convertible to permanent",
            "C": "Coverage for grandchildren only",
            "D": "A discount for having children"
        },
        "correct_answer": "B",
        "explanation": "Children's term riders provide coverage on all children in the family, typically convertible to permanent insurance without underwriting at a specified age."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is 'key person' term insurance?",
        "options": {
            "A": "Insurance for locksmiths",
            "B": "Business-owned coverage on essential employees to protect the company from financial loss",
            "C": "Insurance for the owner only",
            "D": "Group term insurance"
        },
        "correct_answer": "B",
        "explanation": "Key person insurance protects businesses from financial loss if a key employee dies, covering costs of finding/training replacements and lost revenue."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'informal inquiry' or 'trial application' in term underwriting?",
        "options": {
            "A": "The formal application",
            "B": "A preliminary assessment to estimate coverage likelihood before formal application",
            "C": "The policy document",
            "D": "The premium quote"
        },
        "correct_answer": "B",
        "explanation": "An informal inquiry allows agents to submit basic health information to get preliminary underwriting feedback before the client formally applies."
    },
])

# ==================== FINAL EXPENSE QUESTIONS (37 total) ====================

# Final Expense - Easy (13 questions)
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is final expense insurance primarily designed to cover?",
        "options": {
            "A": "Retirement income",
            "B": "End-of-life costs like funeral, burial, and outstanding bills",
            "C": "Investment growth",
            "D": "Health care premiums"
        },
        "correct_answer": "B",
        "explanation": "Final expense insurance (burial insurance) is designed to cover funeral costs, burial expenses, medical bills, and other end-of-life expenses."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What is the typical face amount range for final expense policies?",
        "options": {
            "A": "$500,000 - $1,000,000",
            "B": "$2,000 - $35,000",
            "C": "$100,000 - $250,000",
            "D": "Unlimited"
        },
        "correct_answer": "B",
        "explanation": "Final expense policies typically range from $2,000 to $35,000, designed to cover immediate end-of-life costs rather than income replacement."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "Who is the primary target market for final expense insurance?",
        "options": {
            "A": "Young professionals",
            "B": "Seniors aged 50-85 concerned about being a burden to family",
            "C": "Wealthy individuals",
            "D": "Business owners only"
        },
        "correct_answer": "B",
        "explanation": "Final expense targets seniors (typically 50-85) who want to ensure their final expenses don't burden their families financially."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What type of underwriting is typically used for final expense?",
        "options": {
            "A": "Full medical underwriting with exams",
            "B": "Simplified issue with health questions only",
            "C": "No underwriting at all",
            "D": "Financial underwriting only"
        },
        "correct_answer": "B",
        "explanation": "Final expense uses simplified issue underwriting with health questions but no medical exam, making it accessible to seniors."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "How do you open a conversation about final expense insurance sensitively?",
        "options": {
            "A": "Ask if they're planning to die soon",
            "B": "Ask about their plans to protect their family from final expenses",
            "C": "Don't discuss it at all",
            "D": "Focus only on price"
        },
        "correct_answer": "B",
        "explanation": "Approach sensitively by focusing on protecting loved ones and ensuring their wishes are carried out without financial burden on family."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Is final expense insurance whole life or term?",
        "options": {
            "A": "Always term",
            "B": "Usually whole life with lifetime coverage",
            "C": "Universal life only",
            "D": "Variable life only"
        },
        "correct_answer": "B",
        "explanation": "Final expense is typically whole life insurance, providing permanent coverage with fixed premiums that don't increase with age."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What's a common reason seniors buy final expense insurance?",
        "options": {
            "A": "To get rich",
            "B": "To ensure their funeral and bills are paid without burdening family",
            "C": "For investment growth",
            "D": "Because it's required by law"
        },
        "correct_answer": "B",
        "explanation": "Most seniors buy final expense to ensure their funeral costs and final bills are covered, protecting their family from financial burden."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "How long does final expense coverage last?",
        "options": {
            "A": "10 years",
            "B": "For the insured's entire lifetime",
            "C": "20 years",
            "D": "Until age 80"
        },
        "correct_answer": "B",
        "explanation": "As whole life insurance, final expense provides coverage for the insured's entire lifetime as long as premiums are paid."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "What's the average cost of a funeral in the United States?",
        "options": {
            "A": "$500-$1,000",
            "B": "$7,000-$12,000 or more",
            "C": "$50-$100",
            "D": "Funerals are free"
        },
        "correct_answer": "B",
        "explanation": "Average funeral costs range from $7,000-$12,000+, making final expense insurance important for those without savings to cover these costs."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can final expense beneficiaries use the money for anything?",
        "options": {
            "A": "No, only for funeral expenses",
            "B": "Yes, beneficiaries can use the death benefit for any purpose",
            "C": "Only for medical bills",
            "D": "Only for burial plots"
        },
        "correct_answer": "B",
        "explanation": "While designed for final expenses, beneficiaries receive a lump sum they can use for funeral costs, bills, or any other need."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What's an effective way to present final expense to a senior prospect?",
        "options": {
            "A": "High-pressure tactics",
            "B": "Kitchen table presentation focusing on protecting family and peace of mind",
            "C": "Mail them a policy",
            "D": "Only discuss online"
        },
        "correct_answer": "B",
        "explanation": "Final expense is best presented in a warm, face-to-face setting focusing on the emotional benefit of protecting family and providing peace of mind."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Do final expense premiums increase with age?",
        "options": {
            "A": "Yes, they increase every year",
            "B": "No, they are locked in at the issue age",
            "C": "Only after age 70",
            "D": "They decrease over time"
        },
        "correct_answer": "B",
        "explanation": "Final expense premiums are fixed based on issue age and don't increase, providing predictable payments for seniors on fixed incomes."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Client Communication",
        "question": "How do you address a senior's concern about affordability?",
        "options": {
            "A": "Tell them to find the money somehow",
            "B": "Show how the monthly premium compares to daily expenses like coffee",
            "C": "Ignore the concern",
            "D": "Recommend they skip the insurance"
        },
        "correct_answer": "B",
        "explanation": "Relate premiums to everyday expenses - 'the cost of a daily coffee' - to help seniors understand the affordability and value."
    },
])

# Final Expense - Intermediate (12 questions)
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'graded benefit' final expense?",
        "options": {
            "A": "Immediate full coverage",
            "B": "Reduced or return-of-premium benefit for initial years, then full coverage",
            "C": "Declining coverage",
            "D": "Coverage only for accidents"
        },
        "correct_answer": "B",
        "explanation": "Graded benefit policies have a waiting period (usually 2-3 years) where death benefit is limited, designed for higher-risk applicants."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What health conditions commonly lead to graded benefit placement?",
        "options": {
            "A": "Perfect health",
            "B": "Conditions like diabetes with insulin, COPD with oxygen, recent heart issues",
            "C": "Being a non-smoker",
            "D": "Being under age 50"
        },
        "correct_answer": "B",
        "explanation": "Serious health conditions like insulin-dependent diabetes, oxygen use, or recent cardiac events typically result in graded benefit classification."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is a 'lead' in final expense sales?",
        "options": {
            "A": "The metal lead",
            "B": "A prospect who has expressed interest through a response card, call, or other means",
            "C": "The agent's boss",
            "D": "A policy document"
        },
        "correct_answer": "B",
        "explanation": "Leads are prospects who've shown interest through response cards, TV/radio ads, or digital inquiries, indicating potential for a sale."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'modified' or 'graded' whole life in final expense?",
        "options": {
            "A": "Standard immediate coverage",
            "B": "A policy with limited benefits in early years, typically for less healthy applicants",
            "C": "Term insurance",
            "D": "Universal life"
        },
        "correct_answer": "B",
        "explanation": "Modified/graded policies limit benefits during initial years (return of premium + interest if death occurs) for applicants with health issues."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How do you explain the value of final expense to family members present?",
        "options": {
            "A": "Ignore them",
            "B": "Include them in the conversation about how it protects them from financial burden",
            "C": "Ask them to leave",
            "D": "Only talk to the applicant"
        },
        "correct_answer": "B",
        "explanation": "Include family members - they often influence the decision and benefit directly from the protection. Address their concerns too."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is the 'level benefit' tier in final expense?",
        "options": {
            "A": "Decreasing coverage",
            "B": "Immediate full death benefit from day one for healthy applicants",
            "C": "No coverage",
            "D": "Term coverage"
        },
        "correct_answer": "B",
        "explanation": "Level benefit (preferred or standard) provides immediate full death benefit coverage for applicants who qualify based on health questions."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Underwriting",
        "question": "What is a 'knockout' question in final expense underwriting?",
        "options": {
            "A": "A boxing question",
            "B": "A health question that, if answered yes, automatically disqualifies or limits coverage",
            "C": "The first question asked",
            "D": "An optional question"
        },
        "correct_answer": "B",
        "explanation": "Knockout questions identify serious conditions that automatically result in decline or graded benefit placement (e.g., 'Are you currently receiving hospice care?')."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is 'field underwriting' in final expense sales?",
        "options": {
            "A": "Underwriting in a corn field",
            "B": "The agent's assessment of the applicant to select the appropriate product tier",
            "C": "Home office review",
            "D": "Medical exam"
        },
        "correct_answer": "B",
        "explanation": "Field underwriting is the agent's on-site assessment using health questions to determine whether the applicant qualifies for level, graded, or guaranteed issue."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is 'guaranteed issue' final expense?",
        "options": {
            "A": "The best coverage tier",
            "B": "Coverage with no health questions, but typically graded benefits and higher premiums",
            "C": "Free coverage",
            "D": "Term life insurance"
        },
        "correct_answer": "B",
        "explanation": "Guaranteed issue accepts all applicants within age limits without health questions, but has graded benefits and higher premiums due to higher risk."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Communication",
        "question": "How do you handle the objection 'I don't want to think about death'?",
        "options": {
            "A": "Force the conversation",
            "B": "Acknowledge the discomfort but focus on protecting family and providing peace of mind",
            "C": "End the conversation",
            "D": "Change the subject permanently"
        },
        "correct_answer": "B",
        "explanation": "Acknowledge feelings, then reframe: 'This isn't about death, it's about making sure your family is protected and you have peace of mind.'"
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What does 'assignment' to a funeral home mean?",
        "options": {
            "A": "Homework assignment",
            "B": "Directing the death benefit to be paid directly to a funeral home",
            "C": "Changing beneficiaries",
            "D": "Canceling the policy"
        },
        "correct_answer": "B",
        "explanation": "Assignment allows directing some or all of the death benefit directly to a funeral home to pay for services upon death."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Sales Process",
        "question": "What is the 'kitchen table' sales approach in final expense?",
        "options": {
            "A": "Selling kitchen tables",
            "B": "In-home, face-to-face presentations in a comfortable setting",
            "C": "Phone sales only",
            "D": "Online sales"
        },
        "correct_answer": "B",
        "explanation": "Kitchen table sales refers to the traditional in-home presentation style that builds trust and allows for personalized, empathetic conversations."
    },
])

# Final Expense - Expert (12 questions)
QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'MIB' checking in final expense underwriting?",
        "options": {
            "A": "A government agency",
            "B": "Medical Information Bureau - database checking past insurance application medical disclosures",
            "C": "A marketing firm",
            "D": "A funeral home network"
        },
        "correct_answer": "B",
        "explanation": "MIB (Medical Information Bureau) checks reveal medical conditions disclosed on previous insurance applications, helping verify applicant statements."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'prescription database checking' (Rx check) in final expense?",
        "options": {
            "A": "Checking for drug interactions",
            "B": "Reviewing prescription history to verify health conditions and medications",
            "C": "Counting pills",
            "D": "Doctor verification"
        },
        "correct_answer": "B",
        "explanation": "Rx database checks reveal prescription history, helping verify disclosed conditions and identify undisclosed health issues."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'face amount buildup' in final expense?",
        "options": {
            "A": "Makeup application",
            "B": "Some policies that increase death benefit over time through dividends or rider",
            "C": "Decreasing coverage",
            "D": "Premium increase"
        },
        "correct_answer": "B",
        "explanation": "Some final expense policies offer increasing death benefits through dividends or increasing benefit riders, providing inflation protection."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is 'agency replacement' in final expense?",
        "options": {
            "A": "Changing insurance companies",
            "B": "Replacing a client's existing final expense policy with a new one - requires documentation",
            "C": "Replacing agents",
            "D": "Replacing leads"
        },
        "correct_answer": "B",
        "explanation": "Replacement involves substituting existing coverage with new coverage - requires special forms, client acknowledgment, and suitability justification."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What does 'ADL' refer to in final expense health questions?",
        "options": {
            "A": "Annual Death Limits",
            "B": "Activities of Daily Living - bathing, dressing, eating, toileting, transferring, continence",
            "C": "Additional Death Liability",
            "D": "Agent Delivery Log"
        },
        "correct_answer": "B",
        "explanation": "ADLs (Activities of Daily Living) assess functional ability. Inability to perform ADLs independently often affects eligibility or tier placement."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'accelerated death benefit' in final expense?",
        "options": {
            "A": "Faster claim payment",
            "B": "Accessing a portion of death benefit while living if diagnosed with terminal illness",
            "C": "Increased premium",
            "D": "Double coverage"
        },
        "correct_answer": "B",
        "explanation": "Accelerated death benefit (living benefit) allows accessing a portion of the death benefit if diagnosed with a qualifying terminal illness."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is 'conservation' in final expense?",
        "options": {
            "A": "Environmental protection",
            "B": "Efforts to keep an existing policy in force rather than allowing it to lapse",
            "C": "Selling more policies",
            "D": "Lead generation"
        },
        "correct_answer": "B",
        "explanation": "Conservation involves working with clients considering lapse to help them keep coverage in force, protecting both the client and renewal commissions."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is 'rescission' in final expense?",
        "options": {
            "A": "A discount",
            "B": "Voiding a policy for material misrepresentation on the application",
            "C": "Renewal",
            "D": "Rate increase"
        },
        "correct_answer": "B",
        "explanation": "Rescission is the insurer's right to void a policy (typically within contestable period) if the applicant made material misrepresentations."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'pre-need' vs. 'at-need' in the funeral context?",
        "options": {
            "A": "They're the same",
            "B": "Pre-need is planning before death; at-need is arrangements at time of death",
            "C": "Pre-need is more expensive",
            "D": "At-need provides better coverage"
        },
        "correct_answer": "B",
        "explanation": "Pre-need plans are arranged before death (often funded with final expense), while at-need arrangements are made immediately following death."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Sales Process",
        "question": "What is 'tele-app' or 'phone interview' in final expense?",
        "options": {
            "A": "A telephone sale",
            "B": "A recorded phone interview conducted by the carrier to verify application information",
            "C": "Agent training call",
            "D": "Customer service call"
        },
        "correct_answer": "B",
        "explanation": "Tele-app/phone interview is a recorded carrier call verifying the applicant understands the policy and confirming health information."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Underwriting",
        "question": "What is a 'build chart' used for in final expense?",
        "options": {
            "A": "Construction planning",
            "B": "Determining if height/weight ratios fall within acceptable limits",
            "C": "Building schedules",
            "D": "Agent quotas"
        },
        "correct_answer": "B",
        "explanation": "Build charts specify acceptable height/weight combinations for coverage. Applicants outside limits may be declined or rated."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'policy loan' availability in final expense whole life?",
        "options": {
            "A": "Not available",
            "B": "Borrowing against cash value, though often limited due to small face amounts",
            "C": "Available only after 20 years",
            "D": "Only for premium payment"
        },
        "correct_answer": "B",
        "explanation": "While technically available, policy loans in final expense are often impractical due to small face amounts and limited cash value accumulation."
    },
])

async def seed_additional_questions():
    """Insert additional questions into the database"""
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url or not db_name:
        print("Error: MONGO_URL or DB_NAME not set")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Seeding {len(QUESTIONS)} additional quiz questions...")
    
    # Add IDs and timestamps to each question
    for q in QUESTIONS:
        q['id'] = str(uuid.uuid4())
        q['created_at'] = datetime.now(timezone.utc).isoformat()
        q['is_active'] = True
    
    # Insert all questions
    if QUESTIONS:
        result = await db.quiz_questions.insert_many(QUESTIONS)
        print(f"Inserted {len(result.inserted_ids)} questions")
    
    # Show final counts
    products = ["IUL", "FIA", "Term", "Final Expense"]
    difficulties = ["Easy", "Intermediate", "Expert"]
    
    print("\nFinal question counts:")
    for product in products:
        print(f"\n{product}:")
        for diff in difficulties:
            count = await db.quiz_questions.count_documents({
                "product": product,
                "difficulty": diff
            })
            print(f"  {diff}: {count}")
    
    total = await db.quiz_questions.count_documents({})
    print(f"\nTotal questions: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_additional_questions())
