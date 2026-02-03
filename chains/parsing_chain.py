from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from config.llm_factory import parsing_user_data_llm
from models.input_models import Experience

# Pydantic 모델 정의 (출력 파싱용)
class ExperienceList(BaseModel):
    """경험 목록 구조화 모델"""
    experiences: List[Experience] = Field(description="추출된 경험/경력 목록")

def create_experience_parsing_chain():
    """비정형 텍스트에서 경험 정보를 추출하는 체인"""
    
    # 최신 LangChain: with_structured_output() 사용
    structured_llm = parsing_user_data_llm.with_structured_output(ExperienceList)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 이력서 데이터 구조화 전문가입니다.
사용자가 입력한 비정형 텍스트(경력 기술서, 메모 등)를 분석하여 구조화된 JSON 데이터로 변환하세요.

다음 규칙을 따르세요:
1. 모호한 내용은 원본 텍스트를 최대한 유지하세요.
2. 날짜/기간 정보가 있다면 'YYYY.MM - YYYY.MM' 형식으로 표준화 시도하세요 (불가능하면 원본 유지).
3. 기술 스택은 쉼표로 구분된 리스트로 추출하세요.
4. id는 비워두세요 (시스템이 생성함)."""),
        ("user", "{text}")
    ])
    
    # 최신 LCEL: prompt | structured_llm
    chain = prompt | structured_llm
    return chain

def parse_experiences_from_text(text: str) -> List[dict]:
    """텍스트를 파싱하여 경험 리스트 딕셔너리로 반환
    
    Args:
        text: 파싱할 비정형 텍스트
        
    Returns:
        구조화된 경험 딕셔너리 리스트
        
    Raises:
        ValueError: LLM 설정 오류 또는 파싱 실패
    """
    chain = create_experience_parsing_chain()
    if not chain:
        raise ValueError("LLM 설정 오류: API Key를 확인해주세요.")
        
    try:
        result = chain.invoke({"text": text})
        # Pydantic 모델을 dict로 변환
        return [exp.model_dump() if hasattr(exp, 'model_dump') else exp.dict() 
                for exp in result.experiences] # type: ignore
    except Exception as e:
        # 실제 운영시에는 로깅 필요
        print(f"Parsing error: {e}")
        raise ValueError(f"AI 파싱 실패: {str(e)}")
