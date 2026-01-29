from typing import List, Dict
from pydantic import BaseModel, Field

class CompanyResearch(BaseModel):
    """기업 및 직무 리서치 결과 (텍스트 원본)"""
    content: str = Field(description="외부 리서치 도구에서 생성된 텍스트 리포트 원본")

class StrategyResponse(BaseModel):
    """전략 응답 (Markdown 형식)"""
    content: str = Field(
        description="전략 전체 내용 (Markdown 형식). "
                    "핵심 역량 매칭, 문항별 전략, 주의사항 등을 모두 포함한 Markdown 형식의 전략 문서"
    )

class WritingStrategy(BaseModel):
    """지원서 작성 전략"""
    core_competencies: List[str] = Field(description="핵심 직무 역량")
    talent_traits: List[str] = Field(description="기업의 선호 인재상")
    user_strengths: List[str] = Field(description="사용자의 강점 (직무/인재상 부합)")
    user_gaps: List[str] = Field(description="사용자의 약점/부족한 점 (보완 필요)")
    question_strategy: Dict[str, str] = Field(description="문항별 작성 포인트 (Key: 문항ID/Index, Value: 전략)")
    cautions: List[str] = Field(description="작성 시 주의사항 및 피해야 할 표현")
    content: str = Field(description="전략 전체 텍스트 (채팅/설명 포함)")
