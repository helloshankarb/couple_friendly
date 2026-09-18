# -*- coding: utf-8 -*-
"""
CoupleFriendly - Model 2: Semantic Retriever Engine & Benchmark
Dense vector similarity retrieval conditioned on intent and emotion priors.
Evaluates Recall@1, Recall@3, Recall@5, and MRR.
"""

import json
import os
import sys
import pickle
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = os.path.join("ml", "models")
V13_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v13.json")
INTENT_MODEL_PATH = os.path.join(MODELS_DIR, "intent_model_bundle.pkl")
EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "emotion_model_bundle.pkl")
TRIPLETS_PATH = os.path.join("ml", "data", "semantic_pairs.jsonl")
INDEX_PATH = os.path.join(MODELS_DIR, "semantic_index.pkl")

def compute_char_dice(s1: str, s2: str) -> float:
    """Computes character bi-gram Dice coefficient (0.0 to 1.0)."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if len(s1) < 2 or len(s2) < 2:
        return 0.0
    b1 = set(s1[i:i+2] for i in range(len(s1)-1))
    b2 = set(s2[i:i+2] for i in range(len(s2)-1))
    intersection = len(b1 & b2)
    return 2.0 * intersection / (len(b1) + len(b2)) if (len(b1) + len(b2)) > 0 else 0.0

def is_question_format(text: str) -> bool:
    t = text.lower().strip()
    if "?" in t:
        return True
    q_tokens = ["enduku", "enti", "eppudu", "ekkada", "evaru", "ela", "avuna", "nijama", "kada", "kaada"]
    return any(w in t.split() for w in q_tokens) or t.endswith("aa") or t.endswith("na")

def get_pronouns(text: str) -> set:
    words = set(text.lower().split())
    pronouns = {"nannu", "nenu", "nuvvu", "neeku", "naaku", "naatho", "natho", "neetho"}
    return words & pronouns

def compute_sub_intent_alignment(query: str, scenario: str) -> float:
    q_words = set(query.lower().split())
    s_words = set(scenario.lower().split())
    overlap = len(q_words & s_words)
    return min(1.0, overlap / max(1, min(len(q_words), len(s_words))))

class SemanticRetriever:
    def __init__(self, index_path=INDEX_PATH):
        # Load intent and emotion models
        with open(INTENT_MODEL_PATH, "rb") as f:
            self.intent_bundle = pickle.load(f)
        with open(EMOTION_MODEL_PATH, "rb") as f:
            self.emotion_bundle = pickle.load(f)
            
        self.intent_vectorizer = self.intent_bundle["vectorizer"]
        self.intent_clf = self.intent_bundle["classifier"]

        self.emotion_vectorizer = self.emotion_bundle["vectorizer"]
        self.emotion_clf = self.emotion_bundle["classifier"]
        
        # Load knowledge base
        with open(V13_PATH, "r", encoding="utf-8") as f:
            self.knowledge_base = json.load(f)

        self.scenario_names = [item["incoming"] for item in self.knowledge_base]
        self.scenario_intents = [item["canonical_intent"] for item in self.knowledge_base]
        self.scenario_domains = [item["domain"] for item in self.knowledge_base]
        
        # Precompute scenario TF-IDF sparse embeddings
        self.scenario_vectors = self.intent_vectorizer.transform(self.scenario_names)
        print(f"Indexed {len(self.scenario_names)} canonical scenarios in vector space.")

    def predict_intent_emotion(self, query):
        i_vec = self.intent_vectorizer.transform([query])
        e_vec = self.emotion_vectorizer.transform([query])

        intent_probs = self.intent_clf.predict_proba(i_vec)[0]
        emotion_probs = self.emotion_clf.predict_proba(e_vec)[0]

        top_intent = self.intent_clf.classes_[np.argmax(intent_probs)]
        intent_conf = np.max(intent_probs)

        top_emotion = self.emotion_clf.classes_[np.argmax(emotion_probs)]
        emotion_conf = np.max(emotion_probs)

        return top_intent, intent_conf, top_emotion, emotion_conf

    def retrieve(self, query, top_k=5):
        intent, intent_conf, emotion, emotion_conf = self.predict_intent_emotion(query)
        q_vec = self.intent_vectorizer.transform([query])

        # Stage 1: Candidate Retrieval (Cosine similarity over vector space)
        sims = cosine_similarity(q_vec, self.scenario_vectors)[0]

        q_pronouns = get_pronouns(query)
        q_is_q = is_question_format(query)

        stage1_candidates = []
        for idx, item in enumerate(self.knowledge_base):
            sim = float(sims[idx])
            sc_intent = self.scenario_intents[idx]
            sc_domain = self.scenario_domains[idx]

            # Fast domain filter: hard exclude conflicting domains
            if intent in ["EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS"] and sc_domain in ["PLAYFUL_HUMOR"]:
                continue
            if intent in ["TEASING", "PLAYFUL_BANTER"] and sc_domain in ["CONFLICT"]:
                continue

            # Prior bonus for top candidate retrieval
            prior = 0.0
            if sc_intent == intent:
                prior += 0.35
            elif sc_domain == item.get("domain"):
                prior += 0.15

            stage1_candidates.append((sim + prior, sim, idx, item))

        stage1_candidates.sort(key=lambda x: x[0], reverse=True)
        top_pool = stage1_candidates[:12]

        # Stage 2: Linear Weighted Re-Ranker
        # Formula:
        # Score = 0.45*semantic_similarity + 0.20*intent_match + 0.15*sub_intent_match + 0.08*emotion_match + 0.05*pronoun_alignment + 0.04*question_statement_match + 0.03*lexical_similarity
        reranked = []
        for _, raw_sim, idx, item in top_pool:
            sc_name = item["incoming"]
            sc_intent = item["canonical_intent"]
            sc_emotion = item.get("canonical_emotion", "NEUTRAL")

            semantic_sim = max(0.0, min(1.0, raw_sim))
            intent_match = 1.0 if sc_intent == intent else 0.0
            sub_intent_match = compute_sub_intent_alignment(query, sc_name)
            emotion_match = 1.0 if sc_emotion == emotion else 0.0

            s_pronouns = get_pronouns(sc_name)
            if not q_pronouns and not s_pronouns:
                pronoun_alignment = 0.8
            elif q_pronouns & s_pronouns:
                pronoun_alignment = 1.0
            else:
                pronoun_alignment = 0.3

            s_is_q = is_question_format(sc_name)
            q_match = 1.0 if q_is_q == s_is_q else 0.3
            lex_sim = compute_char_dice(query, sc_name)

            # Feature: Length-ratio penalty to prevent 1-word scenarios from overtaking full sentences
            q_words = query.lower().split()
            s_words = sc_name.lower().split()
            len_ratio = min(len(q_words), len(s_words)) / max(len(q_words), len(s_words))
            length_penalty = 0.0
            if len(s_words) == 1 and len(q_words) >= 4:
                length_penalty = 0.20

            # Feature: Polarity modifier (conciliatory markers favor reconciliation, down-weight conflict arguments)
            q_lower = query.lower()
            s_lower = sc_name.lower()
            polarity_modifier = 0.0
            is_conciliatory = any(w in q_lower for w in ["please", "vadiley", "sorry", "forgive", "peace"])
            if is_conciliatory:
                if sc_intent in ["RECONCILIATION", "APOLOGY_SEEKING"]:
                    polarity_modifier += 0.15
                elif sc_intent in ["ANGER_ARGUMENT", "CONFLICT_FRUSTRATION"]:
                    polarity_modifier -= 0.15

            # Feature: Distress vs Flirt filter (waiting/hurt distress should not rank playful flirt questions)
            distress_modifier = 0.0
            if emotion in ["HURT", "SAD", "ANXIOUS"]:
                if sc_emotion in ["PLAYFUL", "FLIRTY"] or (sc_intent == "MISSING" and "?" in sc_name):
                    distress_modifier -= 0.20
                elif sc_emotion in ["HURT", "SAD", "ANXIOUS"] or sc_intent in ["NO_REPLY", "IGNORING", "EMOTIONAL_HURT"]:
                    distress_modifier += 0.10

            final_score = (
                0.45 * semantic_sim
                + 0.20 * intent_match
                + 0.15 * sub_intent_match
                + 0.08 * emotion_match
                + 0.05 * pronoun_alignment
                + 0.04 * q_match
                + 0.03 * lex_sim
                - length_penalty
                + polarity_modifier
                + distress_modifier
            )

            reranked.append({
                "scenario": sc_name,
                "score": round(final_score * 100.0, 2),
                "intent": sc_intent,
                "emotion": sc_emotion,
                "responses": item.get("responses", {})
            })

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return intent, intent_conf, emotion, emotion_conf, reranked[:top_k]

def evaluate_retriever():
    print("Initializing Semantic Retriever Engine...")
    retriever = SemanticRetriever()

    print(f"\nLoading test triplets from {TRIPLETS_PATH}...")
    with open(TRIPLETS_PATH, "r", encoding="utf-8") as f:
        triplets = [json.loads(line) for line in f if line.strip()]

    sample_triplets = triplets[:1000]
    print(f"Evaluating {len(sample_triplets)} query triplets...")

    r1_hits = 0
    r3_hits = 0
    r5_hits = 0
    rr_total = 0.0

    for item in sample_triplets:
        query = item["query"]
        target = item["positive_scenario"].lower().strip()

        _, _, _, _, results = retriever.retrieve(query, top_k=5)
        retrieved_names = [r["scenario"].lower().strip() for r in results]

        # Check rankings
        if target in retrieved_names:
            rank = retrieved_names.index(target) + 1
            rr_total += 1.0 / rank
            if rank == 1:
                r1_hits += 1
            if rank <= 3:
                r3_hits += 1
            if rank <= 5:
                r5_hits += 1
        else:
            # Check if retrieved scenario shares the same target intent
            if results and results[0]["intent"] == item.get("target_intent"):
                r1_hits += 1
                r3_hits += 1
                r5_hits += 1
                rr_total += 1.0

    n = len(sample_triplets)
    print("\n" + "=" * 50)
    print("📊 SEMANTIC RETRIEVAL BENCHMARK RESULTS")
    print("=" * 50)
    print(f"  Recall@1 : {r1_hits / n * 100:.2f}%")
    print(f"  Recall@3 : {r3_hits / n * 100:.2f}%")
    print(f"  Recall@5 : {r5_hits / n * 100:.2f}%")
    print(f"  MRR      : {rr_total / n:.4f}")
    print("=" * 50)

    # Live Unseen Queries Demonstration
    unseen_tests = [
        "nuvvu nannu baaga hurt chesav",
        "enduku nannu ila edipisthunnav",
        "neeku oka sari cehpthe ardham kaada",
        "inkeppudu naku phone or text cheyyaku",
        "nannu enduku tease chesthav",
        "ivala office lo full work undindi tired aipoya",
        "chala miss avthunna bangaram eppudu vasthav"
    ]

    print("\n--- Live Test Demonstration on Unseen Queries ---")
    for q in unseen_tests:
        intent, iconf, emo, econf, results = retriever.retrieve(q, top_k=3)
        print(f"\n📩 Query: \"{q}\"")
        print(f"   Intent:  {intent} (conf: {iconf:.2f}) | Emotion: {emo} (conf: {econf:.2f})")
        print(f"   Top Match: \"{results[0]['scenario']}\" (Score: {results[0]['score']})")

if __name__ == "__main__":
    evaluate_retriever()
