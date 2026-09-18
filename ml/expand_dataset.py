# -*- coding: utf-8 -*-
"""
CoupleFriendly - Synthetic Expansion & ML Dataset Generation Engine
Expands flirt_dataset_v13.json into robust ML training datasets with hard negatives.
"""

import json
import os
import random
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from taxonomy import ALL_INTENTS, ALL_EMOTIONS, HARD_NEGATIVE_PAIRS

DATA_DIR = os.path.join("ml", "data")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")
os.makedirs(SPLITS_DIR, exist_ok=True)

V13_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v13.json")

# Nicknames and particles
NICKNAMES = ["bujji", "bangaram", "baby", "sweetheart", "bujjimunda", "chitti", "ra", "andi"]
PREFIXES = ["", "Arey ", "Hey ", "Osi ", "Mari ", "Asalu ", "Pls ", "Please "]
SUFFIX_PARTICLES = ["", " ra", " le", " kadha", " ga", " mari", " bujji", " bangaram", " baby"]

# Synonym substitution maps for Tanglish colloquial expansion
SYNONYMS = {
    "tease": ["tease", "allari", "aatapattisthu", "teasing"],
    "edipisthunnav": ["edipisthunnav", "baadha peduthunnav", "hurt chesthunnav", "kallalo tears theppisthunnav", "crying theppisthunnav"],
    "matladaku": ["matladaku", "matladoddu", "silent ga undu", "matladatam maaney", "natho matladakudadhu"],
    "kopam": ["kopam", "gussa", "irritation", "chiraku"],
    "ardham kaada": ["ardham kaada", "ardham kavatleda", "chepthe vinava", "mind leda", "ardham cheskova"],
    "inkeppudu": ["inkeppudu", "inka eppudu", "malli eppudu", "life lo inka"],
    "call": ["call", "phone", "voice call"],
    "message": ["message", "msg", "text"],
    "ignore": ["ignore", "pattinchukovadam ledu", "maripoyav", "care ledu"],
    "reply": ["reply", "text back", "response", "msg ki answer"],
    "miss": ["miss avthunna", "gurthuku vasthunnav", "gurthosthunnav", "ontariga anipisthundi"],
    "love": ["love you", "premisthunna", "chala ishtam", "pranam nuvvu"],
    "cute": ["cute", "andham", "handsome", "bavunnav", "chakkaga unnav"],
    "tinnava": ["tinnava", "food thinnava", "lunch aindha", "dinner chesava", "bhojanam chesava"],
    "morning": ["good morning", "mrng", "gm", "morning bujji", "melukuvachinda"],
    "night": ["good night", "gn", "paduko", "sleep time", "sweet dreams"],
    "bayataki": ["bayataki veldama", "meet avdhama", "date ki veldama", "bayata kaluddham"]
}

def clean_tanglish(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def generate_variations(text, intent, count=25):
    """Generates realistic colloquial variations of an incoming scenario."""
    variations = set()
    variations.add(text)

    # Basic normalization
    lower = text.lower().strip("?!.,\"'")
    words = lower.split()

    # 1. Particles and Nicknames variations
    for _ in range(count * 2):
        prefix = random.choice(PREFIXES)
        suffix = random.choice(SUFFIX_PARTICLES)
        
        # Word order and particles
        cand = f"{prefix}{lower}{suffix}".strip()
        variations.add(cand)

        # Synonym substitutions
        cand_words = list(words)
        modified = False
        for i, w in enumerate(cand_words):
            for key, syns in SYNONYMS.items():
                if key in w:
                    cand_words[i] = random.choice(syns)
                    modified = True
                    break
        if modified:
            cand2 = f"{prefix}{' '.join(cand_words)}{suffix}".strip()
            variations.add(cand2)

        # Word order rearrangement (Subject/Object)
        if len(words) >= 4:
            if "nannu" in words:
                idx = words.index("nannu")
                perm = list(words)
                perm.pop(idx)
                perm.append("nannu")
                variations.add(f"{prefix}{' '.join(perm)}{suffix}".strip())

        if len(variations) >= count:
            break

    # Typo injections (real chat patterns)
    typo_cand = list(variations)
    for t in typo_cand:
        t_mod = t.replace("chepp", "cepp").replace("cheyy", "ceyy").replace("ardham", "artham").replace("undhi", "undi")
        if t_mod != t:
            variations.add(t_mod)

    return list(variations)[:count]

def build_all_datasets():
    print("Loading V13 Master Dataset...")
    with open(V13_PATH, "r", encoding="utf-8") as f:
        v13_data = json.load(f)

    intent_records = []
    emotion_records = []
    semantic_triplets = []
    generation_records = []

    # Map scenarios by intent for triplet mining
    scenario_by_intent = {}
    for item in v13_data:
        intent = item["canonical_intent"]
        scenario_by_intent.setdefault(intent, []).append(item)

    print(f"Expanding {len(v13_data)} scenarios into training datasets...")

    CRITICAL_SEEDS = [
        # Basic / Daily
        ("Em chesthunnav", "DAILY_ACTIVITY", "NEUTRAL", "DAILY_RITUALS"),
        ("Ekkada unnav", "DAILY_ACTIVITY", "NEUTRAL", "DAILY_RITUALS"),
        ("Tinnava", "FOOD_CHECK", "CARING", "DAILY_RITUALS"),
        ("Office ki vellava", "DAILY_ACTIVITY", "NEUTRAL", "DAILY_RITUALS"),
        ("Ivala em plan", "DAILY_ACTIVITY", "NEUTRAL", "DAILY_RITUALS"),
        ("Inka levaleda", "DAILY_ACTIVITY", "PLAYFUL", "DAILY_RITUALS"),
        ("Busy ga unnav aa", "DAILY_ACTIVITY", "NEUTRAL", "DAILY_RITUALS"),
        ("Free ayyaka call cheyyi", "CALL_REQUEST", "CARING", "COMPLIMENTS_MEDIA"),
        
        # Romantic & Deep Bond
        ("Nuvvu na life lo special", "DEEP_BOND", "ROMANTIC", "ROMANCE"),
        ("Na gurinchi em anukuntunnav", "DEEP_BOND", "ROMANTIC", "ROMANCE"),
        ("Natho eppudu untava", "DEEP_BOND", "ROMANTIC", "ROMANCE"),
        ("Nannu vadilesi vellipovu kada", "DEEP_BOND", "HURT", "ROMANCE"),
        ("Nenu neeku entha important", "DEEP_BOND", "ROMANTIC", "ROMANCE"),
        ("Nuvvu lekunda bore kodthundi", "MISSING", "SAD", "ROMANCE"),
        ("Nijanga nannu love chesthunnava", "ROMANTIC_STATEMENT", "ROMANTIC", "ROMANCE"),
        
        # Compliments & Flirt
        ("Nannu choosthe siggu paduthunnava", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Nee tho matladithe butterflies vastunnayi", "FLIRT_COMPLIMENT", "ROMANTIC", "ROMANCE"),
        ("Nuvvu ila cute ga enduku unnav", "FLIRT_COMPLIMENT", "PLAYFUL", "ROMANCE"),
        ("Nuvvu nannu flirt chesthunnav kada", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Nenu cute ga unna na", "COMPLIMENT_LOOKS", "PLAYFUL", "COMPLIMENTS_MEDIA"),
        ("Nee eyes chala bagunnayi", "COMPLIMENT_LOOKS", "ROMANTIC", "COMPLIMENTS_MEDIA"),
        
        # Teasing vs Hurt
        ("Nannu enduku tease chesthunnav", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Enduku nannu ila edipisthunnav", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Nannu enduku allari chesthunnav", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Nuvvu nannu baaga hurt chesav", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Naatho enduku ila aadukuntunnav", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Nuvvu nannu edipinchaku", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Nannu aatapattisthunnava", "TEASING", "PLAYFUL", "PLAYFUL_HUMOR"),
        ("Nee valla naaku baadha ga undhi", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Nannu ila irritate cheyyaku", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Nuvvu ila chesthe naaku chala hurt avuthundi", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        
        # Conflict & Frustration
        ("Na meeda enduku kopam", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Nuvvu natho enduku ila matladuthunnav", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Naatho matladaku", "ANGER_ARGUMENT", "ANGRY", "CONFLICT"),
        ("Nuvvu eppudu ilage chesthav", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Naaku nee meeda kopam vachindi", "ANGER_ARGUMENT", "ANGRY", "CONFLICT"),
        ("Nuvvu asalu care cheyyatledu", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Na feelings ni serious ga teesukovatledu", "EMOTIONAL_HURT", "HURT", "CONFLICT"),
        ("Inka ila chesthe nenu maatladanu", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Neeku oka sari chepthe ardham kaada", "CONFLICT_FRUSTRATION", "ANGRY", "CONFLICT"),
        ("Inkeppudu naku call or message cheyyaku", "BREAKUP_THREATS", "ANGRY", "CONFLICT"),
        
        # No reply & Ignoring
        ("Enduku reply ivvatledu", "NO_REPLY", "HURT", "CONFLICT"),
        ("Message chusi kuda reply ivvaledu", "NO_REPLY", "HURT", "CONFLICT"),
        ("Online lo unnav kani reply ledu", "NO_REPLY", "JEALOUS", "CONFLICT"),
        ("Naa messages ignore chesthunnav", "IGNORING", "HURT", "CONFLICT"),
        ("Nenu entha sepu wait cheyyali", "NO_REPLY", "SAD", "CONFLICT"),
        ("Reply kosam wait chesthunna", "NO_REPLY", "SAD", "CONFLICT"),
        ("Busy ante naaku reply kuda cheyyava", "NO_REPLY", "HURT", "CONFLICT"),
        ("Na message ki atleast ok ani cheppu", "NO_REPLY", "HURT", "CONFLICT"),
        ("Nannu intentionally ignore chesthunnava", "IGNORING", "ANGRY", "CONFLICT"),
        ("Em jarigindi reply enduku ledu", "NO_REPLY", "HURT", "CONFLICT"),
        
        # Jealousy
        ("Aa ammayi tho enduku antha close ga unnav", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Aa abbai tho daily enduku matladuthav", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Nannu kante vaallatho ekkuva matladuthunnav", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Nee best friend evaru", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Nuvvu vere vallani like chesthunnava", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Aa photo lo unna ammayi evaru", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Na meeda jealousy testhunnava", "JEALOUSY", "PLAYFUL", "ROMANCE"),
        ("Nuvvu nannu replace chesthunnava", "JEALOUSY", "HURT", "ROMANCE"),
        ("Na place lo inkokaru vachara", "JEALOUSY", "JEALOUS", "ROMANCE"),
        ("Nuvvu andaritho ilaane untava", "JEALOUSY", "JEALOUS", "ROMANCE"),
        
        # Apology & Reconciliation
        ("Sorry ra", "APOLOGY_SEEKING", "SAD", "CONFLICT"),
        ("Nenu mistake chesa", "APOLOGY_SEEKING", "SAD", "CONFLICT"),
        ("Na valla hurt ayyava", "APOLOGY_SEEKING", "SAD", "CONFLICT"),
        ("Please na meeda kopam vadiley", "RECONCILIATION", "SAD", "CONFLICT"),
        ("Inka kopam lone unnav aa", "RECONCILIATION", "SAD", "CONFLICT"),
        ("Manam malli normal ga matladukundama", "RECONCILIATION", "ROMANTIC", "CONFLICT"),
        ("Nenu ala anali anukoledu", "APOLOGY_SEEKING", "SAD", "CONFLICT"),
        ("Nannu forgive chesthava", "APOLOGY_SEEKING", "SAD", "CONFLICT"),
        ("Please maatladu", "RECONCILIATION", "SAD", "CONFLICT"),
        ("Mana fight end cheddama", "RECONCILIATION", "ROMANTIC", "CONFLICT"),
        
        # Short / Difficult Messages
        ("Hmm", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Haa", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Sare", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Ledu", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Enduku", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Enti", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Avuna", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Nijama", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Ohh", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS"),
        ("Okayyy", "GENERAL_CHAT", "NEUTRAL", "PLANS_OUTINGS")
    ]

    for seed_text, seed_intent, seed_emotion, seed_domain in CRITICAL_SEEDS:
        v13_data.append({
            "incoming": seed_text,
            "canonical_intent": seed_intent,
            "canonical_emotion": seed_emotion,
            "domain": seed_domain,
            "responses": {}
        })

    for item in v13_data:
        base_text = item["incoming"]
        intent = item["canonical_intent"]
        emotion = item["canonical_emotion"]
        domain = item["domain"]
        responses = item.get("responses", {})

        # Generate 20 variations per scenario
        vars_list = generate_variations(base_text, intent, count=22)

        for var in vars_list:
            clean_var = clean_tanglish(var)
            intent_records.append({
                "text": clean_var,
                "intent": intent,
                "domain": domain
            })
            emotion_records.append({
                "text": clean_var,
                "emotion": emotion,
                "domain": domain
            })

            # Negative mining for semantic triplets
            other_intents = [k for k in scenario_by_intent.keys() if k != intent]
            if other_intents:
                neg_intent = random.choice(other_intents)
                neg_scenario = random.choice(scenario_by_intent[neg_intent])["incoming"]
                semantic_triplets.append({
                    "query": clean_var,
                    "positive_scenario": base_text,
                    "negative_scenario": neg_scenario,
                    "target_intent": intent
                })

        # Generation records
        for tone in ["romantic", "sweet", "funny", "bold"]:
            tone_replies = responses.get(tone, [])
            for r in tone_replies:
                rep_text = r.get("text", "") if isinstance(r, dict) else str(r)
                if rep_text:
                    generation_records.append({
                        "input": {
                            "message": base_text,
                            "intent": intent,
                            "emotion": emotion,
                            "tone": tone.upper()
                        },
                        "output": rep_text
                    })

    # Add hard negative discrimination pairs
    hard_neg_records = []
    for hn in HARD_NEGATIVE_PAIRS:
        vars_a = generate_variations(hn["example_a"], hn["intent_a"], count=15)
        vars_b = generate_variations(hn["example_b"], hn["intent_b"], count=15)

        for va in vars_a:
            intent_records.append({"text": va, "intent": hn["intent_a"], "domain": "HARD_NEGATIVE"})
            hard_neg_records.append({
                "anchor": va,
                "correct_intent": hn["intent_a"],
                "negative_intent": hn["intent_b"],
                "pair_id": hn["pair_id"]
            })
        for vb in vars_b:
            intent_records.append({"text": vb, "intent": hn["intent_b"], "domain": "HARD_NEGATIVE"})
            hard_neg_records.append({
                "anchor": vb,
                "correct_intent": hn["intent_b"],
                "negative_intent": hn["intent_a"],
                "pair_id": hn["pair_id"]
            })

    # Shuffle datasets
    random.seed(42)
    random.shuffle(intent_records)
    random.shuffle(emotion_records)
    random.shuffle(semantic_triplets)
    random.shuffle(generation_records)
    random.shuffle(hard_neg_records)

    print(f"\nTotal Intent Training Examples: {len(intent_records)}")
    print(f"Total Emotion Training Examples: {len(emotion_records)}")
    print(f"Total Semantic Triplet Pairs: {len(semantic_triplets)}")
    print(f"Total Generation Training Examples: {len(generation_records)}")
    print(f"Total Hard Negative Pairs: {len(hard_neg_records)}")

    # Write Master JSONL files
    def write_jsonl(path, items):
        with open(path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Written: {path} ({len(items)} rows)")

    write_jsonl(os.path.join(DATA_DIR, "intent_dataset.jsonl"), intent_records)
    write_jsonl(os.path.join(DATA_DIR, "emotion_dataset.jsonl"), emotion_records)
    write_jsonl(os.path.join(DATA_DIR, "semantic_pairs.jsonl"), semantic_triplets)
    write_jsonl(os.path.join(DATA_DIR, "generation_dataset.jsonl"), generation_records)
    write_jsonl(os.path.join(DATA_DIR, "hard_negatives.jsonl"), hard_neg_records)

    # 80/10/10 Train/Val/Test Split for Intent Classifier
    n = len(intent_records)
    n_train = int(n * 0.8)
    n_val = int(n * 0.1)

    train_set = intent_records[:n_train]
    val_set = intent_records[n_train:n_train + n_val]
    test_set = intent_records[n_train + n_val:]

    write_jsonl(os.path.join(SPLITS_DIR, "intent_train.jsonl"), train_set)
    write_jsonl(os.path.join(SPLITS_DIR, "intent_val.jsonl"), val_set)
    write_jsonl(os.path.join(SPLITS_DIR, "intent_test.jsonl"), test_set)

    print("\n✅ Phase 2 Dataset Generation Complete!")

if __name__ == "__main__":
    build_all_datasets()
