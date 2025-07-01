import uvicorn
import os
import asyncio
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import database  # Убедись, что у тебя есть файл database.py

# === Настройки из переменных окружения ===
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Приветственный текст ===
def load_welcome_text(username):
    try:
        with open('welcome.html', 'r', encoding='utf-8') as file:
            text = file.read()
            return text.replace('@{username}', f'@{username}')
    except FileNotFoundError:
        return f"👋 Привет, @{username}!\n\nНе удалось загрузить приветственный текст."


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start
    Приветствие из файла welcome.html + инлайн-кнопки + клавиатура
    """
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "unknown"

    existing_user = database.get_user(user_id)

    if not existing_user:
        referred_by = context.args[0] if context.args else None

        database.add_user(user_id, username, referred_by)

        if referred_by:
            try:
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"🎉 По вашей ссылке зарегистрировался новый пользователь — @{username}!"
                )
            except Exception as e:
                print(f"[Ошибка] Не удалось уведомить реферера {referred_by}: {e}")

    # === Загружаем приветственный текст ===
    welcome_text = load_welcome_text(username)

    # === Инлайн-кнопки под текстом ===
    keyboard = [
        [
            InlineKeyboardButton("📹 ПЕРЕЙТИ ->", url="https://sovkomprohalva.ru"), 
            InlineKeyboardButton("💬 НАШ Чат", url="https://t.me/+Yaq7IZdTEWA3OWIy") 
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # === Отправляем сообщение с форматированием и кнопками ===
    try:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        print(f"[Ошибка] Не удалось отправить HTML-сообщение: {e}")
        await update.message.reply_text(
            f"👋 Привет, @{username}!\n\n"
            "Мы подготовили для вас подробную информацию. "
            "Пожалуйста, посмотрите видео и присоединитесь к чату.",
            reply_markup=reply_markup
        )

    # === Клавиатура внизу (разная для админа и обычных пользователей) ===
    current_admin_id = ADMIN_ID

    if user_id == current_admin_id:
        menu_keyboard = [
            [KeyboardButton("🔗 Реферальная ссылка"), KeyboardButton("📊 Статистика")],
            [KeyboardButton("🏆 Топ рефереров"), KeyboardButton("🌐 ПЕРЕЙТИ")]
        ]
    else:
        menu_keyboard = [
            [KeyboardButton("🔗 Реферальная ссылка"), KeyboardButton("📊 Статистика")],
            [KeyboardButton("🌐 ПЕРЕЙТИ")]
        ]

    menu_reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    # === Сообщение с меню ===
    await update.message.reply_text(
        "Выберите действие ниже или воспользуйтесь меню:",
        reply_markup=menu_reply_markup
    )


# === Команда /mylink ===
async def my_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет пользователю его уникальную реферальную ссылку
    """
    user = update.effective_user
    user_id = user.id
    ref_link = f"https://t.me/testymynebot_bot?start={user_id}"

    await update.message.reply_text(
        f"🔗 Вот ваша реферальная ссылка:\n"
        f"<code>{ref_link}</code>\n\n"
        f"Поделись реферальной ссылкой с друзьями и привлекай больше кандидатов в свою команду!",
        parse_mode='HTML'
    )


# === Команда /stats === 
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает статистику пользователя: ID и количество приглашённых
    """
    user = update.effective_user
    user_id = str(user.id)

    referrals_count = database.count_referrals(user_id)

    message = (
        f"📊 <b>Статистика для @{user.username or 'пользователя'}:</b>\n\n"
        f"👤 Ваш ID: <code>{user_id}</code>\n"
        f"👥 Приглашено пользователей: <b>{referrals_count}</b>\n\n"
        f"🔗 Используйте /mylink, чтобы приглашать новых пользователей!"
    )

    await update.message.reply_text(message, parse_mode='HTML')


# === Команда /top ===
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает топ 10 пользователей по количеству приглашённых
    """
    top_referrers = database.get_top_referrers(limit=10)

    if not top_referrers:
        await update.message.reply_text("😔 Ещё никто не приглашал пользователей.")
        return

    message = "🏆 <b>ТОП 10 АКТИВНЫХ РЕФЕРЕРОВ:</b>\n\n"

    for idx, (referrer_id, count) in enumerate(top_referrers, start=1):
        word = "пользователей"
        if count % 10 == 1 and count // 10 != 1:
            word = "пользователь"
        elif 2 <= count % 10 <= 4 and count // 10 != 1:
            word = "пользователя"

        message += f"{idx}. 🧑‍💻 ID: <code>{referrer_id}</code> — {count} {word}\n"

    await update.message.reply_text(message, parse_mode='HTML')


# === Команда /broadcast — только для администратора ===
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Рассылает сообщение всем пользователям бота
    Поддерживает HTML-разметку и инлайн-кнопки
    """
    user = update.effective_user
    user_id = str(user.id)

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав на выполнение этой команды.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Используйте: /broadcast имя_файла\n"
            "Например: /broadcast welcome.html"
        )
        return

    filename = context.args[0]

    if not os.path.exists(filename):
        await update.message.reply_text(f"❌ Файл '{filename}' не найден.")
        return

    try:
        # Читаем содержимое файла
        with open(filename, 'r', encoding='utf-8') as file:
            message_text = file.read()

        # === КНОПКИ В РАССЫЛКЕ ===
        keyboard = [
            [
                InlineKeyboardButton("📹 ПЕРЕЙТИ ->", url="https://sovkomprohalva.ru"), 
                InlineKeyboardButton("💬 Наш чат", url="https://t.me/+Yaq7IZdTEWA3OWIy") 
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        users = database.get_all_users()
        success = 0
        failed = 0

        for db_user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=db_user_id,
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                success += 1
            except Exception as e:
                print(f"[Ошибка] Не удалось отправить сообщение {db_user_id}: {e}")
                failed += 1
            await asyncio.sleep(0.05)

        await update.message.reply_text(
            f"📬 Рассылка завершена!\n✅ Успешно: {success}\n❌ Ошибок: {failed}"
        )

    except Exception as e:
        await update.message.reply_text(f"🚫 Ошибка при чтении файла: {e}")


# === Обработчик нажатий на кнопки ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатия на кнопки клавиатуры
    Перенаправляет на соответствующие функции
    """
    text = update.message.text

    if text == "🔗 Реферальная ссылка":
        await my_link(update, context)
    elif text == "📊 Статистика":
        await stats(update, context)
    elif text == "🏆 Топ рефереров":
        await top(update, context)
    elif text == "🌐 ПЕРЕЙТИ":
        await update.message.reply_text("🚀 Открываем веб-приложение...", reply_markup=None)
        # Здесь можно добавить WebAppInfo, когда будет готово


# === Основная асинхронная функция запуска бота через Webhook ===
# === Основная асинхронная функция запуска бота через Webhook ===
async def main():
    """
    Запуск бота через webhook
    """

    # Инициализируем базу данных
    database.init_db()

    # Создаём приложение
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Устанавливаем команды в меню Telegram
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("mylink", "Получить реферальную ссылку"),
        BotCommand("stats", "Посмотреть статистику"),
        BotCommand("top", "Рейтинг активных рефереров"),
        BotCommand("broadcast", "Рассылка всем (только админ)")
    ]
    await app.bot.set_my_commands(commands)

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mylink", my_link))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Добавляем обработчик кнопок
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    # === Настраиваем и запускаем webhook ===
    webhook_url = os.getenv("WEBHOOK_URL", "https://sovkomprohalva-bot.onrender.com ")
    port = int(os.getenv("PORT", "8000"))

    print(f"🌐 Устанавливаю webhook: {webhook_url}/webhook")

    await app.bot.set_webhook(f"{webhook_url}/webhook")

    # Запускаем бота через webhook
    await app.run_webhook(
        listen='0.0.0.0',           # Слушаем все соединения
        port=port,                  # Порт из переменной окружения
        url_path="",                # Путь, можно оставить пустым
        webhook_url=f"{webhook_url}/webhook"  # URL для Telegram
    )
    print("✅ Бот успешно запущен через Webhook")


# === Точка входа для Render.com ===
if __name__ == '__main__':
    asyncio.run(main())
