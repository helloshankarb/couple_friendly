"""
Telugu Native Checker & Fixer for flirt_dataset.json
=====================================================
This script analyzes the entire dataset for non-native Telugu patterns
and flags/fixes sentences that sound too English or unnatural.

Rules for NATIVE Telugu (Roman script):
1. Use Telugu verbs: alochisthunna, gurtosthunnav, chaduvuthunna (NOT "think chesthunna")
2. Natural word order: Telugu SOV structure
3. Colloquial particles: le, kadaa, raa, ey, andi, mowa
4. Authentic terms: bujji, bangaram, baby, babu
5. Keep only English words that Telugu youth ACTUALLY use: cute, hot, miss, call, date, phone
6. Avoid literal English-to-Telugu translations like "Never ignore cheyanu"

Non-native patterns to detect:
- English_verb + "chesthunna/chestha/cheyanu" (e.g., "ignore cheyanu", "study chesthunna")
- "Never + Telugu" constructions (Never ignore, Never forget)
- Formal English phrases dropped directly (e.g., "You are my everything")
- Mixed grammar where English dominates sentence structure
"""

import json
import re
import sys
import io
from pathlib import Path
from collections import defaultdict

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# NON-NATIVE PATTERNS — English verbs that should be Telugu verbs
# ============================================================

# Pattern: "English_word + chesthunna/chestha/cheyanu/cheyyi/chesav" etc
ENGLISH_VERB_TELUGU_SUFFIX = re.compile(
    r'\b(study|ignore|change|prove|trust|survive|save|hire|cooking|'
    r'scroll|breathe|download|install|format|delete|upgrade|'
    r'remind|maintain|manage|handle|avoid|consider|achieve|'
    r'survive|imagine|realize|accept|adjust|convince|challenge|'
    r'explore|experience|experiment|appreciate|celebrate|'
    r'communicate|compensate|concentrate|contribute|coordinate|'
    r'dedicate|demonstrate|eliminate|evaluate|generate|'
    r'investigate|negotiate|participate|accommodate)\s+'
    r'(chesthunna|chestha|cheyanu|cheyyi|chesav|cheddama|chesthunnav|'
    r'cheyadam|chesindhi|chesthundi|chesukoni|chesukunta|chesestha)',
    re.IGNORECASE
)

# Pattern: "Never + Telugu verb" (English-first structure)
NEVER_TELUGU = re.compile(
    r'\bNever\s+\w+', re.IGNORECASE
)

# Pattern: English phrases that are too formal/literal
FORMAL_ENGLISH_PHRASES = [
    "You are my everything",
    "You mean everything",
    "that's my",
    "that's the",
    "beyond words",
    "means everything",
    "means a lot",
    "means so much",
    "of course",
    "obviously",
    "seriously",
    "literally",
    "forever and always",
    "to the moon and back",
    "each and every",
    "one and only",
    "no matter what",
]

# Words that should be in Telugu but are in English
SHOULD_BE_TELUGU = {
    "study": "chaduvuthunna / chaduvutunna",
    "ignore": "pattinchukoledu / okka msg kuda cheyaledu",
    "change": "maaripoyav / maaraledu",
    "forget": "marchipoyav / gurtuledu",
    "forgive": "maaf cheyyi / vadilesey",
    "survive": "brathakadam / brathakalekapothunna",
    "cooking": "vantachesthunna / vanta",
    "breathe": "oopiri / oopiraagatledu",
    "think": "alochisthunna / aalochana",
    "trust": "nammakam / nammaku",
    "promise": "maata isthunna",
    "prove": "chupista / nirupistha",
    "die": "sachipothanu / sastaanu",
    "try": "prayathnam / try chestha (ok in casual)",
    "feeling": "anipistundi / feel avthunna (ok casual)",
}

# Proper native alternatives for common non-native constructions
NATIVE_ALTERNATIVES = {
    "Never ignore cheyanu": "Eppatiki pattinchukokunda undanu / Nee msg miss cheyanu",
    "Study chesthunna": "Chaduvuthunna / Books mundu kurchunna",
    "Change ayyav": "Maaripoyav / Edho teda ga unnav",
    "Prove chestha": "Chupista / Nirupistha",
    "Trust cheyyi": "Nammu / Nammakam pettu",
    "Survive avvanu": "Brathakadam kashtam / Neelekunda undalekapothunna",
    "Cook chesthunna": "Vanta chesthunna",
    "Breathe chesthunna": "Oopiri theesukuntunna",
    "Save chesthunna": "Daachipettukunna / Save chestha (ok casual)",
    "Ignore chesthunnav": "Pattinchukuntlevu / Okka msg kuda cheyavu",
    "Remind chestha": "Gurtuchestha / Gnapakam chestha",
    "Forget avvaledu": "Gurtunde / Marchipoledu",
}


def load_dataset(path):
    """Load flirt_dataset.json"""
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def save_dataset(data, path):
    """Save modified dataset"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_sentence(sentence):
    """
    Analyze a single sentence for non-native Telugu patterns.
    Returns list of issues found.
    """
    issues = []
    
    # 1. Check English verb + Telugu suffix
    matches = ENGLISH_VERB_TELUGU_SUFFIX.findall(sentence)
    if matches:
        for eng_verb, tel_suffix in matches:
            issues.append({
                "type": "english_verb_telugu_suffix",
                "severity": "HIGH",
                "found": f"{eng_verb} {tel_suffix}",
                "suggestion": SHOULD_BE_TELUGU.get(eng_verb.lower(), f"Use native Telugu verb instead of '{eng_verb}'")
            })
    
    # 2. Check "Never + Telugu" patterns
    never_matches = NEVER_TELUGU.findall(sentence)
    if never_matches:
        for match in never_matches:
            issues.append({
                "type": "never_construction",
                "severity": "MEDIUM",
                "found": match,
                "suggestion": "Replace 'Never X' with 'Eppatiki X cheyanu' or native Telugu negation"
            })
    
    # 3. Check formal English phrases
    for phrase in FORMAL_ENGLISH_PHRASES:
        if phrase.lower() in sentence.lower():
            issues.append({
                "type": "formal_english",
                "severity": "LOW",
                "found": phrase,
                "suggestion": f"Replace '{phrase}' with natural Telugu equivalent"
            })
    
    # 4. Check for too many consecutive English words (5+ in a row that aren't common Telugu-youth words)
    # Remove emojis first for this check
    clean = re.sub(r'[^\w\s]', '', sentence)
    words = clean.split()
    consecutive_english = 0
    max_consecutive = 0
    # Words that Telugu youth naturally use in conversation (keep these)
    telugu_youth_english = {
        'bujji', 'bangaram', 'baby', 'raa', 'le', 'kadaa', 'aa', 'ey',
        'na', 'naa', 'ne', 'nee', 'nenu', 'nuvvu', 'enti', 'ippudu',
        'chala', 'chaalu', 'aithe', 'ante', 'inka', 'idi', 'adi',
        'chestha', 'chesthunna', 'avthundhi', 'undhi', 'unnav',
        'vastha', 'veltha', 'paduko', 'thinu', 'thaagu',
        'ga', 'lo', 'ki', 'ni', 'tho', 'meeda', 'nundi',
        'em', 'entha', 'ekkada', 'eppudu', 'evaru',
        'ok', 'okay', 'haha', 'aww', 'hmm', 'yay',
        # Common English that Telugu youth actually use in chat
        'miss', 'love', 'cute', 'hot', 'call', 'msg', 'phone',
        'date', 'plan', 'mood', 'feel', 'happy', 'sorry', 'please',
        'night', 'morning', 'hi', 'hello', 'hey', 'bye',
        'sweet', 'romantic', 'funny', 'bold', 'sexy', 'fire',
        'online', 'offline', 'reply', 'text', 'dm', 'chat',
        'photo', 'selfie', 'pic', 'video', 'reel', 'post',
        'gym', 'diet', 'coffee', 'tea', 'food', 'ice', 'cream',
        'friend', 'best', 'forever', 'always', 'never', 'promise',
        'trust', 'surprise', 'gift', 'treat', 'party',
        'drive', 'trip', 'beach', 'park', 'mall', 'shop',
        'song', 'movie', 'music', 'dance', 'Netflix',
        'stress', 'bore', 'tired', 'busy', 'free', 'chill',
        'serious', 'honest', 'really', 'actually', 'just',
        'too', 'same', 'more', 'first', 'next', 'last',
        'yes', 'no', 'done', 'sure', 'fine', 'cool',
    }
    for word in words:
        if re.match(r'^[a-zA-Z]+$', word) and word.lower() not in telugu_youth_english:
            consecutive_english += 1
            max_consecutive = max(max_consecutive, consecutive_english)
        else:
            consecutive_english = 0
    
    if max_consecutive >= 5:
        issues.append({
            "type": "too_much_english",
            "severity": "MEDIUM",
            "found": f"{max_consecutive} consecutive non-casual English words",
            "suggestion": "Break up with Telugu connectors or use Telugu equivalents"
        })
    
    return issues


def analyze_dataset(dataset):
    """
    Analyze entire dataset and return report.
    """
    report = {
        "total_entries": len(dataset),
        "total_sentences": 0,
        "flagged_sentences": 0,
        "issues_by_type": defaultdict(int),
        "issues_by_severity": defaultdict(int),
        "flagged_entries": []  # List of entries with issues
    }
    
    tones = ["romantic", "sweet", "funny", "bold"]
    
    for idx, entry in enumerate(dataset):
        entry_issues = []
        
        for tone in tones:
            if tone in entry:
                for sent_idx, sentence in enumerate(entry[tone]):
                    report["total_sentences"] += 1
                    issues = check_sentence(sentence)
                    
                    if issues:
                        report["flagged_sentences"] += 1
                        for issue in issues:
                            report["issues_by_type"][issue["type"]] += 1
                            report["issues_by_severity"][issue["severity"]] += 1
                            entry_issues.append({
                                "tone": tone,
                                "sentence_index": sent_idx,
                                "sentence": sentence,
                                "issue": issue
                            })
        
        if entry_issues:
            report["flagged_entries"].append({
                "index": idx,
                "incoming": entry["incoming"],
                "category": entry["category"],
                "issues": entry_issues
            })
    
    return report


def print_report(report):
    """Print a readable analysis report"""
    print("=" * 80)
    print("  TELUGU NATIVE QUALITY REPORT - flirt_dataset.json")
    print("=" * 80)
    print()
    print(f"  Total entries:      {report['total_entries']}")
    print(f"  Total sentences:    {report['total_sentences']}")
    print(f"  Flagged sentences:  {report['flagged_sentences']}")
    print(f"  Quality score:      {100 - (report['flagged_sentences'] / max(report['total_sentences'], 1) * 100):.1f}%")
    print()
    print("-" * 80)
    print("  ISSUES BY TYPE:")
    print("-" * 80)
    for issue_type, count in sorted(report["issues_by_type"].items(), key=lambda x: -x[1]):
        print(f"    {issue_type:<35} {count:>5} occurrences")
    print()
    print("-" * 80)
    print("  ISSUES BY SEVERITY:")
    print("-" * 80)
    for severity in ["HIGH", "MEDIUM", "LOW"]:
        count = report["issues_by_severity"].get(severity, 0)
        marker = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
        print(f"    {marker} {severity:<10} {count:>5} issues")
    print()
    print("=" * 80)
    print("  DETAILED FLAGGED ENTRIES (showing first 30)")
    print("=" * 80)
    
    shown = 0
    for entry in report["flagged_entries"]:
        if shown >= 30:
            remaining = len(report["flagged_entries"]) - 30
            print(f"\n  ... and {remaining} more entries with issues")
            break
        
        print(f"\n  Entry #{entry['index']+1}: \"{entry['incoming']}\" [{entry['category']}]")
        for issue_detail in entry["issues"][:3]:  # Max 3 issues per entry
            severity_icon = "🔴" if issue_detail["issue"]["severity"] == "HIGH" else "🟡" if issue_detail["issue"]["severity"] == "MEDIUM" else "🟢"
            print(f"    {severity_icon} [{issue_detail['tone']}] \"{issue_detail['sentence'][:60]}...\"")
            print(f"       Found: {issue_detail['issue']['found']}")
            print(f"       Fix:   {issue_detail['issue']['suggestion']}")
        shown += 1


def auto_fix_common_issues(dataset):
    """
    Auto-fix the most common non-native patterns.
    Returns fixed dataset + list of changes made.
    """
    changes = []
    tones = ["romantic", "sweet", "funny", "bold"]
    
    # Common replacements (pattern -> native replacement)
    auto_fixes = [
        # "Never X" at start → "Eppatiki X"
        (r'\bNever ignore cheyanu\b', 'Eppatiki pattinchukokunda undanu'),
        (r'\bNever forget\b', 'Eppatiki marchiponu'),
        (r'\bNever change\b', 'Eppatiki maariponu'),
        (r'\bNever break\b', 'Eppatiki break cheyanu'),
        (r'\bNever leave\b', 'Eppatiki vadilipettanu'),
        (r'\bNever alone\b', 'Okkadhannivi kaadu'),
        
        # "Study chesthunna" → "Chaduvuthunna"
        (r'\bStudy chesthunna\b', 'Chaduvuthunna'),
        (r'\bstudy chesthunna\b', 'chaduvuthunna'),
        
        # "Ignore chesthunnav" → "Pattinchukuntlevu"
        (r'\bIgnore chesthunnav\b', 'Pattinchukuntlevu'),
        (r'\bignore chesthunnav\b', 'pattinchukuntlevu'),
        
        # "Cooking chesthunna" → "Vanta chesthunna"
        (r'\bCooking chesthunna\b', 'Vanta chesthunna'),
        (r'\bcooking chesthunna\b', 'vanta chesthunna'),
        
        # "Survive avvanu" → "Brathakadam kashtam"
        (r'\bsurvive avvanu\b', 'brathakadam kashtam'),
        (r'\bSurvive avvanu\b', 'Brathakadam kashtam'),
        
        # "Breathing chesthunna" → "Oopiri theeskuntunna"  
        (r'\bBreathing chesthunna\b', 'Oopiri theeskuntunna'),
        
        # "You are my everything" → "Nuvvu naa sarvam"
        (r'\bYou are my everything\b', 'Nuvvu naa sarvam'),
        (r'\byou are my everything\b', 'nuvvu naa sarvam'),
        
        # "You mean everything to me" → "Nuvvu naaku sarvam"
        (r'\bYou mean everything to me\b', 'Nuvvu naaku anni'),
        
        # "Forever and always" → "Eppatiki eppudu"
        (r'\bForever and always\b', 'Eppatiki eppudu'),
        (r'\bforever and always\b', 'eppatiki eppudu'),
        
        # "Love you to the moon and back" → "Love chestha edo oka pichi level lo"
        (r'\bLove you to the moon and back\b', 'Chandamama daggara ki vellinantha ga love chestha'),
        
        # "I love you more" → "Nenu inka ekkuva love chestha"
        (r'\bI love you more\b', 'Nenu inka ekkuva prem chestha'),
    ]
    
    for idx, entry in enumerate(dataset):
        for tone in tones:
            if tone in entry:
                for sent_idx, sentence in enumerate(entry[tone]):
                    original = sentence
                    modified = sentence
                    
                    for pattern, replacement in auto_fixes:
                        modified = re.sub(pattern, replacement, modified)
                    
                    if modified != original:
                        dataset[idx][tone][sent_idx] = modified
                        changes.append({
                            "entry": idx,
                            "incoming": entry["incoming"],
                            "tone": tone,
                            "original": original,
                            "fixed": modified
                        })
    
    return dataset, changes


def main():
    # Path to dataset
    dataset_path = Path(__file__).parent.parent / "app" / "src" / "main" / "assets" / "flirt_dataset.json"
    
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        return
    
    print(f"Loading dataset from: {dataset_path}")
    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} entries\n")
    
    # Step 1: Analyze
    print("STEP 1: Analyzing for non-native patterns...\n")
    report = analyze_dataset(dataset)
    print_report(report)
    
    # Step 2: Auto-fix
    print("\n\n" + "=" * 80)
    print("  STEP 2: AUTO-FIXING common non-native patterns...")
    print("=" * 80)
    
    fixed_dataset, changes = auto_fix_common_issues(dataset)
    
    if changes:
        print(f"\n  ✅ Made {len(changes)} auto-fixes:\n")
        for change in changes[:20]:
            print(f"  Entry #{change['entry']+1} [{change['incoming']}] ({change['tone']}):")
            print(f"    ❌ {change['original'][:70]}")
            print(f"    ✅ {change['fixed'][:70]}")
            print()
        
        if len(changes) > 20:
            print(f"  ... and {len(changes) - 20} more fixes\n")
        
        # Save fixed version
        output_path = dataset_path.parent / "flirt_dataset_fixed.json"
        save_dataset(fixed_dataset, output_path)
        print(f"  💾 Saved fixed dataset to: {output_path}")
        print(f"     (Review and rename to flirt_dataset.json when satisfied)")
    else:
        print("\n  No auto-fixable issues found!")
    
    # Step 3: Re-analyze fixed version
    print("\n\n" + "=" * 80)
    print("  STEP 3: Re-analyzing after fixes...")
    print("=" * 80 + "\n")
    
    report_after = analyze_dataset(fixed_dataset)
    improvement = report["flagged_sentences"] - report_after["flagged_sentences"]
    print(f"  Before: {report['flagged_sentences']} flagged sentences")
    print(f"  After:  {report_after['flagged_sentences']} flagged sentences")
    print(f"  Fixed:  {improvement} sentences improved")
    print(f"  New quality score: {100 - (report_after['flagged_sentences'] / max(report_after['total_sentences'], 1) * 100):.1f}%")
    
    # Print remaining HIGH severity issues for manual review
    remaining_high = [
        e for e in report_after["flagged_entries"]
        if any(i["issue"]["severity"] == "HIGH" for i in e["issues"])
    ]
    if remaining_high:
        print(f"\n  ⚠️  {len(remaining_high)} entries still have HIGH severity issues (need manual fix):")
        for entry in remaining_high[:10]:
            print(f"    - Entry #{entry['index']+1}: \"{entry['incoming']}\"")
            for i in entry["issues"]:
                if i["issue"]["severity"] == "HIGH":
                    print(f"      {i['sentence'][:50]}... → {i['issue']['suggestion']}")


if __name__ == "__main__":
    main()
