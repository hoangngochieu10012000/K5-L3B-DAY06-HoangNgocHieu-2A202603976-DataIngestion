import re
import unicodedata
from pathlib import Path
import pypdf

def normalize_text(text: str) -> str:
    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)
    
    # 2. Replace non-breaking spaces and tabs
    text = text.replace("\u00a0", " ").replace("\t", " ")
    
    # 3. Clean line by line
    lines = text.split("\n")
    cleaned_lines = []
    
    HEADER_PATTERNS = [
        re.compile(r"^AI VIET NAM\s*[–-]?\s*AI COURSE\s*2025", re.IGNORECASE),
        re.compile(r"^AI VIET NAM\s*\(AIO2025\)\s*aivietnam\.edu\.vn", re.IGNORECASE),
    ]
    
    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            cleaned_lines.append("")
            continue
            
        # Check header patterns
        is_header = any(pat.search(stripped) for pat in HEADER_PATTERNS)
        if is_header:
            continue
            
        # Check if line is just page number (digits only, 1-3 digits)
        if re.match(r"^\d{1,3}$", stripped):
            continue
            
        cleaned_lines.append(stripped)
        
    # Rejoin lines
    result = "\n".join(cleaned_lines)
    
    # Collapse multiple blank lines to at most two newlines
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result

reader = pypdf.PdfReader("data/AIO2025_Tutorial_RAG.pdf")
print("Testing normalization on page 1, 3, 4, 9, 21:")
for p in [1, 3, 4, 9, 21]:
    raw = reader.pages[p - 1].extract_text()
    norm = normalize_text(raw)
    print(f"--- Page {p} ---")
    print("Raw length:", len(raw), "Normalized length:", len(norm))
    print("First 200 chars:\n", norm[:200])
    print()
