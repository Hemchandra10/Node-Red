import pandas as pd
import json
import sys

# Read rules from Excel
df = pd.read_excel("/workspaces/Node-Red/rule2.xlsx")
rules = df.to_dict(orient="records")

# Read input JSON
if len(sys.argv) < 2:
    print(json.dumps({"error": "No input provided"}))
    sys.exit(1)

try:
    input_data = json.loads(sys.argv[1])
except Exception as e:
    print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
    sys.exit(1)

price = input_data.get("price")
medication = input_data.get("medication")

# Evaluate rules
rules.sort(key=lambda r: float(r["Action Value"]) if r["Action Type"] == "Discount" else 0, reverse=True)

for rule in rules:
    condition = rule["Condition"]
    operator = rule["Operator"]
    value = rule["value"]
    action_type = rule["Action Type"]
    action_value = rule["Action Value"]

    # Simple check for price-based rules
    match = False
    if condition == "price":
        try:
            if operator == ">" and price > value:
                match = True
            elif operator == ">=" and price >= value:
                match = True
            elif operator == "<" and price < value:
                match = True
            elif operator == "<=" and price <= value:
                match = True
            elif operator == "==" and price == value:
                match = True
        except:
            continue

    if match:
        if action_type == "Discount":
            discounted_price = price * (1 - float(action_value) / 100.0)
            result = {
                "medication": medication,
                "original_price": price,
                "discount_applied_percent": float(action_value),
                "discounted_price": round(discounted_price, 2),
                "rule_applied": rule["Rule Name"]
            }
        else:
            result = {
                "medication": medication,
                "original_price": price,
                "message": "No Discount Applied",
                "rule_applied": rule["Rule Name"]
            }

        print(json.dumps(result))
        sys.exit(0)

# No rule matched
print(json.dumps({
    "medication": medication,
    "original_price": price,
    "message": "No matching rule found"
}))

#curl -X POST http://localhost:1880/apply-discount -H "Content-Type: application/json" -d '{"price": 2000, "medication": "MedX"}'