from pydantic import BaseModel, Field

from config.llm_factory import get_chat_model
from config.prompts import GUIDELINE_VALIDATION_PROMPT, DEFAULT_GUIDELINE_TEXT


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
    if isinstance(result, dict):
        return GuidelineValidationResult(**result)
    if isinstance(result, GuidelineValidationResult):
        return result
    # If result is a BaseModel (but not GuidelineValidationResult), convert it
    if isinstance(result, BaseModel):
        return GuidelineValidationResult(**result.model_dump())
    raise TypeError("Unexpected result type: {}".format(type(result)))