#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# 현재 디렉토리를 path에 추가하여 로컬 모듈 임포트 가능하게 함
sys.path.append(os.getcwd())

from tools.llm_util import MODEL_PROVIDER_MAP, MODEL_DISPLAY_NAMES, parse_llm_response_content
from config.llm_factory import get_chat_model

def test_all_models():
    load_dotenv()
    
    print("=" * 80)
    print(f"{ 'Model Name':<30} | {'Provider':<15} | {'Status':<10} | {'Response'}")
    print("-" * 80)
    
    for model_name, provider in MODEL_PROVIDER_MAP.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            # 팩토리 함수를 통해 모델 인스턴스 생성
            llm = get_chat_model(provider=provider, model=model_name, temperature=0)
            
            # 간단한 호출 테스트
            response = llm.invoke("Hi, please respond with only your model name and 'OK'.")
            content = parse_llm_response_content(response.content).strip().replace("\n", " ")
            
            print(f"{model_name:<30} | {provider:<15} | {'SUCCESS':<10} | {content[:30]}...")
            
        except Exception as e:
            error_msg = str(e).replace("\n", " ")
            print(f"{model_name:<30} | {provider:<15} | {'FAILED':<10} | {error_msg[:50]}...")

    print("=" * 80)

if __name__ == "__main__":
    test_all_models()
