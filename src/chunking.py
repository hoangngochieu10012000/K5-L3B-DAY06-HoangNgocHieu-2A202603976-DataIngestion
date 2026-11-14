from .models import Chunk, DocumentPage
import re


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split page text into fixed-size character windows with overlap."""
    text = page.text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    step = max(1, size - overlap)
    idx = 0
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk = Chunk(
                chunk_id=f"{page.document_id}_p{page.page}_a{idx:02d}",
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=chunk_text,
                metadata={
                    "section": page.metadata.get("section", "general"),
                    "strategy": "A",
                    "chunk_index": idx,
                    "char_length": len(chunk_text)
                }
            )
            chunks.append(chunk)
            idx += 1

        if end >= len(text):
            break
        start += step

    return chunks


def _split_oversized_paragraph(para: str, max_size: int) -> list[str]:
    """Split a single paragraph that exceeds max_size by sentence or newline boundaries."""
    # Split by sentence boundaries: dot followed by space/newline or newline
    sentence_delims = re.split(r"(?<=[.!?\n])\s+", para)
    sub_chunks = []
    current = ""

    for s in sentence_delims:
        s = s.strip()
        if not s:
            continue
        if len(current) + len(s) + 1 <= max_size:
            current = (current + " " + s).strip()
        else:
            if current:
                sub_chunks.append(current)
            if len(s) > max_size:
                # Break long sentence by character window
                for i in range(0, len(s), max_size):
                    sub_chunks.append(s[i:i + max_size].strip())
                current = ""
            else:
                current = s

    if current:
        sub_chunks.append(current)

    return sub_chunks


def by_paragraph(page: DocumentPage, max_size: int = 700) -> list[Chunk]:
    """Group paragraphs together without exceeding max_size, respecting document structure."""
    text = page.text.strip()
    if not text:
        return []

    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not raw_paragraphs:
        return []

    expanded_paragraphs = []
    for p in raw_paragraphs:
        if len(p) > max_size:
            expanded_paragraphs.extend(_split_oversized_paragraph(p, max_size))
        else:
            expanded_paragraphs.append(p)

    grouped_chunks: list[str] = []
    current_group = ""

    for p in expanded_paragraphs:
        if not current_group:
            current_group = p
        elif len(current_group) + len(p) + 2 <= max_size:
            current_group = current_group + "\n\n" + p
        else:
            grouped_chunks.append(current_group)
            current_group = p

    if current_group:
        grouped_chunks.append(current_group)

    chunks: list[Chunk] = []
    for idx, c_text in enumerate(grouped_chunks):
        c_text = c_text.strip()
        if not c_text:
            continue
        chunk = Chunk(
            chunk_id=f"{page.document_id}_p{page.page}_b{idx:02d}",
            document_id=page.document_id,
            source=page.source,
            page=page.page,
            text=c_text,
            metadata={
                "section": page.metadata.get("section", "general"),
                "strategy": "B",
                "chunk_index": idx,
                "char_length": len(c_text)
            }
        )
        chunks.append(chunk)

    return chunks
