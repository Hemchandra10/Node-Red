# import pandas as pd
# import sys
# import json
# from durable.lang import *

# try:
#     # Load rules from Excel
#     rules_file = "/workspaces/Node-Red/rule2.xlsx"  # Ensure this file exists in the same directory
#     rules_df = pd.read_excel(rules_file)

#     print(rules_df.to_json(orient='records'))

# except Exception as e:
#     print({"error": str(e)})


import pandas as pd
import json
import sys

# Step 1: Read rules from Excel
rules_df = pd.read_excel("/workspaces/Node-Red/rule2.xlsx")
rules = rules_df.to_dict(orient="records")

# Step 2: Handle input JSON (from command-line argument)
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

# Step 3: Sort rules by best action value if discount
rules.sort(key=lambda r: float(r["Action Value"]) if r["Action Type"] == "Discount" else 0,reverse=True)

# Step 4: Apply the first matching rule
matched = False
for rule in rules:
    condition = rule["Condition"]
    operator = rule["Operator"]
    value = rule["value"]
    action_type = rule["Action Type"]
    action_value = float(rule["Action Value"])

    # Only handling simple condition: price [operator] value
    try:
        if condition == "price":
            if operator == ">" and price > value:
                matched = True
            elif operator == "<" and price < value:
                matched = True
            elif operator == "==" and price == value:
                matched = True
            elif operator == ">=" and price >= value:
                matched = True
    except:
        continue

    if matched:
        if action_type == "Discount":
            discounted_price = price - (price * (action_value/100))
            result = {
                "medication": medication,
                "original_price": price,
                "discount_applied": action_value,
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

# Step 5: No rule matched
print(json.dumps({"message": "No matching rule found", "medication": medication, "price": price}))