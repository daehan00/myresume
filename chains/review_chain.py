import asyncio
from dataclasses import dataclass

from langchain_core.messages import (
    SystemMessage, 
    HumanMessage, 
    BaseMessage, 
    AnyMessage
)
from tools.llm_util import (
    parse_llm_response_content,
    format_messages_to_text
)
from models.state import ResumeState
from config.prompts import (
    REVIEW_SYSTEM_PROMPT, 
    REVIEW_HUMAN_PROMPT, 
    DEFAULT_GUIDELINE_TEXT
)
from config.llm_factory import final_llm

@dataclass
class ReviewContext:
    question: str
    draft: str
    feedback: str
    guidelines: str
    company_name: str
    position_name: str
    user_experiences: str

def generate_final_essays(state: ResumeState) -> dict[str, str]:
    """
    Step 6에서 선택된 초안과 피드백을 바탕으로 최종 초안 생성을 위한 프롬프트를 반환합니다.
    (실제 LLM 호출 대신 프롬프트 텍스트를 반환, 비동기 구조 유지)
    
    Args:
        state (ResumeState): 현재 세션 상태
        
    Returns:
        Dict[str, str]: 문항 번호(ID)를 키로 하고, 생성된 프롬프트 텍스트를 값으로 하는 딕셔너리
    """
    questions = state.get("essay_questions", [])
    final_results = {}
    
    async def _process_all_questions():
        tasks = []
        for i, q in enumerate(questions):
            # 1-based index string for keys
            q_idx = str(i + 1)
            context = _initialize_context(state, i)
            # tasks.append(_generate_single_final_draft_test(q_idx, context))
            tasks.append(_generate_single_final_draft(q_idx, context))
        
        # [(q_idx, text), (q_idx, text), ...]
        results = await asyncio.gather(*tasks)
        return dict(results)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 루프가 실행 중인 경우 (Streamlit 등)
            import nest_asyncio
            nest_asyncio.apply()
            final_results = loop.run_until_complete(_process_all_questions())
        else:
            final_results = asyncio.run(_process_all_questions())
    except RuntimeError:
        # "There is no current event loop in thread"
        final_results = asyncio.run(_process_all_questions())
    except ImportError:
        # nest_asyncio가 없는 경우 (동기적으로 실행 시도하거나 에러)
        # 여기서는 간단히 asyncio.run 시도
         final_results = asyncio.run(_process_all_questions())

    return final_results

async def _generate_single_final_draft_test(
    q_idx: str, context: ReviewContext
) -> tuple[str, str]:
    """단일 문항에 대한 프롬프트 생성 (비동기 시뮬레이션)"""
    
    # 프롬프트 생성
    messages = _make_prompt(context)
    
    # 메시지를 하나의 텍스트로 변환
    full_prompt_text = format_messages_to_text(messages)
    
    # (LLM 호출 대신 텍스트 반환)
    return (q_idx, full_prompt_text)

async def _generate_single_final_draft(
    q_idx: str, context: ReviewContext
) -> tuple[str, str]:
    """단일 문항에 대한 피드백을 반영하여 최종 초안 생성"""
    messages = _make_prompt(context)

    response = final_llm.invoke(messages)
    
    # 유틸리티 함수를 사용하여 안전하게 텍스트 추출
    result = parse_llm_response_content(response.content)

    return (q_idx, result)


def _initialize_context(state: ResumeState, idx: int) -> ReviewContext:
    """State에서 필요한 정보를 추출하여 Context 객체 생성"""
    q_id = str(idx + 1)
    
    # 질문 텍스트
    question_item = state["essay_questions"][idx]
    question_text = question_item.get("question_text", "")
    
    # 선택된 초안 가져오기
    drafts = state.get("generated_drafts", {})
    selections = state.get("draft_selections", {})
    
    selected_idx = selections.get(q_id, 0)
    draft_list = drafts.get(q_id, [])
    
    if draft_list and len(draft_list) > selected_idx:
        selected_draft = draft_list[selected_idx]
    else:
        selected_draft = "선택된 초안이 없습니다."
        
    # 피드백 가져오기
    feedbacks = state.get("draft_feedbacks", {})
    feedback_text = feedbacks.get(q_id, "")
    if not feedback_text:
        feedback_text = "별도의 수정 요청사항 없음 (자연스럽게 다듬어주세요)"
    
    # 추가 컨텍스트 정보
    guidelines = state.get("writing_guidelines")
    if not guidelines:
        guidelines = DEFAULT_GUIDELINE_TEXT
        
    company_name = state.get("company_name", "회사명 미상")
    position_name = state.get("position_name", "직무 미상")
    user_experiences = state.get("user_experiences", "")
        
    return ReviewContext(
        question=question_text,
        draft=selected_draft,
        feedback=feedback_text,
        guidelines=guidelines,
        company_name=company_name,
        position_name=position_name,
        user_experiences=user_experiences
    )

def _make_prompt(context: ReviewContext) -> list[BaseMessage | AnyMessage]:
    """Context를 기반으로 LangChain 메시지 리스트 생성"""
    
    # 시스템 메시지 (추가 정보 포맷팅)
    system_content = REVIEW_SYSTEM_PROMPT.format(
        guidelines=context.guidelines,
        company_name=context.company_name,
        position_name=context.position_name,
        user_experiences=context.user_experiences
    )
    system_msg = SystemMessage(content=system_content)
    
    # 사용자 메시지 (템플릿 적용)
    human_content = REVIEW_HUMAN_PROMPT.format(
        question=context.question,
        draft=context.draft,
        feedback=context.feedback
    )
    human_msg = HumanMessage(content=human_content)
    
    return [system_msg, human_msg]

