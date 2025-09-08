# 작업 목록: [기능 이름]

**입력**: `/specs/[###-feature-name]/`의 설계 문서
**전제조건**: plan.md (필수), research.md, data-model.md, contracts/

## 실행 흐름 (main)
```
1. 기능 디렉터리에서 plan.md 로드
   → 찾을 수 없으면: ERROR "구현 계획을 찾을 수 없음"
   → 추출: 기술 스택, 라이브러리, 구조
2. 선택적 설계 문서 로드:
   → data-model.md: 엔티티 추출 → 모델 작업
   → contracts/: 각 파일 → 계약 테스트 작업
   → research.md: 결정사항 추출 → 설정 작업
3. 카테고리별 작업 생성:
   → 설정: 프로젝트 초기화, 종속성, 린팅
   → 테스트: 계약 테스트, 통합 테스트
   → 핵심: 모델, 서비스, CLI 명령
   → 통합: DB, 미들웨어, 로깅
   → 마무리: 단위 테스트, 성능, 문서
4. 작업 규칙 적용:
   → 다른 파일 = 병렬 실행을 위해 [P] 표시
   → 같은 파일 = 순차 실행 ([P] 없음)
   → 구현 전 테스트 (TDD)
5. 작업을 순차적으로 번호 매기기 (T001, T002...)
6. 종속성 그래프 생성
7. 병렬 실행 예시 생성
8. 작업 완전성 검증:
   → 모든 계약에 테스트가 있는가?
   → 모든 엔티티에 모델이 있는가?
   → 모든 엔드포인트가 구현되었는가?
9. 반환: SUCCESS (작업 실행 준비 완료)
```

## 형식: `[ID] [P?] 설명`
- **[P]**: 병렬 실행 가능 (다른 파일, 종속성 없음)
- 설명에 정확한 파일 경로 포함

## 경로 규칙
- **단일 프로젝트**: 저장소 루트의 `src/`, `tests/`
- **웹 앱**: `backend/src/`, `frontend/src/`
- **모바일**: `api/src/`, `ios/src/` 또는 `android/src/`
- **AI 에이전트**: `core/src/`, `interface/src/`
- 아래 경로는 단일 프로젝트를 가정 - plan.md 구조에 따라 조정

## 단계 3.1: 설정
- [ ] T001 구현 계획에 따른 프로젝트 구조 생성
- [ ] T002 [프레임워크] 종속성으로 [언어] 프로젝트 초기화
- [ ] T003 [P] 린팅 및 포맷팅 도구 구성

## 단계 3.2: 테스트 우선 (TDD) ⚠️ 3.3 전에 반드시 완료
**중요: 이 테스트들은 반드시 작성되어야 하고 모든 구현 전에 반드시 실패해야 함**
- [ ] T004 [P] tests/contract/test_agents_post.py에서 POST /api/agents 계약 테스트
- [ ] T005 [P] tests/contract/test_agents_get.py에서 GET /api/agents/{id} 계약 테스트
- [ ] T006 [P] tests/integration/test_agent_creation.py에서 에이전트 생성 통합 테스트
- [ ] T007 [P] tests/integration/test_agent_execution.py에서 에이전트 실행 흐름 통합 테스트

## 단계 3.3: 핵심 구현 (테스트가 실패한 후에만)
- [ ] T008 [P] src/models/agent.py에 에이전트 모델
- [ ] T009 [P] src/services/agent_service.py에 AgentService CRUD
- [ ] T010 [P] src/cli/agent_commands.py에 CLI --create-agent
- [ ] T011 POST /api/agents 엔드포인트
- [ ] T012 GET /api/agents/{id} 엔드포인트
- [ ] T013 입력 검증
- [ ] T014 오류 처리 및 로깅

## 단계 3.4: 통합
- [ ] T015 AgentService를 DB에 연결
- [ ] T016 인증 미들웨어
- [ ] T017 요청/응답 로깅
- [ ] T018 CORS 및 보안 헤더

## 단계 3.5: 마무리
- [ ] T019 [P] tests/unit/test_validation.py에서 검증 단위 테스트
- [ ] T020 성능 테스트 (<200ms)
- [ ] T021 [P] docs/api.md 업데이트
- [ ] T022 중복 제거
- [ ] T023 manual-testing.md 실행

## 종속성
- 구현(T008-T014) 전에 테스트(T004-T007)
- T008이 T009, T015를 차단
- T016이 T018을 차단
- 마무리(T019-T023) 전에 구현

## 병렬 실행 예시
```
# T004-T007을 함께 실행:
작업: "tests/contract/test_agents_post.py에서 POST /api/agents 계약 테스트"
작업: "tests/contract/test_agents_get.py에서 GET /api/agents/{id} 계약 테스트"
작업: "tests/integration/test_agent_creation.py에서 에이전트 생성 통합 테스트"
작업: "tests/integration/test_agent_execution.py에서 에이전트 실행 통합 테스트"
```

## 주의사항
- [P] 작업 = 다른 파일, 종속성 없음
- 구현 전 테스트 실패 확인
- 각 작업 후 커밋
- 피해야 할 것: 모호한 작업, 같은 파일 충돌

## 작업 생성 규칙
*main() 실행 중 적용됨*

1. **계약에서**:
   - 각 계약 파일 → 계약 테스트 작업 [P]
   - 각 엔드포인트 → 구현 작업
   
2. **데이터 모델에서**:
   - 각 엔티티 → 모델 생성 작업 [P]
   - 관계 → 서비스 레이어 작업
   
3. **사용자 스토리에서**:
   - 각 스토리 → 통합 테스트 [P]
   - 빠른 시작 시나리오 → 검증 작업

4. **순서**:
   - 설정 → 테스트 → 모델 → 서비스 → 엔드포인트 → 마무리
   - 종속성이 병렬 실행을 차단

## 검증 체크리스트
*게이트: 반환 전에 main()에서 확인*

- [ ] 모든 계약에 해당 테스트가 있음
- [ ] 모든 엔티티에 모델 작업이 있음
- [ ] 모든 테스트가 구현 전에 있음
- [ ] 병렬 작업이 실제로 독립적임
- [ ] 각 작업이 정확한 파일 경로를 명시함
- [ ] 다른 [P] 작업과 같은 파일을 수정하는 작업이 없음