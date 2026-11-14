import pypdf
import json

reader = pypdf.PdfReader("data/AIO2025_Tutorial_RAG.pdf")
print(f"Total physical pages: {len(reader.pages)}")

results = []
for idx, page in enumerate(reader.pages):
    txt = page.extract_text() or ""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    results.append({
        "page": idx + 1,
        "chars": len(txt),
        "lines": len(lines),
        "sample": lines[:3] if lines else []
    })

for r in results:
    print(f"Page {r['page']:02d}: {r['chars']:4d} chars, {r['lines']:2d} lines | {r['sample']}")
