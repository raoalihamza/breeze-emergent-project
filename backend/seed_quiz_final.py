"""
Final batch of Quiz Questions for Breeze Matrix
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

FINAL_QUESTIONS = []

# ==================== FINAL BATCH OF IUL QUESTIONS ====================

FINAL_QUESTIONS.extend([
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Can the premium amount change in an IUL policy?",
        "options": {
            "A": "No, it's always fixed",
            "B": "Yes, IUL offers flexible premiums within certain limits",
            "C": "Only if you miss a payment",
            "D": "Premiums automatically increase annually"
        },
        "correct_answer": "B",
        "explanation": "IUL policies offer premium flexibility, allowing you to adjust payment amounts within policy guidelines, subject to minimum and maximum limits."
    },
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What is the FIRST thing you should establish with a potential IUL client?",
        "options": {
            "A": "Their credit score",
            "B": "Their insurance needs and financial goals",
            "C": "How much premium they can pay",
            "D": "Their age"
        },
        "correct_answer": "B",
        "explanation": "Understanding the client's needs and goals first ensures you can recommend an appropriate solution, rather than fitting them into a product."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What role does the 'general account' play in an IUL's safety guarantees?",
        "options": {
            "A": "It provides higher returns",
            "B": "It's backed by the insurance company's assets and reserves, providing security",
            "C": "It's a separate investment account",
            "D": "It doesn't affect the policyholder"
        },
        "correct_answer": "B",
        "explanation": "IUL cash values are held in the insurer's general account, backed by the company's assets and reserves, providing the security behind the 0% floor guarantee."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A client age 35 is considering IUL for retirement supplementation. What's the key advantage of their age?",
        "options": {
            "A": "They get free coverage",
            "B": "Lower COI costs and longer time horizon for cash value accumulation",
            "C": "Age doesn't matter",
            "D": "They can skip premiums"
        },
        "correct_answer": "B",
        "explanation": "Starting young means lower cost of insurance, more years for tax-deferred growth, and more time to recover from any flat market years."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How does 'overloan protection' work in some IUL policies?",
        "options": {
            "A": "It prevents you from taking loans",
            "B": "It helps prevent policy lapse due to excessive loans by adjusting the death benefit or structure",
            "C": "It increases your loan amount",
            "D": "It's automatic in all policies"
        },
        "correct_answer": "B",
        "explanation": "Overloan protection riders help prevent policy lapse when loan values become too high relative to cash value, typically by adjusting the policy structure to maintain coverage."
    },
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A surgeon earning $800K/year asks about asset protection. How might IUL help?",
        "options": {
            "A": "IUL provides no asset protection",
            "B": "In many states, life insurance cash values have creditor protection, which may help shield assets",
            "C": "IUL is only for retirement",
            "D": "Asset protection isn't a valid concern"
        },
        "correct_answer": "B",
        "explanation": "Many states offer varying degrees of creditor protection for life insurance cash values. For high-liability professionals, this can be an additional planning benefit."
    },
])

# ==================== FINAL BATCH OF FIA QUESTIONS ====================

FINAL_QUESTIONS.extend([
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Are FIA returns guaranteed to match the S&P 500?",
        "options": {
            "A": "Yes, always",
            "B": "No, returns are linked to but don't match the index exactly due to caps, floors, and participation rates",
            "C": "Only in good years",
            "D": "FIAs don't use indices"
        },
        "correct_answer": "B",
        "explanation": "FIA returns are linked to an index but are subject to caps, participation rates, and spreads, so they won't match actual index returns."
    },
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "When explaining FIA to a client, what's the most important concept to communicate?",
        "options": {
            "A": "The exact historical returns",
            "B": "The balance between growth potential and principal protection",
            "C": "How much commission you'll earn",
            "D": "That it's better than stocks"
        },
        "correct_answer": "B",
        "explanation": "Clients need to understand the core value proposition: opportunity for index-linked growth with protection against loss of principal."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What happens to FIA gains once they're credited?",
        "options": {
            "A": "They can be lost in future down years",
            "B": "They're locked in and cannot be lost due to index performance",
            "C": "They're returned to the insurance company",
            "D": "They convert to term insurance"
        },
        "correct_answer": "B",
        "explanation": "Once interest is credited to a FIA, it becomes part of the protected principal. Future index declines cannot reduce previously credited gains."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "If a client needs funds during the surrender period beyond the free withdrawal, what happens?",
        "options": {
            "A": "No withdrawals are allowed",
            "B": "Surrender charges apply to amounts exceeding the free withdrawal provision",
            "C": "All funds are frozen",
            "D": "The policy automatically cancels"
        },
        "correct_answer": "B",
        "explanation": "Withdrawals beyond the free withdrawal amount incur surrender charges during the surrender period. This must be clearly disclosed before purchase."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'spread' in FIA crediting and how does it differ from a cap?",
        "options": {
            "A": "They're the same thing",
            "B": "Spread is subtracted from the return; cap limits maximum return. A 10% return with 2% spread = 8%, but with 9% cap = 9%",
            "C": "Spread only applies to losses",
            "D": "Cap is added to returns"
        },
        "correct_answer": "B",
        "explanation": "Spread reduces the credited rate by a fixed amount (index return minus spread). Cap limits the maximum credit. They work differently and can result in different outcomes."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Suitability",
        "question": "When comparing a FIA to a fixed annuity for a conservative client, what's the key trade-off?",
        "options": {
            "A": "Fixed annuities always pay more",
            "B": "FIA offers potential for higher returns but variable crediting; fixed offers predictable but potentially lower returns",
            "C": "FIA has shorter surrender periods",
            "D": "There's no difference in risk"
        },
        "correct_answer": "B",
        "explanation": "Fixed annuities offer predictable, declared rates. FIAs offer higher potential returns but with variability. The choice depends on the client's need for predictability vs. growth potential."
    },
])

# ==================== FINAL BATCH OF TERM QUESTIONS ====================

FINAL_QUESTIONS.extend([
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "What does 'non-renewable' term mean?",
        "options": {
            "A": "You can't renew regardless of health",
            "B": "The policy ends after the term with no renewal option",
            "C": "Premiums can't be renewed",
            "D": "It's eco-friendly insurance"
        },
        "correct_answer": "B",
        "explanation": "Non-renewable term policies end at the expiration of the term period with no option to continue coverage, unlike guaranteed renewable term."
    },
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Amy, 28, is single with no kids but has $30,000 in student loans co-signed by her parents. Does she need life insurance?",
        "options": {
            "A": "No, single people don't need insurance",
            "B": "Yes, to protect her parents from the co-signed debt if she passes away",
            "C": "Only if she's married",
            "D": "Student loans don't need insurance"
        },
        "correct_answer": "B",
        "explanation": "Co-signed debt doesn't disappear at death. Amy's parents would be responsible for $30,000. Term insurance protects them from this financial burden."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What is a 'child rider' on a term policy?",
        "options": {
            "A": "Insurance for a child's bicycle",
            "B": "A rider providing small death benefits for all children, often convertible later",
            "C": "Makes the child the owner",
            "D": "Reduces premium if you have children"
        },
        "correct_answer": "B",
        "explanation": "A child rider provides a small death benefit (often $10,000-$25,000) for all eligible children under one premium. Many are convertible to permanent insurance later without evidence of insurability."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Compliance",
        "question": "When must an agent disclose that they're replacing an existing policy with a new term policy?",
        "options": {
            "A": "Never, it's private",
            "B": "When any existing coverage will lapse as a result of the new purchase",
            "C": "Only if asked",
            "D": "Only for permanent policies"
        },
        "correct_answer": "B",
        "explanation": "Replacement regulations require disclosure when new insurance will cause existing coverage to lapse, ensuring clients understand the implications of switching."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "What is 'premium banding' in term life pricing?",
        "options": {
            "A": "A rubber band around premium payments",
            "B": "Death benefit ranges (bands) with different rates per thousand; higher face amounts may have lower unit costs",
            "C": "Monthly payment groupings",
            "D": "A discount for paying annually"
        },
        "correct_answer": "B",
        "explanation": "Premium banding means cost per $1,000 of coverage may decrease at certain thresholds (e.g., $250K, $500K, $1M). Sometimes increasing coverage to the next band can actually lower total premium."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client owns a term policy and develops a serious health condition. Their term expires in 3 years. What strategy should you discuss?",
        "options": {
            "A": "Wait until expiration to address",
            "B": "Consider converting to permanent insurance now while conversion privilege exists, preserving insurability",
            "C": "Cancel the policy immediately",
            "D": "Nothing can be done"
        },
        "correct_answer": "B",
        "explanation": "Converting while the conversion privilege exists locks in permanent coverage regardless of current health, preserving insurability that would be lost if they waited until term expiration."
    },
])

# ==================== FINAL BATCH OF FINAL EXPENSE QUESTIONS ====================

FINAL_QUESTIONS.extend([
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Product Knowledge",
        "question": "Do final expense policies build cash value?",
        "options": {
            "A": "No, never",
            "B": "Yes, but typically minimal amounts",
            "C": "Only after 20 years",
            "D": "Cash value equals the death benefit"
        },
        "correct_answer": "B",
        "explanation": "As whole life policies, final expense products do build cash value over time, though amounts are typically small due to the lower premiums and death benefits."
    },
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Suitability",
        "question": "Why might someone choose final expense over traditional whole life?",
        "options": {
            "A": "Higher death benefits",
            "B": "Simplified underwriting and affordable premiums designed for seniors' needs",
            "C": "Better cash value growth",
            "D": "Shorter application process only"
        },
        "correct_answer": "B",
        "explanation": "Final expense offers simplified underwriting (no medical exams), affordable premiums, and death benefits sized appropriately for end-of-life costs."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Product Knowledge",
        "question": "What's the difference between 'pre-need' and 'final expense' insurance?",
        "options": {
            "A": "They're exactly the same",
            "B": "Pre-need is sold through funeral homes for specific funeral costs; final expense is general coverage for any end-of-life expense",
            "C": "Final expense pays more",
            "D": "Pre-need has no waiting period"
        },
        "correct_answer": "B",
        "explanation": "Pre-need insurance is typically sold by funeral homes for specific funeral arrangements. Final expense is a more flexible whole life policy that can be used for any end-of-life costs."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client's family member says, 'Mom doesn't need insurance, we'll pay for everything.' How should you proceed?",
        "options": {
            "A": "Leave immediately",
            "B": "Ensure the decision is Mom's to make, while respecting family input and exploring if Mom wants this independence",
            "C": "Ignore the family member",
            "D": "Only speak to the family member going forward"
        },
        "correct_answer": "B",
        "explanation": "While respecting family dynamics, ensure the senior client makes their own informed decision. Many seniors want to handle their own final expenses rather than burden family."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Product Knowledge",
        "question": "How do 'face amount options' work in final expense policies?",
        "options": {
            "A": "You can only get one amount",
            "B": "Carriers offer multiple face amounts based on health qualification level",
            "C": "Face amount is determined by age only",
            "D": "All applicants get the same amount"
        },
        "correct_answer": "B",
        "explanation": "Final expense carriers typically offer varying face amounts based on the applicant's health qualification (Level, Graded, Guaranteed), with healthier applicants qualifying for higher amounts."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is 'mental capacity' and why is it crucial in final expense sales to seniors?",
        "options": {
            "A": "Not relevant to insurance",
            "B": "The client must understand what they're buying; sales to those who lack capacity are voidable and potentially fraudulent",
            "C": "Only matters for large policies",
            "D": "Family members determine this"
        },
        "correct_answer": "B",
        "explanation": "Mental capacity means the client understands the nature and consequences of the purchase. Sales to those lacking capacity are ethically and legally problematic and may be voided."
    },
])

# ==================== ADDITIONAL MIXED QUESTIONS ====================

FINAL_QUESTIONS.extend([
    # More IUL
    {
        "product": "IUL",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "David, age 45, wants life insurance that will help pay for his children's college. How can IUL help?",
        "options": {
            "A": "IUL can't help with college funding",
            "B": "Cash value can be accessed through loans or withdrawals to help pay college costs",
            "C": "IUL pays tuition directly",
            "D": "Only 529 plans work for college"
        },
        "correct_answer": "B",
        "explanation": "IUL cash value can be accessed through tax-free loans to help fund college costs while maintaining the death benefit for protection."
    },
    {
        "product": "IUL",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client's Fidelity & Guaranty IUL has been in force for 15 years. They now need funds for an emergency. What options exist?",
        "options": {
            "A": "Cancel the policy only option",
            "B": "Policy loans, partial withdrawals, or surrender; each has different tax and policy implications",
            "C": "They can't access funds",
            "D": "Emergency funds aren't allowed"
        },
        "correct_answer": "B",
        "explanation": "After 15 years, they can take policy loans (tax-free if managed properly), partial withdrawals (up to basis), or surrender. Each option has different implications."
    },
    # More FIA
    {
        "product": "FIA",
        "difficulty": "Easy",
        "category": "Client Scenarios",
        "question": "Helen, 62, has $150,000 in a money market earning 0.5%. She wants better returns without stock market risk. What might you recommend?",
        "options": {
            "A": "Put it all in stocks",
            "B": "A Fixed Indexed Annuity offering growth potential with principal protection",
            "C": "Leave it in money market",
            "D": "Buy term insurance"
        },
        "correct_answer": "B",
        "explanation": "A FIA offers Helen potential for better returns than money market while protecting her principal from market losses, matching her risk tolerance and goals."
    },
    {
        "product": "FIA",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client purchased a FIA with Fidelity & Guaranty Life 5 years ago. The surrender period is 10 years. They want to move to a different carrier. What should they know?",
        "options": {
            "A": "They can move anytime without penalty",
            "B": "Moving now would incur surrender charges; they should evaluate if benefits outweigh costs",
            "C": "They're locked in forever",
            "D": "Surrender charges don't apply to transfers"
        },
        "correct_answer": "B",
        "explanation": "With 5 years remaining in a 10-year surrender period, moving would incur charges. They must evaluate whether the new product's benefits outweigh the surrender cost."
    },
    # More Term
    {
        "product": "Term",
        "difficulty": "Easy",
        "category": "Compliance",
        "question": "What should a client understand about their beneficiary designation?",
        "options": {
            "A": "It's permanent and can't change",
            "B": "They can change beneficiaries anytime, and should review regularly",
            "C": "Only family members can be beneficiaries",
            "D": "The insurance company chooses beneficiaries"
        },
        "correct_answer": "B",
        "explanation": "Beneficiary designations can typically be changed anytime by the policy owner. Regular review ensures designations reflect current wishes, especially after life changes."
    },
    {
        "product": "Term",
        "difficulty": "Intermediate",
        "category": "Client Scenarios",
        "question": "A client age 40 with a 20-year mortgage should consider which term length?",
        "options": {
            "A": "10-year term",
            "B": "20 or 30-year term to cover the full mortgage period",
            "C": "Annual renewable term",
            "D": "Term length doesn't matter"
        },
        "correct_answer": "B",
        "explanation": "To fully protect the mortgage obligation, a 20 or 30-year term ensures coverage throughout the mortgage period. A 10-year term would leave 10+ years unprotected."
    },
    # More Final Expense
    {
        "product": "Final Expense",
        "difficulty": "Easy",
        "category": "Sales Process",
        "question": "What's the best way to discuss funeral costs with a client?",
        "options": {
            "A": "Use scare tactics",
            "B": "Discuss average costs sensitively and ask about their preferences and plans",
            "C": "Avoid the topic",
            "D": "Focus only on investment returns"
        },
        "correct_answer": "B",
        "explanation": "Discussing funeral costs should be handled sensitively, sharing average costs ($10,000-$15,000) while asking about their preferences, existing plans, and concerns about burdening family."
    },
    {
        "product": "Final Expense",
        "difficulty": "Intermediate",
        "category": "Suitability",
        "question": "A client wants final expense but can barely afford food. What should you do?",
        "options": {
            "A": "Sell them a policy anyway",
            "B": "Recognize this may not be suitable; basic needs should come before insurance premiums",
            "C": "Suggest they skip meals to pay premiums",
            "D": "Ignore their financial situation"
        },
        "correct_answer": "B",
        "explanation": "Suitability requires that insurance premiums don't compromise basic necessities. If a client can't afford basic needs, final expense may not be appropriate at this time."
    },
    # Cross-cutting compliance questions
    {
        "product": "IUL",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What records should an agent maintain after selling an IUL policy?",
        "options": {
            "A": "None required",
            "B": "Needs analysis, illustrations provided, suitability documentation, and notes from client meetings",
            "C": "Only the application",
            "D": "Records are the carrier's responsibility"
        },
        "correct_answer": "B",
        "explanation": "Agents should maintain comprehensive records including needs analysis, all illustrations shown, suitability documentation, and meeting notes to demonstrate proper sales practices."
    },
    {
        "product": "FIA",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client wants to place an inherited IRA from their deceased parent into a FIA. What must be considered?",
        "options": {
            "A": "No special considerations",
            "B": "Inherited IRA rules (SECURE Act), required distributions, and how surrender period aligns with distribution timeline",
            "C": "Inherited IRAs can't be put in FIAs",
            "D": "The inheritance tax only"
        },
        "correct_answer": "B",
        "explanation": "Inherited IRAs have distribution requirements under the SECURE Act. The FIA surrender period must align with distribution needs to avoid forced withdrawals with surrender charges."
    },
    {
        "product": "Term",
        "difficulty": "Expert",
        "category": "Compliance",
        "question": "What is 'material misrepresentation' and how does it affect a term policy?",
        "options": {
            "A": "A minor typo on the application",
            "B": "False statements that would have affected underwriting decisions; can lead to claim denial or policy rescission",
            "C": "Only matters for health questions",
            "D": "Has no impact after issue"
        },
        "correct_answer": "B",
        "explanation": "Material misrepresentation involves false statements that would have changed the underwriting decision. During the contestability period, it can result in claim denial or policy rescission."
    },
    {
        "product": "Final Expense",
        "difficulty": "Expert",
        "category": "Client Scenarios",
        "question": "A client with advanced dementia's daughter wants to buy final expense on her mother. What ethical concerns arise?",
        "options": {
            "A": "No concerns, proceed with sale",
            "B": "Questions of insurable interest, consent, and competency must be evaluated; potentially an unsuitable sale",
            "C": "Adult children can always buy on parents",
            "D": "Dementia doesn't affect insurance decisions"
        },
        "correct_answer": "B",
        "explanation": "Selling insurance when the insured lacks capacity to consent raises serious ethical and legal issues. The daughter may lack insurable interest, and the sale may be voidable."
    },
])

# Add unique IDs to all questions
for q in FINAL_QUESTIONS:
    q['id'] = str(uuid.uuid4())
    q['created_at'] = datetime.now(timezone.utc).isoformat()


async def seed_final_questions():
    """Add final batch of questions"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    if FINAL_QUESTIONS:
        await db.quiz_questions.insert_many(FINAL_QUESTIONS)
        
        total = await db.quiz_questions.count_documents({})
        print(f"Added {len(FINAL_QUESTIONS)} more questions. Total now: {total}")
        
        # Print breakdown
        print("\nFinal question breakdown:")
        for product in ['IUL', 'FIA', 'Term', 'Final Expense']:
            for difficulty in ['Easy', 'Intermediate', 'Expert']:
                count = await db.quiz_questions.count_documents({
                    'product': product,
                    'difficulty': difficulty
                })
                print(f"  {product} - {difficulty}: {count} questions")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_final_questions())
