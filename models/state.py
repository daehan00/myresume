from typing import TypedDict, List, Optional, Annotated, Literal
from langgraph.graph.message import add_messages

# 임시 타입 정의 (나중에 input_models.py 등으로 이동 가능)
class EssayQuestion(TypedDict):
    id: str
    question_text: str
    char_limit: Optional[int]

class ResumeState(TypedDict):
    """전체 워크플로우 상태 스키마"""
    company_name: str
    current_step: int
    messages: Annotated[list, add_messages]
    # 추가 필드는 기획서에 따라 점진적으로 추가
