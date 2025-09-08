# 🚀 빠른 시작 예제

이 예제는 vibe-agents 프로젝트에서 첫 번째 AI 에이전트를 만드는 과정을 보여줍니다.

## 📝 예제: 간단한 AI 챗봇 에이전트

### 1단계: 새 기능 생성

```bash
# 프로젝트 루트에서 실행
./scripts/create-new-feature.sh "사용자와 대화할 수 있는 AI 챗봇 에이전트"
```

**출력:**
```
Switched to a new branch '001-ai'
BRANCH_NAME: 001-ai
SPEC_FILE: /path/to/vibe-agents/specs/001-ai/spec.md
FEATURE_NUM: 001
```

### 2단계: 명세서 작성

`specs/001-ai/spec.md` 파일을 편집:

```markdown
# 기능 명세서: AI 챗봇 에이전트

**기능 브랜치**: `001-ai-chatbot-agent`  
**생성일**: 2024-12-08  
**상태**: 초안  
**입력**: 사용자 설명: "사용자와 대화할 수 있는 AI 챗봇 에이전트"

## 사용자 시나리오 & 테스트

### 주요 사용자 스토리
개발자가 CLI를 통해 AI 챗봇과 자연어로 대화할 수 있습니다. 챗봇은 사용자의 질문에 대해 상황에 맞는 답변을 제공합니다.

### 수용 시나리오
1. **Given** 사용자가 `vibe-agents chatbot --chat` 명령 실행, **When** "안녕하세요"라고 입력, **Then** 친근한 한국어 인사말로 응답
2. **Given** 사용자가 "파이썬에 대해 알려주세요"라고 질문, **When** 챗봇이 처리, **Then** 파이썬에 대한 유용한 정보를 구조화된 형식으로 제공
3. **Given** 사용자가 이전 대화 내용을 확인하고 싶을 때, **When** `--history` 옵션 사용, **Then** 최근 대화 기록을 보여줌

### 엣지 케이스
- 사용자가 빈 메시지를 입력하면 재입력을 요청
- AI 모델이 응답하지 못하면 적절한 오류 메시지 표시
- 네트워크 연결이 없으면 오프라인 상태임을 알림

## 요구사항

### 기능 요구사항
- **FR-001**: 시스템은 CLI를 통해 사용자의 텍스트 입력을 받아야 함
- **FR-002**: 시스템은 외부 AI 모델(예: OpenAI GPT)을 통해 응답을 생성해야 함
- **FR-003**: 시스템은 대화 세션 동안 히스토리를 메모리에 유지해야 함
- **FR-004**: 시스템은 대화 히스토리를 로컬 파일에 저장해야 함
- **FR-005**: 시스템은 이전 대화 히스토리를 조회할 수 있어야 함
- **FR-006**: 시스템은 한국어와 영어를 모두 지원해야 함
- **FR-007**: 시스템은 연결 오류 시 적절한 오류 메시지를 표시해야 함

### 핵심 엔티티
- **ChatSession**: 대화 세션 정보 (ID, 시작 시간, 사용자 ID)
- **Message**: 개별 메시지 (발신자, 내용, 타임스탬프, 세션 ID)
- **ChatAgent**: AI 챗봇 에이전트 (모델 설정, 응답 생성 로직)

## 검토 & 수용 체크리스트

### 콘텐츠 품질
- [x] 구현 세부사항 없음 (언어, 프레임워크, API)
- [x] 사용자 가치 및 비즈니스 요구에 집중
- [x] 비기술적 이해관계자를 위해 작성
- [x] 모든 필수 섹션 완료

### 요구사항 완전성
- [x] [명확화 필요] 마커가 남아있지 않음
- [x] 요구사항이 테스트 가능하고 명확함
- [x] 성공 기준이 측정 가능함
- [x] 범위가 명확히 제한됨
- [x] 종속성 및 가정이 식별됨
```

### 3단계: 구현 계획 생성

```bash
./scripts/setup-plan.sh
```

`specs/001-ai/plan.md` 파일을 편집:

```markdown
# 구현 계획: AI 챗봇 에이전트

**브랜치**: `001-ai-chatbot-agent` | **날짜**: 2024-12-08 | **명세서**: [spec.md](./spec.md)

## 요약
CLI를 통해 사용자와 대화할 수 있는 AI 챗봇 에이전트를 구현합니다. OpenAI GPT 모델을 백엔드로 사용하며, 로컬 파일 시스템에 대화 히스토리를 저장합니다.

## 기술 컨텍스트
**언어/버전**: Python 3.11  
**주요 종속성**: Click, OpenAI, Pydantic  
**AI 모델**: OpenAI GPT-4  
**저장소**: JSON 파일 (대화 히스토리)  
**테스트**: pytest  
**대상 플랫폼**: Linux 서버  
**프로젝트 유형**: single  
**성능 목표**: 5초 이내 응답  
**제약사항**: 오프라인 모드 지원 없음  
**규모/범위**: 단일 사용자, 로컬 사용

## 헌법 체크

**단순성**:
- 프로젝트 수: 1 (cli + lib)
- 프레임워크 직접 사용? ✅ (Click 직접 사용)
- 단일 데이터 모델? ✅ (Message, Session 모델만)

**아키텍처**:
- 모든 기능을 에이전트로? ✅ (ChatAgent 클래스)
- 에이전트별 CLI: `vibe-agents chatbot --chat`, `--history`
- 에이전트 문서: llms.txt 형식 계획 ✅

**테스트 (비협상적)**:
- RED-GREEN-Refactor 사이클 강제? ✅
- Contract→Integration→E2E→Unit 순서? ✅
- 실제 종속성 사용? ✅ (실제 OpenAI API 테스트 환경)
```

### 4단계: 작업 목록 생성

```bash
# 전제조건 확인
./scripts/check-task-prerequisites.sh

# 작업 목록 템플릿 복사
cp templates/tasks-template.md specs/001-ai/tasks.md
```

`specs/001-ai/tasks.md`를 편집하여 구체적인 작업 정의:

```markdown
# 작업 목록: AI 챗봇 에이전트

## 단계 3.1: 설정
- [ ] T001 프로젝트 구조 생성 (src/vibe_agents/chatbot/)
- [ ] T002 Python 패키지 의존성 추가 (click, openai, pydantic)
- [ ] T003 [P] 린팅 설정 (black, isort, flake8)

## 단계 3.2: 테스트 우선 (TDD)
- [ ] T004 [P] 채팅 기능 계약 테스트 작성 (tests/contract/test_chat_api.py)
- [ ] T005 [P] 히스토리 조회 통합 테스트 작성 (tests/integration/test_history.py)
- [ ] T006 [P] 에이전트 응답 통합 테스트 작성 (tests/integration/test_agent_response.py)

## 단계 3.3: 핵심 구현 (테스트가 실패한 후에만)
- [ ] T007 [P] Message 모델 구현 (src/vibe_agents/chatbot/models.py)
- [ ] T008 [P] ChatAgent 클래스 구현 (src/vibe_agents/chatbot/agent.py)
- [ ] T009 [P] 히스토리 저장/로드 서비스 (src/vibe_agents/chatbot/storage.py)
- [ ] T010 CLI 명령 구현 (src/vibe_agents/chatbot/cli.py)
- [ ] T011 OpenAI API 통합
- [ ] T012 오류 처리 및 로깅

## 단계 3.4: 통합
- [ ] T013 ChatAgent와 저장소 연결
- [ ] T014 CLI와 에이전트 연결
- [ ] T015 구성 파일 지원 (API 키 등)

## 단계 3.5: 마무리
- [ ] T016 [P] 단위 테스트 (tests/unit/test_models.py)
- [ ] T017 성능 테스트 (5초 이내 응답 확인)
- [ ] T018 [P] 사용자 문서 작성
- [ ] T019 수동 테스트 시나리오 실행
```

### 5단계: 구현 시작

이제 TDD 원칙에 따라 구현을 시작합니다:

```bash
# 테스트부터 작성
touch tests/contract/test_chat_api.py
# 테스트가 실패하는 것을 확인한 후
# 구현 시작
touch src/vibe_agents/chatbot/models.py
```

## 📋 체크리스트

이 예제를 따라하면서 확인할 사항들:

- [ ] 새 브랜치가 생성되었나요?
- [ ] 명세서에 기술적 세부사항이 없나요?
- [ ] 모든 요구사항이 테스트 가능한가요?
- [ ] 헌법 원칙을 준수하고 있나요?
- [ ] 테스트를 먼저 작성하고 있나요?

## 🎯 다음 단계

이 예제를 완료한 후:

1. 더 복잡한 에이전트 구현해보기
2. 다중 에이전트 시스템 설계
3. 웹 인터페이스 추가
4. 다른 AI 모델 통합

## 💡 팁

- 명세서 작성 시 "사용자가 왜 이것을 원하는가?"를 항상 생각하세요
- 구현하기 전에 반드시 테스트를 작성하세요
- 복잡해지면 헌법을 다시 읽어보세요
- 각 단계마다 커밋하여 진행 상황을 추적하세요