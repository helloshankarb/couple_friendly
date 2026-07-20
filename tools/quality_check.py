import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('app/src/main/assets/flirt_dataset.json', encoding='utf-8') as f:
    data = json.load(f)

bad_words = ["dynamic", "catalog", "database", "certified", "dispatch",
             "coordinate", "premium", "alerts", "absolute", "priority alert",
             "mood catalog"]
cringe_patterns = [r"\bseductive mode\b", r"\bactivate\b", r"\bColgate model\b",
                   r"\bworkout aipothundi\b", r"\bmarry me energy\b"]

issues = []
total_replies = 0
emoji_missing = 0

for i, entry in enumerate(data):
    incoming = entry.get("incoming", "")
    for tone in ("romantic", "sweet", "funny", "bold"):
        replies = entry.get(tone, [])
        for j, reply in enumerate(replies):
            total_replies += 1
            # Check bad corporate words
            for bw in bad_words:
                if bw.lower() in reply.lower():
                    issues.append(f"[{i}][{tone}][{j}] CORPORATE WORD '{bw}': {reply[:60]}")
            # Check cringe patterns
            for cp in cringe_patterns:
                if re.search(cp, reply, re.I):
                    issues.append(f"[{i}][{tone}][{j}] CRINGE: {reply[:60]}")
            # Check pure English (no Telugu/Tanglish markers)
            telugu_markers = ["ga", "lo", "la", "ki", "ku", "ni", "na", "ne", "nee",
                              "bangaram", "bujji", "baby", "ra", "rey", "enti", "kadaa",
                              "le", "kaadu", "undhi", "avthunna", "chesthunna", "aipoya",
                              "chestha", "undi", "unna", "ledu", "avutundhi", "padthundi"]
            words = [re.sub(r'[^\w]', '', w) for w in reply.lower().split()]
            has_marker = any(m in words for m in telugu_markers)
            if not has_marker and len(words) > 5:
                issues.append(f"[{i}][{tone}][{j}] PURE ENGLISH: {reply[:70]}")
            # Check too short (under 4 words)
            if len([w for w in words if w]) < 4:
                issues.append(f"[{i}][{tone}][{j}] TOO SHORT: {reply}")
            # Check no emoji
            if not re.search(r'[\U00002600-\U000027BF\U0001F300-\U0001FAFF\U00002700-\U000027BF❤️💕😍😘🥰😏😂🤣🥺]', reply):
                emoji_missing += 1

print(f"Total entries: {len(data)}")
print(f"Total replies: {total_replies}")
print(f"Issues found: {len(issues)}")
print(f"Replies without emoji: {emoji_missing}")
print()
if issues:
    print("=== ISSUES ===")
    for iss in issues:
        print(" ", iss)
else:
    print("No issues found!")
