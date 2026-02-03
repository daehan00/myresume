from pydantic import BaseModel, Field
from typing import List, Literal
from config.llm_factory import input_validation_llm
from config.prompts import INPUT_VALIDATION_PROMPT
from models.state import ResumeState

# 검증 결과 모델
class ValidationItem(BaseModel):
    status: Literal["충분", "부족", "불명확"] = Field(description="항목의 상태")
    reason: str = Field(description="판단 이유")

class ValidationResult(BaseModel):
    company_name: ValidationItem = Field(description="회사명 검증 결과")
    job_posting: ValidationItem = Field(description="채용공고 검증 결과")
    cleaned_job_posting: str = Field(
        description="채용공고에서 필요한 내용만 추출하여 정리한 결과. "
                    "회사 소개, 직무 설명, 주요 업무, 필수/우대 자격요건, 기대역량, "
                    "인재상, 복리후생 등 지원서 작성에 필요한 핵심 정보만 포함. "
                    "광고성 문구, 네비게이션 메뉴, 페이지 헤더/푸터, 중복 컨텐츠는 제거"
    )
    overall_status: Literal["PASS", "FAIL"] = Field(description="전체 통과 여부")
    additional_questions: List[str] = Field(description="부족하거나 불명확한 항목에 대해 사용자에게 물어볼 추가 질문 목록")

def create_validation_chain():
    """입력 데이터 충분성 검증 체인"""
    
    # 최신 LangChain: with_structured_output 사용
    structured_llm = input_validation_llm.with_structured_output(ValidationResult)
        
    # 최신 LCEL: prompt | structured_llm
    chain = INPUT_VALIDATION_PROMPT | structured_llm
    return chain

def validate_resume_input(state: ResumeState) -> ValidationResult:
    """ResumeState 데이터를 기반으로 검증 수행
    
    Args:
        state: 현재 워크플로우 상태
        
    Returns:
        검증 결과 (각 항목별 상태, 추가 질문 등)
        
    Raises:
        ValueError: LLM 설정 오류 또는 필수 데이터 부족
    """
    # 1. 코드 레벨 사전 검증: 사용자 경험 존재 여부
    user_exp = state.get("user_experiences", "")
    if not user_exp or len(user_exp.strip()) < 50:
        raise ValueError(
            "사용자 경험/경력 정보가 부족합니다. 최소 50자 이상의 경험을 입력해주세요."
        )
    
    # 2. 코드 레벨 사전 검증: 자기소개서 문항 존재 여부
    essays = state.get("essay_questions", [])
    if not essays or len(essays) == 0:
        raise ValueError(
            "자기소개서 문항이 없습니다. 최소 1개 이상의 문항을 입력해주세요."
        )
    
    # 3. 채용공고 존재 확인 (UI에서 안전하게 입력되었다고 가정)
    job_posting = state.get("job_posting", "")
    if not job_posting.strip():
        raise ValueError(
            "채용공고 내용이 없습니다. 채용공고 URL을 스크래핑하거나 직접 입력해주세요."
        )
    
    # 4. AI 검증 체인 실행 (회사명/직무명 교차 검증)
    chain = create_validation_chain()
    if not chain:
        raise ValueError("LLM 설정 오류")
    
    result = chain.invoke({
        "company_name": state.get("company_name", ""),
        "position_name": state.get("position_name", ""),
        "job_posting": job_posting,
    })
    
    return result # type: ignore
