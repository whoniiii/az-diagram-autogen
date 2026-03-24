# 슬라이드 패턴 라이브러리

> 자주 사용되는 슬라이드 HTML 패턴 모음.
> 서브에이전트 프롬프트에서 "이 패턴으로 만들어줘"라고 참조할 수 있다.

---

## 1. 타이틀 슬라이드

```html
<section data-background-gradient="linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2137 100%)">
    <h1>{메인 타이틀}</h1>
    <h2 style="font-size:1.1em; color:#79c0ff; margin-top:0.3em;">{서브 타이틀}</h2>
    <p class="subtitle" style="font-size:0.8em; margin-top:1em;">
        {한 줄 설명}
    </p>
    <p style="margin-top:1.5em;">
        <span class="tag">{태그1}</span>
        <span class="tag">{태그2}</span>
        <span class="tag">{태그3}</span>
    </p>
    <p class="github-link" style="margin-top:1.5em;">
        <a href="{URL}" target="_blank">🔗 {링크 텍스트}</a>
    </p>
</section>
```

---

## 2. 목차 테이블

```html
<section>
    <h2>📋 목차</h2>
    <table>
        <thead>
            <tr><th>파트</th><th>내용</th><th>시간</th></tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="highlight-text">Part 1</span></td>
                <td>{내용}</td>
                <td><span class="time-badge">~60분</span></td>
            </tr>
            <!-- 반복 -->
        </tbody>
    </table>
</section>
```

---

## 3. 개념 설명 (Box 카드)

```html
<section>
    <h2>{제목}</h2>
    <div class="box box-blue">
        <h4>🔵 {소제목 1}</h4>
        <p class="medium">{설명}</p>
    </div>
    <div class="box box-orange" class="fragment">
        <h4>🟠 {소제목 2}</h4>
        <p class="medium">{설명}</p>
    </div>
    <div class="box box-green" class="fragment">
        <h4>🟢 {소제목 3}</h4>
        <p class="medium">{설명}</p>
    </div>
</section>
```

---

## 4. Mermaid 다이어그램

```html
<section>
    <h2>{제목}</h2>
    <div class="mermaid">
graph LR
    A["{시작}"] --> B["{단계1}"]
    B --> C["{단계2}"]
    C --> D["{단계3}"]
    D --> E["{결과}"]
    
    style A fill:#4fc3f7
    style E fill:#66bb6a
    </div>
    <p class="small" style="margin-top:1em;">{보충 설명}</p>
</section>
```

### Mermaid 다이어그램 유형별 예시

#### 좌우 흐름 (LR)
```
graph LR
    A[입력] --> B[처리] --> C[출력]
```

#### 상하 흐름 (TD)
```
graph TD
    A[시작] --> B{분기}
    B -->|옵션A| C[결과A]
    B -->|옵션B| D[결과B]
```

#### 시퀀스 다이어그램
```
sequenceDiagram
    participant U as 사용자
    participant A as API
    participant S as Search
    participant L as LLM
    U->>A: 질문
    A->>S: 벡터 검색
    S-->>A: 관련 문서
    A->>L: 프롬프트 + 문서
    L-->>A: 응답
    A-->>U: 답변 + 출처
```

---

## 5. 비교표

```html
<section>
    <h2>{제목}</h2>
    <table>
        <thead>
            <tr>
                <th>기준</th>
                <th>{옵션 A}</th>
                <th>{옵션 B}</th>
                <th>{옵션 C}</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>{기준1}</strong></td>
                <td>{값}</td>
                <td>{값}</td>
                <td>{값}</td>
            </tr>
            <!-- 반복 -->
        </tbody>
    </table>
    <p class="small" style="margin-top:0.5em;">💡 {팁 또는 권장사항}</p>
</section>
```

---

## 6. 코드 스니펫

```html
<section>
    <h2>{제목}</h2>
    <p class="medium">{설명}</p>
    <pre><code class="language-python" data-trim data-noescape>
# {코드 설명 주석}
def example_function():
    result = do_something()
    return result
    </code></pre>
    <p class="small">📁 <span class="code-inline">{파일경로}</span></p>
</section>
```

### 지원 언어 태그
- `language-python`, `language-typescript`, `language-javascript`
- `language-yaml`, `language-bash`, `language-json`
- `language-bicep`, `language-sql`, `language-csharp`

---

## 7. 2컬럼 레이아웃

```html
<section>
    <h2>{제목}</h2>
    <div class="columns">
        <div class="col">
            <div class="box box-blue">
                <h4>{왼쪽 제목}</h4>
                <ul>
                    <li>{항목1}</li>
                    <li>{항목2}</li>
                </ul>
            </div>
        </div>
        <div class="col">
            <div class="box box-green">
                <h4>{오른쪽 제목}</h4>
                <ul>
                    <li>{항목1}</li>
                    <li>{항목2}</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

---

## 8. 이미지 슬라이드

```html
<section>
    <h2>{제목}</h2>
    <img src="{상대경로}" alt="{설명}" />
    <p class="small">{캡션}</p>
</section>
```

---

## 9. 스텝 (단계별 절차)

```html
<section>
    <h2>{제목}</h2>
    <div class="box box-blue" style="text-align:left;">
        <p><span class="step-num">1</span> <strong>{단계1}</strong></p>
        <p class="medium" style="margin-left:34px;">{설명}</p>
    </div>
    <div class="box box-blue fragment" style="text-align:left;">
        <p><span class="step-num">2</span> <strong>{단계2}</strong></p>
        <p class="medium" style="margin-left:34px;">{설명}</p>
    </div>
    <div class="box box-green fragment" style="text-align:left;">
        <p><span class="step-num">3</span> <strong>{단계3}</strong></p>
        <p class="medium" style="margin-left:34px;">{설명}</p>
    </div>
</section>
```

---

## 10. 핵심 메시지 / 인용

```html
<section>
    <h2>{제목}</h2>
    <div class="box box-blue" style="text-align:center; padding:40px;">
        <p style="font-size:1.4em; color:#e6edf3; line-height:1.6;">
            "{핵심 메시지 또는 인용문}"
        </p>
        <p class="small" style="margin-top:1em;">— {출처}</p>
    </div>
</section>
```

---

## 11. 숫자/KPI 강조

```html
<section>
    <h2>{제목}</h2>
    <div class="columns">
        <div class="col" style="text-align:center;">
            <p style="font-size:3em; color:#58a6ff; font-weight:bold;">{숫자1}</p>
            <p class="medium">{설명1}</p>
        </div>
        <div class="col" style="text-align:center;">
            <p style="font-size:3em; color:#3fb950; font-weight:bold;">{숫자2}</p>
            <p class="medium">{설명2}</p>
        </div>
        <div class="col" style="text-align:center;">
            <p style="font-size:3em; color:#f0883e; font-weight:bold;">{숫자3}</p>
            <p class="medium">{설명3}</p>
        </div>
    </div>
</section>
```

---

## 11. 체크리스트 / 요약

```html
<section>
    <h2>✅ {제목}</h2>
    <div class="box box-green">
        <ul class="checklist">
            <li>{항목1}</li>
            <li>{항목2}</li>
            <li>{항목3}</li>
            <li>{항목4}</li>
            <li>{항목5}</li>
        </ul>
    </div>
</section>
```

---

## 12. Q&A / 감사합니다

```html
<section data-background-gradient="linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2137 100%)">
    <h1>🙋 Q&A</h1>
    <p class="subtitle" style="font-size:1em; margin-top:1em;">
        질문이 있으시면 편하게 말씀해주세요
    </p>
    <p style="margin-top:2em; font-size:1.5em;">감사합니다! 🙏</p>
</section>
```

---

## Fragment 애니메이션 팁

```html
<!-- 순차 등장 -->
<li class="fragment">첫 번째</li>
<li class="fragment">두 번째</li>

<!-- 특정 효과 -->
<p class="fragment fade-in">페이드 인</p>
<p class="fragment highlight-blue">파란색 강조</p>
<p class="fragment fade-up">아래에서 올라옴</p>

<!-- 인덱스 지정 (순서 제어) -->
<p class="fragment" data-fragment-index="2">두 번째로 등장</p>
<p class="fragment" data-fragment-index="1">첫 번째로 등장</p>
```

## Speaker Notes

```html
<section>
    <h2>슬라이드 제목</h2>
    <p>슬라이드 내용</p>
    <aside class="notes">
        발표자만 보이는 노트. S 키로 열기.
        여기에 발표 스크립트나 추가 설명을 작성.
    </aside>
</section>
```
