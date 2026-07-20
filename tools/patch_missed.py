import json, sys
sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = "app/src/main/assets/flirt_dataset.json"
with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

def fix(incoming_text, tone, index, new_line):
    for entry in data:
        if entry["incoming"] == incoming_text:
            entry[tone][index] = new_line
            print(f"  Fixed [{tone}][{index}] in '{incoming_text}'")
            return
    print(f"  WARN not found: {incoming_text}")

# Entry 3 "Em chesthunnav" funny[1] - too long/cringe
fix("Em chesthunnav", "funny", 1, "prapancham pause chesanu ne kosam only! 😂")

# Entry 8 "Sup" bad lines
fix("Sup", "romantic", 0, "Nuvvu unnav anduke manchi ga feel avthunna bujji! ❤️")
fix("Sup", "romantic", 3, "Ne kosam naa gunde endho full ga undhi bangaram! 💕")
fix("Sup", "bold",    3, "Ne presence tho energy level max avthundhi bangaram! 😏")

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Saved.")
