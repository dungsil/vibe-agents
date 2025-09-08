# Spec-Driven Development 워크플로우 가이드

이 문서는 vibe-agents 프로젝트에서 명세 주도 개발(Spec-Driven Development)을 실제로 활용하는 방법을 상세히 설명합니다.

## 🎯 개요

명세 주도 개발은 다음 단계를 따릅니다:
1. **명세서 작성**: 무엇을 구축할지와 왜 구축하는지 정의
2. **기술 계획**: 어떻게 구축할지 기술 스택과 아키텍처 결정
3. **작업 분해**: 구현 가능한 작업들로 세분화
4. **구현**: 테스트 우선 개발로 실제 코드 작성

## 📋 단계별 가이드

### 1단계: 새 기능 시작

```bash
# 새 기능 브랜치와 명세서 생성
./scripts/create-new-feature.sh "AI 챗봇 에이전트 구현"
```

이 명령은:
- 자동으로 기능 번호를 할당 (001, 002, ...)
- 새 Git 브랜치 생성 (예: `001-ai-chatbot-agent`)
- `specs/001-ai-chatbot-agent/` 디렉터리 생성
- 명세서 템플릿 복사

### 2단계: 명세서 작성

생성된 `specs/001-ai-chatbot-agent/spec.md` 파일을 편집:

```markdown
# 기능 명세서: AI 챗봇 에이전트

## 사용자 시나리오 & 테스트

### 주요 사용자 스토리
사용자가 자연어로 질문을 입력하면, AI 에이전트가 적절한 답변을 생성하여 응답합니다.

### 수용 시나리오
1. **Given** 사용자가 "안녕하세요"라고 입력, **When** 에이전트가 처리, **Then** 친근한 인사말로 응답
2. **Given** 사용자가 복잡한 질문 입력, **When** 에이전트가 처리, **Then** 구조화된 답변 제공

## 요구사항

### 기능 요구사항
- **FR-001**: 시스템은 사용자의 텍스트 입력을 받아야 함
- **FR-002**: 시스템은 AI 모델을 통해 응답을 생성해야 함
- **FR-003**: 시스템은 대화 히스토리를 유지해야 함
- **FR-004**: 시스템은 CLI 인터페이스를 제공해야 함
```

**중요 원칙:**
- **무엇**과 **왜**에 집중
- 기술 스택이나 구현 방법은 언급하지 않음
- 모든 요구사항이 테스트 가능해야 함

### 3단계: 구현 계획 생성

```bash
# 구현 계획 템플릿 설정
./scripts/setup-plan.sh
```

생성된 `specs/001-ai-chatbot-agent/plan.md` 파일을 편집:

```markdown
# 구현 계획: AI 챗봇 에이전트

## 기술 컨텍스트
**언어/버전**: Python 3.11
**주요 종속성**: FastAPI, OpenAI, Pydantic
**AI 모델**: OpenAI GPT-4
**저장소**: SQLite (대화 히스토리)
**테스트**: pytest
**대상 플랫폼**: Linux 서버
**프로젝트 유형**: single
```

### 4단계: 헌법 준수 확인

계획이 `/memory/constitution.md`의 원칙을 따르는지 확인:

```markdown
## 헌법 체크

**단순성**:
- 프로젝트 수: 1 (cli만)
- 프레임워크 직접 사용? ✅
- 단일 데이터 모델? ✅

**아키텍처**:
- 모든 기능을 에이전트로? ✅
- 에이전트별 CLI: chatbot --chat, --history
- 에이전트 문서: llms.txt 형식 계획 ✅

**테스트 (비협상적)**:
- RED-GREEN-Refactor 사이클 강제? ✅
- Contract→Integration→E2E→Unit 순서? ✅
- 실제 종속성 사용? ✅
```

### 5단계: 설계 문서 생성

계획에 따라 필요한 설계 문서들을 생성:

```bash
# 연구 문서
touch specs/001-ai-chatbot-agent/research.md

# 데이터 모델
touch specs/001-ai-chatbot-agent/data-model.md

# API 계약
mkdir -p specs/001-ai-chatbot-agent/contracts

# 빠른 시작 가이드
touch specs/001-ai-chatbot-agent/quickstart.md
```

### 6단계: 작업 목록 생성

```bash
# 작업 전제조건 확인
./scripts/check-task-prerequisites.sh

# 작업 목록 템플릿 복사 (수동)
cp templates/tasks-template.md specs/001-ai-chatbot-agent/tasks.md
```

`tasks.md`를 편집하여 구체적인 작업들을 정의:

```markdown
## 단계 3.2: 테스트 우선 (TDD)
- [ ] T004 [P] 채팅 API 계약 테스트 작성
- [ ] T005 [P] 대화 히스토리 통합 테스트 작성

## 단계 3.3: 핵심 구현
- [ ] T008 [P] ChatAgent 모델 구현
- [ ] T009 [P] ChatService 구현
- [ ] T010 [P] CLI 인터페이스 구현
```

### 7단계: 구현 실행

헌법의 원칙에 따라 TDD로 구현:

1. **테스트 먼저 작성**
2. **테스트가 실패하는 것 확인** (RED)
3. **최소한의 코드로 테스트 통과** (GREEN)
4. **리팩터링** (REFACTOR)

## 🔧 스크립트 활용법

### create-new-feature.sh
새 기능을 시작할 때 사용:
```bash
./scripts/create-new-feature.sh "기능 설명"
./scripts/create-new-feature.sh --json "기능 설명"  # JSON 출력
```

### setup-plan.sh
구현 계획을 설정할 때 사용:
```bash
./scripts/setup-plan.sh
./scripts/setup-plan.sh --json  # JSON 출력
```

### check-task-prerequisites.sh
작업 생성 전 준비 상태 확인:
```bash
./scripts/check-task-prerequisites.sh
./scripts/check-task-prerequisites.sh --json  # JSON 출력
```

### get-feature-paths.sh
현재 기능의 경로 정보 확인:
```bash
./scripts/get-feature-paths.sh
```

## 📂 디렉터리 구조 이해

```
specs/001-feature-name/
├── spec.md              # 기능 명세서 (필수)
├── plan.md              # 구현 계획 (필수)
├── tasks.md             # 작업 목록
├── research.md          # 연구 결과
├── data-model.md        # 데이터 모델
├── quickstart.md        # 빠른 시작 가이드
└── contracts/           # API 계약서
    ├── chat-api.yaml
    └── history-api.yaml
```

## 🎯 모범 사례

### 명세서 작성 시
- ✅ 사용자 가치에 집중
- ✅ 명확하고 테스트 가능한 요구사항
- ❌ 기술적 구현 세부사항 포함 금지
- ❌ 추측이나 가정 금지 → [명확화 필요] 표시

### 계획 작성 시
- ✅ 헌법 원칙 준수
- ✅ 복잡성 정당화
- ✅ 테스트 우선 접근법
- ❌ 과도한 추상화나 미래 대비

### 구현 시
- ✅ RED-GREEN-REFACTOR 사이클
- ✅ 각 작업 후 커밋
- ✅ CLI 인터페이스 제공
- ❌ 테스트 없는 구현

## 🔗 추가 자료

- [헌법](../memory/constitution.md): 프로젝트 원칙과 규칙
- [명세서 템플릿](../templates/spec-template.md): 명세서 작성 가이드
- [계획 템플릿](../templates/plan-template.md): 구현 계획 가이드
- [작업 템플릿](../templates/tasks-template.md): 작업 분해 가이드