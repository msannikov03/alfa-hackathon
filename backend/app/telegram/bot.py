from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from app.config import settings
from app.services.llm_service import llm_service
from app.agents.briefing_agent import briefing_agent
from app.database import AsyncSessionLocal
from app.models import User, AutonomousAction, BusinessContext
from sqlalchemy import select
from datetime import datetime
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conversation states for business setup
BUSINESS_NAME, BUSINESS_TYPE, LOCATION = range(3)

# Conversation states for password setup
SET_PASSWORD = range(1)

# Conversation states for mode selection
SELECT_MODE = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler with mode selection"""
    # Check if user already has a mode set
    user_mode = context.user_data.get('mode')

    if not user_mode:
        # First time - ask user to select mode
        keyboard = [
            [InlineKeyboardButton("🎭 Demo Mode - Try with sample data", callback_data="mode_demo")],
            [InlineKeyboardButton("🚀 Live Mode - Create your account", callback_data="mode_live")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = """👋 Welcome to Alfa Business Assistant!

I'm your autonomous AI business assistant that:
• Works independently while you sleep
• Makes decisions within your thresholds
• Sends morning briefings at 6:00 AM
• Only asks approval for important decisions

**Please choose your mode:**

🎭 **Demo Mode** - Explore with pre-loaded sample business data
   • Perfect for testing and seeing what I can do
   • View a coffee shop business with real scenarios
   • No setup required!

🚀 **Live Mode** - Set up your own business account
   • Configure your actual business
   • Start getting real insights
   • Customize everything

Choose a mode to get started! 💪"""

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        # User already has mode - show main menu
        await show_main_menu(update, context, user_mode)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    """Show main menu based on user's mode"""
    # Build keyboard based on webapp availability
    keyboard = []

    # Only add webapp button if URL is configured and not localhost (i.e., deployed)
    webapp_url = settings.TELEGRAM_WEBAPP_URL
    if webapp_url and "localhost" not in webapp_url:
        keyboard.append([InlineKeyboardButton("📊 Open Dashboard", web_app=WebAppInfo(url=webapp_url))])

    # Add main action buttons
    keyboard.extend([
        [
            InlineKeyboardButton("📈 Today's Stats", callback_data="stats"),
            InlineKeyboardButton("✅ Approvals", callback_data="approvals"),
        ],
        [
            InlineKeyboardButton("📋 Briefing", callback_data="briefing"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ])

    # Add mode switch option
    if mode == "demo":
        keyboard.append([InlineKeyboardButton("🚀 Switch to Live Mode", callback_data="mode_live")])
    else:
        keyboard.append([InlineKeyboardButton("🎭 View Demo Mode", callback_data="mode_demo")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    mode_text = "🎭 Demo Mode" if mode == "demo" else "🚀 Live Mode"

    welcome_message = f"""Welcome to Alfa Business Assistant! {mode_text}

I'm your autonomous AI business assistant.

**What I do:**
• Work independently while you sleep
• Make decisions within thresholds
• Send morning briefings at 6:00 AM
• Request approval only for important decisions

**Commands:**
/setup - Configure business profile
/briefing - Get today's briefing
/stats - Today's statistics
/approve - Pending approvals
/help - Show help
/changemode - Switch between Demo/Live mode

Or just message me, and I'll help! 💪"""

    # Use appropriate method based on whether this is a callback or message
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def handle_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode selection (demo/live)"""
    query = update.callback_query
    await query.answer()

    mode = query.data.replace("mode_", "")
    context.user_data['mode'] = mode

    if mode == "demo":
        # Link user to demo account
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == "demo_admin")
            )
            demo_user = result.scalar_one_or_none()

            if demo_user:
                context.user_data['user_id'] = demo_user.id
                await query.edit_message_text(
                    f"""✅ Demo Mode Activated!

You're now exploring a sample coffee shop business in Moscow.

This demo includes:
• 📊 Real business metrics and KPIs
• 🤖 Sample autonomous actions
• 📋 Pre-generated briefings
• ✅ Pending approval scenarios

Perfect for seeing what the assistant can do!

Let me show you the main menu..."""
                )
                await show_main_menu(update, context, mode)
            else:
                await query.edit_message_text(
                    "❌ Demo data not found. Please run the seed script first:\n\n"
                    "`docker exec alfa_backend python seed_demo_data.py`"
                )
    else:  # live mode
        # Create or get user's own account
        telegram_user = update.effective_user
        db_user = await _get_or_create_user(telegram_user)
        context.user_data['user_id'] = db_user.id

        # Check if user has business context
        business_context = await _get_business_context(db_user.id)

        if not business_context:
            await query.edit_message_text(
                """✅ Live Mode Activated!

Let's set up your business profile to get started.

Use /setup to configure your business, or use the menu below."""
            )
        else:
            await query.edit_message_text(
                f"""✅ Live Mode Activated!

Welcome back to your business: {business_context.get('business_name', 'Your Business')}!

Let me show you the main menu..."""
            )

        await show_main_menu(update, context, mode)


async def changemode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow users to change between demo and live mode"""
    current_mode = context.user_data.get('mode', 'none')

    keyboard = [
        [InlineKeyboardButton("🎭 Demo Mode", callback_data="mode_demo")],
        [InlineKeyboardButton("🚀 Live Mode", callback_data="mode_live")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Current mode: **{current_mode.title() if current_mode != 'none' else 'Not Set'}**\n\n"
        "Choose a mode:",
        reply_markup=reply_markup
    )


async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get today's briefing"""
    # Get user ID from context (demo mode) or create user (live mode)
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    message = update.callback_query.message if update.callback_query else update.message
    await message.reply_text("Generating briefing... ⏳")

    try:
        briefing_data = await briefing_agent.generate_daily_briefing(user_id)

        response = f"""📋 Брифинг на {datetime.now().strftime('%d.%m.%Y')}

{briefing_data.get('summary', 'Нет данных')}

Действий выполнено: {len(briefing_data.get('completed_actions', []))}
Время сэкономлено: ~{briefing_data.get('metrics', {}).get('time_saved_hours', 0)} часов"""

        keyboard = [
            [InlineKeyboardButton("📊 Подробная статистика", callback_data="stats")],
            [InlineKeyboardButton("✅ Проверить одобрения", callback_data="approvals")],
        ]

        await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error getting briefing: {e}")
        await update.message.reply_text("Ошибка при генерации брифинга. Попробуйте позже.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's statistics"""
    # Get user ID from context (demo mode) or create user (live mode)
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            # Get today's actions
            today = datetime.now().date()
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == user_id)
                .where(AutonomousAction.executed_at >= today)
            )
            actions = result.scalars().all()

            # Calculate stats
            total_actions = len(actions)
            approved = sum(1 for a in actions if a.was_approved is True)
            pending = sum(1 for a in actions if a.required_approval and a.was_approved is None)

            response = f"""📈 Статистика за сегодня

Всего действий: {total_actions}
Одобрено: {approved}
Ожидает одобрения: {pending}

Время сэкономлено: ~{round(total_actions * 0.25, 1)} часов
Решений автоматизировано: {round((total_actions - pending) / max(total_actions, 1) * 100)}%"""

            keyboard = [
                [InlineKeyboardButton("📋 Показать брифинг", callback_data="briefing")],
                [InlineKeyboardButton("✅ Одобрения", callback_data="approvals")],
            ]

            message = update.callback_query.message if update.callback_query else update.message
            await message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        message = update.callback_query.message if update.callback_query else update.message
        await message.reply_text("Ошибка при получении статистики.")


async def approvals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending approvals"""
    # Get user ID from context (demo mode) or create user (live mode)
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == user_id)
                .where(AutonomousAction.required_approval == True)
                .where(AutonomousAction.was_approved == None)
                .order_by(AutonomousAction.executed_at.desc())
            )
            pending_actions = result.scalars().all()

            if not pending_actions:
                response = "✅ Нет ожидающих одобрений!"
                keyboard = [[InlineKeyboardButton("📈 Статистика", callback_data="stats")]]
            else:
                response = f"⏳ Ожидает одобрения: {len(pending_actions)}\n\n"
                keyboard = []

                for action in pending_actions[:5]:  # Show first 5
                    response += f"• {action.description}\n"
                    response += f"  Сумма: ₽{action.impact_amount:,.0f}\n\n"

                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                f"✅ Одобрить #{action.id}", callback_data=f"approve_{action.id}"
                            ),
                            InlineKeyboardButton(
                                f"❌ Отклонить #{action.id}", callback_data=f"decline_{action.id}"
                            ),
                        ]
                    )

                keyboard.append([InlineKeyboardButton("✅ Одобрить все", callback_data="approve_all")])

            message = update.callback_query.message if update.callback_query else update.message
            await message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error getting approvals: {e}")
        message = update.callback_query.message if update.callback_query else update.message
        await message.reply_text("Ошибка при получении одобрений.")


async def setup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start business setup wizard"""
    await update.message.reply_text(
        "🏢 Давайте настроим ваш бизнес-профиль!\n\n"
        "Как называется ваш бизнес?\n\n"
        "Отправьте /cancel чтобы отменить."
    )
    return BUSINESS_NAME


async def setup_business_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save business name and ask for type"""
    context.user_data['business_name'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("☕ Кафе/Ресторан", callback_data="setup_type_cafe")],
        [InlineKeyboardButton("💇 Салон красоты", callback_data="setup_type_salon")],
        [InlineKeyboardButton("🛒 Розничная торговля", callback_data="setup_type_retail")],
        [InlineKeyboardButton("🏪 Другое", callback_data="setup_type_other")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Отлично! Бизнес: {update.message.text}\n\n"
        "Выберите тип бизнеса:",
        reply_markup=reply_markup
    )
    return BUSINESS_TYPE


async def setup_business_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save business type and ask for location"""
    query = update.callback_query
    await query.answer()

    type_map = {
        "setup_type_cafe": "coffee_shop",
        "setup_type_salon": "salon",
        "setup_type_retail": "retail",
        "setup_type_other": "other"
    }

    business_type = type_map.get(query.data, "other")
    context.user_data['business_type'] = business_type

    await query.edit_message_text(
        "📍 В каком городе находится ваш бизнес?\n\n"
        "Например: Москва, Санкт-Петербург"
    )
    return LOCATION


async def setup_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save location and complete setup"""
    location = update.message.text
    context.user_data['location'] = location

    # Get or create user
    telegram_user = update.effective_user
    db_user = await _get_or_create_user(telegram_user)

    # Create or update business context
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BusinessContext).where(BusinessContext.user_id == db_user.id)
            )
            business_context = result.scalar_one_or_none()

            if business_context:
                # Update existing
                business_context.business_name = context.user_data['business_name']
                business_context.business_type = context.user_data['business_type']
                business_context.location = location
            else:
                # Create new
                business_context = BusinessContext(
                    user_id=db_user.id,
                    business_name=context.user_data['business_name'],
                    business_type=context.user_data['business_type'],
                    location=location,
                    operating_hours={"open": "09:00", "close": "18:00"},
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
                session.add(business_context)

            await session.commit()

        await update.message.reply_text(
            f"✅ Профиль настроен!\n\n"
            f"🏢 Бизнес: {context.user_data['business_name']}\n"
            f"📂 Тип: {context.user_data['business_type']}\n"
            f"📍 Город: {location}\n\n"
            f"Теперь я могу помогать вам более эффективно!\n\n"
            f"Используйте /briefing для получения брифинга или просто напишите мне."
        )

    except Exception as e:
        logger.error(f"Error saving business context: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при сохранении. Попробуйте позже."
        )

    return ConversationHandler.END


async def setup_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel setup"""
    await update.message.reply_text(
        "Настройка отменена. Используйте /setup чтобы начать заново."
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = """❓ Справка по Alfa Business Assistant

Основные команды:
/start - Начать работу
/setup - Настроить бизнес-профиль
/setpassword - Установить пароль для доступа к дашборду
/briefing - Получить утренний брифинг
/stats - Статистика за сегодня
/approve - Проверить одобрения
/help - Эта справка

Что я умею:
✅ Автономно выполнять задачи
📊 Генерировать ежедневные брифинги
💰 Принимать финансовые решения в пределах порогов
📈 Анализировать паттерны и учиться
🔔 Отправлять уведомления о важных событиях

Пороги решений:
• До ₽10,000 - автоматически
• ₽10,000-₽50,000 - требуется одобрение
• Более ₽50,000 - обязательная эскалация

Просто напишите мне, и я помогу! 💪"""

    await update.message.reply_text(help_text)


async def setpassword_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start password setup wizard"""
    await update.message.reply_text(
        "🔐 Установка пароля для доступа к дашборду\n\n"
        "Введите желаемый пароль (минимум 6 символов):\n\n"
        "Отправьте /cancel чтобы отменить."
    )
    return SET_PASSWORD


async def setpassword_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the password"""
    password = update.message.text

    # Delete the message with password for security
    try:
        await update.message.delete()
    except:
        pass

    if len(password) < 6:
        await update.message.reply_text(
            "❌ Пароль должен быть минимум 6 символов. Попробуйте еще раз."
        )
        return SET_PASSWORD

    telegram_user = update.effective_user
    db_user = await _get_or_create_user(telegram_user)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == db_user.id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Set username if not set
                if not user.username:
                    user.username = telegram_user.username or f"user_{telegram_user.id}"

                # Hash and save password
                user.hashed_password = pwd_context.hash(password)
                await session.commit()

                await update.message.reply_text(
                    f"✅ Пароль установлен!\n\n"
                    f"👤 Ваш логин: {user.username}\n\n"
                    f"Теперь вы можете войти в дашборд на http://localhost:3000/dashboard\n"
                    f"используя этот логин и установленный пароль."
                )
            else:
                await update.message.reply_text("❌ Ошибка при сохранении пароля.")

    except Exception as e:
        logger.error(f"Error setting password: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

    return ConversationHandler.END


async def setpassword_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel password setup"""
    await update.message.reply_text(
        "Установка пароля отменена. Используйте /setpassword чтобы начать заново."
    )
    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    # Check if it's a group chat and bot is mentioned
    if update.message.chat.type in ["group", "supergroup"]:
        # Only respond to mentions in groups
        if not update.message.text or f"@{context.bot.username}" not in update.message.text:
            return

    user = update.effective_user
    db_user = await _get_or_create_user(user)
    user_message = update.message.text

    # Get business context
    business_context = await _get_business_context(db_user.id)

    # Process with LLM
    try:
        result = await llm_service.process_with_context(
            message=user_message, business_context=business_context
        )

        response = result["response"]

        # If action requires approval, add buttons
        if result["requires_approval"]:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Одобрить", callback_data="approve_action"),
                    InlineKeyboardButton("❌ Отклонить", callback_data="decline_action"),
                ],
                [InlineKeyboardButton("📋 Подробнее", callback_data="action_details")],
            ]
            await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте еще раз.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    # Handle mode selection
    if callback_data.startswith("mode_"):
        await handle_mode_selection(update, context)
    elif callback_data == "help":
        await help_command(update, context)
    elif callback_data == "stats":
        await stats(update, context)
    elif callback_data == "approvals":
        await approvals(update, context)
    elif callback_data == "briefing":
        await briefing(update, context)
    elif callback_data.startswith("approve_"):
        action_id = callback_data.split("_")[1]
        if action_id == "all":
            await approve_all_actions(update, context)
        else:
            await approve_action(update, context, int(action_id))
    elif callback_data.startswith("decline_"):
        action_id = callback_data.split("_")[1]
        await decline_action(update, context, int(action_id))
    else:
        await query.edit_message_text("Function under development...")


async def approve_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_id: int):
    """Approve a specific action"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction).where(AutonomousAction.id == action_id)
            )
            action = result.scalar_one_or_none()

            if action:
                action.was_approved = True
                await session.commit()
                await update.callback_query.edit_message_text(
                    f"✅ Действие #{action_id} одобрено!\n\n{action.description}"
                )
            else:
                await update.callback_query.edit_message_text("❌ Действие не найдено.")
    except Exception as e:
        logger.error(f"Error approving action: {e}")
        await update.callback_query.edit_message_text("Ошибка при одобрении.")


async def decline_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_id: int):
    """Decline a specific action"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction).where(AutonomousAction.id == action_id)
            )
            action = result.scalar_one_or_none()

            if action:
                action.was_approved = False
                await session.commit()
                await update.callback_query.edit_message_text(
                    f"❌ Действие #{action_id} отклонено.\n\n{action.description}"
                )
            else:
                await update.callback_query.edit_message_text("❌ Действие не найдено.")
    except Exception as e:
        logger.error(f"Error declining action: {e}")
        await update.callback_query.edit_message_text("Ошибка при отклонении.")


async def approve_all_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve all pending actions"""
    # Get user ID from context (demo mode) or create user (live mode)
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == user_id)
                .where(AutonomousAction.required_approval == True)
                .where(AutonomousAction.was_approved == None)
            )
            actions = result.scalars().all()

            for action in actions:
                action.was_approved = True

            await session.commit()

            await update.callback_query.edit_message_text(
                f"✅ Одобрено {len(actions)} действий!"
            )
    except Exception as e:
        logger.error(f"Error approving all: {e}")
        await update.callback_query.edit_message_text("Ошибка при одобрении.")


async def _get_or_create_user(telegram_user) -> User:
    """Get or create user in database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == str(telegram_user.id))
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=str(telegram_user.id),
                username=telegram_user.username,
                full_name=telegram_user.full_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user


async def _get_business_context(user_id: int) -> dict:
    """Get business context for user"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BusinessContext).where(BusinessContext.user_id == user_id)
            )
            context = result.scalar_one_or_none()

            if context:
                return {
                    "business_name": context.business_name,
                    "business_type": context.business_type,
                    "location": context.location,
                    "operating_hours": context.operating_hours,
                    "decision_thresholds": context.decision_thresholds,
                }
    except Exception as e:
        logger.error(f"Error getting business context: {e}")

    return {}


async def setup_telegram_bot():
    """Initialize Telegram bot"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("No Telegram bot token provided")
        return

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add business setup conversation handler
    setup_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setup", setup_start)],
        states={
            BUSINESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_business_name)],
            BUSINESS_TYPE: [CallbackQueryHandler(setup_business_type, pattern="^setup_type_")],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_location)],
        },
        fallbacks=[CommandHandler("cancel", setup_cancel)],
    )
    application.add_handler(setup_conv_handler)

    # Add password setup conversation handler
    password_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setpassword", setpassword_start)],
        states={
            SET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, setpassword_save)],
        },
        fallbacks=[CommandHandler("cancel", setpassword_cancel)],
    )
    application.add_handler(password_conv_handler)

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("briefing", briefing))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("approve", approvals))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("changemode", changemode_command))

    # Add callback query handler for buttons (must be after setup handler)
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot and begin polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info("Telegram bot started with enhanced features and polling for updates")