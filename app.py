import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 먼저 로드 (settings 임포트 전에 실행)
load_dotenv()

# 로컬 모듈 (환경 변수 로드 후 임포트)
from config.settings import settings
from models.state import ResumeState
from ui.components.sidebar import render_sidebar
from ui.pages.step1_input import render_step1
from ui.pages.step2_validation import render_step2
from ui.pages.step3_research import render_step3
from ui.pages.step4_strategy import render_step4
from ui.pages.step5_guidelines import render_step5
from ui.pages.step6_essay import render_step6

st.set_page_config(
    page_title="Resume Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

def init_session_state():
    """세션 상태 초기화"""
    if "resume_state" not in st.session_state:
        st.session_state.resume_state = ResumeState(
            company_name="",
            position_name="",
            job_posting="",
            job_posting_url="",
            essay_questions=[],
            user_experiences="",
            validation_status={},
            additional_questions=[],
            current_step=1,
            completed_steps=[],
            step_status="대기중",
            messages=[],
            company_research=None,
            writing_strategy=None
        )

def main():
    init_session_state()
    
    state = st.session_state.resume_state
    
    # 도달한 최대 단계 업데이트
    if state["current_step"] > state["max_step"]:
        state["max_step"] = state["current_step"]
    
    # 사이드바 렌더링
    with st.sidebar:
        st.title("Resume Assistant 📝")
        render_sidebar()
    
    # 메인 영역 라우팅
    step = st.session_state.resume_state["current_step"]
    
    if step == 1:
        render_step1()
    elif step == 2:
        render_step2()
    elif step == 3:
        render_step3()
    elif step == 4:
        render_step4()
    elif step == 5:
        render_step5()
    elif step == 6:
        render_step6()
    else:
        st.error(f"알 수 없는 단계입니다: {step}")

if __name__ == "__main__":
    main()