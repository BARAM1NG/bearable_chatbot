import pandas as pd
from langchain_core.documents import Document
from collections import defaultdict

# -----------------------------
# 1. 파일 로드 및 전처리
# -----------------------------
def load_csv(file_path: str, drop_columns: list = None) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    if drop_columns:
        df = df.drop(columns=drop_columns)
    return df

# -----------------------------
# 2. 전공별 책 요약 문서 생성 (청크 단위)
# -----------------------------
def merge_documents_by_major_with_chunking(df: pd.DataFrame, max_books_per_doc: int = 10) -> list[Document]:
    grouped = defaultdict(list)

    for _, row in df.iterrows():
        grouped[row["major"]].append({
            "bookName": row["bookName"],
            "author": row["author"],
            "summary": row["bookSummary"],
            "department": row["department"]
        })

    merged_documents = []
    for major, entries in grouped.items():
        for i in range(0, len(entries), max_books_per_doc):
            chunk = entries[i:i + max_books_per_doc]
            combined_text = ""
            for e in chunk:
                combined_text += (
                    f"[책 제목: {e['bookName']}]\n"
                    f"[저자: {e['author']}]\n"
                    f"[요약]\n{e['summary']}\n"
                    f"[분야]\n{e['department']}\n"
                    f"{'-'*40}\n"
                )

            metadata = {
                "major": major,
                "num_books": len(chunk),
                "type": "merged_book_summaries",
                "department": chunk[0].get("department", "Unknown"),
                "chunk_index": i // max_books_per_doc
            }

            merged_documents.append(Document(page_content=combined_text, metadata=metadata))

    return merged_documents

