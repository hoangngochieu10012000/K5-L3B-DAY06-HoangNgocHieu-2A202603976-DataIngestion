# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

**Học viên:** Hoàng Ngọc Hiệu  
**MSSV:** 2A202603976  
**Lớp:** K5-L3B  

---

## Dữ liệu và pipeline
- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:**
  - *Chủ đề:* Tài liệu đào tạo kỹ thuật chuyên sâu về Retrieval-Augmented Generation (RAG) và LangChain Framework của AI VIET NAM (AIO2025).
  - *Nguồn & quyền:* File `data\AIO2025_Tutorial_RAG.pdf` (phiên bản AIO2025-v1.0), được cung cấp trong khuôn khổ chương trình học AI VIET NAM, sử dụng hợp lệ cho mục đích nghiên cứu và thực hành kỹ thuật cá nhân.
  - *Số trang:* Tổng cộng 35 trang vật lý.
  - *Quy tắc tính trang:* Loại bỏ trang 2 (Mục lục - Table of Contents), trang 20 (code stub cụt dưới 100 ký tự không mang nội dung độc lập), và trang 35 (Phụ lục chứa liên kết tải code tham khảo bên ngoài). Tổng số trang nội dung hữu ích được đưa vào pipeline là **32 trang** (đạt và vượt yêu cầu tối thiểu 30 trang), với dung lượng văn bản từ 772 đến 2.191 ký tự/trang, tổng cộng 52.520 ký tự thô.
  - *Manifest dữ liệu:* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\data\manifest.json](../../data/manifest.json).

- **Chuẩn hóa, lỗi và giới hạn:**
  - *Chuẩn hóa Unicode & ký tự:* Chuẩn hóa toàn bộ văn bản về dạng Unicode NFC (`unicodedata.normalize('NFC', text)`), thay thế các khoảng trắng không ngắt (`\u00a0`) và ký tự tab (`\t`) bằng khoảng trắng tiêu chuẩn.
  - *Làm sạch cấu trúc:* Loại bỏ các dòng running header lặp lại qua các trang (`AI VIET NAM (AIO2025) aivietnam.edu.vn`, `AI VIET NAM – AI COURSE 2025`), loại bỏ các số trang đơn lẻ ở chân trang footer (`\d{1,3}`), thu gọn các dòng trống liên tiếp về tối đa 2 dòng mới (`\n\n`) để bảo toàn cấu trúc phân đoạn và thụt đầu dòng của code block.
  - *Mã nguồn đọc và chuẩn hóa:* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\ingestion.py](../../starter/src/ingestion.py).
  - *Lỗi và giới hạn:* Một số sơ đồ kiến trúc phức tạp trong PDF được biểu diễn dưới dạng hình ảnh hoặc text phân mảnh; pipeline xử lý trích xuất văn bản thuần qua `pypdf`, không dùng OCR ngoài nên chỉ tập trung vào văn bản có thể trích xuất trực tiếp.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:**
  - *Embedding model:* `google/embeddinggemma-2` (phiên bản open-weights chính thức của Google DeepMind, phát hành 2026, hỗ trợ tiếng Việt và đa ngữ mạnh mẽ qua kiến trúc Gemma 2, 740M tham số).
  - *Số chiều:* 768 chiều.
  - *Instruction prefixes tuân thủ chuẩn của Google:*
    - Document chunks: `title: none | text: {content}`
    - Query benchmark: `task: question answering | query: {question}`
  - *Mã nguồn Embedding:* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\embeddings.py](../../starter/src/embeddings.py).
  - *Vector store:* Qdrant Embedded Local (`qdrant-client==1.20.0`), lưu trữ bền vững tại thư mục `starter\results\qdrant_db\`, không phụ thuộc Docker daemon.
  - *Mã nguồn Vector Store:* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\store.py](../../starter/src/store.py).
  - *Metric:* Cosine Similarity (`Distance.COSINE`).
  - *Lệnh chạy:*
    ```bash
    cd starter
    python -m src.run
    ```
  - *Mã nguồn điều phối (Pipeline Orchestrator):* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\run.py](../../starter/src/run.py).
  - *Chi phí:* **$0.00** (Chạy offline hoàn toàn trên GPU cục bộ NVIDIA GeForce RTX 4060 Laptop GPU qua PyTorch CUDA).

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:**
  - *Metadata bắt buộc:* `document_id` (`aio2025-tutorial-rag`), `source` (`data\AIO2025_Tutorial_RAG.pdf`), `page` (số trang vật lý từ 1 đến 34).
  - *Trường lọc bổ sung:* `section` (dạng string Enum phân loại chủ đề chương mục).
  - *Nguồn giá trị & lý do chọn:* Giá trị `section` được ánh xạ trực tiếp từ cấu trúc chương mục của tài liệu:
    - `dan_nhap`: Trang 1 (Dẫn nhập bài học)
    - `thuat_ngu`: Trang 3 (Bảng thuật ngữ cốt lõi RAG)
    - `ly_thuyet_co_ban`: Trang 4–8 (Nguồn gốc RAG, In-Context RAG, Phase 1 Ingestion & Chunking)
    - `retrieval_generation`: Trang 9–14 (Phase 2 Retrieval, Hybrid Search, RRF, Reranking, Phase 3 Generation & CoT)
    - `phan_tich_vai_tro`: Trang 15–16 (Phân tích kịch bản loại bỏ các thành phần)
    - `gioi_thieu_langchain`: Trang 17–19 (Tổng quan LangChain và Document Loaders/Splitters)
    - `thuc_hanh_pipeline`: Trang 21–30 (Thực hành mã nguồn, tiền xử lý, Chroma, HuggingFace LLM)
    - `cau_hoi_trac_nghiem`: Trang 31–34 (Câu hỏi ôn tập kiến thức)
  - Lý do chọn: Cho phép người dùng thu hẹp không gian tìm kiếm chính xác vào phần lý thuyết, thuật ngữ, hoặc mã nguồn thực hành, ngăn ngừa nhiễu ngữ nghĩa chéo chương.

---

## Cấu hình và benchmark
- **A / B / C (tham số cụ thể, khác biệt duy nhất B–C):**
  - *Chiến lược A (Fixed-size Window Chunking):* Cửa sổ cố định kích thước 500 ký tự, độ chồng lấp (overlap) 50 ký tự. Gắn metadata `document_id`, `source`, `page`, `section`. Truy xuất không lọc.
  - *Chiến lược B (Structure/Paragraph-aware Chunking):* Phân đoạn văn bản dựa trên ranh giới đoạn văn (`\n\n`) và câu kết thúc (`. `, `! `, `? `), gom các đoạn thành chunk có kích thước tối đa 700 ký tự. Gắn cùng bộ metadata, truy xuất không lọc.
  - *Chiến lược C (Structure/Paragraph-aware + Metadata Filter):* Dùng **chính xác các chunk của Chiến lược B**, tại thời điểm truy xuất áp dụng thêm bộ lọc metadata `section` khi câu hỏi có điều kiện lọc (chỉ lọc với giá trị filter được người dùng cung cấp trước).
  - *Kiểm soát so sánh:* A–B chỉ thay đổi kỹ thuật chunking (cố định vs cấu trúc đoạn). B–C chỉ thay đổi việc áp dụng metadata filtering.
  - *Mã nguồn Chunking:* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\chunking.py](../../starter/src/chunking.py).

- **≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence:**
  - Bộ benchmark gồm **20 câu hỏi** được lưu tại [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\benchmark\questions.json](../../benchmark/questions.json) và bản sao tại [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\data\benchmark.json](../../starter/data/benchmark.json):
    - **15 câu Dev** (`q01` – `q15`): gồm 8 câu trực tiếp, 3 câu diễn đạt lại, 2 câu điều kiện/ngoại lệ, và 2 câu kiểm tra metadata filter (`q10`, `q11`).
    - **5 câu Test** (`q16` – `q20`): gồm 2 câu trực tiếp, 1 câu diễn đạt lại, 1 câu điều kiện/ngoại lệ, và 1 câu kiểm tra metadata filter (`q18`).
  - *Mã nguồn đánh giá (Evaluation):* [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\src\evaluation.py](../../starter/src/evaluation.py).
  - *Kiểm chứng evidence:* 100% các đoạn `evidence_quote` được kiểm tra tự động và đối chiếu thủ công, đảm bảo tồn tại nguyên văn trên đúng số trang `gold_page` sau khi chuẩn hóa văn bản.

- **Tiêu chí chọn chiến lược đã chốt trước khi xem test:**
  1. Ưu tiên 1: Evidence Hit@3 trên tập Dev đạt cao nhất (độ bao phủ bằng chứng).
  2. Ưu tiên 2: Tính mạch lạc của chunk (Chunk Coherence) phải giữ trọn ý và ngữ cảnh.
  3. Ưu tiên 3: Tối ưu tài nguyên lưu trữ (số lượng vector index) và thời gian thực thi.

---

## Kết quả

### Bảng 1: Hiệu năng truy xuất và tài nguyên
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|---|---|---|---|---|
| **A** (Fixed 500/50) | Dev | 7/15 (46.67%) | 9/15 (60.00%) | 126 | 2.57s | $0.00 |
| **A** (Fixed 500/50) | Test | 4/5 (80.00%) | 5/5 (100.00%) | 126 | 2.57s | $0.00 |
| **B** (Paragraph max 700) | Dev | 7/15 (46.67%) | 11/15 (73.33%) | 97 | 1.92s | $0.00 |
| **B** (Paragraph max 700) | Test | 3/5 (60.00%) | 3/5 (60.00%) | 97 | 1.92s | $0.00 |
| **C** (B + Section Filter) | Dev | 7/15 (46.67%) | 11/15 (73.33%) | 97 | 1.92s | $0.00 |
| **C** (B + Section Filter) | Test | 3/5 (60.00%) | 3/5 (60.00%) | 97 | 1.92s | $0.00 |

### Bảng 2: Đánh giá chất lượng thủ công (Audit)
| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| **A** | 1.00 / 2 (10/10 mẫu) | 15/15 (100.0%) | 0/1 (0.0% - không áp dụng lọc) | Mức 2: 4, Mức 1: 1, Mức 0: 0 → **1.80 / 2** |
| **B** | 2.00 / 2 (10/10 mẫu) | 15/15 (100.0%) | 0/1 (0.0% - không áp dụng lọc) | Mức 2: 3, Mức 1: 0, Mức 0: 2 → **1.20 / 2** |
| **C** | 2.00 / 2 (10/10 mẫu) | 15/15 (100.0%) | 1/1 (100.0% tuân thủ tuyệt đối) | Mức 2: 3, Mức 1: 0, Mức 0: 2 → **1.20 / 2** |

- **Đường dẫn trace, nhãn thủ công và cách chọn mẫu:**
  - Full trace Strategy A: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\results\traces_strategy_a.json](../../starter/results/traces_strategy_a.json)
  - Full trace Strategy B: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\results\traces_strategy_b.json](../../starter/results/traces_strategy_b.json)
  - Full trace Strategy C: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\results\traces_strategy_c.json](../../starter/results/traces_strategy_c.json)
  - Bảng tổng hợp thí nghiệm: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\artifacts\experiment_log.csv](../../artifacts/experiment_log.csv)
  - Dữ liệu audit thủ công: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\results\manual_audit.json](../../starter/results/manual_audit.json)
  - Tóm tắt benchmark tổng hợp: [Lab06\K5-L3B-DAY06-HoangNgocHieu-2A202603976-DataIngestion\starter\results\benchmark_summary.json](../../starter/results/benchmark_summary.json)
  - *Cách chọn mẫu:* Coherence chọn 10 điểm cố định tại các trang tiêu biểu trải dài từ đầu đến cuối tài liệu (Trang 1, 3, 4, 6, 9, 11, 14, 17, 21, 24); Metadata và Grounding được audit trên toàn bộ 5 câu test × Top-3 (15 chunk/chiến lược).

---

## Phân tích và kết luận
- **So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:**
  - *So sánh A–B (Chunking):*
    - Trên tập Dev (15 câu), Strategy B vượt trội về Evidence Hit@3: đạt **73.33% (11/15)** so với **60.00% (9/15)** của Strategy A. Về tính mạch lạc (Coherence), Strategy B đạt tuyệt đối **2.00/2** do bảo toàn ranh giới câu và đoạn văn, trong khi Strategy A chỉ đạt **1.00/2** vì thường xuyên cắt ngang câu tại giới hạn 500 ký tự. Ngoài ra, Strategy B tạo ra ít hơn 23% số chunk (97 so với 126), giúp giảm kích thước index và thời gian nhúng (1.92s vs 2.57s).
    - Trên tập Test nhỏ (5 câu), Strategy A tình cờ đạt Hit@3 cao hơn (100% vs 60%) do một số câu hỏi có bằng chứng ngắn nằm ở đầu trang khớp tốt với cửa sổ cố định. Tuy nhiên, theo tiêu chí đã cố định trước khi xem test (ưu tiên kết quả Dev và Coherence), Strategy B là chiến lược ưu việt hơn về mặt thiết kế hệ thống.
  - *So sánh B–C (Metadata Filter):*
    - Đối với câu hỏi có filter như `q18` (Test set: câu hỏi về sự cố ở Phase 2 Retrieval), ở Strategy B không lọc, vị trí Rank 3 rơi vào trang 5 (`ly_thuyet_co_ban`). Trong khi đó, ở Strategy C với filter `section="retrieval_generation"`, toàn bộ 100% kết quả top-3 đều thuộc đúng chương Retrieval, loại bỏ hoàn toàn các trang lý thuyết không liên quan.
  - *2 ví dụ sai tiêu biểu:*
    1. **Câu `q17` (Test, Trang 3 - Bảng thuật ngữ):** *"Giới hạn số lượng tokens tối đa mà LLM có thể tiếp nhận và xử lý trong một lần prompt được gọi là gì?"* (Đáp án: Context Window).
       - Ở Strategy B & C: Do trang 3 chứa toàn bộ bảng thuật ngữ dưới dạng các dòng liên tiếp, việc nhóm đoạn khiến định nghĩa "Context Window" bị gộp chung với nhiều thuật ngữ khác (Grounding, Chunking), làm loãng mật độ vector so với một đoạn mã nguồn ở trang 34 có chứa từ khóa "prompt", dẫn đến Top-3 không trúng trang 3 (Hit@3 = False).
       - Ở Strategy A: Cửa sổ cố định 500 ký tự tình cờ cắt trúng khối chứa Context Window với mật độ cao, giúp Strategy A trúng ngay Rank 1 (Score: 0.7532).
    2. **Câu `q19` (Test, Trang 16 - Kịch bản 3: Loại bỏ LLM):** *"Theo phân tích kịch bản mở rộng, vai trò bộ não của LLM trong hệ thống RAG là gì?"*
       - Ở Strategy B & C: Mô hình embedding ưu tiên các chunk ở Trang 1 và Trang 15 có từ khóa "mở rộng" và "LLM", trong khi chunk chứa cụm từ chính xác *"Vai trò LLM: Bộ não..."* ở Trang 16 xếp ở vị trí sau hoặc bị thiếu do phân đoạn quá dài.

- **Chiến lược chọn, đánh đổi, điều kiện áp dụng:**
  - *Chiến lược được chọn:* **Chiến lược B kết hợp bộ lọc linh hoạt (C khi có ngữ cảnh)**.
  - *Đánh đổi:* Mặc dù Strategy A có thể cho kết quả ngẫu nhiên tốt hơn ở một vài câu hỏi test ngắn hạn, nó đánh đổi tính hoàn chỉnh ngữ nghĩa của chunk (cắt đứt giữa câu, mất chủ ngữ khiến LLM dễ ảo giác khi sinh câu trả lời thực tế). Strategy B tạo ra các chunk tự đứng độc lập được (Coherence = 2.0), tiết kiệm 23% chi phí lưu trữ/tính toán.
  - *Điều kiện áp dụng:* Khi corpus có cấu trúc chương mục và tiêu đề rõ ràng, chiến lược phân đoạn theo cấu trúc kết hợp metadata filtering là tối ưu nhất.

- **Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí:**
  - *Tập test nhỏ (5 câu):* Kích thước mẫu 5 câu có phương sai lớn (mỗi câu chiếm 20%), nên biến động giữa A và B phản ánh độ nhạy của mẫu hơn là xu hướng tổng quát; tập Dev (15 câu) phản ánh đáng tin cậy hơn.
  - *Đo thời gian:* Thời gian chạy trên GPU RTX 4060 rất nhanh (~2 giây cho 100 chunk) nên chênh lệch thời gian giữa các lần chạy bị ảnh hưởng nhỏ bởi I/O đĩa.
  - *Chi phí:* Chi phí tài chính bằng $0 do chạy mô hình nguồn mở cục bộ, nhưng yêu cầu phần cứng tối thiểu có GPU hỗ trợ CUDA và dung lượng RAM > 8GB.

- **Nếu làm lại hoặc mở rộng, cải tiến gì?**
  1. *Hybrid Retrieval (Dense + BM25):* Kết hợp giữa `google/embeddinggemma-2` và BM25 thông qua thuật toán RRF (Reciprocal Rank Fusion) để xử lý triệt để các câu hỏi hỏi về định nghĩa chính xác thuật ngữ (như `q17`).
  2. *Adaptive Semantic Chunking:* Chia chunk linh hoạt theo khoảng cách cosine giữa các câu liên tiếp thay vì chỉ dựa vào ngắt dòng đoạn văn (`\n\n`), giúp các đoạn có mật độ ngữ nghĩa đồng nhất hơn.
  3. *Tự động sinh Metadata Filter qua LLM Guardrail:* Cho phép hệ thống tự phân loại ý định người dùng thành trường `section` trước khi gửi truy vấn đến Qdrant.
