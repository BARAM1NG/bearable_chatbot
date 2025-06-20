from langchain_docling import DoclingLoader
from docling.chunking import HybridChunker
from langchain_docling.loader import ExportType
from langchain_core.documents import Document
import fitz  # PyMuPDF
from langchain.schema import Document
import os

# 문서 로딩 및 청킹을 위한 설정
EXPORT_TYPE = ExportType.DOC_CHUNKS # 문서 청크 추출 타입 설정
EMBED_MODEL_ID = "BAAI/bge-m3"

def load_and_process_docs(pdf_path, embed_model_id = "BAAI/bge-m3", chunk_size=1000, overlap=100):
    """
    문서를 로드하고 Pinecone 호환 메타데이터로 처리하는 함수
    
    Args:
        pdf_path (list): 로드할 파일 경로 리스트
        embed_model_id (str): 임베딩 모델 ID
        chunk_size (int, optional): 청크 크기. 기본값 1200
        overlap (int, optional): 청크 오버랩. 기본값 100
        
    Returns:
        list: Pinecone 호환 메타데이터를 가진 Document 객체 리스트
    """
    # DoclingLoader 초기화 및 로딩

    if isinstance(pdf_path, str):
        pdf_path = [pdf_path]

    loader = DoclingLoader(
        file_path=pdf_path,
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker(tokenizer=embed_model_id, chunk_size=chunk_size, overlap=overlap)
    )
    
    # 문서 로드
    original_docs = loader.load()
    print(f"로드된 문서 수: {len(original_docs)}")
    
    # 메타데이터 변환 및 새 문서 생성
    pinecone_docs = []
    
    for doc in original_docs:
        # 메타데이터에서 필요한 정보만 추출
        simplified = {}
        metadata = doc.metadata
        
        # 1. dl_meta의 doc_items의 label 추출
        if 'dl_meta' in metadata and isinstance(metadata['dl_meta'], dict):
            # headings 추출
            if 'headings' in metadata['dl_meta']:
                simplified['headings'] = metadata['dl_meta']['headings']
                
            # doc_items의 label 추출
            if 'doc_items' in metadata['dl_meta'] and metadata['dl_meta']['doc_items']:
                items = metadata['dl_meta']['doc_items']
                labels = [item.get('label') for item in items if 'label' in item]
                if labels:
                    simplified['doc_items_labels'] = labels

        # 2. origin의 filename 추출
        if ('dl_meta' in metadata and 'origin' in metadata['dl_meta'] and 
                'filename' in metadata['dl_meta']['origin']):
            simplified['filename'] = metadata['dl_meta']['origin']['filename']
        
        # 페이지 번호 추가 (있을 경우)
        if 'page' in metadata:
            simplified['page'] = metadata['page']
        
        # 새 Document 객체 생성
        pinecone_docs.append(
            Document(
                page_content=doc.page_content,
                metadata=simplified
            )
        )
    
    # 결과 요약
    if pinecone_docs:
        print(f"변환된 문서 수: {len(pinecone_docs)}")
        print("샘플 메타데이터:")
        print(pinecone_docs[0].metadata)
    
    return pinecone_docs


def extract_by_page(pdf_path):
    '''PDF 파일을 페이지 단위로 추출하여 Document 객체 리스트로 반환하는 함수'''

    doc = fitz.open(pdf_path)
    docs = []

    filename = os.path.basename(pdf_path)

    for i, page in enumerate(doc):
        text = page.get_text()
        docs.append(Document(
            page_content=text,
            metadata={"page": i + 1, "filename": filename}
        ))
    return docs


def extract_by_2pages(pdf_path):
    '''PDF 파일을 2페이지 단위로 추출하여 Document 객체 리스트로 반환하는 함수'''
    doc = fitz.open(pdf_path)
    docs = []

    filename = os.path.basename(pdf_path)

    for i in range(0, len(doc), 2):
        # 두 페이지의 텍스트를 이어붙이기
        text = doc[i].get_text()
        if i + 1 < len(doc):
            text += "\n" + doc[i + 1].get_text()
        
        docs.append(Document(
            page_content=text,
            metadata={
                "page_range": f"{i + 1}-{min(i + 2, len(doc))}",
                "filename": filename
            }
        ))
    return docs

#기존 함수에서 load를 위에 extract_by_page 함수 출력값으로 대체
#chunker를 by_page=True로 설정하여 페이지 단위로 청킹, chunk_size를 99999로 설정하여 페이지 전체를 하나의 청크로 처리, overlap을 0으로 설정하여 페이지 간 중복을 방지




def load_and_process_docs_chunk_by_page(docs, embed_model_id ="BAAI/bge-m3", chunk_size=99999, overlap=0):
    """
    문서를 로드하고 Pinecone 호환 메타데이터로 처리하는 함수
    
    Args:
        docs (list): 한 페이지 씩 나누어진 문서 리스트
        embed_model_id (str): 임베딩 모델 ID
        chunk_size (int, optional): 청크 크기. 기본값 99999
        overlap (int, optional): 청크 오버랩. 기본값 0
        by_page (bool, optional): 페이지 단위로 청킹 여부. 기본값 True
        
    Returns:
        list: Pinecone 호환 메타데이터를 가진 Document 객체 리스트
    """
    # DoclingLoader 초기화 및 로딩
    loader = DoclingLoader(
        docs,
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker(tokenizer=embed_model_id, chunk_size=chunk_size, overlap=overlap, by_page=True)   
    )
    
    # 문서 로드
    original_docs =docs #이 부분을 수정하여 extract_by_page 함수의 결과를 사용

    print(f"로드된 문서 수: {len(original_docs)}")
    
    # 메타데이터 변환 및 새 문서 생성
    pinecone_docs = []
    
    for doc in original_docs:
        # 메타데이터에서 필요한 정보만 추출
        simplified = {}
        # 수동 메타데이터 구성
        if "filename" in doc.metadata:
            simplified["filename"] = doc.metadata["filename"]
        if "page_range" in doc.metadata:
            simplified["page_range"] = doc.metadata["page_range"]
        if "page" in doc.metadata:
            simplified["page"] = doc.metadata["page"]

        pinecone_docs.append(Document(
            page_content=doc.page_content,
            metadata=simplified
        ))
    # 결과 요약
    if pinecone_docs:
        print(f"변환된 문서 수: {len(pinecone_docs)}")
        print("샘플 메타데이터:")
        print(pinecone_docs[0].metadata)
    
    return pinecone_docs



def load_and_process_docs_chunk_by_page_metadata(docs, pdf_path,embed_model_id = "BAAI/bge-m3", chunk_size=99999, overlap=0):
    """
    문서를 로드하고 Pinecone 호환 메타데이터로 처리하는 함수
    
    Args:
        docs (list): 한 페이지 씩 나누어진 문서 리스트
        embed_model_id (str): 임베딩 모델 ID
        chunk_size (int, optional): 청크 크기. 기본값 99999
        overlap (int, optional): 청크 오버랩. 기본값 0
        by_page (bool, optional): 페이지 단위로 청킹 여부. 기본값 True
        
    Returns:
        list: Pinecone 호환 메타데이터를 가진 Document 객체 리스트
    """
    # DoclingLoader 초기화 및 로딩
    loader = DoclingLoader(
        [pdf_path],
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker(tokenizer=embed_model_id, chunk_size=chunk_size, overlap=overlap, by_page=True)   
    )
    
    # 문서 로드
    original_docs =docs #이 부분을 수정하여 extract_by_page 함수의 결과를 사용

    print(f"로드된 문서 수: {len(original_docs)}")

    docling_docs = loader.load()

    print(f"원본 문서 수: {len(docs)}, Docling 분석 문서 수: {len(docling_docs)}")
    
    # 메타데이터 변환 및 새 문서 생성
    pinecone_docs = []
    for original_doc, docling_doc in zip(docs, docling_docs):
        simplified = {}

        # 1. 원래 metadata에서 page, filename 등 유지
        if "page" in original_doc.metadata:
            simplified["page"] = original_doc.metadata["page"]
        if "filename" in original_doc.metadata:
            simplified["filename"] = original_doc.metadata["filename"]

        # 2. Docling에서 생성한 dl_meta 병합
        dl_meta = docling_doc.metadata.get("dl_meta", {})

        # headings 추출
        if "headings" in dl_meta:
            simplified["headings"] = dl_meta["headings"]

        # doc_items_labels 추출
        if "doc_items" in dl_meta:
            labels = [item.get("label") for item in dl_meta["doc_items"] if "label" in item]
            if labels:
                simplified["doc_items_labels"] = labels

        # origin filename 추출 (있으면 덮어쓰기)
        if "origin" in dl_meta and "filename" in dl_meta["origin"]:
            simplified["filename"] = dl_meta["origin"]["filename"]

        pinecone_docs.append(
            Document(
                page_content=original_doc.page_content,
                metadata=simplified
            )
        )

    if pinecone_docs:
        print(f"변환된 문서 수: {len(pinecone_docs)}")
        print("샘플 메타데이터:")
        print(pinecone_docs[0].metadata)

    return pinecone_docs
