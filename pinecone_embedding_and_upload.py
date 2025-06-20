from langchain.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from tqdm import tqdm



#네임스페이스 이름 : policy, subject, admission, book, service

def upload_in_batches(docs, embeddings, index_name, namespace, batch_size=32):
    """
    문서를 Pinecone에 배치 단위로 업로드하는 함수

    Args:
        docs (list): Document 객체 리스트
        embeddings: LangChain 임베딩 객체
        index_name (str): Pinecone 인덱스 이름
        namespace (str): Pinecone namespace 이름 (e.g., "subject")
        batch_size (int): 업로드 배치 크기 (기본값: 32)
    """
    all_batches = [docs[i:i+batch_size] for i in range(0, len(docs), batch_size)]
    for i, batch in enumerate(tqdm(all_batches, desc=f"Uploading to Pinecone (ns={namespace})")):
        PineconeVectorStore.from_documents(
            documents=batch,
            embedding=embeddings,
            index_name=index_name,
            namespace=namespace,
        )