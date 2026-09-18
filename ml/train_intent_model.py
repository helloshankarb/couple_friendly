# -*- coding: utf-8 -*-
"""
CoupleFriendly - Model 1: Intent & Emotion Classifier Trainer
Trains a high-speed, sub-millisecond Char+Word N-gram classifier with scikit-learn.
Evaluates on held-out test set and hard-negative discrimination suite.
"""

import json
import os
import sys
import pickle

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score

MODELS_DIR = os.path.join("ml", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TRAIN_PATH = os.path.join("ml", "data", "splits", "intent_train.jsonl")
VAL_PATH = os.path.join("ml", "data", "splits", "intent_val.jsonl")
TEST_PATH = os.path.join("ml", "data", "splits", "intent_test.jsonl")
HARD_NEG_PATH = os.path.join("ml", "data", "hard_negatives.jsonl")

def load_jsonl(path):
    texts, labels = [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                texts.append(item["text"])
                labels.append(item["intent"])
    return texts, labels

def train_and_eval():
    print("Loading training, validation, and test datasets...")
    train_texts, train_labels = load_jsonl(TRAIN_PATH)
    val_texts, val_labels = load_jsonl(VAL_PATH)
    test_texts, test_labels = load_jsonl(TEST_PATH)

    print(f"Train samples: {len(train_texts)}")
    print(f"Val samples:   {len(val_texts)}")
    print(f"Test samples:  {len(test_texts)}")

    # Feature Union: Word (1-2) grams + Character (3-5) grams for Tanglish morphology & typos
    print("\nBuilding Char+Word Hybrid N-Gram Vectorizer...")
    word_vec = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
        analyzer="word"
    )
    char_vec = TfidfVectorizer(
        ngram_range=(3, 5),
        min_df=3,
        sublinear_tf=True,
        analyzer="char"
    )

    union = FeatureUnion([
        ("word", word_vec),
        ("char", char_vec)
    ])

    X_train = union.fit_transform(train_texts)
    X_val = union.transform(val_texts)
    X_test = union.transform(test_texts)

    print(f"Total vocabulary features: {X_train.shape[1]}")

    print("\nTraining Calibrated Logistic Regression Classifier...")
    clf = LogisticRegression(
        C=2.5,
        max_iter=500,
        solver="lbfgs",
        class_weight="balanced",
        random_state=42
    )
    clf.fit(X_train, train_labels)

    # Validation Evaluation
    val_preds = clf.predict(X_val)
    val_acc = accuracy_score(val_labels, val_preds)
    val_f1 = f1_score(val_labels, val_preds, average="macro")
    print(f"Validation Accuracy: {val_acc * 100:.2f}% | Macro F1: {val_f1 * 100:.2f}%")

    # Test Evaluation
    test_preds = clf.predict(X_test)
    test_acc = accuracy_score(test_labels, test_preds)
    test_f1 = f1_score(test_labels, test_preds, average="macro")
    print(f"Test Set Accuracy:   {test_acc * 100:.2f}% | Macro F1: {test_f1 * 100:.2f}%")

    # Hard-Negative Discrimination Evaluation
    print("\nEvaluating Hard-Negative Discrimination...")
    with open(HARD_NEG_PATH, "r", encoding="utf-8") as f:
        hard_negs = [json.loads(line) for line in f if line.strip()]

    hn_correct = 0
    for hn in hard_negs:
        anchor = hn["anchor"]
        expected = hn["correct_intent"]
        confuser = hn["negative_intent"]
        
        vec = union.transform([anchor])
        pred = clf.predict(vec)[0]
        
        if pred == expected:
            hn_correct += 1

    hn_acc = (hn_correct / len(hard_negs)) * 100
    print(f"Hard-Negative Accuracy: {hn_correct}/{len(hard_negs)} ({hn_acc:.2f}%)")

    # Critical Hard-Negative Test Pairs
    critical_tests = [
        ("Nannu enduku tease chesthunnav", "TEASING"),
        ("Enduku nannu ila edipisthunnav", "EMOTIONAL_HURT"),
        ("Nuvvu nannu hurt chesav", "EMOTIONAL_HURT"),
        ("Na meeda enduku kopam", "ANGER_ARGUMENT"),
        ("Neeku oka sari chepthe ardham kaada", "CONFLICT_FRUSTRATION"),
        ("Neeku oka sari cehpthe ardham kaada", "CONFLICT_FRUSTRATION"),
        ("Inkeppudu naku call or msg ceyyaku", "BREAKUP_THREATS"),
        ("Nuvvu nannu ignore chesthunnav", "IGNORING"),
        ("Enduku reply ivvatledu", "NO_REPLY"),
        ("Good morning bujji lechava", "GREETING_MORNING"),
        ("Tinnava bujji eeroju em curry", "FOOD_CHECK")
    ]

    print("\n--- Live Critical Hard-Negative Test Pairs ---")
    for text, expected in critical_tests:
        vec = union.transform([text])
        probs = clf.predict_proba(vec)[0]
        pred_idx = np.argmax(probs)
        pred_class = clf.classes_[pred_idx]
        conf = probs[pred_idx]
        
        status = "✅ PASS" if pred_class == expected else "❌ FAIL"
        print(f"{status} | \"{text:<36}\" -> {pred_class:<22} (Conf: {conf:.2f}, Expected: {expected})")

    # Export Model Artifacts
    model_bundle = {
        "vectorizer": union,
        "classifier": clf,
        "classes": list(clf.classes_)
    }
    bundle_path = os.path.join(MODELS_DIR, "intent_model_bundle.pkl")
    with open(bundle_path, "wb") as f:
        pickle.dump(model_bundle, f)
    print(f"\nModel artifact saved to: {bundle_path}")

if __name__ == "__main__":
    train_and_eval()
