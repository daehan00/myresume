import streamlit as st
from models.output_models import CompanyResearch
from config.prompts import DEEP_RESEARCH_PROMPT

def render_step3():
    st.header("3단계: 기업 리서치 (Deep Research)")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    st.info("💡 Google Deep Research와 같은 외부 도구를 사용하여 기업 분석을 수행하고, 결과를 아래에 입력해주세요.")
    
    # 1. 프롬프트 생성 섹션
    st.subheader("1. 리서치 프롬프트 생성")
    st.markdown("아래 프롬프트를 복사하여 외부 리서치 도구에 입력하세요.")
    
    prompt = _generate_research_prompt(state)
    
    st.code(prompt, language="text")
    # st.code는 우측 상단에 복사 버튼을 자동으로 제공합니다.
    
    st.markdown("---")
    
    # 2. 결과 입력 섹션
    st.subheader("2. 리서치 결과 입력")
    
    # 기존에 저장된 값이 있으면 불러오기
    current_content = ""
    if state.get("company_research"):
        company_research = state["company_research"]

        if isinstance(company_research, CompanyResearch):
            current_content = company_research.content
        elif isinstance(company_research, dict):
            current_content = company_research.get("content", "")
        else:
            current_content = str(company_research)
        
    research_content = st.text_area(
        "리서치 리포트 내용을 여기에 붙여넣으세요:",
        value=current_content,
        height=400,
        placeholder="예: [기업 개요] 삼성전자는...\n[경영 방향]..."
    )
    
    st.markdown("---")
    
    # 3. 네비게이션
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("👈 이전 단계로"):
            state["current_step"] = 2
            st.rerun()
            
    with col2:
        if st.button("저장하고 다음 단계로 (전략 수립) 👉", type="primary", use_container_width=True):
            if not research_content.strip():
                st.warning("⚠️ 리서치 결과를 입력해주세요.")
            else:
                # 결과 저장
                state["company_research"] = CompanyResearch(content=research_content)
                
                # 다음 단계로 이동
                state["current_step"] = 4
                
                # 3단계 완료 처리
                if "completed_steps" not in state:
                    state["completed_steps"] = []
                if 3 not in state["completed_steps"]:
                    state["completed_steps"].append(3)
                    
                st.rerun()

def _generate_research_prompt(state) -> str:
    """Deep Research용 프롬프트 생성"""
    company = state.get("company_name", "")
    position = state.get("position_name", "")
    job_posting = state.get("job_posting", "")
    
    prompt = DEEP_RESEARCH_PROMPT.format(
        company=company,
        position=position,
        job_posting=job_posting
    )
    return prompt
