# -*- coding: utf-8 -*-
"""
CoupleFriendly - Model 1b: Emotion Classifier Trainer
Trains a high-speed, sub-millisecond Char+Word N-gram emotion classifier with scikit-learn.
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
from sklearn.metrics import accuracy_score, f1_score

MODELS_DIR = os.path.join("ml", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

DATA_PATH = os.path.join("ml", "data", "emotion_dataset.jsonl")

def load_data():
    texts, labels = [], []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                texts.append(item["text"])
                labels.append(item["emotion"])
    return texts, labels

def train_and_eval():
    print("Loading emotion dataset...")
    texts, labels = load_data()
    print(f"Total samples: {len(texts)}")

    # 80/20 train/test split
    n = len(texts)
    n_train = int(n * 0.8)
    train_texts, train_labels = texts[:n_train], labels[:n_train]
    test_texts, test_labels = texts[n_train:], labels[n_train:]

    print("\nBuilding Char+Word Hybrid N-Gram Vectorizer for Emotion...")
    word_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, analyzer="word")
    char_vec = TfidfVectorizer(ngram_range=(3, 5), min_df=3, sublinear_tf=True, analyzer="char")

    union = FeatureUnion([("word", word_vec), ("char", char_vec)])
    X_train = union.fit_transform(train_texts)
    X_test = union.transform(test_texts)

    print(f"Total emotion features: {X_train.shape[1]}")

    print("\nTraining Emotion Logistic Regression Classifier...")
    clf = LogisticRegression(C=2.5, max_iter=500, solver="lbfgs", class_weight="balanced", random_state=42)
    clf.fit(X_train, train_labels)

    test_preds = clf.predict(X_test)
    test_acc = accuracy_score(test_labels, test_preds)
    test_f1 = f1_score(test_labels, test_preds, average="macro")
    print(f"Emotion Test Set Accuracy: {test_acc * 100:.2f}% | Macro F1: {test_f1 * 100:.2f}%")

    # Critical Emotion Verification
    test_cases = [
        ("Enduku nannu ila edipisthunnav", "HURT"),
        ("Nannu enduku tease chesthunnav", "PLAYFUL"),
        ("Na meeda enduku kopam", "ANGRY"),
        ("Neeku oka sari cehpthe ardham kaada", "ANGRY"),
        ("Chala miss avthunna bujji", "MISSING"),
        ("Nuvve naa pranam bangaram", "ROMANTIC"),
        ("A ammai evaru neetho photo lo unnadhi", "JEALOUS")
    ]

    print("\n--- Live Critical Emotion Test Pairs ---")
    for text, expected in test_cases:
        vec = union.transform([text])
        pred = clf.predict(vec)[0]
        status = "✅ PASS" if pred == expected else "❌ FAIL"
        print(f"{status} | \"{text:<38}\" -> Emotion: {pred:<12} (Expected: {expected})")

    # Export Model Artifact
    bundle = {
        "vectorizer": union,
        "classifier": clf,
        "classes": list(clf.classes_)
    }
    bundle_path = os.path.join(MODELS_DIR, "emotion_model_bundle.pkl")
    with open(bundle_path, "wb") as f:
        pickle.dump(bundle, f)
    print(f"\nEmotion model artifact saved to: {bundle_path}")

if __name__ == "__main__":
    train_and_eval()
