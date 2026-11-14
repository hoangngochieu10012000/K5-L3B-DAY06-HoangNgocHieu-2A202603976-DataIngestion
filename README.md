# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Học viên: Hoàng Ngọc Hiệu - MSSV: 2A202603976 - Lớp: K5-L3B**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| **32 trang nội dung hữu ích** (AIO2025 RAG Tutorial) | **3 cấu hình (A, B, C)** | **20 câu hỏi (15 dev / 5 test)** |

---

## Hướng dẫn chạy và tái lập kết quả

### 1. Yêu cầu môi trường
- Python 3.11 – 3.13
- GPU (NVIDIA CUDA) hoặc CPU
- Cài đặt các thư viện phụ thuộc:
  ```bash
  pip install pypdf sentence-transformers qdrant-client torch transformers
  ```

### 2. Thực thi toàn bộ pipeline
Chạy trực tiếp từ thư mục gốc hoặc thư mục `starter/`:
```bash
# Cách 1: Từ thư mục gốc
python -m starter.src.run

# Cách 2: Từ thư mục starter/
cd starter
python -m src.run
```

Lệnh này sẽ tự động:
1. Đọc và chuẩn hóa dữ liệu từ [data/AIO2025_Tutorial_RAG.pdf](data/AIO2025_Tutorial_RAG.pdf) (32 trang nội dung).
2. Phân chia chunk cho Chiến lược A (Fixed 500/50) và Chiến lược B (Paragraph-based max 700).
3. Tạo vector embeddings với mô hình `google/embeddinggemma-2` (768 chiều).
4. Lưu trữ vào vector store cục bộ Qdrant Embedded tại `starter/results/qdrant_db/` (hỗ trợ kiểm tra idempotence không nhân bản).
5. Thực thi bộ benchmark 20 câu hỏi ([benchmark/questions.json](benchmark/questions.json)) qua 3 cấu hình A, B, C.
6. Tính toán Hit@1, Evidence Hit@3, xuất toàn bộ traces top-3 và cập nhật [artifacts/experiment_log.csv](artifacts/experiment_log.csv).

---

## Cấu trúc bài nộp
- `STUDENT.md`: Thông tin học viên Hoàng Ngọc Hiệu (MSSV: 2A202603976, Lớp: K5-L3B).
- `data/manifest.json`: Manifest chi tiết về corpus, số trang vật lý (35), số trang nội dung (32), quy tắc tính trang và quyền sử dụng.
- `benchmark/questions.json`: Bộ 20 câu hỏi benchmark kèm evidence quote đã kiểm chứng (15 dev / 5 test, 3 câu có metadata filter).
- `starter/src/` & `src/`: Mã nguồn pipeline gồm `ingestion.py`, `chunking.py`, `embeddings.py`, `store.py`, `evaluation.py`, `run.py`.
- `starter/results/` & `results/`: Traces top-3 của các chiến lược A, B, C, tóm tắt benchmark và nhãn audit thủ công.
- `artifacts/experiment_log.csv`: Bảng ghi nhật ký thí nghiệm chi tiết.
- `report/individual/2A202603976_HoangNgocHieu.md` & `report/individual/MSSV_HoTen.md`: Báo cáo chi tiết theo 5 khía cạnh đánh giá.
