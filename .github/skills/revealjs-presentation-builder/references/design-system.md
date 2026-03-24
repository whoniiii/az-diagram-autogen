# 디자인 시스템: GitHub Dark 스타일 reveal.js

> 이 파일의 CSS를 서브에이전트 프롬프트에 **그대로 포함**해야 한다.
> 축약하거나 "위의 디자인 시스템 참조" 같은 간접 참조를 하지 않는다.

## 컬러 팔레트

| 용도 | 색상 | HEX | CSS 변수 |
|------|------|-----|----------|
| 배경 | ⬛ GitHub Dark | `#0d1117` | `--r-background-color` |
| 본문 텍스트 | ⬜ Light | `#e6edf3` | `--r-main-color` |
| 제목/링크 | 🔵 Blue | `#58a6ff` | `--r-heading-color` |
| 보조 제목 | 🔵 Light Blue | `#79c0ff` | h3, h4 |
| 회색 텍스트 | ⚪ Gray | `#8b949e` | `.subtitle`, `.small` |
| 강조 (주황) | 🟠 Orange | `#f0883e` | `.highlight-text`, `.code-inline` |
| 성공 (초록) | 🟢 Green | `#3fb950` | `.accent`, `.box-green` |
| 경고 (빨강) | 🔴 Red | `#f85149` | `.warn`, `.box-red` |
| 테두리 | ⬛ Border | `#30363d` | table, pre, box, img |
| 카드 배경 | ⬛ Card BG | `#161b22` | table th, `.box` 내부 |
| 선택 영역 | 🔵 Selection | `#264f78` | `--r-selection-background-color` |

## 전체 CSS 코드 (복사 필수)

```css
:root {
    --r-background-color: #0d1117;
    --r-main-color: #e6edf3;
    --r-heading-color: #58a6ff;
    --r-link-color: #58a6ff;
    --r-link-color-hover: #79c0ff;
    --r-selection-background-color: #264f78;
    --r-heading-font: 'Segoe UI', 'Malgun Gothic', sans-serif;
    --r-main-font: 'Segoe UI', 'Malgun Gothic', sans-serif;
    --r-code-font: 'Cascadia Code', 'D2Coding', 'Consolas', monospace;
    --r-heading-text-transform: none;
}

.reveal { font-size: 28px; }

.reveal h1 { font-size: 2.0em; color: #58a6ff; text-shadow: 0 0 20px rgba(88, 166, 255, 0.3); }
.reveal h2 { font-size: 1.6em; color: #58a6ff; }
.reveal h3 { font-size: 1.2em; color: #79c0ff; }
.reveal h4 { font-size: 1.0em; color: #79c0ff; }

/* 텍스트 유틸리티 */
.reveal .subtitle { color: #8b949e; font-size: 0.85em; margin-top: 0.5em; }
.reveal .highlight-text { color: #f0883e; font-weight: bold; }
.reveal .accent { color: #3fb950; }
.reveal .warn { color: #f85149; }
.reveal .small { font-size: 0.65em; color: #8b949e; }
.reveal .medium { font-size: 0.8em; }
.reveal .emoji { font-size: 1.2em; }

/* 테이블 */
.reveal table { margin: 0.5em auto; border-collapse: collapse; font-size: 0.7em; width: 90%; }
.reveal table th { background-color: #161b22; color: #58a6ff; padding: 10px 14px; border: 1px solid #30363d; font-weight: 600; }
.reveal table td { padding: 8px 14px; border: 1px solid #30363d; color: #c9d1d9; vertical-align: top; }
.reveal table tr:nth-child(even) { background-color: rgba(22, 27, 34, 0.5); }
.reveal table tr:hover { background-color: rgba(48, 54, 61, 0.5); }

/* 코드 블록 */
.reveal pre { width: 95%; font-size: 0.55em; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); border: 1px solid #30363d; border-radius: 8px; }
.reveal code { font-family: var(--r-code-font); }
.reveal pre code { max-height: 480px; padding: 16px; }
.reveal .code-inline { background-color: rgba(110, 118, 129, 0.2); color: #f0883e; padding: 2px 6px; border-radius: 4px; font-family: var(--r-code-font); font-size: 0.9em; }

/* 리스트 */
.reveal ul, .reveal ol { display: block; text-align: left; margin-left: 1em; }
.reveal li { margin-bottom: 0.4em; line-height: 1.5; }

/* 박스 카드 */
.reveal .box { background-color: rgba(22, 27, 34, 0.8); border: 1px solid #30363d; border-radius: 10px; padding: 20px 28px; margin: 12px auto; text-align: left; width: 90%; }
.reveal .box-blue { border-left: 4px solid #58a6ff; }
.reveal .box-green { border-left: 4px solid #3fb950; }
.reveal .box-orange { border-left: 4px solid #f0883e; }
.reveal .box-red { border-left: 4px solid #f85149; }

/* 컬럼 레이아웃 */
.reveal .columns { display: flex; gap: 20px; width: 95%; margin: 0 auto; }
.reveal .col { flex: 1; text-align: left; }

/* 태그/배지 */
.reveal .tag { display: inline-block; background-color: rgba(56, 139, 253, 0.15); color: #58a6ff; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; margin: 2px; border: 1px solid rgba(56, 139, 253, 0.3); }
.reveal .tag-green { background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border-color: rgba(63, 185, 80, 0.3); }
.reveal .tag-orange { background-color: rgba(240, 136, 62, 0.15); color: #f0883e; border-color: rgba(240, 136, 62, 0.3); }

/* 시간 배지 */
.reveal .time-badge { display: inline-block; background: linear-gradient(135deg, #238636, #2ea043); color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 0.7em; margin-left: 8px; }

/* 스텝 넘버 */
.reveal .step-num { display: inline-block; background-color: #58a6ff; color: #0d1117; width: 28px; height: 28px; line-height: 28px; border-radius: 50%; text-align: center; font-weight: bold; font-size: 0.8em; margin-right: 6px; }

/* 체크리스트 */
.reveal .checklist { list-style: none; padding-left: 0; }
.reveal .checklist li::before { content: "☐ "; color: #58a6ff; }

/* GitHub 링크 */
.reveal .github-link { font-size: 0.65em; color: #8b949e; }
.reveal .github-link a { color: #58a6ff; }

/* 이미지 */
.reveal img { max-height: 480px; border: 1px solid #30363d; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }

/* Mermaid */
.reveal .mermaid { font-size: 0.65em; }
.reveal .mermaid svg { max-width: 95% !important; max-height: 500px !important; }

/* 슬라이드 번호 */
.reveal .slide-number { color: #8b949e; font-size: 14px; }

/* 진행바 */
.progress span { background: linear-gradient(90deg, #58a6ff, #3fb950) !important; }
```

## HTML 보일러플레이트

```html
<!DOCTYPE html>
<html lang="{언어코드}">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{프레젠테이션 제목}</title>

    <!-- Reveal.js 5.x -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css" id="theme" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/monokai.css" />

    <style>
        /* === 위의 전체 CSS 코드를 여기에 붙여넣기 === */
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">

            <!-- Section 1: 타이틀 -->
            <section>
                <section data-background-gradient="linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2137 100%)">
                    <!-- 타이틀 슬라이드 -->
                </section>
                <section>
                    <!-- 목차 슬라이드 -->
                </section>
            </section>

            <!-- Section 2~N: 본문 -->
            <section>
                <section><!-- 섹션 타이틀 --></section>
                <section><!-- 세부 슬라이드 --></section>
            </section>

        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/zoom/zoom.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: 'c/t',
            showSlideNumber: 'all',
            width: 1280,
            height: 720,
            margin: 0.04,
            minScale: 0.2,
            maxScale: 2.0,
            transition: 'slide',
            transitionSpeed: 'default',
            plugins: [RevealHighlight, RevealNotes, RevealZoom]
        }).then(() => {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'dark',
                themeVariables: {
                    darkMode: true,
                    background: '#0d1117',
                    primaryColor: '#1f6feb',
                    primaryTextColor: '#e6edf3',
                    primaryBorderColor: '#58a6ff',
                    lineColor: '#8b949e',
                    secondaryColor: '#238636',
                    tertiaryColor: '#21262d',
                    fontSize: '14px',
                    fontFamily: '"Segoe UI", "Malgun Gothic", sans-serif'
                },
                flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
                securityLevel: 'loose'
            });

            document.querySelectorAll('.mermaid').forEach((el, index) => {
                const graphDefinition = el.textContent.trim();
                try {
                    mermaid.render('mermaid-graph-' + index, graphDefinition).then(({ svg }) => {
                        el.innerHTML = svg;
                    });
                } catch (e) {
                    console.error('Mermaid rendering error:', e);
                }
            });

            Reveal.on('slidechanged', event => {
                event.currentSlide.querySelectorAll('.mermaid svg').forEach(svg => {
                    svg.style.maxWidth = '100%';
                });
            });
        });
    </script>
</body>
</html>
```
