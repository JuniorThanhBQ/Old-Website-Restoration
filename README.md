# Junior Thành — *As It Was*

A restoration of **https://juniorthanh09.netlify.app/** — a personal portfolio first built
with Next.js 16 and deployed to Netlify in 2022 — rebuilt as a dependency-free static site
and restyled after Harry Styles' *"As It Was"*.

The copy is not rewritten. Every Vietnamese sentence, quirk and straight quote is carried
over verbatim; what changed is the design language around it.

## The idea

*As It Was* is a song about standing in the present while looking back at a room you can
no longer enter. So the site is built as **one house with two rooms**, switchable from the
header — and each room has its own light *and* its own soundtrack:

- **Now** — cold daylight and submerged blue: `#EEF3F7` paper, deep-navy ink, an accent tone
  of **`#4292C6`**, scored with Billie Eilish's *"everything i wanted"*. Lucid, weightless,
  a little underwater.
- **Then** — the 2022 site's own dark room (`#0B0C0E`) with its amber accent (`#FFA200`),
  scored with Harry Styles' *"As It Was"*. Warm, archival, lamplit.

Same content, same layout, same coordinates — only the light (and the song) changes. That
*is* the brief: retain the interface character of that era while blending in modern trends,
rather than reskinning it into something the original never was.

The switch is not a filter: hero scrim and media grading, header, rules, cards, the footer
wash and every accent derive from theme tokens, so the two rooms are genuinely different
places. The hero footage is the same twelve seconds of train, graded cool in the present and
warm in the past.

The original's furniture is all here: its favicon, the header play button with the two songs
it shipped, and the homepage's own composition — name indented over the video, a full-width
hairline, four fact columns beneath it. The player needs JavaScript, so it is hidden rather
than shown-but-dead when scripting is off; everything else, including all the copy, works
without it.

## Listening, attribution, and a room that remembers you

Three small things layer on top of the restoration; all of them degrade to nothing when
scripting is off.

**Liner notes.** Pressing the header play button starts the soundtrack of the room you are
standing in and opens a themed "now playing" card under the header: room, song title,
artist, a five-bar equaliser fed by a Web Audio `AnalyserNode` (with a deterministic
fallback when the analyser is unavailable, and static bars under `prefers-reduced-motion`),
and the credit. Switching rooms mid-song pauses one track and resumes the other exactly
where it stopped — each room remembers its own position. `Escape` dismisses the card.

**Rooms are addresses.** Each room can be sent to someone: `/…/?room=then` opens the past,
`/?room=now` the present, and picking a room writes the parameter straight into the URL with
`replaceState` — no history spam, no questions. The card's share button copies that address
and confirms it; where the Clipboard API is unavailable it puts the room in the address bar
instead and says so.

**The signature.** The footer carries a monogram seal (`V.T.T.A`) and the line
**`Product created by V.T.Thanh Assistant.`**, repeated inside the liner card and declared in
`<meta name="generator">`. The seal's dashed ring turns slowly, and stops when motion is
reduced.

**The time capsule.** On the first visit the page records the date in `localStorage`
(`jth-first-seen`) and the footer says so — *"Lần đầu ghé thăm: 17/11/2026 · căn phòng này
nhớ bạn"* ("the room remembers you"). It never leaves the browser, and without JavaScript the
line simply does not exist.

Audio provenance, stated plainly: the two shipped mp3s are the owner's own 2022 uploads
(`assets-src/song.mp3`, `assets-src/song2.mp3`), re-encoded and renamed one-per-room. No
third-party audio was downloaded. To swap in different masters, drop them into `assets-src/`
and re-run `tools/build-assets.py`.

## Build

None. There is no package manifest, no framework, no bundler.

```bash
python3 -m http.server 8080     # open http://localhost:8080/
```

## Quality

Measured, not asserted — full evidence in [`docs/ai-dlc/05-verification.md`](docs/ai-dlc/05-verification.md).

| | |
|---|---|
| Lighthouse mobile — Now room | **97** performance · **100** accessibility · **100** best practices · **100** SEO |
| Lighthouse mobile — Then room | **97** performance · **100** accessibility · **100** best practices · **100** SEO |
| Lighthouse desktop | **100** across all four |
| Layout shift | **0** |
| axe-core (WCAG 2.1 AA, both themes, desktop + mobile) | **0 violations** |
| Contrast, pixel-sampled on rendered backgrounds (19 text pairs × 2 rooms) | **0 below AA** |
| Functional checks (`tools/qa.py`) | **163 / 163** |
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
                            as-it-was.mp3 (Then) + everything-i-wanted.mp3 (Now), one per room (opt-in)
assets-src/                 original 2022 media, untouched — provenance, not shipped
tools/build-assets.py       reproducible image/video/audio/favicon pipeline
tools/build-fonts.py        reproducible font pipeline (+ --check coverage gate)
tools/qa.py                 163-check verification sweep
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

Product created by **V.T.Thanh Assistant.**
