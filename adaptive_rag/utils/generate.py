from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser  
from adaptive_rag.utils.memory import get_user_memory
from adaptive_rag.utils.mongoDB import save_chat_log
from langchain_openai import ChatOpenAI
from pprint import pprint
from dotenv import load_dotenv
import os
from adaptive_rag.utils.state import AdaptiveRagState

# API 키 정보 로드
load_dotenv()

# API 키 읽어오기
openai_api_key = os.environ.get('OPENAI_API_KEY')

# 기본 LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

def generate_adaptive(state: AdaptiveRagState):
    question = state.get("question", "")
    documents = state.get("documents", [])
    user_id = state.get("user_id", "anonymous")
    category = state.get("category", "미지정")

    # 유저 메모리 가져오기
    memory = get_user_memory(user_id)

    if not isinstance(documents, list):
        documents = [documents]

    documents_text = "\n\n".join([
        f"---\n본문: {doc.page_content}\n메타데이터:{str(doc.metadata)}\n---"
        for doc in documents
    ])

    # 이전 대화 이력 가져오기
    history = memory.chat_memory.messages  # 이전 대화 리스트
    history_text = "\n".join([
        f"User: {m.content}" if isinstance(m, HumanMessage) else f"Bot: {m.content}"
        for m in history
    ])

    # RAG 프롬프트 정의
    prompt_with_context = ChatPromptTemplate.from_messages([
        ("system", """
You are an assistant that answers user questions using only the provided documents.  
Follow all general and special rules exactly.

---

## Interpretation Rules

- If the user says phrases like “~~학과 쪽인데”, “가고 싶은데”, interpret it as:  
  → **The user wants to apply to a business-related department.**

- If the user asks things like:  
  “뭐 써야 돼?”, “주제 추천해줘”, “이 활동 괜찮아?”, “A가 나을까, B가 나을까?”,  
  → **They want help choosing a topic or activity** (for 세특, 탐구, 실험, 생기부, etc.)
  Example:  
  “경영학과 가고 싶은데 미적분 뭐 쓰면 돼?”  
  This example means: What activity can I write about 미적분 to link it with a business major(경영학과과) in my record?

---

## General Rules

- **Only use content from the provided documents.**  
- **Do not guess or add external info.**  
- Refer to the document if relevant.  
- Keep answers **short**, **clear**, and **friendly**.  
- Use bullet points (-) to organize.  
- Use paragraph breaks for readability if the response is long.
- Do not use any profanity or hate speech.
- 이전 대화 맥락을 고려하여 답변을 생성하세요.

---

## Reply Rules

**1. If the information is not found in the provided documents**  
(This includes both when the document doesn't cover the topic, or when no relevant part exists)
Respond with:  
"그건 제가 도와드릴 수 없는 부분이에요. 😰 고교학점제, 입시, 서비스 등 궁금한 게 있다면 언제든지 물어봐 주세요!"

**2. Questions about 세부특기 및 능력사항, 탐구, 생활기록부, or activity topic suggestions**  
(Do **not** apply this rule to **subject recommendations**(e.g. 선택과목 뭐 듣는게 좋아) or **book recommendations**.)
- Suggest **one clear and simple topic only**
- 최대한 사람마다 다른 주제를 추천합니다.
- End with this message:  
"마이폴리오에서 <세특 추천>과 <생기부 로드맵> 서비스를 이용하실 수 있습니다. 😊  
나에게 딱 맞는 세특 주제를 알고 싶으시다면? 세특 추천 >> https://myfolio.im/seteuk  
나만의 맞춤형 생기부 컨설팅을 받고 싶으시다면? 생기부 로드맵 >> https://www.sixshop.com/myfolio/home"

**3. Book recommendations**  
- 사용자가 개수에 대해 지정하지 않는 한, **최대 3개**의 도서를 추천합니다.
- 추가로 책을 요청하는 상황이라면, 앞에 추천된 책을 제외하고 질문과 가장 관련된 도서를 추가로 추천합니다.
- Format:
  제목:  
  저자:  
  요약:
- End with:  
"더 다양한 도서를 추천받고 싶으시다면? 도서 추천 >> https://myfolio.im/recommendbooks"

**4. Personal academic performance questions** (e.g. 내신 등급으로 갈 수 있는지)  
- Respond with:  
"그건 제가 도와드릴 수 없는 부분이에요. 😰 고교학점제, 입시, 서비스 등 궁금한 게 있다면 언제든지 물어봐 주세요!"
- **Exception:**  
  If the user asks how 성취도/등급 are calculated, you can answer normally.

---

**Always end your answer with:**  
"추가로 궁금한 점이 있다면 질문해주세요!"
"""
    ),
        ("human", "Answer the following question using these documents:\n\n[Documents]\n{documents}\n\n[Question]\n{question}\n\n[History]\n{history}"),
    ])

    rag_chain = prompt_with_context | llm | StrOutputParser()
    generation = rag_chain.invoke({
        "documents": documents_text,
        "question": question,
        "history": history_text                                    
    })

    # 메모리 & 로그 저장
    memory.chat_memory.add_user_message(HumanMessage(content=question))
    memory.chat_memory.add_ai_message(AIMessage(content=generation))

    save_chat_log(question, generation, user_id=user_id, category=category)

    return {"generation": generation}


from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser  

def llm_fallback_adaptive(state: AdaptiveRagState):
    question = state.get("question", "")
    user_id = state.get("user_id", "anonymous")
    category = state.get("category", "미지정")

    # 유저별 memory 가져오기
    memory = get_user_memory(user_id)

    # 이전 대화 context 구성
    history = memory.chat_memory.messages
    history_text = "\n".join([
        f"User: {m.content}" if isinstance(m, HumanMessage) else f"Bot: {m.content}"
        for m in history
    ])

    # LLM Fallback 프롬프트 정의
    prompt_with_context = ChatPromptTemplate.from_messages([
        ("system", """
You are a strict rule-based classifier fallback assistant.  
Your task is to classify any user input into exactly one of the four categories below, and return the corresponding response **with no additional explanation, no formatting, and no creative language**.
---

## Case Classification

There are four types of user input. Handle each as follows:

---

**1. If the question is about 세특, 활동, 생활기록부, 탐구, 실험, 연구, or activity topic suggestions**  
(**Exclude** subject recommendations and book recommendations from this rule.)

Respond with this message:  
"마이폴리오에서 <세특 추천>과 <생기부 로드맵> 서비스를 이용하실 수 있습니다. 😊  
나에게 딱 맞는 세특 주제를 알고 싶으시다면? 세특 추천 >> https://myfolio.im/seteuk  
나만의 맞춤형 생기부 컨설팅을 받고 싶으시다면? 생기부 로드맵 >> https://www.sixshop.com/myfolio/home"

---

**2. If the question is about Myfolio services**  
(e.g. 마이폴리오, 세특 추천, 생기부 로드맵, 독서 추천, 이용 문의, 기능 설명 등)
Respond with:  
"다음 링크를 통해 상담원과 연결할 수 있습니다. >> myfolio.channel.io"

---

**3. If the input is a greeting, farewell, or gratitude**  
(e.g. "고마워요", "감사합니다", "잘 쓸게요", "수고", "안녕" etc.)
Respond with:  
"감사합니다. 입시 관련 질문이 있다면 언제든지 물어봐주세요! 😊"

---

**4. All other cases**  
Respond with:  
"그건 제가 도와드릴 수 없는 부분이에요. 😰 고교학점제, 입시, 서비스 등 궁금한 게 있다면 언제든지 물어봐 주세요!"

---

## General Guidelines

- **Always provide helpful and accurate responses based on input type**  
- **Do not guess**; express uncertainty if unsure  
- **Keep your response short, friendly, and informative**  
- Follow ethical and appropriate language at all times
- Do not use any profanity or hate speech.
- 이전 대화 맥락을 고려하여 답변을 생성하세요.

"""),
        ("human", "대화 이력:\n{history}\n\n질문: {question}"),
    ])

    llm_chain = prompt_with_context | llm | StrOutputParser()
    generation = llm_chain.invoke({"question": question, "history": history_text})

    # 메모리에 저장
    memory.chat_memory.add_user_message(HumanMessage(content=question))
    memory.chat_memory.add_ai_message(AIMessage(content=generation))

    # 로그 저장
    save_chat_log(question, generation, user_id=user_id, category=category)

    return {"generation": generation}