"""
Carrier Seeder for Breeze Matrix
Seeds the 13 insurance carriers with their company colors and resources
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

# Carrier data with company colors and resources
CARRIERS = [
    {
        "name": "Aflac",
        "slug": "aflac",
        "description": "Supplemental insurance including accident, critical illness, and life insurance products.",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Aflac_katakana_logo.png/400px-Aflac_katakana_logo.png",
        "primary_color": "#00A3E0",
        "secondary_color": "#003057",
        "products": ["Final Expense", "Term Life", "Supplemental Health"],
        "agent_portal_url": "https://www.aflac.com/business/resources/agent-center/default.aspx",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.aflac.com/business/resources/underwriting/default.aspx", "type": "guidelines"},
            {"name": "Product Guide", "url": "https://www.aflac.com/business/products/default.aspx", "type": "product_guide"},
            {"name": "Agent Resources", "url": "https://www.aflac.com/business/resources/default.aspx", "type": "other"}
        ]
    },
    {
        "name": "American Amicable",
        "slug": "american-amicable",
        "description": "Specializes in final expense life insurance with simplified issue products.",
        "logo_url": "https://static.prod-images.emergentagent.com/jobs/048e97d8-c3a1-45e2-b971-6471d37f6898/images/0b0b5877219447956a8cc9cce082b873403917705cbd0c49d4fdf961fe3b9760.png",
        "primary_color": "#1E3A5F",
        "secondary_color": "#C5A572",
        "products": ["Final Expense", "Whole Life"],
        "agent_portal_url": "https://www.americanamicable.com/agent-login",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.americanamicable.com/underwriting", "type": "guidelines"},
            {"name": "Product Portfolio", "url": "https://www.americanamicable.com/products", "type": "product_guide"},
            {"name": "Agent Support", "url": "https://www.americanamicable.com/agent-support", "type": "other"}
        ]
    },
    {
        "name": "Americo",
        "slug": "americo",
        "description": "Life insurance and annuity solutions including IUL, term, and final expense products.",
        "logo_url": "https://epnkc.com/wp-content/uploads/2024/02/americo-logo.png",
        "primary_color": "#00529B",
        "secondary_color": "#8DC63F",
        "products": ["IUL", "Term Life", "Final Expense", "Annuities"],
        "agent_portal_url": "https://www.americo.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.americo.com/underwriting-guidelines", "type": "guidelines"},
            {"name": "Product Information", "url": "https://www.americo.com/products", "type": "product_guide"},
            {"name": "Marketing Resources", "url": "https://www.americo.com/marketing", "type": "other"}
        ]
    },
    {
        "name": "Ethos",
        "slug": "ethos",
        "description": "Modern, technology-driven term life insurance with instant approvals.",
        "logo_url": "https://res.cloudinary.com/value-penguin/image/upload/w_200/referral_logos/us/life_insurance/ethos-3",
        "primary_color": "#6366F1",
        "secondary_color": "#1E1B4B",
        "products": ["Term Life", "Whole Life"],
        "agent_portal_url": "https://www.ethoslife.com/agents",
        "resources": [
            {"name": "Underwriting Guide", "url": "https://www.ethoslife.com/underwriting", "type": "guidelines"},
            {"name": "Product Overview", "url": "https://www.ethoslife.com/products", "type": "product_guide"},
            {"name": "Agent Portal", "url": "https://www.ethoslife.com/agent-login", "type": "other"}
        ]
    },
    {
        "name": "United Home Life",
        "slug": "united-home-life",
        "description": "Final expense specialist with graded and level benefit whole life products.",
        "logo_url": "https://www.unitedhomelife.com/ResourcePackages/UHL/assets/src/images/UHL-logo.png",
        "primary_color": "#B8860B",
        "secondary_color": "#2F4F4F",
        "products": ["Final Expense", "Whole Life"],
        "agent_portal_url": "https://www.unitedhomelife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.unitedhomelife.com/underwriting", "type": "guidelines"},
            {"name": "Product Guide", "url": "https://www.unitedhomelife.com/products", "type": "product_guide"},
            {"name": "Rate Calculator", "url": "https://www.unitedhomelife.com/calculator", "type": "other"}
        ]
    },
    {
        "name": "Kansas City Life",
        "slug": "kansas-city-life",
        "description": "Full portfolio including term, whole life, and universal life insurance products.",
        "logo_url": "https://static.prod-images.emergentagent.com/jobs/048e97d8-c3a1-45e2-b971-6471d37f6898/images/1902ca99ec038cf5e7e451d99a2cb5873210a3e363d8ec81abdba561ca71ba0b.png",
        "primary_color": "#8B0000",
        "secondary_color": "#FFD700",
        "products": ["Term Life", "Whole Life", "Universal Life", "Final Expense"],
        "agent_portal_url": "https://www.kclife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.kclife.com/underwriting", "type": "guidelines"},
            {"name": "Product Portfolio", "url": "https://www.kclife.com/products", "type": "product_guide"},
            {"name": "Forms Library", "url": "https://www.kclife.com/forms", "type": "other"}
        ]
    },
    {
        "name": "Royal Neighbors",
        "slug": "royal-neighbors",
        "description": "Fraternal benefit society offering life insurance and annuity products.",
        "logo_url": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/Royal_Neighbors_of_America_logo.jpg/250px-Royal_Neighbors_of_America_logo.jpg",
        "primary_color": "#4B0082",
        "secondary_color": "#FFB6C1",
        "products": ["Term Life", "Whole Life", "Annuities", "Final Expense"],
        "agent_portal_url": "https://www.royalneighbors.org/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.royalneighbors.org/underwriting", "type": "guidelines"},
            {"name": "Product Information", "url": "https://www.royalneighbors.org/products", "type": "product_guide"},
            {"name": "Agent Resources", "url": "https://www.royalneighbors.org/agent-resources", "type": "other"}
        ]
    },
    {
        "name": "American Equity",
        "slug": "american-equity",
        "description": "Leading provider of fixed indexed annuities with competitive crediting strategies.",
        "logo_url": "https://assets.simpleviewinc.com/simpleview/image/upload/c_fill,f_jpg,h_200,q_80,w_300/v1/crm/desmoines/American-Equity-1--5a9f96755056a36_5a9f97f2-5056-a36a-06c7202ee6b35cbd.jpg",
        "primary_color": "#004C97",
        "secondary_color": "#78BE20",
        "products": ["Fixed Indexed Annuities", "Fixed Annuities"],
        "agent_portal_url": "https://www.american-equity.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.american-equity.com/underwriting", "type": "guidelines"},
            {"name": "Annuity Products", "url": "https://www.american-equity.com/products", "type": "product_guide"},
            {"name": "Sales Tools", "url": "https://www.american-equity.com/sales-tools", "type": "other"}
        ]
    },
    {
        "name": "Fidelity & Guaranty Life",
        "slug": "fidelity-guaranty",
        "description": "Fixed indexed annuities and indexed universal life with strong crediting options.",
        "logo_url": "https://success.fglife.com/hubfs/Logos%20(Current%202026)/Hubspot_FG%20Logo%20Name%20Full%20Color.svg",
        "primary_color": "#00843D",
        "secondary_color": "#003366",
        "products": ["IUL", "Fixed Indexed Annuities"],
        "agent_portal_url": "https://www.fglife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.fglife.com/underwriting", "type": "guidelines"},
            {"name": "IUL Product Guide", "url": "https://www.fglife.com/iul", "type": "product_guide"},
            {"name": "FIA Product Guide", "url": "https://www.fglife.com/annuities", "type": "product_guide"},
            {"name": "Agent Tools", "url": "https://www.fglife.com/tools", "type": "other"}
        ]
    },
    {
        "name": "Allianz",
        "slug": "allianz",
        "description": "Global insurance leader offering fixed indexed annuities with innovative features.",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Allianz_logo.svg/400px-Allianz_logo.svg.png",
        "primary_color": "#003781",
        "secondary_color": "#C4D600",
        "products": ["Fixed Indexed Annuities", "Fixed Annuities"],
        "agent_portal_url": "https://www.allianzlife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.allianzlife.com/underwriting", "type": "guidelines"},
            {"name": "Product Overview", "url": "https://www.allianzlife.com/products", "type": "product_guide"},
            {"name": "Training Center", "url": "https://www.allianzlife.com/training", "type": "other"}
        ]
    },
    {
        "name": "National Life Group",
        "slug": "national-life-group",
        "description": "Comprehensive life insurance portfolio including IUL, term, and living benefits.",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/NLG_White_Logo_2x_Green.png/250px-NLG_White_Logo_2x_Green.png",
        "primary_color": "#005A9C",
        "secondary_color": "#F7941D",
        "products": ["IUL", "Term Life", "Whole Life", "Annuities"],
        "agent_portal_url": "https://www.nationallife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.nationallife.com/underwriting", "type": "guidelines"},
            {"name": "IUL Product Suite", "url": "https://www.nationallife.com/iul", "type": "product_guide"},
            {"name": "Living Benefits Guide", "url": "https://www.nationallife.com/living-benefits", "type": "product_guide"},
            {"name": "Agent Portal", "url": "https://www.nationallife.com/agent-login", "type": "other"}
        ]
    },
    {
        "name": "TransAmerica",
        "slug": "transamerica",
        "description": "Full-service carrier with life, annuities, and supplemental health products.",
        "logo_url": "https://cdn.freebiesupply.com/logos/large/2x/transamerica-logo-png-transparent.png",
        "primary_color": "#E31837",
        "secondary_color": "#FFFFFF",
        "products": ["IUL", "Term Life", "Whole Life", "Annuities", "Long-Term Care"],
        "agent_portal_url": "https://www.transamerica.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.transamerica.com/underwriting", "type": "guidelines"},
            {"name": "Life Products", "url": "https://www.transamerica.com/life", "type": "product_guide"},
            {"name": "Annuity Products", "url": "https://www.transamerica.com/annuities", "type": "product_guide"},
            {"name": "Financial Tools", "url": "https://www.transamerica.com/tools", "type": "other"}
        ]
    },
    {
        "name": "Columbus Life",
        "slug": "columbus-life",
        "description": "Western & Southern company offering competitive IUL and term products.",
        "logo_url": "https://static.prod-images.emergentagent.com/jobs/048e97d8-c3a1-45e2-b971-6471d37f6898/images/b98bc117ac3d95a6d0c0b295c7383f16b6a51397b56ec743de01588e745ec99f.png",
        "primary_color": "#1C4587",
        "secondary_color": "#B8860B",
        "products": ["IUL", "Term Life", "Whole Life"],
        "agent_portal_url": "https://www.columbuslife.com/agents",
        "resources": [
            {"name": "Underwriting Guidelines", "url": "https://www.columbuslife.com/underwriting", "type": "guidelines"},
            {"name": "Product Portfolio", "url": "https://www.columbuslife.com/products", "type": "product_guide"},
            {"name": "Agent Resources", "url": "https://www.columbuslife.com/resources", "type": "other"}
        ]
    }
]


async def seed_carriers():
    """Seed the carriers database"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Clear existing carriers
    await db.carriers.delete_many({})
    
    # Insert all carriers
    for carrier in CARRIERS:
        carrier_doc = {
            'id': str(uuid.uuid4()),
            'name': carrier['name'],
            'slug': carrier['slug'],
            'description': carrier['description'],
            'logo_url': carrier.get('logo_url'),
            'primary_color': carrier['primary_color'],
            'secondary_color': carrier['secondary_color'],
            'products': carrier['products'],
            'agent_portal_url': carrier['agent_portal_url'],
            'resources': carrier['resources'],
            'guideline_url': carrier['resources'][0]['url'] if carrier['resources'] else None,
            'notes': None,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.carriers.insert_one(carrier_doc)
    
    print(f"Successfully seeded {len(CARRIERS)} carriers!")
    
    # List them
    for carrier in CARRIERS:
        print(f"  - {carrier['name']} ({carrier['primary_color']})")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_carriers())
