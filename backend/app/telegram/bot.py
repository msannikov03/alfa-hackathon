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
import logging

logger = logging.getLogger(__name__)

# Conversation states for business setup
BUSINESS_NAME, BUSINESS_TYPE, LOCATION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    webapp_url = settings.TELEGRAM_WEBAPP_URL

    keyboard = [
        [InlineKeyboardButton("📊 Open Dashboard", web_app=WebAppInfo(url=webapp_url))],
        [
            InlineKeyboardButton("📈 Today's Stats", callback_data="stats"),
            InlineKeyboardButton("✅ Approvals", callback_data="approvals"),
        ],
        [
            InlineKeyboardButton("📋 Briefing", callback_data="briefing"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = """Добро пожаловать в Alfa Business Assistant! 🚀

Я ваш автономный AI-помощник для бизнеса.

Что я делаю:
• Работаю самостоятельно, пока вы спите
• Принимаю решения в рамках порогов
• Отправляю утренние брифинги в 6:00
• Запрашиваю одобрение только для важных решений

Команды:
/setup - Настроить бизнес-профиль
/briefing - Получить сегодняшний брифинг
/stats - Статистика за сегодня
/approve - Pending approvals
/help - Помощь

Или просто напишите мне, и я помогу! 💪"""

    # Create user if not exists
    await _get_or_create_user(update.effective_user)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get today's briefing"""
    user = update.effective_user
    db_user = await _get_or_create_user(user)

    await update.message.reply_text("Генерирую брифинг... ⏳")

    try:
        briefing_data = await briefing_agent.generate_daily_briefing(db_user.id)

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
    user = update.effective_user
    db_user = await _get_or_create_user(user)

    try:
        async with AsyncSessionLocal() as session:
            # Get today's actions
            today = datetime.now().date()
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == db_user.id)
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
    user = update.effective_user
    db_user = await _get_or_create_user(user)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == db_user.id)
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

    if callback_data == "help":
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
        await query.edit_message_text("Функция в разработке...")


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
    user = update.effective_user
    db_user = await _get_or_create_user(user)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == db_user.id)
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

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("briefing", briefing))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("approve", approvals))
    application.add_handler(CommandHandler("help", help_command))

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