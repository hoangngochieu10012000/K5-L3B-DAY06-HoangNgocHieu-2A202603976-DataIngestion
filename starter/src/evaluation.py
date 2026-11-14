"""Evaluate retrieved evidence and preserve per-query traces."""
import unicodedata
from typing import Any


def _normalize_for_match(text: str) -> str:
    """Normalize text for evidence comparison (lowercase, NFC, collapse whitespaces)."""
    text = unicodedata.normalize("NFC", text or "")
    text = " ".join(text.lower().split())
    return text


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and gold evidence match; keep Hit@1 and Hit@3 traces.

    A hit requires:
    1. Page matches gold_page (or one of multiple gold pages if provided).
    2. Chunk text contains the key gold evidence quote (normalized).
    """
    gold_pages = question.get("gold_page")
    if not isinstance(gold_pages, list):
        gold_pages = [gold_pages] if gold_pages is not None else []

    evidence_quotes = question.get("evidence_quote")
    if not isinstance(evidence_quotes, list):
        evidence_quotes = [evidence_quotes] if evidence_quotes is not None else []

    norm_evidence = [_normalize_for_match(eq) for eq in evidence_quotes if eq]

    hits_eval = []
    has_hit_at_3 = False
    has_hit_at_1 = False

    for rank, hit in enumerate(hits):
        hit_page = hit.get("page")
        hit_text_norm = _normalize_for_match(hit.get("text", ""))

        page_match = hit_page in gold_pages
        evidence_match = False
        matched_quote = None

        for eq in norm_evidence:
            # Check if evidence quote (or significant substring) is inside chunk text
            if eq in hit_text_norm:
                evidence_match = True
                matched_quote = eq
                break
            # Fallback for slight boundary trimming: check 80% prefix if length >= 30
            elif len(eq) >= 30 and eq[: int(len(eq) * 0.8)] in hit_text_norm:
                evidence_match = True
                matched_quote = eq[: int(len(eq) * 0.8)]
                break

        is_hit = page_match and evidence_match

        if rank == 0 and is_hit:
            has_hit_at_1 = True
        if is_hit:
            has_hit_at_3 = True

        hits_eval.append({
            "rank": rank + 1,
            "chunk_id": hit.get("chunk_id"),
            "page": hit_page,
            "section": hit.get("section"),
            "score": hit.get("score"),
            "page_match": page_match,
            "evidence_match": evidence_match,
            "is_hit": is_hit,
            "text_preview": hit.get("text", "")[:150] + "..." if len(hit.get("text", "")) > 150 else hit.get("text", "")
        })

    return {
        "question_id": question.get("id"),
        "split": question.get("split", "dev"),
        "question": question.get("question"),
        "gold_page": gold_pages,
        "filter": question.get("filter"),
        "hit_at_1": has_hit_at_1,
        "hit_at_3": has_hit_at_3,
        "hits": hits_eval
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by split (dev / test / total)."""
    splits = ["dev", "test", "total"]
    summary: dict[str, Any] = {}

    for s in splits:
        if s == "total":
            sub_traces = traces
        else:
            sub_traces = [t for t in traces if t.get("split") == s]

        total = len(sub_traces)
        if total == 0:
            summary[s] = {
                "total": 0,
                "hit1_count": 0,
                "hit3_count": 0,
                "hit1_rate": "0/0 (N/A)",
                "hit3_rate": "0/0 (N/A)",
                "hit1_pct": 0.0,
                "hit3_pct": 0.0
            }
            continue

        hit1_count = sum(1 for t in sub_traces if t.get("hit_at_1"))
        hit3_count = sum(1 for t in sub_traces if t.get("hit_at_3"))

        summary[s] = {
            "total": total,
            "hit1_count": hit1_count,
            "hit3_count": hit3_count,
            "hit1_rate": f"{hit1_count}/{total}",
            "hit3_rate": f"{hit3_count}/{total}",
            "hit1_pct": round(hit1_count / total * 100, 2),
            "hit3_pct": round(hit3_count / total * 100, 2)
        }

    return summary
