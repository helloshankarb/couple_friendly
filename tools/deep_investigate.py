#!/usr/bin/env python3
"""Deep investigation & native‑style cleanup for flirt_dataset.json.

- Removes stray UTF‑8‑BOM and broken emoji encodings.
- Collapses repeated whitespace ("  ") to a single space.
- Fixes a small dictionary of common spelling/typo patterns observed in the data.
- Flags any non‑Roman (Telugu) characters – these are printed for manual review.
- Writes the cleaned JSON back (pretty printed, UTF‑8 without BOM).
- Prints a concise change‑log (incoming message, tone, original → cleaned).
"""
import json, pathlib, re, sys

DATASET_PATH = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")

# ---------------------------------------------------------------------------
# 1️⃣  Unicode / emoji fixes
BROKEN_EMOJI = {
    "â¤ï¸": "❤️",
    "â¤": "❤️",
    "â¤ï¸": "❤️",  # duplicate for safety
}

# 2️⃣  Simple typo / double‑space normalisation
TYPO_MAP = {
    "tapassu  chesthunna": "tapassu chesthunna",  # double space -> single
    "tapassu  chesthunna!": "tapassu chesthunna!",
    "kattukuntundhi": "kattukuntundhi",  # placeholder – keep as‑is
    # Add more patterns as you discover them
}

# 3️⃣  Detect any Telugu script characters (U+0C00–U+0C7F)
TELUGU_REGEX = re.compile(r"[\u0C00-\u0C7F]")


def clean_reply(text: str) -> str:
    # a. Replace broken emojis
    for broken, good in BROKEN_EMOJI.items():
        if broken in text:
            text = text.replace(broken, good)
    # b. Apply typo map (simple substring replace)
    for bad, good in TYPO_MAP.items():
        if bad in text:
            text = text.replace(bad, good)
    # c. Collapse any run of whitespace to a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}", file=sys.stderr)
        sys.exit(1)
    raw = DATASET_PATH.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)

    changes = []
    telugu_issues = []
    for entry in data:
        incoming = entry.get("incoming", "<no incoming>")
        for tone in ["romantic", "sweet", "funny", "bold"]:
            cleaned = []
            for reply in entry.get(tone, []):
                new_reply = clean_reply(reply)
                # Record changes
                if new_reply != reply:
                    changes.append({
                        "incoming": incoming,
                        "tone": tone,
                        "old": reply,
                        "new": new_reply,
                    })
                # Detect Telugu script characters (just for reporting)
                if TELUGU_REGEX.search(new_reply):
                    telugu_issues.append({"incoming": incoming, "tone": tone, "text": new_reply})
                cleaned.append(new_reply)
            entry[tone] = cleaned

    # Write back cleaned JSON (pretty printed, no BOM)
    DATASET_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- Reporting ----
    print(f"=== Deep investigation result ===")
    print(f"Total entries processed: {len(data)}")
    print(f"Total replies changed: {len(changes)}")
    for i, ch in enumerate(changes[:20]):  # show first 20 changes
        print(f"[{i}] Incoming: {ch['incoming']} | Tone: {ch['tone']}")
        print(f"    old: {ch['old']}")
        print(f"    new: {ch['new']}")
    if telugu_issues:
        print("\n--- Telugu script detected (needs manual review) ---")
        for i, iss in enumerate(telugu_issues[:10]):
            print(f"[{i}] Incoming: {iss['incoming']} | Tone: {iss['tone']} -> {iss['text']}")
    else:
        print("No Telugu script characters found – all replies are Romanised.")

if __name__ == "__main__":
    main()
