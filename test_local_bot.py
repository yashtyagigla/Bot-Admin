import sys
from real_services import (
    get_country_groups,
    get_countries_by_group,
    get_data_packages,
    get_data_sizes_by_package,
    get_price_for_plan
)

# ---------------- TEST LOGIC ----------------
country_name = sys.argv[1] if len(sys.argv) > 1 else "Thailand"

print(f"\n🧠 TEST: Starting full eSIM flow (LIVE API + Cached)\n")
groups = get_country_groups()
print("Available Groups:", groups)

# auto-detect alphabet group
first_letter = country_name[0].upper()
selected_group = None
for group in groups:
    if group[0] <= first_letter <= group[-1]:
        selected_group = group
        break

if not selected_group:
    print(f"⚠ Could not auto-detect group for {country_name}")
    sys.exit()

print(f"\n📍 Auto-detected group: {selected_group}")
countries = get_countries_by_group(selected_group)
match = next((c for c in countries if c["name"].lower() == country_name.lower()), None)

if not match:
    print(f"⚠ Country '{country_name}' not found in group {selected_group}.")
    sys.exit()

print(f"🌍 Selected country: {match['name']} ({match['code']})")

# Step 2: Test all package types one by one
packages = get_data_packages()
print(f"\nAvailable Packages: {packages}")

for package_type in packages:
    print(f"\n📦 Testing package type: {package_type}")
    data_sizes = get_data_sizes_by_package(match["name"], package_type)
    print(f"Available Data Sizes for {package_type}: {data_sizes}")

    if not data_sizes:
        continue

    selected_data = data_sizes[-1]  # pick the largest or Unlimited
    print(f"Selected data size: {selected_data}")

    # Step 3: Fetch price for selected data
    print("💰 Fetching live price...")
    price = get_price_for_plan(match["name"], selected_data.replace("🌐", "").split()[0])
    if price:
        print(f"✅ Price for {selected_data} in {match['name']}: ₹{price}")
    else:
        print(f"⚠ No valid price found for {selected_data} in {match['name']}")

print("\n✅ Local test complete!")