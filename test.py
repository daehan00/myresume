import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 먼저 로드
load_dotenv()

# 로컬 모듈
from config.settings import settings
from models.state import ResumeState
from models.input_models import EssayQuestion
from models.output_models import CompanyResearch, WritingStrategy
from ui.components.sidebar import render_sidebar
from ui.pages.step1_input import render_step1
from ui.pages.step2_validation import render_step2
from ui.pages.step3_research import render_step3
from ui.pages.step4_strategy import render_step4
from ui.pages.step5_guidelines import render_step5
from ui.pages.step6_essay import render_step6
from ui.pages.step7_review import render_step7
from ui.pages.step8_final import render_step8

from chains.guideline_chain import DEFAULT_GUIDELINE_TEXT
from langchain_core.messages import AIMessage

# step8은 아직 없지만 구조상 준비

st.set_page_config(
    page_title="[TEST] Resume Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Mock Data Generators ---

def get_base_inputs():
    return {
        "company_name": "테크스타트업",
        "position_name": "백엔드 개발자",
        "job_posting": """
        [주요업무]
        - Python/Django 기반의 웹 서비스 서버 개발
        - 대용량 트래픽 처리를 위한 시스템 아키텍처 설계
        - AWS 클라우드 인프라 운영 및 관리
        
        [자격요건]
        - Python 개발 경력 3년 이상
        - RESTful API 설계 및 구현 경험
        - RDBMS 및 NoSQL 데이터베이스 경험
        
        [우대사항]
        - MSA 환경에서의 개발 경험
        - Docker, Kubernetes 등 컨테이너 환경 경험
        """,
        "job_posting_url": "https://example.com/job/123",
        "essay_questions": [
            EssayQuestion(id="1", question_text="지원 동기와 본인이 해당 직무에 적합하다고 생각하는 이유를 서술하시오.", char_limit=1000),
            EssayQuestion(id="2", question_text="가장 어려웠던 기술적 챌린지와 그것을 극복한 과정을 구체적으로 서술하시오.", char_limit=1000)
        ],
        "user_experiences": """
        1. 프로젝트: 이커머스 백엔드 리팩토링
        - 기간: 2023.01 - 2023.06
        - 역할: 백엔드 리드
        - 내용: 레거시 모놀리식 아키텍처를 MSA로 전환. 주문 처리 속도 50% 향상.
        - 기술: Python, FastAPI, Kafka, Redis
        
        2. 프로젝트: 실시간 로그 분석 시스템
        - 기간: 2022.05 - 2022.12
        - 내용: ELK 스택을 활용한 로그 수집 파이프라인 구축
        """,
        "validation_status": {"company_name": "충분", "job_posting": "충분", "essay_questions": "충분", "user_experiences": "충분"},
        "additional_questions": [],
        "need_validation": False
    }

def get_research_data():
    return CompanyResearch(
        content="""
        [기업 개요]
        테크스타트업은 2020년 설립된 핀테크 기업으로, AI 기반의 자산 관리 솔루션을 제공합니다.
        
        [주요 사업]
        - AI 로보어드바이저
        - 마이데이터 기반 신용 분석
        
        [인재상]
        - 기술적 깊이를 추구하는 개발자
        - 주도적으로 문제를 해결하는 사람
        - 끊임없이 학습하는 러너
        """
    )

def get_strategy_data():
    return WritingStrategy(
        core_competencies=["Python 전문성", "시스템 설계 능력", "문제 해결력"],
        talent_traits=["주도성", "기술적 깊이"],
        user_strengths=["MSA 전환 경험", "성능 최적화 성과"],
        user_gaps=["금융 도메인 경험 부족"],
        question_strategy={
            "1": "지원 동기에는 핀테크 산업에 대한 관심과 MSA 경험을 연결하여 기여 가능성을 강조",
            "2": "이커머스 리팩토링 프로젝트를 중심으로 문제 해결 과정을 STAR 기법으로 상세 기술"
        },
        cautions=["추상적인 표현 지양", "성과는 구체적인 수치로 제시"],
        content="""
## 1. 핵심 전략
- **MSA 전환 경험 강조**: 지원 동기와 기술적 챌린지 항목 모두에서 MSA 전환을 통한 성능 개선 경험을 핵심 강점으로 내세웁니다.
- **핀테크 도메인 관심 연결**: 금융 데이터 처리의 중요성과 본인의 기술적 강점(대용량 트래픽 처리)을 연결합니다.

## 2. 문항별 작성 포인트
### Q1. 지원 동기 및 적합성
- **접근**: 단순히 '코딩이 좋아서'가 아니라, '금융 서비스의 기술적 혁신'에 기여하고 싶다는 명확한 목표를 제시하세요.
- **소재**: Kafka와 Redis를 활용한 대용량 트래픽 처리 경험이 테크스타트업의 시스템 아키텍처에 어떻게 기여할 수 있는지 구체적으로 언급합니다.

### Q2. 기술적 챌린지
- **접근**: STAR 기법을 활용하여 상황(S), 과제(T), 행동(A), 결과(R)를 명확히 구분합니다.
- **소재**: 모놀리식에서 MSA로 전환하며 겪었던 데이터 정합성 문제나 네트워크 레이턴시 이슈를 해결한 과정을 상세히 기술합니다.

## 3. 주의사항
- '열심히 하겠습니다'와 같은 추상적인 표현은 지양하고, 수치(속도 50% 향상 등)를 근거로 제시하세요.
""",
    )

def get_draft_data():
    return {
        "1": [
            "(옵션 A) 저는 어릴 때부터 코딩을 좋아했습니다. 다양한 토이 프로젝트를 통해 실력을 쌓아왔으며...",
            "(옵션 B) 사용자의 불편함을 해결하는 백엔드 개발자가 되고 싶습니다. 기술적 한계를 극복하는 과정에서..."
        ],
        "2": [
            "(옵션 A) 레거시 시스템을 MSA로 전환하며 트래픽 처리를 개선했습니다. 이 과정에서 병목 현상을 발견하고...",
            "(옵션 B) Kafka를 도입하여 데이터 파이프라인을 구축했습니다. 실시간 데이터 처리의 정합성을 보장하기 위해..."
        ]
    }

def get_final_essays_data(drafts, selections, feedbacks):
    """선택된 초안과 피드백을 결합하여 가공된 최종본 시뮬레이션"""
    final = {}
    for q_id, draft_list in drafts.items():
        sel_idx = selections.get(q_id, 0)
        selected_text = draft_list[sel_idx]
        feedback = feedbacks.get(q_id, "")
        
        if feedback:
            final[q_id] = (
                f"{selected_text}\n\n"
                f"--- [AI 피드백 반영 완료] ---\n"
                f"요청하신 피드백: '{feedback}' 내용을 반영하여 문장을 다듬고 내용을 보강하였습니다.\n"
                f"최종적으로 정합성이 확보된 버전입니다."
            )
        else:
            final[q_id] = f"{selected_text}\n\n[AI 수정 사항: 선택하신 초안을 문법 및 가독성 중심으로 최종 검토하였습니다.]"
    return final

# --- Session Init ---

def init_session_state():
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
            writing_strategy=None,
            writing_guidelines=None,
        )

# --- Test Controls ---

def render_test_controls():
    with st.sidebar.expander("🧪 TEST CONTROLS", expanded=True):
        st.caption("개발 및 테스트용 컨트롤 패널입니다.")
        
        state = st.session_state.resume_state
        
        # 1. 강제 단계 이동
        target_step = st.number_input("Step 이동", min_value=1, max_value=8, value=state["current_step"])
        if target_step != state["current_step"]:
            state["current_step"] = target_step
            st.rerun()
            
        st.markdown("---")
        st.write("📥 **데이터 주입 & LLM 스킵**")
        
        # 2. 데이터 주입 버튼들
        
        # Case 1: 기본 입력만 주입 (Step 2 검증 테스트용)
        if st.button("Level 1: 입력 완료 (Step 2로)"):
            inputs = get_base_inputs()
            state.update(inputs)
            state["current_step"] = 2
            state["completed_steps"] = [1]
            st.success("기본 입력값 로드 완료")
            st.rerun()

        # Case 2: 리서치 완료 상태 (Step 4 전략 테스트용)
        if st.button("Level 2: 리서치 완료 (Step 4로)"):
            inputs = get_base_inputs()
            state.update(inputs)
            state["company_research"] = get_research_data()
            state["current_step"] = 4
            state["completed_steps"] = [1, 2, 3]
            st.success("리서치 데이터 로드 완료")
            st.rerun()

        # Case 2.5: 전략/가이드 완료 (Step 6 초안 생성 '테스트'용)
        # 실제 LLM 호출을 테스트하기 위해 초안 데이터는 넣지 않음
        if st.button("Level 2.5: 전략/가이드 완료 (Step 6 진입)"):
            inputs = get_base_inputs()
            state.update(inputs)
            
            # 리서치 데이터
            state["company_research"] = get_research_data()
            
            # 전략 데이터 및 채팅 히스토리 동기화
            strategy_data = get_strategy_data()
            state["writing_strategy"] = strategy_data
            st.session_state.strategy_initial_generated = True
            st.session_state.strategy_messages = [AIMessage(content=strategy_data.content)]
            
            # 가이드라인
            state["writing_guidelines"] = DEFAULT_GUIDELINE_TEXT
            
            # 초안 데이터는 명시적으로 제거 (생성 유도)
            if "generated_drafts" in state:
                del state["generated_drafts"]
            
            state["current_step"] = 6
            state["completed_steps"] = [1, 2, 3, 4, 5]
            st.success("Step 6 진입 완료 (초안 생성 버튼 대기)")
            st.rerun()

        # Case 3: 전략/가이드 완료 + 초안 생성 완료 (Step 6 UI 테스트용)
        # LLM 생성 없이 바로 비교 화면을 보기 위함
        if st.button("Level 3: 초안 생성 완료 (Step 6로)"):
            inputs = get_base_inputs()
            state.update(inputs)
            
            # 리서치 데이터
            state["company_research"] = get_research_data()
            
            # 전략 데이터 및 채팅 히스토리 동기화
            strategy_data = get_strategy_data()
            state["writing_strategy"] = strategy_data
            
            # Step 4 UI가 '이미 생성된 상태'로 인식하도록 설정
            st.session_state.strategy_initial_generated = True
            st.session_state.strategy_messages = [AIMessage(content=strategy_data.content)]
            
            state["writing_guidelines"] = DEFAULT_GUIDELINE_TEXT
            
            # Step 6의 LLM 결과물 주입
            state["generated_drafts"] = get_draft_data()
            state["draft_models"] = ["Mock-GPT-4", "Mock-Claude-3"]
            state["draft_selections"] = {"1": 0, "2": 0}
            state["draft_feedbacks"] = {"1": "", "2": ""}
            
            state["current_step"] = 6
            state["completed_steps"] = [1, 2, 3, 4, 5]
            st.success("초안 데이터 로드 완료 (LLM 스킵)")
            st.rerun()

        # Case 4: 초안 선택 완료 (Step 7 진입용)
        if st.button("Level 4: 초안 선택 완료 (Step 7로)"):
            inputs = get_base_inputs()
            state.update(inputs)
            
            state["company_research"] = get_research_data()
            
            # 전략 데이터 및 채팅 히스토리 동기화
            strategy_data = get_strategy_data()
            state["writing_strategy"] = strategy_data
            st.session_state.strategy_initial_generated = True
            st.session_state.strategy_messages = [AIMessage(content=strategy_data.content)]
            
            state["writing_guidelines"] = DEFAULT_GUIDELINE_TEXT
            state["generated_drafts"] = get_draft_data()
            state["draft_models"] = ["Mock-GPT-4", "Mock-Claude-3"]
            
            # 사용자가 선택하고 피드백을 남긴 상태 시뮬레이션
            state["draft_selections"] = {"1": 1, "2": 0} # 1번 문항은 B안, 2번 문항은 A안
            state["draft_feedbacks"] = {"1": "좀 더 구체적으로 써주세요", "2": ""}
            
            # 아직 최종본은 생성 안 된 상태 (Step 7 들어가서 버튼 누르게 됨)
            if "confirmed_essays" in state:
                del state["confirmed_essays"]

            state["current_step"] = 7
            state["completed_steps"] = [1, 2, 3, 4, 5, 6]
            st.success("선택 데이터 로드 완료 (최종 생성 대기)")
            st.rerun()

        # Case 5: 최종본 생성 완료 (Step 7 결과 확인용)
        if st.button("Level 5: 최종본 생성 완료 (Step 7 결과)"):
            inputs = get_base_inputs()
            state.update(inputs)
            
            state["company_research"] = get_research_data()
            
            # 전략 데이터 및 채팅 히스토리 동기화
            strategy_data = get_strategy_data()
            state["writing_strategy"] = strategy_data
            st.session_state.strategy_initial_generated = True
            st.session_state.strategy_messages = [AIMessage(content=strategy_data.content)]
            
            state["writing_guidelines"] = DEFAULT_GUIDELINE_TEXT
            
            drafts = get_draft_data()
            state["generated_drafts"] = drafts
            state["draft_models"] = ["Mock-GPT-4", "Mock-Claude-3"]
            
            # 사용자 선택 및 피드백 예시
            selections = {"1": 1, "2": 0}
            feedbacks = {
                "1": "성과 수치를 더 구체적으로 언급해주고, 문체를 더 전문적으로 바꿔주세요.",
                "2": "기술적인 챌린지 극복 과정을 조금 더 강조해서 수정해주세요."
            }
            state["draft_selections"] = selections
            state["draft_feedbacks"] = feedbacks
            
            # 최종 결과 주입 (선택/피드백 반영 시뮬레이션)
            state["confirmed_essays"] = get_final_essays_data(drafts, selections, feedbacks)
            
            state["current_step"] = 7
            state["completed_steps"] = [1, 2, 3, 4, 5, 6] # 7은 아직 완료 안 된 상태로 진입 (검토 중)
            st.success("최종본 및 피드백 데이터 로드 완료")
            st.rerun()

        st.markdown("---")
        # 3. 상태 초기화
        if st.button("🗑️ 전체 초기화"):
            st.session_state.clear()
            st.rerun()

        # 4. 현재 상태 보기
        with st.expander("🔍 현재 State JSON 보기"):
            st.json(state)

# --- Main App ---

def main():
    init_session_state()
    
    # 테스트 컨트롤 렌더링
    render_test_controls()
    
    # 기존 사이드바 (단계 표시용)
    with st.sidebar:
        st.markdown("---")
        st.title("Resume Assistant 📝")
        render_sidebar()
    
    # 메인 영역 라우팅
    step = st.session_state.resume_state["current_step"]
    
    st.caption(f"🔧 TEST MODE ACTIVATED | Current Step: {step}")
    
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
    elif step == 7:
        render_step7()
    elif step == 8:
        render_step8()
    else:
        st.error(f"알 수 없는 단계입니다: {step}")

if __name__ == "__main__":
    main()