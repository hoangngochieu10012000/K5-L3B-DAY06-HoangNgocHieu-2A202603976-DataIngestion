import json
from pathlib import Path

traces_a = json.load(open("starter/results/traces_strategy_a.json", encoding="utf-8"))
traces_b = json.load(open("starter/results/traces_strategy_b.json", encoding="utf-8"))
traces_c = json.load(open("starter/results/traces_strategy_c.json", encoding="utf-8"))

test_a = [t for t in traces_a if t["split"] == "test"]
test_b = [t for t in traces_b if t["split"] == "test"]
test_c = [t for t in traces_c if t["split"] == "test"]

print("=== TEST TRACES STRATEGY A ===")
for t in test_a:
    print(f"[{t['question_id']}] Hit@1: {t['hit_at_1']}, Hit@3: {t['hit_at_3']} | Q: {t['question'][:50]}")
    for h in t["hits"]:
        print(f"   Rank {h['rank']} (p.{h['page']}): is_hit={h['is_hit']}, score={h['score']:.4f}")

print("\n=== TEST TRACES STRATEGY B ===")
for t in test_b:
    print(f"[{t['question_id']}] Hit@1: {t['hit_at_1']}, Hit@3: {t['hit_at_3']} | Q: {t['question'][:50]}")
    for h in t["hits"]:
        print(f"   Rank {h['rank']} (p.{h['page']}): is_hit={h['is_hit']}, score={h['score']:.4f}")

print("\n=== TEST TRACES STRATEGY C ===")
for t in test_c:
    print(f"[{t['question_id']}] Hit@1: {t['hit_at_1']}, Hit@3: {t['hit_at_3']} | Q: {t['question'][:50]}")
    for h in t["hits"]:
        print(f"   Rank {h['rank']} (p.{h['page']}): is_hit={h['is_hit']}, score={h['score']:.4f}")
