import streamlit as st
from typing import List
import uuid
from models.input_models import EssayQuestion
from tools.web_scraper import scrape_job_posting

def render_job_details_form(disabled: bool = False):
    """기본 채용 정보 입력 폼"""
    st.subheader("1. 채용 정보")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "회사명*",
            key="input_company_name",
            value=st.session_state.resume_state.get("company_name", ""),
            placeholder="예: 삼성전자",
            disabled=disabled
        )
    with col2:
        st.text_input(
            "지원 직무*",
            key="input_position_name",
            value=st.session_state.resume_state.get("position_name", ""),
            placeholder="예: SW 개발",
            disabled=disabled
        )
    
    # URL 입력 및 스크래핑 버튼
    col_url, col_btn = st.columns([3, 1])
    with col_url:
        st.text_input(
            "채용 공고 URL*",
            key="input_job_posting_url",
            value=st.session_state.resume_state.get("job_posting_url", ""),
            placeholder="https://recruit.samsung.com/...",
            disabled=disabled
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)  # 버튼 정렬을 위한 여백
        if st.button("🔍 스크래핑", key="scrape_btn", use_container_width=True, disabled=disabled):
            url = st.session_state.get("input_job_posting_url", "").strip()
            if not url:
                st.warning("⚠️ URL을 먼저 입력해주세요.")
            else:
                with st.spinner("채용공고를 불러오는 중..."):
                    scraped_content = scrape_job_posting(url)
                    if scraped_content:
                        # 성공: 텍스트 영역에 자동 입력
                        st.session_state["input_job_posting"] = scraped_content
                        st.success(f"✅ 스크래핑 성공! ({len(scraped_content)}글자)")
                        st.rerun()
                    else:
                        # 실패: 사용자에게 직접 복사 안내
                        st.error(
                            "❌ 스크래핑에 실패했습니다. "
                            "채용공고 페이지에서 내용을 직접 복사해서 아래 텍스트 영역에 붙여넣어주세요."
                        )
    
    st.text_area(
        "채용 공고 내용*",
        key="input_job_posting",
        value=st.session_state.resume_state.get("job_posting", ""),
        height=200,
        placeholder="위 '스크래핑' 버튼을 눌러 자동으로 불러오거나, 직접 복사해서 붙여넣으세요.",
        disabled=disabled
    )
    st.caption("💡 팁: URL을 입력하고 '스크래핑' 버튼을 누르면 자동으로 내용이 채워집니다.")

def render_essay_questions_form(disabled: bool = False):
    """자기소개서 문항 입력 폼 (동적 추가/삭제)"""
    st.subheader("2. 자기소개서 문항")
    
    # 세션에 임시 리스트가 없으면 초기화
    if "temp_questions" not in st.session_state:
        # 기존 state에 데이터가 있으면 가져오고, 없으면 빈 리스트
        current_data = st.session_state.resume_state.get("essay_questions", [])
        if not current_data:
            current_data = [{"id": str(uuid.uuid4()), "question_text": "", "char_limit": None}]
        st.session_state.temp_questions = current_data

    # 문항 추가 버튼
    if st.button("➕ 문항 추가", key="add_question_btn", disabled=disabled):
        st.session_state.temp_questions.append({
            "id": str(uuid.uuid4()), 
            "question_text": "", 
            "char_limit": None
        })
        st.rerun()

    # 문항 리스트 렌더링
    questions_to_remove = []
    for i, q in enumerate(st.session_state.temp_questions):
        with st.expander(f"문항 {i+1}", expanded=True):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                q["question_text"] = st.text_area(
                    "질문 내용",
                    value=q["question_text"],
                    key=f"q_text_{q['id']}",
                    height=100,
                    disabled=disabled
                )
                
                limit_val = q.get("char_limit")
                if limit_val is None:
                    limit_val = 0
                
                new_limit = st.number_input(
                    "글자 수 제한 (0이면 제한 없음)",
                    min_value=0,
                    value=int(limit_val),
                    key=f"q_limit_{q['id']}",
                    disabled=disabled
                )
                q["char_limit"] = new_limit if new_limit > 0 else None
            
            with col2:
                if len(st.session_state.temp_questions) > 1:
                    if st.button("🗑️", key=f"del_q_{q['id']}", disabled=disabled):
                        questions_to_remove.append(i)
    
    # 삭제 처리
    if questions_to_remove:
        for idx in sorted(questions_to_remove, reverse=True):
            st.session_state.temp_questions.pop(idx)
        st.rerun()

def render_experience_form(disabled: bool = False):
    """경험/경력 입력 폼 (단순 텍스트)"""
    st.subheader("3. 주요 경험/경력")
    
    st.text_area(
        "경험/경력 내용*",
        key="input_user_experiences",
        value=st.session_state.resume_state.get("user_experiences", ""),
        height=400,
        placeholder="경험, 경력, 프로젝트 등을 자유롭게 작성해주세요.\n\n예시:\n- AI 기반 추천 시스템 개발 (2023.03 - 2023.08)\n  역할: 백엔드 개발자\n  내용: Python/FastAPI를 사용하여 REST API 개발...\n\n- 데이터 분석 프로젝트 (2022.09 - 2022.12)\n  ...",
        disabled=disabled
    )
    st.caption("💡 팁: 최소 50자 이상 작성해주세요. 프로젝트명, 기간, 역할, 내용, 성과 등을 포함하면 좋습니다.")


