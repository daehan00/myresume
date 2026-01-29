from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from config.llm_factory import get_chat_model
from models.output_models import WritingStrategy, StrategyResponse

# 초기 전략 수립 프롬프트
INITIAL_STRATEGY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 대기업 인사팀 출신의 취업 컨설팅 전문가입니다.
사용자의 경험과 채용 공고, 기업 분석 내용을 바탕으로 합격 가능성을 높이는 '자기소개서 작성 전략'을 수립해주세요.

다음 정보를 종합적으로 분석해야 합니다:
1. 지원 기업 및 직무
2. 채용 공고 (요구 역량)
3. 기업 리서치 결과 (인재상, 사업 방향)
4. 사용자 경험/경력 (소재)
5. 자기소개서 문항

[출력 형식]
답변은 Markdown 형식으로 작성하며, 다음 섹션을 반드시 포함해야 합니다:

# 1. 핵심 직무 역량 & 인재상 매칭
- 공고와 기업 분석에서 도출한 핵심 키워드 3~5개
- 사용자의 경험 중 매칭되는 강점
- 보완이 필요한 약점(Gap) 및 대응 방안

# 2. 문항별 작성 전략
(각 문항별로)
- **문항 [번호]**: [문항 요약]
- **의도 파악**: 출제 의도 분석
- **소재 추천**: 사용자의 경험 중 가장 적합한 소재 (구체적으로)
- **작성 포인트**: 강조해야 할 핵심 키워드 및 흐름

# 3. 전체적인 작성 컨셉 및 주의사항
- 전체적인 글의 톤앤매너
- 절대 사용하지 말아야 할 표현이나 주의할 점

[주의사항]
- 사용자와 대화하듯이 자연스럽고 전문적인 어조로 작성하세요.
- 단순히 정보를 나열하지 말고, '전략적'인 인사이트를 제공하세요.
- 사용자가 추가로 수정 요청을 하면 친절하게 답변하고 전략을 보완하세요."""),
    ("user", """
[지원 정보]
기업명: {company_name}
직무: {position_name}

[채용 공고]
{job_posting}

[기업 리서치]
{company_research}

[자기소개서 문항]
{essay_questions}

[사용자 경험/경력]
{user_experiences}

위 정보를 바탕으로 자기소개서 작성 전략을 수립해주세요.""")
])

# 피드백 반영 프롬프트 (채팅 히스토리 포함)
FEEDBACK_STRATEGY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 대기업 인사팀 출신의 취업 컨설팅 전문가입니다.
사용자의 피드백을 바탕으로 자기소개서 작성 전략을 수정하고 보완해주세요.

기존 대화 내용을 참고하여:
1. 사용자가 요청한 내용을 반영하세요
2. 수정된 부분을 명확히 표시하세요
3. 전체 전략의 일관성을 유지하세요
4. 필요하면 추가 제안도 해주세요

답변은 Markdown 형식으로 작성하고, 이전과 동일한 섹션 구조를 유지하세요."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{user_input}")
])

# 구조화된 데이터 추출용 프롬프트
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "당신은 자기소개서 컨설팅 내용을 구조화된 데이터로 변환하는 AI입니다."),
    ("user", "다음 전략 상담 내용을 분석하여 정해진 형식(JSON)으로 추출하세요.\n\n[상담 내용]\n{content}")
])

# 사용 가능한 모델 목록
MODEL_PROVIDER_MAP = {
    "gemini-3-pro-preview": "google_genai",
    "gemini-3-flash-preview": "google_genai",
    "gemini-2.5-pro": "google_genai",
    "gemini-2.5-flash": "google_genai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
}

# 사용자에게 표시할 모델 이름
MODEL_DISPLAY_NAMES = {
    "gemini-3-pro-preview": "Gemini 3 Pro (Preview) - 최고 성능",
    "gemini-3-flash-preview": "Gemini 3 Flash (Preview) - 빠른 응답",
    "gemini-2.5-pro": "Gemini 2.5 Pro - 안정적",
    "gemini-2.5-flash": "Gemini 2.5 Flash - 경제적",
    "gpt-4o": "GPT-4o - OpenAI 최신",
    "gpt-4o-mini": "GPT-4o Mini - 빠르고 경제적",
}

def get_provider_for_model(model: str) -> str:
    """모델명으로부터 프로바이더를 자동 감지
    
    Args:
        model: 모델 이름
        
    Returns:
        프로바이더 이름 (google_genai, openai 등)
        
    Raises:
        ValueError: 지원하지 않는 모델인 경우
    """
    if model not in MODEL_PROVIDER_MAP:
        raise ValueError(f"지원하지 않는 모델입니다: {model}")
    return MODEL_PROVIDER_MAP[model]

def create_initial_strategy_chain(
    model: str = "gemini-3-pro-preview",
    provider_name: str = "google_genai",
    temperature: float = 0.7
):
    """초기 전략 수립 체인 생성 (with_structured_output 사용)
    
    Args:
        model: 사용할 모델 (gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash)
        provider_name: LLM 프로바이더 이름 (google_genai, openai 등)
        temperature: 생성 온도 (0.0-1.0)
        
    Returns:
        Runnable chain
    """
    llm = get_chat_model(provider=provider_name, model=model, temperature=temperature)
    
    return (
        INITIAL_STRATEGY_PROMPT 
        | llm.with_structured_output(StrategyResponse)
    )

def create_feedback_strategy_chain(
    model: str = "gemini-2.5-flash",
    provider_name: str = "google_genai",
    temperature: float = 0.7
):
    """피드백 반영 전략 수정 체인 (채팅 히스토리 포함)
    
    Args:
        model: 사용할 모델 (gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash)
        provider_name: LLM 프로바이더 이름 (google_genai, openai 등)
        temperature: 생성 온도 (0.0-1.0)
        
    Returns:
        Runnable chain
    """
    llm = get_chat_model(provider=provider_name, model=model, temperature=temperature)
    
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
