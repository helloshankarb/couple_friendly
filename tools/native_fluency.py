#!/usr/bin/env python3
"""Deep investigation + native‑style cleanup for flirt_dataset.json.

This script performs the same checks as `fix_dataset.py` (BOM handling, broken
emoji replacement, whitespace normalisation) **and** applies a curated
"native‑Telugu" replacement map. The goal is to replace generic English slang
that Indian users (Andhra Pradesh / Telangana) would not type in a real
conversation with authentic Tanglish equivalents.

Typical replacements (you can extend the map as needed):
    "baby"   -> "babu"
    "hey"    -> "hey"   # keep but can be "hey" (common) – unchanged
    "lol"    -> "lol"   # keep as is – often used online
    "cute"   -> "cute"  # already natural
    "nice"   -> "nice"  # keep
    "cool"   -> "cool"  # keep
    "kiss"   -> "kiss"  # keep
    "love you" -> "love you" (kept because many use it) – you can replace with
                "nuvvu na heart" etc.
The map below contains the most common non‑native words we identified in the
current dataset. Feel free to add more entries.
"""
import json
import pathlib
import re
import sys

DATASET_PATH = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")

# ---------------------------------------------------------------------------
# 1️⃣ Unicode / emoji fixes (same as before)
BROKEN_EMOJI = {
    "â¤ï¸": "❤️",
    "â¤": "❤️",
    "â¤ï¸": "❤️",  # duplicate for safety
}

# 2️⃣ Simple typo / double‑space normalisation (extend as you discover)
TYPO_MAP = {
    "tapassu  chesthunna": "tapassu chesthunna",
    "tapassu  chesthunna!": "tapassu chesthunna!",
}

# 3️⃣ Native‑Telugu replacement map (English words → Tanglish equivalents)
NATIVE_MAP = {
    "baby": "babu",
    "hey": "hey",
    "lol": "lol",
    "nice": "nice",
    "cool": "cool",
    "kiss": "kiss",
    "love you": "love you",  # keep – many use it directly
    "sweet": "sweet",
    "awesome": "awesome",
    # add more specific replacements if you find them
}

# 4️⃣ Detect any Telugu script characters (U+0C00–U+0C7F) – should be none
TELUGU_REGEX = re.compile(r"[\u0C00-\u0C7F]")


def replace_native(text: str) -> str:
    """Replace English words with Telugu‑slang equivalents.
    The replacement is case‑insensitive and works on word boundaries.
    """
    for eng, telugu in NATIVE_MAP.items():
        # use regex to replace only full words, ignore case
        pattern = re.compile(rf"(?i)\b{re.escape(eng)}\b")
        text = pattern.sub(telugu, text)
    return text


def clean_reply(text: str) -> str:
    # a. Replace broken emojis
    for broken, good in BROKEN_EMOJI.items():
        if broken in text:
            text = text.replace(broken, good)
    # b. Apply typo map (simple substring replace)
    for bad, good in TYPO_MAP.items():
        if bad in text:
            text = text.replace(bad, good)
    # c. Apply native‑Telugu map
    text = replace_native(text)
    # d. Collapse any run of whitespace to a single space
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
                if new_reply != reply:
                    changes.append({
                        "incoming": incoming,
                        "tone": tone,
                        "old": reply,
                        "new": new_reply,
                    })
                # Detect any Telugu script characters (should be none)
                if TELUGU_REGEX.search(new_reply):
                    telugu_issues.append({"incoming": incoming, "tone": tone, "text": new_reply})
                cleaned.append(new_reply)
            entry[tone] = cleaned

    # Write back cleaned JSON (pretty printed, UTF‑8 without BOM)
    DATASET_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- Reporting ----
    print("=== Native‑style cleanup result ===")
    print(f"Total entries processed: {len(data)}")
    print(f"Total replies changed: {len(changes)}")
    # show first 20 changes for quick review
    for i, ch in enumerate(changes[:20]):
        print(f"[{i}] Incoming: {ch['incoming']} | Tone: {ch['tone']}")
        print(f"    old: {ch['old']}")
        print(f"    new: {ch['new']}\n")
    if telugu_issues:
        print("\n--- Telugu script detected (needs manual review) ---")
        for i, iss in enumerate(telugu_issues[:10]):
            print(f"[{i}] Incoming: {iss['incoming']} | Tone: {iss['tone']} -> {iss['text']}")
    else:
        print("No Telugu script characters found – all replies are Romanised.")

if __name__ == "__main__":
    main()
