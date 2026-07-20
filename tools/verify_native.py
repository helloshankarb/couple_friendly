#!/usr/bin/env python3
import json
import pathlib
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")
    
    if not p.exists():
        print(f"Error: {p} does not exist", file=sys.stderr)
        sys.exit(1)
        
    data = json.loads(p.read_text(encoding='utf-8-sig'))
    
    tests = [
        "tapassu chesthunna",
        "upiri pilchukovachu",
        "jeevitham loki",
        "navvu vastundhi",
        "khushi aipoyanu",
        "kalalu aa",
        "eduru chusano",
        "Customer care",
        "daachipettukunthunna"
    ]
    
    print("=== Verifying Native Telugu Phrasings in flirt_dataset.json ===")
    missing_count = 0
    for t in tests:
        found = False
        found_reply = ""
        for entry in data:
            for tone in ["romantic", "sweet", "funny", "bold"]:
                for reply in entry.get(tone, []):
                    if t.lower() in reply.lower():
                        found = True
                        found_reply = reply
                        break
                if found: break
            if found: break
        if found:
            print(f"[FOUND] '{t}' -> '{found_reply}'")
        else:
            print(f"[MISSING] '{t}'")
            missing_count += 1
            
    if missing_count == 0:
        print("\nAll native Telugu phrases are successfully verified and present in flirt_dataset.json!")
    else:
        print(f"\nWarning: {missing_count} phrases were not found. Please review.")

if __name__ == "__main__":
    main()
