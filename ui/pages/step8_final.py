import streamlit as st
from models.state import ResumeState

def render_step8():
    st.header("8단계: 최종 결과 (Final Result)")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # 7단계 완료 체크
    if "confirmed_essays" not in state or not state["confirmed_essays"]:
        st.error("⚠️ 최종 결과가 없습니다. 7단계를 먼저 완료해주세요.")
        if st.button("👈 7단계로 이동"):
            state["current_step"] = 7
            st.rerun()
        return

    st.success("🎉 모든 과정이 완료되었습니다! 아래에서 전체 내용을 확인하고 복사하세요.")

    # 1. 입력 정보 (토글 숨김)
    with st.expander("1. 입력 정보 (Input Data)", expanded=False):
        st.caption("사용자가 초기에 입력한 기본 정보입니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("기업명", value=state.get("company_name", ""), disabled=True)
        with col2:
            st.text_input("직무명", value=state.get("position_name", ""), disabled=True)
            
        st.markdown("**채용 공고**")
        st.text_area("채용 공고 내용", value=state.get("job_posting", ""), height=200, disabled=True)
        
        st.markdown("**사용자 경험/경력**")
        st.text_area("경험/경력 내용", value=state.get("user_experiences", ""), height=200, disabled=True)

    # 2. 리서치 결과 (토글 숨김)
    with st.expander("2. 기업 리서치 결과 (Research)", expanded=False):
        research = state.get("company_research")
        content = ""
        if research:
            if hasattr(research, "content"):
                content = research.content
            elif isinstance(research, dict):
                content = research.get("content", "")
        
        st.text_area("리서치 내용", value=content, height=300, disabled=True)

    # 3. 작성 전략 (토글 숨김)
    with st.expander("3. 작성 전략 (Strategy)", expanded=False):
        strategy = state.get("writing_strategy")
        content = ""
        if strategy:
            if hasattr(strategy, "content"):
                content = strategy.content
            elif isinstance(strategy, dict):
                content = strategy.get("content", "")
        
        st.markdown(content) # 전략은 마크다운으로 보는게 가독성이 좋음
        # 원본 텍스트 복사용
        with st.popover("전략 텍스트 복사하기"):
            st.code(content, language=None)

    # 4. 작성 가이드 (토글 숨김)
    with st.expander("4. 작성 가이드 (Guidelines)", expanded=False):
        guidelines = state.get("writing_guidelines", "")
        st.text_area("가이드라인", value=guidelines, height=200, disabled=True)

    # 5. 최종 자기소개서 (기본 열림)
    with st.expander("5. 최종 자기소개서 (Final Essays)", expanded=True):
        st.info("우측 상단의 복사 버튼을 클릭하여 내용을 복사할 수 있습니다.")
        
        final_essays = state.get("confirmed_essays", {})
        questions = state.get("essay_questions", [])
        
        for i, q in enumerate(questions):
            q_idx = str(i + 1)
            q_text = q.get("question_text", f"문항 {q_idx}")
            content = final_essays.get(q_idx, "내용 없음")
            
            st.markdown(f"#### Q{q_idx}. {q_text}")
            st.code(content, language=None) # 복사하기 편하도록 code 블록 사용
            st.markdown("---")

    # 홈으로 돌아가기 또는 초기화
    if st.button("🔄 처음부터 다시 하기 (데이터 초기화)"):
        st.session_state.clear()
        st.rerun()
