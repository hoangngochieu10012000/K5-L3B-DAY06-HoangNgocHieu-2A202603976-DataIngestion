from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from starter.src.ingestion import load_pdf

pages = load_pdf(Path("data/AIO2025_Tutorial_RAG.pdf"), "aio2025-tutorial-rag", "data/AIO2025_Tutorial_RAG.pdf")
page_map = {p.page: p.text for p in pages}

check_pages = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 24, 26, 31]
for cp in check_pages:
    txt = page_map.get(cp, "")
    print(f"==================== PAGE {cp} (len={len(txt)}) ====================")
    lines = txt.split("\n")
    for l in lines[:10]:
        print("  ", l)
    print("...")
    for l in lines[-6:]:
        print("  ", l)
