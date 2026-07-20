#!/usr/bin/env python3
import json, re, pathlib, sys

DATASET_PATH = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")

# Map of broken emoji encodings to proper emojis
BROKEN_MAP = {
    "â¤ï¸": "❤️",
    "â¤": "❤️",
    "â¤ï¸": "❤️",  # duplicate entries – safe
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    "â¤ï¸": "❤️",
    # Add any other broken patterns you see in the file
}

def clean_text(text: str) -> str:
    # Replace broken emojis
    for broken, repl in BROKEN_MAP.items():
        if broken in text:
            text = text.replace(broken, repl)
    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}", file=sys.stderr)
        sys.exit(1)
    # Use utf-8-sig to automatically skip BOM if present
    raw = DATASET_PATH.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)
    changed = []
    for entry in data:
        for tone in ["romantic", "sweet", "funny", "bold"]:
            cleaned = []
            for reply in entry.get(tone, []):
                new_reply = clean_text(reply)
                if new_reply != reply:
                    changed.append({"incoming": entry.get("incoming"), "tone": tone, "old": reply, "new": new_reply})
                cleaned.append(new_reply)
            entry[tone] = cleaned
    # Write back pretty‑printed JSON without BOM
    DATASET_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Dataset cleaned – total entries: {len(data)}")
    print(f"Modifications applied: {len(changed)}")
    for i, ch in enumerate(changed[:10]):
        print(f"[{i}] Incoming: {ch['incoming']} | Tone: {ch['tone']}\n  old: {ch['old']}\n  new: {ch['new']}\n")

if __name__ == "__main__":
    main()
