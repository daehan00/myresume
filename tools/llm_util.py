from typing import Any
from langchain_core.messages import (
    BaseMessage, 
    SystemMessage, 
    HumanMessage,
    AnyMessage
)

# 사용 가능한 모델 목록
MODEL_PROVIDER_MAP = {
    "gemini-3-pro-preview": "google_genai",
    "gemini-3-flash-preview": "google_genai",
    "gemini-2.5-pro": "google_genai",
    "gemini-2.5-flash": "google_genai",
    "gemini-2.5-flash-lite": "google_genai",
    "gpt-4.1": "openai",
    "gpt-5": "openai",
}

# 사용자에게 표시할 모델 이름
MODEL_DISPLAY_NAMES = {
    "gemini-3-pro-preview": "Gemini 3 Pro (Preview) - 최고 성능",
    "gemini-3-flash-preview": "Gemini 3 Flash (Preview) - 빠른 응답",
    "gemini-2.5-pro": "Gemini 2.5 Pro - 안정적",
    "gemini-2.5-flash": "Gemini 2.5 Flash - 경제적",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite - 매우 빠르고 경제적",
    "gpt-4.1": "GPT-4.1",
    "gpt-5": "GPT-5",
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

def parse_llm_response_content(content: Any) -> str:
    """LLM 응답 컨텐츠를 안전하게 문자열로 변환합니다.
    
    일부 모델(예: Gemini)은 응답을 리스트나 딕셔너리 형태로 반환할 수 있습니다.
    이 함수는 다양한 형식의 응답에서 텍스트를 추출하여 하나의 문자열로 결합합니다.
    
    Args:
        content: LLM 응답의 content 필드 값 (str, list, dict 등)
        
    Returns:
        추출된 텍스트 문자열
    """
    if isinstance(content, str):
        return content
        
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
            elif hasattr(item, 'text'):  # 객체인 경우 (text 속성 확인)
                text_parts.append(item.text) # type: ignore
            elif isinstance(item, str):
                text_parts.append(item)
            else:
                text_parts.append(str(item))
        return "\n".join(text_parts)
    
    if isinstance(content, dict) and 'text' in content:
        return content['text']
        
    return str(content)

def format_messages_to_text(messages: list[BaseMessage | AnyMessage]) -> str:
    """메시지 리스트를 하나의 보기 좋은 텍스트로 변환"""
    formatted_text = ""
    
    for msg in messages:
        if isinstance(msg, SystemMessage):
            formatted_text += f"=== [SYSTEM PROMPT] ===\n{msg.content}\n\n"
        elif isinstance(msg, HumanMessage):
            formatted_text += f"=== [USER PROMPT] ===\n{msg.content}\n\n"
        else:
            formatted_text += f"=== [{msg.type}] ===\n{msg.content}\n\n"
            
    return formatted_text.strip()