import pandas as pd
import json

df = pd.read_excel("/workspaces/Node-Red/rule2.xlsx")

rules = df.to_dict(orient="records")

json_file = "rules2.json"

with open(json_file,'w') as f:
    json.dump(rules, f, indent=4)

print(f"rules saved to {json_file}")