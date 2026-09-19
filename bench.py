from __future__ import annotations

import os
import re
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


class HeadingChunker:
    """
    Chiến lược chunking tùy chỉnh chia nhỏ theo các tiêu đề/mục (Heading/Section)
    của văn bản quy định đại học. Mỗi điều khoản (## Điều ...) là một chunk trọn vẹn.
    Nếu mục quá dài, chia nhỏ tiếp và gắn lại tiêu đề của mục vào từng mảnh con.
    """

    def __init__(self, max_section_size: int = 500) -> None:
        self.max_section_size = max_section_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Tách theo heading Markdown (## hoặc #)
        sections = re.split(r"(?m)(?=^#{1,3}\s+)", text.strip())
        chunks: list[str] = []

        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            if len(sec) <= self.max_section_size:
                chunks.append(sec)
            else:
                # Nếu section quá dài, lấy dòng header đầu tiên gắn vào các đoạn sau
                lines = sec.split("\n", 1)
                header = lines[0] if len(lines) > 0 else ""
                body = lines[1] if len(lines) > 1 else ""

                sub_chunks = RecursiveChunker(chunk_size=self.max_section_size - len(header) - 10).chunk(body)
                for sc in sub_chunks:
                    chunks.append(f"{header}\n{sc.strip()}")

        return chunks if chunks else [text]


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Thời hạn mượn sách thư viện tối đa và số lượng sách được mượn là bao nhiêu?",
        "filter": {"audience": "student"},
        "unfiltered_comparison": True,
        "gold_answer": "Sinh viên được mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày.",
        "gold_doc": "library-student",
        "gold_feature": "05 cuốn sách in trong thời hạn 14 ngày",
    },
    {
        "id": 2,
        "query": "Sinh viên cần đạt điều kiện gì về GPA và điểm rèn luyện để được nhận học bổng khuyến khích học tập mức Xuất sắc?",
        "filter": None,
        "unfiltered_comparison": False,
        "gold_answer": "Điểm trung bình học kỳ GPA đạt từ 3.60 trở lên và điểm rèn luyện đạt từ 90 điểm trở lên (tích lũy tối thiểu 15 tín chỉ, không có điểm F).",
        "gold_doc": "scholarship-policy",
        "gold_feature": "GPA đạt từ 3.60 trở lên và điểm rèn luyện đạt từ 90",
    },
    {
        "id": 3,
        "query": "Sinh viên có điểm GPA từ bao nhiêu thì được phép đăng ký vượt tải tối đa 26 tín chỉ trong một học kỳ?",
        "filter": None,
        "unfiltered_comparison": False,
        "gold_answer": "Sinh viên có điểm GPA tích lũy từ 3.2 trở lên được phép đăng ký vượt tải tối đa 26 tín chỉ nếu được Cố vấn học tập phê duyệt.",
        "gold_doc": "course-registration",
        "gold_feature": "GPA từ 3.2 trở lên được phép đăng ký vượt tải tối đa 26 tín chỉ",
    },
    {
        "id": 4,
        "query": "Thời hạn nộp đơn phúc khảo bài thi kết thúc học phần là bao lâu và lệ phí phúc khảo là bao nhiêu?",
        "filter": None,
        "unfiltered_comparison": False,
        "gold_answer": "Thời hạn nộp đơn phúc khảo là 07 ngày làm việc kể từ ngày công bố điểm thi, và lệ phí là 100.000 VNĐ cho mỗi học phần dự thi.",
        "gold_doc": "exam-appeal-procedure",
        "gold_feature": "07 ngày làm việc kể từ ngày phòng Khảo thí công bố điểm thi",
    },
    {
        "id": 5,
        "query": "Giờ giới nghiêm của ký túc xá là mấy giờ và những thiết bị sinh nhiệt nào bị nghiêm cấm trong phòng ở?",
        "filter": None,
        "unfiltered_comparison": False,
        "gold_answer": "Ký túc xá đóng cổng lúc 23h00 hàng ngày; nghiêm cấm đun nấu bằng bếp điện, bếp gas, bếp từ hoặc thiết bị công suất lớn vượt quá 1000W.",
        "gold_doc": "dormitory-regulations",
        "gold_feature": "đóng cổng vào lúc 23h00 hàng ngày",
    },
]


def parse_markdown_file(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2].strip()
            fm = dict(re.findall(r"^(\w+):\s*(.+)$", raw_fm, re.M))
            return fm, body
    return {}, text.strip()


def build_store(chunker, data_dir: Path = Path("data/university")) -> tuple[EmbeddingStore, int]:
    store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=_mock_embed)
    all_chunks: list[Document] = []

    for file_path in sorted(data_dir.glob("*.md")):
        metadata, body = parse_markdown_file(file_path)
        chunks = chunker.chunk(body)

        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{file_path.stem}#{i}",
                content=chunk_text,
                metadata={
                    **metadata,
                    "doc_id": file_path.stem,
                    "source": str(file_path),
                    "chunk_index": i,
                },
            )
            all_chunks.append(doc)

    store.add_documents(all_chunks)
    return store, len(all_chunks)


def run_benchmark(strategy_name: str, chunker) -> dict:
    store, total_chunks = build_store(chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda p: f"[AGENT ANSWER based on context: {p[:180].replace(chr(10), ' ')}...]")

    results = []
    print(f"\n=======================================================")
    print(f"CHIẾN LƯỢC: {strategy_name} (Tổng số chunk nạp vào store: {total_chunks})")
    print(f"=======================================================")

    for q in BENCHMARK_QUERIES:
        query_text = q["query"]
        meta_filter = q["filter"]
        top_results = store.search_with_filter(query_text, top_k=3, metadata_filter=meta_filter)

        top1 = top_results[0] if top_results else None
        top1_doc = top1["metadata"].get("doc_id", "none") if top1 else "none"
        top1_score = top1["score"] if top1 else 0.0

        # Kiểm tra sự xuất hiện của gold_doc và đặc trưng câu trả lời trong top-3
        has_gold_doc = any(r["metadata"].get("doc_id") == q["gold_doc"] for r in top_results)
        has_gold_feature = any(q["gold_feature"] in r["content"] for r in top_results)

        # Chấm điểm retrieval quality (0, 1, 2 điểm)
        if top1_doc == q["gold_doc"] and q["gold_feature"] in (top1["content"] if top1 else ""):
            score_pts = 2
        elif has_gold_doc and has_gold_feature:
            score_pts = 1
        elif has_gold_doc:
            score_pts = 1
        else:
            score_pts = 0

        agent_ans = agent.answer(query_text, top_k=3)

        res_entry = {
            "query_id": q["id"],
            "query": query_text,
            "filter": meta_filter,
            "top1_doc": top1_doc,
            "top1_score": top1_score,
            "top1_preview": (top1["content"][:100].replace("\n", " ") if top1 else "None"),
            "has_gold_doc": has_gold_doc,
            "has_gold_feature": has_gold_feature,
            "score_pts": score_pts,
            "agent_ans": agent_ans,
            "top_results": top_results,
        }
        results.append(res_entry)

        print(f"\n[Câu {q['id']}] {query_text}")
        if meta_filter:
            print(f"  * Bộ lọc metadata: {meta_filter}")
        print(f"  * Top-1 Doc: {top1_doc} (score={top1_score:.4f})")
        print(f"  * Có Gold doc trong Top-3: {has_gold_doc} | Chứa đáp án chuẩn: {has_gold_feature}")
        print(f"  * Điểm chất lượng: {score_pts}/2 điểm")
        print(f"  * Top-1 Preview: {res_entry['top1_preview']}...")

        # Nếu là câu có A/B so sánh filter
        if q["unfiltered_comparison"]:
            unfiltered_res = store.search_with_filter(query_text, top_k=3, metadata_filter=None)
            unfiltered_top1 = unfiltered_res[0]["metadata"].get("doc_id") if unfiltered_res else "none"
            print(f"  [A/B So sánh] Khi KHÔNG dùng filter: Top-1 Doc = {unfiltered_top1}")
            if unfiltered_top1 != q["gold_doc"]:
                print(f"  --> Bằng chứng: Khi không filter, hệ thống bị lẫn sang tài liệu khác ({unfiltered_top1})!")

    total_pts = sum(r["score_pts"] for r in results)
    print(f"\n===> Tổng điểm chất lượng truy xuất: {total_pts}/10 điểm")
    return {"strategy": strategy_name, "total_chunks": total_chunks, "score": total_pts, "results": results}


def main():
    strategies = [
        ("HeadingChunker (Section-based, max=400)", HeadingChunker(max_section_size=400)),
        ("FixedSizeChunker (size=300, overlap=50)", FixedSizeChunker(chunk_size=300, overlap=50)),
        ("RecursiveChunker (chunk_size=300)", RecursiveChunker(chunk_size=300)),
    ]

    summary_outputs = []
    output_file = Path("ket_qua_benchmark.txt")
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("=================================================================\n")
        out.write("KẾT QUẢ ĐÁNH GIÁ TRUY XUẤT (BENCHMARK RESULTS) — LAB 07 (K4-L3A)\n")
        out.write("Chủ đề: Dịch vụ & Quy định Đại học\n")
        out.write("=================================================================\n\n")

        for name, chunker in strategies:
            res = run_benchmark(name, chunker)
            summary_outputs.append(res)
            out.write(f"\n### CHIẾN LƯỢC: {name} (Tổng số chunks: {res['total_chunks']}) - Điểm: {res['score']}/10\n")
            for r in res["results"]:
                out.write(f"Câu {r['query_id']}: {r['query']}\n")
                out.write(f"  - Filter: {r['filter']}\n")
                out.write(f"  - Top-1: {r['top1_doc']} (score={r['top1_score']:.4f})\n")
                out.write(f"  - Có Gold trong Top-3: {r['has_gold_doc']} (Chứa nội dung đáp án: {r['has_gold_feature']})\n")
                out.write(f"  - Điểm câu: {r['score_pts']}/2\n")
                out.write(f"  - Top-1 Preview: {r['top1_preview']}\n\n")

    print(f"\n\n[ĐÃ LƯU] Kết quả benchmark đã được ghi vào file '{output_file}'.")


if __name__ == "__main__":
    main()
