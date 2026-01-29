# 지원서 작성 보조 웹앱 기획 문서

## 1. 프로젝트 개요

### 1.1 프로젝트명
**Resume Assistant** - 지원서 작성 보조 시스템

### 1.2 목적
채용 공고 분석부터 자기소개서 작성까지 체계적인 8단계 워크플로우를 통해 
정합성 있는 지원서 작성을 지원하는 웹 애플리케이션

### 1.3 핵심 원칙
- **정합성 우선**: 빠른 생성보다 전략-내용 일관성 보장
- **단계별 검증**: 모든 단계에 사용자 확인/피드백 지점 존재
- **순차 진행**: 전략·요령 확정 전 글 작성 단계 진입 금지

---

## 2. 기술 스택

### 2.1 프론트엔드
| 구분 | 기술 | 용도 |
|------|------|------|
| UI 프레임워크 | Streamlit | 웹 인터페이스 구현 |
| 상태 관리 | streamlit session_state | 단계별 데이터 유지 |

### 2.2 백엔드/AI
| 구분 | 기술 | 용도 |
|------|------|------|
| AI 오케스트레이션 | LangGraph | 워크플로우 상태 관리 및 분기 |
| LLM 통합 | LangChain | LLM 호출, 프롬프트 관리 |
| LLM | OpenAI GPT-4 또는 Claude | 텍스트 생성 및 분석 |
| 웹 스크래핑 | BeautifulSoup, requests | 채용공고 URL 파싱 |

### 2.3 데이터 저장
| 구분 | 기술 | 용도 |
|------|------|------|
| 세션 데이터 | JSON/pickle | 작업 중 데이터 임시 저장 |
| 영구 저장 | SQLite 또는 파일시스템 | 최종 결과물 저장 |

---

## 3. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐       │
│  │ 1단계   │ 2단계   │ 3단계   │ ...     │ 8단계   │       │
│  │ 입력    │ 검증    │ 리서치  │         │ 최종    │       │
│  └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘       │
└───────┼─────────┼─────────┼─────────┼─────────┼─────────────┘
        │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    StateGraph                         │   │
│  │  ┌────────┐    ┌────────┐    ┌────────┐             │   │
│  │  │ Node 1 │───▶│ Node 2 │───▶│ Node 3 │───▶ ...     │   │
│  │  └────────┘    └────────┘    └────────┘             │   │
│  │       │             │             │                  │   │
│  │       ▼             ▼             ▼                  │   │
│  │  [검증/분기]   [검증/분기]   [검증/분기]            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangChain Layer                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Prompts   │  │   Chains   │  │   Tools    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM (GPT-4/Claude)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. LangGraph 워크플로우 설계

### 4.1 전체 상태 스키마

```python
from typing import TypedDict, List, Optional, Literal

class ResumeState(TypedDict):
    # 1단계: 입력 데이터
    job_posting: str                    # 채용 공고 원문
    job_posting_url: Optional[str]      # 채용 공고 URL
    company_name: str                   # 회사명
    position_name: str                  # 지원 직무명
    essay_questions: List[EssayQuestion]  # 자기소개서 문항 목록
    user_experiences: List[Experience]  # 사용자 경험/경력
    
    # 2단계: 검증 결과
    validation_status: dict             # 각 항목별 충분/부족/불명확
    additional_questions: List[str]     # 추가 질문 목록
    
    # 3단계: 리서치 결과
    company_research: CompanyResearch   # 기업 리서치 보고서
    
    # 4단계: 전략
    writing_strategy: WritingStrategy   # 지원서 작성 전략
    
    # 5단계: 작성 요령
    writing_guidelines: WritingGuidelines  # 자기소개서 작성 요령
    
    # 6단계: 초안
    essay_drafts: dict                  # 문항별 초안 (문항ID -> 초안목록)
    confirmed_essays: dict              # 확정된 초안 (문항ID -> 최종본)
    
    # 7단계: 검토 결과
    review_result: ReviewResult         # 종합 검토 결과
    
    # 메타 정보
    current_step: int                   # 현재 단계 (1-8)
    step_status: Literal["진행중", "대기중", "완료"]
    user_feedback: Optional[str]        # 사용자 피드백
```

### 4.2 노드 정의

| 노드명 | 역할 | 입력 | 출력 |
|--------|------|------|------|
| `collect_input` | 입력 데이터 수집 및 정리 | 사용자 입력 | 정리된 입력 데이터 |
| `validate_info` | 정보 충분성 검증 | 입력 데이터 | 검증 결과, 추가 질문 |
| `research_company` | 기업/직무 리서치 | 회사명, 직무, 공고 | 리서치 보고서 |
| `create_strategy` | 작성 전략 수립 | 리서치, 공고, 경험 | 작성 전략 문서 |
| `create_guidelines` | 작성 요령 생성 | 전략, 기본값 | 작성 요령 문서 |
| `write_essay` | 문항별 초안 생성 | 전략, 요령, 문항 | 초안 후보 2-3개 |
| `review_all` | 전체 검토 | 모든 확정 초안 | 검토 결과 |
| `finalize` | 최종 정리 | 모든 산출물 | 최종 패키지 |

### 4.3 분기 조건

```python
def should_continue_validation(state: ResumeState) -> str:
    """2단계 검증 루프 분기"""
    if all(v == "충분" for v in state["validation_status"].values()):
        return "research"  # 3단계로 진행
    return "ask_more"      # 추가 질문 필요

def should_continue_essay(state: ResumeState) -> str:
    """6단계 문항 반복 분기"""
    total = len(state["essay_questions"])
    done = len(state["confirmed_essays"])
    if done < total:
        return "next_question"  # 다음 문항으로
    return "review"            # 7단계로 진행
```

---

## 5. 단계별 상세 설계

### 5.1 1단계: 입력 수집

**UI 구성요소**
- 탭 또는 섹션 기반 입력 폼
- 채용 공고: URL 입력 또는 텍스트 직접 입력 선택
- 자기소개서 문항: 동적 추가/삭제 가능한 폼
- 경험/경력: 프로젝트 단위 구조화 입력

**데이터 모델**
```python
class EssayQuestion(TypedDict):
    id: str
    question_text: str           # 문항 원문
    char_limit: Optional[int]    # 글자 수 제한

class Experience(TypedDict):
    id: str
    project_name: str            # 프로젝트/업무명
    role: str                    # 역할
    description: str             # 수행 내용
    technologies: List[str]      # 사용 기술
    achievements: str            # 성과
    period: str                  # 기간
```

### 5.2 2단계: 필수 정보 검증

**검증 대상**
1. 회사 기본 정보 - 회사명이 명확한지
2. 채용 공고 - 직무 특정 가능한지
3. 자기소개서 문항 - 문항이 1개 이상 있는지
4. 사용자 경험 - 최소 1개 이상의 경험이 있는지

**검증 기준**
| 항목 | 충분 | 부족 | 불명확 |
|------|------|------|--------|
| 회사명 | 정식 명칭 확인됨 | 누락 | 약어/불완전 |
| 채용공고 | 직무/자격요건 포함 | 누락 | 일부만 있음 |
| 문항 | 1개 이상 완전한 형태 | 없음 | 불완전 |
| 경험 | 1개 이상 구체적 | 없음 | 추상적 |

### 5.3 3단계: 기업 및 직무 리서치

**조사 항목**
```python
class CompanyResearch(TypedDict):
    company_overview: str        # 기업 개요 및 주요 사업
    business_direction: str      # 경영 방향
    talent_philosophy: str       # 인재상
    recent_issues: str           # 최근 주요 이슈
    position_requirements: str   # 직무 역량/역할 특성
    culture: str                 # 조직 문화 (확인된 범위)
    unverified_items: List[str]  # 확인 불가 항목 명시
```

### 5.4 4단계: 지원서 작성 전략

**전략 구성요소**
```python
class WritingStrategy(TypedDict):
    core_competencies: List[str]      # 핵심 직무 역량
    talent_traits: List[str]          # 선호 인재상
    user_strengths: List[str]         # 사용자 강점 (충족)
    user_gaps: List[str]              # 사용자 약점 (미달)
    question_strategy: dict           # 문항별 강조 포인트
    cautions: List[str]               # 작성 시 주의사항
```

### 5.5 5단계: 자기소개서 작성 요령

**기본값 (자동 적용)**
```python
DEFAULT_GUIDELINES = {
    "style": "담백한 서술형",
    "tone": "업무 문서 수준, 감정 표현 최소화",
    "structure": ["핵심 요지", "근거 경험/성과", "직무·기업과의 연결"],
    "goal_expression": "현실적, 기간·행동 중심",
}

FORCED_RULES = [
    "AI 톤 표현 금지",
    "영어 병기 금지",
    "순수 텍스트만 사용",
    "과장된 비전/포부 금지",
]
```

### 5.6 6단계: 문항별 초안 작성

**반복 프로세스**
1. 문항 1개 선택
2. 초안 2-3개 병렬 생성
3. 사용자 선택 또는 수정 요청
4. 확정 후 다음 문항으로

### 5.7 7단계: 종합 검토

**검토 항목**
- 문항 간 경험 중복 여부
- 핵심 직무 역량 커버리지
- 인재상 반영 균형
- 톤 및 표현 일관성
- 규칙 위반 여부

### 5.8 8단계: 최종 결과

**산출물**
1. 기업 리서치 보고서
2. 지원서 작성 전략
3. 자기소개서 작성 요령
4. 최종 자기소개서 전체

---

## 6. 폴더 구조

```
myresume/
├── app.py                      # Streamlit 메인 진입점
├── requirements.txt            # 의존성 목록
├── .env                        # 환경 변수 (API 키 등)
├── .env.example                # 환경 변수 예시
│
├── config/
│   ├── __init__.py
│   ├── settings.py             # 전역 설정
│   └── prompts.py              # 프롬프트 템플릿 관리
│
├── models/
│   ├── __init__.py
│   ├── state.py                # LangGraph 상태 스키마
│   ├── input_models.py         # 입력 데이터 모델
│   └── output_models.py        # 출력 데이터 모델
│
├── workflow/
│   ├── __init__.py
│   ├── graph.py                # LangGraph 워크플로우 정의
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── input_node.py       # 1단계 노드
│   │   ├── validation_node.py  # 2단계 노드
│   │   ├── research_node.py    # 3단계 노드
│   │   ├── strategy_node.py    # 4단계 노드
│   │   ├── guidelines_node.py  # 5단계 노드
│   │   ├── essay_node.py       # 6단계 노드
│   │   ├── review_node.py      # 7단계 노드
│   │   └── finalize_node.py    # 8단계 노드
│   └── edges.py                # 분기 조건 함수
│
├── chains/
│   ├── __init__.py
│   ├── research_chain.py       # 리서치용 체인
│   ├── strategy_chain.py       # 전략 수립용 체인
│   ├── writing_chain.py        # 글 작성용 체인
│   └── review_chain.py         # 검토용 체인
│
├── tools/
│   ├── __init__.py
│   ├── web_scraper.py          # 웹 스크래핑 도구
│   └── text_utils.py           # 텍스트 처리 유틸리티
│
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py          # 사이드바 (단계 네비게이션)
│   │   ├── input_forms.py      # 입력 폼 컴포넌트
│   │   ├── feedback.py         # 피드백 UI
│   │   └── display.py          # 결과 표시 컴포넌트
│   └── pages/
│       ├── __init__.py
│       ├── step1_input.py      # 1단계 페이지
│       ├── step2_validation.py # 2단계 페이지
│       ├── step3_research.py   # 3단계 페이지
│       ├── step4_strategy.py   # 4단계 페이지
│       ├── step5_guidelines.py # 5단계 페이지
│       ├── step6_essay.py      # 6단계 페이지
│       ├── step7_review.py     # 7단계 페이지
│       └── step8_final.py      # 8단계 페이지
│
├── storage/
│   ├── __init__.py
│   ├── session_manager.py      # 세션 데이터 관리
│   └── file_manager.py         # 파일 저장/불러오기
│
├── tests/
│   ├── __init__.py
│   ├── test_workflow.py
│   ├── test_chains.py
│   └── test_nodes.py
│
└── docs/
    ├── PROJECT_PLAN.md         # 본 문서
    └── CODING_RULES.md         # 코딩 규칙
```

---

## 7. 화면 흐름

```
┌─────────────────────────────────────────────────────────────┐
│  사이드바          │              메인 영역                  │
│ ┌───────────────┐ │ ┌─────────────────────────────────────┐ │
│ │ 1. 입력 수집  │◀│ │                                     │ │
│ │ 2. 정보 검증  │ │ │         현재 단계 UI                │ │
│ │ 3. 기업 리서치│ │ │                                     │ │
│ │ 4. 전략 수립  │ │ │   - 입력 폼 또는 결과 표시          │ │
│ │ 5. 작성 요령  │ │ │   - 사용자 피드백 버튼              │ │
│ │ 6. 초안 작성  │ │ │                                     │ │
│ │ 7. 종합 검토  │ │ ├─────────────────────────────────────┤ │
│ │ 8. 최종 결과  │ │ │   [이전] [확인/다음] [수정요청]     │ │
│ └───────────────┘ │ └─────────────────────────────────────┘ │
│                   │                                         │
│ ┌───────────────┐ │                                         │
│ │ 진행 상태     │ │                                         │
│ │ ████████░░░░  │ │                                         │
│ │ 4/8 단계      │ │                                         │
│ └───────────────┘ │                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 핵심 제약 사항

### 8.1 단계 진입 조건
| 단계 | 진입 조건 |
|------|-----------|
| 3단계 | 2단계 검증 모두 "충분" |
| 4단계 | 3단계 리서치 사용자 확인 완료 |
| 5단계 | 4단계 전략 사용자 확정 완료 |
| 6단계 | 5단계 작성 요령 확정 완료 |
| 7단계 | 6단계 모든 문항 초안 확정 완료 |
| 8단계 | 7단계 검토 완료 및 수정 반영 완료 |

### 8.2 AI 출력 검증 규칙
모든 AI 출력에 대해 후처리 검증 수행:

1. **금지어 검사**: 도움드리겠습니다, 열정, 성장, 최선을 다하겠습니다
2. **영어 검사**: 괄호 안 영문, 약어 검출
3. **이모지 검사**: 유니코드 이모지 검출
4. **과장 표현 검사**: 선언적 비전, 비현실적 포부 패턴

---

## 9. 향후 확장 고려사항

- 이력서 연동 기능
- 포트폴리오 분석 연동
- 면접 예상 질문 생성
- 다국어 지원 (현재는 한국어 전용)
- 팀/조직 단위 사용자 관리
