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
from app.models import (
    User, BusinessContext, AutonomousAction, Briefing,
    FinancialTransaction, CashFlowPrediction, LegalUpdate,
    Competitor, CompetitorAction, MarketTrend, ComplianceAlert
)
from passlib.context import CryptContext
from sqlalchemy import select
import hashlib

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

        # 7. Create Finance Data
        print("\n💰 Creating financial data...")
        result = await session.execute(
            select(FinancialTransaction).where(FinancialTransaction.user_id == demo_user.id)
        )
        existing_transactions = result.scalars().all()

        if not existing_transactions:
            # Create 30 days of realistic transactions
            transactions = []
            base_date = datetime.now() - timedelta(days=30)

            for day in range(30):
                date = base_date + timedelta(days=day)
                # Daily revenue (varies by day of week)
                is_weekend = date.weekday() >= 5
                revenue = 85000 if is_weekend else 72000
                revenue += (hash(str(date)) % 15000) - 7500  # Random variation

                transactions.append(FinancialTransaction(
                    user_id=demo_user.id,
                    date=date.replace(hour=20),
                    amount=revenue,
                    description=f"Daily revenue - {date.strftime('%A')}"
                ))

                # Random expenses
                if day % 3 == 0:  # Every 3 days
                    transactions.append(FinancialTransaction(
                        user_id=demo_user.id,
                        date=date.replace(hour=14),
                        amount=-8500,
                        description="Coffee beans supplier - 50kg premium blend"
                    ))

                if day % 7 == 0:  # Weekly
                    transactions.append(FinancialTransaction(
                        user_id=demo_user.id,
                        date=date.replace(hour=10),
                        amount=-25000,
                        description="Staff salaries - weekly"
                    ))
                    transactions.append(FinancialTransaction(
                        user_id=demo_user.id,
                        date=date.replace(hour=11),
                        amount=-12000,
                        description="Rent payment"
                    ))

                if day == 15:  # Mid-month
                    transactions.append(FinancialTransaction(
                        user_id=demo_user.id,
                        date=date.replace(hour=9),
                        amount=-18000,
                        description="Equipment maintenance"
                    ))

            for tx in transactions:
                session.add(tx)

            # Create cash flow prediction
            prediction_data = []
            current_balance = 450000  # Starting balance
            for i in range(7):
                date = datetime.now() + timedelta(days=i)
                is_weekend = date.weekday() >= 5
                daily_revenue = 85000 if is_weekend else 72000
                daily_expenses = -15000 if i % 3 == 0 else -5000
                current_balance += daily_revenue + daily_expenses

                prediction_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "balance": current_balance,
                    "revenue": daily_revenue,
                    "expenses": abs(daily_expenses)
                })

            prediction = CashFlowPrediction(
                user_id=demo_user.id,
                predicted_data=prediction_data,
                insights={
                    "risks": [
                        "Rent payment due in 3 days (₽12,000)",
                        "Coffee supplier invoice pending (₽8,500)"
                    ],
                    "recommendations": [
                        "Cash flow is stable for the next week",
                        "Consider negotiating payment terms with supplier",
                        "Weekend revenue is 18% higher - optimize staffing"
                    ],
                    "summary": "Healthy cash flow with ₽450K current balance. No immediate concerns."
                }
            )
            session.add(prediction)
            print(f"✅ Created {len(transactions)} financial transactions and cash flow prediction")
        else:
            print(f"✅ Financial data already exists ({len(existing_transactions)} transactions)")

        # 8. Create Legal Updates
        print("\n⚖️  Creating legal updates...")
        result = await session.execute(
            select(LegalUpdate).where(LegalUpdate.user_id == demo_user.id)
        )
        existing_legal = result.scalars().all()

        if not existing_legal:
            legal_updates = [
                {
                    "title": "НДС повышение с 20% до 22% с 2025 года",
                    "url": "https://www.garant.ru/news/vat-increase-2025",
                    "source": "Гарант.Ру",
                    "summary": "Правительство РФ утвердило повышение ставки НДС с 20% до 22% начиная с 1 января 2025 года. Изменения коснутся всех предприятий общей системы налогообложения.",
                    "impact_level": "High",
                    "category": "Tax Changes",
                    "details": {
                        "action_required": "Обновить ценообразование и бухгалтерское ПО",
                        "deadline": "2025-01-01",
                        "estimated_impact": "Увеличение налоговой нагрузки на 10%",
                        "recommendations": [
                            "Пересмотреть цены с учетом нового НДС",
                            "Проконсультироваться с бухгалтером",
                            "Обновить кассовое оборудование"
                        ]
                    }
                },
                {
                    "title": "Новые требования к онлайн-кассам с июля 2024",
                    "url": "https://www.nalog.gov.ru/rn77/news/kkt-requirements-2024",
                    "source": "ФНС России",
                    "summary": "С 1 июля 2024 года вступают в силу новые требования к онлайн-кассам. Все ККТ должны поддерживать формат фискальных данных ФФД 1.2.",
                    "impact_level": "High",
                    "category": "Equipment Compliance",
                    "details": {
                        "action_required": "Обновить прошивку ККТ до ФФД 1.2",
                        "deadline": "2024-07-01",
                        "estimated_impact": "Возможны штрафы до ₽30,000",
                        "recommendations": [
                            "Проверить версию ФФД на кассах",
                            "Обновить прошивку через ОФД",
                            "Протестировать новый формат чеков"
                        ]
                    }
                },
                {
                    "title": "Изменения в санитарных правилах для общепита",
                    "url": "https://rospotrebnadzor.ru/sanpin-catering-2024",
                    "source": "Роспотребнадзор",
                    "summary": "Обновлены СанПиН для предприятий общественного питания. Новые требования к хранению продуктов и обработке посуды.",
                    "impact_level": "Medium",
                    "category": "Health & Safety",
                    "details": {
                        "action_required": "Проверить соответствие новым СанПиН",
                        "deadline": "2024-09-01",
                        "estimated_impact": "Может потребоваться новое оборудование",
                        "recommendations": [
                            "Пройти проверку соответствия",
                            "Обучить персонал новым правилам",
                            "Обновить журналы учета"
                        ]
                    }
                },
                {
                    "title": "Маркировка молочной продукции обязательна",
                    "url": "https://честныйзнак.рф/milk-marking-2024",
                    "source": "Честный ЗНАК",
                    "summary": "С 1 сентября 2024 года вступает в силу обязательная маркировка молочной продукции системой 'Честный ЗНАК'.",
                    "impact_level": "Medium",
                    "category": "Product Marking",
                    "details": {
                        "action_required": "Настроить систему маркировки молочных продуктов",
                        "deadline": "2024-09-01",
                        "estimated_impact": "Дополнительные расходы на маркировку",
                        "recommendations": [
                            "Зарегистрироваться в системе Честный ЗНАК",
                            "Установить ПО для маркировки",
                            "Обучить персонал работе с системой"
                        ]
                    }
                }
            ]

            for legal_data in legal_updates:
                legal_update = LegalUpdate(
                    user_id=demo_user.id,
                    title=legal_data["title"],
                    url=legal_data["url"],
                    source=legal_data["source"],
                    summary=legal_data["summary"],
                    impact_level=legal_data["impact_level"],
                    category=legal_data["category"],
                    full_text_hash=hashlib.md5(legal_data["summary"].encode()).hexdigest(),
                    details=legal_data["details"]
                )
                session.add(legal_update)

            print(f"✅ Created {len(legal_updates)} legal updates")
        else:
            print(f"✅ Legal updates already exist ({len(existing_legal)} updates)")

        # 8b. Create Compliance Alerts
        print("\n⚠️  Creating compliance alerts...")
        result = await session.execute(
            select(ComplianceAlert).where(ComplianceAlert.user_id == demo_user.id)
        )
        existing_alerts = result.scalars().all()

        if not existing_alerts:
            # Get the legal updates we just created
            result = await session.execute(
                select(LegalUpdate).where(LegalUpdate.user_id == demo_user.id)
            )
            legal_updates_list = result.scalars().all()

            if legal_updates_list:
                compliance_alerts = []
                for legal_update in legal_updates_list[:3]:  # Create alerts for first 3 legal updates
                    due_date_map = {
                        "НДС повышение": datetime.now().date() + timedelta(days=45),
                        "онлайн-кассам": datetime.now().date() + timedelta(days=15),
                        "санитарных правилах": datetime.now().date() + timedelta(days=90),
                        "маркировка": datetime.now().date() + timedelta(days=120)
                    }

                    # Determine due date based on title
                    due_date = datetime.now().date() + timedelta(days=30)
                    for key, date in due_date_map.items():
                        if key in legal_update.title:
                            due_date = date
                            break

                    alert = ComplianceAlert(
                        user_id=demo_user.id,
                        legal_update_id=legal_update.id,
                        status='pending',
                        action_required=legal_update.details.get('action_required', 'Review legal update'),
                        due_date=due_date
                    )
                    compliance_alerts.append(alert)
                    session.add(alert)

                print(f"✅ Created {len(compliance_alerts)} compliance alerts")
            else:
                print("⚠️  No legal updates found to create compliance alerts")
        else:
            print(f"✅ Compliance alerts already exist ({len(existing_alerts)} alerts)")

        # 9. Create Competitors
        print("\n🏪 Creating competitor data...")
        result = await session.execute(
            select(Competitor).where(Competitor.user_id == demo_user.id)
        )
        existing_competitors = result.scalars().all()

        if not existing_competitors:
            competitors_data = [
                {
                    "name": "Coffee House на Арбате",
                    "website_url": "https://coffeehouse-arbat.ru",
                    "vk_group_id": "coffeehouse_arbat",
                    "telegram_channel": "@coffeehouse_moscow",
                    "actions": [
                        {
                            "action_type": "price_change",
                            "details": {
                                "product": "Капучино",
                                "old_price": 350,
                                "new_price": 385,
                                "change_percent": 10,
                                "detected_date": (datetime.now() - timedelta(days=3)).isoformat()
                            }
                        },
                        {
                            "action_type": "new_promotion",
                            "details": {
                                "title": "Счастливые часы 15:00-17:00",
                                "description": "Скидка 20% на весь ассортимент",
                                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                                "end_date": (datetime.now() + timedelta(days=23)).isoformat()
                            }
                        }
                    ]
                },
                {
                    "name": "Starbucks - ТРЦ Европейский",
                    "website_url": "https://starbucks.ru",
                    "vk_group_id": "starbucks_russia",
                    "telegram_channel": "@starbucks_russia",
                    "actions": [
                        {
                            "action_type": "new_product",
                            "details": {
                                "product": "Тыквенный латте",
                                "price": 450,
                                "category": "Сезонное предложение",
                                "launch_date": (datetime.now() - timedelta(days=5)).isoformat()
                            }
                        }
                    ]
                },
                {
                    "name": "Шоколадница - Новый Арбат",
                    "website_url": "https://shoko.ru",
                    "vk_group_id": "shokoladnitsa",
                    "telegram_channel": "@shoko_official",
                    "actions": [
                        {
                            "action_type": "price_change",
                            "details": {
                                "product": "Американо",
                                "old_price": 180,
                                "new_price": 200,
                                "change_percent": 11,
                                "detected_date": (datetime.now() - timedelta(days=10)).isoformat()
                            }
                        },
                        {
                            "action_type": "new_promotion",
                            "details": {
                                "title": "Бизнес-ланч",
                                "description": "Кофе + выпечка = 300₽",
                                "start_date": (datetime.now() - timedelta(days=14)).isoformat()
                            }
                        }
                    ]
                },
                {
                    "name": "Кофемания - Смоленская",
                    "website_url": "https://coffeemania.ru",
                    "vk_group_id": "coffeemania",
                    "telegram_channel": "@coffeemania_official",
                    "actions": [
                        {
                            "action_type": "new_product",
                            "details": {
                                "product": "Авторский десерт 'Тирамису делюкс'",
                                "price": 520,
                                "category": "Десерты",
                                "launch_date": (datetime.now() - timedelta(days=2)).isoformat()
                            }
                        }
                    ]
                }
            ]

            for comp_data in competitors_data:
                competitor = Competitor(
                    user_id=demo_user.id,
                    name=comp_data["name"],
                    website_url=comp_data["website_url"],
                    vk_group_id=comp_data["vk_group_id"],
                    telegram_channel=comp_data["telegram_channel"],
                    last_scanned=datetime.now() - timedelta(hours=2)
                )
                session.add(competitor)
                await session.flush()

                # Add competitor actions
                for action_data in comp_data["actions"]:
                    action = CompetitorAction(
                        competitor_id=competitor.id,
                        action_type=action_data["action_type"],
                        details=action_data["details"]
                    )
                    session.add(action)

            print(f"✅ Created {len(competitors_data)} competitors with actions")
        else:
            print(f"✅ Competitors already exist ({len(existing_competitors)} competitors)")

        # 10. Create Market Trends
        print("\n📈 Creating market trends...")
        result = await session.execute(
            select(MarketTrend).where(MarketTrend.user_id == demo_user.id)
        )
        existing_trends = result.scalars().all()

        if not existing_trends:
            trends_data = [
                {
                    "title": "Рост спроса на альтернативное молоко",
                    "insight_type": "Opportunity",
                    "observation": "Анализ показывает 45% рост запросов 'овсяное молоко' и 'соевое молоко' в вашем районе за последний месяц. Конкуренты еще не адаптировались.",
                    "recommendation_action": "Добавить 3-4 вида альтернативного молока (овсяное, соевое, миндальное) с наценкой +30₽ к напитку",
                    "recommendation_justification": "Целевая аудитория готова платить премию за здоровые опции. Ожидаемый прирост выручки: ₽15,000/месяц при 10% конверсии",
                    "strength_score": 0.87,
                    "category": "operational"
                },
                {
                    "title": "Конкуренты повышают цены - окно возможностей",
                    "insight_type": "Opportunity",
                    "observation": "Coffee House и Шоколадница подняли цены на 10-11%. Ваши цены теперь на 8% ниже среднерыночных.",
                    "recommendation_action": "Поднять цены на топ-5 позиций на 5-7%, сохраняя конкурентное преимущество",
                    "recommendation_justification": "Клиенты не заметят небольшое повышение на фоне конкурентов. Прогноз: +₽45,000/месяц выручки без потери трафика",
                    "strength_score": 0.92,
                    "category": "competitor"
                },
                {
                    "title": "Низкая конверсия в утренние часы",
                    "insight_type": "Efficiency Improvement",
                    "observation": "Утренний трафик (8-10 AM) высокий (80 чел/день), но средний чек ₽320 vs ₽500 днем. Люди берут только кофе без выпечки.",
                    "recommendation_action": "Запустить 'Завтрак-комбо': кофе + круассан = 450₽ (скидка 10%)",
                    "recommendation_justification": "Увеличит средний чек на 40% в утренние часы. Прогноз: +₽14,400/день дополнительной выручки",
                    "strength_score": 0.79,
                    "category": "financial"
                },
                {
                    "title": "НДС 22% с 2025 года - пересмотр цен критичен",
                    "insight_type": "Threat",
                    "observation": "Повышение НДС на 2 п.п. увеличит ваши налоговые обязательства на ₽22,500/месяц при текущей выручке",
                    "recommendation_action": "Провести аудит ценообразования и заложить НДС 22% в цены с декабря 2024",
                    "recommendation_justification": "Опережающее повышение цен до закона избежит шока для клиентов. Конкуренты сделают то же самое",
                    "strength_score": 0.95,
                    "category": "legal"
                },
                {
                    "title": "Сезонность: продажи холодных напитков +40% летом",
                    "insight_type": "Opportunity",
                    "observation": "Исторические данные показывают резкий рост спроса на айс-латте, фраппе и лимонады с мая по август",
                    "recommendation_action": "Увеличить закупки льда на 60%, добавить 2 новых холодных напитка к меню с апреля",
                    "recommendation_justification": "Прошлое лето было дефицит льда = потеря ₽180K выручки. Подготовка заранее максимизирует доход",
                    "strength_score": 0.88,
                    "category": "operational"
                }
            ]

            for trend_data in trends_data:
                trend = MarketTrend(
                    user_id=demo_user.id,
                    title=trend_data["title"],
                    insight_type=trend_data["insight_type"],
                    observation=trend_data["observation"],
                    recommendation_action=trend_data["recommendation_action"],
                    recommendation_justification=trend_data["recommendation_justification"],
                    strength_score=trend_data["strength_score"],
                    category=trend_data["category"]
                )
                session.add(trend)

            print(f"✅ Created {len(trends_data)} market trends")
        else:
            print(f"✅ Market trends already exist ({len(existing_trends)} trends)")

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
