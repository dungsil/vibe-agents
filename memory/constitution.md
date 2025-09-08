# Vibe Agents Constitution
<!-- AI 에이전트 바이브코딩 실험 프로젝트 헌법 -->

## Core Principles

### I. Agent-First Development
모든 기능은 독립적인 AI 에이전트로 시작해야 합니다.
- 에이전트는 자체 완결적이고, 독립적으로 테스트 가능하며, 문서화되어야 합니다
- 명확한 목적이 필요하며, 조직적 목적만을 위한 에이전트는 금지됩니다
- 각 에이전트는 특정 도메인이나 기능에 집중해야 합니다

### II. CLI Interface
모든 에이전트는 CLI를 통해 기능을 노출해야 합니다.
- 텍스트 입출력 프로토콜: stdin/args → stdout, errors → stderr
- JSON 및 사람이 읽을 수 있는 형식을 지원해야 합니다
- 모든 에이전트는 --help, --version, --format 옵션을 제공해야 합니다

### III. Test-First (비협상적)
TDD는 필수입니다: 테스트 작성 → 사용자 승인 → 테스트 실패 → 구현
- Red-Green-Refactor 사이클을 엄격히 따라야 합니다
- 구현 전 테스트, RED 단계 건너뛰기 금지
- Git 커밋은 구현 전 테스트를 보여줘야 합니다

### IV. Integration Testing
통합 테스트가 필요한 핵심 영역:
- 새로운 에이전트 컨트랙트 테스트
- 컨트랙트 변경사항
- 에이전트 간 통신
- 공유 스키마 및 데이터 모델

### V. Observability
텍스트 I/O로 디버깅 가능성을 보장합니다.
- 구조화된 로깅이 필요합니다
- 프론트엔드 로그 → 백엔드 (통합 스트림)
- 충분한 오류 컨텍스트 제공

### VI. Versioning & Breaking Changes
MAJOR.MINOR.BUILD 형식을 사용합니다.
- 모든 변경 시 BUILD 번호 증가
- 중단적 변경 처리 (병렬 테스트, 마이그레이션 계획)

### VII. Simplicity
단순함부터 시작하고, YAGNI 원칙을 따릅니다.
- 초기 구현 시 최대 3개 프로젝트
- 추가 프로젝트는 문서화된 정당화 필요
- 프레임워크를 직접 사용 (래퍼 클래스 금지)

## AI Agents Specific Constraints

### Agent Architecture
- 각 에이전트는 명확한 책임과 경계를 가져야 합니다
- 에이전트 간 통신은 표준화된 메시지 형식을 사용해야 합니다
- 상태 관리는 외부 저장소를 통해 수행해야 합니다

### Prompt Engineering
- 모든 프롬프트는 버전 관리되어야 합니다
- 프롬프트 템플릿은 재사용 가능해야 합니다
- A/B 테스트 가능한 프롬프트 구조를 유지해야 합니다

### Model Integration
- LLM 모델에 종속되지 않는 구조여야 합니다
- 모델 전환이 가능한 어댑터 패턴을 사용해야 합니다
- 모델별 성능 메트릭을 수집해야 합니다

## Development Workflow

### Spec-Driven Development
- 모든 에이전트는 명세서부터 시작해야 합니다
- 구현 계획이 명세서를 따라야 합니다
- 코드는 명세서의 표현이어야 합니다

### Experimentation Framework
- 모든 실험은 가설과 성공 메트릭을 가져야 합니다
- 실험 결과는 문서화되고 공유되어야 합니다
- 실패한 실험도 학습으로 기록해야 합니다

### Quality Gates
- 모든 PR/리뷰는 헌법 준수를 확인해야 합니다
- 복잡성은 정당화되어야 합니다
- 운영 시 개발 지침은 `/memory/constitution.md`를 따라야 합니다

## Governance

헌법은 모든 다른 관행보다 우선합니다.
- 수정안은 문서화, 승인, 마이그레이션 계획이 필요합니다
- 모든 PR/리뷰는 준수를 확인해야 합니다
- 복잡성은 정당화되어야 합니다

**Version**: 1.0.0 | **Ratified**: 2024-12-08 | **Last Amended**: 2024-12-08