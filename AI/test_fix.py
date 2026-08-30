import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent / "text"))

from starter.text_verify import verify_text
import json

case1 = "HTML is a used to build frontend applicatations."
case2 = "nepal has heavy floods due to rain"

print("--- CASE 1 ---")
res1 = verify_text(case1)
print(json.dumps(res1, indent=2))

# print("\n--- CASE 2 ---")
# res2 = verify_text(case2)
# print(json.dumps(res2, indent=2))
