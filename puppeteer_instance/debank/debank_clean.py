import json
from collections import defaultdict

# Load original JSON
with open("debank_raw.json") as f:
    data = json.load(f)

def parse_usd(value):
    if isinstance(value, str):
        if "<$0.01" in value:
            return 0.0
        return float(value.replace("$", "").replace(",", "").strip())
    return float(value)

def parse_amount(value):
    if isinstance(value, str):
        value = value.replace(",", "").strip()
        try:
            return float(value.split()[0])
        except:
            return 0.0
    return float(value)

# Aggregate wallet tokens
wallets = defaultdict(lambda: {"Amount": 0.0, "USD Value": 0.0})
for item in data["wallets"]:
    token = item["Token"]
    wallets[token]["Amount"] += parse_amount(item["Amount"])
    wallets[token]["USD Value"] += parse_usd(item["USD Value"])

# Aggregate protocol tokens
protocols = defaultdict(lambda: {"Amount": 0.0, "USD Value": 0.0})
for item in data["protocols"]:
    token = item.get("Pool") or item.get("Supplied") or item.get("Rewards")
    if not token:
        continue
    usd_value = parse_usd(item.get("USD Value", "0"))
    if usd_value < 0.01:
        continue
    protocols[token]["Amount"] += parse_amount(item.get("Balance", "0"))
    protocols[token]["USD Value"] += usd_value

# Merge both sources
combined = defaultdict(lambda: {"Amount": 0.0, "USD Value": 0.0})
for token, info in wallets.items():
    if info["USD Value"] >= 1.0:
        combined[token]["Amount"] += info["Amount"]
        combined[token]["USD Value"] += info["USD Value"]

for token, info in protocols.items():
    if info["USD Value"] >= 1.0:
        combined[token]["Amount"] += info["Amount"]
        combined[token]["USD Value"] += info["USD Value"]

# Output cleaned data
cleaned_data = {
    "total_assets_usd": sum(v["USD Value"] for v in combined.values()),
    "tokens": [
        {
            "token": token,
            "amount": round(values["Amount"], 6),
            "usd_value": round(values["USD Value"], 2)
        }
        for token, values in sorted(combined.items(), key=lambda x: -x[1]["USD Value"])
    ],
    "timestamp": data["timestamp"]
}

# Save to cleaned_data.json
with open("debank_cleaned.json", "w") as outfile:
    json.dump(cleaned_data, outfile, indent=2)

print("✅ Cleaned data saved to cleaned_data.json")

