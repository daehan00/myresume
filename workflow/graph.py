from langgraph.graph import StateGraph, END
from models.state import ResumeState

def create_resume_graph() -> StateGraph:
    """지원서 작성 워크플로우 그래프 생성"""
    graph = StateGraph(ResumeState)
    
    # TODO: 노드 및 엣지 추가
    
    return graph
