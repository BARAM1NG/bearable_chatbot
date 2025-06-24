import streamlit as st
import requests
import uuid
import os
import time

# 이 파일(app.py) 위치 기준
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 페이지 설정
st.set_page_config(
    page_title="마이폴리오 챗봇",
    page_icon=os.path.join(BASE_DIR, "asset", "mypolio.png"),
    layout="centered",
)

# CSS 로드
def load_css(file_name: str):
    css_path = os.path.join(BASE_DIR, file_name)
    if not os.path.isfile(css_path):
        raise FileNotFoundError(f"CSS 파일을 찾을 수 없습니다: {css_path}")
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- 세션 상태 초기화 및 타임아웃 설정 ---
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()
if 'timeout_message_shown' not in st.session_state:
    st.session_state.timeout_message_shown = False

if time.time() - st.session_state.last_activity > 300 and not st.session_state.timeout_message_shown:
    st.session_state.messages = []
    st.session_state.stage = "initial"
    st.session_state.category = None
    st.session_state.show_reset = False

    st.session_state.messages.append({
        "role": "assistant",
        "content": "💬 5분 동안 활동이 없어 챗봇 세션이 자동으로 종료되었습니다. 추가 문의가 있으시면 새 질문을 입력해주세요."
    })
    st.session_state.timeout_message_shown = True
    st.rerun()

# ── 로고와 초기 안내 영역 ──
logo_path = os.path.join(BASE_DIR, "asset", "mypolio.png")

#         #   <h2 style="font-size:18px; margin:0 0 0.5rem;">마이폴리오 AI 챗봇입니다</h2>
try:
    col1, col2, col3 = st.columns([1.7, 1, 1.5])
    with col2:
        st.image(logo_path, width=100)

    st.markdown(
        """
        <div style="text-align:center; margin:2rem 0;">
          <h1 style="font-size:24px; font-weight:bold; margin:1rem 0 0.5rem;">안녕하세요! 마이폴리오 챗봇입니다!</h1>
          <p><strong>문의 유형 안내</strong></p>
          <ul style="text-align:left; display:inline-block; line-height:1.6;">
            <li><strong>운영 문의</strong>: 제도, 졸업 요건, 교과 이수 기준 등</li>
            <li><strong>과목 선택</strong>: 과목 소개, 계열/진로별 추천 과목 정보 등</li>
            <li><strong>입시 정보</strong>: 입시 전형 개념, 대학/학과 소개 정보 등</li>
            <li><strong>도서 추천</strong>: 진로 맞춤 책 소개</li>
            <li><strong>고객 문의</strong>: 챗봇 사용법, 시스템 오류 등</li>
          </ul>
          <p style="margin-top:1.5rem; font-size:13px; color:#888;">
            ※ 챗봇의 답변은 참고용이며, 정확한 정보는 교육청 공식 채널에서 확인해 주세요.
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.warning("로고 이미지를 찾을 수 없습니다.")

# 하단 우측 고정 라이선스 및 출처 표시
st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 0.5rem;
        right: 1rem;
        color: #888888;
        font-size: 0.6rem;
        text-align: right;
        line-height: 1.2;
        z-index: 999;
    ">
        본 챗봇은 경희대학교x베어러블 산학협력 프로젝트로 제작되었습니다.  
        일부 데이터 및 모델은  
        <a href="https://github.com/smilegate-ai/korean_unsmile_dataset" target="_blank" style="color: #888888; text-decoration: underline;">
        Smilegate AI의 공개 GitHub 저장소</a>의 자료를 활용했으며,  
        Apache License 2.0 하에 사용됩니다.
    </div>
    """,
    unsafe_allow_html=True
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "stage" not in st.session_state:
    st.session_state.stage = "initial"
if "category" not in st.session_state:
    st.session_state.category = None
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

# ← 여기에 추가
if "pending" not in st.session_state:
    st.session_state.pending = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""

# 카테고리 목록
categories = ["운영 문의", "과목 선택", "입시 연계", "도서 추천", "고객 문의"]

def handle_category_selection(category_name):
    st.session_state.category = category_name
    st.session_state.show_reset = False
    st.session_state.timeout_message_shown = False
    st.session_state.last_activity = time.time()
    if category_name == "고객 문의":
        st.session_state.messages.append({"role": "user", "content": category_name})
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"'{category_name}' 관련 문의는 [myfolio.channel.io](https://myfolio.channel.io)를 이용해주세요."
        })
        st.markdown(
            '<a href="https://myfolio.channel.io" target="_blank"> myfolio.channel.io로 이동하기</a>',
            unsafe_allow_html=True
        )
        st.session_state.stage = "initial"
    else:
        st.session_state.stage = "chatting"
        st.session_state.messages.append({"role": "user", "content": category_name})
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"'{category_name}'에 대해 궁금한 점을 입력해주세요."
        })
    st.rerun()

# 초기 화면: 카테고리 선택
if st.session_state.stage == "initial":
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "안녕하세요! 당신을 위한 입시 도우미, 마폴이 입니다.\n"
                "아래 카테고리를 선택하고 질문을 입력해주세요😊\n"
                "희망하는 진로와 학년을 함께 물어보면 더 정확한 정보를 드릴 수 있어요!"
            )
        })
    for msg in st.session_state.messages:
        avatar = logo_path if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        if cols[i].button(cat, key=f"cat_{i}", use_container_width=True):
            handle_category_selection(cat)
    st.stop()

# 채팅 화면
if st.session_state.stage == "chatting":
    # 대화 이력 렌더링
    for msg in st.session_state.messages:
        avatar = logo_path if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("documents"):
                with st.expander("참고 문서 보기", expanded=False):
                    for doc in msg["documents"]:
                        source = doc.get("metadata", {}).get("source", "N/A")
                        st.markdown(f"**출처:** {source}")
                        st.caption(doc.get("page_content", ""))
                        st.divider()
    # 사용자 입력 및 즉시 표시
    prompt = st.chat_input("마이폴리오 AI에게 무엇이든 물어보세요!")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending = True
        st.session_state.pending_prompt = prompt
        st.session_state.last_activity = time.time()
        st.rerun()

    # pending일 때 답변 생성
    if st.session_state.get("pending", False):
        with st.spinner("답변을 생성하는 중입니다. 잠시만 기다려주세요…"):
            try:
                payload = {
                    "question": st.session_state.pending_prompt,
                    "user_id": st.session_state.user_id,
                    "category": st.session_state.category
                }
                res = requests.post("http://localhost:8000/chat/", json=payload)
                res.raise_for_status()
                data = res.json()
                assistant_msg = {"role": "assistant", "content": data.get("answer", "")}  
                if docs := data.get("documents"):
                    assistant_msg["documents"] = docs
                st.session_state.messages.append(assistant_msg)
                st.session_state.show_reset = True
            except Exception as e:
                st.error(f"오류 발생: {e}")
            finally:
                st.session_state.pending = False
        st.rerun()

    # Q&A 완료 후 재선택 버튼
    if st.session_state.show_reset:
        if st.button("🔄 카테고리 재선택"):
            st.session_state.stage = "initial"
            st.session_state.show_reset = False
            st.rerun()