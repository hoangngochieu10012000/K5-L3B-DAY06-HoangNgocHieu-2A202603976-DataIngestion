import json
import pypdf

reader = pypdf.PdfReader("data/AIO2025_Tutorial_RAG.pdf")
total_physical_pages = len(reader.pages)

# Pages excluded:
# - Page 2: Mục lục (Table of Contents)
# - Page 20: Code snippet overflow fragment (< 100 chars, no standalone conceptual content)
# - Page 35: Phụ lục (Appendix / external link)
excluded_pages = {2, 20, 35}

content_pages = []
total_characters = 0

for i, page in enumerate(reader.pages):
    page_num = i + 1
    raw_text = page.extract_text() or ""
    char_len = len(raw_text)
    
    is_content = page_num not in excluded_pages
    page_info = {
        "page_number": page_num,
        "is_content_page": is_content,
        "character_count": char_len,
        "exclusion_reason": "Table of Contents" if page_num == 2 else ("Code fragment (<100 chars)" if page_num == 20 else ("Appendix / Reference links" if page_num == 35 else None))
    }
    if is_content:
        content_pages.append(page_info)
        total_characters += char_len

manifest = {
    "source_id": "aio2025-tutorial-rag",
    "title": "AI VIET NAM (AIO2025) - Tutorial: RAG (Retrieval-Augmented Generation)",
    "source_path_or_url": "data/AIO2025_Tutorial_RAG.pdf",
    "license_or_permission": "Tài liệu đào tạo của AI VIET NAM (AIO2025), sử dụng cho mục đích học tập và nghiên cứu cá nhân.",
    "accessed_at": "2026-11-14",
    "version": "AIO2025-v1.0",
    "total_physical_pages": total_physical_pages,
    "total_content_pages": len(content_pages),
    "total_characters_raw": total_characters,
    "page_counting_rules": "Loại bỏ trang bìa/mục lục (trang 2), trang cụt chứa fragment mã nguồn ngắn dưới 100 ký tự (trang 20), và trang phụ lục/tài liệu tham khảo (trang 35). Các trang nội dung còn lại (32 trang) đều có dung lượng từ 772 đến 2191 ký tự có cấu trúc hoàn chỉnh.",
    "content_pages": content_pages
}

with open("data/manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Manifest created: {len(content_pages)} content pages, {total_characters} characters.")
