"""AI 챗봇 화면 구현."""

from __future__ import annotations
import streamlit as st

from src.chatbot.engine import build_context_message, chat, get_client

EXAMPLE_QUESTIONS = [
    "Ni 회수율 90% 이상을 달성하면서 탄소 배출을 최소화하는 조건은?",
    "온도를 60°C에서 80°C로 올리면 탄소 배출이 얼마나 늘어나?",
    "H₂O₂를 줄이면 회수율에 어떤 영향이 있어?",
    "현재 조건에서 탄소 배출을 20% 줄이려면 어떻게 해야 해?",
    "반응 시간 120분과 240분의 차이는?",
]


def render_chatbot(
    api_key: str,
    condition: dict[str, float] | None = None,
    last_result: dict | None = None,
) -> None:
    """AI 챗봇 화면 렌더링."""
    st.header("🤖 AI 공정 어시스턴트")
    st.caption("침출 공정 최적화, 탄소 감축 전략, 조건 추천 등 무엇이든 물어보세요.")

    # 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "gemini_client" not in st.session_state:
        try:
            st.session_state.gemini_client = get_client(api_key)
        except Exception as e:
            st.error(f"❌ AI 초기화 실패: {e}")
            return

    # 현재 조건 컨텍스트 표시
    if condition:
        with st.expander("📋 현재 시뮬레이터 조건 (챗봇이 참고 중)", expanded=False):
            ctx = build_context_message(condition, last_result)
            st.code(ctx, language=None)

    # 예시 질문 버튼
    st.markdown("**💡 예시 질문**")
    cols = st.columns(2)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"example_{i}", use_container_width=True):
                st.session_state.pending_question = q

    st.divider()

    # 대화 히스토리 표시
    for msg in st.session_state.chat_history:
        avatar = "🧑‍🔬" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 예시 질문 자동 입력 처리
    pending = st.session_state.pop("pending_question", None)
    user_input = st.chat_input("공정 조건, 탄소 감축, 최적화 전략 등 질문하세요...")
    query = pending or user_input

    if query:
        # 컨텍스트 포함 메시지 구성
        context = build_context_message(condition, last_result)
        full_message = f"{context}\n\n사용자 질문: {query}" if context else query

        # 사용자 메시지 표시
        with st.chat_message("user", avatar="🧑‍🔬"):
            st.markdown(query)
        st.session_state.chat_history.append({"role": "user", "content": query})

        # Gemini 응답
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("분석 중..."):
                try:
                    answer = chat(
                        st.session_state.gemini_client,
                        st.session_state.chat_history[:-1],  # 방금 추가한 것 제외
                        full_message,
                    )
                except Exception as e:
                    answer = f"❌ 응답 오류: {e}"
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # 대화 초기화
    if st.session_state.chat_history:
        if st.button("🗑️ 대화 초기화", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
