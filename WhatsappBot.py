# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # # #pip install flask twilio
# # # import asyncio
# # # from flask import Flask, request
# # # from twilio.twiml.messaging_response import MessagingResponse
# # # from dummy_services import get_country_groups, get_countries_by_group, get_data_packages, get_data_sizes, get_plan_price
# # # from payu import generate_payu_link  # your existing PayU function

# # # # ---------------- CONFIG ----------------
# # # app = Flask(__name__)
# # # USER_STATE = {}  # phone -> user session

# # # # ---------------- HELPER FUNCTIONS ----------------
# # # def send_message(resp, message, options=None):
# # #     """Send a WhatsApp message with optional numbered options"""
# # #     if options:
# # #         options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
# # #         message += "\n\n" + options_text
# # #     resp.message(message)

# # # def parse_number_choice(text, options):
# # #     """Return selected item from numbered input"""
# # #     if text.isdigit():
# # #         idx = int(text)-1
# # #         if 0 <= idx < len(options):
# # #             return options[idx]
# # #     return None

# # # # ---------------- FLASK WEBHOOK ----------------
# # # @app.route("/whatsapp", methods=["POST"])
# # # def whatsapp_webhook():
# # #     resp = MessagingResponse()
# # #     try:
# # #         sender = request.values.get('From')  # WhatsApp number
# # #         text = request.values.get('Body', '').strip()
# # #         print(f"[LOG] Message from {sender}: {text}")

# # #         state = USER_STATE.get(sender, {"step": "country_group"})

# # #         # ---------------- STEP 1: COUNTRY GROUP ----------------
# # #         if state["step"] == "country_group":
# # #             try:
# # #                 groups = get_country_groups(user_id=sender)
# # #                 send_message(resp, "Welcome to eSimNowAI! Choose your destination country group:", groups)
# # #                 state["step"] = "country_group_pending"
# # #             except Exception as e:
# # #                 print(f"[ERROR] Failed to fetch country groups: {e}")
# # #                 send_message(resp, "⚠ Unable to load country groups. Please try again later.")

# # #         # ---------------- STEP 2: COUNTRY GROUP PENDING ----------------
# # #         elif state["step"] == "country_group_pending":
# # #             groups = get_country_groups(user_id=sender)
# # #             choice = parse_number_choice(text, groups)
# # #             if choice:
# # #                 state["country_group"] = choice
# # #                 try:
# # #                     countries = get_countries_by_group(choice, user_selections=state)
# # #                     if not countries:
# # #                         raise Exception("No countries found")
# # #                     country_names = [f"{c['flag']} {c['name']}" for c in countries]
# # #                     send_message(resp, f"Choose a country from group {choice}:", country_names)
# # #                     state["step"] = "country_pending"
# # #                     state["countries_list"] = countries
# # #                 except Exception as e:
# # #                     print(f"[ERROR] {e}")
# # #                     send_message(resp, f"⚠ No countries found in group {choice}. Try again.")
# # #                     state["step"] = "country_group"
# # #             else:
# # #                 send_message(resp, "⚠ Invalid input. Please enter the number corresponding to the country group.")

# # #         # ---------------- STEP 3: COUNTRY PENDING ----------------
# # #         elif state["step"] == "country_pending":
# # #             countries = state.get("countries_list", [])
# # #             choice = parse_number_choice(text, countries)
# # #             if choice:
# # #                 country_name = choice["name"]
# # #                 state["country"] = country_name
# # #                 packages = get_data_packages(user_selections=state)
# # #                 send_message(resp, f"Country selected: {country_name}\nChoose data package type:", packages)
# # #                 state["step"] = "package_type_pending"
# # #             else:
# # #                 send_message(resp, "⚠ Invalid input. Please select a valid country number.")

# # #         # ---------------- STEP 4: PACKAGE TYPE PENDING ----------------
# # #         elif state["step"] == "package_type_pending":
# # #             packages = get_data_packages(user_selections=state)
# # #             if text in packages:
# # #                 state["package_type"] = text
# # #                 data_sizes = get_data_sizes(text, user_selections=state)
# # #                 send_message(resp, f"Selected {text} data. Choose your plan:", data_sizes)
# # #                 state["step"] = "data_pending"
# # #             else:
# # #                 send_message(resp, "⚠ Invalid package type. Please type one of the options exactly.")

# # #         # ---------------- STEP 5: DATA SIZE PENDING ----------------
# # #         elif state["step"] == "data_pending":
# # #             data_sizes = get_data_sizes(state["package_type"], user_selections=state)
# # #             if text in data_sizes:
# # #                 state["data"] = text
# # #                 price = get_plan_price(text, user_selections=state)
# # #                 # Generate dynamic PayU link
# # #                 payu_link = generate_payu_link(
# # #                     amount=price,
# # #                     productinfo=f"{text} eSim for {state['country']}",
# # #                     firstname="WhatsAppUser",
# # #                     email="user@example.com",
# # #                     phone=sender.replace("whatsapp:", "")
# # #                 )
# # #                 send_message(resp, f"You selected {text} for {state['country']}\nPrice: ₹{price}\n💳 Pay via: {payu_link}")
# # #                 state["step"] = "payment_done"
# # #             else:
# # #                 send_message(resp, "⚠ Invalid data size. Please type one of the options.")

# # #         # Save user state
# # #         USER_STATE[sender] = state

# # #     except Exception as e:
# # #         print(f"[ERROR] Exception in webhook for {sender}: {e}")
# # #         resp.message("⚠ Something went wrong. Please try again later.")

# # #     return str(resp)

# # # # ---------------- RUN FLASK ----------------
# # # if __name__ == "__main__":
# # #     print("WhatsApp bot running on port 5000...")
# # #     app.run(host="0.0.0.0", port=5000)


# # from flask import Flask, request
# # from twilio.twiml.messaging_response import MessagingResponse
# # from real_services import (
# #     get_country_groups,
# #     get_countries_by_group,
# #     get_available_data_sizes,
# #     get_price_for_plan
# # )
# # from payu import generate_payu_link

# # app = Flask(__name__)
# # USER_STATE = {}


# # # ---------------- HELPER FUNCTIONS ----------------
# # def send_message(resp, message, options=None):
# #     """Send a WhatsApp message with optional numbered options"""
# #     if options:
# #         options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
# #         message += "\n\n" + options_text
# #     resp.message(message)


# # def parse_choice(text, options):
# #     """Parse user numeric input to select an item"""
# #     if text.isdigit():
# #         idx = int(text) - 1
# #         if 0 <= idx < len(options):
# #             return options[idx]
# #     return None


# # def get_data_packages():
# #     """Return 3-tier data package ranges"""
# #     return ["Minimal (1GB–10GB)", "Medium (10GB–20GB)", "Heavy (20GB–Unlimited)"]


# # def get_data_sizes_by_package(country, package_type):
# #     """Filter data sizes by package range"""
# #     all_sizes = get_available_data_sizes(country)
# #     filtered = []
# #     for size in all_sizes:
# #         num = int(size.replace("GB", "").strip()) if "GB" in size else 0
# #         if package_type.startswith("Minimal") and 1 <= num <= 10:
# #             filtered.append(size)
# #         elif package_type.startswith("Medium") and 10 <= num <= 20:
# #             filtered.append(size)
# #         elif package_type.startswith("Heavy") and num >= 20:
# #             filtered.append(size)
# #     print(f"[INFO] {len(filtered)} data sizes found for {country} ({package_type}): {filtered}")
# #     return filtered or ["1GB", "3GB", "5GB"]


# # # ---------------- FLASK WEBHOOK ----------------
# # @app.route("/whatsapp", methods=["POST"])
# # def whatsapp_webhook():
# #     resp = MessagingResponse()
# #     sender = request.values.get("From")
# #     text = request.values.get("Body", "").strip()
# #     state = USER_STATE.get(sender, {"step": "group"})

# #     try:
# #         # ---------------- STEP 1: COUNTRY GROUP ----------------
# #         if state["step"] == "group":
# #             groups = get_country_groups()
# #             send_message(resp, "🌍 Welcome to eSimNowAI!\nSelect your country group:", groups)
# #             state["step"] = "group_pending"

# #         # ---------------- STEP 2: SELECT COUNTRY ----------------
# #         elif state["step"] == "group_pending":
# #             groups = get_country_groups()
# #             choice = parse_choice(text, groups)
# #             if not choice:
# #                 send_message(resp, "⚠ Invalid choice. Please enter a valid number.")
# #             else:
# #                 countries = get_countries_by_group(choice)
# #                 country_names = [f"{c['flag']} {c['name']}" for c in countries[:10]]
# #                 send_message(resp, f"Choose a country from {choice}:", country_names)
# #                 state.update({"step": "country_pending", "countries": countries})

# #         # ---------------- STEP 3: SELECT PACKAGE ----------------
# #         elif state["step"] == "country_pending":
# #             countries = state["countries"]
# #             choice = parse_choice(text, countries)
# #             if choice:
# #                 state["country"] = choice["name"]
# #                 packages = get_data_packages()
# #                 send_message(
# #                     resp,
# #                     f"Country selected: {state['country']}\nNow choose your data usage preference:",
# #                     packages
# #                 )
# #                 state["step"] = "package_pending"
# #             else:
# #                 send_message(resp, "⚠ Invalid input. Please try again.")

# #         # ---------------- STEP 4: SELECT DATA SIZE ----------------
# #         elif state["step"] == "package_pending":
# #             packages = get_data_packages()
# #             choice = parse_choice(text, packages)
# #             if not choice:
# #                 send_message(resp, "⚠ Invalid input. Please enter the correct package number.")
# #             else:
# #                 state["package"] = choice
# #                 sizes = get_data_sizes_by_package(state["country"], choice)
# #                 send_message(resp, f"Selected package: {choice}\nNow choose a data size:", sizes)
# #                 state["step"] = "data_pending"
# #                 state["sizes"] = sizes

# #         # ---------------- STEP 5: PRICE + PAYMENT ----------------
# #         elif state["step"] == "data_pending":
# #             sizes = state["sizes"]
# #             choice = parse_choice(text, sizes)
# #             if choice:
# #                 state["data"] = choice
# #                 # 💰 Fetch live price using API
# #                 price = get_price_for_plan(state["country"], choice)

# #                 if not price:
# #                     send_message(resp, f"⚠ No valid plan found for {state['country']} {choice}. Try a different size.")
# #                 else:
# #                     payu_link = generate_payu_link(
# #                         amount=float(price),
# #                         productinfo=f"{choice} eSIM for {state['country']}",
# #                         firstname="WhatsAppUser",
# #                         email="user@example.com",
# #                         phone=sender.replace("whatsapp:", "")
# #                     )
# #                     send_message(
# #                         resp,
# #                         f"You selected {choice} for {state['country']}\n💰 Price: ₹{price}\n💳 Pay here: {payu_link}"
# #                     )
# #                     state["step"] = "done"
# #             else:
# #                 send_message(resp, "⚠ Invalid selection. Please enter a valid option.")

# #         USER_STATE[sender] = state

# #     except Exception as e:
# #         print("[ERROR]", e)
# #         resp.message("⚠ Something went wrong. Please try again later.")

# #     return str(resp)


# # # ---------------- RUN FLASK ----------------
# # if __name__ == "__main__":
# #     print("💬 WhatsApp bot running at http://127.0.0.1:5050/whatsapp")
# #     app.run(host="0.0.0.0", port=5050)

# # pip install flask twilio requests

# from flask import Flask, request
# from twilio.twiml.messaging_response import MessagingResponse
# from real_services import (
#     get_country_groups,
#     get_countries_by_group,
#     get_data_packages,
#     get_data_sizes_by_package,
#     get_price_for_plan
# )
# from payu import generate_payu_link

# app = Flask(__name__)
# USER_STATE = {}


# def send_message(resp, message, options=None):
#     """Helper: send numbered message options."""
#     if options:
#         options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
#         message += "\n\n" + options_text
#     resp.message(message)


# def parse_choice(text, options):
#     """Helper: convert numeric input into a list selection."""
#     if text.isdigit():
#         idx = int(text) - 1
#         if 0 <= idx < len(options):
#             return options[idx]
#     return None


# @app.route("/whatsapp", methods=["POST"])
# def whatsapp_webhook():
#     resp = MessagingResponse()
#     sender = request.values.get("From")
#     text = request.values.get("Body", "").strip()
#     state = USER_STATE.get(sender, {"step": "group"})

#     try:
#         if state["step"] == "group":
#             groups = get_country_groups()
#             send_message(resp, "🌍 Welcome to eSimNowAI!\nSelect your country group:", groups)
#             state["step"] = "group_pending"

#         elif state["step"] == "group_pending":
#             groups = get_country_groups()
#             choice = parse_choice(text, groups)
#             if not choice:
#                 send_message(resp, "⚠ Invalid. Enter the number of your choice.")
#             else:
#                 countries = get_countries_by_group(choice)
#                 country_names = [f"{c['flag']} {c['name']}" for c in countries[:10]]
#                 send_message(resp, f"Choose a country from {choice}:", country_names)
#                 state.update({"step": "country", "countries": countries})

#         elif state["step"] == "country":
#             countries = state["countries"]
#             choice = parse_choice(text, countries)
#             if choice:
#                 state["country"] = choice["name"]
#                 packages = get_data_packages()
#                 send_message(resp, f"🌎 {state['country']} selected.\nChoose package type:", packages)
#                 state["step"] = "package"
#             else:
#                 send_message(resp, "⚠ Invalid country number. Try again.")

#         elif state["step"] == "package":
#             packages = get_data_packages()
#             if text in packages:
#                 state["package"] = text
#                 sizes = get_data_sizes_by_package(state["country"], text)
#                 send_message(resp, f"Selected {text} package.\nChoose data size:", sizes)
#                 state["step"] = "data"
#             else:
#                 send_message(resp, "⚠ Invalid package. Try again.")

#         elif state["step"] == "data":
#             sizes = get_data_sizes_by_package(state["country"], state["package"])
#             if text in sizes:
#                 state["data"] = text
#                 price = get_price_for_plan(state["country"], text)

#                 if not price:
#                     send_message(resp, f"⚠ No valid price found for {state['country']} {text}.")
#                 else:
#                     payu_link = generate_payu_link(
#                         amount=float(price),
#                         productinfo=f"{text} eSim for {state['country']}",
#                         firstname="WhatsAppUser",
#                         email="user@example.com",
#                         phone=sender.replace("whatsapp:", "")
#                     )
#                     send_message(
#                         resp,
#                         f"You selected {text} for {state['country']}\n💰 Price: ₹{price}\n💳 Pay here: {payu_link}"
#                     )
#                     state["step"] = "done"
#             else:
#                 send_message(resp, "⚠ Invalid data size. Please try again.")

#         USER_STATE[sender] = state

#     except Exception as e:
#         print("[ERROR]", e)
#         resp.message("⚠ Something went wrong. Please try again later.")

#     return str(resp)


# if __name__ == "__main__":
#     print("💬 WhatsApp bot running at http://127.0.0.1:5050/whatsapp")
#     app.run(host="0.0.0.0", port=5050)

# ==========================================================
# 💬 WhatsApp Bot (Local Test + Live API Ready)
# ==========================================================
# 👉 pip install flask twilio requests
# Run locally:
#     python WhatsappBot.py
# Then test via Postman:
#     POST http://127.0.0.1:5050/whatsapp
#     Body: From=whatsapp:+911234567890 & Body=hi
# ==========================================================

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from real_services import (
    get_country_groups,
    get_countries_by_group,
    get_data_packages,
    get_data_sizes_by_package,
    get_price_for_plan,
)
from payu import generate_payu_link

app = Flask(__name__)
USER_STATE = {}  # Keeps track of user progress


# ---------------- HELPER FUNCTIONS ----------------
def send_message(resp, message, options=None):
    """Send a WhatsApp message (with numbered options if provided)"""
    if options:
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        message += "\n\n" + options_text
    resp.message(message)


def parse_choice(text, options):
    """Return selected option by number"""
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(options):
            return options[idx]
    return None


# ---------------- WEBHOOK HANDLER ----------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    resp = MessagingResponse()
    sender = request.values.get("From")
    text = request.values.get("Body", "").strip()
    state = USER_STATE.get(sender, {"step": "group"})

    try:
        # 🏁 STEP 1 — COUNTRY GROUP
        if state["step"] == "group":
            groups = get_country_groups()
            send_message(resp, "🌍 Welcome to eSimNowAI!\nChoose your country group:", groups)
            state["step"] = "group_pending"

        # 🌍 STEP 2 — SELECT COUNTRY GROUP
        elif state["step"] == "group_pending":
            groups = get_country_groups()
            choice = parse_choice(text, groups)
            if not choice:
                send_message(resp, "⚠ Invalid input. Enter the number of your country group.")
            else:
                countries = get_countries_by_group(choice)
                if not countries:
                    send_message(resp, "⚠ No countries found in this group.")
                else:
                    country_names = [f"{c['flag']} {c['name']}" for c in countries[:10]]
                    send_message(resp, f"🌎 Select your country from {choice}:", country_names)
                    state.update({"step": "country", "countries": countries})

        # 🇮🇳 STEP 3 — SELECT COUNTRY
        elif state["step"] == "country":
            countries = state.get("countries", [])
            choice = parse_choice(text, countries)
            if not choice:
                send_message(resp, "⚠ Invalid input. Please select a valid country.")
            else:
                state["country"] = choice["name"]
                packages = get_data_packages()
                send_message(resp, f"✅ Country selected: {state['country']}\nChoose your package:", packages)
                state["step"] = "package"

        # 📦 STEP 4 — PACKAGE TYPE
        elif state["step"] == "package":
            packages = get_data_packages()

            # ✅ Accept both numeric and text input (case-insensitive)
            choice = parse_choice(text, packages)  # check if user typed number (1, 2, 3)
            normalized_text = text.strip().capitalize()

            # If numeric input is valid, use it
            if choice:
                selected_package = choice
            # If typed text (e.g., "heavy" or "Medium") is valid, use it
            elif normalized_text in [p.capitalize() for p in packages]:
                selected_package = normalized_text
            else:
                send_message(
                    resp,
                    "⚠ Invalid package. Please type a number (1, 2, 3) or name (Minimal, Medium, Heavy)."
                )
                return str(resp)

            # ✅ Continue only if we have a valid package
            state["package"] = selected_package
            data_sizes = get_data_sizes_by_package(state["country"], selected_package)

            if not data_sizes:
                send_message(
                    resp,
                    f"⚠ No plans found for {state['country']} in {selected_package} range."
                )
            else:
                send_message(
                    resp,
                    f"📦 Selected *{selected_package}* package.\nChoose a data size for {state['country']}:",
                    data_sizes,
                )
                state["step"] = "data"

        # 📊 STEP 5 — DATA SIZE → PRICE + PAYMENT
        elif state["step"] == "data":
            data_sizes = get_data_sizes_by_package(state["country"], state["package"])
            choice = parse_choice(text, data_sizes)  # ✅ allows numeric input (1, 2, 3)
            
            if not choice:
                send_message(resp, "⚠ Invalid data size. Please select from the available options.")
            else:
                state["data"] = choice
                price = get_price_for_plan(state["country"], choice)

                if not price:
                    send_message(resp, f"⚠ No valid price found for {state['country']} {choice}. Try again.")
                else:
                    payu_link = generate_payu_link(
                        amount=float(price),
                        productinfo=f"{choice} eSim for {state['country']}",
                        firstname="WhatsAppUser",
                        email="user@example.com",
                        phone=sender.replace("whatsapp:", ""),
                    )
                    send_message(
                        resp,
                        f"💰 You selected {choice} for {state['country']}.\n"
                        f"Price: ₹{price}\n\nClick below to pay securely:\n{payu_link}",
                    )
                    state["step"] = "done"

        USER_STATE[sender] = state

    except Exception as e:
        print("[ERROR]", e)
        resp.message("⚠ Something went wrong. Please try again later.")

    return str(resp)


# ---------------- LOCAL SERVER ----------------
if __name__ == "__main__":
    print("💬 WhatsApp bot running locally at http://127.0.0.1:5050/whatsapp")
    app.run(host="0.0.0.0", port=5050)