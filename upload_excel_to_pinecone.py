from tqdm import tqdm
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

def upload_in_batches(documents: list[Document], embeddings, index_name: str, namespace: str, batch_size: int = 32):
    for i in tqdm(range(0, len(documents), batch_size), desc="Uploading to Pinecone"):
        batch = documents[i:i+batch_size]
        PineconeVectorStore.from_documents(
            documents=batch,
            embedding=embeddings,
            index_name=index_name,
            namespace=namespace
        )
