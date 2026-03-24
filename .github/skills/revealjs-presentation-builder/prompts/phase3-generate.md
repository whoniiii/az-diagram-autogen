# Phase 3: 콘텐츠 생성

## 목적
Phase 2에서 확정된 슬라이드 구조를 바탕으로 실제 HTML 파일과 필요 시 부속 문서를 생성한다.

## 파일 생성 전략

### 프레젠테이션 HTML (필수)
- **25장 이하**: 직접 `create` 도구로 생성
- **25장 이상**: `task` (general-purpose) 서브에이전트에 위임

### 부속 문서 (사용자 요청 시에만)
- 핸드아웃, 참고 자료, 실습 가이드 등
- 사용자가 명시적으로 요청한 경우에만 생성
- `task` (general-purpose) 서브에이전트에 위임하여 병렬 생성

## 서브에이전트 프롬프트 템플릿

서브에이전트에게 전달할 프롬프트는 반드시 다음을 포함:

### 1. 기술 스택 지정
```
- reveal.js 5.x CDN: https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/
- Mermaid.js CDN: https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
- highlight.js: reveal.js 내장 플러그인 (monokai 테마)
- standalone HTML 파일 하나
```

### 2. 디자인 시스템 포함
`references/design-system.md`의 **전체 CSS**를 프롬프트에 포함한다.
축약하지 않고 CSS 코드 블록 전체를 넣는다.

### 3. 슬라이드 내용 상세 기술
Phase 2에서 설계한 구조를 기반으로 **각 슬라이드의 내용을 구체적으로** 기술한다.

```
## Section 2: {섹션명}
- Slide: {제목} — {상세 내용, 포함할 텍스트, Mermaid 코드, 비교표 데이터 등}
```

**🚨 핵심**: 슬라이드 내용이 구체적일수록 결과물 품질이 높다.
추상적 지시 ❌ → 구체적 내용 + 표현 형식 ✅

### 4. 필수 지시사항 (항상 포함)
```
## 중요 지시사항
1. 파일을 하나의 완전한 standalone HTML로 만들어줘
2. 모든 슬라이드를 생략 없이 작성해줘. 절대로 "..." 이나 "이하 생략" 하지 마라
3. Mermaid는 reveal.js 초기화 후 렌더링해줘
4. 코드 블록에는 적절한 언어 태그를 넣어줘
5. 이미지는 상대경로로 참조해줘
6. 슬라이드 번호 표시: slideNumber: 'c/t'
7. fragment 애니메이션으로 progressive disclosure 사용
```

## 병렬 생성

산출물이 여러 파일일 경우, `task` 에이전트를 병렬로 실행:

```
# 동시에 병렬 실행
task(general-purpose): 프레젠테이션 HTML 생성
task(general-purpose): 부속 문서 생성 (요청 시)
```

## Phase 3 완료 조건

- [ ] index.html 생성됨
- [ ] (요청 시) 부속 문서 생성됨
- [ ] 모든 파일의 존재 및 크기 확인
