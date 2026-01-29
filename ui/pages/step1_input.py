import streamlit as st
from ui.components.input_forms import (
    render_job_details_form,
    render_essay_questions_form,
    render_experience_form
)

def render_step1():
    st.header("1단계: 기본 정보 입력")
    st.markdown("---")
    
    # 1. 채용 정보
    render_job_details_form()
    st.markdown("---")
    
    # 2. 자기소개서 문항
    render_essay_questions_form()
    st.markdown("---")
    
    # 3. 경험/경력
    render_experience_form()
    st.markdown("---")
    
    # 다음 단계 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("저장하고 다음 단계로 (정보 검증) 👉", type="primary", use_container_width=True):
            _save_and_proceed()

def _save_and_proceed():
    """입력 데이터 저장 및 단계 이동"""
    state = st.session_state.resume_state
    
    # 필수 필드 검증
    company_name = st.session_state.get("input_company_name", "").strip()
    position_name = st.session_state.get("input_position_name", "").strip()
    job_url = st.session_state.get("input_job_posting_url", "").strip()
    job_content = st.session_state.get("input_job_posting", "").strip()
    
    if not all([company_name, position_name, job_url, job_content]):
        st.error("⚠️ 회사명, 지원 직무, 채용 공고 URL 및 내용은 필수 입력 항목입니다.")
        return

    # Form input keys -> State mapping
    state["company_name"] = company_name
    state["position_name"] = position_name
    state["job_posting"] = job_content
    state["job_posting_url"] = job_url
    
    # Dynamic lists -> State mapping
    if "temp_questions" in st.session_state:
        state["essay_questions"] = st.session_state.temp_questions
    
    # user_experiences는 단순 텍스트로 저장
    user_exp = st.session_state.get("input_user_experiences", "").strip()
    state["user_experiences"] = user_exp
    
    # 검증이 필요함을 표시하는 플래그 설정 (step2에서 자동 검증 트리거)
    st.session_state.need_validation = True
    
    # 기존 검증 결과 초기화
    if "validation_done" in st.session_state:
        del st.session_state.validation_done
    
    # Move step
    state["current_step"] = 2
    
    # 1단계 완료 처리
    if "completed_steps" not in state:
        state["completed_steps"] = []
    if 1 not in state["completed_steps"]:
        state["completed_steps"].append(1)
    
    # 2단계 진입 시 검증 로직이 다시 실행되도록 플래그 초기화 (필요 시)
    st.rerun()
