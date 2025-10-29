#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# import requests

# BASE_URL = "https://apiesim.connectingit.in/api"

# def get_country_groups(user_id=None):
#     """Group countries alphabetically A–E, F–J, etc."""
#     return ["A-E", "F-J", "K-O", "P-T", "U-Z"]


# def get_countries_by_group(group, user_selections=None):
#     """Fetch country list from live API and group them"""
#     try:
#         resp = requests.get(f"{BASE_URL}/country/list", timeout=10)
#         resp.raise_for_status()
#         data = resp.json().get("data", [])
#         groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}

#         for c in data:
#             name = c.get("countryName", "")
#             code = c.get("countryCode", "")
#             first = name[0].upper() if name else "Z"
#             flag = f"🇨🇮"  # generic fallback flag

#             # simple flag mapping (optional improvement)
#             if code:
#                 flag = chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))

#             country_obj = {"name": name, "code": code, "flag": flag}

#             if "A" <= first <= "E":
#                 groups["A-E"].append(country_obj)
#             elif "F" <= first <= "J":
#                 groups["F-J"].append(country_obj)
#             elif "K" <= first <= "O":
#                 groups["K-O"].append(country_obj)
#             elif "P" <= first <= "T":
#                 groups["P-T"].append(country_obj)
#             else:
#                 groups["U-Z"].append(country_obj)

#         return groups.get(group, [])
#     except Exception as e:
#         print(f"[ERROR] Fetch countries failed: {e}")
#         return []


# def get_data_packages(user_selections=None):
#     """Static package list"""
#     return ["Minimal", "Medium", "Heavy"]


# def get_data_sizes(package_type, user_selections=None):
#     """Static data size options"""
#     mapping = {
#         "Minimal": ["1GB", "2GB", "3GB"],
#         "Medium": ["5GB", "10GB", "20GB"],
#         "Heavy": ["30GB", "50GB", "100GB"]
#     }
#     return mapping.get(package_type, [])


# def get_plan_price(data_size, user_selections=None):
#     """Fetch price live from /api/product/get-all-product"""
#     try:
#         country = user_selections.get("country", "").lower()
#         resp = requests.get(f"{BASE_URL}/product/get-all-product", timeout=10)
#         resp.raise_for_status()
#         products = resp.json().get("data", [])

#         # Filter by country + data size
#         matches = [
#             p for p in products
#             if country in p.get("productName", "").lower()
#             and data_size.lower() in p.get("productName", "").lower()
#         ]

#         if matches:
#             p = matches[0]
#             return {
#                 "priceInr": float(p.get("priceInr", 0)),
#                 "priceUsd": float(p.get("priceUsd", 0)),
#                 "validity": p.get("validity", "N/A")
#             }

#         print(f"[WARN] No match found for {country} {data_size}")
#         return {"priceInr": 0, "priceUsd": 0, "validity": "N/A"}

#     except Exception as e:
#         print(f"[ERROR] Fetch plan price failed: {e}")
#         return {"priceInr": 0, "priceUsd": 0, "validity": "N/A"}

# real_services.py
# import requests
# import json
# import os

# COUNTRIES_URL = "https://apiesim.connectingit.in/api/country/list"
# PRODUCTS_URL = "https://apiesim.connectingit.in/api/product/get-all-product"
# CACHE_FILE = "data_cache.json"

# # ------------------- CACHE MANAGEMENT -------------------
# def load_cache():
#     """Load data from local JSON cache if available."""
#     if os.path.exists(CACHE_FILE):
#         with open(CACHE_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_cache(data):
#     """Save fresh data to cache."""
#     with open(CACHE_FILE, "w") as f:
#         json.dump(data, f, indent=2)

# # ------------------- FETCH LIVE DATA -------------------
# def fetch_live_data():
#     """Fetch countries and product data from live API and cache locally."""
#     print("[LIVE] Fetching countries and products...")
#     countries_res = requests.get(COUNTRIES_URL)
#     products_res = requests.get(PRODUCTS_URL)

#     countries_res.raise_for_status()
#     products_res.raise_for_status()

#     countries = countries_res.json().get("data", [])
#     products = products_res.json().get("data", [])

#     cache_data = {"countries": countries, "products": products}
#     save_cache(cache_data)
#     print(f"[CACHE] Saved {len(countries)} countries and {len(products)} products.")
#     return cache_data

# # ------------------- MAIN DATA ACCESS -------------------
# def get_data():
#     """Get combined data (use cache if possible)."""
#     try:
#         if os.path.exists(CACHE_FILE):
#             print("[CACHE] Loading data from cache...")
#             return load_cache()
#         else:
#             return fetch_live_data()
#     except Exception as e:
#         print(f"[ERROR] Failed to fetch or load data: {e}")
#         return load_cache()

# # ------------------- COUNTRY HANDLING -------------------
# def get_country_groups():
#     """Return 5 alphabetic country groups."""
#     return ["A-E", "F-J", "K-O", "P-T", "U-Z"]

# def get_countries_by_group(group):
#     """Group countries alphabetically."""
#     data = get_data()
#     countries = data.get("countries", [])
#     groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}

#     for c in countries:
#         name = c.get("countryName", "")
#         flag = "🌍"
#         first = name[0].upper() if name else ""
#         entry = {
#             "name": name,
#             "code": c.get("countryCode", ""),
#             "id": c.get("countryLocalId", ""),
#             "flag": flag
#         }
#         if "A" <= first <= "E":
#             groups["A-E"].append(entry)
#         elif "F" <= first <= "J":
#             groups["F-J"].append(entry)
#         elif "K" <= first <= "O":
#             groups["K-O"].append(entry)
#         elif "P" <= first <= "T":
#             groups["P-T"].append(entry)
#         else:
#             groups["U-Z"].append(entry)

#     return groups.get(group, [])

# # ------------------- PLANS & PRICE HANDLING -------------------
# def get_plans_by_country(country_name):
#     """Return all plans that match the given country name."""
#     data = load_cache()
#     if not data or "products" not in data:
#         print("[INFO] No cached plans found, fetching live data...")
#         data = fetch_and_cache_data()

#     matched = []
#     for plan in data["products"]:
#         countries = plan.get("countries") or []  # handle None safely
#         for c in countries:
#             if not isinstance(c, dict):
#                 continue
#             if country_name.lower() in c.get("countryName", "").lower():
#                 matched.append(plan)
#                 break  # avoid duplicate matches per plan

#     print(f"[DEBUG] get_plans_by_country({country_name}) → {len(matched)} plans found")
#     if matched:
#         sample_names = [p["name"] for p in matched[:5]]
#         print(f"[TRACE] Example plan names: {sample_names}")
#     else:
#         print(f"[WARN] No plans found for {country_name}")
#     return matched

# def get_available_data_sizes(country_name):
#     """Return unique data sizes available for a given country."""
#     plans = get_plans_by_country(country_name)
#     sizes = sorted({p.get("data", "N/A") for p in plans if p.get("data")})
#     return sizes or ["1GB", "3GB", "5GB"]

# def get_plan_price(country_name, data_size):
#     """Find a matching plan and return its finalAmount."""
#     plans = get_plans_by_country(country_name)
#     for p in plans:
#         if str(p.get("data", "")).strip() == str(data_size).replace("GB", "").strip():
#             return p.get("finalAmount", "N/A")
#     return "N/A"

# def get_price_for_plan(country_name, data_size):
#     """
#     Find price for given country and data size like '5GB'.
#     """
#     try:
#         print(f"[DEBUG] get_price_for_plan({country_name}, {data_size}) called")
#         plans = get_plans_by_country(country_name)
#         if not plans:
#             print(f"[WARN] No plans found for {country_name}")
#             return None

#         size_key = data_size.lower().replace(" ", "")
#         for plan in plans:
#             pname = str(plan.get("name", "")).lower().replace(" ", "")
#             if size_key in pname:
#                 price = plan.get("finalAmount") or plan.get("price") or "0"
#                 print(f"[MATCH ✅] Found plan: {plan.get('name')} → ₹{price}")
#                 return price

#         print(f"[WARN] No valid price found for {country_name} {data_size}")
#         return None
#     except Exception as e:
#         print(f"[ERROR] get_price_for_plan failed: {e}")
#         return None


import json
import os
import requests

# ---------------- CONFIG ----------------
CACHE_FILE = "data_cache.json"
COUNTRY_API = "https://apiesim.connectingit.in/api/country/list"
PRODUCT_API = "https://apiesim.connectingit.in/api/product/get-all-product"

# ---------------- PACKAGE RANGES ----------------
PACKAGE_RANGES = {
    "Minimal": (1, 9.999),    # up to but not including 10GB
    "Medium": (10, 19.999),
    "Heavy": (20, 9999)
}


def get_data_packages():
    """Return the available package categories."""
    return list(PACKAGE_RANGES.keys())


def get_data_sizes_by_package(country_name, package_type):
    """
    Filter data sizes based on package type and include validity in label.
    Only show plans that actually have a valid price.
    """
    plans = get_plans_by_country(country_name)
    if not plans:
        print(f"[WARN] No plans found for {country_name}")
        return []

    min_gb, max_gb = PACKAGE_RANGES.get(package_type, (0, 9999))
    filtered = set()

    for p in plans:
        data_val = str(p.get("data", "")).replace("GB", "").strip()
        validity = p.get("validity", "N/A")
        price = p.get("finalAmount") or p.get("price") or None

        # 🚫 Skip plans with no price
        if not price or float(price) <= 0:
            continue

        # 🌀 Handle Unlimited
        if package_type == "Heavy" and (data_val == "0" or "unlimited" in str(p.get("name", "")).lower()):
            filtered.add(f"Unlimited Data 🌐 — {validity} Days")
            continue

        # ✅ Normal numeric plans
        if not data_val.replace('.', '', 1).isdigit():
            continue
        gb = float(data_val)
        if min_gb <= gb < max_gb:
            filtered.add(f"{int(gb)}GB — {validity} Days")

    result = sorted(
        list(filtered),
        key=lambda x: 9999 if "Unlimited" in x else int(x.split("GB")[0])
    )

    print(f"[INFO] {len(result)} valid plans found for {country_name} ({package_type}): {result}")
    return result

# ---------------- FETCH LIVE DATA ----------------
def fetch_live_data():
    print("[LIVE] Fetching countries and products from API...")

    try:
        countries_response = requests.get(COUNTRY_API, timeout=30)
        products_response = requests.get(PRODUCT_API, timeout=60)

        countries = countries_response.json().get("data", [])
        products = products_response.json().get("data", [])

        cache = {"countries": countries, "products": products}
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

        print(f"[CACHE] ✅ Saved {len(countries)} countries and {len(products)} products.")
        return cache

    except Exception as e:
        print(f"[ERROR] Failed to fetch live data: {e}")
        return {"countries": [], "products": []}


# ---------------- LOAD OR FETCH CACHE ----------------
def load_data():
    if os.path.exists(CACHE_FILE):
        print("[CACHE] Loading data from cache...")
        with open(CACHE_FILE) as f:
            return json.load(f)
    else:
        return fetch_live_data()


# ---------------- COUNTRY GROUPS ----------------
def get_country_groups():
    """Alphabetically divide countries into groups"""
    return ["A-E", "F-J", "K-O", "P-T", "U-Z"]


def get_countries_by_group(group):
    """Return filtered unique countries from API or cache by alphabet group"""
    data = load_data().get("countries", [])
    groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}
    seen = set()  # ✅ track duplicate country names

    for c in data:
        name = c.get("countryName", "").strip()
        if not name or name.lower() in seen:
            continue  # skip duplicates
        seen.add(name.lower())

        flag = "🌍"
        first = name[:1].upper() if name else "Z"

        country_obj = {
            "name": name,
            "code": c.get("countryCode", ""),
            "flag": flag
        }

        if "A" <= first <= "E":
            groups["A-E"].append(country_obj)
        elif "F" <= first <= "J":
            groups["F-J"].append(country_obj)
        elif "K" <= first <= "O":
            groups["K-O"].append(country_obj)
        elif "P" <= first <= "T":
            groups["P-T"].append(country_obj)
        else:
            groups["U-Z"].append(country_obj)

    return groups.get(group, [])


# ---------------- PLAN FILTERING ----------------
def get_plans_by_country(country_name):
    """Return plans that match a given country name (case-insensitive)"""
    data = load_data()
    products = data.get("products", [])
    matched = []

    for p in products:
        for c in p.get("countries", []):
            if not c:
                continue
            cname = c.get("countryName", "").lower()
            if country_name.lower() in cname:
                matched.append(p)

    print(f"[DEBUG] get_plans_by_country({country_name}) → {len(matched)} plans found")
    if matched:
        sample_names = [p.get("name") for p in matched[:5]]
        print(f"[TRACE] Example plan names: {sample_names}")
    return matched


# ---------------- DATA SIZE EXTRACTION ----------------
def get_available_data_sizes(country_name):
    """Extract available unique data sizes (like 1GB, 5GB, etc.)"""
    plans = get_plans_by_country(country_name)
    sizes = set()

    for p in plans:
        data_val = str(p.get("data", "")).strip()
        if data_val.isdigit():
            sizes.add(f"{data_val}GB")

    sizes = sorted(list(sizes), key=lambda x: int(x.replace("GB", "")))
    return sizes or ["1GB", "3GB", "5GB"]


# ---------------- PRICE FETCH ----------------
def get_price_for_plan(country_name, data_size):
    """Return correct plan price — handles Unlimited and validity."""
    print(f"[DEBUG] get_price_for_plan({country_name}, {data_size}) called")
    plans = get_plans_by_country(country_name)
    if not plans:
        print(f"[WARN] No plans found for {country_name}")
        return None

    # 🧹 Normalize input (remove emojis, dashes, and extra words)
    clean_data = (
        str(data_size)
        .replace("🌐", "")
        .replace("—", "-")
        .replace("data", "")
        .replace("days", "")
        .replace("unlimited", "unlimited")
        .strip()
        .lower()
    )

    size_value = None
    validity_value = None

    parts = clean_data.split("-")
    if parts:
        size_part = parts[0].strip()
        if "gb" in size_part:
            size_value = size_part.replace("gb", "").strip()
        elif "unlimited" in size_part:
            size_value = "unlimited"

    # extract validity (if present)
    if len(parts) > 1:
        validity_value = "".join([ch for ch in parts[1] if ch.isdigit()])

    # 🔍 Look for matching plan
    for p in plans:
        plan_name = str(p.get("name", "")).lower()
        plan_data = str(p.get("data", "")).strip().lower()
        plan_validity = str(p.get("validity", "")).strip().lower()
        price = p.get("finalAmount") or p.get("price")

        # ✅ Unlimited match (covers both data=0 or “Unlimited”)
        if (
            size_value == "unlimited"
            and ("unlimited" in plan_name or plan_data == "0")
        ):
            print(f"[MATCH ✅] Found Unlimited plan: {p.get('name')} → ₹{price}")
            return price

        # ✅ Numeric data + validity match
        if size_value and plan_data == size_value:
            if not validity_value or validity_value == plan_validity:
                print(f"[MATCH ✅] Found plan: {p.get('name')} → ₹{price}")
                return price

    print(f"[WARN] No valid price found for {country_name} {data_size}")
    return None
# ==========================================================
# 📦 PACKAGE RANGE LOGIC — with Unlimited pretty label
# ==========================================================

PACKAGE_RANGES = {
    "Minimal": (1, 4.999),
    "Medium": (5, 19.999),
    "Heavy": (20, 9999)  # includes Unlimited (0GB)
}


def get_data_packages():
    """Return available package categories."""
    return list(PACKAGE_RANGES.keys())


def get_data_sizes_by_package(country_name, package_type):
    """
    Filter data sizes based on package type and include validity in label.
    'Heavy' also includes 'Unlimited' (data == 0) with pretty label.
    """
    plans = get_plans_by_country(country_name)
    if not plans:
        print(f"[WARN] No plans found for {country_name}")
        return []

    min_gb, max_gb = PACKAGE_RANGES.get(package_type, (0, 9999))
    filtered = set()

    for p in plans:
        data_val = str(p.get("data", "")).replace("GB", "").strip()
        validity = p.get("validity", "N/A")

        # 🌀 Handle Unlimited plans (data == 0 or name contains 'Unlimited')
        if package_type == "Heavy" and (data_val == "0" or "unlimited" in str(p.get("name", "")).lower()):
            filtered.add(f"Unlimited Data 🌐 — {validity} Days")
            continue

        if not data_val.replace('.', '', 1).isdigit():
            continue

        gb = float(data_val)
        if min_gb <= gb < max_gb:
            filtered.add(f"{int(gb)}GB — {validity} Days")

    # Sort with Unlimited at the end
    result = sorted(
        list(filtered),
        key=lambda x: 9999 if "Unlimited" in x else int(x.split("GB")[0])
    )

    print(f"[INFO] {len(result)} plans found for {country_name} ({package_type}): {result}")
    return result or ["1GB — 7 Days", "3GB — 15 Days", "5GB — 30 Days"]