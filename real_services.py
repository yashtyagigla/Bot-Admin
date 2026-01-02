import requests

BASE_API = "http://161.35.242.66:8000/products/db"

# ---------------- COUNTRY SEARCH (loose matching) ----------------
def search_countries(query):
    try:
        r = requests.get(BASE_API, timeout=20)
        products = r.json().get("data", [])
    except Exception as e:
        print("[API ERROR]", e)
        return []

    q = query.lower().strip()
    results = set()

    for p in products:
        for c in p.get("countries", []):
            name = c.get("country_name", "")
            if not name:
                continue

            name_l = name.lower()

            # loose + typo friendly
            if q in name_l or name_l.startswith(q):
                results.add(name)

    return sorted(results)

# ---------------- AVAILABLE DATA OPTIONS ----------------
def get_available_data_options(country, duration):
    try:
        r = requests.get(
            BASE_API,
            params={
                "country": country.lower(),
                "duration": int(duration)
            },
            timeout=20
        )

        if r.status_code != 200:
            return []

        products = r.json().get("data", [])
    except Exception as e:
        print("[API ERROR]", e)
        return []

    data_options = set()

    for p in products:
        data_val = p.get("data")
        if not data_val:
            continue

        if str(data_val).lower() == "unlimited":
            data_options.add("unlimited")
        else:
            data_options.add(str(data_val))

    # unlimited last me aaye, baaki ascending
    return sorted(
        data_options,
        key=lambda x: (x != "unlimited", float(x) if x.isdigit() else 9999)
    )


# ---------------- PLANS USING API PARAMS ----------------
def get_plans(country, duration, data_filter):
    try:
        r = requests.get(
            BASE_API,
            params={
                "country": country.lower(),
                "duration": int(duration)
            },
            timeout=20
        )
        products = r.json().get("data", [])
    except Exception as e:
        print("[API ERROR]", e)
        return []

    plans = []

    for p in products:
        raw_data = str(p.get("data")).lower()

        # ---- DATA FILTER ----
        if data_filter == "unlimited":
            if raw_data != "unlimited":
                continue
            data_label = "Unlimited"
        else:
            if raw_data == "unlimited":
                continue
            try:
                if float(raw_data) != float(data_filter):
                    continue
                data_label = f"{raw_data}GB"
            except:
                continue

        plans.append({
            "provider": p.get("provider", "Unknown"),
            "region": p.get("region", "N/A"),
            "data": data_label,
            "days": p.get("validity"),
            "usd": float(p.get("price", 0))
        })

    return plans