import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ти — AI-помічник у Telegram-боті студента.

Відповідай українською мовою, якщо користувач не попросив іншу мову.
Відповіді мають бути зрозумілими, корисними та лаконічними.

Формат відповіді:
- використовуй звичайний текст;
- не використовуй Markdown;
- не використовуй заголовки з символами #;
- не використовуй горизонтальні лінії ---;
- не використовуй таблиці;
- не використовуй складне форматування;
- для переліків використовуй прості маркери • або нумерацію;
- не додавай зайві вступи або підсумки, якщо вони не потрібні;
- структуруй довгі відповіді за допомогою коротких абзаців і простих списків.

Якщо користувач ставить технічне питання, пояснюй матеріал послідовно і зрозуміло.
"""

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Студент", callback_data="student")],
        [InlineKeyboardButton("IT-технології", callback_data="technologies")],
        [InlineKeyboardButton("Контакти", callback_data="contacts")],
        [InlineKeyboardButton("Prompt AI", callback_data="prompt_ai")],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_for_ai"] = False

    await update.message.reply_text(
        "Вітаю! Я Telegram-бот для лабораторної роботи №3.\n\n"
        "Оберіть потрібний пункт меню:",
        reply_markup=get_main_menu(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    if query.data == "student":
        context.user_data["waiting_for_ai"] = False

        await query.edit_message_text(
            "Студентка: Войтюк А.С.\n"
            "Група: ІП-32",
            reply_markup=get_main_menu(),
        )

    elif query.data == "technologies":
        context.user_data["waiting_for_ai"] = False

        await query.edit_message_text(
            "IT-технології:\n\n"
            "• C# / .NET\n"
            "• HTML / CSS\n"
            "• JavaScript\n"
            "• SQL / NoSQL\n"
            "• Git\n"
            "• Unity\n",
            reply_markup=get_main_menu(),
        )

    elif query.data == "contacts":
        context.user_data["waiting_for_ai"] = False

        await query.edit_message_text(
            "Контакти:\n\n"
            "Телефон: +380 66 466 58 46\n"
            "E-mail: voitiuk.anastasiia_ip32@edu.kpi.ua",
            reply_markup=get_main_menu(),
        )

    elif query.data == "prompt_ai":
        context.user_data["waiting_for_ai"] = True

        await query.edit_message_text(
            "Prompt AI\n\n"
            "Надішліть текстовий запит, який потрібно "
            "передати Gemini.\n\n"
            "Наприклад:\n"
            "Поясни простими словами, що таке REST API."
        )


async def ai_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("waiting_for_ai"):
        return

    user_prompt = update.message.text

    context.user_data["waiting_for_ai"] = False

    await update.message.reply_text(
        "Генерую відповідь..."
    )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        await update.message.reply_text(response.text)

    except Exception as error:
        print(f"Gemini API error: {error}")

        await update.message.reply_text(
            "Виникла помилка під час звернення до Gemini. "
            "Спробуйте ще раз."
        )


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN не знайдено у .env"
        )

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY не знайдено у .env"
        )

    application = Application.builder().token(
        TELEGRAM_BOT_TOKEN
    ).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_message_handler
        )
    )

    print("Бот запущено...")

    application.run_polling()


if __name__ == "__main__":
    main()

