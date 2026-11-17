# 01 — Intent, Requirements & Acceptance Criteria

Project: **Old Website Restoration** — restoration of `https://juniorthanh09.netlify.app/`
Issue under execution: [issue #1 "Recalling Memories from the Past"](https://github.com/JuniorThanhBQ/Old-Website-Restoration/issues/1)
Lifecycle: AI-DLC (Inception → Construction → Operations) with AIDD spec-first practice.

---

## 1. Intent (verbatim from the issue, normalised into requirements)

The requester (repository owner) asks for four things:

| # | Requirement (issue language) | Normalised engineering requirement |
|---|---|---|
| R1 | "recreate this website" | Content and information architecture of the 2022 Next.js site must be preserved: all sections, all Vietnamese copy, all links. |
| R2 | "in a style similar to the song 'Harry Styles - As It Was'" | The visual language must express the song's meaning and look, applied as a *design system*, not decoration. |
| R3 | "should still retain the interface characteristics of that era, but … blended with more modern design trends" | Era-specific UI motifs (full-bleed hero video, frosted-glass overlay, pill navigation, bracketed FAQ numbering, radial "ikigai" diagram, quote interludes) must survive; modern practice (fluid type, real grid, motion with `prefers-reduced-motion`, strict a11y) must be layered on. |
| R4 | "Just deploy it using GitHub Pages" | Must be a purely static artefact, hosted from this repository via GitHub Pages. No server runtime, no Vercel/Render. |
| R5 | "make sure it meets the standards for performance, security, and UI/UX" | Measurable budgets for performance, a documented security hardening posture, and an accessibility/UX quality gate. See §4. |

Implicit constraints derived from the environment: the public repository is empty, the automation identity has `push` (not `admin`) rights, and GitHub Pages must therefore be published through a workflow (`actions/deploy-pages`), which requires only `pages: write` on the job token.

## 2. Why "As It Was" is a design brief, not a colour pick

The song is about returning to a place that has changed and finding that *"it's not the same as it was"* — nostalgia, circularity (the lyrics circle, the video spins on a rotating platform), and the tension between a remembered past and a present that keeps moving. The official visual language is mid-century/Brutalist geometry, primary-colour blocking on concrete neutrals, wide-angle symmetry, and a spinning circular stage.

Translated into interface decisions (traceability: R2 → token/component):

| Song / video motif | Design decision |
|---|---|
| "It's not the same as it was" | A **dual-palette system**: `Now` (bone/ink) and `Then` (near-black + amber glass — literally the 2022 look). One control switches between them; the visitor chooses which past they are looking at. |
| Rotating stage | Slow-rotating circular motif: the ikigai diagram, the scroll-progress ring, and the rotating needle in the hero badge. All disabled under `prefers-reduced-motion`. |
| Primary-colour blocking on concrete | Signal red accent + ink navy on a warm bone canvas; primary colours used strictly as blocks/accents, never as gradients-where-a-block-would-do. |
| Wide-angle symmetry, hard edges | A 12-column grid with visible hairline rules; radius kept small (2–6px) so panels read as *plates*, not bubbles. |
| Mid-century warmth | A variable serif (Fraunces) for display type against a neutral grotesque (Inter) for text. |
| Nostalgia / archival | Footnote-style bracketed numbering, letterpress-ish rules, `01 / 07` counters, and a footer "design idea" credit, echoing the original's `The Art Of Documentary` credit. |

## 3. Personas and jobs

| Persona | Job-to-be-done |
|---|---|
| A recruiter / classmate on a phone | Learn who this person is in under 20 seconds, then find a way to contact them. |
| The owner (author) | Show a memento of 2022 that still looks current, without maintaining a framework. |
| A returning visitor from 2022 | Recognise the old site ("Then" palette) and see that it grew up ("Now" palette). |
| Assistive-tech user | Get the same information with a screen reader, keyboard only, or reduced motion. |

## 4. Acceptance criteria (binary, testable)

**Content fidelity (R1)**
- AC-1 All seven regions exist in order: header/nav, hero, Giới thiệu, Nghiệp vụ, Mục tiêu, FAQ, footer.
- AC-2 Every piece of prose from the 2022 site is present and byte-identical in meaning, Vietnamese diacritics intact (see `content-inventory.md` which is normative).
- AC-3 All 10 FAQ question/answer pairs are present and operable.
- AC-4 All external links from the original are preserved with `target="_blank"` + `rel="noopener noreferrer"`.

**Design (R2, R3)**
- AC-5 Both palettes (`Now`, `Then`) exist; the choice persists across reloads and respects `prefers-color-scheme` on first visit.
- AC-6 Era motifs present: full-bleed hero video, frosted panel, pill nav, bracketed FAQ numbers, radial diagram, quote interludes.
- AC-7 CLS ≤ 0.1 measured by Lighthouse, with no shift attributable to images (every image carries explicit dimensions or `aspect-ratio`; measured CLS 0). Webfonts use `font-display: swap`, so a late swap can move text slightly. Metric-matched fallback faces (`size-adjust` / `ascent-override`) were evaluated and deliberately not shipped: calibrating them requires the real Georgia/Arial binaries, which are absent from the build environment, so the values would have been guesses against DejaVu and could be worse than no override on user machines.

**Deployment (R4)**
- AC-8 The site is served over HTTPS from `https://juniorthanhbq.github.io/Old-Website-Restoration/` with HTTP 200 and no 404 for any referenced sub-resource.
- AC-9 All asset URLs resolve correctly under the `/Old-Website-Restoration/` base path (no root-absolute traps).

**Performance (R5)**
- AC-10 Lighthouse (mobile, throttled) Performance ≥ 90; LCP ≤ 2.5 s, CLS ≤ 0.1, TBT small.
- AC-11 First-load transfer (HTML + CSS + JS + fonts + above-the-fold media) ≤ 1.2 MB, excluding the lazy hero video.
- AC-12 Zero third-party network requests on load (fonts, analytics, embeds all absent or self-hosted).

**Security (R5)**
- AC-13 A restrictive `Content-Security-Policy` is delivered; no inline script executes; no `eval`, no `innerHTML` with untrusted data.
- AC-14 No secret, token, or personal data is committed. `Referrer-Policy` limited, no `document.write`, external links `noopener`.
- AC-15 Static-only surface: no forms that post, no server endpoints, no dependencies with a build-time install at deploy.

**UI/UX & accessibility (R5)**
- AC-16 axe-core: zero critical/serious violations on desktop and mobile.
- AC-17 Fully keyboard operable: visible focus, skip link, working mobile menu, working theme toggle, accessible accordion (`aria-expanded`, `aria-controls`) and Escape-to-close.
- AC-18 Contrast ≥ 4.5:1 for body text and ≥ 3:1 for large text/UI in **both** palettes.
- AC-19 Motion respects `prefers-reduced-motion: reduce` (video replaced by poster, no transforms/parallax).
- AC-20 Usable from 320 px to 1920 px with no horizontal scroll at 320/375/768/1024/1440.

## 5. Explicit non-goals (scope guard)

- No framework, bundler, or runtime dependency — the value here is a static memento that will still open in ten years.
- No CMS, comments, contact form, analytics, or cookie banner (nothing to consent to).
- No re-hosting of *third-party* audio. The 2022 site streamed `song.mp3`/`song2.mp3`; the first pass dropped the player as a licensing risk. **The owner then asked for it back**, and the audio shipped is the owner's own page content, so it is restored (see D1). The player stays opt-in: nothing is fetched or played until the visitor presses the button.
- No deployment to Vercel/Render/Netlify (explicitly out of scope in the issue).

## 6. Human-in-the-loop decisions (AI-DLC oversight)

| Decision | Owner | Note |
|---|---|---|
| Adopt the dual-palette interpretation of "As It Was" | Requester approved by asking for the song's *meaning* to be used | Documented as the primary creative risk. |
| Restore the background-music player and the 2022 favicon | **Owner**, issue comment on the reopened ticket | Supersedes the first pass's D1. The owner asked for their own page's favicon and play button back, so both are restored from the original assets rather than redrawn. Autoplay is still refused — the button is the only way audio starts. |
| Static HTML/CSS/JS instead of Next.js | Agent | Required by GitHub Pages + R5 budgets. |
| Publish via Actions workflow rather than `gh-pages` branch | Agent | Automation identity lacks `admin`, so Pages must be enabled by the owner or by a workflow with `pages: write`. |
