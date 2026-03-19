# azure-arch-builder (GHCP Edition)

> Azure AI/Data 인프라를 자연어로 설계하고 자동 배포까지 이어주는 GitHub Copilot CLI 스킬

"AI Search랑 Foundry 만들고 싶어" 라고 말하면, 대화를 통해 아키텍처를 확정하고 Bicep 코드 생성부터 실제 Azure 배포까지 자동으로 진행합니다.

> **Note**: 이 버전은 GitHub Copilot CLI (GHCP) 환경에 최적화되어 있습니다.
> Claude Code CLI용 원본은 `.claude/skills/azure-arch-builder`에 있습니다.

---

## 설치

### 프로젝트 스킬 (현재 프로젝트만)

프로젝트 루트의 `.github/skills/` 폴더에 배치합니다:

```
your-project/
└── .github/
    └── skills/
        └── azure-arch-builder/
            ├── SKILL.md
            ├── agents/
            ├── references/
            └── scripts/
```

### 개인 스킬 (모든 프로젝트에서 사용)

```powershell
# 홈 디렉토리 기준
New-Item -ItemType Directory -Path "$env:USERPROFILE\.copilot\skills" -Force
git clone https://github.com/whoniiii/az_work "$env:USERPROFILE\.copilot\skills\azure-arch-builder"
```

---

## 사용법

설치 후 프로젝트 폴더에서 GitHub Copilot CLI를 실행합니다:

```powershell
cd your-project
copilot
```

Azure 인프라 관련 요청을 하면 스킬이 자동으로 발동됩니다:

```
"AI Search랑 Microsoft Foundry 만들어줘, private endpoint 포함해서"
"RAG 챗봇 아키텍처 구성해줘"
"Azure에 데이터 레이크하우스 올려줘"
```

### 스킬 확인

```
/skills list
```

---

## Claude Code CLI 버전과의 차이점

| 항목 | Claude Code CLI | GHCP |
|------|----------------|------|
| 스킬 위치 | `.claude/skills/` | `.github/skills/` 또는 `~/.copilot/skills/` |
| URL 조회 | `WebFetch` | `web_fetch` |
| 웹 검색 | `WebSearch` | `web_search` |
| 사용자 질문 | `AskUserQuestion` (복수 질문, 옵션 description) | `ask_user` (단일 질문, 문자열 배열 선택지) |
| 서브에이전트 | `Agent` | `task` (agent_type 지정) |
| 셸 환경 | Bash | PowerShell |
| 파일 링크 | `computer://` 프로토콜 | 파일 경로 직접 안내 |
| 도구 사전 로드 | `ToolSearch` 필요 | 불필요 (항상 사용 가능) |

---

## 특징

- **최신 정보 기반**: API 버전, 서비스 명칭, 속성 등을 MS Docs에서 실시간 확인하여 적용
- **보안 우선**: Private Endpoint, 민감 정보 파일 저장 금지 등 보안 원칙 내장
- **대화형 설계**: 사용자와 대화하며 점진적으로 아키텍처 확정
- **단계별 승인**: 모든 주요 단계에서 사용자 확인 후 진행
- **GHCP 네이티브**: PowerShell 셸, ask_user 도구 등 GHCP 환경에 맞게 최적화

---

## 사전 요구사항

- [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) 설치
- Azure CLI (`az`) 설치 및 로그인 (`az login`)
- Python 3 (다이어그램 생성용)

---

## 라이선스

MIT
