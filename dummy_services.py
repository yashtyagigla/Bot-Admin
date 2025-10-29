# dummy_services.py
import random

COUNTRIES = [
    {"name": "Australia", "flag": "🇦🇺"},
    {"name": "Brazil", "flag": "🇧🇷"},
    {"name": "Canada", "flag": "🇨🇦"},
    {"name": "Denmark", "flag": "🇩🇰"},
    {"name": "Egypt", "flag": "🇪🇬"},
    {"name": "France", "flag": "🇫🇷"},
    {"name": "Germany", "flag": "🇩🇪"},
    {"name": "India", "flag": "🇮🇳"},
    {"name": "Japan", "flag": "🇯🇵"},
    {"name": "Kenya", "flag": "🇰🇪"},
    {"name": "Mexico", "flag": "🇲🇽"},
    {"name": "Norway", "flag": "🇳🇴"},
    {"name": "Peru", "flag": "🇵🇪"},
    {"name": "Qatar", "flag": "🇶🇦"},
    {"name": "Turkey", "flag": "🇹🇷"},
    {"name": "USA", "flag": "🇺🇸"},
    {"name": "Vietnam", "flag": "🇻🇳"},
    {"name": "Zimbabwe", "flag": "🇿🇼"},
]

DATA_PACKAGES = {
    "Minimal": ["1GB", "2GB", "3GB"],
    "Medium": ["5GB", "10GB", "20GB"],
    "Heavy": ["30GB", "50GB", "100GB"]
}

PLAN_PRICES = {
    "1GB": 300, "2GB": 500, "3GB": 700,
    "5GB": 1200, "10GB": 2200, "20GB": 4000,
    "30GB": 6000, "50GB": 9000, "100GB": 15000
}

# ---------------- DUMMY WEB SERVICES ----------------
def get_country_groups(user_id=None):
    """Return country groups, simulating a web service call"""
    # Simulate random failure
    if random.random() < 0.05:
        raise Exception("Service unavailable")
    return ["A-E", "F-J", "K-O", "P-T", "U-Z"]

def get_countries_by_group(group, user_selections=None):
    """Return list of countries for a given group"""
    if random.random() < 0.05:
        raise Exception("Service unavailable")
    groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}
    for c in COUNTRIES:
        first = c["name"][0].upper()
        if "A" <= first <= "E":
            groups["A-E"].append(c)
        elif "F" <= first <= "J":
            groups["F-J"].append(c)
        elif "K" <= first <= "O":
            groups["K-O"].append(c)
        elif "P" <= first <= "T":
            groups["P-T"].append(c)
        else:
            groups["U-Z"].append(c)
    return groups.get(group, [])

def get_data_packages(user_selections=None):
    """Return data package types"""
    if random.random() < 0.05:
        raise Exception("Service unavailable")
    return list(DATA_PACKAGES.keys())

def get_data_sizes(package_type, user_selections=None):
    """Return available data sizes for package type"""
    if random.random() < 0.05:
        raise Exception("Service unavailable")
    return DATA_PACKAGES.get(package_type, [])

def get_plan_price(data_size, user_selections=None):
    """Return price for selected plan"""
    if random.random() < 0.05:
        raise Exception("Service unavailable")
    return PLAN_PRICES.get(data_size, 0)
