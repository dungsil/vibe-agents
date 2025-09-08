# 🤖 Vibe Agents

**AI 에이전트 바이브코딩 실험 프로젝트**

AI 에이전트 개발을 위한 명세 주도 개발(Spec-Driven Development) 환경입니다.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/dungsil/vibe-agents)

---

## 📖 목차

- [🤔 명세 주도 개발이란?](#-명세-주도-개발이란)
- [⚡ 빠른 시작](#-빠른-시작)
- [📚 핵심 철학](#-핵심-철학)
- [🌟 개발 단계](#-개발-단계)
- [🔧 전제 조건](#-전제-조건)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [🛠️ 워크플로우](#️-워크플로우)
- [📖 자세히 알아보기](#-자세히-알아보기)

## 🤔 명세 주도 개발이란?

명세 주도 개발(Spec-Driven Development)은 **전통적인 소프트웨어 개발 방식을 뒤바꿉니다**. 수십 년 동안 코드가 왕이었습니다. 명세서는 "실제 작업"인 코딩이 시작되면 버려지는 비계에 불과했습니다. 명세 주도 개발은 이를 바꿉니다: **명세서가 실행 가능**해져서 단순히 안내하는 것이 아니라 직접 구현을 생성합니다.

## ⚡ 빠른 시작

### 1. 프로젝트 구조 확인

이 저장소는 이미 명세 주도 개발을 위한 기본 구조를 가지고 있습니다:

```
vibe-agents/
├── memory/              # 헌법 및 거버넌스 문서
├── scripts/             # 자동화 스크립트
├── templates/           # 명세서, 계획, 작업 템플릿
├── specs/               # 기능 명세서가 저장될 위치
└── src/                 # 소스 코드 (명세서에서 생성)
```

### 2. 새 기능 명세서 생성

새로운 기능을 시작하려면:

```bash
# 새 기능 브랜치와 명세서 생성
./scripts/create-new-feature.sh "AI 채팅 에이전트 생성"
```

이렇게 하면 다음이 생성됩니다:
- 새 브랜치 (예: `001-ai-chat-agent`)
- `specs/001-ai-chat-agent/` 디렉터리
- 기본 명세서 템플릿

### 3. 명세서 작성

생성된 `specs/001-ai-chat-agent/spec.md` 파일을 편집하여:
- **무엇을** 구축할 것인지와 **왜** 구축하는지에 집중
- 기술 스택에 대해서는 걱정하지 말 것

### 4. 구현 계획 생성

명세서가 준비되면:

```bash
# 구현 계획 설정
./scripts/setup-plan.sh
```

그리고 `specs/001-ai-chat-agent/plan.md`에서 기술 스택과 아키텍처 선택을 정의합니다.

## 📚 핵심 철학

명세 주도 개발은 다음을 강조하는 구조화된 프로세스입니다:

- **의도 주도 개발**: "어떻게" 전에 "무엇을"과 "왜"를 정의하는 명세서
- **풍부한 명세서 생성**: 가드레일과 조직 원칙 사용
- **다단계 개선**: 프롬프트에서 일회성 코드 생성이 아닌 점진적 접근
- **고급 AI 모델 기능에 대한 강한 의존**: 명세서 해석을 위한 AI 활용

## 🌟 개발 단계

| 단계 | 초점 | 주요 활동 |
|------|------|-----------|
| **0-to-1 개발** ("그린필드") | 처음부터 생성 | <ul><li>고수준 요구사항으로 시작</li><li>명세서 생성</li><li>구현 단계 계획</li><li>프로덕션 준비 애플리케이션 구축</li></ul> |
| **창의적 탐색** | 병렬 구현 | <ul><li>다양한 솔루션 탐색</li><li>여러 기술 스택 및 아키텍처 지원</li><li>UX 패턴 실험</li></ul> |
| **반복적 개선** ("브라운필드") | 기존 시스템 현대화 | <ul><li>반복적으로 기능 추가</li><li>레거시 시스템 현대화</li><li>프로세스 적응</li></ul> |

## 🔧 전제 조건

- **Linux/macOS** (또는 Windows의 WSL2)
- AI 코딩 에이전트: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), 또는 [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [Python 3.11+](https://www.python.org/downloads/) 또는 선호하는 개발 언어
- [Git](https://git-scm.com/downloads)

## 📁 프로젝트 구조

### 핵심 디렉터리

```
vibe-agents/
├── memory/                          # 거버넌스 및 헌법
│   ├── constitution.md              # 핵심 원칙 및 규칙
│   └── constitution_update_checklist.md
├── scripts/                         # 자동화 스크립트
│   ├── common.sh                    # 공통 유틸리티
│   ├── create-new-feature.sh        # 새 기능 생성
│   ├── setup-plan.sh               # 구현 계획 설정
│   ├── get-feature-paths.sh         # 경로 관리
│   └── check-task-prerequisites.sh  # 준비 상태 검증
├── templates/                       # 명세서 및 계획 템플릿
│   ├── spec-template.md             # 기능 명세서 템플릿
│   ├── plan-template.md             # 구현 계획 템플릿
│   └── tasks-template.md            # 작업 분해 템플릿
├── specs/                           # 기능 명세서
│   └── [###-feature-name]/
│       ├── spec.md                  # 기능 명세서
│       ├── plan.md                  # 구현 계획
│       ├── tasks.md                 # 작업 목록
│       ├── research.md              # 연구 결과
│       ├── data-model.md            # 데이터 모델
│       ├── quickstart.md            # 빠른 시작 가이드
│       └── contracts/               # API 계약
└── src/                            # 소스 코드 (명세서에서 생성)
```

## 🛠️ 워크플로우

### 1단계: 명세서 생성
```bash
# 새 기능 생성
./scripts/create-new-feature.sh "AI 에이전트 대화 기능"

# AI 에이전트에게 명세서 작성 요청
# 예: "/specify AI 에이전트가 사용자와 자연어로 대화할 수 있는 기능을 구축하세요"
```

### 2단계: 기술 계획 생성
```bash
# 구현 계획 설정
./scripts/setup-plan.sh

# AI 에이전트에게 기술 스택 정의 요청
# 예: "/plan Python과 FastAPI를 사용하여 구현하고, OpenAI GPT-4를 백엔드로 사용하세요"
```

### 3단계: 작업 분해 및 구현
```bash
# 작업 준비 상태 확인
./scripts/check-task-prerequisites.sh

# AI 에이전트에게 작업 목록 생성 요청
# 예: "/tasks 구현 계획을 기반으로 실행 가능한 작업 목록을 생성하세요"
```

### 4단계: 헌법 준수 확인

모든 구현은 `/memory/constitution.md`에 정의된 원칙을 따라야 합니다:

- **에이전트 우선**: 모든 기능은 독립적인 에이전트로 시작
- **CLI 인터페이스**: 모든 에이전트는 CLI를 통해 접근 가능
- **테스트 우선**: 구현 전 반드시 테스트 작성
- **관찰성**: 텍스트 I/O로 디버깅 가능성 보장
- **단순성**: YAGNI 원칙 준수

## 📖 자세히 알아보기

- **[워크플로우 가이드](./docs/workflow.md)** - 상세한 단계별 개발 프로세스
- **[빠른 시작 예제](./docs/quickstart.md)** - 첫 번째 AI 에이전트 만들기
- **[헌법](./memory/constitution.md)** - 프로젝트의 핵심 원칙과 규칙
- **[명세서 템플릿](./templates/spec-template.md)** - 기능 명세서 작성 가이드
- **[구현 계획 템플릿](./templates/plan-template.md)** - 기술 구현 계획 가이드

---

## 🤝 기여하기

이 프로젝트는 명세 주도 개발 방법론을 실험하는 공간입니다. 기여를 환영합니다!

1. 새 기능은 항상 명세서부터 시작하세요
2. 헌법의 원칙을 따라주세요
3. 모든 변경사항은 테스트와 함께 제출하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

이 프로젝트는 [GitHub의 spec-kit](https://github.com/github/spec-kit)에서 영감을 받았습니다.
