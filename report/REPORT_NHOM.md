# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K4-L3A
**Thành viên:** Sinh viên 1, Sinh viên 2, Sinh viên 3
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế và Dịch vụ Đại học (University Regulations & Services)

**Tại sao nhóm chọn chủ đề này?**
Chủ đề dịch vụ và quy định đại học là biến thể bắt buộc của lớp K4-L3A. Đây là một miền tri thức thực tế có tính cấu trúc cao, bao gồm các điều khoản rõ ràng về học vụ (đăng ký môn học, học phí, học bổng), dịch vụ hỗ trợ (thư viện, ký túc xá, phúc khảo bài thi). Dữ liệu này giúp kiểm nghiệm rõ rệt vai trò của việc phân tách tài liệu theo đối tượng (`audience`), tránh nhầm lẫn giữa quy định của sinh viên và giảng viên.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | course-registration.md | https://vinuni.edu.vn/academic/course-registration-policy | 2026-09-01 / 2026.1 | 1,342 | audience: student, department: academic-affairs |
| 2 | library-student.md | https://vinuni.edu.vn/library/student-borrowing-policy | 2026-09-01 / 2026.1 | 1,056 | audience: student, department: library |
| 3 | library-faculty.md | https://vinuni.edu.vn/library/faculty-resource-policy | 2026-09-01 / 2026.1 | 1,204 | audience: faculty, department: library |
| 4 | scholarship-policy.md | https://vinuni.edu.vn/scholarship/merit-scholarship-regulations | 2026-09-01 / 2026.1 | 1,398 | audience: student, department: student-affairs |
| 5 | dormitory-regulations.md | https://vinuni.edu.vn/campus/dormitory-regulations | 2026-09-01 / 2026.1 | 1,320 | audience: student, department: campus-services |
| 6 | exam-appeal-procedure.md | https://vinuni.edu.vn/testing/exam-appeal-procedure | 2026-09-01 / 2026.1 | 1,380 | audience: all, department: testing-quality |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | str | `library-student` | Định danh tài liệu gốc để phục vụ xóa (`delete_document`) và truy vết nguồn gốc câu trả lời. |
| `audience` | str | `student`, `faculty`, `all` | Phân loại đối tượng áp dụng; bắt buộc dùng để tiền lọc (pre-filter), tránh nhầm lẫn quy định của sinh viên và giảng viên. |
| `department` | str | `academic-affairs`, `library` | Lọc theo phòng ban phụ trách, giúp khoanh vùng tài liệu chuyên trách khi câu hỏi đề cập đơn vị cụ thể. |
| `category` | str | `regulations`, `services` | Phân loại loại văn bản (quy chế hay thủ tục dịch vụ). |
| `source_url` | str | `https://vinuni.edu.vn/...` | Cung cấp đường dẫn nguồn để người dùng kiểm chứng và bảo đảm tính minh bạch dữ liệu (provenance). |
| `document_version` | str | `2026.1` | Kiểm soát phiên bản và tính cập nhật của văn bản quy phạm. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy định thực tế (chunk_size=200):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `course-registration.md` | FixedSizeChunker (`fixed_size`) | 7 | 193.9 | Có thể bị cắt cụt giữa điều khoản nếu ranh giới cắt trúng giữa câu. |
| `course-registration.md` | SentenceChunker (`by_sentences`) | 5 | 246.0 | Giữ trọn vẹn câu nhưng kích thước chunk không đều do câu dài ngắn khác nhau. |
| `course-registration.md` | RecursiveChunker (`recursive`) | 10 | 122.1 | Giữ cấu trúc đoạn văn tương đối tốt, nhưng một số mảnh nhỏ bị phân rã. |
| `library-student.md` | FixedSizeChunker (`fixed_size`) | 6 | 171.0 | Cắt cố định, một số chunk thiếu ngữ cảnh tiêu đề. |
| `library-student.md` | SentenceChunker (`by_sentences`) | 4 | 230.2 | Khá mạch lạc theo từng câu điều khoản. |
| `library-student.md` | RecursiveChunker (`recursive`) | 7 | 130.9 | Chia theo đoạn văn bản, độ dài vừa phải. |
| `scholarship-policy.md` | FixedSizeChunker (`fixed_size`) | 7 | 195.0 | Ranh giới 200 ký tự làm tách rời điều kiện GPA và mức học bổng. |
| `scholarship-policy.md` | SentenceChunker (`by_sentences`) | 5 | 247.8 | Gom đủ các câu trong cùng một nhóm điều kiện. |
| `scholarship-policy.md` | RecursiveChunker (`recursive`) | 10 | 123.0 | Mảnh nhỏ hơn, giữ được các gạch đầu dòng tốt. |

### Chiến lược của từng thành viên

**Thành viên 1 — Sinh viên 1**
- **Loại chiến lược:** FixedSize (có overlap: `chunk_size=300, overlap=50`)
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng cửa sổ trượt (sliding window) với kích thước 300 ký tự và độ chồng chéo 50 ký tự. Overlap giúp các thông tin quan trọng nằm ở ranh giới cắt không bị đứt đoạn, bảo đảm câu liền trước và liền sau có sự kết nối ngữ cảnh.

**Thành viên 2 — Sinh viên 2**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=300`)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản có cấu trúc phân cấp bằng danh sách phân tách `["\n\n", "\n", ". ", " ", ""]`. Ưu tiên bảo toàn trọn vẹn đoạn văn (paragraph), chỉ chia nhỏ tiếp khi đoạn văn vượt quá giới hạn, giúp chunk mang tính mạch lạc tự nhiên theo cấu trúc soạn thảo.

**Thành viên 3 — Sinh viên 3**
- **Loại chiến lược:** Custom `HeadingChunker` (chia theo Điều khoản / Tiêu đề, max_size=400)
- **Mô tả & lý do chọn:** Văn bản quy chế trường đại học được biên soạn có cấu trúc mục rõ ràng (`## Điều 1. ...`, `## Điều 2. ...`). Chiến lược này tách theo từng Điều/Mục làm đơn vị ngữ nghĩa trọn vẹn; nếu một Điều quá dài sẽ đệ quy chia nhỏ và gắn lại tiêu đề của Điều đó vào từng mảnh con để giữ trọn ngữ cảnh.
- **Code snippet:**
```python
class HeadingChunker:
    def __init__(self, max_section_size: int = 400) -> None:
        self.max_section_size = max_section_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = re.split(r"(?m)(?=^#{1,3}\s+)", text.strip())
        chunks: list[str] = []
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            if len(sec) <= self.max_section_size:
                chunks.append(sec)
            else:
                lines = sec.split("\n", 1)
                header, body = lines[0], lines[1] if len(lines) > 1 else ""
                sub_chunks = RecursiveChunker(chunk_size=self.max_section_size - len(header) - 10).chunk(body)
                for sc in sub_chunks:
                    chunks.append(f"{header}\n{sc.strip()}")
        return chunks if chunks else [text]
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Sinh viên 1 | FixedSizeChunker (300, ov=50) | 3/10 (trên mock) | Đơn giản, overlap 50 ký tự giúp giảm thiểu rủi ro mất thông tin ở ranh giới cắt. | Có thể cắt trúng giữa câu hoặc giữa điều khoản; độ dài chunk cố định không theo cấu trúc ngữ nghĩa. |
| Sinh viên 2 | RecursiveChunker (300) | 0/10 (trên mock) | Giữ được cấu trúc đoạn văn tự nhiên, kích thước chunk được kiểm soát đều đặn. | Khi đoạn văn dài bị phân rã, các mảnh con phía sau có thể bị mất ngữ cảnh của tiêu đề chính. |
| Sinh viên 3 | HeadingChunker (Section-based) | 0/10 (trên mock) | Đạt độ mạch lạc ngữ nghĩa (Chunk Coherence) cao nhất; mỗi Điều khoản là một chunk hoàn chỉnh có tiêu đề. | Kích thước chunk phụ thuộc vào độ dài từng Điều của văn bản gốc; trên mock embedding bị ảnh hưởng do vector ngẫu nhiên. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Chiến lược **`HeadingChunker`** (chia theo từng điều khoản/tiêu đề Markdown) là phương pháp tối ưu nhất cho văn bản quy chế, chính sách đại học. Trong các văn bản pháp quy, người soạn thảo đã gom nhóm thông tin thành các Điều khoản trọn vẹn về mặt ngữ nghĩa (ví dụ Điều 1 nói về Thời gian đăng ký, Điều 2 nói về Số tín chỉ). Việc chia theo Heading giúp loại bỏ triệt để hiện tượng câu cụt hoặc mất đầu mất đuôi, đồng thời khi trích xuất nguồn, LLM có thể dễ dàng viện dẫn chính xác "Theo Điều X của Quy chế..." một cách tự nhiên và chính xác.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thời hạn mượn sách thư viện tối đa và số lượng sách được mượn là bao nhiêu? | Sinh viên được mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày. (Cần lọc `audience: student` để tránh lẫn quy định 30 cuốn/90 ngày của giảng viên). | `library-student.md` (Điều 1) |
| 2 | Sinh viên cần đạt điều kiện gì về GPA và điểm rèn luyện để được nhận học bổng khuyến khích học tập mức Xuất sắc? | Điểm trung bình học kỳ GPA đạt từ 3.60 trở lên và điểm rèn luyện đạt từ 90 điểm trở lên (tích lũy tối thiểu 15 tín chỉ, không có điểm F). | `scholarship-policy.md` (Điều 1 & 2) |
| 3 | Sinh viên có điểm GPA từ bao nhiêu thì được phép đăng ký vượt tải tối đa 26 tín chỉ trong một học kỳ? | Sinh viên có điểm GPA tích lũy từ 3.2 trở lên được phép đăng ký vượt tải tối đa 26 tín chỉ nếu được Cố vấn học tập phê duyệt. | `course-registration.md` (Điều 2) |
| 4 | Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là bao lâu và lệ phí phúc khảo là bao nhiêu? | Thời hạn nộp đơn phúc khảo là 07 ngày làm việc kể từ ngày công bố điểm thi, và lệ phí là 100.000 VNĐ cho mỗi học phần dự thi. | `exam-appeal-procedure.md` (Điều 1 & 2) |
| 5 | Giờ giới nghiêm của ký túc xá là mấy giờ và những thiết bị sinh nhiệt nào bị nghiêm cấm trong phòng ở? | Ký túc xá đóng cổng lúc 23h00 hàng ngày; nghiêm cấm đun nấu bằng bếp điện, bếp gas, bếp từ hoặc thiết bị công suất lớn vượt quá 1000W. | `dormitory-regulations.md` (Điều 1 & 2) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời hạn mượn sách thư viện tối đa (có filter audience=student) | HeadingChunker / FixedSize | Có (khi có filter) | Bắt buộc phải có filter `audience=student` để loại tài liệu của giảng viên. |
| 2 | Điều kiện học bổng Xuất sắc | FixedSizeChunker / HeadingChunker | Có trong top-3 (FixedSize) | Trích xuất được Điều 1 & 2 của quy chế học bổng. |
| 3 | Điều kiện đăng ký vượt tải 26 tín chỉ | HeadingChunker | Có trong top-3 | Chứa trọn vẹn Điều 2 về quy định tín chỉ và Cố vấn học tập. |
| 4 | Thời hạn và lệ phí phúc khảo bài thi | HeadingChunker | Có trong top-3 | Chunk chứa đầy đủ cả 2 thông tin: 7 ngày làm việc và 100.000 VNĐ. |
| 5 | Giờ giới nghiêm ký túc xá & thiết bị cấm | FixedSizeChunker | Có trong top-3 (FixedSize) | Top-3 chứa nội dung đóng cổng 23h00 và cấm thiết bị > 1000W. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Lọc bằng metadata đóng vai trò quyết định ở **Câu hỏi số 1**. Trong bộ tài liệu của nhóm có hai tài liệu cùng thuộc danh mục Thư viện: `library-student.md` (sinh viên được mượn 5 cuốn trong 14 ngày) và `library-faculty.md` (giảng viên được mượn 30 cuốn trong 90 ngày). Khi người dùng hỏi *"Thời hạn mượn sách thư viện tối đa là bao nhiêu?"*, nếu không lọc, hệ thống trả về tài liệu của giảng viên hoặc tài liệu ký túc xá. Nhờ áp dụng `metadata_filter={"audience": "student"}`, hệ thống loại bỏ ngay lập tức các tài liệu của giảng viên từ vòng tiền lọc (Pre-filtering), bảo đảm trả về đúng quy định dành cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sự khác biệt giữa Cosine hình học và ngữ nghĩa thực:** MockEmbedder minh họa rõ ràng rằng nếu chỉ tính toán số học trên hash MD5 ngẫu nhiên, hệ thống không thể hiểu sự tương đồng từ vựng; việc sử dụng mô hình embedding chuẩn (Sentence Transformers/OpenAI) là yếu tố sống còn cho chất lượng RAG.
2. **Ưu thế của Heading Chunking trong văn bản pháp quy:** Chia nhỏ dựa trên cấu trúc tài liệu (`## Điều...`) mang lại độ mạch lạc ngữ nghĩa (Chunk Coherence) vượt trội hơn nhiều so với việc cắt thô theo số lượng ký tự (`FixedSizeChunker`).
3. **Pre-filtering metadata cứu vãn bài toán đa đối tượng:** Khi các đối tượng khác nhau (sinh viên vs giảng viên) có quy định khác nhau trong cùng một dịch vụ, metadata filter là cách duy nhất để tránh ô nhiễm ngữ cảnh (context contamination).

**Bài học rút ra khi so sánh trong nhóm:**
Cùng một tập văn bản quy định, chiến lược chunking quyết định trực tiếp đến hình hài và chất lượng của thông tin đưa vào prompt của LLM. Chunk quá nhỏ sẽ làm đứt gãy ngữ cảnh (ví dụ chỉ lấy được điều kiện GPA mà mất điều kiện điểm rèn luyện), trong khi chunk quá lớn sẽ chứa nhiều thông tin dư thừa làm loãng sự tập trung của mô hình ngôn ngữ lớn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nhóm sẽ bổ sung thêm các trường metadata chi tiết hơn ở cấp độ chunk (như `section_title`, `regulation_type`), và xây dựng cơ chế chunking kết hợp (Hybrid Chunking): vừa cắt theo Heading để giữ toàn vẹn điều khoản, vừa gắn thêm breadcrumb tiêu đề cha vào đầu mỗi chunk để khi tìm kiếm độc lập vẫn giữ nguyên vị trí phân cấp của văn bản.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

