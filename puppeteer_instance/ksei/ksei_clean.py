import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_equity(data):
    return [
        {
            "type": "equity",
            "instrument": item["efek"],
            "quantity": item["jumlah"],
            "price": item["harga"],
            "investment_value": item["nilaiInvestasi"],
            "broker": item["partisipan"]
        }
        for item in data.get("data", [])
        if item["jumlah"] > 0
    ]

def extract_cash(data):
    return [
        {
            "type": "cash",
            "bank": item["bank"],
            "balance_idr": item["saldoIdr"]
        }
        for item in data.get("data", [])
        if item["saldoIdr"] > 0
    ]

def extract_bond(data):
    return [
        {
            "type": "bond",
            "instrument": item["efek"],
            "quantity": item["jumlah"],
            "price": item["harga"],
            "investment_value": item["nilaiInvestasi"],
            "broker": item["partisipan"]
        }
        for item in data.get("data", [])
        if item["jumlah"] > 0
    ]

def extract_mutual_fund(data):
    return [
        {
            "type": "mutual_fund",
            "instrument": item["efek"],
            "quantity": item["jumlah"],
            "price": item["harga"],
            "investment_value": item["nilaiInvestasi"],
            "broker": item["partisipan"]
        }
        for item in data.get("data", [])
        if item["jumlah"] > 0
    ]

# Load all JSON files
equity_data = load_json("ekuitas.json")
cash_data = load_json("kas.json")
# lainnya.json skipped
bond_data = load_json("obligasi.json")
mutual_fund_data = load_json("reksadana.json")

# Process and combine cleaned data
cleaned_data = (
    extract_equity(equity_data) +
    extract_cash(cash_data) +
    extract_bond(bond_data) +
    extract_mutual_fund(mutual_fund_data)
)

# Export to standardized JSON
with open("ksei_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("Exported cleaned and standardized data to ksei_cleaned.json")
