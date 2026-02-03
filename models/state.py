from typing import TypedDict, List, Optional, Annotated, Literal
from langgraph.graph.message import add_messages
from models.input_models import EssayQuestion
from models.output_models import CompanyResearch, WritingStrategy

class ResumeState(TypedDict):
    """전체 워크플로우 상태 스키마"""
    
    # 1단계: 입력 데이터
    job_posting: str                    # 채용 공고 원문
    job_posting_url: Optional[str]      # 채용 공고 URL
    company_name: str                   # 회사명
    position_name: str                  # 지원 직무명
    essay_questions: List[EssayQuestion]  # 자기소개서 문항 목록
    user_experiences: str               # 사용자 경험/경력 (자유 텍스트)
    
    # 2단계: 검증 결과
    validation_status: dict             # 각 항목별 충분/부족/불명확
    additional_questions: List[str]     # 추가 질문 목록
    
    # 3단계: 리서치 결과
    company_research: Optional[CompanyResearch] # 기업 리서치 결과
    
    # 4단계: 전략 수립
    writing_strategy: Optional[WritingStrategy] # 작성 전략

    # 5단계: 가이드라인 작성
    writing_guidelines: Optional[str]

    # 6단계: 자기소개서 초안 작성
    # page에서 초기화
    # generated_drafts: dict
    # draft_models: list[str]
    # draft_selections: dict
    # draft_feedbacks: dict
    
    # 메타 정보
    current_step: int                   # 현재 단계 (1-8)
    completed_steps: List[int]          # 완료된 단계 목록
    step_status: Literal["진행중", "대기중", "완료"]
    messages: Annotated[list, add_messages]  # 대화 이력
