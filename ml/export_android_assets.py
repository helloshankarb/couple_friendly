# -*- coding: utf-8 -*-
"""
CoupleFriendly - Phase 3 Production Asset Exporter for Android
Exports frozen Milestone 2.1 Python ML models and dataset
into validated, Android-readable JSON assets for native Kotlin inference.

Validates:
  - model bundle existence and required fields
  - coefficient dimension matching
  - vocabulary uniqueness
  - scenario vector validity
  - canonical tag completeness
"""

import json
import os
import sys
import pickle
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join("app", "src", "main", "assets", "ml")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS_DIR = os.path.join("ml", "models")
V13_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v13.json")
INTENT_MODEL_PATH = os.path.join(MODELS_DIR, "intent_model_bundle.pkl")
EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "emotion_model_bundle.pkl")

EXPORT_VERSION = 1
errors = []

def validate_file_exists(path, label):
    if not os.path.isfile(path):
        errors.append(f"MISSING: {label} at {path}")
        return False
    return True

def export_classifier(bundle_path, output_filename, model_name="Intent"):
    print(f"Exporting {model_name} classifier from {bundle_path}...")

    if not validate_file_exists(bundle_path, f"{model_name} model bundle"):
        return None, 0, 0

    with open(bundle_path, "rb") as f:
        bundle = pickle.load(f)

    for key in ["vectorizer", "classifier"]:
        if key not in bundle:
            errors.append(f"{model_name}: missing '{key}' in bundle")
            return None, 0, 0

    vectorizer = bundle["vectorizer"]
    clf = bundle["classifier"]

    # Decompose FeatureUnion
    if not hasattr(vectorizer, 'transformer_list') or len(vectorizer.transformer_list) < 2:
        errors.append(f"{model_name}: vectorizer is not a FeatureUnion with word+char components")
        return None, 0, 0

    word_vec = vectorizer.transformer_list[0][1]
    char_vec = vectorizer.transformer_list[1][1]

    word_vocab = word_vec.vocabulary_
    word_idf = word_vec.idf_
    char_vocab = char_vec.vocabulary_
    char_idf = char_vec.idf_

    num_word_feats = len(word_vocab)
    num_char_feats = len(char_vocab)
    total_feats = num_word_feats + num_char_feats

    classes = clf.classes_.tolist()
    num_classes = len(classes)
    intercepts = clf.intercept_
    coef = clf.coef_

    # Validate coefficient dimensions
    if coef.shape[0] != num_classes:
        errors.append(f"{model_name}: coef rows ({coef.shape[0]}) != classes ({num_classes})")
    if coef.shape[1] != total_feats:
        errors.append(f"{model_name}: coef cols ({coef.shape[1]}) != total features ({total_feats})")
    if intercepts.shape[0] != num_classes:
        errors.append(f"{model_name}: intercept length ({intercepts.shape[0]}) != classes ({num_classes})")

    # Validate IDF dimensions
    if len(word_idf) != num_word_feats:
        errors.append(f"{model_name}: word IDF length ({len(word_idf)}) != word vocab ({num_word_feats})")
    if len(char_idf) != num_char_feats:
        errors.append(f"{model_name}: char IDF length ({len(char_idf)}) != char vocab ({num_char_feats})")

    # Validate vocabulary uniqueness
    word_indices = list(word_vocab.values())
    if len(word_indices) != len(set(word_indices)):
        errors.append(f"{model_name}: duplicate word feature indices found")
    char_indices = list(char_vocab.values())
    if len(char_indices) != len(set(char_indices)):
        errors.append(f"{model_name}: duplicate char feature indices found")

    # Extract normalization metadata
    word_norm = getattr(word_vec, 'norm', 'l2')
    char_norm = getattr(char_vec, 'norm', 'l2')
    word_sublinear = getattr(word_vec, 'sublinear_tf', False)
    char_sublinear = getattr(char_vec, 'sublinear_tf', False)

    data = {
        "version": EXPORT_VERSION,
        "model_name": model_name,
        "feature_config": {
            "word_ngram_min": word_vec.ngram_range[0],
            "word_ngram_max": word_vec.ngram_range[1],
            "char_ngram_min": char_vec.ngram_range[0],
            "char_ngram_max": char_vec.ngram_range[1],
            "word_analyzer": "word",
            "char_analyzer": "char",
            "word_norm": word_norm,
            "char_norm": char_norm,
            "word_sublinear_tf": word_sublinear,
            "char_sublinear_tf": char_sublinear
        },
        "classes": classes,
        "intercepts": np.round(intercepts, 6).tolist(),
        "num_word_features": num_word_feats,
        "num_char_features": num_char_feats,
        "word_vocab": word_vocab,
        "word_idf": np.round(word_idf, 6).tolist(),
        "char_vocab": char_vocab,
        "char_idf": np.round(char_idf, 6).tolist(),
        "coefficients": np.round(coef, 6).tolist()
    }

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(',', ':'))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  -> {output_filename}: {size_kb:.1f} KB  ({num_classes} classes, {total_feats} features)")
    return bundle, num_classes, total_feats

def export_scenarios_index(intent_bundle):
    print(f"Exporting Scenarios Vector Index from {V13_PATH}...")

    if not validate_file_exists(V13_PATH, "v13 dataset"):
        return 0, 0

    with open(V13_PATH, "r", encoding="utf-8") as f:
        kb = json.load(f)

    if not kb:
        errors.append("Dataset is empty")
        return 0, 0

    vectorizer = intent_bundle["vectorizer"]

    # Import normalizer for normalized text
    try:
        from ml.normalizer import normalize_tanglish
    except ImportError:
        from normalizer import normalize_tanglish

    scenario_names = [item["incoming"] for item in kb]
    tfidf_mat = vectorizer.transform(scenario_names)

    total_replies = 0
    indexed_items = []
    for idx, item in enumerate(kb):
        row = tfidf_mat[idx]
        coo = row.tocoo()
        sparse_indices = coo.col.tolist()
        sparse_values = coo.data.copy()

        # L2-normalize for cosine similarity
        norm = float(np.sqrt(np.sum(sparse_values ** 2)))
        if norm > 0:
            sparse_values = sparse_values / norm

        # Validate sparse values
        if np.any(np.isnan(sparse_values)) or np.any(np.isinf(sparse_values)):
            errors.append(f"Scenario {idx} '{item['incoming']}': invalid sparse values (NaN/Inf)")
            continue

        sparse_values = np.round(sparse_values, 6).tolist()

        # Validate canonical tags
        canonical_intent = item.get("canonical_intent", "")
        canonical_emotion = item.get("canonical_emotion", "")
        if not canonical_intent:
            errors.append(f"Scenario {idx} '{item['incoming']}': missing canonical_intent")
        if not canonical_emotion:
            errors.append(f"Scenario {idx} '{item['incoming']}': missing canonical_emotion")

        # Collect responses for all tones
        responses_clean = {}
        for tone in ["romantic", "sweet", "funny", "bold"]:
            t_list = []
            raw_list = item.get("responses", {}).get(tone, [])
            for r in raw_list:
                text = r.get("text", "") if isinstance(r, dict) else str(r)
                if text.strip():
                    t_list.append(text.strip())
            responses_clean[tone] = t_list
            total_replies += len(t_list)

        indexed_items.append({
            "id": idx,
            "incoming": item["incoming"],
            "normalized": normalize_tanglish(item["incoming"]),
            "category": item.get("category", "casual_chat"),
            "domain": item.get("domain", "GENERAL"),
            "intent": canonical_intent or "GENERAL_CHAT",
            "sub_intent": item.get("sub_intent", ""),
            "emotion": canonical_emotion or "NEUTRAL",
            "sparse_indices": sparse_indices,
            "sparse_values": sparse_values,
            "responses": responses_clean
        })

    out_path = os.path.join(OUTPUT_DIR, "scenarios_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(indexed_items, f, separators=(',', ':'))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  -> scenarios_index.json: {size_kb:.1f} KB  ({len(indexed_items)} scenarios, {total_replies} replies)")
    return len(indexed_items), total_replies

def export_normalizer_rules():
    print("Exporting Normalizer Rules...")
    try:
        from ml.normalizer import PHONETIC_TYPO_MAP
    except ImportError:
        from normalizer import PHONETIC_TYPO_MAP

    rules = {
        "version": EXPORT_VERSION,
        "elongation_compression": {
            "pattern": "([a-zA-Z])\\1{2,}",
            "replacement": "\\1",
            "description": "Compress 3+ repeated characters to 1"
        },
        "punctuation_rules": {
            "repeated_punctuation": "([!?.,])\\1+",
            "replacement": "\\1"
        },
        "phonetic_typo_map": PHONETIC_TYPO_MAP,
        "pronoun_corrections": {
            "meeru": "nuvvu",
            "ela unnaru": "ela unnav",
            "meere": "nuvve"
        },
        "pronouns": ["nannu", "nenu", "nuvvu", "neeku", "naaku", "naatho", "natho", "neetho"],
        "question_tokens": ["enduku", "enti", "eppudu", "ekkada", "evaru", "ela", "avuna", "nijama", "kada", "kaada"],
        "conciliatory_tokens": ["please", "vadiley", "sorry", "forgive", "peace"],
        "crying_tokens": ["edip", "edav", "yedus", "edupu", "crying"],
        "feelings_tokens": ["feelings", "care cheyyatledu", "pattinchukovatledu"],
        "breakup_tokens": [
            "inkeppudu", "inka eppudu", "block chestha", "block chesta",
            "breakup", "vellipotha", "naa valla kaadu", "single ga untanu",
            "dooram undu", "dooranga undu"
        ],
        "frustration_tokens": [
            "ardham kaada", "ardham kaadha", "ardham avvatleda", "ardham kavatleda",
            "ardham kavatledha", "ardham cheskova", "ardham chesukova",
            "oka sari chepthe", "okkasari chepthe", "enni sarlu",
            "chepthe vinava", "cheppindi vinava", "vinara", "vinava",
            "buddhi leda", "mind leda", "sense leda", "visugu", "visugosthondi",
            "visiginchaku", "chiraku", "chimpestha", "gola cheyyaku"
        ]
    }

    num_rules = len(PHONETIC_TYPO_MAP) + len(rules["pronoun_corrections"])
    out_path = os.path.join(OUTPUT_DIR, "normalizer_rules.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  -> normalizer_rules.json: {size_kb:.1f} KB  ({num_rules} substitution rules)")
    return num_rules

if __name__ == "__main__":
    print("=" * 50)
    print("Android ML Asset Export")
    print("=" * 50)
    print()

    # Validate source files exist before any processing
    all_sources_exist = True
    for path, label in [
        (INTENT_MODEL_PATH, "Intent model bundle"),
        (EMOTION_MODEL_PATH, "Emotion model bundle"),
        (V13_PATH, "v13 dataset"),
    ]:
        if not os.path.isfile(path):
            print(f"  FATAL: {label} not found at {path}")
            all_sources_exist = False

    if not all_sources_exist:
        print("\nValidation:            FAIL")
        print("Cannot proceed without all source assets.")
        sys.exit(1)

    intent_bundle, intent_classes, intent_feats = export_classifier(
        INTENT_MODEL_PATH, "intent_classifier.json", "Intent"
    )
    emotion_bundle, emotion_classes, emotion_feats = export_classifier(
        EMOTION_MODEL_PATH, "emotion_classifier.json", "Emotion"
    )

    num_scenarios, num_replies = 0, 0
    if intent_bundle:
        num_scenarios, num_replies = export_scenarios_index(intent_bundle)

    num_normalizer_rules = export_normalizer_rules()

    # Calculate total asset size
    total_size = 0
    for fname in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(fpath):
            total_size += os.path.getsize(fpath)

    print()
    print("-" * 50)
    print(f"Intent features:       {intent_feats}")
    print(f"Intent classes:        {intent_classes}")
    print(f"Emotion features:      {emotion_feats}")
    print(f"Emotion classes:       {emotion_classes}")
    print(f"Scenarios:             {num_scenarios}")
    print(f"Replies:               {num_replies}")
    print(f"Normalizer rules:      {num_normalizer_rules}")
    print(f"Total asset size:      {total_size / 1024:.1f} KB ({total_size / (1024*1024):.2f} MB)")
    print()

    if errors:
        print(f"Validation:            FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("Validation:            PASS")
        print()
        print("✅ All Android ML assets exported and validated successfully.")
