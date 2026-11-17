# 03 — Design System

The visual language is derived from *As It Was* (see `01-intent-and-requirements.md` §2). Every
token below is a decision with a reason; components are described as behaviour, not markup, so the
implementation has freedom while staying consistent.

## 1. Concept

**"Two rooms in one house."** The visitor stands in the *present* — a cold, blue-lit editorial
room with hard rules, like a record sleeve left in daylight — and one control (`Now` / `Then`)
walks them into the *past*: the 2022 site's own near-black room with amber glass panels. Same
floor plan, same furniture, different light — and a different song in each room. That is the
song in one interaction: the place is identical, the feeling is not.

The two rooms are named after what they hold, not after a colour:

- **Now** — Billie Eilish, *"everything i wanted"*. Submerged, lucid, cool. Paper `#EEF3F7`,
  deep-navy ink, a blue tone of `#4292C6`.
- **Then** — Harry Styles, *"As It Was"*. Warm, archival, lamplit. Near-black `#0B0C0E` with
  the 2022 site's own amber `#FFA200`.

The 2022 interface characteristics survive as *furniture*: full-bleed hero video with the name set
over it, pill-shaped nav with a fill-on-hover, bracketed `[ 01 ]` FAQ numbering, a radial four-circle
"ikigai" diagram, quote interludes that interrupt the page rhythm, and the header's own play button.

## 2. Colour tokens

Two palettes are themable via `[data-theme]` on `<html>`. Name = semantic role, value = palette.
Every surface — page canvas, hero scrim, header scrim, footer wash, ikigai core — reads from this
set, so switching rooms re-lights the whole page rather than tinting a few links.

### Now (default, light)

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#EEF3F7` cool paper | page background |
| `--canvas-deep` | `#DFE8F0` | alternating band, inset wells |
| `--canvas-ink` | `#0B1B29` deep navy | inverse surfaces, ikigai core |
| `--ink` | `#0E1C28` navy-black | body text |
| `--ink-soft` | `#4A5A69` | secondary text (6.4:1 on canvas) |
| `--rule` | `rgba(14,28,40,0.16)` | hairline rules, grid lines |
| `--rule-strong` | `rgba(14,28,40,0.40)` | emphasised rules, chip borders |
| `--accent` | `#4292C6` blue | the room's tone: progress, rules, large display, icons |
| `--accent-text` | `#2A6E9C` | links and small accent text (4.9:1 on canvas) |
| `--accent-fill` | `#2F7BA9` | accent fills carrying small text (4.6:1 with white) |
| `--accent-ink` | `#FFFFFF` | text on the fill |
| `--surface` | `#FBFDFE` | raised card |
| `--card-bg` | `#FBFDFE` | opaque card (the liner HUD) |
| `--hero-bg` / `--hero-tint` | `#06131F` / `6,19,31` | hero bed and scrim tint |
| `--hero-accent` | `#7CC0E8` | the name accent and clock on dark (7.4:1 on the scrim) |
| `--deep-bg` | `#0B1B29` | footer wash |
| `--deep-ink` / `--deep-soft` / `--deep-quiet` | `#E7F0F7` / `0.82α` / `0.62α` | footer text tiers |
| `--shadow` | `0 1px 0 rgba(14,28,40,.05), 0 20px 44px -26px rgba(14,28,40,.32)` | card lift |

### Then (the 2022 room)

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#0B0C0E` | page background |
| `--canvas-deep` | `#141619` | band |
| `--canvas-ink` | `#06070A` | ikigai core, deepest edge |
| `--ink` | `#F2EFE9` | body text |
| `--ink-soft` | `#A8AEB8` | secondary (8.8:1 on `#0B0C0E`) |
| `--rule` | `rgba(242,239,233,0.18)` | rules |
| `--rule-strong` | `rgba(242,239,233,0.46)` | emphasised rules |
| `--accent` / `--accent-text` / `--accent-fill` | `#FFA200` amber | the original site's own accent, restored (9.7:1 on canvas) |
| `--accent-ink` | `#0B0C0E` | text on amber |
| `--surface` | `rgba(255,255,255,0.05)` | translucent card |
| `--card-bg` | `#16191D` | opaque card (the liner HUD) |
| `--hero-bg` / `--hero-tint` | `#0B0C0E` / `6,7,9` | hero bed and scrim tint |
| `--hero-accent` | `#FFB43A` | the name accent and clock on dark |
| `--deep-bg` | `#06070A` | footer wash |
| `--shadow` | `0 22px 60px -30px #000` | depth |

### Why four accent roles instead of one

A single accent cannot be both a large display colour and a body-text colour at `#4292C6`: it is
5.1:1 on the navy hero but only 3.4:1 on the light canvas, which fails AA for anything smaller than
large text. Rather than silently break the requested tone or quietly darken it everywhere, the
token set separates the *tone* from its *roles*:

| Role | Reads as | Guarantee |
|---|---|---|
| `--accent` | the room's tone | exactly the briefed value; used where WCAG asks 3:1 (rules, fills behind nothing, large display, icons, focus ring) |
| `--accent-text` | the tone, darkened for small text | ≥ 4.5:1 on the canvas in both rooms |
| `--accent-fill` | the tone, darkened for small text *on* the tone | ≥ 4.5:1 against `--accent-ink` |
| `--accent-ink` | the text that sits on a fill | flips white/near-black per room |

Measured on rendered pixels (not on the token values in isolation): Now body copy 15.5:1, Now link
4.9:1, Now footer label 5.1:1; Then body copy 17.1:1, Then link 9.7:1, Then footer label 10.0:1.

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

**Hero** — full-viewport, and a direct restatement of the 2022 prototype rather than a
reinterpretation of it. Layers, back to front: muted looping video (`train.mp4`) → poster →
scrim. On top, three blocks in the prototype's own order:

1. **Name** — indented about a quarter of the viewport from the left, so the column row below can
   run underneath it. `Junior Thành` on one line (display serif, `Thành` in `--hero-accent` — amber
   in the past room, ice blue in the present one), then
   `Văn Trung Thành - K23 ᵀᴹ` as a mono byline beneath.
2. **Hairline** — full-width rule, the prototype's `<hr>`, separating the name from the facts.
3. **Columns** — four across at desktop, stacking on mobile: `HCMC-OU`, `Châm ngôn`
   (the quote plus a live clock chip), and two fact lists (`Ngành học`/`Chuyên ngành`/`Chứng chỉ`
   and `Sở thích`/`Trình độ`/`Khác`), each entry a serif label over its value with a hairline
   between rows.

The first pass wrapped all of this in a frosted plate with a rotating badge and a scroll cue. Those
were my inventions, not the original's, so they are gone — the glass tokens went with them.

The hero is the clearest proof that the rooms are different light rather than different pages: the
same footage is graded per room through `--hero-media-filter` (cool, desaturated and hue-shifted
towards the blue in `Now`; a touch warmer and lightly sepia'd in `Then`), and the scrim gradients
are generated from `--hero-tint`. Nothing about the composition moves.

**Header music button** — the prototype's play control, restored at the owner's request, now with
one song per room. A single icon button in `.header-tools` (`aria-pressed`, label toggles between
`Bật nhạc nền` and `Tắt nhạc nền`) plays the soundtrack of the room being viewed: `Then` →
*"As It Was"*, `Now` → *"everything i wanted"*. Nothing is fetched until it is pressed. Switching
rooms pauses one track and resumes the other at its own position; both loop. `document.title`
shows `elapsed / total` while playing, as the 2022 site did.

**Liner notes HUD (`#liner`)** — the feature this revision adds, and the place the assistant signs
its work. A card anchored under the header, visible exactly while a track plays: room label, song
title (display serif), artist (mono, `--accent-text`), a five-bar equaliser driven by a Web Audio
`AnalyserNode` — one bar per frequency band — and the credit line
`Product created by V.T.Thanh Assistant.` Bars are scaled with a per-bar `--level` custom property
so CSS owns the geometry and JS only writes numbers. Fallbacks: without `AudioContext` the levels
come from a deterministic sine walk; under `prefers-reduced-motion` they are set once, statically;
`Escape` hides the card without stopping playback; with JS off the card never appears. Its
background is `--card-bg` rather than `--surface`, because a translucent card over the page would
lose the artist line in the dark room.

The card's share link (`.liner__share`) sits under the credit: 0.6 rem mono in `--accent-text`
(5.4:1 on `--card-bg`, the same measured pair as the artist line), underlined rather than
colour-only, hover to `--ink`, and it re-labels itself (`Sao chép liên kết phòng này` →
`Đã sao chép liên kết phòng này`) when the room changes.

**Signature seal** — a 43 px SVG in the footer: dashed outer ring (slow CSS rotation, stopped under
reduced motion), inner rule, `V.T.T.A` in mono. Beside it, in two lines, the product credit. It is
deliberately small and printed in `--accent`, so it reads as a maker's stamp on the page rather
than a banner.

**Time capsule (`#capsule`)** — a footer line that records the first visit in
`localStorage['jth-first-seen']` and prints it as `dd/mm/yyyy`, followed by *"căn phòng này nhớ
bạn"* (this room remembers you). It ships with the `hidden` attribute and is only revealed when
the script can parse a date, so a no-JS or storage-blocked visitor sees nothing rather than a
broken label. Nothing is transmitted.

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
