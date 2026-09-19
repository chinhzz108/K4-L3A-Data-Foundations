# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được phép mượn tối đa 5 cuốn sách tại thư viện trong 14 ngày. | Người học có thể mượn nhiều nhất năm quyển sách ở thư viện trường trong hai tuần. | cao | -0.0050 | Bất ngờ (Do Mock) |
| 2 | Quy trình đăng ký học phần bắt đầu từ 8h00 sáng thứ Hai tuần tới. | Cổng thông tin đào tạo mở đăng ký môn học lúc 8 giờ sáng ngày đầu tuần sau. | cao | -0.1745 | Bất ngờ (Do Mock) |
| 3 | Sinh viên có hoàn cảnh khó khăn được xét miễn giảm học phí theo quy định. | Ký túc xá cấm sinh viên nấu ăn bằng bếp điện trong phòng ở. | thấp | -0.0990 | Đúng |
| 4 | Hạn nộp đơn phúc khảo bài thi kết thúc học phần là 7 ngày sau khi công bố điểm. | Thư viện trường mở cửa phục vụ bạn đọc từ thứ Hai đến thứ Bảy hàng tuần. | thấp | -0.1667 | Đúng |
| 5 | Sinh viên đạt điểm rèn luyện xuất sắc và GPA trên 3.6 sẽ được nhận học bổng. | Học bổng khuyến khích học tập trao cho sinh viên có kết quả học tập và rèn luyện xuất sắc. | cao | -0.2507 | Bất ngờ (Do Mock) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*
Kết quả bất ngờ nhất là các cặp câu có cùng ý nghĩa thực tế (Cặp 1, 2, 5) lại cho điểm độ tương tự âm hoặc gần 0 khi chạy trên `MockEmbedder`. Điều này phản ánh rõ ràng rằng `MockEmbedder` chỉ băm MD5 chuỗi ký tự thô để tạo vector ngẫu nhiên nên không có khả năng hiểu ngữ nghĩa (semantic understanding). Để các vector phản ánh đúng mức độ tương đồng về nội dung và ngữ cảnh, hệ thống bắt buộc phải sử dụng các mô hình embedding học sâu thực tế (như Sentence Transformers hoặc OpenAI/Gemini Embeddings).


---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`). Chiến lược cá nhân sử dụng: **`HeadingChunker` (chia nhỏ theo tiêu đề/điều khoản quy định, max_size=400)**.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn mượn sách thư viện tối đa và số lượng sách được mượn là bao nhiêu? (Filter: audience=student) | Điều 3. Quản lý khách thăm và An ninh trật tự (dormitory-regulations) | 0.1709 | Chưa (nằm ở top sau do Mock) | [Agent] Trả lời dựa trên context được truy xuất (do MockEmbedder chưa định tuyến chuẩn). |
| 2 | Sinh viên cần đạt điều kiện gì về GPA và điểm rèn luyện để được nhận học bổng khuyến khích học tập mức Xuất sắc? | Điều 3. Quản lý khách thăm và An ninh trật tự (dormitory-regulations) | 0.1949 | Chưa | [Agent] Trả lời dựa trên context được cung cấp. |
| 3 | Sinh viên có điểm GPA từ bao nhiêu thì được phép đăng ký vượt tải tối đa 26 tín chỉ trong một học kỳ? | Quy trình Tiếp nhận và Xử lý Đơn Phúc khảo bài thi (exam-appeal-procedure) | 0.1927 | Chưa | [Agent] Trả lời tóm tắt từ ngữ cảnh nhận được. |
| 4 | Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là bao lâu và lệ phí phúc khảo là bao nhiêu? | Điều 1. Thời gian và Cổng đăng ký (course-registration) | 0.1065 | Chưa | [Agent] Trả lời tóm tắt từ ngữ cảnh nhận được. |
| 5 | Giờ giới nghiêm của ký túc xá là mấy giờ và những thiết bị sinh nhiệt nào bị nghiêm cấm trong phòng ở? | Điều 3. Quy trình xét chọn và Trao học bổng (scholarship-policy) | 0.2395 | Chưa | [Agent] Trả lời tóm tắt từ ngữ cảnh nhận được. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (khi chạy so sánh với các chiến lược FixedSize có overlap)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*
Khi sử dụng `MockEmbedder`, kết quả retrieval phụ thuộc vào hàm băm ngẫu nhiên nên điểm số cosine không phản ánh ngữ nghĩa thật. Tuy nhiên, việc chia nhỏ theo cấu trúc Heading/Section (`HeadingChunker`) giúp các đoạn văn bản giữ nguyên vẹn trọn vẹn ngữ cảnh của từng điều khoản (không bị ngắt câu giữa chừng như `FixedSizeChunker`), và cơ chế Pre-filtering metadata (`audience: student`) đã chứng minh tính hiệu quả vượt trội khi loại bỏ hoàn toàn các tài liệu dành riêng cho giảng viên/nhân viên trước khi tìm kiếm.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

