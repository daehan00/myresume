import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from chains.strategy_chain import (
    create_initial_strategy_chain, 
    create_feedback_strategy_chain,
    create_strategy_extraction_chain,
    get_provider_for_model
)
from tools.llm_util import (
    MODEL_PROVIDER_MAP,
    MODEL_DISPLAY_NAMES
)


@st.dialog("⚠️ 전략 저장 확인")
def show_overwrite_dialog(last_ai_message, state):
    st.write("이미 저장된 전략이 있습니다.")
    st.write("현재 대화 내용으로 **덮어쓰시겠습니까**, 아니면 기존 전략을 **유지하시겠습니까**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("기존 유지 (다음 단계로)", use_container_width=True):
            state["current_step"] = 5
            st.rerun()
            
    with col2:
        if st.button("덮어쓰고 저장", type="primary", use_container_width=True):
            _save_strategy(last_ai_message, state)

def _save_strategy(content, state):
    """전략 추출 및 저장 로직"""
    with st.spinner("💾 전략을 시스템에 저장하고 다음 단계로 이동 중입니다..."):
        try:
            extraction_chain = create_strategy_extraction_chain()
            structured_strategy = extraction_chain.invoke({"content": content})
            
            # 텍스트 원본도 포함
            structured_strategy.content = content
            
            # State 저장
            state["writing_strategy"] = structured_strategy
            state["current_step"] = 5

            # 4단계 완료 처리
            if "completed_steps" not in state:
                state["completed_steps"] = []

            if 4 not in state["completed_steps"]:
                state["completed_steps"].append(4)
            
            st.rerun()
        except Exception as e:
            
            
            st.error(f"❌ 데이터 저장 중 오류가 발생했습니다: {e}")

def render_step4():
    st.header("4단계: 지원서 작성 전략 수립")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # 선행 단계 데이터 검증
    # company_research가 Pydantic 모델인지 dict인지 확인하여 content 추출
    research_obj = state.get("company_research")
    research_content = None
    if research_obj:
        if hasattr(research_obj, "content"):
            research_content = research_obj.content
        elif isinstance(research_obj, dict):
            research_content = research_obj.get("content")
            
    has_research = bool(research_content)
    has_posting = state.get("job_posting")
    
    if not has_research or not has_posting:
        st.error("⛔️ 필수 데이터가 누락되었습니다.")
        st.warning("이전 단계(리서치 및 채용공고 입력)를 먼저 완료해주세요.")
        
        if st.button("👈 3단계(리서치)로 돌아가기"):
            state["current_step"] = 3
            st.rerun()
        return

    # 세션 상태에 채팅 기록 초기화
    if "strategy_messages" not in st.session_state:
        st.session_state.strategy_messages = []
        st.session_state.strategy_initial_generated = False
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        # 채팅 기록 표시
        for msg in st.session_state.strategy_messages:
            if isinstance(msg, AIMessage):
                with st.chat_message("ai"):
                    st.markdown(msg.content)
            elif isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(msg.content)

    # 초기 전략 생성 (기록이 없을 때만)
    # 조건: 
    # 1. 초기 생성이 아직 안 되었음 (strategy_initial_generated is False)
    # 2. 메시지 기록이 비어있음 (len == 0) - 재진입 시 중복 실행 방지
    if not st.session_state.strategy_initial_generated and len(st.session_state.strategy_messages) == 0:
        with chat_container:
            with st.chat_message("ai"):
                # 현재 선택된 모델 가져오기 (기본값 또는 세션값)
                current_index = st.session_state.get("strategy_model_index", 0)
                model_keys = list(MODEL_PROVIDER_MAP.keys())
                current_model = model_keys[current_index]

                with st.spinner(f"🤖 AI가 채용공고와 리서치 결과를 분석하여 전략을 수립 중입니다... ({MODEL_DISPLAY_NAMES.get(current_model, current_model)})"):
                    try:
                        chain = create_initial_strategy_chain(model=current_model)
                        
                        # 리서치 콘텐츠 안전하게 추출
                        c_research = state.get("company_research")
                        c_content = "리서치 정보 없음"
                        if c_research:
                            if hasattr(c_research, "content"):
                                c_content = c_research.content
                            elif isinstance(c_research, dict):
                                c_content = c_research.get("content", "리서치 정보 없음")

                        input_data = {
                            "company_name": state["company_name"],
                            "position_name": state["position_name"],
                            "job_posting": state["job_posting"],
                            "company_research": c_content,
                            "essay_questions": "\n".join([f"{i+1}. {q['question_text']}" for i, q in enumerate(state["essay_questions"])]),
                            "user_experiences": state["user_experiences"]
                        }
                        
                        result = chain.invoke(input_data)
                        ai_content = result.content
                        
                        # 화면에 즉시 표시 및 상태 저장
                        st.markdown(ai_content)
                        st.session_state.strategy_messages.append(AIMessage(content=ai_content))
                        st.session_state.strategy_initial_generated = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {e}")
                        return
    
    st.markdown("---")
    
    # 하단 컨트롤 바 (입력창 바로 위)
    # 구성: [모델설정(팝오버)] [이전 버튼] [다음 버튼]
    ctl_col1, ctl_col2, ctl_col3 = st.columns([1, 1, 3])
    
    with ctl_col1:
        # 모델 설정 팝오버
        with st.popover("⚙️ 모델 설정", use_container_width=True):
            model_keys = list(MODEL_PROVIDER_MAP.keys())
            model_labels = [MODEL_DISPLAY_NAMES.get(k, k) for k in model_keys]
            
            selected_index = st.selectbox(
                "사용할 AI 모델",
                options=range(len(model_keys)),
                format_func=lambda i: model_labels[i],
                index=st.session_state.get("strategy_model_index", 0),
                key="strategy_model_index",
                help="더 강력한 모델일수록 응답 품질이 높지만 속도가 느릴 수 있습니다."
            )
            
            selected_model = model_keys[selected_index]
            selected_provider = get_provider_for_model(selected_model)
            st.caption(f"Provider: {selected_provider}")

    with ctl_col2:
        if st.button("👈 이전", use_container_width=True):
            state["current_step"] = 3
            st.rerun()

    with ctl_col3:
        if st.button("✅ 전략 확정 및 다음 👉", type="primary", use_container_width=True):
            # 가장 최근 AI 메시지를 가져옴
            last_ai_message = None
            for msg in reversed(st.session_state.strategy_messages):
                if isinstance(msg, AIMessage):
                    last_ai_message = msg.content
                    break
            
            if not last_ai_message:
                st.error("❌ 저장할 전략을 찾을 수 없습니다.")
            else:
                # 이미 저장된 전략이 있는지 확인
                if state.get("writing_strategy"):
                    show_overwrite_dialog(last_ai_message, state)
                else:
                    _save_strategy(last_ai_message, state)

    # 사용자 입력 (피드백) - 화면 최하단
    user_input = st.chat_input("💬 전략에 대한 피드백이나 수정 요청을 입력하세요...")
    
    if user_input:
        # 1. 사용자 메시지 즉시 표시 및 저장
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        st.session_state.strategy_messages.append(HumanMessage(content=user_input))
        
        # 2. AI 응답 생성 및 표시
        with chat_container:
            with st.chat_message("ai"):
                # 현재 선택된 모델 가져오기
                current_index = st.session_state.get("strategy_model_index", 0)
                model_keys = list(MODEL_PROVIDER_MAP.keys())
                current_model = model_keys[current_index]
                
                with st.spinner(f"🤖 피드백을 반영하여 전략을 수정하고 있습니다... ({MODEL_DISPLAY_NAMES.get(current_model, current_model)})"):
                    try:
                        feedback_chain = create_feedback_strategy_chain(model=current_model)
                        
                        # 채팅 히스토리 변환 (마지막 사용자 메시지 제외)
                        chat_history = st.session_state.strategy_messages[:-1]
                        
                        result = feedback_chain.invoke({
                            "chat_history": chat_history,
                            "user_input": user_input
                        })
                        
                        ai_content = result.content
                        st.markdown(ai_content)
                        st.session_state.strategy_messages.append(AIMessage(content=ai_content))
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {e}")