from document_chunking import (
    extract_by_page,
    extract_by_2pages,
    load_and_process_docs,
    load_and_process_docs_chunk_by_page_metadata,
    load_and_process_docs_chunk_by_page
)

def load_documents_with_chunking(pdf_path, chunk_mode="page", page_unit=1, use_metadata=True):
    """
    PDF를 의미 단위 또는 페이지 단위로 로드하고 청크화합니다.

    Args:
        pdf_path (str): PDF 파일 경로
        chunk_mode (str): "meaning" 또는 "page"
        page_unit (int): 1 또는 2 (page mode일 경우)
        use_metadata (bool): 페이지별 청크에 메타데이터 포함 여부

    Returns:
        list: 청크된 문서 리스트
    """
    if chunk_mode == "meaning":
        return load_and_process_docs(pdf_path)

    elif chunk_mode == "page":
        if page_unit == 1:
            docs_by_page = extract_by_page(pdf_path)
        elif page_unit == 2:
            docs_by_page = extract_by_2pages(pdf_path)
        else:
            raise ValueError("page_unit은 1 또는 2만 가능합니다.")

        if use_metadata:
            return load_and_process_docs_chunk_by_page_metadata(docs_by_page, pdf_path)
        else:
            return load_and_process_docs_chunk_by_page(docs_by_page)

    else:
        raise ValueError("chunk_mode는 'meaning' 또는 'page' 중 하나여야 합니다.")
