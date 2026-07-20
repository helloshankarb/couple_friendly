"""
Powerful Telugu Native Fixer v2.0
---------------------------------
Context-aware replacement of English words/phrases with native Telugu equivalents.
Uses pattern matching (word + surrounding context) instead of blind replacement.

Categories:
1. English_word + Telugu_verb_suffix → native verb form
2. Common English phrases → native Telugu phrases
3. Sentence structure fixes (translated-sounding → natural)
4. English filler words → Telugu equivalents
"""

import json
import re
import sys
from collections import Counter

INPUT_FILE = 'app/src/main/assets/flirt_dataset.json'
OUTPUT_FILE = 'app/src/main/assets/flirt_dataset.json'

# ═══════════════════════════════════════════════════════════════════
# PATTERN RULES: (regex_pattern, replacement, description)
# These are context-aware — they match English words with surrounding Telugu context
# ═══════════════════════════════════════════════════════════════════

CONTEXT_PATTERNS = [
    # ─── SLEEP / NIDRA ───
    (r'\bsleep\s+(aavatle|raatle|raale|raaledhu|avvatle)', r'nidra \1', 'sleep→nidra before Telugu suffix'),
    (r'\bsleep\s+raadu', r'nidra raadu', 'sleep raadu→nidra raadu'),
    (r'\bsleep\s+pattale', r'nidra pattale', 'sleep pattale→nidra pattale'),
    (r'\bsleep\s+eppudu', r'nidra eppudu', 'sleep eppudu→nidra eppudu'),
    (r'\bSleep\s+eat', r'Nidra food', 'Sleep eat→Nidra food'),
    (r'\bsleep\b(?!\s+(tight|well|mode))', r'nidra', 'sleep→nidra generic'),
    
    # ─── SCROLLING → SCROLL CHESTHUNNA ───
    (r'\bscrolling\b', r'scroll chesthunna', 'scrolling→scroll chesthunna'),
    
    # ─── TASTE / RUCHI ───
    (r'\btaste\s+(ochindhi|vasthundhi|chesth|cheyy|test)', r'ruchi \1', 'taste→ruchi'),
    (r'\btaste\b', r'ruchi', 'taste→ruchi generic'),
    (r'\bTaste\b', r'Ruchi', 'Taste→Ruchi'),
    
    # ─── WAIT / EDURU CHOOSTUNNA ───
    (r'\bwait\s+chesth(unna|unnav|anu)', r'eduru choosth\1', 'wait chesthunna→eduru choostunna'),
    (r'\bwait\s+chese\b', r'eduru choose', 'wait chese→eduru choose'),
    (r'\bwait\s+cheyy', r'eduru choos', 'wait cheyy→eduru choos'),
    (r'[Cc]an\'t\s+wait', r'Aagalekapothunna', "can't wait→aagalekapothunna"),
    (r'\bwaiting\b', r'eduru choostunna', 'waiting→eduru choostunna'),
    
    # ─── THINK / AALOCHISTHUNNA ───  
    (r'\bthink\s+chesth(unna|unnav|undi)', r'aalochisth\1', 'think chesthunna→aalochisthunna'),
    (r'\bthink\b(?!\s+(tank|pad))', r'aalochinchu', 'think→aalochinchu'),
    (r'\bthinking\b', r'aalochisthunna', 'thinking→aalochisthunna'),
    
    # ─── SMILE / NAVVU ───
    (r'\bsmile\s+(vasthundhi|ochindhi|automatic|istundhi)', r'navvu \1', 'smile→navvu'),
    (r'\bsmile\s+oohinchukunth', r'navvu oohinchukunth', 'smile→navvu'),
    (r'\bsmile\b(?!\s+emoji)', r'navvu', 'smile→navvu'),
    (r'\bsmiling\b', r'navvuthunna', 'smiling→navvuthunna'),
    
    # ─── DREAM / KALALU ───
    (r'\bdream\s+come\s+true', r'kalalu nijam', 'dream come true→kalalu nijam'),
    (r'\bdream\s+(chesth|chesthunna|vasth|ochindhi|loki)', r'kalalu \1', 'dream→kalalu'),
    (r'\bDream\s+come\s+true', r'Kalalu nijam', 'Dream come true→Kalalu nijam'),
    (r'\bdream\b(?!\s+(team|date|plan))', r'kalalu', 'dream→kalalu'),
    
    # ─── WORRY / TENSION ───
    (r'\bworry\s+chey(aku|akandi|yaku)', r'tension pad\1', 'worry cheyaku→tension padaku'),
    (r'\b[Dd]on\'t\s+worry', r'Tension padaku', "don't worry→tension padaku"),
    (r'\bWorry\s+cheyaku', r'Tension padaku', 'Worry cheyaku→Tension padaku'),
    (r'\bworry\b', r'tension', 'worry→tension'),
    
    # ─── IGNORE / PATTINCHUKOLEDU ───
    (r'\bignore\s+chesth(e|unna|unnav)', r'pattinchukokund\1', 'ignore chesthe→pattinchukokunte'),
    (r'\bignore\s+chey(aku|yaku)', r'pattinchukokunda undaku', 'ignore cheyaku→pattinchukokunda undaku'),
    (r'\bIgnore\s+kaadu', r'Pattinchukoledu kaadu', 'Ignore kaadu→Pattinchukoledu kaadu'),
    (r'\bignore\b(?!\s+impossible)', r'pattinchukokunda', 'ignore→pattinchukokunda'),
    
    # ─── FORGET / MARCHIPOVU ───
    (r'\bforget\s+(raadu|raaledhu|avvadhu)', r'marchipovadhu', 'forget raadu→marchipovadhu'),
    (r'\bforget\b', r'marchipovu', 'forget→marchipovu'),
    
    # ─── HEART / GUNDE ───
    (r'\bheart\s+(melting|happy|sad|full|lo)', r'gunde \1', 'heart→gunde'),
    (r'\bheart\b(?!\s+(emoji|attack|king))', r'gunde', 'heart→gunde'),
    
    # ─── WORLD / PRAPANCHAM ───
    (r'\bworld\s+(lo|ni|chesav|ki|ante)', r'prapancham \1', 'world→prapancham'),
    (r'\bentire\s+world', r'moththam prapancham', 'entire world→moththam prapancham'),
    (r'my\s+world', r'naa prapancham', 'my world→naa prapancham'),
    
    # ─── LIFE / JEEVITHAM ───
    (r'\blife\s+(lo|loki|ki|ni|aithey|ante|full)', r'jeevitham \1', 'life→jeevitham'),
    (r'\blife\b(?!\s+(hack|style|partner|goal))', r'jeevitham', 'life→jeevitham'),
    
    # ─── TOGETHER / KALISI ───
    (r'\btogether\s+(thindaam|cheddaam|undaam|cheskundaam|plan)', r'kalisi \1', 'together→kalisi'),
    (r'\btogether\b(?!\s+goal)', r'kalisi', 'together→kalisi'),
    
    # ─── HAPPY / KHUSHI ───
    (r'\bhappy\s+aipoy(anu|indhi|av|aam)', r'khushi aipoy\1', 'happy→khushi'),
    (r'\bhappy\b(?!\s+(birthday|meal|ending))', r'khushi', 'happy→khushi'),
    
    # ─── CLOSE / DAGGARA ───
    (r'\bclose\s+(ga|lo|ki|undaali|raa)', r'daggara \1', 'close→daggara'),
    (r'\bclose\b(?!\s+(chesth|cheyy|door|eyes))', r'daggara', 'close→daggara'),
    
    # ─── SAD / BAADHA ───
    (r'\bsad\s+(aipoy|avth|ga|feel)', r'baadha \1', 'sad→baadha'),
    (r'\bsad\b', r'baadha', 'sad→baadha'),
    
    # ─── ANGRY / KOPAM ───
    (r'\bangry\s+(aipo|avth|ga|bird)', r'kopam \1', 'angry→kopam'),
    
    # ─── CARE / PATTANA ───
    (r'\bcare\s+chesth(unna|unnav|anu)', r'choosukunth\1', 'care chesthunna→choosukunthunna'),
    (r'\bcare\b(?!\s+taker)', r'choosukuntha', 'care→choosukuntha'),
    
    # ─── STRONG / DHAIRYAM ───
    (r'\bstrong\s+(ga|avvu|undhi)', r'dhairyam ga', 'strong→dhairyam'),
    (r'\bstrong\b', r'dhairyam ga', 'strong→dhairyam ga'),
    
    # ─── LUCK / ADRUSHTAM ───
    (r'\bluck\s+(ne|naa|ki|tho)', r'adrushtam \1', 'luck→adrushtam'),
    (r'\blucky\s+(feel|charm|ga)', r'adrushtam \1', 'lucky→adrushtam'),
    (r'\bBest\s+of\s+luck', r'All the best', 'Best of luck→All the best (common in Telugu)'),
    
    # ─── COMPLETE / POORTHI ───
    (r'\bcomplete\s+(aipo|chesth|avth|ga)', r'poorthi \1', 'complete→poorthi'),
    (r'\bcomplete\b', r'poorthi', 'complete→poorthi'),
    
    # ─── PERFECT / SARIPOINDI ───
    (r'\bperfect\s+set', r'saripoinda set', 'perfect set→saripoinda set'),
    
    # ─── START / MODALU ───
    (r'\bstart\s+(chesth|cheyy|avth|aipoy)', r'modalu \1', 'start→modalu'),
    (r'\bstart\b(?!\s+(soon|panelu))', r'modalu', 'start→modalu'),
    
    # ─── ENGLISH FILLER ADVERBS ───
    (r'\bseriously\b', r'nijam ga', 'seriously→nijam ga'),
    (r'\bcompletely\b', r'purthi ga', 'completely→purthi ga'),
    
    # ─── MISS / GURTHU VASTHUNNAV ───
    (r'\bmiss\s+ches(anu|indhi|aam)', r'gurthu vasthunnav', 'miss chesanu→gurthu vasthunnav'),
    (r'\bmiss\s+chesav', r'gurthu ochindha', 'miss chesav→gurthu ochindha'),
    (r'\bmiss\s+chesth(unna|unnav)', r'gurthu vasth\1v', 'miss chesthunna→gurthu vasthunnav'),
    (r'\bmiss\s+chestha\b', r'gurthu vasthundhi', 'miss chestha→gurthu vasthundhi'),
    
    # ─── GELCHAV / GADIPAV ───
    (r'\bgelch(av|anu|indhi)', r'gadip\1', 'gelchav→gadipav (spent/passed day)'),
    
    # ─── CREATE CHESTHA / SAMAYAM CHESKUNTA ───
    (r'\bcreate\s+chesth(a|unna|unnav)', r'samayam cheskunth\1', 'create chestha→samayam cheskunta'),
    (r'\bcreate\s+cheyy', r'samayam cheskune', 'create cheyy→samayam cheskune'),
    
    # ─── PRESERVE / DAACHI PETTUKUNTHA ───
    (r'\bpreserve\s+chesth(a|unna)', r'daachi pettukunth\1', 'preserve chestha→daachi pettukuntha'),
    
    # ─── NOTICE / GAMANINCHU ───
    (r'\bnotice\s+ches(av|anu|indhi)', r'gamanинch\1', 'notice chesav→gamaninchav'),
    
    # ─── DISTURB / ALOCHANALU ───
    (r'\bdisturb\s+chesth(unnai|unna|undhi)', r'icharagaa vasth\1', 'disturb chesthunnai→vasthunnai'),
    
    # ─── COMMON NON-NATIVE PHRASES ───
    (r'you are my entire', r'nuvvu naa moththam', 'you are my entire→nuvvu naa moththam'),
    (r'You are my', r'Nuvve naa', 'You are my→Nuvve naa'),
    (r'you are my', r'nuvve naa', 'you are my→nuvve naa'),
    (r'\bI miss you\b', r'Ne leni lotu bharinchaleka', 'I miss you→ne leni lotu'),
    (r'\bmiss you\b', r'ne leni lotu', 'miss you→ne leni lotu'),
    (r'\bmiss avthunna\b', r'gurthu vasthunnav', 'miss avthunna→gurthu vasthunnav'),
]

# ═══════════════════════════════════════════════════════════════════
# FULL SENTENCE REPLACEMENTS (for sentences that need complete restructuring)
# ═══════════════════════════════════════════════════════════════════

SENTENCE_FIXES = {
    # sleep patterns
    "Ha bujji sleep aavatle scrolling!": "Ha bujji nidra ravatle scroll chesthunna ala!",
    "10 PM ki coffee taguthav sleep eppudu?": "10 PM ki coffee taguthav nidra eppudu?",
    "Sleep eat repeat ade plan bujji!": "Nidra food repeat ade plan bujji!",
    "Ne kosam jaaguthunna bangaram sleep raadu!": "Ne kosam jaaguthunna bangaram nidra raadu!",
    
    # taste patterns
    "Chivariki taste ochindhi nee ki good bujji": "Chivariki ruchi telisindhi nee ki manchidhi bujji",
    "Can't wait to taste excited!": "Aagalekapothunna ruchi chooseddaam excited!",
    "Taste test willing brave soul!": "Ruchi test ki ready brave soul!",
    
    # non-native sentence structures
    "Nuvvu nacchinadhi naa adrushtam bangaram!": "Nacchav kaadu love aipoya baby!",
    "Same bangaram you are my entire world!": "Same bangaram nuvve naa moththam lokam!",
    
    # wait patterns
    "Ee hello kosam entha wait chesano telusa bujji?": "Ee hello kosam entha eduru chesano telusa bujji?",
    "Nuvvu msg chese varaku ne kosam wait chesthunna bangaram!": "Nuvvu msg chese varaku ne kosam eduru choostunna bangaram!",
    "Nothing much bujji ne msg kosam wait chesthunna!": "Nothing much bujji ne msg kosam eduru choostunna!",
    
    # think patterns  
    "Ne gurinchi think chesthunna nijam ga!": "Ne gurinchi aalochisthunna nijam ga!",
    "Ne gurinchi think chesthunna wild ga!": "Ne gurinchi aalochisthunna wild ga!",
    "Cute nenu kuda ne gurinche think!": "Cute nenu kuda ne gurinche aalochisthunna!",
    
    # worry patterns
    "Office work related don't worry bujji!": "Office work related tension padaku bujji!",
    "Just friend don't worry bujji!": "Just friend tension padaku bujji!",
    "Worry cheyaku ne di ne baby!": "Tension padaku ne di ne baby!",
    
    # smile patterns
    "Ne msg vasthe automatic ga smile vastundhi bangaram!": "Ne msg vasthe automatic ga navvu vastundhi bangaram!",
    "Ne hey vinagane na face lo smile automatic!": "Ne hey vinagane na face lo navvu automatic!",
    "Morning ne smile oohinchukunthunna ikkada!": "Morning ne navvu oohinchukunthunna ikkada!",
    
    # dream patterns
    "Dream come true aipoyindhi naa di!": "Kalalu nijam aipoyindhi naa di!",
    "Movie date naa dream chivariki baby!": "Movie date naa kalalu chivariki baby!",
    
    # heart patterns
    "Ne hey ki heart happy aipoyindhi bangaram!": "Ne hey ki gunde khushi aipoyindhi bangaram!",
    "Em cute bangaram heart melting!": "Em cute bangaram gunde karigipothundhi!",
    
    # ignore patterns
    "Nuvvu naa priority bujji ignore impossible!": "Nuvvu naa priority bujji pattinchukokunda undadam impossible!",
    "Ignore kaadu multitasking fail aindhi!": "Pattinchukoledu kaadu multitasking fail aindhi!",
    
    # forget patterns
    "Too hot to forget bujji nuvvu!": "Too hot marchipovadaniki bujji nuvvu!",
    "Sorry world lo best forget raadu ne ni!": "Sorry lokam lo best marchipovadhu ne ni!",
    
    # together patterns
    "Aithe raa solve chesukondaam together!": "Aithe raa solve chesukondaam kalisi!",
    "Life aithe full ga live cheddama together!": "Jeevitham aithe full ga live cheddama kalisi!",
    "Come over together thindaam bujji!": "Come over kalisi thindaam bujji!",
    
    # life patterns
    "Eppudo eppudo ani eduru chusthunte vacchav naa life loki!": "Eppudo eppudo ani eduru chusthunte vacchav naa jeevitham loki!",
    "Nenu aithe nuvvu marchipovu life lo!": "Nenu aithe nuvvu marchipovu jeevitham lo!",
    "Nuvvu nacchav chaalu na life ki adey enough!": "Nuvvu nacchav chaalu naa jeevitham ki adhe chaalu!",
    
    # lucky/luck patterns
    "Lucky charm nuvvu naa di!": "Adrushtam charm nuvve naa di!",
    "Lucky feel avthunna baby blessed!": "Adrushtam feel avthunna baby blessed!",
    
    # close patterns
    "Ne daggara close ga undaali ippudu!": "Ne daggara daggara ga undaali ippudu!",
    
    # care patterns
    "Ne happiness protect chestha nenu!": "Ne santosham kaapaadutha nenu!",
}

# ═══════════════════════════════════════════════════════════════════
# EXCLUSION PATTERNS (don't replace in these contexts)
# ═══════════════════════════════════════════════════════════════════

EXCLUDE_CONTEXTS = [
    # Keep "love" as-is (very natural in Telugu texting)
    r'\blove\b',
    # Keep common English that's natural in Telugu texting
    r'\b(plan|call|okay|hot|ready|cute|busy|free|bored|cool|nice|sure|mood|vibe)\b',
    r'\b(morning|night|tonight|today|tomorrow|evening)\b',
    r'\b(food|coffee|tea|movie|song|music|gym|office|phone)\b',
    r'\b(msg|text|reply|online|offline|notification|screenshot)\b',
    r'\b(baby|bujji|bangaram|ra|raa)\b',
    r'\b(miss|date|mood|feel|boring|tension|jealous|possessive)\b',
]


def apply_fixes(data):
    """Apply all fixes to dataset."""
    stats = Counter()
    
    # Pass 1: Full sentence replacements (highest priority)
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone not in entry:
                continue
            for i, sentence in enumerate(entry[tone]):
                # Strip emoji for matching, preserve original
                clean = sentence.strip()
                for old_sent, new_sent in SENTENCE_FIXES.items():
                    if clean.startswith(old_sent.split('!')[0]) or clean == old_sent:
                        # Preserve trailing emoji
                        emoji_part = ''
                        emoji_match = re.search(r'[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F\u2705\u2B50]+\s*$', clean)
                        if emoji_match:
                            emoji_part = ' ' + emoji_match.group().strip()
                        
                        # Check if new_sent already has emoji
                        new_has_emoji = bool(re.search(r'[\U0001F600-\U0001FAFF\u2764\u2728\uFE0F]+', new_sent))
                        if new_has_emoji:
                            entry[tone][i] = new_sent
                        else:
                            entry[tone][i] = new_sent + emoji_part
                        stats['sentence_fixes'] += 1
                        break
    
    # Pass 2: Context-aware regex replacements
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone not in entry:
                continue
            for i, sentence in enumerate(entry[tone]):
                original = sentence
                for pattern, replacement, desc in CONTEXT_PATTERNS:
                    if re.search(pattern, entry[tone][i], re.IGNORECASE):
                        entry[tone][i] = re.sub(pattern, replacement, entry[tone][i], count=1, flags=re.IGNORECASE)
                
                if entry[tone][i] != original:
                    stats['pattern_fixes'] += 1
    
    # Pass 3: Fix capitalization issues (double capitals after replacement)
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone not in entry:
                continue
            for i, sentence in enumerate(entry[tone]):
                # Fix things like "Nidra Nidra" or double words
                entry[tone][i] = re.sub(r'\b(\w+)\s+\1\b', r'\1', entry[tone][i])
    
    return stats


def validate_json(data):
    """Validate dataset structure."""
    errors = []
    for idx, entry in enumerate(data):
        if 'incoming' not in entry:
            errors.append(f"Entry {idx}: missing 'incoming'")
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone not in entry:
                errors.append(f"Entry {idx}: missing '{tone}'")
            elif not isinstance(entry[tone], list) or len(entry[tone]) != 5:
                errors.append(f"Entry {idx}: '{tone}' should have exactly 5 items")
    return errors


def main():
    print("=" * 60)
    print("  Telugu Native Fixer v2.0 - Context-Aware")
    print("=" * 60)
    
    # Load
    with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    print(f"\n📂 Loaded {len(data)} entries")
    
    # Validate before
    errors = validate_json(data)
    if errors:
        print(f"⚠️  {len(errors)} validation errors found before fixing!")
        for e in errors[:5]:
            print(f"   {e}")
        return
    
    # Apply fixes
    stats = apply_fixes(data)
    
    print(f"\n✅ Fixes applied:")
    print(f"   Sentence-level fixes: {stats.get('sentence_fixes', 0)}")
    print(f"   Pattern-level fixes:  {stats.get('pattern_fixes', 0)}")
    print(f"   Total: {sum(stats.values())}")
    
    # Validate after
    errors = validate_json(data)
    if errors:
        print(f"\n❌ VALIDATION FAILED after fixing! {len(errors)} errors")
        for e in errors[:5]:
            print(f"   {e}")
        print("   NOT saving file.")
        return
    
    # Count remaining English words
    eng_words = ['sleep', 'taste', 'wait', 'waiting', 'think', 'thinking',
                 'smile', 'smiling', 'dream', 'worry', 'ignore', 'forget',
                 'heart', 'world', 'life', 'together', 'happy', 'close',
                 'sad', 'angry', 'care', 'strong', 'luck', 'lucky',
                 'complete', 'perfect', 'start', 'scrolling', 'seriously']
    
    remaining = Counter()
    for entry in data:
        for tone in ['romantic', 'sweet', 'funny', 'bold']:
            if tone in entry:
                for s in entry[tone]:
                    for w in re.findall(r'[a-zA-Z]+', s.lower()):
                        if w in eng_words:
                            remaining[w] += 1
    
    print(f"\n📊 Remaining English words (target list):")
    for w, c in remaining.most_common(15):
        print(f"   {w}: {c}")
    print(f"   Total remaining: {sum(remaining.values())}")
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved to {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == '__main__':
    main()
