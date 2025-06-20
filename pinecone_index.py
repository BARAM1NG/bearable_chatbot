from pinecone import Pinecone
from config import PINECONE_API_KEY

def init_pinecone(api_key: str, index_name: str):
    """
    Pinecone 인스턴스를 초기화하고 지정된 인덱스를 반환합니다.
    
    Args:
        api_key (str): Pinecone API 키
        index_name (str): 사용할 인덱스 이름
    
    Returns:
        Index: Pinecone 인덱스 객체
    """
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    return index
