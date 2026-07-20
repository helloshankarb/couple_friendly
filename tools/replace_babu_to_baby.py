#!/usr/bin/env python3
import json
import pathlib
import re
import sys

DATASET_PATH = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")

def replace_babu_to_baby(text: str) -> tuple[str, int]:
    """Replace babu with baby.
    Preserves case:
    - babu -> baby
    - Babu -> Baby
    - BABU -> BABY
    Returns the new text and count of replacements.
    """
    replacements = 0
    
    # Replace whole words only
    def repl_func(match):
        nonlocal replacements
        replacements += 1
        word = match.group(0)
        if word.isupper():
            return "BABY"
        elif word[0].isupper():
            return "Baby"
        else:
            return "baby"

    new_text = re.sub(r"\b[bB][aA][bB][uU]\b", repl_func, text)
    return new_text, replacements

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if not DATASET_PATH.exists():
        print(f"Error: Dataset file not found at {DATASET_PATH}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Reading dataset from: {DATASET_PATH}")
    raw_content = DATASET_PATH.read_text(encoding="utf-8-sig")
    
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)
        
    total_changes = 0
    modified_records = []
    
    for i, entry in enumerate(data):
        entry_changed = False
        old_entry = json.dumps(entry, ensure_ascii=False)
        
        for tone in ["romantic", "sweet", "funny", "bold"]:
            if tone in entry:
                new_replies = []
                for reply in entry[tone]:
                    new_reply, count = replace_babu_to_baby(reply)
                    if count > 0:
                        total_changes += count
                        entry_changed = True
                    new_replies.append(new_reply)
                entry[tone] = new_replies
                
        if entry_changed:
            modified_records.append({
                "index": i,
                "incoming": entry.get("incoming", ""),
                "old": old_entry,
                "new": json.dumps(entry, ensure_ascii=False)
            })

    # Write the modified JSON back
    output_content = json.dumps(data, ensure_ascii=False, indent=2)
    DATASET_PATH.write_text(output_content, encoding="utf-8")
    
    print(f"\nSuccessfully replaced 'babu' with 'baby'!")
    print(f"Total replacements made: {total_changes}")
    print(f"Total objects updated: {len(modified_records)}")
    
    # Write a quick summary log or print it
    print("\nSample modified replies:")
    for idx, change in enumerate(modified_records[:15]):
        print(f"\n[{idx+1}] Incoming trigger: '{change['incoming']}'")
        old_obj = json.loads(change['old'])
        new_obj = json.loads(change['new'])
        for tone in ["romantic", "sweet", "funny", "bold"]:
            if old_obj.get(tone) != new_obj.get(tone):
                print(f"  Tone ({tone}):")
                for r_old, r_new in zip(old_obj[tone], new_obj[tone]):
                    if r_old != r_new:
                        print(f"    Old: {r_old}")
                        print(f"    New: {r_new}")

if __name__ == "__main__":
    main()
