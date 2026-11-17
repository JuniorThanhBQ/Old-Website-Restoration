# Junior Thành — *As It Was*

A restoration of **https://juniorthanh09.netlify.app/** — a personal portfolio first built
with Next.js 16 and deployed to Netlify in 2022 — rebuilt as a dependency-free static site
and restyled after Harry Styles' *"As It Was"*.

The copy is not rewritten. Every Vietnamese sentence, quirk and straight quote is carried
over verbatim; what changed is the design language around it.

## The idea

*As It Was* is a song about standing in the present while looking back at a room you can
no longer enter. So the site is built as **one house with two rooms**, switchable from the
header:

- **Now** — bone paper (`#F4F0E8`), near-black ink, signal red. Editorial, contemporary.
- **Then** — the 2022 site's own dark room (`#0B0C0E`) with its amber accent (`#FFA200`).

Same content, same layout, same coordinates — only the light changes. That *is* the brief:
retain the interface character of that era while blending in modern trends, rather than
reskinning it into something the original never was.

The original's furniture is all here: its favicon, the header play button with the two songs
it shipped, and the homepage's own composition — name indented over the video, a full-width
hairline, four fact columns beneath it. The player needs JavaScript, so it is hidden rather
than shown-but-dead when scripting is off; everything else, including all the copy, works
without it.

## Build

None. There is no package manifest, no framework, no bundler.

```bash
python3 -m http.server 8080     # open http://localhost:8080/
```

## Quality

Measured, not asserted — full evidence in [`docs/ai-dlc/05-verification.md`](docs/ai-dlc/05-verification.md).

| | |
|---|---|
| Lighthouse mobile | **97** performance · **100** accessibility · **100** best practices · **100** SEO |
| Lighthouse desktop | **100** across all four |
| Layout shift | **0** |
| axe-core (WCAG 2.1 AA, both themes, desktop + mobile) | **0 violations** |
| Functional checks (`tools/qa.py`) | **114 / 114** |
| Third-party runtime requests | **zero** — fonts self-hosted and subsetted to 164 glyphs (107 KB) |

## Structure

```
index.html                  the whole page — one file, semantic, no framework
404.html                    styled, relative links
assets/css/style.css        design tokens first, then layers: reset→tokens→base→layout→components→utilities
assets/css/fonts.css        generated @font-face block
assets/js/main.js           progressive enhancement only; every feature degrades to a working page
assets/fonts/               Fraunces · Inter · JetBrains Mono, glyph-subsetted
assets/img/                 portrait (3 widths × avif/webp), hero poster, the 2022 favicon set, OU logo, OG card
assets/media/               hero.mp4 + hero.webm, 12 s silent loop, lazily attached;
                            as-it-was-1.mp3 + -2.mp3, the header player's two songs (opt-in)
assets-src/                 original 2022 media, untouched — provenance, not shipped
tools/build-assets.py       reproducible image/video/audio/favicon pipeline
tools/build-fonts.py        reproducible font pipeline (+ --check coverage gate)
tools/qa.py                 114-check verification sweep
docs/ai-dlc/                intent → content → design → technical → verification → operations
```

## Documentation

Written spec-first, then verified against the spec:

1. [`01-intent-and-requirements.md`](docs/ai-dlc/01-intent-and-requirements.md) — why "As It Was" is a design brief
2. [`02-content-inventory.md`](docs/ai-dlc/02-content-inventory.md) — the normative copy, verbatim
3. [`03-design-system.md`](docs/ai-dlc/03-design-system.md) — tokens, type scale, components
4. [`04-technical-spec.md`](docs/ai-dlc/04-technical-spec.md) — constraints, security posture, deviations
5. [`05-verification.md`](docs/ai-dlc/05-verification.md) — acceptance evidence
6. [`06-operations.md`](docs/ai-dlc/06-operations.md) — deploy, rebuild, maintain

## Accessibility

Skip link first in the tab order; `:focus-visible` on every control; FAQ as real
buttons with `aria-expanded`/`aria-controls`/`hidden`; mobile sheet traps focus and
restores it on close; `prefers-reduced-motion` drops the video and all animation;
`prefers-contrast: more` removes translucency and thickens rules; a print stylesheet
expands every FAQ answer.

Original credits preserved: design idea — *The Art Of Documentary*; site —
Junior Thành (Văn Trung Thành, K23, HCMC-OU).
