import pandas as pd
import sys
import json
from durable.lang import *

# Load rules from Excel
rules_file = "/workspaces/Node-Red/rule2.xlsx"  # Ensure this file exists in the same directory
rules_df = pd.read_excel(rules_file)


def apply_discount(price):
    """
    Apply discount rules based on the price value.
    """
    for _, rule in rules_df.iterrows():
        operator = rule["Operator"]
        value = rule["value"]
        action_type = rule["Action Type"]
        action_value = rule["Action Value"]

        if operator == ">=" and price >= value:
            return {"action": action_type, "value": action_value}
        elif operator == "<" and price < value:
            return {"action": action_type, "value": action_value}
    
    return {"action": "No Discount", "value": "None"}

if __name__ == "__main__":
    try:
        # Ensure input is received
        if len(sys.argv) < 2:
            raise ValueError("No input provided")

        input_json = sys.argv[1].strip()
        
        # Ensure input is not empty
        if not input_json:
            raise ValueError("Empty JSON input received")

        # Parse JSON input
        input_data = json.loads(input_json)
        
        # Example: Just returning the same input for testing
        print(json.dumps({"received": input_data}))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON format"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

#$ curl -X POST http://localhost:1880/apply-discount -H "Content-Type: application/json" -d '{"price": 1500}'