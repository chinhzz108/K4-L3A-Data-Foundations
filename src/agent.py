from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_blocks = []
        for i, res in enumerate(results, start=1):
            source = res.get("metadata", {}).get("source", res.get("id", "unknown"))
            content = res.get("content", "").strip()
            context_blocks.append(f"[{i}] (Nguồn: {source}):\n{content}")

        context = "\n\n".join(context_blocks)
        prompt = (
            "Bạn là trợ lý giải đáp thắc mắc dựa trên cơ sở tri thức.\n"
            "Dưới đây là các đoạn thông tin (context) được truy xuất để trả lời câu hỏi. "
            "Hãy chỉ dùng thông tin được cung cấp để trả lời, không tự suy đoán, và trích dẫn số thứ tự nguồn [1], [2] tương ứng.\n\n"
            f"--- NGỮ CẢNH ---\n{context}\n\n"
            f"--- CÂU HỎI ---\n{question}\n\n"
            "--- CÂU TRẢ LỜI ---"
        )
        return self.llm_fn(prompt)

