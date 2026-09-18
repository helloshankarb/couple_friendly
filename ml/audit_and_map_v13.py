# -*- coding: utf-8 -*-
"""
Audits flirt_dataset_v12.json and creates flirt_dataset_v13.json with canonical 36 intents and 9 emotions.
"""

import json
import os
import re
from taxonomy import ALL_INTENTS, ALL_EMOTIONS, DOMAINS

V12_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v12.json")
V13_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v13.json")

def map_scenario(item):
    inc = item.get("incoming", "").lower().strip()
    cat = item.get("category", "").lower().strip()
    orig_intent = str(item.get("intent", "")).upper().strip()
    sub_intent = str(item.get("sub_intent", "")).upper().strip()

    # Default
    domain = "PLANS_OUTINGS"
    intent = "GENERAL_CHAT"
    emotion = "NEUTRAL"

    # --- 1. CONFLICT & EMOTIONAL HURT ---
    if any(k in inc for k in ["inkeppudu", "block", "breakup", "vellipotha", "dooram undu", "single ga untanu"]) or (
        any(v in inc for v in ["call", "message", "msg"]) and any(neg in inc for neg in ["ceyyaku", "cheyyaku", "vaddu", "oddu"])
    ):
        domain = "CONFLICT"
        intent = "BREAKUP_THREATS"
        emotion = "ANGRY"
    elif any(k in inc for k in ["edip", "edav", "edus", "yedus", "hurt", "kallalo neellu", "baadha", "badha", "crying", "tears"]):
        domain = "CONFLICT"
        intent = "EMOTIONAL_HURT"
        emotion = "HURT"
    elif any(k in inc for k in ["oka sari chepthe", "ardham kaada", "ardham kaadha", "enni sarlu", "chepthe vinava", "visugu", "chiraku", "buddhi leda"]):
        domain = "CONFLICT"
        intent = "CONFLICT_FRUSTRATION"
        emotion = "ANGRY"
    elif any(k in inc for k in ["ignore", "pattinchukodam", "pattinchukovadam", "maripoyav"]):
        domain = "CONFLICT"
        intent = "IGNORING"
        emotion = "ANGRY"
    elif any(k in inc for k in ["reply ivvatledu", "reply ivvaledu", "reply late", "reply enduku"]):
        domain = "CONFLICT"
        intent = "NO_REPLY"
        emotion = "ANGRY"
    elif any(k in inc for k in ["forgive", "sorry", "kshaminchu"]):
        domain = "CONFLICT"
        intent = "APOLOGY_SEEKING"
        emotion = "SAD"
    elif any(k in inc for k in ["reconciliation", "fight aapesthama", "normal ga matlad"]):
        domain = "CONFLICT"
        intent = "RECONCILIATION"
        emotion = "NEUTRAL"
    elif any(k in inc for k in ["kopam", "gussa", "fight", "matladaku", "matladanu", "vadiley"]) or cat in ["fight", "angry", "conflict"]:
        domain = "CONFLICT"
        intent = "ANGER_ARGUMENT"
        emotion = "ANGRY"

    # --- 2. ROMANCE & ATTACHMENT ---
    elif any(k in inc for k in ["ex", "other girl", "ammai", "ammailu", "abbai", "jealous"]) or cat in ["jealous", "jealousy"]:
        domain = "ROMANCE"
        intent = "JEALOUSY"
        emotion = "JEALOUS"
    elif any(k in inc for k in ["pelli", "marriage", "proposal"]) or cat in ["proposal"]:
        domain = "ROMANCE"
        intent = "PROPOSAL"
        emotion = "ROMANTIC"
    elif any(k in inc for k in ["miss", "missing", "gurthosth", "ontari", "lonely"]) or cat in ["miss", "missing"]:
        domain = "ROMANCE"
        intent = "MISSING"
        emotion = "MISSING"
    elif any(k in inc for k in ["promise", "future", "relationship", "bond", "trust"]) or cat in ["trust", "future_plans"]:
        domain = "ROMANCE"
        intent = "DEEP_BOND"
        emotion = "ROMANTIC"
    elif any(k in inc for k in ["hot", "sexy", "tempt", "hug", "kiss", "lip", "muddu", "attraction", "crush"]) or cat in ["flirt", "bold"]:
        domain = "ROMANCE"
        intent = "FLIRT_COMPLIMENT"
        emotion = "ROMANTIC"
    elif any(k in inc for k in ["love", "prema", "pranam", "prapancham", "ishtam", "heart"]) or cat in ["love", "romantic"]:
        domain = "ROMANCE"
        intent = "ROMANTIC_STATEMENT"
        emotion = "ROMANTIC"

    # --- 3. DAILY RITUALS & CARE ---
    elif any(k in inc for k in ["morning", "mrng", "gm", "lechava", "melukuva"]) or cat in ["morning", "morning_motivation"]:
        domain = "DAILY_RITUALS"
        intent = "GREETING_MORNING"
        emotion = "HAPPY"
    elif any(k in inc for k in ["night", "gn", "nidra", "sleep", "paduko", "dreams"]) or cat in ["night", "night_chat"]:
        domain = "DAILY_RITUALS"
        intent = "GREETING_NIGHT"
        emotion = "NEUTRAL"
    elif any(k in inc for k in ["tinnava", "thinnava", "tinna", "food", "lunch", "dinner", "breakfast", "curry"]) or cat in ["food"]:
        domain = "DAILY_RITUALS"
        intent = "FOOD_CHECK"
        emotion = "NEUTRAL"
    elif any(k in inc for k in ["tablet", "fever", "pain", "headache", "care", "rest", "medicine", "health", "water thagu"]) or cat in ["care", "health", "support"]:
        domain = "DAILY_RITUALS"
        intent = "HEALTH_CARE"
        emotion = "NEUTRAL"
    elif any(k in inc for k in ["sleepy", "tired", "nidrosthondi", "alasata"]) or cat in ["sleepy"]:
        domain = "DAILY_RITUALS"
        intent = "SLEEP_REST"
        emotion = "NEUTRAL"
    elif any(k in inc for k in ["office", "work", "college", "chaduvukuntunna", "busy", "task"]) or cat in ["study_work", "busy"]:
        domain = "DAILY_RITUALS"
        intent = "DAILY_ACTIVITY"
        emotion = "NEUTRAL"

    # --- 4. PLAYFUL & HUMOR ---
    elif any(k in inc for k in ["teas", "allari", "prank", "roast", "silly"]) or cat in ["teasing", "playful"]:
        domain = "PLAYFUL_HUMOR"
        intent = "TEASING"
        emotion = "PLAYFUL"
    elif any(k in inc for k in ["challenge", "bet", "compet", "poti"]) or cat in ["funny"] and any(k in inc for k in ["dare", "win"]):
        domain = "PLAYFUL_HUMOR"
        intent = "PLAYFUL_BANTER"
        emotion = "PLAYFUL"
    elif any(k in inc for k in ["joke", "chutkule", "comedy", "navv"]) or cat in ["funny"]:
        domain = "PLAYFUL_HUMOR"
        intent = "JOKING"
        emotion = "PLAYFUL"
    elif any(k in inc for k in ["hero", "pedda", "over action", "dabbha", "build-up"]):
        domain = "PLAYFUL_HUMOR"
        intent = "SARCASM_CUTE"
        emotion = "PLAYFUL"

    # --- 5. COMPLIMENTS & MEDIA ---
    elif any(k in inc for k in ["dress", "saree", "shirt", "outfit", "style"]):
        domain = "COMPLIMENTS_MEDIA"
        intent = "COMPLIMENT_OUTFIT"
        emotion = "HAPPY"
    elif any(k in inc for k in ["cute", "handsome", "beautiful", "andham", "gorgeous", "eyes", "smile", "chupu"]) or cat in ["compliment", "compliments"]:
        domain = "COMPLIMENTS_MEDIA"
        intent = "COMPLIMENT_LOOKS"
        emotion = "HAPPY"
    elif any(k in inc for k in ["photo", "pic", "selfie", "snap", "video"]) or cat in ["photo"]:
        domain = "COMPLIMENTS_MEDIA"
        intent = "PHOTO_REQUEST"
        emotion = "EXCITED"
    elif any(k in inc for k in ["call", "phone", "voice", "matladu"]) or cat in ["calls"]:
        domain = "COMPLIMENTS_MEDIA"
        intent = "CALL_REQUEST"
        emotion = "EXCITED"

    # --- 6. PLANS & OUTINGS ---
    elif any(k in inc for k in ["date", "meet", "kaluddham", "bayataki", "dinner date"]) or cat in ["date"]:
        domain = "PLANS_OUTINGS"
        intent = "DATE_REQUEST"
        emotion = "EXCITED"
    elif any(k in inc for k in ["movie", "cinema", "trip", "tour", "travel", "long drive"]) or cat in ["music_movies", "plans"]:
        domain = "PLANS_OUTINGS"
        intent = "MOVIE_TRIP"
        emotion = "EXCITED"
    elif any(k in inc for k in ["bore", "boring", "time pass", "ontariga"]):
        domain = "PLANS_OUTINGS"
        intent = "BOREDOM"
        emotion = "SAD"
    else:
        domain = "PLANS_OUTINGS"
        intent = "GENERAL_CHAT"
        emotion = "NEUTRAL"

    assert intent in ALL_INTENTS, f"Invalid intent: {intent}"
    assert domain in DOMAINS, f"Invalid domain: {domain}"

    return domain, intent, emotion

def audit_and_build():
    with open(V12_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded V12 dataset with {len(data)} scenarios.\n")

    v13_data = []
    intent_counts = {}
    domain_counts = {}
    emotion_counts = {}

    for item in data:
        dom, intent, emotion = map_scenario(item)
        
        item_v13 = dict(item)
        item_v13["domain"] = dom
        item_v13["canonical_intent"] = intent
        item_v13["canonical_emotion"] = emotion

        v13_data.append(item_v13)

        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        domain_counts[dom] = domain_counts.get(dom, 0) + 1
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    with open(V13_PATH, "w", encoding="utf-8") as f:
        json.dump(v13_data, f, ensure_ascii=False, indent=2)

    print("=== DOMAIN COVERAGE ===")
    for dom, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dom:<25}: {count} scenarios")

    print("\n=== INTENT COVERAGE (Top 25) ===")
    for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:25]:
        print(f"  {intent:<28}: {count} scenarios")

    print("\n=== EMOTION COVERAGE ===")
    for emo, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {emo:<25}: {count} scenarios")

    print(f"\nV13 Master Dataset written to {V13_PATH} ({len(v13_data)} scenarios)")

if __name__ == "__main__":
    audit_and_build()
