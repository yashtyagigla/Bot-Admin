# # # # # # # # pip install flask requests python-telegram-bot==21.3
# # # # # # # # pip install duckdb fastapi uvicorn httpx
# # # # # # # # TELEGRAM BOT ID 8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from real_services import (
    search_countries,
    get_plans,
    get_available_data_options
)

# ================= ENV =================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "7898226054:AAHBsfNIryD9IIU1cUYfJsAGDdzeaqRc79s"

USER_STATE = {}

# ================= CURRENCY =================
def usd_to_inr(usd):
    try:
        r = requests.get(
            "https://api.freecurrencyapi.com/v1/latest",
            params={
                "apikey": "YOUR_API_KEY",
                "base_currency": "USD",
                "currencies": "INR"
            },
            timeout=8
        )
        return round(float(usd) * float(r.json()["data"]["INR"]), 2)
    except Exception:
        return round(float(usd) * 82, 2)

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text.strip().lower()

    # 🔄 Restart
    if text in ["hi", "hello", "hey", "start"]:
        USER_STATE[chat_id] = {"step": "country"}
        await update.message.reply_text("🌍 Type country name:")
        return

    state = USER_STATE.get(chat_id, {})

    # ---------- COUNTRY ----------
    if state.get("step") == "country":
        matches = search_countries(text)
        if not matches:
            return

        keyboard = [
            [InlineKeyboardButton(c, callback_data=f"country|{c}")]
            for c in matches[:20]
        ]

        await update.message.reply_text(
            "Select country:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ---------- DURATION ----------
    if state.get("step") == "duration":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter duration in days (number only)")
            return

        duration = int(text)
        country = state["country"]

        data_options = get_available_data_options(country, duration)

        if not data_options:
            await update.message.reply_text("❌ No plans for this duration")
            return

        USER_STATE[chat_id]["duration"] = duration
        USER_STATE[chat_id]["step"] = "data"

        keyboard = [
            [InlineKeyboardButton(
                "Unlimited" if d == "unlimited" else f"{d}GB",
                callback_data=f"data|{d}"
            )]
            for d in data_options
        ]

        keyboard.append([InlineKeyboardButton("🔄 Restart", callback_data="restart")])

        await update.message.reply_text(
            f"📶 Select data for *{country} – {duration} days*:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

# ================= CALLBACK HANDLER =================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = q.message.chat.id
    data = q.data
    state = USER_STATE.get(chat_id, {})

    # ---------- COUNTRY SELECT ----------
    if data.startswith("country|"):
        country = data.split("|", 1)[1]
        USER_STATE[chat_id] = {
            "step": "duration",
            "country": country
        }

        await q.edit_message_text(
            f"📅 Enter duration (days) for *{country}*:",
            parse_mode="Markdown"
        )
        return

    # ---------- DATA SELECT ----------
    if data.startswith("data|"):
        data_filter = data.split("|", 1)[1]
        country = state["country"]
        duration = state["duration"]

        plans = get_plans(country, duration, data_filter)

        if not plans:
            await q.edit_message_text("❌ No plans found")
            return

        msg = f"📦 *{country} – {duration} Day Plans*\n\n"

        for p in plans:
            inr = usd_to_inr(p["usd"])
            msg += (
                f"📡 *{p['provider']}*\n"
                f"🌍 Region: `{p['region']}`\n"
                f"📶 Data: `{p['data']}` | ⏳ `{p['days']} Days`\n"
                f"💰 Price: *₹{inr}* (${p['usd']})\n\n"
            )

        keyboard = [
            [InlineKeyboardButton("⬅ Back to Data", callback_data="back_data")],
            [InlineKeyboardButton("🔄 Restart", callback_data="restart")]
        ]

        await q.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ---------- BACK TO DATA ----------
    if data == "back_data":
        USER_STATE[chat_id]["step"] = "data"
        country = state["country"]
        duration = state["duration"]

        data_options = get_available_data_options(country, duration)

        keyboard = [
            [InlineKeyboardButton(
                "Unlimited" if d == "unlimited" else f"{d}GB",
                callback_data=f"data|{d}"
            )]
            for d in data_options
        ]

        keyboard.append([InlineKeyboardButton("🔄 Restart", callback_data="restart")])

        await q.edit_message_text(
            f"📶 Select data for *{country} – {duration} days*:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # ---------- RESTART ----------
    if data == "restart":
        USER_STATE[chat_id] = {"step": "country"}
        await q.edit_message_text("🌍 Type country name:")

# ================= MAIN =================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 Telegram bot running...")
    asyncio.run(app.run_polling())