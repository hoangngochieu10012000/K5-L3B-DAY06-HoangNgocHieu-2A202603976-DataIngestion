import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from starter.src.ingestion import load_pdf
from starter.src.chunking import fixed_size, by_paragraph

pages = load_pdf(Path("data/AIO2025_Tutorial_RAG.pdf"), "aio2025-tutorial-rag", "data/AIO2025_Tutorial_RAG.pdf")
print(f"Total pages loaded: {len(pages)}")

chunks_a = []
for p in pages:
    chunks_a.extend(fixed_size(p, size=500, overlap=50))

chunks_b = []
for p in pages:
    chunks_b.extend(by_paragraph(p, max_size=700))

print(f"Strategy A (Fixed size 500, overlap 50): {len(chunks_a)} chunks")
lengths_a = [len(c.text) for c in chunks_a]
print(f"  Min len: {min(lengths_a)}, Max len: {max(lengths_a)}, Avg len: {sum(lengths_a)/len(lengths_a):.1f}")

print(f"Strategy B (Paragraph-based, max 700): {len(chunks_b)} chunks")
lengths_b = [len(c.text) for c in chunks_b]
print(f"  Min len: {min(lengths_b)}, Max len: {max(lengths_b)}, Avg len: {sum(lengths_b)/len(lengths_b):.1f}")

print("\nSample Chunk A[0]:\n", repr(chunks_a[0].text[:120]))
print("\nSample Chunk B[0]:\n", repr(chunks_b[0].text[:120]))
