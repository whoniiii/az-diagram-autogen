# Phase 4: 검증 & 수정

## 목적
생성된 파일을 검증하고, 사용자의 수정 요청을 처리한다.

## 검증 체크리스트

### 1. 파일 존재 확인
```powershell
# 모든 생성된 파일의 존재 및 크기 확인
Get-Item presentation\index.html | Select-Object Name, Length
Get-ChildItem labs\*.md | Select-Object Name, Length
Get-ChildItem docs\*.md | Select-Object Name, Length
```

### 2. HTML 구조 검증
- `<!DOCTYPE html>` 로 시작하는지
- reveal.js CDN 링크가 포함되어 있는지
- `<section>` 태그 수가 예상 슬라이드 수와 일치하는지
- Mermaid 초기화 코드가 reveal.js 초기화 후에 있는지

```powershell
# 슬라이드 수 확인
(Select-String -Path presentation\index.html -Pattern '<section' | Measure-Object).Count
```

### 3. 주요 구성 요소 확인
- [ ] reveal.js CDN 로드
- [ ] highlight.js 플러그인
- [ ] Mermaid.js CDN 로드
- [ ] CSS 디자인 시스템 (--r-background-color 등)
- [ ] 슬라이드 번호 설정
- [ ] 이미지 경로 유효성 (상대경로)

## 사용자에게 결과 보고

```markdown
## ✅ 생성 완료

| 파일 | 크기 | 설명 |
|------|------|------|
| index.html | XX KB | N장 슬라이드 |

### 사용법
- `index.html`을 브라우저에서 열기
- → 수평 이동 (섹션), ↓ 수직 이동 (세부 슬라이드)
- `S` 키로 발표자 노트 보기
- `F` 키로 전체화면
- `O` 키로 슬라이드 오버뷰
```

## 수정 처리

사용자가 수정을 요청하면:

### 슬라이드 내용 수정
- `edit` 도구로 해당 `<section>` 블록을 직접 수정
- `old_str`에 해당 슬라이드의 고유한 텍스트를 포함하여 정확히 매칭

### 슬라이드 추가
- 삽입 위치의 `</section>` 직전에 새 `<section>` 블록 추가

### 슬라이드 삭제
- 해당 `<section>...</section>` 블록을 빈 문자열로 교체

### 스타일 변경
- CSS 변수 값을 수정하여 전체 테마 변경
- 개별 클래스 수정으로 특정 요소 스타일링

### 대규모 수정 (10개 이상 슬라이드)
- `task` (general-purpose) 에이전트에 전체 재생성 위임
- 기존 파일의 CSS 스타일은 유지하고 슬라이드 내용만 교체

## 반복 수정 흐름

```
사용자 수정 요청
    ↓
edit 도구로 수정 적용
    ↓
수정 결과 보고 (변경 내용 요약)
    ↓
사용자 추가 수정? → Yes → 반복
                  → No → 완료
```

## Phase 4 완료 조건

- [ ] 사용자가 "완료" 또는 더 이상 수정 요청 없음
- [ ] 최종 파일 목록과 크기 보고
