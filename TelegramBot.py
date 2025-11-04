# # # # # pip install flask requests python-telegram-bot==21.3
# # # # # pip install duckdb fastapi uvicorn httpx
# # # # # TELEGRAM BOT ID 8452377576:AAHdrDpRx6hlqkq5RxrV4tBjC49WWLnfgwk

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import requests
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ---- IMPORT SERVICES ----
from real_services import (
    get_country_groups,
    get_countries_by_group,
    get_data_packages,
    get_data_sizes_by_package,
    get_price_for_plan
)
from payu import generate_payu_link

# ---- LOAD ENV ----
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8081222005:AAGLlgJm5G28c8hd7wwPePbjHZFqNefl8sI"
PASSPORT_UPLOAD_URL = "https://api.escuelajs.co/api/v1/files/upload"

USER_STATE = {}

# ==========================================================
# 🟢 START COMMAND
# ==========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    USER_STATE[chat_id] = {"step": "phone"}

    keyboard = [[KeyboardButton("📱 Share Phone Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "🌍 *Welcome to eSimNowAI!*\n"
        "The world's largest eSIM store.\n\n"
        "Please share your *phone number* to continue:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ==========================================================
# 📞 HANDLE PHONE NUMBER
# ==========================================================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    state = USER_STATE.get(chat_id, {})
    if state.get("step") != "phone":
        return

    phone_number = update.message.contact.phone_number
    state["phone"] = phone_number
    state["step"] = "country_group"
    USER_STATE[chat_id] = state

    groups = get_country_groups()
    keyboard = [[InlineKeyboardButton(k, callback_data=f"group|{k}")] for k in groups]

    await update.message.reply_text(
        f"✅ Phone number received: {phone_number}",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "🌎 Please select your *country group*: ",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ==========================================================
# 🧭 CALLBACK HANDLER
# ==========================================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat.id)
    data = query.data
    state = USER_STATE.get(chat_id, {})

    try:
        # ---- COUNTRY GROUP ----
        if data.startswith("group|"):
            group = data.split("|")[1]
            state["country_group"] = group

            country_data = get_countries_by_group(group, page=1)
            countries = country_data["countries"]
            total_pages = country_data["total_pages"]

            keyboard = [
                [InlineKeyboardButton(f"{c.get('flag', '🌍')} {c.get('name', '')}", callback_data=f"country|{c.get('name', '')}")]
                for c in countries
            ]

            # Pagination buttons
            nav_buttons = []
            if total_pages > 1:
                nav_buttons.append(InlineKeyboardButton("➡ Next", callback_data=f"page|{group}|2"))
            if nav_buttons:
                keyboard.append(nav_buttons)

            await query.edit_message_text(
                f"🌎 Choose a country from *{group}* (Page 1 of {total_pages}):",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            state["step"] = "country"

                # ---------------- PAGINATION HANDLER ----------------
        elif data.startswith("page|"):
            _, group, page_str = data.split("|")
            page = int(page_str)
            state["country_group"] = group
            state["page"] = page

            country_data = get_countries_by_group(group, page=page)
            countries = country_data["countries"]
            total_pages = country_data["total_pages"]

            keyboard = [
                [InlineKeyboardButton(f"{c.get('flag', '🌍')} {c['name']}", callback_data=f"country|{c['name']}")]
                for c in countries
            ]

            # Pagination buttons
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton("⬅ Prev", callback_data=f"page|{group}|{page-1}"))
            if page < total_pages:
                nav_buttons.append(InlineKeyboardButton("➡ Next", callback_data=f"page|{group}|{page+1}"))
            if nav_buttons:
                keyboard.append(nav_buttons)

            await query.edit_message_text(
                f"Choose a country from *{group}* (Page {page} of {total_pages}):",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        # ---- COUNTRY ----
        elif data.startswith("country|"):
            country = data.split("|")[1]
            state["country"] = country

            packages = get_data_packages()
            keyboard = [[InlineKeyboardButton(p, callback_data=f"package|{p}")] for p in packages]

            await query.edit_message_text(
                f"🌎 *{country}* selected.\nNow choose your package type:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            state["step"] = "package"

        # ---- PACKAGE ----
        # elif data.startswith("package|"):
        #     package_type = data.split("|")[1]
        #     state["package_type"] = package_type

        #     data_sizes = get_data_sizes_by_package(state["country"], package_type)
        #     keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]

        #     await query.edit_message_text(
        #         f"📦 Selected *{package_type}* package.\nNow choose your data size:",
        #         reply_markup=InlineKeyboardMarkup(keyboard),
        #         parse_mode="Markdown"
        #     )
        #     state["step"] = "data"

        elif data.startswith("package|"):
            package_type = data.split("|")[1]
            state["package_type"] = package_type

            data_sizes = get_data_sizes_by_package(state["country"], package_type)

            # 🛡️ Handle no plans case safely
            if not data_sizes or all("⚠️" in d for d in data_sizes):
                await query.edit_message_text(
                    f"⚠️ Sorry, no *{package_type}* plans are available for *{state['country']}*.\n"
                    f"Please try another category.",
                    parse_mode="Markdown"
                )
                return

            # ✅ Otherwise, show data size buttons
            keyboard = [[InlineKeyboardButton(d, callback_data=f"data|{d}")] for d in data_sizes]

            await query.edit_message_text(
                f"📦 Selected *{package_type}* package.\nNow choose your data size:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

            state["step"] = "data"
        # ---- DATA SIZE + PRICE ----
        elif data.startswith("data|"):
            data_size = data.split("|")[1]
            state["data"] = data_size
            price = get_price_for_plan(state["country"], data_size)

            if not price:
                await query.edit_message_text(f"⚠️ No valid plan found for {state['country']} ({data_size}).")
                return

            state["price"] = price
            state["step"] = "passport"
            USER_STATE[chat_id] = state

            await query.edit_message_text(
                f"You selected *{data_size}* for *{state['country']}*\n"
                f"💰 Price: ₹{price}\n\n"
                "📸 *Please upload your passport image* to continue with the purchase.\n\n"
                "This is required for eSIM activation. **Send it as a photo, not a document.**",
                parse_mode="Markdown"
            )

        USER_STATE[chat_id] = state

    except Exception as e:
        print(f"[ERROR] Callback: {e}")
        await query.edit_message_text("⚠ Something went wrong. Please try again later.")

# ==========================================================
# 🖼️ PASSPORT UPLOAD HANDLER
# ==========================================================
# async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = str(update.message.chat.id)
#     state = USER_STATE.get(chat_id, {})
#     if state.get("step") != "passport":
#         return

#     phone_number = state.get("phone", "unknown")
#     clean_phone = "".join(filter(str.isalnum, phone_number))
#     file_path = f"passport_{clean_phone}_{chat_id}.jpg"

#     photo = update.message.photo[-1]
#     photo_file = await photo.get_file()
#     await photo_file.download_to_drive(file_path)
#     print(f"✅ Downloaded: {file_path}")

#     upload_success = False
#     try:
#         with open(file_path, "rb") as f:
#             files = {"passport_image": f}
#             data = {"chat_id": chat_id, "phone_number": phone_number}
#             response = await asyncio.to_thread(requests.post, PASSPORT_UPLOAD_URL, files=files, data=data, timeout=30)
#             upload_success = response.status_code == 200
#             print(f"[UPLOAD] Status: {response.status_code}")
#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             print(f"🗑️ Deleted: {file_path}")

#     if not upload_success:
#         await update.message.reply_text("❌ Failed to upload passport. Please try again.")
#         return

#     # ✅ Upload success — show order summary + Buy Now button
#     phone = state.get("phone", "9999999999")
#     price = state.get("price")
#     data_size = state.get("data")
#     country = state.get("country")

#     payu_link = generate_payu_link(
#         amount=float(price),
#         productinfo=f"{data_size} {country} eSIM",
#         firstname="TelegramUser",
#         email="user@example.com",
#         phone=phone
#     )

#     keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
#     await update.message.reply_text(
#         f"✅ Passport image received and **uploaded successfully**!\n\n"
#         f"📋 *Order Summary:*\n"
#         f"🌎 Country: *{country}*\n"
#         f"📦 Package: *{data_size}*\n"
#         f"💰 Price: ₹{price}\n"
#         f"📱 Phone: {phone}\n\n"
#         "Click below to pay securely:",
#         reply_markup=InlineKeyboardMarkup(keyboard),
#         parse_mode="Markdown"
#     )

# ---------------- PHOTO HANDLER (for passport upload) ----------------
# async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = str(update.message.chat.id)
#     state = USER_STATE.get(chat_id, {})

#     if state.get("step") != "passport":
#         return

#     phone_number = state.get("phone", "unknown_phone")

#     # Get the highest resolution photo
#     photo = update.message.photo[-1]
#     photo_file = await photo.get_file()

#     # Clean filename
#     clean_phone = "".join(filter(str.isalnum, phone_number))
#     file_path = f"passport_{clean_phone}_{chat_id}.jpg"

#     try:
#         # Download the photo locally
#         await photo_file.download_to_drive(file_path)
#         print(f"✅ Downloaded image: {file_path}")

#         # 🚫 Commented out upload logic for now
#         # with open(file_path, 'rb') as f:
#         #     files = {'passport_image': (f.name, f, 'image/jpeg')}
#         #     data = {
#         #         'chat_id': chat_id,
#         #         'phone_number': phone_number,
#         #         'country': state.get("country", "N/A"),
#         #         'package': state.get("data", "N/A"),
#         #         'price': state.get("price", "N/A"),
#         #     }
#         #     response = await asyncio.to_thread(
#         #         requests.post,
#         #         PASSPORT_UPLOAD_URL,
#         #         files=files,
#         #         data=data,
#         #         timeout=30
#         #     )
#         #
#         #     if response.status_code in [200, 201]:
#         #         upload_success = True
#         #     else:
#         #         upload_success = False

#         # ✅ For now — always assume upload is successful
#         upload_success = True

#     except Exception as e:
#         print(f"[ERROR] While saving image: {e}")
#         await update.message.reply_text("⚠️ Something went wrong while saving your photo. Please try again.")
#         return
#     finally:
#         # Delete the local file
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             print(f"🗑️ Deleted temporary file: {file_path}")

#     # ✅ Continue flow — even if fake upload
#     # if upload_success:
#     #     state["passport_photo_id"] = photo.file_id
#     #     state["step"] = "payment"
#     #     USER_STATE[chat_id] = state

#     #     phone = state.get("phone", "9999999999")
#     #     price = state.get("price")
#     #     data_size = state.get("data")
#     #     country = state.get("country")

#     #     payu_link = generate_payu_link(
#     #         amount=float(price),
#     #         productinfo=f"{data_size} {country} eSIM",
#     #         firstname="TelegramUser",
#     #         email="user@example.com",
#     #         phone=phone
#     #     )

#     #     keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
#     #     await update.message.reply_text(
#     #         f"✅ Image received successfully!\n\n"
#     #         f"📋 *Order Summary:*\n"
#     #         f"🌍 Country: *{country}*\n"
#     #         f"📦 Package: *{data_size}*\n"
#     #         f"💰 Price: ₹{price}\n"
#     #         f"📱 Phone: {phone}\n\n"
#     #         "Click below to pay securely:",
#     #         reply_markup=InlineKeyboardMarkup(keyboard),
#     #         parse_mode="Markdown"
#     #     )

#         if upload_success:
#             state["passport_photo_id"] = photo.file_id
#             state["step"] = "payment"
#             USER_STATE[chat_id] = state

#             phone = state.get("phone", "9999999999")
#             price = state.get("price")
#             data_size = state.get("data")
#             country = state.get("country")

#             # --- ✅ Fetch Plan ID from Live API ---
#             plan_id = "N/A"
#         try:
#             resp = await asyncio.to_thread(
#                 requests.get,
#                 "https://apiesim.connectingit.in/api/product/get-all-product",
#                 timeout=30
#             )
#             if resp.status_code == 200:
#                 data = resp.json()
#                 if isinstance(data, list):
#                     target_country = country.lower().replace(" ", "")
#                     target_data = data_size.lower().replace(" ", "").replace("—", "-").replace("–", "-")
                    
#                     for p in data:
#                         name = str(p.get("name", "")).lower().replace(" ", "").replace("—", "-").replace("–", "-")
#                         if target_country in name and target_data.split("-")[0] in name:
#                             plan_id = p.get("localPlanId", "N/A")
#                             print(f"[MATCH ✅] Found Plan ID: {plan_id} for {p.get('name')}")
#                             break
#                     else:
#                         print(f"[WARN] No match found for {country} ({data_size}) in API results.")
#             else:
#                 print(f"[ERROR] API returned {resp.status_code}: {resp.text}")
#         except Exception as e:
#             print(f"[WARN] Could not fetch plan ID: {e}")

#             # --- ✅ Continue to payment ---
#             payu_link = generate_payu_link(
#                 amount=float(price),
#                 productinfo=f"{data_size} {country} eSIM",
#                 firstname="TelegramUser",
#                 email="user@example.com",
#                 phone=phone
#             )

#             keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]

#             await update.message.reply_text(
#                 f"✅ Passport image received and **uploaded successfully**!\n\n"
#                 f"📋 *Order Summary:*\n"
#                 f"🌍 Country: *{country}*\n"
#                 f"📦 Package: *{data_size}*\n"
#                 f"💰 Price: ₹{price}\n"
#                 f"📱 Phone: {phone}\n"
#                 f"🆔 Plan ID: {plan_id}\n\n"
#                 "Click below to pay securely:",
#                 reply_markup=InlineKeyboardMarkup(keyboard),
#                 parse_mode="Markdown"
#             )

# ---------------- PHOTO HANDLER ----------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    state = USER_STATE.get(chat_id, {})

    if state.get("step") != "passport":
        return

    # Get the user's phone number
    phone_number = state.get("phone", "unknown_phone")

    # Get the photo file
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()

    # Generate a clean filename
    clean_phone = "".join(filter(str.isalnum, phone_number))
    file_path = f"passport_{clean_phone}_{chat_id}.jpg"

    # Save temporarily
    await photo_file.download_to_drive(file_path)
    print(f"✅ Downloaded image: {file_path}")

    # --- Simulated upload (for now accepts any image) ---
    upload_success = True
    plan_id = "N/A"

        # 🧩 Fetch Plan ID from live API (smarter matching)
    try:
        resp = await asyncio.to_thread(
            requests.get,
            "https://apiesim.connectingit.in/api/product/get-all-product",
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            target_country = state.get("country", "").lower()
            target_data = state.get("data", "").lower()

            # extract just the number before 'gb' if available
            gb_part = None
            if "gb" in target_data:
                gb_part = target_data.split("gb")[0].strip()

            for p in data:
                pname = str(p.get("name", "")).lower()
                pdata = str(p.get("data", "")).lower()

                # ✅ Flexible match: country must match, and data either matches GB number or "unlimited"
                if (
                    target_country in pname
                    and (
                        (gb_part and gb_part in pname)
                        or "unlimited" in pname
                        or pdata in ["unlimited", "∞", "0"]
                    )
                ):
                    plan_id = p.get("localPlanId", "N/A")
                    print(f"[MATCH ✅] Found Plan ID: {plan_id} for {p.get('name')}")
                    break
            else:
                print(f"[WARN] No matching Plan ID found for {target_country} ({target_data})")

        else:
            print(f"[ERROR] Plan ID API returned {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Could not fetch plan ID: {e}")

    # 🗑️ Delete the local file
    try:
        os.remove(file_path)
        print(f"🗑️ Deleted temporary file: {file_path}")
    except Exception as e:
        print(f"[WARN] Could not delete file: {e}")

    # Update state
    state["passport_photo_id"] = photo.file_id
    state["step"] = "payment"
    state["plan_id"] = plan_id
    USER_STATE[chat_id] = state

    # ✅ Send confirmation message to Telegram
    price = state.get("price", "N/A")
    data_size = state.get("data", "N/A")
    country = state.get("country", "N/A")
    phone = state.get("phone", "N/A")

    from payu import generate_payu_link
    payu_link = generate_payu_link(
        amount=float(price),
        productinfo=f"{data_size} {country} eSIM",
        firstname="TelegramUser",
        email="user@example.com",
        phone=phone
    )

    keyboard = [[InlineKeyboardButton("💳 Buy Now", url=payu_link)]]
    await update.message.reply_text(
        f"✅ Image received successfully!\n\n"
        f"📋 *Order Summary:*\n"
        f"🌍 Country: *{country}*\n"
        f"📦 Package: *{data_size}*\n"
        f"💰 Price: ₹{price}\n"
        f"📱 Phone: {phone}\n"
        f"🆔 Plan ID: {plan_id}\n\n"
        "Click below to pay securely:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ==========================================================
# 💬 TEXT HANDLER — Restart if user types random text
# ==========================================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ==========================================================
# 🚀 MAIN
# ==========================================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 Telegram bot polling started...")
    asyncio.run(app.run_polling())