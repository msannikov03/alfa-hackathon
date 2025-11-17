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
from app.services.competitor_service import competitor_service
from app.services.legal_service import legal_service
from app.services.finance_service import finance_service
from app.services.trends_service import trends_service
from app.database import AsyncSessionLocal
from app.models import User, AutonomousAction, BusinessContext, Competitor, LegalUpdate, ComplianceAlert, CashFlowPrediction
from sqlalchemy import select
from datetime import datetime
from passlib.context import CryptContext
import logging
import io
import tempfile
import os

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conversation states for business setup
BUSINESS_NAME, BUSINESS_TYPE, LOCATION = range(3)

# Conversation states for password setup
SET_PASSWORD = range(1)

# Conversation states for mode selection
SELECT_MODE = range(1)

# Conversation states for competitor addition
COMPETITOR_NAME, COMPETITOR_URL = range(2)


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

        welcome_message = """👋 Добро пожаловать в Alfa Business Assistant!

Я ваш автономный бизнес-ассистент на основе ИИ:
• Работаю независимо, пока вы спите
• Принимаю решения в рамках ваших порогов
• Отправляю утренние брифинги в 6:00
• Прошу одобрения только для важных решений

**Выберите режим работы:**

🎭 **Демо-режим** - Исследуйте с готовыми демо-данными
   • Идеально для тестирования и знакомства
   • Просмотр кофейни с реальными сценариями
   • Настройка не требуется!

🚀 **Рабочий режим** - Настройте свой бизнес-аккаунт
   • Настройте параметры вашего реального бизнеса
   • Начните получать реальные инсайты
   • Настройте всё под себя

Выберите режим, чтобы начать! 💪"""

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
        keyboard.append([InlineKeyboardButton("🚀 Переключить на рабочий режим", callback_data="mode_live")])
    else:
        keyboard.append([InlineKeyboardButton("🎭 Посмотреть демо-режим", callback_data="mode_demo")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    mode_text = "🎭 Демо-режим" if mode == "demo" else "🚀 Рабочий режим"

    welcome_message = f"""Добро пожаловать в Alfa Business Assistant! {mode_text}

Я ваш автономный бизнес-ассистент на основе ИИ.

**Что я делаю:**
• Работаю независимо, пока вы спите
• Принимаю решения в рамках порогов
• Отправляю утренние брифинги в 6:00
• Прошу одобрения только для важных решений

**Команды:**
/setup - Настроить профиль бизнеса
/briefing - Получить брифинг за сегодня
/stats - Статистика за сегодня
/approve - Ожидающие одобрения
/help - Показать помощь
/changemode - Переключить между Демо/Рабочим режимом

Или просто напишите мне, и я помогу! 💪"""

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
                    f"""✅ Демо-режим активирован!

Теперь вы исследуете демо-кофейню в Москве.

Демо включает:
• 📊 Реальные бизнес-метрики и KPI
• 🤖 Примеры автономных действий
• 📋 Готовые брифинги
• ✅ Сценарии ожидающих одобрений

Идеально для знакомства с возможностями ассистента!

Показываю главное меню..."""
                )
                await show_main_menu(update, context, mode)
            else:
                await query.edit_message_text(
                    "❌ Демо-данные не найдены. Пожалуйста, запустите скрипт инициализации:\n\n"
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
                """✅ Рабочий режим активирован!

Давайте настроим профиль вашего бизнеса для начала работы.

Используйте /setup для настройки бизнеса, или воспользуйтесь меню ниже."""
            )
        else:
            await query.edit_message_text(
                f"""✅ Рабочий режим активирован!

С возвращением! Ваш бизнес: {business_context.get('business_name', 'Ваш бизнес')}!

Показываю главное меню..."""
            )

        await show_main_menu(update, context, mode)


async def changemode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow users to change between demo and live mode"""
    current_mode = context.user_data.get('mode', 'none')

    keyboard = [
        [InlineKeyboardButton("🎭 Демо-режим", callback_data="mode_demo")],
        [InlineKeyboardButton("🚀 Рабочий режим", callback_data="mode_live")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Текущий режим: **{current_mode.title() if current_mode != 'none' else 'Не установлен'}**\n\n"
        "Выберите режим:",
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
    await message.reply_text("Генерирую брифинг... ⏳")

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

📊 Основные команды:
/start - Начать работу
/setup - Настроить бизнес-профиль
/setpassword - Установить пароль для доступа к дашборду
/briefing - Получить утренний брифинг
/stats - Статистика за сегодня
/approve - Проверить одобрения
/changemode - Переключить режим (Demo/Live)
/help - Эта справка

🎯 Мониторинг конкурентов:
/competitors - Список конкурентов
/addcompetitor - Добавить конкурента
/scancompetitors - Сканировать конкурентов

⚖️ Юридический мониторинг:
/legal - Последние обновления законов
/setcontext - Настроить бизнес-контекст
/compliance - Задачи по соблюдению

💰 Финансовая аналитика:
/forecast - Прогноз денежного потока
📎 Отправьте CSV - Загрузить транзакции

📈 Стратегический анализ:
/trends - Анализ трендов

Что я умею:
✅ Автономно выполнять задачи
📊 Генерировать ежедневные брифинги
💰 Принимать финансовые решения
🎯 Отслеживать конкурентов
⚖️ Мониторить законодательство
📈 Предсказывать финансы

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


# ============ COMPETITORS COMMANDS ============

async def competitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all competitors"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Competitor).where(Competitor.user_id == user_id)
            )
            competitors = result.scalars().all()

            if not competitors:
                response = "📊 У вас пока нет конкурентов для мониторинга.\n\n"
                response += "Используйте /addcompetitor чтобы добавить первого конкурента."
            else:
                response = f"📊 Ваши конкуренты ({len(competitors)}):\n\n"
                for comp in competitors:
                    response += f"• {comp.name}\n"
                    if comp.website_url:
                        response += f"  🌐 {comp.website_url}\n"
                    if comp.last_scanned:
                        response += f"  📅 Последнее сканирование: {comp.last_scanned.strftime('%d.%m.%Y %H:%M')}\n"
                    else:
                        response += "  ⏳ Еще не сканировался\n"
                    response += "\n"

                response += "\nИспользуйте /addcompetitor чтобы добавить еще\n"
                response += "Используйте /scancompetitors чтобы запустить сканирование"

            await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error listing competitors: {e}")
        await update.message.reply_text("❌ Ошибка при получении списка конкурентов.")


async def addcompetitor_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start competitor addition wizard"""
    await update.message.reply_text(
        "🎯 Добавление конкурента\n\n"
        "Как называется конкурент?\n\n"
        "Отправьте /cancel чтобы отменить."
    )
    return COMPETITOR_NAME


async def addcompetitor_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save competitor name and ask for URL"""
    context.user_data['competitor_name'] = update.message.text

    await update.message.reply_text(
        f"Отлично! Конкурент: {update.message.text}\n\n"
        "Теперь отправьте URL сайта конкурента:\n"
        "(например: https://competitor.com)"
    )
    return COMPETITOR_URL


async def addcompetitor_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save competitor URL and complete"""
    url = update.message.text
    competitor_name = context.user_data.get('competitor_name')

    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            competitor_data = {
                "name": competitor_name,
                "website_url": url
            }
            competitor = await competitor_service.create(session, user_id, competitor_data)

            await update.message.reply_text(
                f"✅ Конкурент добавлен!\n\n"
                f"🎯 Название: {competitor.name}\n"
                f"🌐 Сайт: {competitor.website_url}\n\n"
                f"Используйте /scancompetitors чтобы начать мониторинг."
            )
    except Exception as e:
        logger.error(f"Error adding competitor: {e}")
        await update.message.reply_text("❌ Ошибка при добавлении конкурента.")

    return ConversationHandler.END


async def addcompetitor_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel competitor addition"""
    await update.message.reply_text(
        "Добавление конкурента отменено. Используйте /addcompetitor чтобы попробовать снова."
    )
    return ConversationHandler.END


async def scancompetitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force scan all competitors"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    await update.message.reply_text("🔍 Запускаю сканирование конкурентов...")

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Competitor).where(Competitor.user_id == user_id)
            )
            competitors = result.scalars().all()

            if not competitors:
                await update.message.reply_text("У вас пока нет конкурентов для сканирования.")
                return

            scanned = 0
            failed = 0
            for comp in competitors:
                try:
                    scan_result = await competitor_service.scan_competitor(session, comp.id, user_id)
                    if not scan_result.get("success", False):
                        failed += 1
                        error_msg = scan_result.get('error', 'Неизвестная ошибка')
                        details = scan_result.get('details', [])
                        response_text = f"⚠️ {comp.name}: {error_msg}"
                        if details:
                            response_text += "\n\nПодробности:\n"
                            for detail in details:
                                response_text += f"• {detail}\n"
                        await update.message.reply_text(response_text)
                    else:
                        scanned += 1
                        actions_found = scan_result.get('found_actions', 0)
                        if actions_found > 0:
                            await update.message.reply_text(
                                f"✅ {comp.name}: найдено {actions_found} изменений!"
                            )
                        else:
                            await update.message.reply_text(
                                f"✅ {comp.name}: {scan_result.get('message', 'изменений не обнаружено')}"
                            )
                except Exception as e:
                    logger.error(f"Error scanning competitor {comp.name}: {e}")
                    failed += 1
                    await update.message.reply_text(
                        f"❌ {comp.name}: Критическая ошибка при сканировании"
                    )

            await update.message.reply_text(
                f"📊 Сканирование завершено!\n\n"
                f"✅ Успешно: {scanned}\n"
                f"❌ Ошибок: {failed}"
            )
    except Exception as e:
        logger.error(f"Error scanning competitors: {e}")
        await update.message.reply_text("❌ Ошибка при сканировании конкурентов.")


# ============ LEGAL COMMANDS ============

async def legal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View recent legal updates"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(LegalUpdate)
                .where(LegalUpdate.user_id == user_id)
                .order_by(LegalUpdate.detected_at.desc())
                .limit(5)
            )
            updates = result.scalars().all()

            if not updates:
                response = "⚖️ Релевантных юридических обновлений пока нет.\n\n"
                response += "Используйте /setcontext чтобы настроить бизнес-контекст для мониторинга."
            else:
                response = f"⚖️ Последние юридические обновления ({len(updates)}):\n\n"
                for upd in updates:
                    impact_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(upd.impact_level, "⚪")
                    response += f"{impact_emoji} {upd.title}\n"
                    response += f"📝 {upd.summary[:200]}...\n"
                    response += f"🔗 {upd.url}\n"
                    response += f"📅 {upd.detected_at.strftime('%d.%m.%Y')}\n\n"

            await update.message.reply_text(response, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error getting legal updates: {e}")
        await update.message.reply_text("❌ Ошибка при получении юридических обновлений.")


async def setcontext_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set business context for legal monitoring"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    # Check if user has a message
    if len(context.args) == 0:
        await update.message.reply_text(
            "⚖️ Установка бизнес-контекста для юридического мониторинга\n\n"
            "Опишите ваш бизнес в свободной форме:\n"
            "Например: 'Кофейня в Москве, работаем как ООО'\n\n"
            "Используйте: /setcontext [описание бизнеса]"
        )
        return

    description = " ".join(context.args)

    try:
        async with AsyncSessionLocal() as session:
            result = await legal_service.update_business_context(session, user_id, description)
            if result:
                await update.message.reply_text(
                    f"✅ Бизнес-контекст сохранен!\n\n"
                    f"📝 Описание: {description}\n\n"
                    f"Теперь система будет отслеживать релевантные законодательные изменения."
                )
            else:
                await update.message.reply_text(
                    "❌ Не удалось обработать описание. Попробуйте еще раз."
                )
    except Exception as e:
        logger.error(f"Error setting business context: {e}")
        await update.message.reply_text("❌ Ошибка при сохранении бизнес-контекста.")


async def compliance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View compliance alerts"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ComplianceAlert)
                .where(ComplianceAlert.user_id == user_id)
                .where(ComplianceAlert.status != 'completed')
                .order_by(ComplianceAlert.due_date.asc())
            )
            alerts = result.scalars().all()

            if not alerts:
                response = "✅ Нет активных задач по соблюдению законодательства!"
            else:
                response = f"⚠️ Активные задачи по соблюдению ({len(alerts)}):\n\n"
                for alert in alerts:
                    days_left = (alert.due_date - datetime.now().date()).days if alert.due_date else 0
                    urgency = "🔴" if days_left <= 3 else "🟡" if days_left <= 7 else "🟢"

                    response += f"{urgency} До {alert.due_date.strftime('%d.%m.%Y')} ({days_left} дней)\n"
                    response += f"📌 {alert.action_required[:200]}\n"
                    response += f"Статус: {alert.status}\n\n"

            await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting compliance alerts: {e}")
        await update.message.reply_text("❌ Ошибка при получении задач.")


# ============ FINANCE COMMANDS ============

async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View latest financial forecast"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CashFlowPrediction)
                .where(CashFlowPrediction.user_id == user_id)
                .order_by(CashFlowPrediction.created_at.desc())
            )
            forecast = result.scalar_one_or_none()

            if not forecast:
                response = "💰 У вас пока нет финансового прогноза.\n\n"
                response += "Отправьте CSV файл с транзакциями, и я создам прогноз на 7 дней!"
            else:
                response = f"💰 Прогноз денежного потока на 7 дней:\n"
                response += f"📅 Создан: {forecast.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

                # Show predicted data
                if forecast.predicted_data:
                    for day in forecast.predicted_data[:7]:
                        balance = day.get('balance', 0)
                        emoji = "✅" if balance > 0 else "⚠️" if balance > -10000 else "❌"
                        response += f"{emoji} {day.get('date', 'N/A')}: ₽{balance:,.0f}\n"

                # Show risks
                risks = forecast.insights.get('risks', [])
                if risks:
                    response += f"\n⚠️ Риски:\n"
                    for risk in risks[:3]:
                        response += f"• {risk.get('message', 'N/A')}\n"

                # Show recommendations
                recommendations = forecast.insights.get('recommendations', [])
                if recommendations:
                    response += f"\n💡 Рекомендации:\n"
                    for rec in recommendations[:3]:
                        response += f"• {rec.get('message', 'N/A')}\n"

            await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        await update.message.reply_text("❌ Ошибка при получении прогноза.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CSV file uploads for financial forecasting"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    document = update.message.document

    # Check if it's a CSV file
    if not document.file_name.endswith('.csv'):
        await update.message.reply_text(
            "⚠️ Пожалуйста, отправьте CSV файл с финансовыми транзакциями."
        )
        return

    await update.message.reply_text("📊 Обрабатываю CSV файл...")

    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()

        async with AsyncSessionLocal() as session:
            # Step 1: Get column mapping from LLM
            import csv
            content_str = file_content.decode('utf-8')
            reader = csv.reader(io.StringIO(content_str))
            headers = next(reader)
            rows_list = list(reader)
            sample_rows = rows_list[:min(3, len(rows_list))]

            await update.message.reply_text("🤖 AI анализирует структуру файла...")

            mapping = await finance_service.get_column_mapping_from_llm(headers, sample_rows)

            # Ask for current balance
            context.user_data['csv_file'] = bytes(file_content)
            context.user_data['csv_mapping'] = mapping

            await update.message.reply_text(
                f"✅ Файл обработан!\n\n"
                f"AI определил колонки:\n"
                f"📅 Дата: {mapping['date_column']}\n"
                f"📝 Описание: {mapping['description_column']}\n"
                f"💵 Сумма: {mapping['amount_logic']}\n\n"
                f"Теперь отправьте текущий баланс (число):"
            )

            # Set state to wait for balance
            context.user_data['waiting_for_balance'] = True

    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при обработке файла: {str(e)}\n\n"
            f"Убедитесь, что файл содержит корректные данные о транзакциях."
        )


async def handle_balance_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle balance input after CSV upload"""
    if not context.user_data.get('waiting_for_balance'):
        return

    try:
        current_balance = float(update.message.text.replace(',', '').replace(' ', ''))
    except ValueError:
        await update.message.reply_text("⚠️ Введите корректное число для баланса.")
        return

    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    await update.message.reply_text("📈 Создаю прогноз...")

    try:
        async with AsyncSessionLocal() as session:
            csv_file = context.user_data['csv_file']
            mapping = context.user_data['csv_mapping']

            # Store transactions
            await finance_service.store_transactions_from_csv(session, user_id, csv_file, mapping)

            # Create forecast
            forecast_result = await finance_service.create_forecast(session, user_id, current_balance)

            response = "✅ Прогноз создан!\n\n"
            response += "Используйте /forecast чтобы посмотреть детали."

            await update.message.reply_text(response)

            # Clean up
            context.user_data['waiting_for_balance'] = False
            context.user_data.pop('csv_file', None)
            context.user_data.pop('csv_mapping', None)

    except Exception as e:
        logger.error(f"Error creating forecast: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при создании прогноза: {str(e)}"
        )
        context.user_data['waiting_for_balance'] = False


# ============ TRENDS COMMAND ============

async def trends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View strategic trends"""
    user_id = context.user_data.get('user_id')
    if not user_id:
        user = update.effective_user
        db_user = await _get_or_create_user(user)
        user_id = db_user.id

    await update.message.reply_text("📊 Анализирую стратегические тренды...")

    try:
        async with AsyncSessionLocal() as session:
            trends = await trends_service.identify_trends(session, user_id)

            if not trends:
                response = "📈 Пока недостаточно данных для анализа трендов.\n\n"
                response += "Добавьте данные:\n"
                response += "• Конкуренты: /addcompetitor\n"
                response += "• Финансы: отправьте CSV\n"
                response += "• Юридический контекст: /setcontext"
            else:
                response = f"📈 Стратегические тренды ({len(trends)}):\n\n"
                for trend in trends[:5]:
                    type_emoji = {
                        "Opportunity": "✨",
                        "Threat": "⚠️",
                        "Efficiency Improvement": "⚡"
                    }.get(trend.get('insight_type'), "📊")

                    response += f"{type_emoji} {trend.get('title', 'N/A')}\n"
                    response += f"📝 {trend.get('observation', 'N/A')}\n"

                    recommendations = trend.get('recommendation', {})
                    if isinstance(recommendations, dict) and 'actions' in recommendations:
                        response += f"💡 Действия:\n"
                        for action in recommendations['actions'][:2]:
                            response += f"  • {action}\n"

                    response += f"🎯 Важность: {trend.get('strength_score', 0)}/10\n\n"

            await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        await update.message.reply_text("❌ Ошибка при анализе трендов.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    # First check if waiting for balance input
    if context.user_data.get('waiting_for_balance'):
        await handle_balance_input(update, context)
        return

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

    # Add competitor addition conversation handler
    addcompetitor_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addcompetitor", addcompetitor_start)],
        states={
            COMPETITOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, addcompetitor_name)],
            COMPETITOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, addcompetitor_url)],
        },
        fallbacks=[CommandHandler("cancel", addcompetitor_cancel)],
    )
    application.add_handler(addcompetitor_conv_handler)

    # Add command handlers - Core
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("briefing", briefing))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("approve", approvals))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("changemode", changemode_command))

    # Add command handlers - Competitors
    application.add_handler(CommandHandler("competitors", competitors_command))
    application.add_handler(CommandHandler("scancompetitors", scancompetitors_command))

    # Add command handlers - Legal
    application.add_handler(CommandHandler("legal", legal_command))
    application.add_handler(CommandHandler("setcontext", setcontext_command))
    application.add_handler(CommandHandler("compliance", compliance_command))

    # Add command handlers - Finance
    application.add_handler(CommandHandler("forecast", forecast_command))

    # Add command handlers - Trends
    application.add_handler(CommandHandler("trends", trends_command))

    # Add document handler for CSV uploads
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Add callback query handler for buttons (must be after conversation handlers)
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot and begin polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info("Telegram bot started with Phase 2 features and polling for updates")