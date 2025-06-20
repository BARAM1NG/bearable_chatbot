# main_excel.py
#해당 코드는 책 CSV 파일에 맞춰 Pinecone에 업로드하는 파이프라인을 실행합니다.

from pipeline_runner_excel import run_excel_to_pinecone_pipeline

if __name__ == "__main__":
    run_excel_to_pinecone_pipeline(
        file_path=r"C:\Users\moonk\OneDrive\바탕 화면\책샘플.csv", #파일경로 입력
        drop_columns=["publisher"], #제외할 열 입력
        index_name="myfolio-chatbot", # Pinecone 인덱스 이름
        namespace="book" # Pinecone 네임스페이스 설정
    )
