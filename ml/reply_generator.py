# -*- coding: utf-8 -*-
"""
CoupleFriendly - Model 3: Controlled Tanglish Reply Variation & Multi-Angle Generation Engine
Generates 3 distinct, purposeful, 100% colloquial Tanglish replies:
  Angle 1: Empathy & Direct Validation
  Angle 2: Reassurance & Constructive Action
  Angle 3: Affectionate Softening

Filter priority:
  Relevance -> Emotional Appropriateness -> Tone -> Safety -> Natural Tanglish -> Diversity
"""

import json
import os
import sys
import random
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from ml.semantic_retriever import SemanticRetriever
except ImportError:
    from semantic_retriever import SemanticRetriever

NICKNAMES = ["bujji", "bangaram", "baby", "sweetheart", "chitti"]

# Unnatural translated English patterns to replace with native Tanglish expressions
UNNATURAL_TRANSLATIONS = {
    r".*don't feel sad please.*": "Ayyoo bujji, ala baadha padaku please... nenu unna kadha neetho! 🥰",
    r".*ninnu miss avuthunna too.*": "nenu kuda ninnu chala miss avuthunna bujji! 🥰",
    r".*i miss you too.*": "nenu kuda ninnu chala miss avuthunna bujji ❤️",
    r".*don't cry please.*": "please edavaku bujji, naaku chala baadha ga undi 🥰",
    r".*take care please.*": "baga care theesuko bujji ❤️"
}

def cleanup_syntax(text: str) -> str:
    """Removes template corruption artifacts, dangling punctuation, and double spaces."""
    if not text:
        return ""
    clean = text.strip().strip('"\'')

    # Remove template corruption like "Hurt ayithe ." or "cheppu , "
    clean = re.sub(r'\b(ayithe|chesthe|unte|kani|kuda)\s+([.,!?])', r'\1', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\s+([,!?.:;])', r'\1', clean)
    clean = re.sub(r'([,!?])\1+', r'\1', clean)
    clean = re.sub(r',\s*,', ',', clean)
    clean = re.sub(r'\b(Aww|Ayyoo)\s+\w+,\s*Ayyoo\s+', 'Ayyoo ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'([🥰❤️😊💕😘])\s*\1+', r'\1', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Ensure clean spacing after punctuation
    clean = re.sub(r'([.,!?])(?=[a-zA-Z])', r'\1 ', clean)
    return clean

def sanitize_tanglish(text: str) -> str:
    if not text:
        return ""
    clean = cleanup_syntax(text)

    # Check for unnatural English translations
    for bad_pat, good_rep in UNNATURAL_TRANSLATIONS.items():
        clean = re.sub(bad_pat, good_rep, clean, flags=re.IGNORECASE)

    # Native phonetic corrections
    corrections = {
        "alochichadame": "alochinchadame",
        "puri munigipoyanu": "poorthiga munigipoya",
        "upiri theesukuntunna": "nee dhyasa lo unna",
        "oopiri theeskuntunna": "nee dhyasa lo unna",
        "vunta": "unta",
        "vuntunna": "untunna",
        "cheshanu": "chesa",
        "chesthunnau": "chesthunna",
        "eduru choostunna": "wait chesthunna",
        "eduruchoostunna": "wait chesthunna",
        "badha ga undhi": "baadhaga undi",
        "badhaga undhi": "baadhaga undi",
        "vintha": "vinta",
        "kopam ga": "kopamga",
        "matladaku": "matladoddu",
        "vadiley": "vadilei",
        "cehpthe": "chepthe",
        "ceyyaku": "cheyyaku"
    }
    for wrong, right in corrections.items():
        clean = re.sub(r'\b' + re.escape(wrong) + r'\b', right, clean, flags=re.IGNORECASE)
    
    # Pronoun cleanup (preserve intimacy)
    clean = re.sub(r'\bmeeru\b', 'nuvvu', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bela unnaru\b', 'ela unnav', clean, flags=re.IGNORECASE)
    return cleanup_syntax(clean)

def apply_safety_gate(replies, intent, tone):
    """Strict emotional safety: blocks mockery and sexual escalation on distress/conflict."""
    tone_lower = tone.lower()
    sensitive = ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"]
    if intent not in sensitive:
        return replies

    safe_list = []
    if tone_lower == "funny":
        for r in replies:
            if not any(bad in r.lower() for bad in ["cartoon", "photo frame", "facial glow", "mascara", "makeup"]):
                safe_list.append(r)
        if len(safe_list) < 3:
            safe_list.extend([
                "Sare bujji, first kopam thagginchuko... tarvatha nannu question cheyyi 😂❤️",
                "Ayyo bujji, ila serious avvaku... first oka smile ivvu, tarvatha settle cheddam 😂❤️",
                "Mana fight ki referee avasaram ledu, direct ga ice cream tho settle cheddam 😂❤️"
            ])
        return safe_list[:3]

    elif tone_lower == "bold":
        for r in replies:
            if not any(bad in r.lower() for bad in ["kisses thoti mayam", "wilder", "intense romance", "chest meeda", "hug lo"]):
                safe_list.append(r)
        if len(safe_list) < 3:
            safe_list.extend([
                "Nuvvu hurt ayye la malli cheyyanu bujji, first naa maatavinu ❤️",
                "Nee smile tirigi vacche varaku ninnu convince cheyyadam naa responsibility 😏❤️",
                "First step evaru vesina okay... manam matladukundam, dooram undaku 😉❤️"
            ])
        return safe_list[:3]

    return replies

def compute_token_overlap(s1: str, s2: str) -> float:
    """Computes Jaccard word overlap between two replies."""
    w1 = set(s1.lower().split())
    w2 = set(s2.lower().split())
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)

class LocalReplyGenerator:
    def __init__(self):
        self.retriever = SemanticRetriever()

    def generate(self, user_message, tone="SWEET", num_replies=3):
        intent, intent_conf, emotion, emotion_conf, top_scenarios = self.retriever.retrieve(user_message, top_k=5)
        tone_key = tone.lower()
        lower_msg = user_message.lower()

        # Contextual relevance overrides for sensitive grievances
        # E.g., 'na feelings ni serious ga teesukovatledu' -> Emotional Validation, not commitment lecture!
        if any(w in lower_msg for w in ["feelings", "care cheyyatledu", "pattinchukovatledu"]) and intent in ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION"]:
            angle_1 = "Nee feelings naaku chala important bujji, ninnu alochinchakunda hurt chesi unte nijanga sorry. ❤️"
            angle_2 = "Ala anukoku please... nenu epudu nee side eh untanu, nee manasulo emundo cheppu poorthiga vintanu bujji. 🥺"
            angle_3 = "Nuvvu naa life lo entha special oo naaku telusu bangaram, inko sari ila feel avvanivvanu. 🥰"
            return {
                "query": user_message,
                "detected_intent": intent,
                "intent_confidence": round(intent_conf, 2),
                "detected_emotion": emotion,
                "emotion_confidence": round(emotion_conf, 2),
                "top_scenario": top_scenarios[0]["scenario"] if top_scenarios else "General",
                "scenario_score": top_scenarios[0]["score"] if top_scenarios else 0,
                "reply_style": tone.upper(),
                "final_replies": [angle_1, angle_2, angle_3]
            }

        # Contextual relevance overrides for crying & emotional hurt (#032)
        # Empathy (understand why hurt) -> Reassurance (promise to listen) -> Affection (soften interaction)
        if any(w in lower_msg for w in ["edip", "edav", "yedus", "edupu", "crying"]) and intent in ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION"]:
            angle_1 = "Nijanga chala sorry bujji, ninnu baadha pettalani asalu anukoledhu... na valla baadha padaku please ❤️"
            angle_2 = "Nee side enti anipinchindo cheppu bangaram, poorthiga vintanu... calm ga matladukundam 🥺"
            angle_3 = "Nuvvu edisthe naaku chala baadha ga untundhi ra... nuvve na bangaram, please smile cheyyi 🥰"
            return {
                "query": user_message,
                "detected_intent": intent,
                "intent_confidence": round(intent_conf, 2),
                "detected_emotion": emotion,
                "emotion_confidence": round(emotion_conf, 2),
                "top_scenario": top_scenarios[0]["scenario"] if top_scenarios else "General",
                "scenario_score": top_scenarios[0]["score"] if top_scenarios else 0,
                "reply_style": tone.upper(),
                "final_replies": [angle_1, angle_2, angle_3]
            }

        # Collect raw responses across the top 3-5 scenarios
        candidate_pool = []
        for sc in top_scenarios:
            responses = sc.get("responses", {}).get(tone_key, [])
            for r in responses:
                text = r.get("text", "") if isinstance(r, dict) else str(r)
                if text:
                    candidate_pool.append(sanitize_tanglish(text))

        # Safe fallback pools by intent category
        if intent in ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"]:
            angle_defaults = [
                # Angle 1: Empathy & Sincere Apology
                "Hurt ayithe nijanga sorry bujji. Nee side enti anipinchindo cheppu, poorthiga vinta. ❤️",
                # Angle 2: Reassurance & Action
                "Ninnu hurt cheyyalani assalu ledu bangaram, manam calm ga matladukundama? 🥺",
                # Angle 3: Affectionate Softening
                "Ala baadha padaku ra, nuvvu lekunda naaku em tochadu... cool avvu please. 🥰"
            ]
        elif intent == "TEASING":
            angle_defaults = [
                # Angle 1: Direct playful tease
                "Ninnu tease cheyyadam lo unde kick eh veru bangaram! 😂",
                # Angle 2: Cute counter-banter
                "Mari intha mudhuga unte evaraina aatapattinchakunda ela untaru bujji? 😜",
                # Angle 3: Affectionate flirt
                "Nee cute reactions chusthe smile aagadu mari, anthe na tappu em ledu! 🥰"
            ]
        elif intent in ["MISSING", "ROMANTIC_STATEMENT", "DEEP_BOND"]:
            angle_defaults = [
                # Angle 1: Deep emotional validation
                "Nuvvu lekunda unte naaku kuda asalu roju gadavadu bangaram. ❤️",
                # Angle 2: Sweet action / connection
                "Chala miss avthunna bujji, free ayyaka ventane call chesthava? 🥰",
                # Angle 3: Romantic reassurance
                "Nee gundello, nee prathi alochana lonae unna chitti, eppatiki neethone unta! 😘"
            ]
        else:
            angle_defaults = [
                "Nee message chusthe chaalu bangaram, naa roju super ga start avuthundhi! ❤️",
                "Cheppu bujji, ivala em plans unnayi neeku? 🥰",
                "Eppudu msg chesthava ani wait chesthunna chitti! 😘"
            ]

        # Multi-Angle Selection Pipeline (Relevance -> Appropriateness -> Tone -> Safety -> Diversity)
        selected_replies = []

        # Try to select diverse candidates from the retrieved scenarios first
        for cand in candidate_pool:
            cand_clean = sanitize_tanglish(cand)
            if not cand_clean or len(cand_clean) < 8:
                continue

            # Check overlap with already selected replies (Diversity check)
            too_similar = any(compute_token_overlap(cand_clean, existing) > 0.55 for existing in selected_replies)
            if not too_similar:
                selected_replies.append(cand_clean)
            if len(selected_replies) >= num_replies:
                break

        # If pool lacks diversity or has fewer than 3, fill with multi-angle defaults
        for fallback in angle_defaults:
            if len(selected_replies) >= num_replies:
                break
            fb_clean = sanitize_tanglish(fallback)
            too_similar = any(compute_token_overlap(fb_clean, existing) > 0.55 for existing in selected_replies)
            if not too_similar:
                selected_replies.append(fb_clean)

        # Apply Safety Gate
        safe_replies = apply_safety_gate(selected_replies, intent, tone)
        final_list = [cleanup_syntax(r) for r in safe_replies[:num_replies]]

        return {
            "query": user_message,
            "detected_intent": intent,
            "intent_confidence": round(intent_conf, 2),
            "detected_emotion": emotion,
            "emotion_confidence": round(emotion_conf, 2),
            "top_scenario": top_scenarios[0]["scenario"] if top_scenarios else "General",
            "scenario_score": top_scenarios[0]["score"] if top_scenarios else 0,
            "reply_style": tone.upper(),
            "final_replies": final_list
        }

if __name__ == "__main__":
    generator = LocalReplyGenerator()
    test_cases = [
        ("enduku nannu ila edipisthunnav", "SWEET"),
        ("na feelings ni serious ga teesukovatledu", "SWEET"),
        ("nannu enduku tease chesthunnav", "FUNNY"),
        ("nuvvu chala beautiful", "ROMANTIC"),
        ("ninnu miss avthunaa", "ROMANTIC")
    ]
    print("\n" + "=" * 76)
    print("✨ TEST MULTI-ANGLE DIVERSE REPLY GENERATION")
    print("=" * 76)
    for q, t in test_cases:
        res = generator.generate(q, tone=t)
        print(f"\n📩 Query: \"{res['query']}\" [{res['detected_intent']} / {res['detected_emotion']}] Style: {res['reply_style']}")
        for idx, r in enumerate(res["final_replies"], 1):
            print(f"  Angle {idx}: {r}")
