# # # #!/usr/bin/env python3
# # # # -*- coding: utf-8 -*-
# # # # # #pip install flask twilio

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
import re

# ---------- IMPORT YOUR EXISTING LOGIC ----------
from real_services import (
    get_country_groups,
    get_countries_by_group,
    get_data_packages,
    get_data_sizes_by_package,
    get_price_for_plan,
)
from payu import generate_payu_link
# ------------------------------------------------

app = Flask(__name__)
USER_STATE = {}

# ===============================================================
# 🧩 Helper: Send Twilio WhatsApp Response
# ===============================================================
def send_message(msg_text):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(msg_text)
    return str(resp)

# ===============================================================
# 🟢 Restart / Start Flow
# ===============================================================
def start_flow(from_number):
    USER_STATE[from_number] = {"step": "phone"}
    msg = (
        "🌍 *Welcome to eSimNowAI!*\n"
        "The world's largest eSIM store.\n\n"
        "Please reply with your *phone number* to continue:"
    )
    return send_message(msg)

# ===============================================================
# 🔄 WhatsApp Webhook Endpoint
# ===============================================================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip()
    state = USER_STATE.get(from_number, {})

    # 1️⃣ Start or restart
    if not state or re.match(r"^(hi|hello|start|restart|help|hey|yo|sup)$", body, re.I):
        return start_flow(from_number)

    # 2️⃣ Phone number
    if state.get("step") == "phone":
        phone = re.sub(r"\D", "", body)
        if len(phone) < 7:
            return send_message("⚠️ Please enter a valid phone number (digits only).")
        state["phone"] = "+" + phone
        state["step"] = "country_group"
        USER_STATE[from_number] = state

        groups = get_country_groups()
        msg = "🌎 *Please select your country group:*\n\n"
        msg += "\n".join([f"{i+1}. {g}" for i, g in enumerate(groups)])
        msg += "\n\n✏️ Reply with the *number* or *group name* (e.g., 1 or A-C)"
        return send_message(msg)

    # 3️⃣ Country group
    if state.get("step") == "country_group":
        groups = get_country_groups()
        choice = body.strip().upper()

        # Number or text
        if choice.isdigit() and 1 <= int(choice) <= len(groups):
            group = groups[int(choice) - 1]
        else:
            group = next((g for g in groups if g.upper() == choice), None)

        if not group:
            return send_message("⚠️ Invalid choice. Please reply with a valid number or group name.")

        state["country_group"] = group
        country_data = get_countries_by_group(group, page=1)
        countries = country_data["countries"]
        total_pages = country_data["total_pages"]

        state["countries"] = countries  # store for numeric reply
        state["step"] = "country"
        USER_STATE[from_number] = state

        msg = f"🌍 *Choose a country from {group}* (Page 1 of {total_pages}):\n\n"
        msg += "\n".join([f"{i+1}. {c.get('flag', '🌐')} {c['name']}" for i, c in enumerate(countries[:10])])
        msg += "\n\n✏️ Reply with the *number* or *country name*."
        return send_message(msg)

    # 4️⃣ Country
    if state.get("step") == "country":
        countries = state.get("countries", [])
        choice = body.strip().title()

        if choice.isdigit() and 1 <= int(choice) <= len(countries):
            country = countries[int(choice) - 1]["name"]
        else:
            match = next((c["name"] for c in countries if c["name"].lower() == choice.lower()), None)
            country = match or choice

        state["country"] = country
        state["step"] = "package"
        USER_STATE[from_number] = state

        packages = get_data_packages()
        msg = f"🌎 *{country}* selected.\n\nPlease select your *package type:*\n"
        msg += "\n".join([f"{i+1}. {p}" for i, p in enumerate(packages)])
        msg += "\n\n✏️ Reply with *number* or *package name*."
        return send_message(msg)

    # 5️⃣ Package
    if state.get("step") == "package":
        packages = get_data_packages()
        choice = body.strip()

        if choice.isdigit() and 1 <= int(choice) <= len(packages):
            package_type = packages[int(choice) - 1]
        else:
            package_type = next((p for p in packages if p.lower() == choice.lower()), None)

        if not package_type:
            return send_message("⚠️ Invalid package choice. Please reply with a valid number or name.")

        state["package_type"] = package_type
        data_sizes = get_data_sizes_by_package(state["country"], package_type)
        state["data_sizes"] = data_sizes
        state["step"] = "data"
        USER_STATE[from_number] = state

        msg = f"📦 *{package_type}* selected.\n\nPlease select your *data size:*\n"
        msg += "\n".join([f"{i+1}. {d}" for i, d in enumerate(data_sizes)])
        msg += "\n\n✏️ Reply with *number* or *data size name*."
        return send_message(msg)

    # 6️⃣ Data + Price
    if state.get("step") == "data":
        data_sizes = state.get("data_sizes", [])
        choice = body.strip()

        if choice.isdigit() and 1 <= int(choice) <= len(data_sizes):
            data_size = data_sizes[int(choice) - 1]
        else:
            data_size = next((d for d in data_sizes if d.lower() == choice.lower()), None)

        if not data_size:
            return send_message("⚠️ Invalid choice. Please reply with a valid number or data size name.")

        state["data"] = data_size
        price = get_price_for_plan(state["country"], data_size)
        if not price:
            return send_message(f"⚠️ No valid plan found for {state['country']} ({data_size}). Please try another.")

        state["price"] = price
        state["step"] = "passport"
        USER_STATE[from_number] = state

        msg = (
            f"You selected *{data_size}* for *{state['country']}*\n"
            f"💰 Price: ₹{price}\n\n"
            "📸 Please upload your *passport image* to continue.\n"
            "Send it as an *image*, not as a document."
        )
        return send_message(msg)

    # 7️⃣ Passport Upload Simulation
    if state.get("step") == "passport":
        plan_id = "N/A"
        try:
            resp = requests.get("https://apiesim.connectingit.in/api/product/get-all-product", timeout=30)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                target_country = state.get("country", "").lower().replace(" ", "")
                target_data = state.get("data", "").lower().replace(" ", "").replace("—", "-").replace("–", "-")
                for p in data:
                    name = str(p.get("name", "")).lower().replace(" ", "").replace("—", "-").replace("–", "-")
                    if target_country in name and target_data.split("-")[0] in name:
                        plan_id = p.get("localPlanId", "N/A")
                        break
        except Exception as e:
            print("[PlanID ERROR]", e)

        state["plan_id"] = plan_id
        state["step"] = "payment"
        USER_STATE[from_number] = state

        phone = state.get("phone", "N/A")
        country = state.get("country", "N/A")
        data_size = state.get("data", "N/A")
        price = state.get("price", "N/A")

        payu_link = generate_payu_link(
            amount=float(price),
            productinfo=f"{data_size} {country} eSIM",
            firstname="WhatsAppUser",
            email="user@example.com",
            phone=phone
        )

        msg = (
            f"✅ Image received successfully!\n\n"
            f"📋 *Order Summary:*\n"
            f"🌍 Country: *{country}*\n"
            f"📦 Package: *{data_size}*\n"
            f"💰 Price: ₹{price}\n"
            f"📱 Phone: {phone}\n"
            f"🆔 Plan ID: {plan_id}\n\n"
            f"Click below to pay securely:\n{payu_link}"
        )
        return send_message(msg)

    # 8️⃣ Fallback — restart flow if invalid
    return start_flow(from_number)

# ===============================================================
# 🚀 Run Flask
# ===============================================================
if __name__ == "__main__":
    print("🚀 WhatsApp Bot running on port 5050...")
    app.run(host="0.0.0.0", port=5050, debug=True)