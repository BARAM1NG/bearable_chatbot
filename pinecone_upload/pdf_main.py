# pdf_main.py

#사용자 선택
# '''1. CHUNKING을 의미 단위로 할지, 페이지 단위로 할지 선택
#    2. 페이지단위로 할 시 1페이지 단위로 청크할지, 2페이지 단위로 청크할지 선택
#    3. 페이지단위로 청크할 때 metadata를 포함하면 안되는 파일 존재, -> USE_METADATA = False
# '''

# CHUNK_MODE = "meaning" or "page"
# PAGE_UNIT = 페이지 단위 자르기 (1 or 2) (CHUNK_MODE가 "page"일 때만 사용)
# USE_METADATA = 페이지별 청크일 때 metadata 포함 여부 정하기기
# FILE_PATHS = 실제 경로
# INDEX_NAME = Pinecone 인덱스 이름 / 웹에서 직접 인덱스 생성 후 사용
# NAMESPACE = Pinecone 네임스페이스 설정 / 문서 별 다르게 넣기

from pipeline_runner import run_pdf_to_pinecone_pipeline

if __name__ == "__main__":
    run_pdf_to_pinecone_pipeline(
        file_path=r"C:\Users\moonk\OneDrive\바탕 화면\대학생활\세미나\고교학점제 자료\편집본\2025신입생학부모를위한 고등학교 안내서_경기교육청_편집본.pdf",
        chunk_mode="meaning",
        page_unit=1,
        use_metadata=True,
        index_name="myfolio-chatbot",
        namespace="policy"
    )

