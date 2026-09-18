import sys
sys.path.insert(0, '.')
import json
from cli_test import is_intent_match, is_emotion_match
from ml.normalizer import normalize_tanglish
from ml.semantic_retriever import SemanticRetriever

r = SemanticRetriever()
with open('test_messages.jsonl', 'r', encoding='utf-8') as f:
    items = [json.loads(line) for line in f if line.strip()]

print('--- INTENT MISMATCHES ---')
for item in items:
    norm = normalize_tanglish(item['input'])
    intent, i_c, emotion, e_c = r.predict_intent_emotion(norm)
    if not is_intent_match(intent, item['expected_intent']):
        print(f"#{item['id']:02d} In: '{item['input']:30}' | Pred: {intent:20} | Exp: {item['expected_intent']}")

print('\n--- EMOTION MISMATCHES ---')
for item in items:
    norm = normalize_tanglish(item['input'])
    intent, i_c, emotion, e_c = r.predict_intent_emotion(norm)
    if not is_emotion_match(emotion, item['expected_emotion']):
        print(f"#{item['id']:02d} In: '{item['input']:30}' | Pred: {emotion:15} | Exp: {item['expected_emotion']}")
