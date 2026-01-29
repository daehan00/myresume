from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    openai_api_key: str
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
