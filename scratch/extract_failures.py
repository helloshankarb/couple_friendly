import sys
sys.path.insert(0, '.')
import json
from ml.normalizer import normalize_tanglish
from ml.semantic_retriever import SemanticRetriever
from ml.taxonomy import get_hierarchical_domain
from cli_test import map_canonical_to_hierarchy, is_intent_match, is_emotion_match

retriever = SemanticRetriever()

with open('test_messages.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line) for line in f if line.strip()]

domain_failures = []
recall1_failures = []

for idx, item in enumerate(records, 1):
    raw = item["input"]
    exp_intent = item["expected_intent"]
    exp_emotion = item["expected_emotion"]
    category = item.get("category", "")
    
    norm = normalize_tanglish(raw)
    intent, i_conf, emotion, e_conf = retriever.predict_intent_emotion(norm)
    pred_dom, pred_int, pred_sub = map_canonical_to_hierarchy(intent, norm)
    
    # Expected domain lookup
    exp_dom = get_hierarchical_domain(exp_intent)
    
    # Check domain
    is_domain = (pred_dom.upper() == exp_dom.upper()) or (pred_dom.upper() in exp_intent.upper()) or (exp_dom in pred_dom.upper())
    if not is_domain:
        domain_failures.append({
            "id": idx,
            "input": raw,
            "expected_domain": exp_dom,
            "predicted_domain": pred_dom,
            "expected_intent": exp_intent,
            "predicted_intent": pred_int,
            "canonical_intent": intent,
            "emotion": emotion
        })
        
    # Check Recall@1
    _, _, _, _, top_sc = retriever.retrieve(norm, top_k=5)
    top1_intent = top_sc[0]["intent"] if top_sc else ""
    r1_match = is_intent_match(top1_intent, exp_intent) or (top1_intent == intent)
    
    # Also check if top1 scenario itself is the most relevant scenario
    # A Recall@1 failure is when top1 intent doesn't match expected OR top scenario is noticeably less aligned than rank 2
    if not is_intent_match(top_sc[0]["intent"], exp_intent):
        recall1_failures.append({
            "id": idx,
            "input": raw,
            "expected_intent": exp_intent,
            "top_candidates": top_sc[:5]
        })

print(f"Total Domain Failures: {len(domain_failures)}")
for df in domain_failures:
    print(f"#{df['id']:02d} | '{df['input']:30}' | ExpDom: {df['expected_domain']:18} | PredDom: {df['predicted_domain']:18} | ExpInt: {df['expected_intent']:20} | PredInt: {df['predicted_intent']}")

print(f"\nTotal Recall@1 Failures (Intent Mismatch): {len(recall1_failures)}")
for rf in recall1_failures:
    print(f"#{rf['id']:02d} | '{rf['input']:30}' | ExpInt: {rf['expected_intent']:20}")
    for rank, sc in enumerate(rf["top_candidates"][:3], 1):
        print(f"    Rank {rank}: '{sc['scenario']}' [{sc['intent']}] Score: {sc['score']}")
