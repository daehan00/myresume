import streamlit as st

from chains.guideline_chain import (
    DEFAULT_GUIDELINE_TEXT,
    ai_validate_guidelines
)

def render_step5():
    st.header("5단계: 작성 요령 가이드 확인")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # 가이드라인 초기화 (없을 경우 기본값 설정)
    if "writing_guidelines" not in state or not state["writing_guidelines"]:
        state["writing_guidelines"] = DEFAULT_GUIDELINE_TEXT

    st.info("💡 최종 초안을 작성할 때 적용될 **공통 작성 가이드**입니다. 내용을 확인하시고 필요 시 수정해 주세요.")

    # 1. 가이드라인 편집 영역
    st.markdown("### 📝 공통 가이드라인 편집")
    
    # 폼을 사용하여 입력값 관리
    with st.form(key="guidelines_edit_form"):
        edited_guidelines = st.text_area(
            "자기소개서 작성 규칙",
            value=state["writing_guidelines"],
            height=350,
            help="이 가이드는 모든 문항의 초안 작성 시 AI에게 전달됩니다."
        )
        
        col_submit_1, col_submit_2 = st.columns([3, 1])
        with col_submit_2:
            update_submitted = st.form_submit_button("🛠️ 수정사항 반영 (AI 검수)", use_container_width=True)

    # 폼 제출 처리 (수정사항이 있을 때만)
    if update_submitted:
        if edited_guidelines and edited_guidelines != state["writing_guidelines"]:
            with st.spinner("🤖 AI가 수정된 가이드를 검토하고 업데이트 중입니다..."):
                updated_text = ai_validate_guidelines(edited_guidelines)
                state["writing_guidelines"] = updated_text
                st.success("✅ 가이드라인이 업데이트되었습니다!")
                st.rerun()
        else:
            st.info("변경된 내용이 없습니다.")

    # 2. 하단 네비게이션
    st.markdown("---")
    nav_col1, nav_col2 = st.columns([1, 3])
    
    with nav_col1:
        if st.button("👈 이전 단계"):
            state["current_step"] = 4
            st.rerun()
            
    with nav_col2:
        if st.button("✅ 가이드 확정 및 초안 작성 (다음) 👉", type="primary", use_container_width=True):
            # 최종 확정된 내용을 상태에 저장 (이미 폼 제출 시 저장되지만 확신을 위해)
            state["writing_guidelines"] = edited_guidelines
            state["current_step"] = 6
            if 5 not in state["completed_steps"]:
                state["completed_steps"].append(5)
            st.rerun()
