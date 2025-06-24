# backend

이 디렉터리는 FastAPI를 활용해 챗봇의 백엔드 API 서버를 구현합니다.  
현재 이 백엔드는 **MyFolio 서비스와 연동될 웹 페이지에 연결하기 위한 목적**으로 개발되었으며,  
**프론트엔드와 백엔드를 분리**하여 구성되어 있습니다.  

현재 상태에서는 로컬 환경에서 작동하지만, 실제 서비스를 위해서는 **퍼블릭 서버에 배포가 필요**합니다.  
이를 통해 프론트엔드 페이지에서 사용자의 질문을 받아 챗봇 응답을 API 형태로 전달하게 됩니다.

## 주요 파일

- `main.py`: FastAPI 애플리케이션 진입점으로, `/chat/` 엔드포인트를 통해 챗봇과의 상호작용을 처리합니다.

## 주요 기능

- `/chat/` POST API:
  - 사용자의 질문과 선택적 `user_id`, `category`를 받아 챗봇 응답을 반환합니다.
  - 내부적으로 `adaptive_rag`의 `initialize_graph_for_api()`와 `get_chatbot_response()`를 호출합니다.
  - 응답에는 다음이 포함됩니다:
    - `answer`: 생성된 응답 텍스트
    - `documents`: 검색 기반 RAG 문서 리스트 (옵션)
    - `user_id`, `category`, `question`

## 실행 방법

    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload`: 코드 변경 시 서버가 자동으로 재시작 (개발 시 유용).
    *   `--host 0.0.0.0`: 모든 네트워크 인터페이스에서 접속을 허용.
    *   `--port 8000`: 서버가 8000번 포트에서 실행.

    서버가 정상적으로 시작되면 다음과 유사한 로그가 터미널에 출력:
    ```
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [...] using [...]
    INFO:     Started server process [...]
    INFO:     Waiting for application startup.
    Application startup: Initializing RAG graph...
    Initializing RAG graph for API...
    RAG graph initialized for API.
    RAG graph initialized and ready.
    INFO:     Application startup complete.
    ```

## 전제 조건

**환경변수 설정** :
    adaptive_rag 모듈이 정상적으로 동작해야 하며, 아래 환경 변수 또는 .env 설정 필요:

    - OPENAI_API_KEY
    - PINECONE_API_KEY
    - COHERE_API_KEY
    - MONGODB_API_KEY

**의존성 패키지 설치**:
    프로젝트 루트 디렉토리에 `requirements.txt` 파일이 있는지 확인하고, 다음 명령어를 실행하여 필요한 패키지를 설치.
    ```bash
    pip install -r requirements.txt
    ```
