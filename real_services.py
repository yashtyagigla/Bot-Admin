#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests

# ---------------- CONFIG ----------------
CACHE_FILE = "data_cache.json"
COUNTRY_API = "https://apiesim.connectingit.in/api/country/list"
PRODUCT_API = "https://apiesim.connectingit.in/api/product/get-all-product"

# ==========================================================
# 📦 PACKAGE RANGE LOGIC — with Unlimited pretty label
# ==========================================================

PACKAGE_RANGES = {
    "Minimal": (1, 9.999),   # 1GB to <10GB
    "Medium": (10, 19.999),  # 10GB to <20GB
    "Heavy": (20, 9999)      # 20GB and above (includes Unlimited)
}


def get_data_packages():
    """Return available package categories."""
    return list(PACKAGE_RANGES.keys())


def get_data_sizes_by_package(country_name, package_type):
    """
    Filter data sizes based on package type and include validity in label.
    'Heavy' also includes 'Unlimited' (data == 0 or name contains 'Unlimited').
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
        name = str(p.get("name", "")).lower()

        # 🌀 Handle Unlimited
        if package_type == "Heavy" and (data_val == "0" or "unlimited" in name):
            filtered.add(f"Unlimited Data 🌐 — {validity} Days")
            continue

        # 🧮 Skip non-numeric data values
        if not data_val.replace('.', '', 1).isdigit():
            continue

        gb = float(data_val)
        if min_gb <= gb < max_gb:
            filtered.add(f"{int(gb)}GB — {validity} Days")

    # Sort, keeping Unlimited last
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
# def load_data():
#     if os.path.exists(CACHE_FILE):
#         print("[CACHE] Loading data from cache...")
#         with open(CACHE_FILE) as f:
#             return json.load(f)
#     else:
#         return fetch_live_data()

import time

CACHE_FILE = "data_cache.json"
CACHE_EXPIRY_HOURS = 24  # Refresh every 24 hours

def load_data():
    """Load cache if recent; otherwise, fetch new API data."""
    if os.path.exists(CACHE_FILE):
        try:
            file_age_hours = (time.time() - os.path.getmtime(CACHE_FILE)) / 3600
            if file_age_hours < CACHE_EXPIRY_HOURS:
                print(f"[CACHE] Loading data from cache (age: {file_age_hours:.2f} hrs)...")
                with open(CACHE_FILE) as f:
                    return json.load(f)
            else:
                print("[CACHE ⚠️] Cache expired — refreshing live data...")
                return fetch_live_data()
        except Exception as e:
            print(f"[ERROR] Cache read failed: {e}, refetching...")
            return fetch_live_data()
    else:
        print("[CACHE] No cache file found — fetching fresh data...")
        return fetch_live_data()


# ---------------- COUNTRY GROUPS ----------------
def get_countries_by_group(group, page=1, per_page=10):
    """Return filtered unique countries from API or cache by alphabet group, with flags + pagination"""
    data = load_data().get("countries", [])
    groups = {"A-C": [], "D-F": [], "G-I": [], "J-L": [], "M-O": [], "P-R": [], "S-U": [], "V-Z": []}
    seen = set()

    # 🏳️ Prepare grouped country lists
    for c in data:
        name = c.get("countryName", "").strip()
        code = c.get("countryCode", "").upper()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        # 🌍 Generate flag emoji dynamically from ISO country code
        if len(code) == 2:
            flag = chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))
        else:
            flag = "🌍"

        first = name[:1].upper() if name else "Z"
        country_obj = {"name": name, "code": code, "flag": flag}

        if "A" <= first <= "C":
            groups["A-C"].append(country_obj)
        elif "D" <= first <= "F":
            groups["D-F"].append(country_obj)
        elif "G" <= first <= "I":
            groups["G-I"].append(country_obj)
        elif "J" <= first <= "L":
            groups["J-L"].append(country_obj)
        elif "M" <= first <= "O":
            groups["M-O"].append(country_obj)
        elif "P" <= first <= "R":
            groups["P-R"].append(country_obj)
        elif "S" <= first <= "U":
            groups["S-U"].append(country_obj)
        else:
            groups["V-Z"].append(country_obj)

    # 🧾 Pagination logic
    selected_group = groups.get(group, [])
    total = len(selected_group)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page

    paginated = selected_group[start:end]

    print(f"[DEBUG] get_countries_by_group({group}, page={page}) → {len(paginated)} shown / {total} total")
    return {"countries": paginated, "total_pages": total_pages}

def get_country_groups():
    """Return alphabetic country groups for selection buttons."""
    return ["A-C", "D-F", "G-I", "J-L", "M-O", "P-R", "S-U", "V-Z"]

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


# def get_data_sizes_by_package(country_name, package_type):
#     """
#     Filter data sizes based on package type and include validity in label.
#     'Heavy' also includes 'Unlimited' (data == 0) with pretty label.
#     """
#     plans = get_plans_by_country(country_name)
#     if not plans:
#         print(f"[WARN] No plans found for {country_name}")
#         return []

#     min_gb, max_gb = PACKAGE_RANGES.get(package_type, (0, 9999))
#     filtered = set()

#     for p in plans:
#         data_val = str(p.get("data", "")).replace("GB", "").strip()
#         validity = p.get("validity", "N/A")

#         # 🌀 Handle Unlimited plans (data == 0 or name contains 'Unlimited')
#         if package_type == "Heavy" and (data_val == "0" or "unlimited" in str(p.get("name", "")).lower()):
#             filtered.add(f"Unlimited Data 🌐 — {validity} Days")
#             continue

#         if not data_val.replace('.', '', 1).isdigit():
#             continue

#         gb = float(data_val)
#         if min_gb <= gb < max_gb:
#             filtered.add(f"{int(gb)}GB — {validity} Days")

#     # Sort with Unlimited at the end
#     result = sorted(
#         list(filtered),
#         key=lambda x: 9999 if "Unlimited" in x else int(x.split("GB")[0])
#     )

#     print(f"[INFO] {len(result)} plans found for {country_name} ({package_type}): {result}")
#     return result or ["1GB — 7 Days", "3GB — 15 Days", "5GB — 30 Days"]


def get_data_sizes_by_package(country_name, package_type):
    """
    Filter data sizes based on package type (Minimal, Medium, Heavy)
    and include Unlimited plans in Heavy (data == 0 or name contains 'unl'/'unlimited').
    If no plans found, show a user-friendly message.
    """
    plans = get_plans_by_country(country_name)
    if not plans:
        print(f"[WARN] No plans found for {country_name}")
        return [f"⚠️ No plans available for {country_name}. Please try another country."]

    min_gb, max_gb = PACKAGE_RANGES.get(package_type, (0, 9999))
    filtered = set()

    for p in plans:
        name = str(p.get("name", "")).lower()
        data_val = str(p.get("data", "")).strip().lower()
        validity = p.get("validity", "N/A")
        price = p.get("finalAmount") or p.get("price")

        # 🚫 Skip plans with invalid or zero price
        if not price or float(price) <= 0:
            continue

        # ✅ Detect Unlimited plans (more robust)
        if package_type == "Heavy" and (
            data_val in ["unlimited", "∞", "0"]
            or "unl" in name
            or "unlimited" in name
        ):
            filtered.add(f"Unlimited Data 🌐 — {validity} Days")
            continue

        # ✅ Detect numeric data sizes
        if data_val.replace('.', '', 1).isdigit():
            gb = float(data_val)
            if min_gb <= gb < max_gb:
                filtered.add(f"{int(gb)}GB — {validity} Days")

    if not filtered:
        print(f"[INFO] No valid {package_type} plans found for {country_name}")
        return [f"⚠️ No {package_type} plans available for {country_name}. Please try another category."]

    # ✅ Sort results — Unlimited always last
    result = sorted(
        list(filtered),
        key=lambda x: 9999 if "Unlimited" in x else int(x.split("GB")[0])
    )

    print(f"[INFO] {len(result)} valid plans found for {country_name} ({package_type}): {result}")
    return result