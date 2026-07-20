import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('app/src/main/assets/flirt_dataset.json', encoding='utf-8') as f:
    data = json.load(f)

# Corporate/bad words that should never appear
bad_words = ["dynamic", "catalog", "database", "certified", "dispatch",
             "coordinate", "premium", "alerts", "absolute premium",
             "priority alert", "mood catalog"]
# Cringe activation patterns
cringe_patterns = [r"\bactivate\b", r"\bColgate model\b",
                   r"\bworkout aipothundi\b", r"\bmarry me energy\b",
                   r"\bseductive mode\b"]

issues = []
total_replies = 0

for i, entry in enumerate(data):
    for tone in ("romantic", "sweet", "funny", "bold"):
        replies = entry.get(tone, [])
        for j, reply in enumerate(replies):
            total_replies += 1
            # Corporate word check
            for bw in bad_words:
                if bw.lower() in reply.lower():
                    issues.append(f"[{i}][{tone}][{j}] CORPORATE '{bw}': {reply}")
            # Cringe check
            for cp in cringe_patterns:
                if re.search(cp, reply, re.I):
                    issues.append(f"[{i}][{tone}][{j}] CRINGE: {reply}")
            # Too short (under 4 actual words)
            words = [w for w in re.findall(r"[a-zA-Z0-9]+", reply) if len(w) > 1]
            if len(words) < 4:
                issues.append(f"[{i}][{tone}][{j}] TOO SHORT ({len(words)} words): {reply}")

print(f"Total entries: {len(data)}")
print(f"Total replies: {total_replies}")
print(f"Real issues found: {len(issues)}")
print()
if issues:
    print("=== REAL ISSUES ===")
    for iss in issues:
        print(" ", iss)
else:
    print("No real issues found!")
