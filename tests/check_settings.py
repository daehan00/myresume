#!/usr/bin/env python3
"""설정값 로드 확인 스크립트"""

from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

print("=" * 60)
print("환경 변수 확인")
print("=" * 60)

env_vars = [
    "MODEL_PROVIDER",
    "MODEL_NAME",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TEMPERATURE",
    "MAX_TOKENS",
    "DEBUG"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # API 키는 일부만 표시
        if "API_KEY" in var and value:
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
            print(f"{var:25} = {masked}")
        else:
            print(f"{var:25} = {value}")
    else:
        print(f"{var:25} = (설정 안됨)")

print("\n" + "=" * 60)
print("Settings 객체 확인")
print("=" * 60)

from config.settings import settings

print(f"model_provider            = {settings.model_provider}")
print(f"model_name                = {settings.model_name}")
print(f"temperature               = {settings.temperature}")
print(f"max_tokens                = {settings.max_tokens}")
print(f"debug                     = {settings.debug}")

print("\nAPI 키 설정 상태:")
print(f"  OpenAI API Key          = {'✓ 설정됨' if settings.openai_api_key else '✗ 미설정'}")
print(f"  Anthropic API Key       = {'✓ 설정됨' if settings.anthropic_api_key else '✗ 미설정'}")
print(f"  Google API Key          = {'✓ 설정됨' if settings.google_api_key else '✗ 미설정'}")

print("\n" + "=" * 60)
print("설정 검증")
print("=" * 60)

active_key = settings.get_active_api_key()
if active_key:
    masked = active_key[:10] + "..." + active_key[-4:] if len(active_key) > 14 else "***"
    print(f"✓ 현재 provider ({settings.model_provider})의 API 키: {masked}")
else:
    print(f"✗ 현재 provider ({settings.model_provider})의 API 키가 설정되지 않았습니다!")

if settings.is_configured():
    print("✓ 설정이 올바르게 완료되었습니다.")
else:
    print("✗ 필수 설정이 누락되었습니다!")

print("\n" + "=" * 60)
print("LLM 연결 테스트")
print("=" * 60)

try:
    from config.llm_factory import get_chat_model
    llm = get_chat_model(temperature=0)
    print(f"✓ LLM 인스턴스 생성 성공: {type(llm).__name__}")
    
    # 간단한 테스트
    response = llm.invoke("Hello, respond with just 'OK'")
    print(f"✓ LLM 응답 테스트 성공: {response.content[:50]}")
    
except Exception as e:
    print(f"✗ LLM 연결 실패: {e}")

print("=" * 60)
