# # # # pip install flask requests python-telegram-bot==21.3
# # # # pip install duckdb fastapi uvicorn httpx
# # # # TELEGRAM BOT ID 8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # telegram_bot_payu.py
# # # import asyncio
# # # from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# # # from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
# # # from dummy_services import get_country_groups, get_countries_by_group, get_data_packages, get_data_sizes, get_plan_price
# # # from payu import generate_payu_link

# # # USER_STATE = {}

# # # TELEGRAM_BOT_TOKEN = "8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk"

# # # # ---------------- HANDLERS ----------------
# # # async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
# # #     chat_id = str(update.message.chat.id)
# # #     user_name = update.message.from_user.full_name
# # #     print(f"[LOG] /start received from {user_name} ({chat_id})")
# # #     USER_STATE[chat_id] = {"step": "country_group"}

# # #     try:
# # #         groups = get_country_groups(user_id=chat_id)
# # #         keyboard = [[InlineKeyboardButton(k, callback_data=f"group|{k}")] for k in groups]
# # #         await update.message.reply_text(
# # #             "Welcome to the world of eSimNowAI, the world's largest collection of eSims across 180 countries.\n"
# # #             "You are just 15 seconds from activating your eSim!\n\nChoose your destination country group:",
# # #             reply_markup=InlineKeyboardMarkup(keyboard)
# # #         )
# # #     except Exception as e:
# # #         print(f"[ERROR] Failed to fetch country groups for {chat_id}: {e}")
# # #         await update.message.reply_text("⚠ Unable to load country groups. Please try again later.")

# # # async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
# # #     query = update.callback_query
# # #     await query.answer()
# # #     chat_id = str(query.message.chat.id)
# # #     user_name = query.from_user.full_name
# # #     data = query.data
# # #     state = USER_STATE.get(chat_id, {})

# # #     print(f"[LOG] Button clicked by {user_name} ({chat_id}): {data}")

# # #     try:
# # #         # ---------------- COUNTRY GROUP ----------------
# # #         if data.startswith("group|"):
# # #             group = data.split("|")[1]
# # #             state["step"] = "country_select"
# # #             state["country_group"] = group

# # #             countries = get_countries_by_group(group, user_selections=state)
# # #             if not countries:
# # #                 raise Exception("No countries found in this group")
# # #             keyboard = [[InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country|{c['name']}")] for c in countries]
# # #             await query.edit_message_text(f"Choose a country from group {group}:", reply_markup=InlineKeyboardMarkup(keyboard))

# # #         # ---------------- COUNTRY ----------------
# # #         elif data.startswith("country|"):
# # #             country = data.split("|")[1]
# # #             state["step"] = "package_type"
# # #             state["country"] = country

# # #             packages = get_data_packages(user_selections=state)
# # #             keyboard = [[InlineKeyboardButton(p, callback_data=f"package_type|{p}")] for p in packages]
# # #             await query.edit_message_text(f"Country selected: {country}\nChoose data package type:", reply_markup=InlineKeyboardMarkup(keyboard))

# # #         # ---------------- PACKAGE TYPE ----------------
# # #         elif data.startswith("package_type|"):
# # #             package_type = data.split("|")[1]
# # #             state["step"] = "data_select"
# # #             state["package_type"] = package_type

# # #             data_sizes = get_data_sizes(package_type, user_selections=state)
# # #             keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]
# # #             await query.edit_message_text(f"Selected {package_type} data. Choose your plan:", reply_markup=InlineKeyboardMarkup(keyboard))

# # #         # ---------------- DATA SIZE ----------------
# # #         elif data.startswith("data|"):
# # #             data_size = data.split("|")[1]
# # #             state["step"] = "payment"
# # #             state["data"] = data_size

# # #             price = get_plan_price(data_size, user_selections=state)
# # #             payu_link = generate_payu_link(
# # #                 amount=price,
# # #                 productinfo=f"{data_size} eSim for {state['country']}",
# # #                 firstname="TelegramUser",
# # #                 email="user@example.com",
# # #                 phone="9999999999"
# # #             )
# # #             keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
# # #             await query.edit_message_text(f"You selected {data_size} for {state['country']}\nPrice: ₹{price}", reply_markup=InlineKeyboardMarkup(keyboard))

# # #         USER_STATE[chat_id] = state

# # #     except Exception as e:
# # #         print(f"[ERROR] Exception for user {chat_id} at step {state.get('step')}: {e}")
# # #         await query.edit_message_text("⚠ Something went wrong. Please try again later.")


# # # if __name__ == "__main__":
# # #     app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# # #     # Command handlers
# # #     app.add_handler(CommandHandler("start", start))

# # #     # Button / callback handler
# # #     app.add_handler(CallbackQueryHandler(button_callback))

# # #     print("Bot polling started...")
# # #     asyncio.run(app.run_polling())

# # import asyncio
# # from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# # from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
# # from real_services import (
# #     get_country_groups,
# #     get_countries_by_group,
# #     get_data_packages,
# #     get_data_sizes,
# #     get_plan_price,
# # )
# # from payu import generate_payu_link

# # TELEGRAM_BOT_TOKEN = "8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk"
# # USER_STATE = {}


# # async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     chat_id = str(update.message.chat.id)
# #     USER_STATE[chat_id] = {"step": "country_group"}
# #     groups = get_country_groups()
# #     keyboard = [[InlineKeyboardButton(k, callback_data=f"group|{k}")] for k in groups]
# #     await update.message.reply_text(
# #         "🌍 Welcome to *eSimNowAI!*\n"
# #         "The world’s largest eSIM store — choose your country group:",
# #         reply_markup=InlineKeyboardMarkup(keyboard),
# #         parse_mode="Markdown"
# #     )


# # async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     query = update.callback_query
# #     await query.answer()
# #     chat_id = str(query.message.chat.id)
# #     state = USER_STATE.get(chat_id, {})
# #     data = query.data

# #     try:
# #         # COUNTRY GROUP
# #         if data.startswith("group|"):
# #             group = data.split("|")[1]
# #             state["country_group"] = group
# #             countries = get_countries_by_group(group)
# #             keyboard = [
# #                 [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country|{c['name']}")]
# #                 for c in countries[:20]
# #             ]
# #             await query.edit_message_text(
# #                 f"Select a country from {group}:",
# #                 reply_markup=InlineKeyboardMarkup(keyboard)
# #             )
# #             state["step"] = "country"

# #         # COUNTRY
# #         elif data.startswith("country|"):
# #             country = data.split("|")[1]
# #             state["country"] = country
# #             packages = get_data_packages()
# #             keyboard = [[InlineKeyboardButton(p, callback_data=f"package|{p}")] for p in packages]
# #             await query.edit_message_text(
# #                 f"🌎 {country} selected.\nChoose your data package:",
# #                 reply_markup=InlineKeyboardMarkup(keyboard)
# #             )
# #             state["step"] = "package"

# #         # ---------------- PACKAGE TYPE ----------------
# #         elif data.startswith("package_type|"):
# #             package_type = data.split("|")[1]
# #             state["step"] = "data_select"
# #             state["package_type"] = package_type

# #             data_sizes = get_data_sizes_by_package(state["country"], package_type)
# #             keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]
# #             await query.edit_message_text(f"Selected {package_type} package. Choose your plan size:", reply_markup=InlineKeyboardMarkup(keyboard))

# #         # DATA SIZE → PRICE + PAYMENT
# #         elif data.startswith("data|"):
# #             data_size = data.split("|")[1]
# #             state["data"] = data_size
# #             price_info = get_plan_price(data_size, user_selections=state)
# #             price_inr = price_info["priceInr"]
# #             validity = price_info["validity"]

# #             payu_link = generate_payu_link(
# #                 amount=price_inr or 1,
# #                 productinfo=f"{data_size} {state['country']} eSIM",
# #                 firstname="TelegramUser",
# #                 email="user@example.com",
# #                 phone="9999999999"
# #             )

# #             keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
# #             await query.edit_message_text(
# #                 f"You selected *{data_size}* for *{state['country']}*\n"
# #                 f"💰 Price: ₹{price_inr}\n📆 Validity: {validity}",
# #                 reply_markup=InlineKeyboardMarkup(keyboard),
# #                 parse_mode="Markdown"
# #             )

# #         USER_STATE[chat_id] = state

# #     except Exception as e:
# #         print(f"[ERROR] {e}")
# #         await query.edit_message_text("⚠ Something went wrong. Please try again later.")


# # if __name__ == "__main__":
# #     app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
# #     app.add_handler(CommandHandler("start", start))
# #     app.add_handler(CallbackQueryHandler(button_callback))
# #     print("🚀 Telegram bot polling started...")
# #     asyncio.run(app.run_polling())

# import asyncio
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
# from real_services import (
#     get_country_groups,
#     get_countries_by_group,
#     get_data_packages,
#     get_data_sizes_by_package,
#     get_price_for_plan,
# )
# from payu import generate_payu_link

# TELEGRAM_BOT_TOKEN = "8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk"
# USER_STATE = {}


# # ---------------- /start COMMAND ----------------
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = str(update.message.chat.id)
#     USER_STATE[chat_id] = {"step": "country_group"}

#     groups = get_country_groups()
#     keyboard = [[InlineKeyboardButton(k, callback_data=f"group|{k}")] for k in groups]

#     await update.message.reply_text(
#         "🌍 *Welcome to eSimNowAI!*\n"
#         "The world’s largest eSIM store across 180+ countries.\n\n"
#         "Select your destination country group:",
#         reply_markup=InlineKeyboardMarkup(keyboard),
#         parse_mode="Markdown"
#     )


# # ---------------- BUTTON HANDLER ----------------
# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()

#     chat_id = str(query.message.chat.id)
#     state = USER_STATE.get(chat_id, {})
#     data = query.data

#     try:
#         # ---------------- COUNTRY GROUP ----------------
#         if data.startswith("group|"):
#             group = data.split("|")[1]
#             state["country_group"] = group

#             countries = get_countries_by_group(group)
#             keyboard = [
#                 [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country|{c['name']}")]
#                 for c in countries[:20]
#             ]

#             await query.edit_message_text(
#                 f"Choose a country from *{group}*:",
#                 reply_markup=InlineKeyboardMarkup(keyboard),
#                 parse_mode="Markdown"
#             )
#             state["step"] = "country"

#         # ---------------- COUNTRY ----------------
#         elif data.startswith("country|"):
#             country = data.split("|")[1]
#             state["country"] = country

#             packages = get_data_packages()
#             keyboard = [[InlineKeyboardButton(p, callback_data=f"package|{p}")] for p in packages]

#             await query.edit_message_text(
#                 f"🌎 *{country}* selected.\n\nChoose your data package range:",
#                 reply_markup=InlineKeyboardMarkup(keyboard),
#                 parse_mode="Markdown"
#             )
#             state["step"] = "package"

#         # ---------------- PACKAGE TYPE (FILTER RANGE) ----------------
#         elif data.startswith("package|"):
#             package_type = data.split("|")[1]
#             state["package_type"] = package_type

#             # Filter available sizes based on range (from real API)
#             data_sizes = get_data_sizes_by_package(state["country"], package_type)

#             if not data_sizes:
#                 await query.edit_message_text(
#                     f"⚠ No data sizes found for {state['country']} in {package_type} range."
#                 )
#                 return

#             keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]

#             await query.edit_message_text(
#                 f"📦 *{package_type}* package selected.\n"
#                 f"Now choose your data size (filtered from live API):",
#                 reply_markup=InlineKeyboardMarkup(keyboard),
#                 parse_mode="Markdown"
#             )

#             state["step"] = "data"

#         # ---------------- DATA SIZE (SHOW PRICE + PAYU) ----------------
#         elif data.startswith("data|"):
#             data_size = data.split("|")[1]
#             state["data"] = data_size

#             # 💰 Fetch live price from API
#             price = get_price_for_plan(state["country"], data_size)
#             if not price:
#                 await query.edit_message_text(
#                     f"⚠ No valid plan found for {state['country']} ({data_size}). Please choose another."
#                 )
#                 return

#             # 🧾 Generate PayU link
#             payu_link = generate_payu_link(
#                 amount=float(price),
#                 productinfo=f"{data_size} eSIM for {state['country']}",
#                 firstname="TelegramUser",
#                 email="user@example.com",
#                 phone="9999999999"
#             )

#             keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]

#             await query.edit_message_text(
#                 f"✅ You selected *{data_size}* for *{state['country']}*\n\n"
#                 f"💰 *Price:* ₹{price}\n"
#                 f"📆 *Validity:* Based on plan details\n\n"
#                 f"Click below to proceed with payment:",
#                 reply_markup=InlineKeyboardMarkup(keyboard),
#                 parse_mode="Markdown"
#             )

#             state["step"] = "done"

#         USER_STATE[chat_id] = state

#     except Exception as e:
#         print(f"[ERROR] {e}")
#         await query.edit_message_text("⚠ Something went wrong. Please try again later.")


# # ---------------- RUN BOT ----------------
# if __name__ == "__main__":
#     app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CallbackQueryHandler(button_callback))
#     print("🚀 Telegram bot polling started...")
#     asyncio.run(app.run_polling())

# pip install python-telegram-bot==21.3 requests

import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from real_services import (
    get_country_groups,
    get_countries_by_group,
    get_data_packages,
    get_data_sizes_by_package,
    get_price_for_plan,
)
from payu import generate_payu_link

# ---------------- CONFIG ----------------
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
USER_STATE = {}


# ---------------- START HANDLER ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    USER_STATE[chat_id] = {"step": "country_group"}

    groups = get_country_groups()
    keyboard = [[InlineKeyboardButton(k, callback_data=f"group|{k}")] for k in groups]

    await update.message.reply_text(
        "🌍 *Welcome to eSimNowAI!*\nThe world’s largest eSIM store — choose your country group:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ---------------- CALLBACK HANDLER ----------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat.id)
    data = query.data
    state = USER_STATE.get(chat_id, {})

    try:
        # Step 1: Country Group
        if data.startswith("group|"):
            group = data.split("|")[1]
            state["country_group"] = group
            countries = get_countries_by_group(group)

            keyboard = [
                [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country|{c['name']}")]
                for c in countries[:20]
            ]
            await query.edit_message_text(
                f"Choose a country from *{group}*:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            state["step"] = "country"

        # Step 2: Country
        elif data.startswith("country|"):
            country = data.split("|")[1]
            state["country"] = country

            packages = get_data_packages()
            keyboard = [[InlineKeyboardButton(p, callback_data=f"package|{p}")] for p in packages]
            await query.edit_message_text(
                f"🌎 *{country}* selected.\nNow choose your data package type:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            state["step"] = "package"

        # Step 3: Package Type
        elif data.startswith("package|"):
            package_type = data.split("|")[1]
            state["package_type"] = package_type

            data_sizes = get_data_sizes_by_package(state["country"], package_type)
            keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]

            await query.edit_message_text(
                f"📦 Selected *{package_type}* package.\nNow choose your data size:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            state["step"] = "data"

        # Step 4: Data Size + Price
        elif data.startswith("data|"):
            data_size = data.split("|")[1]
            state["data"] = data_size

            price = get_price_for_plan(state["country"], data_size)
            if not price:
                await query.edit_message_text(f"⚠ No valid price found for {state['country']} {data_size}")
                return

            payu_link = generate_payu_link(
                amount=float(price),
                productinfo=f"{data_size} {state['country']} eSIM",
                firstname="TelegramUser",
                email="user@example.com",
                phone="9999999999"
            )

            keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
            await query.edit_message_text(
                f"You selected *{data_size}* for *{state['country']}*\n💰 Price: ₹{price}\n\nClick below to pay securely:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        USER_STATE[chat_id] = state

    except Exception as e:
        print(f"[ERROR] {e}")
        await query.edit_message_text("⚠ Something went wrong. Please try again later.")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 Telegram bot polling started...")
    asyncio.run(app.run_polling())