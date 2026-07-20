#!/usr/bin/env python3
import json
import pathlib
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    p1 = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset.json")
    p2 = pathlib.Path(r"e:/apps/couple_friendly/app/src/main/assets/flirt_dataset_fixed.json")
    
    if not p1.exists():
        print(f"Error: {p1} does not exist", file=sys.stderr)
        sys.exit(1)
    if not p2.exists():
        print(f"Error: {p2} does not exist", file=sys.stderr)
        sys.exit(1)
        
    d1 = json.loads(p1.read_text(encoding='utf-8-sig'))
    d2 = json.loads(p2.read_text(encoding='utf-8-sig'))
    
    print(f"flirt_dataset.json length: {len(d1)} entries")
    print(f"flirt_dataset_fixed.json length: {len(d2)} entries")
    
    diffs = []
    length_mismatches = 0
    incoming_mismatches = 0
    
    # We will compare up to the minimum length to avoid index errors
    min_len = min(len(d1), len(d2))
    
    for i in range(min_len):
        e1 = d1[i]
        e2 = d2[i]
        
        inc1 = e1.get("incoming", "")
        inc2 = e2.get("incoming", "")
        
        if inc1 != inc2:
            incoming_mismatches += 1
            diffs.append(f"Entry {i} Incoming Mismatch: dataset='{inc1}' vs dataset_fixed='{inc2}'")
            continue
            
        for tone in ["romantic", "sweet", "funny", "bold"]:
            r1 = e1.get(tone, [])
            r2 = e2.get(tone, [])
            
            if len(r1) != len(r2):
                length_mismatches += 1
                diffs.append(f"Entry {i} ('{inc1}') Tone '{tone}' Response Count Mismatch: dataset={len(r1)} vs dataset_fixed={len(r2)}")
                continue
                
            for j in range(len(r1)):
                rep1 = r1[j]
                rep2 = r2[j]
                
                if rep1 != rep2:
                    diffs.append({
                        "incoming": inc1,
                        "tone": tone,
                        "index": j,
                        "dataset": rep1,
                        "dataset_fixed": rep2
                    })
                    
    print(f"Total entries compared: {min_len}")
    print(f"Incoming mismatches: {incoming_mismatches}")
    print(f"Response list length mismatches: {length_mismatches}")
    
    # Separate string reports from detailed diff dicts
    list_mismatch_reports = [d for d in diffs if isinstance(d, str)]
    text_mismatches = [d for d in diffs if isinstance(d, dict)]
    
    print(f"Total individual text sentence differences: {len(text_mismatches)}")
    
    if list_mismatch_reports:
        print("\n--- Structural mismatches ---")
        for report in list_mismatch_reports[:10]:
            print(report)
            
    if text_mismatches:
        print("\n--- Sample sentence differences (dataset vs dataset_fixed) ---")
        # Print up to 40 differences to give a comprehensive view
        for idx, d in enumerate(text_mismatches[:40]):
            print(f"\n[{idx+1}] Incoming: '{d['incoming']}' | Tone: {d['tone']} | Index: {d['index']}")
            print(f"  dataset:       {d['dataset']}")
            print(f"  dataset_fixed: {d['dataset_fixed']}")

if __name__ == "__main__":
    main()
