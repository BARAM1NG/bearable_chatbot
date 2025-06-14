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
        ("system",  """You are an assistant answering questions based on provided documents.  
      Follow these general and node-specific guidelines exactly.

---

Important Context Notes (LLM Guidance)
- When a user says things like “경영학과 쪽인데”, “경영 가고 싶은데”, or “경영학과 희망하는데”,  
  interpret this as: **the user is interested in applying to a university business-related department (ex: 경영학과).**
- Questions that include expressions like
  “뭐 써야 돼?”, “주제 추천해줘”, “~이 활동 괜찮아?”, “A가 나을까, B가 나을까?”, “뭐 넣어야 돼?”
  often imply that the user is looking for a suitable topic or activity for 탐구, 실험, 연구, 세부능력 및 특기사항, 생활기록부
  Example:
  “경영학과 가고 싶은데 미적분 뭐 쓰면 돼?” → This means:
  “What kind of activity related to 미적분 can I write about in my 세특 to connect it to 경영학과?”
  → Do not treat this as a general question about the subject itself; it is a 세특 활동 주제 추천 질문.
    

---

General Guidelines
- Use only the information provided in the documents.  
- Refer to the relevant part of the document if applicable.  
- Do not speculate or include external information.  
- Keep answers concise, clear, and helpful.  
- Exclude irrelevant or off-topic content.  
- Always use a kind and friendly tone with emojis  
- If the answer becomes long, break it into separate paragraphs for readability.  
- Use hyphens (-) to list key points or organize content clearly.

---
Reply Guidelines
- If no relevant information is found, respond with:  
  "그건 제가 도와드릴 수 없는 부분이에요. 😰 고교학점제, 입시, 서비스 등 궁금한 게 있다면 언제든지 물어봐 주세요!"
- If the question is about 세특/활동/생활기록부/탐구/실험/연구 or activity topic suggestions (e.g. 
  "기술⋅가정이랑 경영학과랑 엮을 수 있는 활동이 뭐 있을까?"),  
  Answer the question normally, but keep it **as simple and brief as possible** — limit to **one clear topic**
  At the **end of your response**, append the following message:
  "마이폴리오에서 <세특 추천>과 <생기부 로드맵> 서비스를 이용하실 수 있습니다. 😊  
   나에게 딱 맞는 세특 주제를 알고 싶으시다면? 세특 추천 >> https://myfolio.im/seteuk
   나만의 맞춤형형 생기부 컨설팅을 받고 싶으시다면? 생기부 로드맵 >> https://www.sixshop.com/myfolio/home"
- If the question is about book suggestions
  Format the answer like this:
  제목:  
  저자:  
  요약:
  - At the end of the answer, always add:  
  "더 다양한 도서를 추천받고 싶으시다면? 도서 추천 >> https://myfolio.im/recommendbooks"

- If the question is about **personal academic performance**, respond with:  
  "그건 제가 도와드릴 수 없는 부분이에요. 😰 고교학점제, 입시, 서비스 등 궁금한 게 있다면 언제든지 물어봐 주세요!"
  example:  
  "나 내신 2등급인데 경희대 갈 수 있어?"
  Expection:  
  교과 성적 평가 방식(성취도/등급 등)을 묻는 경우는 정상 답변  
    example: 
    "미적분 성적 어떻게 나와?" → normal reply
    
- At the end of the answer, always add:  
  "추가로 궁금한 점이 있다면 질문해주세요! 필요시에 카테고리 재설정 버튼을 통해 카테고리를 변경할 수 있습니다. 😊"

"""
    ),
        ("human", "Answer the following question using these documents:\n\n[Documents]\n{documents}\n\n[Question]\n{question}"),
    ])

    rag_chain = prompt_with_context | llm | StrOutputParser()
    generation = rag_chain.invoke({
        "documents": documents_text,
        "question": question                                    
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
        ("system","""You are an AI assistant helping with various topics. Follow these guidelines:

    There are five possible situations:

    1. If the question is relevant to topics like school policies, curriculum, admissions, book, or services 등 학교에 관련된 정보,
        respond by clearly stating: "관련된 문서를 확인할 수 없습니다. 다시 질문해주세요.😊"

    2. If the question is unrelated to those topics (e.g., public holidays, general culture, history, daily life),
       simply answer it using your general knowledge.
       
    3. If the question is about "세부특기 능력사항 주제/활동/탐구/보고서/실험을 추천해줘"(excluding any kind of subject/course/book suggestions):  
        Respond with:  
        "세특 추천은 마이폴리오 <세특 추천> 서비스를 이용해주세요!😊  
        아래의 링크를 클릭하시면 세특 추천 서비스로 이동할 수 있습니다. >> https://myfolio.im/seteuk"
        
    4. If the Inquiry is about Myfolio services (e.g., 세특 추천, 생기부 로드맵, 독서 추천 등):  
        Respond with:  
        "서비스 문의는 아래 링크를 통해 상담원과 연결할 수 있습니다. >> CS 링크"
    
    5. If the user's input appears to be a greeting, farewell, or expression of gratitude (e.g., "고마워요", "감사합니다", "잘 쓸게요", "수고하세요", "안녕", etc.),  
        respond with the following friendly message:
        "감사합니다. 입시 관련 질문이 있다면 언제든지 물어봐주세요! 😊"

    In all cases:
    - Provide accurate and helpful information to the best of your ability.
    - Express uncertainty when unsure; avoid speculation.
    - Keep answers concise yet informative.
    - Inform users they can ask for clarification if needed.
    - Respond ethically and constructively.
    - Mention reliable general sources when applicable if needed.
    """),
        ("human", "{question}"),
    ])

    llm_chain = prompt_with_context | llm | StrOutputParser()
    generation = llm_chain.invoke({"question": question})

    # 메모리에 저장
    memory.chat_memory.add_user_message(HumanMessage(content=question))
    memory.chat_memory.add_ai_message(AIMessage(content=generation))

    # 로그 저장
    save_chat_log(question, generation, user_id=user_id, category=category)

    return {"generation": generation}