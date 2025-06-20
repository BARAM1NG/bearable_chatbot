# pipeline_runner_excel.py

from excel_chunk_and_merge import load_csv, merge_documents_by_major_with_chunking
from config import OPENAI_API_KEY, PINECONE_API_KEY
from pinecone_index import init_pinecone
from upload_excel_to_pinecone import upload_in_batches
from langchain.embeddings import OpenAIEmbeddings
from collections import defaultdict

def run_excel_to_pinecone_pipeline(
    file_path: str,
    drop_columns: list,
    index_name: str,
    namespace: str,
    embedding_model: str = 'text-embedding-3-large',
    batch_size: int = 32
):
    # 1. CSV 로딩 및 전처리
    df = load_csv(file_path, drop_columns=drop_columns)
    major_docs = merge_documents_by_major_with_chunking(df)

    # 2. 전공별로 그룹핑
    grouped = defaultdict(list)
    for doc in major_docs:
        grouped[doc.metadata["major"]].append(doc)

    # 3. 임베딩 모델 로딩
    embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=OPENAI_API_KEY)

    # 4. Pinecone 연결
    init_pinecone(api_key=PINECONE_API_KEY, index_name=index_name)

    # 5. Pinecone 업로드
    for major, doc_list in grouped.items():
        upload_in_batches(
            documents=doc_list,
            embeddings=embeddings,
            index_name=index_name,
            namespace=namespace,
            batch_size=batch_size
        )
