import pandas as pd
import sys
import json

# Load rules from Excel
rules = pd.read_excel("adherence_rules.xlsx")
rules = rules.to_dict(orient="records")

# Format condition for eval (replace with Python variables)
def format_condition(expr):
    expr = expr.strip()
    expr = expr.replace("AND", "and").replace("OR", "or") 
    expr = expr.replace("days_since_last_refill", "data['days_since_last_refill']")
    expr = expr.replace("stage", "data['stage']")
    expr = expr.replace("price", "data['price]")
    expr = expr.replace("medication", "data['medication]")
    return expr

# Read JSON input safely
try:
    input_json = sys.argv[1]
    data = json.loads(input_json)
except (IndexError, json.JSONDecodeError) as e:
    print(json.dumps({"error": f"Invalid input: {e}"}))
    sys.exit(1)

price = data.get("price")
medication = data.get("medication")

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
                discount_price = price - (price * (discount_value/100))
                msg = f"Discount and Reminder : We have applied {discount_value}% discount on {data['medication']}, New price is {discount_price}. Reminder to Patient {data['patient_id']}, please refill {data['medication']}."

            elif action_type == "Offer" and discount_type == "Discount" :
                new_discount_price = price - (price * (discount_value/100))
                msg = f"More Discount and Resend reminder : We have applied {discount_value}% discount on {data['medication']}, New price is {new_discount_price}. Resend reminder to Patient {data['patient_id']}, please refill {data['medication']}"
            
            elif action_type == "Escalate":
                msg = f"Escalation: Patient {data['patient_id']} has not refilled {data['medication']} for 50+ days. Contact required."

            else:
                msg = f"Action: {action_type} - {action_value}"

            results.append({
                "rule_applied": rule["Rule Name"],
                "message": msg
            })

    except Exception as e:
        results.append({
            "rule_applied": rule["Rule Name"],
            "error": str(e)
        })

# Output results
print(json.dumps(results, indent=2))