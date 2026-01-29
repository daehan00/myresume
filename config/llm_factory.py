from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from config.settings import settings

def get_chat_model(
    provider: str | None = None, 
    model: str | None = None, 
    temperature: float | None = None
) -> BaseChatModel:
    """
    통합 LLM 팩토리 함수 using init_chat_model
    
    Args:
        provider: 'openai', 'anthropic', 'google_genai' (default: settings.model_provider)
        model: 모델명 (default: settings.model_name)
        temperature: 온도 (default: settings.temperature)
    
    Returns:
        Configured ChatModel instance
    """
    
    # 설정값 오버라이드 또는 기본값 사용
    _provider = provider or settings.model_provider
    _model = model or settings.model_name
    _temperature = temperature if temperature is not None else settings.temperature
    
    # API Key 매핑
    api_key = None
    if _provider == "openai":
        api_key = settings.openai_api_key
    elif _provider == "anthropic":
        api_key = settings.anthropic_api_key
    elif _provider == "google_genai":
        api_key = settings.google_api_key
    
    if not api_key:
        # 키가 없으면 실행 시점에 에러가 발생하도록 둡니다 (또는 UI에서 처리)
        pass

    # init_chat_model 활용 (LangChain 최신 문법)
    # 각 provider별 구체적인 클래스 대신 통합 인터페이스 사용
    return init_chat_model(
        model=_model,
        model_provider=_provider,
        temperature=_temperature,
        api_key=api_key
    )
