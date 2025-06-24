# frontend

이 디렉터리는 **Streamlit 기반의 마이폴리오 챗봇 프론트엔드 UI**를 담당합니다.  
현재 구조는 **FastAPI 기반 백엔드와 분리된 형태로 개발되었으며**,  
**시연 및 테스트 목적의 데모 인터페이스**로 제작되었습니다.

사용자는 웹 페이지를 통해 챗봇과 대화하며, 카테고리를 선택해 보다 정확한 응답을 받을 수 있습니다.  
배포 전에는 로컬 환경에서 작동하며, 향후 실제 서비스 적용을 위해 별도 웹 프론트엔드로 확장 가능하도록 설계되어 있습니다.

---

## 웹 진입 화면

<img src="https://raw.githubusercontent.com/BARAM1NG/bearable_chatbot/67dcb3433c126e5964a6e8fc9b4729556060fbd4/frontend/asset/screenshot.png" width="500">

> 사용자가 처음 진입하면 위와 같은 카테고리 선택 인터페이스가 표시되며, Streamlit 기반의 챗 인터페이스로 이어집니다.

---

## 디렉터리 구성

| 파일/폴더        | 설명 |
|------------------|------|
| `app.py`         | Streamlit 애플리케이션 진입점 |
| `style.css`      | 챗봇 스타일링을 위한 커스텀 CSS |
| `asset/`         | 로고 이미지(`mypolio.png`) 및 캡처 이미지 저장 폴더 |

---

## 실행 방법


1.  다음 명령어를 실행하여 Streamlit 애플리케이션을 시작.
    ```bash
    streamlit run frontend/app.py
    ```

    애플리케이션이 정상적으로 시작되면 웹 브라우저가 자동으로 열리거나, 터미널에 접속 가능한 URL(일반적으로 `http://localhost:8501`)이 표시.

    ```
    You can now view your Streamlit app in your browser.

    Local URL: http://localhost:8501
    Network URL: http://<your-local-ip>:8501
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

**asset** : 
style.css, mypolio.png가 프로젝트 구조 내에 있어야 정상 렌더링됨

**백엔드 연결** : 
백엔드 서버 (FastAPI)가 localhost:8000에서 실행 중이어야 함

## 기타
'고객 문의' 선택 시 외부 채널인 myfolio.channel.io로 유도됩니다

## 라이선스 표기

본 프로젝트는 시연 단계에서는 챗봇 인터페이스 하단에 라이선스 문구를 표기하였으며,
제안해 주신 대로, 실제 서비스 도입 시에는 마이폴리오의 푸터 영역에 아래 문구를 추가하는 방식으로 진행하시면 되겠습니다.

라이센스 표기 문구 :
© 2024 Smilegate AI. Korean UnSmile Dataset 및 baseline 모델은  
[GitHub 저장소](https://github.com/smilegate-ai/korean_unsmile_dataset)에서 Apache License 2.0 하에 공개되어 있습니다.