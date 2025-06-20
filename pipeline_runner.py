# pipeline_runner.py

from config import OPENAI_API_KEY, PINECONE_API_KEY
from pinecone_index import init_pinecone
from pinecone_embedding_and_upload import upload_in_batches
from langchain.embeddings import OpenAIEmbeddings
from pdf_chunking import load_documents_with_chunking

def run_pdf_to_pinecone_pipeline(
    file_path: str,
    chunk_mode: str,
    page_unit: int,
    use_metadata: bool,
    index_name: str,
    namespace: str,
    embedding_model: str = 'text-embedding-3-large',
    batch_size: int = 32
):
    # 1. 문서 로딩 및 청크 처리
    chunked_docs = load_documents_with_chunking(
        pdf_path=file_path,
        chunk_mode=chunk_mode,
        page_unit=page_unit,
        use_metadata=use_metadata
    )

    # 2. 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        openai_api_key=OPENAI_API_KEY
    )

    # 3. Pinecone 인덱스 연결
    index = init_pinecone(api_key=PINECONE_API_KEY, index_name=index_name)

    # 4. Pinecone에 업로드
    upload_in_batches(
        docs=chunked_docs,
        embeddings=embeddings,
        index_name=index_name,
        namespace=namespace,
        batch_size=batch_size
    )

