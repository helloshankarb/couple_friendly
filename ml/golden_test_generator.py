# -*- coding: utf-8 -*-
"""
Phase 3 — Golden Test Set Generator
Runs the frozen Python ML pipeline against the 100-message benchmark
and outputs golden reference results (JSON) for Kotlin parity comparison.

Output: ml/golden_test_results.json
"""

import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.normalizer import normalize_tanglish
from ml.semantic_retriever import SemanticRetriever

GOLDEN_TEST_MESSAGES = [
    # Test Set 1: Basic / Daily (1-10)
    "hi",
    "hiiii bujji",
    "em chesthunnav",
    "ekkada unnav",
    "tinnava",
    "office ki vellava",
    "ivala em plan",
    "inka levaleda",
    "busy ga unnav aa",
    "free ayyaka call cheyyi",
    # Test Set 2: Romantic (11-20)
    "nannu miss avuthunnava",
    "nenu gurthosthunnana",
    "nuvvu ante naaku chala ishtam",
    "nuvvu lekunda bore kodthundi",
    "nuvvu na life lo special",
    "na gurinchi em anukuntunnav",
    "nijanga nannu love chesthunnava",
    "nenu neeku entha important",
    "natho eppudu untava",
    "nee smile chusthe naa heart melt avuthundi",
    # Test Set 3: Playful / Teasing (21-30)
    "eh dumma",
    "nuvvu nacchav ante nacchav",
    "pakka drama queen eh nuvvu",
    "abbaa intha cute emiti nuvvu",
    "moham chupiyyi na bangaram",
    "photo pampav enti",
    "flirt chesthunnava natho",
    "nee voice vinali anipisthundi",
    "em anukuntunnav cheppu",
    "vadu ninnu chusi navvadu anta kadha",
    # Test Set 4: Conflict / Hurt (31-40)
    "nuvvu nannu hurt chesav",
    "edusthunna nee valla",
    "matladaku natho",
    "naa feelings ki value ledu neeku",
    "enduku ila chesthav",
    "nuvvu marchipoyav nannu",
    "oka sari kuda call cheyyaledu",
    "ignoring chesthunnav nannu",
    "nee meedha trust ledu inka",
    "breakup cheskundaam",
    # Test Set 5: Emotional Depth (41-50)
    "nuvvu lekunda baaga lonely ga feel avthunna",
    "nee meeda depend avthunna inka",
    "nuvvu naaku strength",
    "life lo nee tho ne happy",
    "entha dooram aina nee dhyasaloney untanu",
    "ninnu vadilesi vellalenu",
    "nuvvu na weakness",
    "nuvvu lekunda incomplete feel avthunna",
    "naa heart full ga nee daggare undi",
    "nuvvu naaku dheevena",
    # Test Set 6: Edge Cases (51-60)
    "ok",
    "hmm",
    "hahaha",
    "🥰🥰🥰",
    "...",
    "nenu bayataku velthunna",
    "night bujji",
    "good morning bangaram",
    "call cheyyava",
    "msg late ga chusanu sorry",
    # Test Set 7: Jealousy / Possessiveness (61-70)
    "evaru aa ammayi",
    "thaanu neetho enduku matladuthundhi",
    "nuvvu verevallaki navvuthav kani naaku kaadhu",
    "nuvvu andari tho ila untava",
    "nee phone lo aa contact evaru",
    "thaanu ninnu chusi navvindi",
    "vere ammayilatho matladaku",
    "nenu jealous feel avthunna",
    "nuvvu naaku maathrame kaadhu anipistundi",
    "neetho matlade rights naake undi",
    # Test Set 8: Commitments / Future (71-80)
    "manamu future lo kuda ilane untama",
    "nee parents ki cheppava manam gurinchi",
    "eppudu cheskundaam marriage",
    "nuvvu serious aa natho",
    "manam permanent kadha",
    "nuvvu inko relationship lo unte",
    "naa daggara eppudu untav kadha",
    "nuvvu nannu leave cheyyavu kadha",
    "manaki future undi kadha",
    "nuvvu naa last love",
    # Test Set 9: Mixed Emotion (81-90)
    "happy ga undi kani miss avthunna",
    "kopam ga undi kani love chesthunna",
    "hurt ayyanu kani forgive chesthunna",
    "excited ga undi nuvvu vachesthunnav kabatti",
    "boring ga undi nuvvu lekunda",
    "nervous ga undi first time",
    "confused ga undi about us",
    "proud ga undi nee gurinchi",
    "scared ga undi nuvvu vellipothe",
    "grateful ga undi nuvvu naa life lo",
    # Test Set 10: Stress Test (91-100)
    "nannu miss avuthunnava leda just chepthunnav",
    "nuvvu really nannu love chesthunnava leda acting aa",
    "breakup annam kabatti ippudu bagundi ani anukuntunnava",
    "naa kopam ninnu hurt chesindhi ante sorry",
    "night 2 ki msg chesthe reply ivvaledu enduku",
    "nee friend nuvvu nannu love chesthav ani nammadu",
    "manaku future ledu anipistundi sometimes",
    "nenu change avthunna neekosam",
    "nuvvu naa life lo undadam naa luck",
    "i love you bujji forever and ever",
]


def run_golden_tests():
    print("Loading SemanticRetriever engine...")
    retriever = SemanticRetriever()

    results = []
    for idx, msg in enumerate(GOLDEN_TEST_MESSAGES, start=1):
        # 1. Normalize
        normalized = normalize_tanglish(msg)

        # 2. Classify intent & emotion via retriever (it bundles both)
        intent_label, intent_conf, emotion_label, emotion_conf, top_scenarios = retriever.retrieve(normalized, top_k=5)

        top_incomings = [s["scenario"] for s in top_scenarios] if top_scenarios else []
        top1_incoming = top_incomings[0] if top_incomings else ""

        results.append({
            "test_id": idx,
            "raw_input": msg,
            "normalized": normalized,
            "intent": intent_label,
            "intent_confidence": round(float(intent_conf), 4),
            "emotion": emotion_label,
            "emotion_confidence": round(float(emotion_conf), 4),
            "top1_scenario_incoming": top1_incoming,
            "top5_scenario_incomings": top_incomings[:5]
        })

    return results


if __name__ == "__main__":
    print("Running golden test set (100 messages)...")
    results = run_golden_tests()

    out_path = os.path.join("ml", "golden_test_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Golden test results saved to {out_path}")
    print(f"   {len(results)} test cases recorded")

    # Summary stats
    intents = set(r["intent"] for r in results)
    emotions = set(r["emotion"] for r in results)
    print(f"   Unique intents: {len(intents)}")
    print(f"   Unique emotions: {len(emotions)}")
    print(f"   Mean intent confidence: {sum(r['intent_confidence'] for r in results) / len(results):.4f}")
    print(f"   Mean emotion confidence: {sum(r['emotion_confidence'] for r in results) / len(results):.4f}")
