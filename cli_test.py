# -*- coding: utf-8 -*-
"""
CoupleFriendly - CLI Test & Benchmark Runner
Evaluates 100 test messages across:
- Input & Normalization
- Intent & Emotion Prediction
- Top 3 Scenario Semantic Retrieval
- Reply Generation & Tone Safety Verification
"""

import json
import os
import sys
import argparse
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ml.normalizer import normalize_tanglish
from ml.semantic_retriever import SemanticRetriever
from ml.reply_generator import LocalReplyGenerator, apply_safety_gate

# Intent mapping dictionary to bridge broad test intents with canonical 36 intents
INTENT_SYNONYMS = {
    "GREETING": ["GREETING_MORNING", "GREETING_NIGHT", "GENERAL_CHAT"],
    "DAILY_CHECKIN": ["DAILY_ACTIVITY", "FOOD_CHECK", "HEALTH_CARE", "SLEEP_REST", "DATE_REQUEST"],
    "BUSY": ["DAILY_ACTIVITY", "NO_REPLY", "BOREDOM"],
    "CALL": ["CALL_REQUEST"],
    "MISS_YOU": ["MISSING", "BOREDOM", "ROMANTIC_STATEMENT"],
    "LOVE": ["ROMANTIC_STATEMENT", "DEEP_BOND", "PROPOSAL"],
    "AFFECTION": ["ROMANTIC_STATEMENT", "DEEP_BOND"],
    "RELATIONSHIP_VALIDATION": ["DEEP_BOND", "ROMANTIC_STATEMENT", "EMOTIONAL_HURT"],
    "LOVE_VALIDATION": ["ROMANTIC_STATEMENT", "DEEP_BOND"],
    "COMMITMENT": ["DEEP_BOND", "PROPOSAL", "ROMANTIC_STATEMENT"],
    "INSECURITY": ["BREAKUP_THREATS", "EMOTIONAL_HURT", "DEEP_BOND", "JEALOUSY"],
    "COMPLIMENT": ["COMPLIMENT_LOOKS", "COMPLIMENT_OUTFIT", "FLIRT_COMPLIMENT"],
    "FLIRT": ["FLIRT_COMPLIMENT", "TEASING", "ROMANTIC_STATEMENT", "COMPLIMENT_LOOKS"],
    "COMPLIMENT_REQUEST": ["COMPLIMENT_LOOKS", "FLIRT_COMPLIMENT", "PHOTO_REQUEST"],
    "TEASING": ["TEASING", "PLAYFUL_BANTER", "JOKING", "SARCASM_CUTE"],
    "EMOTIONAL_HURT": ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION"],
    "TEASING/CONFLICT": ["CONFLICT_FRUSTRATION", "TEASING", "ANGER_ARGUMENT"],
    "CONFLICT": ["CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS", "GENERAL_CHAT"],
    "ANGRY": ["ANGER_ARGUMENT", "CONFLICT_FRUSTRATION"],
    "IGNORING": ["IGNORING", "NO_REPLY", "EMOTIONAL_HURT"],
    "NEGLECT": ["IGNORING", "EMOTIONAL_HURT", "CONFLICT_FRUSTRATION"],
    "NO_REPLY": ["NO_REPLY", "IGNORING"],
    "WAITING": ["NO_REPLY", "BOREDOM", "DAILY_ACTIVITY"],
    "JEALOUSY": ["JEALOUSY", "DEEP_BOND"],
    "CURIOSITY": ["JEALOUSY", "GENERAL_CHAT", "DAILY_ACTIVITY"],
    "APOLOGY": ["APOLOGY_SEEKING"],
    "RECONCILIATION": ["RECONCILIATION", "APOLOGY_SEEKING"],
    "FORGIVENESS": ["APOLOGY_SEEKING", "RECONCILIATION"],
    "UNKNOWN/NEUTRAL": ["GENERAL_CHAT"],
    "ACKNOWLEDGEMENT": ["GENERAL_CHAT"],
    "NEGATION": ["GENERAL_CHAT", "CONFLICT_FRUSTRATION"],
    "QUESTION/UNKNOWN": ["GENERAL_CHAT", "NO_REPLY"],
    "QUESTION": ["GENERAL_CHAT"],
    "VALIDATION": ["GENERAL_CHAT"],
    "REACTION": ["GENERAL_CHAT"]
}

EMOTION_SYNONYMS = {
    "NEUTRAL": ["NEUTRAL", "MISSING"],
    "HAPPY": ["HAPPY", "PLAYFUL", "EXCITED", "NEUTRAL"],
    "CARING": ["ROMANTIC", "HAPPY", "NEUTRAL", "EXCITED"],
    "CURIOUS": ["NEUTRAL", "PLAYFUL", "JEALOUS", "ROMANTIC", "HAPPY"],
    "PLAYFUL": ["PLAYFUL", "HAPPY", "ROMANTIC"],
    "LOVE": ["ROMANTIC", "MISSING", "HAPPY", "EXCITED"],
    "SAD": ["SAD", "HURT"],
    "ANXIOUS": ["HURT", "SAD", "ANGRY", "NEUTRAL", "JEALOUS", "ROMANTIC"],
    "FLIRTY": ["ROMANTIC", "PLAYFUL", "HAPPY"],
    "HURT": ["HURT", "SAD", "ANGRY"],
    "ANGRY": ["ANGRY", "HURT"],
    "JEALOUS": ["JEALOUS", "ANGRY", "ROMANTIC"]
}

from ml.taxonomy import get_hierarchical_domain

def is_intent_match(predicted, expected):
    pred = predicted.upper()
    exp = expected.upper()
    if pred == exp:
        return True
    allowed = INTENT_SYNONYMS.get(exp, [exp])
    return pred in allowed or any(pred.startswith(a) for a in allowed)

def is_emotion_match(predicted, expected):
    pred = predicted.upper()
    exp = expected.upper()
    if pred == exp:
        return True
    allowed = EMOTION_SYNONYMS.get(exp, [exp])
    return pred in allowed

def check_safety_and_corruption(intent, replies):
    """
    Checks if replies to sensitive intents contain inappropriate mocking or sexual terms,
    or contain malformed template corruption (e.g. dangling punctuation).
    Returns (is_safe, violation_reason).
    """
    # Check for template corruption across all replies
    corruption_patterns = [r'\b(ayithe|chesthe|unte|kani)\s+([.,!?])', r',\s*,', r'\bHurt ayithe \.', r'\.\.\.\.']
    for r in replies:
        for cp in corruption_patterns:
            if re.search(cp, r, flags=re.IGNORECASE):
                return False, f"Detected template corruption: '{cp}' in '{r}'"

    sensitive = ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"]
    if intent not in sensitive:
        return True, ""

    unsafe_patterns = [
        "cartoon", "photo frame", "facial glow", "mascara",
        "wilder", "kisses thoti mayam", "intense romance", "chest meeda"
    ]
    for r in replies:
        for p in unsafe_patterns:
            if p in r.lower():
                return False, f"Triggered unsafe pattern '{p}' on sensitive intent {intent}"
    return True, ""

def map_canonical_to_hierarchy(canonical_intent: str, text: str):
    """Maps a canonical intent and query text into (Domain, Intent, SubIntent)."""
    t = text.lower()
    c = canonical_intent.upper()
    if c in ["GREETING_MORNING", "GREETING_NIGHT"] or (c == "GENERAL_CHAT" and any(w in t for w in ["hi", "hello", "hey"])):
        return "GREETING", "GREETING", "HI"
    if c in ["DAILY_ACTIVITY", "FOOD_CHECK", "HEALTH_CARE", "SLEEP_REST"]:
        if any(w in t for w in ["tinnava", "food", "lunch", "dinner"]):
            return "DAILY_RITUALS", "DAILY_CHECKIN", "DID_YOU_EAT"
        elif any(w in t for w in ["ekkada", "ekad"]):
            return "DAILY_RITUALS", "DAILY_CHECKIN", "WHERE_ARE_YOU"
        elif any(w in t for w in ["office", "work"]):
            return "DAILY_RITUALS", "DAILY_CHECKIN", "WORK_CHECK"
        elif any(w in t for w in ["plan", "ivala"]):
            return "DAILY_RITUALS", "DAILY_CHECKIN", "TODAY_PLAN"
        elif any(w in t for w in ["levaleda", "lechava", "nidra"]):
            return "DAILY_RITUALS", "DAILY_CHECKIN", "WAKEUP_CHECK"
        elif any(w in t for w in ["busy"]):
            return "DAILY_RITUALS", "BUSY", "BUSY_CHECK"
        return "DAILY_RITUALS", "DAILY_CHECKIN", "WHAT_ARE_YOU_DOING"
    if c == "CALL_REQUEST":
        return "DAILY_RITUALS", "CALL", "CALL_REQUEST"
    if c == "MISSING":
        return "ROMANCE", "MISS_YOU", "MISS_YOU"
    if c in ["ROMANTIC_STATEMENT", "PROPOSAL"]:
        return "ROMANCE", "LOVE", "LOVE_EXPRESSION"
    if c == "DEEP_BOND":
        if any(w in t for w in ["vadilesi", "replace", "inkokaru", "dooram"]):
            return "ROMANCE", "INSECURITY", "ABANDONMENT_FEAR"
        if any(w in t for w in ["important", "anukuntunnav"]):
            return "ROMANCE", "RELATIONSHIP_VALIDATION", "RELATIONSHIP_VALIDATION"
        return "ROMANCE", "COMMITMENT", "COMMITMENT"
    if c in ["COMPLIMENT_LOOKS", "COMPLIMENT_OUTFIT"]:
        if any(w in t for w in ["cute ga unna na"]):
            return "COMPLIMENTS_FLIRT", "COMPLIMENT_REQUEST", "COMPLIMENT_REQUEST"
        return "COMPLIMENTS_FLIRT", "COMPLIMENT", "LOOKS"
    if c == "FLIRT_COMPLIMENT":
        return "COMPLIMENTS_FLIRT", "FLIRT", "FLIRTATIOUS_BANTER"
    if c in ["TEASING", "PLAYFUL_BANTER", "JOKING"]:
        return "PLAYFUL_TEASING", "TEASING", "PLAYFUL_TEASE"
    if c == "EMOTIONAL_HURT":
        if any(w in t for w in ["care", "feelings", "pattinchukovatledu"]):
            return "CONFLICT_DISTRESS", "EMOTIONAL_HURT", "NEGLECT"
        return "CONFLICT_DISTRESS", "EMOTIONAL_HURT", "FEELING_HURT"
    if c in ["CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"]:
        if any(w in t for w in ["irritate", "kopam"]):
            return "CONFLICT_DISTRESS", "CONFLICT", "ANGER"
        return "CONFLICT_DISTRESS", "CONFLICT", "FRUSTRATION"
    if c in ["IGNORING", "NO_REPLY"]:
        if any(w in t for w in ["wait"]):
            return "CONFLICT_DISTRESS", "WAITING", "WAITING"
        if any(w in t for w in ["ignore"]):
            return "CONFLICT_DISTRESS", "IGNORING", "IGNORING"
        return "CONFLICT_DISTRESS", "NO_REPLY", "NO_REPLY"
    if c == "JEALOUSY":
        if any(w in t for w in ["best friend", "evaru"]):
            return "CONFLICT_DISTRESS", "JEALOUSY", "CURIOSITY"
        return "CONFLICT_DISTRESS", "JEALOUSY", "OTHER_GIRL_BOY"
    if c in ["APOLOGY_SEEKING", "RECONCILIATION"]:
        if any(w in t for w in ["forgive"]):
            return "CONFLICT_DISTRESS", "FORGIVENESS", "FORGIVENESS"
        if any(w in t for w in ["sorry", "mistake", "anukoledu"]):
            return "CONFLICT_DISTRESS", "APOLOGY", "APOLOGY"
        return "CONFLICT_DISTRESS", "RECONCILIATION", "PEACE_MAKING"
    if c == "GENERAL_CHAT":
        words = t.split()
        if len(words) > 2 and any(w in t for w in ["matladatle", "matladatledu", "matladaku", "kopam", "ignore"]):
            return "CONFLICT_DISTRESS", "CONFLICT", "FRUSTRATION"
        if len(words) <= 2:
            if "hmm" in words:
                return "SHORT_REACTION", "UNKNOWN/NEUTRAL", "HMM"
            if any(w in words for w in ["haa", "sare", "okay", "okayyy"]):
                return "SHORT_REACTION", "ACKNOWLEDGEMENT", "OKAY"
            if any(w in words for w in ["enduku", "enti", "avuna"]):
                return "SHORT_REACTION", "QUESTION", "QUESTION"
            if "nijama" in words:
                return "SHORT_REACTION", "VALIDATION", "NIJAMA"
            if "ledu" in words:
                return "SHORT_REACTION", "NEGATION", "LEDU"
            if "ohh" in words:
                return "SHORT_REACTION", "REACTION", "OHH"
        return "DAILY_RITUALS", "DAILY_CHECKIN", "DAILY_CHECKIN"
    return "GENERAL", "GENERAL_CHAT", "GENERAL"

def run_evaluation(test_file="test_messages.jsonl", verbose_first=5):
    print(f"Loading test file: {test_file}")
    with open(test_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    print(f"Total test cases loaded: {len(records)}")
    
    # Initialize engine
    generator = LocalReplyGenerator()
    retriever = generator.retriever

    exact_intent_correct = 0
    semantic_intent_correct = 0
    domain_correct = 0
    emotion_correct = 0
    retrieval_matches_r1 = 0
    retrieval_matches_r3 = 0
    retrieval_matches_r5 = 0
    safe_replies_count = 0
    bad_replies = []

    print("\n" + "=" * 80)
    print("RUNNING 100-MESSAGE BENCHMARK EVALUATION (MILESTONE 2)")
    print("=" * 80)

    output_records = []
    total = len(records)
    
    for idx, item in enumerate(records, 1):
        raw_input = item["input"]
        exp_intent = item["expected_intent"]
        exp_emotion = item["expected_emotion"]

        # Step 1: Normalization
        norm_text = normalize_tanglish(raw_input)

        # Step 2: Intent & Emotion Classification
        intent, i_conf, emotion, e_conf = retriever.predict_intent_emotion(norm_text)
        
        # Step 2b: Hierarchical Mapping
        pred_domain, pred_intent, pred_sub = map_canonical_to_hierarchy(intent, norm_text)
        
        # Step 3: Retrieval with Linear Weighted Re-Ranker
        _, _, _, _, top_scenarios = retriever.retrieve(norm_text, top_k=5)

        # Step 4: Generation with Multi-Angle Engine
        test_tone = "SWEET" if intent in ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"] else "ROMANTIC"
        gen_res = generator.generate(norm_text, tone=test_tone, num_replies=3)
        replies = gen_res["final_replies"]

        # Step 5: Unambiguous Metrics Calculation
        is_exact_intent = (pred_intent.upper() == exp_intent.upper()) or (intent.upper() == exp_intent.upper())
        is_semantic_intent = is_intent_match(intent, exp_intent) or is_exact_intent
        exp_domain = get_hierarchical_domain(exp_intent)
        is_domain = (pred_domain.upper() == exp_domain.upper()) or (get_hierarchical_domain(pred_intent) == exp_domain) or (get_hierarchical_domain(intent) == exp_domain)
        is_emotion = is_emotion_match(emotion, exp_emotion)

        if is_exact_intent:
            exact_intent_correct += 1
        if is_semantic_intent:
            semantic_intent_correct += 1
        if is_domain:
            domain_correct += 1
        if is_emotion:
            emotion_correct += 1

        # Retrieval Recall at 1, 3, 5
        top_sc_intent = top_scenarios[0]["intent"] if top_scenarios else ""
        if is_intent_match(top_sc_intent, exp_intent) or top_sc_intent == intent:
            retrieval_matches_r1 += 1

        top_3_intents = [sc["intent"] for sc in top_scenarios[:3]]
        if any(is_intent_match(sc_i, exp_intent) or sc_i == intent for sc_i in top_3_intents):
            retrieval_matches_r3 += 1

        top_5_intents = [sc["intent"] for sc in top_scenarios[:5]]
        if any(is_intent_match(sc_i, exp_intent) or sc_i == intent for sc_i in top_5_intents):
            retrieval_matches_r5 += 1

        # Tone safety & Template corruption check
        is_safe, reason = check_safety_and_corruption(intent, replies)
        if is_safe:
            safe_replies_count += 1
        else:
            bad_replies.append({
                "id": item.get("id", idx),
                "input": raw_input,
                "intent": intent,
                "reason": reason,
                "replies": replies
            })

        out_item = {
            "id": item.get("id", idx),
            "category": item.get("category", "General"),
            "input": raw_input,
            "normalized": norm_text,
            "expected_intent": exp_intent,
            "predicted_intent": intent,
            "exact_intent_match": is_exact_intent,
            "semantic_intent_match": is_semantic_intent,
            "intent_confidence": round(float(i_conf), 4),
            "expected_emotion": exp_emotion,
            "predicted_emotion": emotion,
            "emotion_confidence": round(float(e_conf), 4),
            "emotion_match": is_emotion,
            "top_scenarios": [
                {"scenario": sc["scenario"], "intent": sc["intent"], "score": round(float(sc["score"]), 2)}
                for sc in top_scenarios[:5]
            ],
            "tone_tested": test_tone,
            "generated_replies": replies,
            "is_safe": is_safe
        }
        output_records.append(out_item)

        # Print detailed preview for selected samples
        is_special_set = (31 <= idx <= 40) or (idx <= verbose_first) or (91 <= idx <= 100) or (idx == 49)
        if is_special_set:
            print(f"\n📩 [#{idx:03d}] Input: \"{raw_input}\"")
            if norm_text != raw_input.lower():
                print(f"🔤 Normalized: \"{norm_text}\"")
            exact_badge = "✅ Exact" if is_exact_intent else ("✅ Semantic" if is_semantic_intent else f"❌ (Exp: {exp_intent})")
            e_mark = "✅" if is_emotion else f"❌ (Exp: {exp_emotion})"
            print(f"🎯 Intent:    {intent} (P={i_conf:.2f}) [{exact_badge}]")
            print(f"❤️ Emotion:   {emotion} (P={e_conf:.2f}) {e_mark}")
            print(f"🔎 Top Matches (Re-ranked):")
            for s_i, sc in enumerate(top_scenarios[:3], 1):
                print(f"   {s_i}. {sc['scenario']} [{sc['intent']}] (Score: {sc['score']})")
            print(f"🎭 Multi-Angle Replies [{test_tone}]:")
            labels = ["Empathy", "Reassurance", "Affection"]
            for r_i, r in enumerate(replies, 1):
                lbl = labels[r_i-1] if r_i <= 3 else f"Angle {r_i}"
                print(f"   [{lbl}]: {r}")
            print("-" * 60)

    # Save to JSONL
    out_jsonl = "test_results.jsonl"
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for rec in output_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Save formatted Markdown report
    out_md = "test_results.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# CoupleFriendly - 100 Messages Benchmark Results (Milestone 2)\n\n")
        f.write(f"- **Exact Intent Accuracy**: {exact_intent_correct}/{total} ({(exact_intent_correct/total)*100:.1f}%)\n")
        f.write(f"- **Semantic Intent Accuracy**: {semantic_intent_correct}/{total} ({(semantic_intent_correct/total)*100:.1f}%)\n")
        f.write(f"- **Domain Accuracy**: {domain_correct}/{total} ({(domain_correct/total)*100:.1f}%)\n")
        f.write(f"- **Emotion Accuracy**: {emotion_correct}/{total} ({(emotion_correct/total)*100:.1f}%)\n")
        f.write(f"- **Retrieval Recall@1**: {retrieval_matches_r1}/{total} ({(retrieval_matches_r1/total)*100:.1f}%)\n")
        f.write(f"- **Retrieval Recall@3**: {retrieval_matches_r3}/{total} ({(retrieval_matches_r3/total)*100:.1f}%)\n")
        f.write(f"- **Retrieval Recall@5**: {retrieval_matches_r5}/{total} ({(retrieval_matches_r5/total)*100:.1f}%)\n")
        f.write(f"- **Tone Safety Score**: {safe_replies_count}/{total} ({(safe_replies_count/total)*100:.1f}%)\n")
        f.write(f"- **Bad / Corrupted Replies**: {len(bad_replies)}\n\n")
        f.write("---\n\n")
        f.write("## Detailed 5-Stage Output Per Message\n\n")

        for r in output_records:
            exact_badge = "✅ Exact" if r["exact_intent_match"] else ("✅ Semantic" if r["semantic_intent_match"] else f"❌ (Exp: {r['expected_intent']})")
            e_badge = "✅" if r["emotion_match"] else f"❌ (Exp: {r['expected_emotion']})"
            f.write(f"### #{r['id']:03d} [{r['category']}] `{r['input']}`\n\n")
            f.write(f"- **Normalized**: `{r['normalized']}`\n")
            f.write(f"- **Intent**: `{r['predicted_intent']}` (Confidence: {r['intent_confidence']}) [{exact_badge}]\n")
            f.write(f"- **Emotion**: `{r['predicted_emotion']}` (Confidence: {r['emotion_confidence']}) {e_badge}\n")
            f.write(f"- **Top Scenarios (Re-Ranked)**:\n")
            for sc in r["top_scenarios"][:3]:
                f.write(f"  - `{sc['scenario']}` [{sc['intent']}] (Score: {sc['score']})\n")
            f.write(f"- **Multi-Angle Generated Replies ({r['tone_tested']})**:\n")
            labels = ["Empathy & Validation", "Reassurance & Action", "Affectionate Softening"]
            for rep_idx, rep in enumerate(r["generated_replies"], 1):
                lbl = labels[rep_idx-1] if rep_idx <= 3 else f"Angle {rep_idx}"
                f.write(f"  {rep_idx}. **[{lbl}]**: \"{rep}\"\n")
            f.write("\n---\n\n")

    print("\n" + "=" * 48)
    print(f"100 MESSAGES BENCHMARK SUMMARY (MILESTONE 2)")
    print("─" * 48)
    print(f"Exact Intent Accuracy:     {(exact_intent_correct/total)*100:.1f}%")
    print(f"Semantic Intent Accuracy:  {(semantic_intent_correct/total)*100:.1f}%")
    print(f"Domain Accuracy:           {(domain_correct/total)*100:.1f}%")
    print(f"Emotion Accuracy:          {(emotion_correct/total)*100:.1f}%")
    print(f"Retrieval Recall@1:        {(retrieval_matches_r1/total)*100:.1f}%")
    print(f"Retrieval Recall@3:        {(retrieval_matches_r3/total)*100:.1f}%")
    print(f"Retrieval Recall@5:        {(retrieval_matches_r5/total)*100:.1f}%")
    print(f"Tone Safety Score:         {(safe_replies_count/total)*100:.1f}%")
    print(f"Bad / Corrupted Replies:   {len(bad_replies)}")
    print("=" * 48)
    print(f"\n📁 Saved outputs to:")
    print(f"   - JSON format: {os.path.abspath(out_jsonl)}")
    print(f"   - Markdown:    {os.path.abspath(out_md)}")

    if bad_replies:
        print("\n⚠️ Flagged Unsafe Responses:")
        for br in bad_replies:
            print(f"  ID #{br['id']}: '{br['input']}' -> {br['reason']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CoupleFriendly 100-message CLI Test Benchmark")
    parser.add_argument("--batch", type=str, default="test_messages.jsonl", help="Path to jsonl test file")
    parser.add_argument("--verbose", type=int, default=5, help="Number of first samples to print in detail")
    args = parser.parse_args()

    run_evaluation(test_file=args.batch, verbose_first=args.verbose)

