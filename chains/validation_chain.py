from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from config.llm_factory import get_chat_model
from models.state import ResumeState
from tools.web_scraper import scrape_job_posting

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
    
    try:
        # 검증은 논리적이여야 하므로 temperature 0
        llm = get_chat_model("google_genai", "gemini-2.5-flash", temperature=0)
    except Exception:
        return None
    
    # 최신 LangChain: with_structured_output 사용
    structured_llm = llm.with_structured_output(ValidationResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 채용 전문가입니다. 지원자가 입력한 정보가 자기소개서를 작성하기에 충분한지 검증하세요.

# 검증 기준
1. 회사명 & 채용공고 교차 검증:
   - 입력된 회사명이 채용공고 내용에 실제로 나타나는가?
   - 입력된 직무명이 채용공고의 직무/포지션과 일치하는가?
   - 불일치 시 '불명확', 일부만 일치 시 '불명확', 명확히 일치 시 '충분'
   
2. 채용공고 내용:
   - 직무 설명, 주요 업무, 자격요건이 구체적으로 포함되어 있는가?
   - 너무 짧거나 제목/개요만 있으면 '부족'

# 채용공고 정리 규칙 (cleaned_job_posting)
원본 채용공고에서 아래 내용만 추출하여 깔금하게 정리하세요:

**포함할 내용:**
- 회사 소개 (비전, 사업 영역, 규모 등 핵심만)
- 모집 직무/포지션 명칭
- 직무 설명 (역할, 책임)
- 주요 업무 내용
- 필수 자격요건
- 우대 자격요건
- 기대하는 역량/특성
- 인재상 또는 조직문화
- 혁심 과제/프로젝트 (있는 경우)
- 복리후생 (간략하게)

**제거할 내용:**
- 웹사이트 네비게이션 메뉴 ("홈", "채용정보", "로그인" 등)
- 페이지 헤더/푸터 ("분야별 채용", "지원하기" 버튼 등)
- 광고성 문구 ("최고의 기회", "함께 성장할" 등 과장된 표현)
- 중복된 컨텐츠
- 지원 방법/절차 안내 ("이력서 제출", "면접 일정" 등)
- 불필요한 디자인 요소 ("---", "===" 등)
- 무의미한 반복 문구

최종 출력은 명료하고 구조화되어야 하며, 지원서 작성에 직접 활용할 수 있는 형태여야 합니다.

# 출력 규칙
각 항목별로 '충분', '부족', '불명확' 중 하나로 판정하고 이유를 적으세요.
부족하거나 불명확한 항목이 있다면, 이를 보완하기 위해 사용자에게 할 질문을 생성하세요.
모든 항목이 '충분'이어야 overall_status가 'PASS'가 됩니다.

중요: 회사명과 직무명이 채용공고와 일치하는지 교차 검증을 반드시 수행하세요."""),
        ("user", """
[입력 데이터]
회사명: {company_name}
지원 직무: {position_name}

[채용공고 원문 - 정리가 필요함]
{job_posting}""")
    ])
    
    # 최신 LCEL: prompt | structured_llm
    chain = prompt | structured_llm
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
