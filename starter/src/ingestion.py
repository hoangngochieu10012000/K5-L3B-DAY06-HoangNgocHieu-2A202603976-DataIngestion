"""Read and normalize source data."""
import logging
import re
import unicodedata
from pathlib import Path
import pypdf
from .models import DocumentPage

logger = logging.getLogger(__name__)

# Deterministic section mapping for the AIO 2025 RAG Tutorial corpus
PAGE_SECTION_MAP = {
    1: "dan_nhap",
    3: "thuat_ngu",
    4: "ly_thuyet_co_ban",
    5: "ly_thuyet_co_ban",
    6: "ly_thuyet_co_ban",
    7: "ly_thuyet_co_ban",
    8: "ly_thuyet_co_ban",
    9: "retrieval_generation",
    10: "retrieval_generation",
    11: "retrieval_generation",
    12: "retrieval_generation",
    13: "retrieval_generation",
    14: "retrieval_generation",
    15: "phan_tich_vai_tro",
    16: "phan_tich_vai_tro",
    17: "gioi_thieu_langchain",
    18: "gioi_thieu_langchain",
    19: "gioi_thieu_langchain",
    21: "thuc_hanh_pipeline",
    22: "thuc_hanh_pipeline",
    23: "thuc_hanh_pipeline",
    24: "thuc_hanh_pipeline",
    25: "thuc_hanh_pipeline",
    26: "thuc_hanh_pipeline",
    27: "thuc_hanh_pipeline",
    28: "thuc_hanh_pipeline",
    29: "thuc_hanh_pipeline",
    30: "thuc_hanh_pipeline",
    31: "cau_hoi_trac_nghiem",
    32: "cau_hoi_trac_nghiem",
    33: "cau_hoi_trac_nghiem",
    34: "cau_hoi_trac_nghiem",
}

EXCLUDED_PAGES = {2, 20, 35}


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC), strip repeated boilerplate headers, footers and whitespace."""
    if not text:
        return ""

    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Replace non-breaking spaces and tabs with standard space
    text = text.replace("\u00a0", " ").replace("\t", " ")

    lines = text.split("\n")
    cleaned_lines = []

    header_patterns = [
        re.compile(r"^AI VIET NAM\s*[–-]?\s*AI COURSE\s*2025", re.IGNORECASE),
        re.compile(r"^AI VIET NAM\s*\(AIO2025\)\s*aivietnam\.edu\.vn", re.IGNORECASE),
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue

        # Skip running header lines
        if any(pat.search(stripped) for pat in header_patterns):
            continue

        # Skip isolated page numbers at footer
        if re.match(r"^\d{1,3}$", stripped):
            continue

        cleaned_lines.append(stripped)

    result = "\n".join(cleaned_lines)
    # Collapse multiple blank lines to at most two
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; keep page number, source, section metadata and clean text.

    Detects and records excluded or empty pages.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {path}")

    reader = pypdf.PdfReader(str(path))
    pages: list[DocumentPage] = []
    
    total_physical = len(reader.pages)
    logger.info(f"Loading PDF '{path}' ({total_physical} physical pages)...")

    empty_pages = []
    for idx, page in enumerate(reader.pages):
        page_num = idx + 1

        # Check exclusion rules
        if page_num in EXCLUDED_PAGES:
            logger.info(f"Skipping excluded page {page_num} (TOC/stub/appendix)")
            continue

        try:
            raw_text = page.extract_text() or ""
        except Exception as e:
            logger.warning(f"Error extracting text from page {page_num}: {e}")
            raw_text = ""

        if not raw_text.strip():
            empty_pages.append(page_num)
            logger.warning(f"Page {page_num} has no text")
            continue

        norm_text = normalize_text(raw_text)
        if not norm_text:
            empty_pages.append(page_num)
            logger.warning(f"Page {page_num} text became empty after normalization")
            continue

        section = PAGE_SECTION_MAP.get(page_num, "general")
        doc_page = DocumentPage(
            document_id=document_id,
            source=source,
            page=page_num,
            text=norm_text,
            metadata={
                "section": section,
                "raw_char_len": len(raw_text),
                "norm_char_len": len(norm_text),
            }
        )
        pages.append(doc_page)

    logger.info(f"Successfully loaded {len(pages)} valid content pages (excluded: {len(EXCLUDED_PAGES)}, empty: {len(empty_pages)}).")
    return pages
