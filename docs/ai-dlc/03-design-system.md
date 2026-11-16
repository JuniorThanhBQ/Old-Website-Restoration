# 03 — Design System

The visual language is derived from *As It Was* (see `01-intent-and-requirements.md` §2). Every
token below is a decision with a reason; components are described as behaviour, not markup, so the
implementation has freedom while staying consistent.

## 1. Concept

**"Two rooms in one house."** The visitor stands in the *present* — a warm, bone-coloured,
editorial room with hard rules and a red accent, like a mid-century record sleeve. One control
(`Now` / `Then`) walks them into the *past*: the 2022 site's own near-black room with amber glass
panels. Same floor plan, same furniture, different light. That is the song in one interaction —
the place is identical, the feeling is not.

The 2022 interface characteristics survive as *furniture*: full-bleed hero video under frosted
glass, pill-shaped nav with a fill-on-hover, bracketed `[ 01 ]` FAQ numbering, a radial four-circle
"ikigai" diagram, and quote interludes that interrupt the page rhythm.

## 2. Colour tokens

Two palettes are themable via `[data-theme]` on `<html>`. Name = semantic role, value = palette.

### Now (default, light)

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#F4F0E8` warm bone | page background |
| `--canvas-deep` | `#E7E0D3` | alternating band, inset wells |
| `--ink` | `#14171C` near-black | body text, rules |
| `--ink-soft` | `#5A5F68` | secondary text (4.9:1 on canvas) |
| `--rule` | `rgba(20,23,28,0.16)` | hairline rules, grid lines |
| `--accent` | `#C3341F` signal red | links, active states, accents |
| `--accent-ink` | `#FFFFFF` | text on accent fill |
| `--surface` | `#FFFDF9` | raised card |
| `--glass` | `rgba(255,253,249,0.62)` + `blur(18px)` | frosted panel on media |
| `--shadow` | `0 1px 0 rgba(20,23,28,.05), 0 18px 40px -24px rgba(20,23,28,.35)` | card lift |

### Then (the 2022 room)

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#0B0C0E` | page background |
| `--canvas-deep` | `#141619` | band |
| `--ink` | `#F2EFE9` | body text |
| `--ink-soft` | `#A8AEB8` | secondary (7.2:1 on `#0B0C0E`) |
| `--rule` | `rgba(242,239,233,0.18)` | rules |
| `--accent` | `#FFA200` amber | the original site's own accent, restored |
| `--accent-ink` | `#0B0C0E` | text on amber |
| `--surface` | `rgba(255,255,255,0.05)` | glass card |
| `--glass` | `rgba(10,11,13,0.55)` + `blur(18px)` | frosted panel |
| `--shadow` | `0 18px 60px -30px #000` | depth |

Amber `#FFA200` on `#0B0C0E` = 9.0:1. Red `#C3341F` on bone `#F4F0E8` = 4.7:1 (body-safe).
Both accent/`--accent-ink` pairs are checked in `VERIFICATION.md`.

## 3. Typography

Self-hosted variable fonts, `woff2`, subset to Latin + Latin-ext + **Vietnamese** (diacritics are
non-negotiable — `Thành`, `Nghiệp vụ`, `ĐGHT`).

| Role | Family | Size (fluid) | Notes |
|---|---|---|---|
| Display / headings | **Fraunces** (variable, opsz 9–144, wght 300–700) | `clamp(2.4rem, 6vw, 5.5rem)` for h1 | soft, slightly wonky mid-century serif; `opsz` rails engaged |
| Body | **Inter** (variable, wght 300–700) | `clamp(1rem, 0.34vw + 0.95rem, 1.125rem)` | neutral grotesque, tall x-height for Vietnamese marks |
| Meta / labels / numbers | **JetBrains Mono** 400/600 | `0.72–0.8rem`, `letter-spacing: .08em`, uppercase | archival, footnote-like; carries the `[ 01 ]` numerals and clock |

Rules: measure capped at `68ch`; headings `text-wrap: balance`; body `text-wrap: pretty`;
`font-display: swap` with a metric-matched fallback (`size-adjust`/`ascent-override` on a local
`@font-face`) so swapping causes no CLS.

## 4. Space, grid, shape

- 12-column grid, max content width `76rem`, gutters `clamp(1rem, 4vw, 4rem)`.
- Spacing scale (rem): `0.25 0.5 0.75 1 1.5 2 3 4 6 8 12` — nothing off-scale.
- Radii: `--r-sm: 2px`, `--r-md: 4px`, `--r-pill: 999px` (pills only for nav, chips, toggles).
  Panels stay nearly square so they read as plates, per the wide-angle/hard-edge motif.
- Borders do the work that shadows used to: 1px `--rule` everywhere, `--shadow` only on true cards.

## 5. Motion

| Element | Behaviour | Reduced motion |
|---|---|---|
| Hero video | `autoplay muted loop playsinline`, fades in over poster | poster image only, no `<video>` playback |
| Entrance | IntersectionObserver adds `.is-in` → `opacity` + 12px `translateY`, 500ms, 60ms stagger, once | none (content visible immediately) |
| Radial diagram | CSS `rotate` on a 60s loop on the ring only | none |
| Scroll cue | 2s bob | none |
| Nav pill hover | background wipes left→right with `transform: scaleX` | colour change only |
| Theme switch | 220ms `background-color`/`color` transition on `body` | none |

All timings ≤ 600ms except explicitly ambient loops; no motion lasts longer than 5s per WCAG 2.3.1
(ambient loops are decorative and stopped under reduced motion).

## 6. Components

**Header** — sticky, transparent over hero, solidifies with a hairline + backdrop blur after 80px
scroll. Left: wordmark `Junior Thành` (display serif, `Thành` in accent). Centre/right: 5 pill nav
links with active-section highlight driven by IntersectionObserver. Right: theme switch (segmented
`Now | Then`, `role="group"`, `aria-pressed`) and a menu button below `860px` opening a full-height
sheet. Skip-link is the first focusable element.

**Hero** — full-viewport. Layers, back to front: muted looping video (`train.mp4`) → poster →
vertical/horizontal scrim → frosted plate. Plate contains: `HCMC-OU` eyebrow, `Junior Thành` h1,
`Văn Trung Thành - K23 ᵀᴹ` byline, standfirst, `Châm ngôn` quote, live clock chip, and a two-column
fact list (`Ngành học`/`Chuyên ngành`/`Chứng chỉ` + `Sở thích`/`Trình độ`/`Khác`). A circular
"spin" badge sits at the plate's edge with rotating text (the rotating-stage motif); it doubles as
the scroll-to-about trigger.

**Section header** — the recurring editorial unit: mono index `01` + rule + label
(`GIỚI THIỆU`), then display h2. Establishes the archival register and makes the page scannable.

**Quote interlude** — full-bleed band in `--canvas-deep`, oversized display serif, hanging
quotation mark, mono attribution `— Junior Thành —`. Used 3× to break rhythm exactly where the
2022 site did.

**Role cards** — 4-up grid → 2-up → 1-up. Each: mono index, English title (display serif),
Vietnamese subtitle (mono, accent), hairline, body, and for the first card an inline link to
Bookshop 360. Hover raises 2px and darkens the rule (no floating).

**About** — asymmetric two-column: prose + two quote cards left, portrait with caption right.
Portrait is `aspect-ratio: 3/4`, `object-fit: cover`, lazy, with a mono caption plate.

**Goals** — centre stage radial diagram: 4 glass nodes on a ring around a solid `Mục tiêu` core,
ring slowly rotating; nodes lift on hover/focus; below, the two closing quotes separated by rules.
Text is real HTML (not SVG text) so it stays selectable and screen-readable; the ring is
`aria-hidden` decoration while an adjacent definition list carries the same four labels.

**FAQ** — two-column: accordion list left, sticky side card right (`Sinh viên trường đại học Mở
TP.Hồ Chí Minh`, chips). Each row: mono `[ 01 ]`, question button spanning the row, plus/minus
glyph built from two rules, panel with the bracketed answer. Native `<details>`-free implementation
for full control: `button[aria-expanded]` + `div[role=region][aria-labelledby]`, animated via
`grid-template-rows: 0fr → 1fr`, Escape closes, multiple may be open.

**Footer** — closing paragraph in display serif, then 4 columns (social, `Điều hướng`,
`Liên kết ngoài`, clock), bottom bar with `© 2026 …` (year computed), the live clock, and
`Ý tưởng Design: The Art Of Documentary`. A thin animated marquee of the site name sits above it,
echoing a record-sleeve spine.

## 7. Anti-goals for the designer/implementer

No gradient mesh, no glassmorphism-everywhere, no purple, no emoji as icons, no border-radius
above 6px on cards, no letter-spacing on body text, no scroll-jacking, no cursor effects, no
"hero with three floating cards", no autoplaying audio.
