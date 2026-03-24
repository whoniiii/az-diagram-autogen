# reveal.js Presentation Builder

자연어로 요청하면 **프로페셔널 HTML 프레젠테이션**을 자동 생성하는 범용 Copilot 스킬입니다.
기술 발표, 제안서, 보고서, 교육, 피칭 등 **모든 용도**에 사용할 수 있습니다.

## 🚀 사용법

Copilot에게 다음과 같이 말하면 자동으로 이 스킬이 활성화됩니다:

```
"프레젠테이션 만들어줘"
"Kubernetes 소개 발표자료 만들어줘"
"고객 제안서 슬라이드 만들어줘"
"프로젝트 킥오프 자료 만들어줘"
"컨퍼런스 발표 슬라이드 만들어줘"
```

## ✨ 특징

- **범용 프레젠테이션 도구** — 기술 발표, 제안서, 보고서, 교육, 피칭 등 용도 불문
- **GitHub Dark 디자인** — 프로페셔널 다크 테마, 일관된 컬러 시스템
- **Mermaid.js 다이어그램** — 아키텍처, 흐름도, 시퀀스 다이어그램 자동 렌더링
- **코드 하이라이팅** — Python, TypeScript, YAML 등 syntax highlighting
- **12가지 슬라이드 패턴** — title, concept, diagram, comparison, code, columns, checklist 등
- **용도별 추천 구조** — 기술 발표, 제안서, 피칭, 교육, 킥오프 등 5가지 템플릿 내장

## 📁 스킬 구조

```
revealjs-presentation-builder/
├── SKILL.md                          # 스킬 정의 & 워크플로
├── README.md                         # 이 파일
├── prompts/
│   ├── phase1-requirements.md        # 요구사항 수집
│   ├── phase2-design.md              # 슬라이드 구조 설계
│   ├── phase3-generate.md            # HTML/MD 콘텐츠 생성
│   └── phase4-review.md              # 검증 & 수정
└── references/
    ├── design-system.md              # CSS 디자인 시스템 (컬러, 클래스)
    └── slide-patterns.md             # 12가지 슬라이드 HTML 패턴
```

## 🎨 디자인 시스템 미리보기

| 요소 | 스타일 |
|------|--------|
| 배경 | GitHub Dark (#0d1117) |
| 제목 | Blue (#58a6ff) with glow |
| 강조 | Orange (#f0883e) |
| 성공 | Green (#3fb950) |
| 경고 | Red (#f85149) |
| 카드 | Dark card with colored left border |
| 태그 | Rounded pill badges |
| 코드 | Monokai theme, rounded corners |

## 📋 워크플로

```
Phase 1: 요구사항 수집 (주제, 대상, 시간, 형식)
    ↓
Phase 2: 슬라이드 구조 설계 (섹션별 슬라이드 구성)
    ↓
Phase 3: HTML/MD 콘텐츠 생성 (서브에이전트 병렬 실행)
    ↓
Phase 4: 검증 & 수정 (파일 확인, 사용자 피드백)
```
