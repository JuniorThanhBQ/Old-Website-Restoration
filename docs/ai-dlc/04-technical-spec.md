# 04 — Technical Specification & Build Plan

## 1. Constraint set

| Constraint | Consequence |
|---|---|
| GitHub Pages, project site | Base path `/Old-Website-Restoration/`. All internal URLs **relative** (`./assets/...`, `#anchor`) — no leading `/`. |
| No build step on deploy | Pure static files committed to `main`; the workflow uploads the directory as an artefact. |
| No third-party runtime | Fonts self-hosted, no analytics, no CDN, no embed. |
| Mobile Lighthouse ≥ 90 | Critical CSS inline, JS deferred and tiny, images sized, video lazy. |
| `automation` token has `push` but not `admin` | Pages must be published by a workflow using `pages: write`; enabling Pages is an owner action if the API refuses. |

## 2. File layout

```
/
├── index.html                 # the whole page, semantic, no framework
├── 404.html                   # styled, relative links
├── robots.txt
├── .nojekyll                  # keep _next-free dirs with underscores, skip Jekyll
├── sitemap.xml
├── site.webmanifest           # PWA manifest (root-relative so icons resolve)
├── assets/
│   ├── css/style.css          # single stylesheet, design tokens first
│   ├── css/fonts.css          # generated @font-face block
│   ├── js/main.js             # progressive enhancement only
│   ├── favicon.svg
│   ├── fonts/                 # 3 glyph-subsetted woff2 (107 KB total)
│   ├── img/                   # portrait (3 widths × avif/webp), poster, favicons, logo, og
│   └── media/hero.mp4 + .webm # re-encoded, lazily attached
├── assets-src/                # original untouched media (provenance, not shipped)
├── tools/build-assets.py      # reproducible image/video pipeline
├── tools/build-fonts.py       # reproducible font pipeline (+ --check coverage gate)
├── tools/qa.py                # local + CI verification sweep
├── docs/ai-dlc/               # AIDD artefacts
├── docs/ai-dlc/               # AIDD artefacts
└── .github/workflows/pages.yml
```

## 3. Asset pipeline (must be reproducible, no binaries authored by hand)

`tools/build-assets.py` regenerates everything in `assets/` from `assets-src/`:

| Output | Rule |
|---|---|
| `img/portrait-{480,780,1120}.webp` + `.avif` | from `assets-src/me1.webp`, quality tuned, `aspect 3:4` crop-free resize |
| `img/hero-poster.{avif,webp}` | frame from `train.mp4`, 1280×720 — avif ~37 KB, webp ~55 KB, plus a base64 LQIP |
| `img/ou-logo.webp` | from `assets-src/ou-logo.webp`, max 320px wide (footer use) |
| `img/favicon.svg` + `favicon-32.png` + `apple-touch-icon.png` | generated from the `JT` monogram (SVG source of truth) |
| `img/og.png` | 1200×630 social card composed from tokens (Pillow) |
| `media/hero.mp4` | `train.mp4` cut to a 12 s silent loop, 1280×720, `+faststart` → **293 KB** |
| `media/hero.webm` | VP9 sibling, served first via `<source>` → ~300 KB |

Every output must keep the visual content of the source (no re-cropping of the portrait's subject).

## 4. HTML requirements

- `<!doctype html>`, `<html lang="vi" data-theme="now">`.
- `<head>`: charset, viewport, title, description, canonical, OG/Twitter (`og:image` → `assets/img/og.png`), `theme-color` per scheme, favicon set, `<link rel="preload">` for the two critical font files and the hero poster; two normal `<link rel="stylesheet">` (no `media`-swap trick — that breaks without JS). Non-critical CSS is not inlined: the whole stylesheet is ~30 KB and gzips well, so splitting it would add a round trip for no gain.
- Landmarks: one `<header>`, one `<main>`, one `<footer>`, `<nav aria-label="Điều hướng chính">`.
- Heading order: exactly one `<h1>` (site name in hero), `<h2>` per section, `<h3>` for cards/FAQ.
- Every `<a>` to another origin: `target="_blank" rel="noopener noreferrer"`; internal anchors plain.
- Every `<img>`: `width`, `height` (or `aspect-ratio`), `loading="lazy"`, `decoding="async"`, meaningful `alt` (decorative → `alt=""`).
- Video: `muted playsinline loop preload="none" poster`, `aria-hidden="true"`, `tabindex="-1"`, wrapped in a `<div>` that also holds the poster as `<img>` for reduced motion; JS only swaps in the video when motion is allowed.
- No inline `<script>`; single `<script src="./assets/js/main.js" defer>`. `integrity` not needed (same origin).
- `<noscript>` fallback: video stays poster, accordion panels visible (`<noscript><style>`), theme defaults to Now.
- FAQ: `button` inside `h3`, `aria-expanded`, `aria-controls`, panel `id` + `role="region"` + `aria-labelledby` + `hidden` toggling.

## 5. CSS requirements

- Cascade layers: `@layer reset, tokens, base, layout, components, utilities`.
- Tokens in `:root` and `[data-theme="then"]`; no raw hex outside the token block.
- Fluid type via `clamp()`; no media-query font jumping beyond one step.
- Layout with `grid`; `minmax`; container-relative units where useful.
- `:focus-visible` outlines on every interactive element: `2px solid var(--accent)` + `2px offset`, plus a `--accent`-tinted ring.
- `@media (prefers-reduced-motion: reduce)` kills all animation/transition and the video.
- `@media (prefers-contrast: more)` thickens rules and removes translucency.
- No `!important` outside a documented reduced-motion/forced-colors block.
- Print styles: hide nav/video, black on white, show all FAQ panels.

## 6. JS requirements (progressive enhancement, no framework)

Vanilla, one IIFE, strict mode, ≤ ~150 lines, all features degrade to a working page:

1. **Theme** — read `localStorage['jth-theme']`, else `matchMedia('(prefers-color-scheme: dark)')`; set `data-theme`; toggle updates `aria-pressed`, `localStorage`, and `<meta name="theme-color">`. Wrap `localStorage` in `try/catch` (Safari private mode).
2. **Clock** — updates hero + footer time every 1s using `Intl.DateTimeFormat('vi-VN', {hour, minute, second})`-ish output matching the original `h:mm:ss AM/PM` style; `aria-live="off"`, `role="timer"` avoided; no layout shift (tabular-nums).
3. **Mobile menu** — toggle `aria-expanded`, `hidden` on the sheet, focus trap, Escape, close on link click, restore focus.
4. **Active nav** — IntersectionObserver on sections; sets `aria-current="true"` on the matching link.
5. **Reveal animations** — IntersectionObserver adding `.is-in`; if IO unsupported or reduced motion, add `.is-in` to everything immediately.
6. **FAQ accordion** — click toggles `aria-expanded` + `hidden` + `grid-template-rows` class; Escape closes focused row.
7. **Scroll progress** — a 2px top bar width driven by `requestAnimationFrame` (passive scroll).
8. **Year** — replace `#year` text with current year.
9. **Header state** — add `.is-stuck` past 80px.
10. **Video** — if `matchMedia('(prefers-reduced-motion: reduce)').matches` is false and `navigator.connection.saveData !== true` and viewport ≥ 480px, append/play the `<video>` (source is `data-src`), else keep poster.

Never use `innerHTML` with variable data; use `textContent`/`classList`/`setAttribute`.

## 7. Security posture (defence in depth for a static site)

- **CSP via `<meta http-equiv>`** (Pages cannot set headers):
  `default-src 'self'; img-src 'self' data:; media-src 'self'; font-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'; upgrade-insecure-requests`
  — `'unsafe-inline'` in `style-src` is required by the two `<noscript>`/`404` style blocks; no inline `<script>` exists, so `script-src 'self'` holds. `frame-ancestors` is ignored in meta (documented).
  **`connect-src` must be `'self'`, not `'none'`** — measured, not assumed: with `'none'`, same-origin `fetch`/XHR is blocked, which fails Lighthouse's `robots-txt` audit outright (SEO 92→100 after the change). `'self'` still blocks every cross-origin beacon, so the exfiltration guarantee is unchanged.
- `referrer` meta `no-referrer-when-downgrade` → set `strict-origin-when-cross-origin`.
- `<meta name="color-scheme" content="light dark">`.
- SRI not applicable (same-origin); **no supply chain at all** — zero npm dependencies.
- No `eval`, `new Function`, `document.write`, `innerHTML` with data.
- Workflow hardening: `permissions: {contents: read, pages: write, id-token: write}` at job level, `actions/checkout@v4` + `upload-pages-artifact`/`deploy-pages` pinned by major tag, no `pull_request_target`, no secrets echoed.
- `.gitignore` excludes editor/OS junk; `assets-src/train.mp4` is the only large binary (7 MB) and it is provenance, not shipped payload.

## 8. GitHub Pages workflow

`.github/workflows/pages.yml`:
- Trigger: `push` to `main`, plus `workflow_dispatch`.
- `concurrency: group: pages, cancel-in-progress: false`.
- Job `verify`: checkout → four grep guards (required files, no root-absolute URLs, no inline `<script>`, no third-party asset host, no committed credentials) → stage `_site/` → `configure-pages` → `upload-pages-artifact`.
- Job `deploy`: `environment: github-pages`, `deploy-pages`, output `page_url`.
- Job `smoke`: curl the live `page_url` and assert 200 for the document plus every critical sub-resource. This is the deployment acceptance gate, replacing a separate `tools/verify-live.py`.

## 9. Deliberate deviations from the 2022 build (recorded, justified)

| # | Deviation | Reason |
|---|---|---|
| D1 | Background-music player removed (`song.mp3`, `song2.mp3`) | Third-party commercial recordings; licensing risk, and autoplay audio violates the UX bar. Owner can re-add their own licensed files. |
| D2 | Next.js → hand-written HTML/CSS/JS | No build/runtime on Pages; a 2022 framework site cannot hit the performance budget or the "still opens in ten years" goal. |
| D3 | FAQ answer 03 still says "Next.js" | Verbatim historical content; see `02-content-inventory.md`. |
| D4 | Anchor ids romanised (`#gioi-thieu` instead of `#about`) with the old names kept as alias `id`s | Readable Vietnamese URLs; both resolve. Actually simpler: keep **both** — primary is romanised, and `#about`/`#role`/`#goal`/`#FAQ` remain as hidden alias anchors for old inbound links. |
| D5 | Contact-chat widget (Tidio) not re-added | Third-party script; violates zero-third-party rule and CSP. |
| D6 | `me1.webp` re-encoded to responsive sizes | 300 KB → ~40–90 KB per variant; original preserved in `assets-src/`. |
| D7 | Hero video re-encoded and lazily attached | 7.2 MB, 4 min → ≤2.5 MB clip/loop, `preload="none"`. |

## 10. Definition of done

All AC-1…AC-20 verified with recorded evidence in `docs/ai-dlc/VERIFICATION.md`, the site live on
Pages, the review complete, and issue #1 closed with a summary comment.
