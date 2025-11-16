"""
Seed script to create demo business and admin account for development and testing.
Run this script to set up a complete demo environment.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.database import AsyncSessionLocal, engine, Base
from app.models import User, BusinessContext, AutonomousAction, Briefing
from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_demo_data():
    """Create comprehensive demo data for testing"""
    print("🌱 Starting seed process...")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Demo Admin User
        print("\n👤 Creating demo admin user...")
        result = await session.execute(
            select(User).where(User.username == "demo_admin")
        )
        demo_user = result.scalar_one_or_none()

        if not demo_user:
            demo_user = User(
                telegram_id="demo_telegram_id",
                username="demo_admin",
                email="demo@alfaassistant.com",
                full_name="Demo Business Owner",
                hashed_password=pwd_context.hash("demo123"),
                is_active=True,
                business_name="Demo Coffee Shop",
                business_type="coffee_shop",
                business_data={
                    "description": "A cozy coffee shop in the heart of Moscow",
                    "established": "2020-01-15",
                    "specialties": ["artisan coffee", "pastries", "breakfast"]
                }
            )
            session.add(demo_user)
            await session.flush()
            print(f"✅ Created demo admin user (ID: {demo_user.id})")
            print(f"   Username: demo_admin")
            print(f"   Password: demo123")
        else:
            print(f"✅ Demo admin user already exists (ID: {demo_user.id})")

        # 2. Create Regular Admin User (for production use)
        print("\n👤 Creating admin user...")
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                telegram_id=None,  # Can be linked later
                username="admin",
                email="admin@example.com",
                full_name="Administrator",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True,
                business_name="My Business",
                business_type="other",
                business_data={}
            )
            session.add(admin_user)
            await session.flush()
            print(f"✅ Created admin user (ID: {admin_user.id})")
            print(f"   Username: admin")
            print(f"   Password: admin123")
        else:
            print(f"✅ Admin user already exists (ID: {admin_user.id})")

        # 3. Create Demo Business Context
        print("\n🏢 Creating demo business context...")
        result = await session.execute(
            select(BusinessContext).where(BusinessContext.user_id == demo_user.id)
        )
        business_context = result.scalar_one_or_none()

        if not business_context:
            business_context = BusinessContext(
                user_id=demo_user.id,
                business_name="Demo Coffee Shop",
                business_type="coffee_shop",
                location="Moscow, Arbat Street",
                operating_hours={
                    "monday": {"open": "08:00", "close": "22:00"},
                    "tuesday": {"open": "08:00", "close": "22:00"},
                    "wednesday": {"open": "08:00", "close": "22:00"},
                    "thursday": {"open": "08:00", "close": "22:00"},
                    "friday": {"open": "08:00", "close": "23:00"},
                    "saturday": {"open": "09:00", "close": "23:00"},
                    "sunday": {"open": "09:00", "close": "22:00"}
                },
                average_daily_revenue=75000,  # ₽75,000 per day
                typical_customer_count=150,
                employee_count=8,
                key_metrics={
                    "avg_transaction": 500,  # ₽500
                    "peak_hours": ["08:00-10:00", "12:00-14:00", "17:00-19:00"],
                    "popular_items": ["Cappuccino", "Croissant", "Americano"],
                    "monthly_revenue": 2250000,  # ₽2.25M
                    "customer_satisfaction": 4.7
                },
                decision_thresholds={
                    "auto_approve": {"max_amount": 10000},
                    "require_approval": {"amount_range": [10000, 50000]},
                    "always_escalate": {"min_amount": 50000}
                }
            )
            session.add(business_context)
            print("✅ Created demo business context")
        else:
            print("✅ Demo business context already exists")

        # 4. Create Admin Business Context
        print("\n🏢 Creating admin business context...")
        result = await session.execute(
            select(BusinessContext).where(BusinessContext.user_id == admin_user.id)
        )
        admin_context = result.scalar_one_or_none()

        if not admin_context:
            admin_context = BusinessContext(
                user_id=admin_user.id,
                business_name="My Business",
                business_type="other",
                location="Moscow",
                operating_hours={
                    "open": "09:00",
                    "close": "18:00"
                },
                average_daily_revenue=50000,
                typical_customer_count=100,
                employee_count=5,
                key_metrics={},
                decision_thresholds={
                    "auto_approve": {"max_amount": 10000},
                    "require_approval": {"amount_range": [10000, 50000]},
                    "always_escalate": {"min_amount": 50000}
                }
            )
            session.add(admin_context)
            print("✅ Created admin business context")
        else:
            print("✅ Admin business context already exists")

        # 5. Create Sample Autonomous Actions for Demo User
        print("\n🤖 Creating sample autonomous actions...")
        result = await session.execute(
            select(AutonomousAction).where(AutonomousAction.user_id == demo_user.id)
        )
        existing_actions = result.scalars().all()

        if not existing_actions:
            sample_actions = [
                {
                    "action_type": "inventory_order",
                    "description": "Ordered 50kg premium coffee beans from trusted supplier",
                    "impact_amount": 8500,
                    "required_approval": False,
                    "was_approved": True,
                    "executed_at": datetime.now() - timedelta(hours=2),
                    "action_metadata": {
                        "reasoning": "Current stock below threshold (10kg remaining). Average consumption: 8kg/day.",
                        "confidence_score": 0.95
                    }
                },
                {
                    "action_type": "staff_schedule",
                    "description": "Adjusted tomorrow's shift schedule: Added Maria for morning rush (8-11 AM)",
                    "impact_amount": 1200,
                    "required_approval": False,
                    "was_approved": True,
                    "executed_at": datetime.now() - timedelta(hours=4),
                    "action_metadata": {
                        "reasoning": "Weather forecast shows sunny day. 30% increase in foot traffic expected.",
                        "confidence_score": 0.88
                    }
                },
                {
                    "action_type": "marketing_campaign",
                    "description": "Launched Instagram promotion: 'Buy 2 pastries, get 1 free' for tomorrow",
                    "impact_amount": 3000,
                    "required_approval": False,
                    "was_approved": True,
                    "executed_at": datetime.now() - timedelta(hours=6),
                    "action_metadata": {
                        "reasoning": "Excess pastry inventory (120 units). Expiry in 24h. Reduce waste, drive traffic.",
                        "confidence_score": 0.82
                    }
                },
                {
                    "action_type": "price_adjustment",
                    "description": "Temporary price increase on iced drinks: +15% (₽450 → ₽520)",
                    "impact_amount": 12000,
                    "required_approval": True,
                    "was_approved": None,
                    "executed_at": datetime.now() - timedelta(minutes=30),
                    "action_metadata": {
                        "reasoning": "Heat wave alert for 3 days. 40% surge in cold beverage sales expected.",
                        "confidence_score": 0.76
                    }
                },
                {
                    "action_type": "supplier_negotiation",
                    "description": "Negotiated 8% discount with milk supplier for quarterly contract",
                    "impact_amount": 49920,
                    "required_approval": True,
                    "was_approved": None,
                    "executed_at": datetime.now() - timedelta(minutes=15),
                    "action_metadata": {
                        "reasoning": "200L/week consumption. ₽49,920 annual savings. Good deal.",
                        "confidence_score": 0.91
                    }
                },
                {
                    "action_type": "equipment_purchase",
                    "description": "Recommended: Purchase second espresso machine for backup",
                    "impact_amount": 185000,
                    "required_approval": True,
                    "was_approved": None,
                    "executed_at": datetime.now() - timedelta(minutes=5),
                    "action_metadata": {
                        "reasoning": "Main machine is 4 years old. ₽180K/month revenue loss risk if it fails.",
                        "confidence_score": 0.73
                    }
                }
            ]

            for action_data in sample_actions:
                action = AutonomousAction(
                    user_id=demo_user.id,
                    action_type=action_data["action_type"],
                    description=action_data["description"],
                    impact_amount=action_data["impact_amount"],
                    required_approval=action_data["required_approval"],
                    was_approved=action_data["was_approved"],
                    executed_at=action_data["executed_at"],
                    action_metadata=action_data.get("action_metadata", {})
                )
                session.add(action)

            print(f"✅ Created {len(sample_actions)} sample actions")
        else:
            print(f"✅ Sample actions already exist ({len(existing_actions)} actions)")

        # 6. Create Sample Briefing for Demo User
        print("\n📋 Creating sample briefing...")
        today = datetime.now().date()
        result = await session.execute(
            select(Briefing).where(
                Briefing.user_id == demo_user.id,
                Briefing.date == today
            )
        )
        existing_briefing = result.scalar_one_or_none()

        if not existing_briefing:
            briefing_content = {
                "summary": """Good morning! Here's your business briefing for Demo Coffee Shop:

**📊 Yesterday's Performance:**
- Revenue: ₽78,500 (+4.5% vs average)
- Customers served: 162 (+8%)
- Average transaction: ₽485
- Customer satisfaction: 4.8/5.0 ⭐

**🤖 Autonomous Actions Taken:**
- Ordered 50kg premium coffee beans (₽8,500)
- Adjusted staff schedule for weekend rush
- Launched Instagram pastry promotion to reduce waste

**⏳ Pending Your Approval:**
- Price adjustment for iced drinks during heat wave (₽12K impact)
- Supplier negotiation: 8% milk discount (₽49K annual savings)
- Equipment purchase recommendation: Backup espresso machine (₽185K)

**🎯 Today's Priorities:**
1. Review pending approvals above
2. Peak hours expected: 8-10 AM, 12-2 PM, 5-7 PM
3. Weather: Sunny, 28°C - expect high foot traffic
4. Inventory alert: Croissant stock low, reorder suggested

**💡 AI Insights:**
- Your Instagram promotion is trending: 47 shares, 230 likes
- Competitor "Coffee House" raised prices by 10% - opportunity to capture market share
- Weekend revenue forecast: ₽165K (based on weather and trends)

Have a great day! I'll keep monitoring and will alert you if anything needs attention.""",
                "metrics": {
                    "revenue": 78500,
                    "customers": 162,
                    "avg_transaction": 485,
                    "satisfaction": 4.8,
                    "actions_completed": 3,
                    "time_saved_hours": 2.5,
                    "pending_approvals": 3,
                    "forecast_revenue": 165000
                },
                "completed_actions": [
                    "Ordered 50kg premium coffee beans",
                    "Adjusted staff schedule",
                    "Launched Instagram promotion"
                ],
                "pending_items": [
                    "Price adjustment for iced drinks",
                    "Supplier contract negotiation",
                    "Equipment purchase approval"
                ],
                "recommendations": [
                    "Review pending high-value approvals",
                    "Monitor Instagram campaign performance",
                    "Prepare for high foot traffic today"
                ]
            }

            briefing = Briefing(
                user_id=demo_user.id,
                date=today,
                content=briefing_content,
                delivered=False
            )
            session.add(briefing)
            print("✅ Created sample briefing for today")
        else:
            print("✅ Sample briefing already exists")

        # Commit all changes
        await session.commit()

        print("\n" + "="*60)
        print("✅ SEED COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 DEMO ACCOUNT CREDENTIALS:")
        print("-" * 60)
        print("Username: demo_admin")
        print("Password: demo123")
        print("Business: Demo Coffee Shop")
        print("Type: Coffee Shop in Moscow")
        print("-" * 60)
        print("\n📝 ADMIN ACCOUNT CREDENTIALS:")
        print("-" * 60)
        print("Username: admin")
        print("Password: admin123")
        print("Business: My Business")
        print("-" * 60)
        print("\n🎯 NEXT STEPS:")
        print("1. Start the backend: docker compose up -d")
        print("2. Login at: http://localhost:3000/login")
        print("3. Use demo_admin/demo123 to see full demo data")
        print("4. Use admin/admin123 for your own account")
        print("5. In Telegram bot, use /start and select 'Demo Mode'")
        print("\n💡 TIP: Demo mode shows pre-populated data for testing!")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(create_demo_data())
