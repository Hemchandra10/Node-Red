import pandas as pd
import sys
import json

# Load rules from Excel
rules = pd.read_excel("complex_rules2.xlsx")
rules = rules.to_dict(orient="records")

# Validate rules before processing
required_fields = ["Rule Name", "Condition", "Action Type", "Action Value", "Discount Type", "Discount Value"]

# Format condition for eval (replace with Python variables)
def format_condition(expr):
    expr = expr.strip()
    expr = expr.replace("AND", "and").replace("OR", "or")
    expr = expr.replace("days_since_last_refill", "data['days_since_last_refill']")
    expr = expr.replace("price", "data['price']")
    expr = expr.replace("medication", "data['medication']")
    expr = expr.replace("stage", "data['stage']")
    return expr

# Read JSON input safely
try:
    input_json = sys.argv[1]
    data = json.loads(input_json)
except (IndexError, json.JSONDecodeError) as e:
    print(json.dumps({"error": f"Invalid input: {e}"}))
    sys.exit(1)

# Extract input data
price = data.get("price")
medication = data.get("medication")
days_since_last_refill = data.get("days_since_last_refill")
stage = data.get("stage")
patient_id = data.get("patient_id")

# Process rules
results = []

for rule in rules:
    try:
        condition = format_condition(rule["Condition"])
        if eval(condition):
            action_type = rule["Action Type"]
            action_value = rule["Action Value"]
            discount_type = rule["Discount Type"]
            discount_value = rule["Discount Value"]

            if action_type == "Fact" and discount_type == "Discount":
                discount_price = price - (price * discount_value / 100)
                msg = f"Discount and Reminder : We have applied {discount_value}% discount on {medication}. New price is {discount_price}. Reminder to Patient {patient_id}, please refill {medication}."

            elif action_type == "Offer" and discount_type == "Discount":
                new_discount_price = price - (price * discount_value / 100)
                msg = f"More Discount and Resend reminder: {discount_value}% discount on {medication}. New price is {new_discount_price}. Resend reminder to Patient {patient_id}, please refill {medication}."

            elif action_type == "Escalate":
                msg = f"Escalation: Patient {patient_id} has not refilled {medication} for 50+ days. Contact required."

            else:
                msg = f"Unknown action type or discount type: {action_type} / {discount_type}"

            results.append({
                "rule_applied": rule["Rule Name"],
                "message": msg
            })

    except Exception as e:
        results.append({
            "rule_applied": rule.get("Rule Name", "Unknown"),
            "error": str(e)
        })

# Output results
print(json.dumps(results, indent=2))