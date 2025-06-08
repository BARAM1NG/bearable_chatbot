from adaptive_rag.utils import tools, safeguard, search, generate, memory, mongoDB, router, slang, state
from adaptive_rag.utils.state import AdaptiveRagState

from typing import TypedDict, List
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from functools import partial

import random
import threading
import sys
from typing import Dict, Any

# 툴 설정 함수
def set_tools():
    """
    Set up the tools for the Adaptive RAG pipeline.
    """
    tools_list = [
        tools.search_policy,
        tools.search_admission,
        tools.search_book,
        tools.search_service,
        tools.search_subject
    ]
    
    return tools_list

# 툴 설정
tools = set_tools()

# AdaptiveRAG 파이프라인 빌드 함수
def build_adaptive_rag() -> StateGraph:
    """StateGraph를 빌드하고 컴파일한 adaptive_rag 객체를 반환."""
    builder = StateGraph(AdaptiveRagState)
    builder.set_entry_point("profanity_prevention")

    builder.add_node("profanity_prevention", partial(safeguard.profanity_prevention))
    builder.add_node("route_question_adaptive", router.route_question_adaptive)

    builder.add_node("search_policy", search.search_policy_adaptive)
    builder.add_node("search_subject", search.search_subject_adaptive)
    builder.add_node("search_admission", search.search_admission_adaptive)
    builder.add_node("search_book", search.search_book_adaptive)
    builder.add_node("search_service", search.search_service_adaptive)

    builder.add_node("generate", generate.generate_adaptive)
    builder.add_node("llm_fallback", generate.llm_fallback_adaptive)

    builder.add_conditional_edges(
        "profanity_prevention",
        safeguard.check_profanity_result,
        {"__end__": "__end__", "route_question_adaptive": "route_question_adaptive"}
    )

    builder.add_conditional_edges(
        "route_question_adaptive",
        lambda state: state["next_node"],
        {
            "search_policy": "search_policy",
            "search_subject": "search_subject",
            "search_admission": "search_admission",
            "search_book": "search_book",
            "search_service": "search_service",
            "llm_fallback": "llm_fallback",
        }
    )

    for node in ["search_policy","search_subject","search_admission","search_book","search_service"]:
        builder.add_edge(node, "generate")
    builder.add_edge("llm_fallback", "__end__")
    builder.add_edge("generate", "__end__")

    return builder.compile()

def run_chatbot():
    """
    챗봇 실행 (5분 무응답 시 자동 종료)
    """
    graph = build_adaptive_rag()
    user_id = random.randint(1, 1_000_000)

    def timeout_exit():
        print("\n5분 동안 입력이 없어 챗봇을 종료합니다.")
        sys.exit(0)

    # 최초 타이머 설정
    timer = threading.Timer(300, timeout_exit)
    timer.start()

    try:
        while True:
            question = input("질문을 입력해주세요 > ").strip()
            # 입력이 들어오면 기존 타이머 취소 후 재시작
            timer.cancel()
            if not question:
                print("종료합니다.")
                break

            inputs = {
                "question": question,
                "user_id": user_id
            }

            for output in graph.stream(inputs):
                for key, value in output.items():
                    final_output = value

            print(f"🤖 답변: {final_output['generation']}")

            # 다시 5분 타이머 시작
            timer = threading.Timer(300, timeout_exit)
            timer.start()

    finally:
        # 프로그램 종료 전 타이머는 반드시 취소
        timer.cancel()

# 챗봇 실행
if __name__ == "__main__":
    run_chatbot()
