# pinecone_upload

이 디렉터리는 **PDF 및 Excel 문서를 청킹 후 Pinecone 벡터 DB에 업로드**하기 위한 파이프라인 코드들을 포함합니다.  
문서 형식(PDF/Excel)과 목적에 따라 적절한 전처리 및 업로드 방식이 분리되어 있으며, RAG 기반 챗봇의 검색 대상 문서를 구축하는 데 사용됩니다.

---

## 디렉터리 구성

### 1. Pinecone 인덱스 생성 및 업로드

- `pinecone_index.py`  
  → Pinecone 인덱스를 생성하는 함수 정의  
- `pinecone_embedding_and_upload.py`  
  → 문서 임베딩 후 Pinecone에 업로드하는 함수 정의

### 2. PDF 문서 처리

- `pdf_main.py`  
  → PDF 업로드를 위한 실행 메인 파일  
- `pdf_chunking.py`  
  → PDF 내용을 의미 단위 또는 페이지 단위로 청킹  
- `pipeline_runner.py`  
  → 청크된 데이터를 Pinecone에 업로드하는 실행 파이프라인

### 3. Excel 문서 처리

- `excel_main.py`  
  → Excel 업로드 실행용 메인 파일  
- `excel_load_and_chunk.py`  
  → Excel 데이터 로드 및 전처리, 열 제거, 청킹 수행  
- `pipeline_runner_excel.py`  
  → 청크된 Excel 데이터를 Pinecone에 업로드하는 실행 파이프라인

---

## 실행 예시

### PDF 업로드

```python
from pipeline_runner import run_pdf_to_pinecone_pipeline

if __name__ == "__main__":
    run_pdf_to_pinecone_pipeline(
        file_path=r"C:/Users/사용자/Desktop/고등학교안내서.pdf",
        chunk_mode="meaning",               # "meaning", "page" 등 선택 가능
        page_unit=1,                        # 페이지 단위 청킹 시 사용
        use_metadata=True,                  # 메타데이터 포함 여부
        index_name="myfolio-chatbot",       # Pinecone 인덱스 이름
        namespace="policy"                  # 업로드할 namespace
    )
```
### EXCEL 업로드

```python
from pipeline_runner_excel import run_excel_to_pinecone_pipeline

if __name__ == "__main__":
    run_excel_to_pinecone_pipeline(
        file_path=r"C:/Users/사용자/Desktop/책샘플.csv",
        drop_columns=["publisher"],         # 제거할 열
        index_name="myfolio-chatbot",
        namespace="book"
    )
```

## 업로드 대상 문서
업로드할 원본 문서는 다음 구글 드라이브 폴더에 정리되어 있습니다:

[업로드 문서 폴더 바로가기](https://drive.google.com/drive/folders/19EWrhd1thP2TnYNQPQwnOEVKYElCSQI1)

## 업로드 시 주의사항

### 1. 문서 형식 구분

- **PDF 문서** → `pipeline_runner.py` 사용
- **Excel 문서** → `pipeline_runner_excel.py` 사용

---

### 2. 올바른 Namespace 지정

| Namespace   | 설명                                |
|-------------|-------------------------------------|
| `admission` | 입시 용어, 대학 및 학과 정보        |
| `subject`   | 과목 소개 및 추천 과목 정보         |
| `policy`    | 고교학점제 운영 관련 정보           |
| `book`      | 도서 관련 데이터                    |
| `service`   | 서비스 문의 관련 데이터 *(미운영)*  |

---

### 3. 청킹 방식 선택

- **PDF**: `"meaning"` (의미 단위), `"page"` (페이지 단위)
- **Excel**: 제거할 열 지정

---

## 필요 환경 변수 (API Key)
아래 API 키는 `.env` 파일 또는 시스템 환경 변수로 설정해야 합니다:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`

---

## 필수 설치 패키지
가상환경 활성화를 권장합니다.
```bash
pip install -r requirements.txt
```
