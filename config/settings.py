from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, Literal
import os

class Settings(BaseSettings):
    """애플리케이션 설정
    
    환경변수는 대소문자 구분 없이 자동 매핑됩니다.
    예: MODEL_PROVIDER, model_provider 모두 인식
    """
    
    # LLM Provider Settings
    model_provider: Literal["openai", "anthropic", "google_genai"] = Field(
        default="google_genai",
        description="LLM 제공자"
    )
    model_name: str = Field(
        default="gemini-2.5-flash-lite",
        description="사용할 모델명"
    )
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API Key")
    google_api_key: Optional[str] = Field(default=None, description="Google AI API Key")
    
    # Common Settings
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=4000, gt=0, description="최대 토큰 수")
    debug: bool = Field(default=False, description="디버그 모드")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 대소문자 구분 안함
        extra="ignore"
    )
    
    def get_active_api_key(self) -> Optional[str]:
        """현재 provider에 해당하는 API 키 반환"""
        if self.model_provider == "openai":
            return self.openai_api_key
        elif self.model_provider == "anthropic":
            return self.anthropic_api_key
        elif self.model_provider == "google_genai":
            return self.google_api_key
        return None
    
    def is_configured(self) -> bool:
        """필수 설정이 완료되었는지 확인"""
        return self.get_active_api_key() is not None

settings = Settings()
