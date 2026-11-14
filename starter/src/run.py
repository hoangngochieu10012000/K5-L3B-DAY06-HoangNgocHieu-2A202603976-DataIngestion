"""Orchestrator for Data Ingestion Pipeline & Benchmark (Day 06)."""
import csv
import json
import logging
import os
from pathlib import Path
import time

# Avoid OpenMP duplicate runtime issue on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from .chunking import by_paragraph, fixed_size
from .embeddings import EmbeddingGemmaEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_pdf
from .store import QdrantVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    start_total_time = time.time()

    # 1. Paths & Setup
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_dir = repo_root / "data"
    results_dir = repo_root / "starter" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = data_dir / "AIO2025_Tutorial_RAG.pdf"
    benchmark_path = repo_root / "benchmark" / "questions.json"
    if not benchmark_path.exists():
        benchmark_path = repo_root / "starter" / "data" / "benchmark.json"

    logger.info("=== STEP 1: LOAD & NORMALIZE CORPUS ===")
    t0 = time.time()
    pages = load_pdf(pdf_path, document_id="aio2025-tutorial-rag", source=str(pdf_path))
    ingest_time = time.time() - t0
    logger.info(f"Loaded {len(pages)} valid content pages in {ingest_time:.2f}s.")
    if len(pages) < 30:
        raise ValueError(f"Corpus only has {len(pages)} pages; minimum required is 30.")

    # 2. Chunking
    logger.info("=== STEP 2: CHUNKING FOR STRATEGIES A, B, C ===")
    chunks_a = []
    for p in pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))

    chunks_b = []
    for p in pages:
        chunks_b.extend(by_paragraph(p, max_size=700))

    # Strategy C uses the exact same chunks as Strategy B
    chunks_c = chunks_b

    logger.info(f"Strategy A (Fixed 500, overlap 50): {len(chunks_a)} chunks")
    logger.info(f"Strategy B/C (Paragraph-based, max 700): {len(chunks_b)} chunks")

    # 3. Embedding Model Initialization
    logger.info("=== STEP 3: INITIALIZE REAL EMBEDDING MODEL ===")
    embedder = EmbeddingGemmaEmbedder(model_name="google/embeddinggemma-2")

    # 4. Generate Embeddings & Upsert to Vector Store
    logger.info("=== STEP 4: EMBED & STORE VECTORS ===")
    db_path = results_dir / "qdrant_db"
    store = QdrantVectorStore(db_path=str(db_path), dimensions=embedder.dimensions)

    # Strategy A
    logger.info("Embedding & indexing Strategy A...")
    t_start_a = time.time()
    texts_a = [c.text for c in chunks_a]
    vecs_a = embedder.embed_documents(texts_a)
    store.reset_collection("A")
    store.upsert("A", chunks_a, vecs_a)
    # Check idempotence / re-ingestion
    initial_count_a = store.count("A")
    store.upsert("A", chunks_a[:5], vecs_a[:5])
    assert store.count("A") == initial_count_a, "Idempotence failed on Strategy A"
    time_a = time.time() - t_start_a
    logger.info(f"Strategy A indexed: {initial_count_a} vectors in {time_a:.2f}s.")

    # Strategy B (also used by C)
    logger.info("Embedding & indexing Strategy B...")
    t_start_b = time.time()
    texts_b = [c.text for c in chunks_b]
    vecs_b = embedder.embed_documents(texts_b)
    store.reset_collection("B")
    store.upsert("B", chunks_b, vecs_b)
    initial_count_b = store.count("B")
    store.upsert("B", chunks_b[:5], vecs_b[:5])
    assert store.count("B") == initial_count_b, "Idempotence failed on Strategy B"
    time_b = time.time() - t_start_b
    logger.info(f"Strategy B indexed: {initial_count_b} vectors in {time_b:.2f}s.")

    # 5. Load Benchmark Questions
    logger.info("=== STEP 5: LOAD BENCHMARK QUESTIONS ===")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    logger.info(f"Loaded {len(questions)} questions (Dev: {sum(1 for q in questions if q['split'] == 'dev')}, Test: {sum(1 for q in questions if q['split'] == 'test')}).")

    # 6. Run Benchmark for Strategies A, B, C
    logger.info("=== STEP 6: EXECUTE BENCHMARK RETRIEVAL ===")
    strategies = [
        {"name": "A", "target_collection": "A", "use_filter": False, "chunk_count": len(chunks_a), "time": time_a},
        {"name": "B", "target_collection": "B", "use_filter": False, "chunk_count": len(chunks_b), "time": time_b},
        {"name": "C", "target_collection": "B", "use_filter": True, "chunk_count": len(chunks_b), "time": time_b},
    ]

    benchmark_results = {}
    for strat in strategies:
        s_name = strat["name"]
        coll = strat["target_collection"]
        use_filter = strat["use_filter"]
        logger.info(f"Running retrieval benchmark for Strategy {s_name} (Filter: {use_filter})...")

        traces = []
        for q in questions:
            q_vec = embedder.embed_query(q["question"])
            filter_kwargs = q.get("filter") if use_filter else None
            hits = store.search(coll, q_vec, top_k=3, filters=filter_kwargs)
            trace = evaluate_query(q, hits)
            traces.append(trace)

        summary = summarize(traces)
        benchmark_results[s_name] = {
            "strategy": s_name,
            "description": "Fixed size 500/50" if s_name == "A" else ("Paragraph-based max 700" if s_name == "B" else "Paragraph-based + section filter"),
            "chunk_count": strat["chunk_count"],
            "indexing_time_sec": round(strat["time"], 2),
            "cost_usd": 0.0,
            "summary": summary,
            "traces": traces
        }

        trace_file = results_dir / f"traces_strategy_{s_name.lower()}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(traces, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved traces for Strategy {s_name} to {trace_file}")

    # 7. Save Overall Summary
    summary_file = results_dir / "benchmark_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved complete benchmark summary to {summary_file}")

    # 8. Update artifacts/experiment_log.csv
    exp_log_path = repo_root / "artifacts" / "experiment_log.csv"
    with open(exp_log_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "strategy", "chunking", "chunk_size", "overlap", "metadata", "filter",
            "vectorizer", "hypothesis", "dev_hit1", "dev_hit3", "test_hit1", "test_hit3", "notes"
        ])
        
        # Strategy A
        sum_a = benchmark_results["A"]["summary"]
        writer.writerow([
            "A", "fixed_size", "500", "50", "source,page,section", "none",
            "google/embeddinggemma-2", "Fixed window chunking baseline",
            sum_a["dev"]["hit1_rate"], sum_a["dev"]["hit3_rate"],
            sum_a["test"]["hit1_rate"], sum_a["test"]["hit3_rate"],
            f"{len(chunks_a)} chunks, indexing {time_a:.1f}s"
        ])
        
        # Strategy B
        sum_b = benchmark_results["B"]["summary"]
        writer.writerow([
            "B", "by_paragraph", "700", "0", "source,page,section", "none",
            "google/embeddinggemma-2", "Paragraph-based preserves semantic boundary",
            sum_b["dev"]["hit1_rate"], sum_b["dev"]["hit3_rate"],
            sum_b["test"]["hit1_rate"], sum_b["test"]["hit3_rate"],
            f"{len(chunks_b)} chunks, indexing {time_b:.1f}s"
        ])

        # Strategy C
        sum_c = benchmark_results["C"]["summary"]
        writer.writerow([
            "C", "by_paragraph", "700", "0", "source,page,section", "section_filter",
            "google/embeddinggemma-2", "Metadata filtering narrows search scope for filtered questions",
            sum_c["dev"]["hit1_rate"], sum_c["dev"]["hit3_rate"],
            sum_c["test"]["hit1_rate"], sum_c["test"]["hit3_rate"],
            f"Filtered queries only, same chunks as B"
        ])

    logger.info(f"Updated {exp_log_path}")

    total_pipeline_time = time.time() - start_total_time
    logger.info(f"=== PIPELINE COMPLETED IN {total_pipeline_time:.2f}s ===")

    store.close()
    return benchmark_results


def main() -> None:
    results = run_pipeline()
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY RESULTS:")
    print("=" * 60)
    for s_name in ["A", "B", "C"]:
        res = results[s_name]
        sum_dev = res["summary"]["dev"]
        sum_test = res["summary"]["test"]
        print(f"Strategy {s_name} ({res['description']}):")
        print(f"  Dev  (15): Hit@1 = {sum_dev['hit1_rate']} ({sum_dev['hit1_pct']}%), Evidence Hit@3 = {sum_dev['hit3_rate']} ({sum_dev['hit3_pct']}%)")
        print(f"  Test  (5): Hit@1 = {sum_test['hit1_rate']} ({sum_test['hit1_pct']}%), Evidence Hit@3 = {sum_test['hit3_rate']} ({sum_test['hit3_pct']}%)")
        print(f"  Chunks: {res['chunk_count']} | Index Time: {res['indexing_time_sec']}s | Cost: ${res['cost_usd']}")
        print()


if __name__ == "__main__":
    main()
