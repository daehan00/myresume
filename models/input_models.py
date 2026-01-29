from typing import TypedDict, Optional, List

class EssayQuestion(TypedDict):
    id: str
    question_text: str
    char_limit: Optional[int]

class Experience(TypedDict):
    id: str
    project_name: str
    role: str
    description: str
    technologies: List[str]
    achievements: str
    period: str
