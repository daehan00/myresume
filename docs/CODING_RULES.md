# 코딩 규칙 및 컨벤션

## 1. 일반 규칙
- **인코딩**: UTF-8
- **언어**: 주석/문서화는 한국어, 식별자는 영어
- **네이밍**: 변수/함수(`snake_case`), 클래스(`PascalCase`), 상수(`SCREAMING_SNAKE_CASE`)
- **Python 버전**: 3.10 이상
- **가상환경**: `uv` 사용 (`.venv`), `pyproject.toml`로 의존성 관리

## 2. 코드 스타일
- **포맷팅**: PEP 8 준수 (들여쓰기 4공백, 최대 100자)
- **도구**: `black`(포맷팅), `isort`(import 정렬), `flake8`(린팅), `mypy`(타입체크) 사용
- **Import 순서**: 표준 라이브러리 -> 서드파티 -> 로컬 모듈 순으로 그룹화

## 3. 타입 힌트
- **필수 적용**: 함수 매개변수/반환값, 클래스 속성, 모듈 레벨 변수
- **검증**: `mypy` 검사 시 오류가 없어야 함

## 4. 문서화
- **Docstring**: Google 스타일 사용 (Args, Returns, Raises 명시)
- **주석**: "무엇을"이 아닌 "왜" 하는지를 설명, 복잡한 로직에만 작성

## 5. LangGraph 규칙
- **상태(State)**: `TypedDict`로 정의, 단계별 데이터 누적 구조 유지
- **노드(Node)**: `state`를 입력받아 업데이트할 필드만 포함된 `dict` 반환
- **엣지(Edge)**: 조건부 로직은 별도 함수로 분리하여 `add_conditional_edges` 사용

## 6. LangChain 규칙

### 6.1 LCEL (LangChain Expression Language) 필수 사용
- **파이프 연산자**: 모든 체인은 `|` 연산자를 사용하여 구성
- **구형 API 금지**: `LLMChain`, `ConversationChain` 등 레거시 클래스 사용 금지
- **Runnable 인터페이스**: 모든 컴포넌트는 `.invoke()`, `.stream()`, `.batch()` 메서드 지원

```python
# ✅ 권장: LCEL 사용
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_messages([("user", "{input}")])
    | llm
    | StrOutputParser()
)
result = chain.invoke({"input": "질문"})

# ❌ 금지: 레거시 Chain 클래스
from langchain.chains import LLMChain  # 사용 금지
chain = LLMChain(llm=llm, prompt=prompt)
```

### 6.2 프롬프트 관리
- **중앙 관리**: 모든 프롬프트는 `config/prompts.py`에서 관리
- **ChatPromptTemplate 사용**: 시스템/사용자/AI 메시지 구분
- **변수 명명**: 프롬프트 변수는 명확하고 일관된 이름 사용 (`{input}`, `{context}` 등)

```python
# config/prompts.py
from langchain_core.prompts import ChatPromptTemplate

RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "당신은 기업 분석 전문가입니다."),
    ("user", "회사명: {company_name}\n직무: {position}\n\n분석 결과를 작성하세요.")
])

# chains/research_chain.py
from config.prompts import RESEARCH_PROMPT

chain = RESEARCH_PROMPT | llm | parser
```

### 6.3 구조화된 출력 (Structured Output)
- **with_structured_output() 사용**: Pydantic 모델 기반 타입 안전한 출력
- **PydanticOutputParser 지양**: 레거시 파서 대신 최신 메서드 우선 사용
- **검증 로직**: Pydantic의 `field_validator`를 활용한 사전 검증

```python
from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI

class CompanyResearch(BaseModel):
    """기업 리서치 결과"""
    company_overview: str = Field(description="기업 개요")
    business_direction: str = Field(description="경영 방향")
    
    @field_validator("company_overview")
    @classmethod
    def validate_overview(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("개요는 50자 이상이어야 합니다")
        return v

# ✅ 권장: with_structured_output 사용
llm = ChatOpenAI(model="gpt-4o")
structured_llm = llm.with_structured_output(CompanyResearch)
chain = prompt | structured_llm
result: CompanyResearch = chain.invoke({"company": "네이버"})

# ❌ 지양: PydanticOutputParser (필요시에만 사용)
from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=CompanyResearch)
```

### 6.4 체인 구성 패턴
- **RunnablePassthrough**: 입력을 그대로 전달하거나 변형
- **RunnableLambda**: 커스텀 함수를 체인에 통합
- **RunnableParallel**: 병렬 실행 및 결과 조합

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel

# 입력 전달 및 변형
chain = (
    RunnablePassthrough.assign(
        processed_input=lambda x: x["raw_input"].strip().lower()
    )
    | prompt
    | llm
)

# 커스텀 함수 통합
def validate_output(text: str) -> str:
    """금지어 검증 후처리"""
    forbidden_words = ["도움드리겠습니다", "열정", "최선을"]
    for word in forbidden_words:
        if word in text:
            raise ValueError(f"금지어 포함: {word}")
    return text

chain = (
    prompt 
    | llm 
    | StrOutputParser() 
    | RunnableLambda(validate_output)
)

# 병렬 실행
parallel_chain = RunnableParallel({
    "research": research_chain,
    "analysis": analysis_chain,
})
result = parallel_chain.invoke({"company": "네이버"})
# result = {"research": ..., "analysis": ...}
```

### 6.5 LLM 모델 선택 및 설정
- **모델별 Import**: `langchain_openai`, `langchain_anthropic` 등 공식 패키지 사용
- **공통 인터페이스**: `BaseChatModel` 타입으로 추상화하여 모델 교체 용이하게
- **파라미터 설정**: temperature, max_tokens 등을 명시적으로 설정

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

def get_llm(model_name: str = "gpt-4o", temperature: float = 0.7) -> BaseChatModel:
    """LLM 인스턴스 생성 팩토리 함수"""
    if model_name.startswith("gpt"):
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=2000,
        )
    elif model_name.startswith("claude"):
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=2000,
        )
    else:
        raise ValueError(f"지원하지 않는 모델: {model_name}")
```

### 6.6 스트리밍 지원
- **긴 응답 처리**: 사용자 경험 향상을 위해 스트리밍 활용
- **astream 메서드**: 비동기 스트리밍 지원 시 사용

```python
# 동기 스트리밍
for chunk in chain.stream({"input": "긴 글 작성 요청"}):
    print(chunk, end="", flush=True)

# 비동기 스트리밍 (Streamlit 등에서 활용)
async for chunk in chain.astream({"input": "질문"}):
    await asyncio.sleep(0.01)  # UI 업데이트
    print(chunk, end="", flush=True)
```

### 6.7 에러 처리 및 재시도
- **with_retry**: 일시적 오류에 대한 자동 재시도
- **fallbacks**: 대체 체인 설정으로 안정성 확보

```python
from langchain_core.runnables import RunnableWithFallbacks

# 재시도 설정
chain_with_retry = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

# Fallback 체인
primary_chain = prompt | gpt4_llm | parser
fallback_chain = prompt | gpt35_llm | parser

chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])
```

### 6.8 검증 및 후처리
- **후처리 검증**: 모든 AI 출력에 대해 금지어/형식 검증 필수
- **RunnableLambda 활용**: 검증 로직을 체인의 일부로 통합
- **예외 처리**: 검증 실패 시 명확한 예외 메시지

```python
class AIOutputError(Exception):
    """AI 출력 검증 실패"""
    pass

def validate_essay_output(text: str) -> str:
    """자기소개서 출력 검증"""
    # 금지어 검사
    forbidden_words = ["도움드리겠습니다", "열정", "성장", "최선을 다하겠습니다"]
    for word in forbidden_words:
        if word in text:
            raise AIOutputError(f"금지어 포함: {word}")
    
    # 영어 검사
    import re
    if re.search(r'\([A-Za-z\s]+\)', text):
        raise AIOutputError("괄호 안 영문 병기 금지")
    
    # 이모지 검사
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # 이모티콘
        u"\U0001F300-\U0001F5FF"  # 기호
        "]+", flags=re.UNICODE)
    if emoji_pattern.search(text):
        raise AIOutputError("이모지 사용 금지")
    
    return text

# 체인에 통합
essay_chain = (
    prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(validate_essay_output)
)
```

### 6.9 메모리 및 대화 기록
- **ChatMessageHistory**: 대화 기록 관리 (필요시에만 사용)
- **RunnableWithMessageHistory**: 메모리 통합 체인 구성

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 세션별 메모리 관리
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 메모리 통합 체인
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

result = chain_with_history.invoke(
    {"input": "질문"},
    config={"configurable": {"session_id": "user123"}}
)
```

### 6.10 타입 힌팅 및 문서화
- **제네릭 타입**: 체인의 입력/출력 타입을 명확히 지정
- **Docstring**: 각 체인의 목적, 입력/출력 형식 문서화

```python
from typing import Dict, Any
from langchain_core.runnables import Runnable

def create_research_chain(llm: BaseChatModel) -> Runnable[Dict[str, Any], CompanyResearch]:
    """기업 리서치 체인 생성
    
    Args:
        llm: 사용할 언어 모델
        
    Returns:
        입력으로 company_name, position을 받아 CompanyResearch 객체를 반환하는 체인
        
    Raises:
        AIOutputError: 출력 검증 실패 시
    """
    return (
        RESEARCH_PROMPT
        | llm.with_structured_output(CompanyResearch)
        | RunnableLambda(validate_research_output)
    )
```

## 7. Streamlit 규칙
- **상태 관리**: `st.session_state`를 사용하여 단계별 데이터 및 플래그 관리
- **구조**: 페이지별 비즈니스 로직과 재사용 가능한 UI 컴포넌트(forms, display 등) 분리
- **UX**: 긴 작업 시 `st.spinner` 등으로 진행 상태 표시

## 8. 에러 처리
- **재시도**: LLM 생성 실패 또는 검증 실패 시 최대 3회 재시도 로직 구현
- **예외 처리**: 커스텀 예외(`AIOutputError` 등)를 정의하여 명시적으로 에러 전파

## 9. 테스트
- **프레임워크**: `pytest` 사용
- **명명 규칙**: `test_<동작>_<조건>_<기대결과>`

## 10. 환경 설정
- **관리**: `.env` 파일 사용 (버전 관리 제외)
- **로드**: `pydantic-settings`를 사용하여 타입 안전하게 로드

## 11. 커밋 규칙
- **형식**: `<타입>: <제목>` (예: `feat: 기능 추가`)
- **타입**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
