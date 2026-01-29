from langchain_core.prompts import ChatPromptTemplate
from config.llm_factory import get_chat_model
from pydantic import BaseModel, Field

# 기본 작성 가이드 템플릿
DEFAULT_GUIDELINE_TEXT = """### [기본 작성 원칙]
- 스타일: 간결하고 명확한 서술형 (불필요한 수식어 및 미사여구 지양, 객관적 사실 기반)
- 톤: 업무 문서 수준 (전문적이고 신뢰감 있는 어조), 감정 표현 최소화
- 구조: 핵심 요지 -> 근거 경험/성과 (STAR 기법 활용) -> 직무·기업과의 연결
- 목표 표현: 현실적이고 구체적 (기간·행동 중심, 측정 가능한 성과 지향)

### [필수 준수 사항]
# - AI 특유의 말투 및 표현 금지: AI가 생성한 듯한 정형화되거나 상투적인 표현, 과도한 긍정적 수식어 사용 금지 (예: '도움이 되겠습니다', '열정적인', '최선을 다하는')
# - 괄호 안 영어 병기 금지: 국문 자기소개서 내 괄호 안 영어 병기 지양- 순수 텍스트만 사용: 불필요한 이모지나 특수문자 사용 금지
# - 과장된 비전이나 추상적인 포부 지양: 구체적인 계획과 실행 가능성에 초점
# - 직무 역량 강조: 지원 직무와 관련된 핵심 역량 및 경험을 명확히 제시
# - 정확성 및 완성도: 오탈자 및 비문 검토 필수"""

class GuidelineValidationResult(BaseModel):
    """가이드라인 검증 결과"""
    is_valid: bool = Field(description="가이드라인이 적절한지 여부")
    issues: list[str] = Field(
        default_factory=list,
        description="발견된 문제점 목록 (예: 너무 추상적, 실행 불가능, 모순된 내용 등)"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="개선 제안 목록"
    )
    improved_guideline: str = Field(
        description="개선된 가이드라인 (문제가 있는 경우) 또는 승인된 원본"
    )

# 가이드라인 검증 프롬프트
GUIDELINE_VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"""당신은 자기소개서 작성 가이드라인을 검토하는 전문가입니다.
기본 템플릿과 비교하여 사용자가 작성한 가이드라인을 검토하고, 다음 기준으로 평가하세요:

[검토 기준]
1. 명확성: 지침이 구체적이고 실행 가능한가?
2. 일관성: 서로 모순되는 규칙이 없는가?
3. 실용성: 실제 자기소개서 작성에 적용 가능한가?
4. 완결성: 중요한 작성 원칙이 빠져있지 않은가?

[주의사항]
- 사용자의 의도를 존중하되, 명백한 문제가 있으면 지적하세요
- 너무 추상적이거나 모호한 표현은 구체화를 제안하세요
- AI가 자기소개서를 작성할 때 실제로 활용 가능한 형태로 개선하세요

[기본 템플릿]
{DEFAULT_GUIDELINE_TEXT}
- 사용자가 작성한 내용을 최대한 보존하면서 개선하세요"""),
    ("user", """다음 자기소개서 작성 가이드라인을 검토해주세요:

{user_guideline}

위 가이드라인의 문제점을 파악하고, 필요시 개선된 버전을 제안해주세요.""")
])

def ai_validate_guidelines(
    user_text: str,
    model: str = "gemini-2.5-flash",
    provider: str = "google_genai"
) -> GuidelineValidationResult:
    """AI 모델을 사용하여 사용자의 가이드라인을 검수
    
    Args:
        user_text: 사용자가 입력한 가이드라인
        model: 사용할 모델
        provider: LLM 프로바이더
        
    Returns:
        GuidelineValidationResult: 검증 결과 및 개선된 가이드라인
    """
    llm = get_chat_model(provider=provider, model=model, temperature=0.3)
    
    chain = (
        GUIDELINE_VALIDATION_PROMPT
        | llm.with_structured_output(GuidelineValidationResult)
    )
    
    result = chain.invoke({"user_guideline": user_text})
    return result.content.improved_guideline