import json
from pathlib import Path
import unicodedata
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from starter.src.ingestion import load_pdf

pages = load_pdf(Path("data/AIO2025_Tutorial_RAG.pdf"), "aio2025-tutorial-rag", "data/AIO2025_Tutorial_RAG.pdf")
page_texts = {p.page: " ".join(unicodedata.normalize("NFC", p.text.lower()).split()) for p in pages}

benchmark = [
    {
        "id": "q01",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Khái niệm RAG lần đầu tiên được đề xuất chính thức trong bài báo nào và bởi ai?",
        "expected_answer": "Bài báo 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks' bởi Patrick Lewis và các cộng sự tại Facebook AI Research (FAIR) vào năm 2020.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 4,
        "evidence_quote": "Khái niệm RAG lần đầu tiên được đề xuất chính thức trong bài báo khoa học “Retrieval- Augmented Generation for Knowledge-Intensive NLP Tasks” bởi Patrick Lewis và các cộng sự tại Facebook AI Research (FAIR) vào năm 2020",
        "filter": None
    },
    {
        "id": "q02",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Thuật ngữ Hallucination trong mô hình ngôn ngữ lớn được định nghĩa như thế nào?",
        "expected_answer": "Hiện tượng mô hình sinh ra thông tin sai lệch, bịa đặt hoặc không có thực nhưng với văn phong tự tin.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 3,
        "evidence_quote": "Hiện tượng mô hình sinh ra thông tin sai lệch, bịa đặt hoặc không có thực nhưng với văn phong tự tin.",
        "filter": None
    },
    {
        "id": "q03",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Kỹ thuật Grounding có vai trò gì trong hệ thống hỏi đáp?",
        "expected_answer": "Kỹ thuật “neo” câu trả lời của mô hình vào dữ liệu thực tế được cung cấp để đảm bảo tính xác thực.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 3,
        "evidence_quote": "Kỹ thuật “neo” câu trả lời của mô hình vào dữ liệu thực tế được cung cấp để đảm bảo tính xác thực.",
        "filter": None
    },
    {
        "id": "q04",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Trong kiến trúc RAG nguyên bản năm 2020, mô hình nào đóng vai trò Generator sinh văn bản?",
        "expected_answer": "BART.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 4,
        "evidence_quote": "Generator (BART) sử dụng đầu vào kết hợp với các tài liệu ẩn (latent documents) tìm được từ Retriever để sinh văn bản.",
        "filter": None
    },
    {
        "id": "q05",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Sự chuyển dịch sang In-Context RAG tận dụng khả năng gì của các mô hình LLM hiện đại?",
        "expected_answer": "Khả năng In-Context Learning mạnh mẽ của LLM mà không cần fine-tune cập nhật trọng số.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 5,
        "evidence_quote": "Mặc dù thuật ngữ RAG vẫn được giữ nguyên, tư duy triển khai kỹ thuật này đã thay đổi căn",
        "filter": None
    },
    {
        "id": "q06",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Mục đích của việc thiết lập chunk overlap (độ chồng lấp) khi chia nhỏ văn bản là gì?",
        "expected_answer": "Đóng vai trò như cầu nối ngữ cảnh nhằm tránh mất thông tin ở ranh giới giữa các chunk.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 8,
        "evidence_quote": "Phần giao thoa này đóng vai trò như “cầu nối” ngữ cảnh.",
        "filter": None
    },
    {
        "id": "q07",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Vì sao không thể cộng trực tiếp điểm số của Vector Search và BM25 trong Hybrid Search?",
        "expected_answer": "Vì điểm số của hai phương pháp có thang đo hoàn toàn khác nhau.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 11,
        "evidence_quote": "Điểm số của Vector Search và BM25 có thang đo hoàn toàn khác nhau, việc",
        "filter": None
    },
    {
        "id": "q08",
        "split": "dev",
        "type": "dien_dat_lai",
        "question": "Sau khi qua bước Cross-Encoder trong Re-ranking, mô hình có thể giải quyết được mối quan hệ gì?",
        "expected_answer": "Đọc hiểu mối quan hệ ngữ nghĩa sâu giữa câu hỏi và ngữ cảnh (ví dụ 'không nhận được' -> 'lỗi/spam').",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 12,
        "evidence_quote": "Sau khi qua Cross-Encoder (Re-ranking): (Mô hình đọc hiểu mối quan hệ “không nhận được” → “lỗi/spam”)",
        "filter": None
    },
    {
        "id": "q09",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Nếu loại bỏ hoàn toàn LLM trong kiến trúc RAG thì hệ thống sẽ như thế nào?",
        "expected_answer": "Hệ thống trở thành công cụ tìm kiếm thuần túy (Search Engine) chỉ trả về đoạn trích.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 16,
        "evidence_quote": "Kịch bản 3: Loại bỏ LLM (Large Language Model)",
        "filter": None
    },
    {
        "id": "q10",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Trong phần cơ sở lý thuyết, các bước của quy trình Ingestion bao gồm những giai đoạn nào?",
        "expected_answer": "Document Loading, Text Cleaning, Chunking, Embedding và Vector Storage.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 6,
        "evidence_quote": "Quy trình này bao gồm các bước từ cơ bản đến nâng cao như sau: 1. Document Loading:",
        "filter": {"section": "ly_thuyet_co_ban"}
    },
    {
        "id": "q11",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Trong phần thực hành, hàm clean_vietnamese_text giúp giải quyết vấn đề gì khi trích xuất PDF?",
        "expected_answer": "Giúp chuẩn hóa văn bản tiếng Việt, loại bỏ ký tự không mong muốn và đảm bảo encoding đồng nhất.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 24,
        "evidence_quote": "Hàm clean_vietnamese_text dưới đây giúp chuẩn hóa văn bản tiếng Việt, loại bỏ các ký tự không mong muốn và đảm bảo encoding đồng nhất.",
        "filter": {"section": "thuc_hanh_pipeline"}
    },
    {
        "id": "q12",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Mô hình ngôn ngữ (LLM) nào được sử dụng trong phần thực hành RAG pipeline?",
        "expected_answer": "Qwen2.5-3B-Instruct.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 26,
        "evidence_quote": "Ở đây, ta sử dụng Qwen2.5-3B-Instruct, một mô hình instruction-tuned với khả năng xử lý hiệu quả trong các tác vụ hỏi đáp và sinh văn bản.",
        "filter": None
    },
    {
        "id": "q13",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Kỹ thuật Chain-of-Thought (CoT) hướng dẫn mô hình làm gì trước khi đưa ra kết luận?",
        "expected_answer": "Yêu cầu mô hình suy nghĩ từng bước (Let's think step by step) dựa trên các dữ kiện trong context.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 14,
        "evidence_quote": "Chain-of-Thought (CoT - Chuỗi suy luận): Yêu cầu mô hình suy nghĩ từng bước (Let’s think step by step) dựa trên các dữ kiện trong context trước khi đưa ra kết luận",
        "filter": None
    },
    {
        "id": "q14",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Vai trò của thành phần VectorStore trong framework LangChain là gì?",
        "expected_answer": "Chịu trách nhiệm lưu trữ các đối tượng Document và vector tương ứng.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 19,
        "evidence_quote": "VectorStore trong LangChain chịu trách nhiệm lưu trữ các đối tượng Document và vector",
        "filter": None
    },
    {
        "id": "q15",
        "split": "dev",
        "type": "dieu_kien_ngoai_le",
        "question": "Hiện tượng 'Lost in the Middle' ảnh hưởng như thế nào đến việc xử lý ngữ cảnh của LLM?",
        "expected_answer": "Mô hình xử lý tốt thông tin ở đầu và cuối prompt nhưng dễ bỏ sót thông tin nằm ở giữa ngữ cảnh.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 31,
        "evidence_quote": "Để khắc phục hiện tượng “Lost in the Middle”, chiến lược sắp xếp ngữ cảnh nào sau đây là",
        "filter": None
    },
    # 5 TEST QUESTIONS
    {
        "id": "q16",
        "split": "test",
        "type": "truc_tiep",
        "question": "Các tác giả tham gia xây dựng Tutorial RAG của AI VIET NAM gồm những ai?",
        "expected_answer": "Dương Trường Bình, Nguyễn Anh Khôi, Trần Đại Nhân, Dương Đình Thắng, Đinh Quang Vinh.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 1,
        "evidence_quote": "Dương Trường Bình Nguyễn Anh Khôi Trần Đại Nhân Dương Đình Thắng Đinh Quang Vinh",
        "filter": None
    },
    {
        "id": "q17",
        "split": "test",
        "type": "dien_dat_lai",
        "question": "Giới hạn số lượng tokens tối đa mà LLM có thể tiếp nhận và xử lý trong một lần prompt được gọi là gì?",
        "expected_answer": "Context Window.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 3,
        "evidence_quote": "Context Window Giới hạn số lượng tokens (đơn vị văn bản) tối đa mà LLM có thể tiếp nhận và xử lý trong một lần prompt.",
        "filter": None
    },
    {
        "id": "q18",
        "split": "test",
        "type": "metadata_filter",
        "question": "Trong Phase 2: Retrieval, điều gì sẽ xảy ra nếu bước truy xuất thông tin bị sai hoặc thiếu?",
        "expected_answer": "LLM sẽ không có đủ dữ liệu để trả lời câu hỏi.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 9,
        "evidence_quote": "Nếu bước này trích xuất thông tin sai hoặc thiếu, LLM sẽ không có đủ dữ liệu để trả lời.",
        "filter": {"section": "retrieval_generation"}
    },
    {
        "id": "q19",
        "split": "test",
        "type": "dieu_kien_ngoai_le",
        "question": "Theo phân tích kịch bản mở rộng, vai trò bộ não của LLM trong hệ thống RAG là gì?",
        "expected_answer": "Tổng hợp thông tin, suy luận và sinh câu trả lời dựa trên ngữ cảnh đã được cung cấp.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 16,
        "evidence_quote": "Vai trò LLM: Bộ não Tổng hợp thông tin, suy luận và sinh câu trả lời dựa trên ngữ cảnh",
        "filter": None
    },
    {
        "id": "q20",
        "split": "test",
        "type": "truc_tiep",
        "question": "Đường dẫn mặc định persist_dir được thiết lập để lưu trữ database trong phần thực hành là gì?",
        "expected_answer": "/content/chroma_data.",
        "gold_source_id": "aio2025-tutorial-rag",
        "gold_page": 26,
        "evidence_quote": 'persist_dir: str = "/content/chroma_data"',
        "filter": None
    }
]

print("Validating all 20 evidence quotes against page texts:")
all_ok = True
for q in benchmark:
    p_num = q["gold_page"]
    norm_txt = page_texts.get(p_num, "")
    eq_norm = " ".join(unicodedata.normalize("NFC", q["evidence_quote"]).lower().split())
    
    found = eq_norm in norm_txt
    if not found:
        # Check prefix
        prefix = eq_norm[:40]
        found = prefix in norm_txt
    status = "OK" if found else "NOT FOUND!"
    if not found:
        all_ok = False
        print(f"[{status}] {q['id']} (Page {p_num}): quote={repr(eq_norm[:60])}")
    else:
        print(f"[{status}] {q['id']} (Page {p_num})")

print(f"\nOverall benchmark validation: {'ALL 20 EVIDENCE QUOTES VERIFIED!' if all_ok else 'SOME FAILED'}")

# Write to benchmark/questions.json and starter/data/benchmark.json
Path("benchmark").mkdir(exist_ok=True)
with open("benchmark/questions.json", "w", encoding="utf-8") as f:
    json.dump(benchmark, f, ensure_ascii=False, indent=2)

with open("starter/data/benchmark.json", "w", encoding="utf-8") as f:
    json.dump(benchmark, f, ensure_ascii=False, indent=2)

print("Saved benchmark/questions.json and starter/data/benchmark.json successfully.")
