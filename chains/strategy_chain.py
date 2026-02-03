from config.llm_factory import get_chat_model
from config.prompts import INITIAL_STRATEGY_PROMPT, FEEDBACK_STRATEGY_PROMPT, EXTRACTION_PROMPT
from models.output_models import WritingStrategy, StrategyResponse
from tools.llm_util import get_provider_for_model

def create_initial_strategy_chain(
    model: str = "gemini-3-pro-preview",
):
    """초기 전략 수립 체인 생성 (with_structured_output 사용)
    
    Args:
        model: 사용할 모델 (gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash)
        
    Returns:
        Runnable chain
    """
    llm = get_chat_model(
        provider=get_provider_for_model(model),
        model=model, temperature=0.7
    )
    
    return (
        INITIAL_STRATEGY_PROMPT 
        | llm.with_structured_output(StrategyResponse)
    )

def create_feedback_strategy_chain(
    model: str = "gemini-2.5-flash",
):
    """피드백 반영 전략 수정 체인 (채팅 히스토리 포함)
    
    Args:
        model: 사용할 모델 (gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash)
        
    Returns:
        Runnable chain
    """
    llm = get_chat_model(
        provider=get_provider_for_model(model),
        model=model, temperature=0.7
    )
    
    return (
        FEEDBACK_STRATEGY_PROMPT
        | llm.with_structured_output(StrategyResponse)
    )

def create_strategy_extraction_chain(
    model: str = "gemini-2.5-pro"
):
    """전략 텍스트 -> 구조화된 데이터 변환 체인
    
    Args:
        model: 사용할 모델
        
    Returns:
        Runnable chain
    """
    provider_name = get_provider_for_model(model)
    llm = get_chat_model(provider=provider_name, model=model, temperature=0)
    
    return (
        EXTRACTION_PROMPT
        | llm.with_structured_output(WritingStrategy)
    )
