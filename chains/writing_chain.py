import asyncio
from typing import Dict, List, Any
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage, 
    AnyMessage
)
from tools.llm_util import (
    get_provider_for_model,
    parse_llm_response_content,
    format_messages_to_text
)
from config.llm_factory import get_chat_model
from config.prompts import WRITER_SYSTEM_PROMPT, WRITER_HUMAN_PROMPT

async def _generate_single_draft_test(state: Dict[str, Any], question: Dict[str, Any], model_name: str) -> str:
    """
    단일 문항, 단일 모델에 대한 초안 생성 (비동기 Task) - 테스트용
    """
    # 비동기 처리 시뮬레이션
    await asyncio.sleep(0.5)
    
    messages = _make_prompt(state, question)

    # 프롬프트 구성 확인용 텍스트 반환
    return format_messages_to_text(messages)

async def _generate_single_draft(
    state: Dict[str, Any],
    question: Dict[str, Any],
    model_name: str
) -> str:
    """
    단일 문항, 단일 모델에 대한 초안 생성 (비동기 Task)
    """
    # 모델 프로바이더 확인 (검증용)
    provider = get_provider_for_model(model_name)
    llm = get_chat_model(provider, model_name, 1.0)

    messages = _make_prompt(state, question)

    response = llm.invoke(messages)
    result = parse_llm_response_content(response.content)

    return result

def _make_prompt(state, question) -> list[BaseMessage | AnyMessage]:
    job_posting = state.get("job_posting", "")
    writing_strategy = state.get("writing_strategy")
    user_experiences = state.get("user_experiences", "")
    writing_guidelines = state.get("writing_guidelines", "")
    
    # 전략 내용 추출
    strategy_content = ""
    if writing_strategy:
        if hasattr(writing_strategy, "content"):
            strategy_content = writing_strategy.content
        elif isinstance(writing_strategy, dict):
            strategy_content = writing_strategy.get("content", "")
        else:
            strategy_content = str(writing_strategy)

    # 시스템 메시지 구성 - 반드시 키워드 인자로 전달
    system_prompt = WRITER_SYSTEM_PROMPT.format(
        job_posting=job_posting,
        strategy_content=strategy_content,
        user_experiences=user_experiences,
        writing_guidelines=writing_guidelines
    )

    human_prompt = WRITER_HUMAN_PROMPT.format(
        question_text=question.get('question_text', ''),
        char_limit=question.get('char_limit', '제한 없음')
    )

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]

    return messages

def generate_drafts(
    state: Dict[str, Any], models: List[str]
) -> Dict[str, List[str]]:
    """
    문항별로 주어진 모델 리스트를 사용하여 병렬로 초안을 생성합니다.
    """
    questions = state.get("essay_questions", [])
    drafts = {}
    
    async def _process_all_questions():
        results = {}
        
        # 모든 (질문, 모델) 조합에 대한 태스크를 한 번에 생성
        all_tasks = []
        task_metadata = []  # (question_idx, model_idx) 매핑 정보
        
        for i, q in enumerate(questions):
            for j, model in enumerate(models):
                task = _generate_single_draft(state, q, model)
                all_tasks.append(task)
                task_metadata.append((i, j))
        
        # 모든 태스크를 한 번에 병렬 실행
        all_outputs = await asyncio.gather(*all_tasks)
        
        # 결과를 질문별로 재구성
        for (q_idx, m_idx), output in zip(task_metadata, all_outputs):
            idx = str(q_idx + 1)
            if idx not in results:
                results[idx] = [None] * len(models)
            results[idx][m_idx] = output
        
        return results

    # 비동기 실행 루프
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 루프가 실행 중인 경우 (Streamlit 등)
            import nest_asyncio
            nest_asyncio.apply()
            drafts = loop.run_until_complete(_process_all_questions())
        else:
            drafts = asyncio.run(_process_all_questions())
    except RuntimeError:
        # "There is no current event loop in thread" or similar
        drafts = asyncio.run(_process_all_questions())
    except ImportError:
        # nest_asyncio가 없는 경우 (동기적으로 실행 시도하거나 에러)
        drafts = asyncio.run(_process_all_questions())

    return drafts
