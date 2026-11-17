# Verification — acceptance evidence

Every claim below was produced by running the command shown, against the local build
served by `python3 -m http.server 8080` in the repository root. Nothing here is estimated.

Reproduce with:

```bash
python3 tools/build-fonts.py --check   # font glyph coverage gate
python3 tools/qa.py                    # 156 functional/structural checks
```

`tools/qa.py` exits non-zero on any failure, so it is safe as a CI gate.

---

## 1. Lighthouse (Chrome 156, headless, Lighthouse 12)

**Mobile** — Moto G Power emulation, 4× CPU throttle, Slow 4G:

| Category | Score |
|---|---|
| Performance | **97** |
| Accessibility | **100** |
| Best practices | **100** |
| SEO | **100** |

| Metric | Value |
|---|---|
| First Contentful Paint | 1.4 s |
| Largest Contentful Paint | 2.4 s |
| Total Blocking Time | 40–60 ms (run variance) |
| Cumulative Layout Shift | **0** |
| Speed Index | 1.4 s |
| Total byte weight | 278 KiB |

The `Then` room was measured separately (a copy of the document with `data-theme="then"`, same
assets): **97 / 100 / 100 / 100**, LCP 2.5 s, TBT 0 ms, CLS 0. The palette change does not move
performance; the two rooms differ only in token values.

**Desktop**:

| Category | Score |
|---|---|
| Performance | **100** |
| Accessibility | **100** |
| Best practices | **100** |
| SEO | **100** |

FCP 0.4 s · LCP 0.5 s · TBT 0 ms · CLS 0.

Target was ≥ 90 on mobile. Achieved 97.

## 2. axe-core (WCAG 2.1 A + AA + best-practice rules)

Re-run after this revision, with all ten FAQ panels forced open **and** the liner HUD shown, so
the new components are audited in their visible state:

| Theme | Viewport | Violations | Passing rules |
|---|---|---|---|
| Now | 1440×900 | **0** | 42 |
| Now | 375×812 | **0** | 42 |
| Then | 1440×900 | **0** | 42 |
| Then | 375×812 | **0** | 42 |

One real defect was found this way: the HUD's entrance animation faded its own text from
`opacity: 0`, so a mid-animation sample measured the label and artist at 4.29:1 and 3.64:1. The
fix was to animate the transform only — the card slides in, but its text is never translucent,
so every frame is compliant.

## 3. Contrast — measured from composited pixels, not assumed

The hero sits on video, so every ratio below was computed from real screenshot pixels behind each
text block (text made transparent, background sampled from the element's own box, text alpha
composited back over it), not from declared CSS colours. Both rooms, 19 text/background pairs:

| Element | Now | Then | Required |
|---|---|---|---|
| Body copy | 15.47 | 17.05 | 4.5 |
| Body link | 4.94 | 9.71 | 4.5 |
| Section sub (`--ink-soft`) | 6.36 | 8.77 | 4.5 |
| Hero title | 14.13 | 15.77 | 3.0 (large) |
| Hero column body | 11.31 | 12.91 | 4.5 |
| Hero byline | 14.25 | 15.86 | 4.5 |
| Fact list `dd` | 10.61 | 12.26 | 4.5 |
| Clock value (`--hero-accent`) | 7.44 | 9.51 | 4.5 |
| Footer link | 10.45 | 11.72 | 4.5 |
| Footer label | 5.12 | 10.00 | 4.5 |
| Footer clock | 5.12 | 10.00 | 4.5 |
| Signature name | 15.13 | 17.55 | 4.5 |
| Signature text | 6.47 | 6.50 | 4.5 |
| Capsule date | 5.12 | 10.00 | 4.5 |
| Role-card subtitle | 4.94 | 9.71 | 4.5 |
| Interlude citation | 4.45 | 8.99 | 3.0 (large) |
| Liner song title | 16.94 | 15.37 | 4.5 |
| Liner artist | 5.40 | 8.75 | 4.5 |
| Liner credit | 6.96 | 7.90 | 4.5 |

Minimum across both rooms: 4.45 (large-text citation), 4.94 (small text). No pair falls below AA.
The tightest small-text pair is `--accent-text` on the Now canvas (4.94), which is exactly why
that role exists separately from the `#4292C6` tone (3.4:1 there).

The hero scrim was verified to keep everything behind the text legible: the media renders at
luminance ≈ 0.04–0.08 under the title and column bands, so white text sits at >12:1 there.

## 4. Structural and content fidelity (`tools/qa.py`)

156 checks, all passing. Coverage:

- **Content** — all 100+ normative Vietnamese strings from
  `02-content-inventory.md` present, diacritics intact.
- **Verbatim fidelity** — straight quotes preserved (no smart-quote substitution),
  `- Junior Thành -` attribution not restyled to em-dashes, and the original's
  spacing quirks kept (`HTML,CSS, JavaScript`, `cuộc sống .Còn lại`, `rảnh .`).
- **Structure** — 5 sections, 4 legacy alias anchors, exactly one `<h1>`, one `main`,
  one `header`, one site footer, `lang="vi"`.
- **Links** — all 11 external URLs preserved exactly; every `target="_blank"` carries
  `rel="noopener noreferrer"`.
- **Assets** — every local reference resolves with status < 400; no broken images;
  every `<img>` has `alt` and dimensions.
- **Interactive** — FAQ opens/closes (10 rows, `aria-expanded` + `hidden` correct),
  theme switches both ways with `aria-pressed`, mobile menu opens/closes.
- **Rooms** — each palette applied end to end (canvas, `--accent` token, footer wash, hero
  scrim) and asserted *distinct* across themes, not merely present.
- **Soundtrack** — two room tracks, `preload="none"`, `loop`, no `src` before intent; only the
  active room plays; a room switch hands playback over and switching back resumes the same
  track mid-song; pause stops both and restores `document.title`.
- **Liner HUD** — appears only while playing, carries the room's title/artist, follows a room
  switch, hides on `Escape` and on pause, stays inside the viewport at 320 px.
- **Attribution** — `Product created by` + `V.T.Thanh Assistant` in the footer and in the HUD,
  seal SVG with its `<text>` node, capsule revealed by JS with a `dd/mm/yyyy` date.
- **Responsive** — no horizontal overflow at 320 / 375 / 768 / 1024 / 1440 / 1920 px.
- **Reduced motion** — no video sources attached, all revealed content visible.
- **No JavaScript** — desktop header nav still visible and usable, all ten FAQ answers
  readable, footer nav present as the mobile fallback, hero renders from its poster.
- **Narrow widths** — at 320/360/375 px the wordmark, theme switch and menu button all
  sit inside the viewport and no horizontal scroll is possible.
- **Security posture** — exactly one `<script>` tag and it has `src`; CSP meta present;
  no root-absolute `src`; no inline scripts.
- **Favicon** — every declared icon resolves, the redrawn `favicon.svg` is gone, the 32 px
  icon is 32×32 and still carries the 2022 artwork's amber on transparency (checked by
  reading its pixels in the browser, not by trusting the file name).
- **Music player** — present, starts paused, fetches no audio before the first press, then
  plays at reduced volume, swaps its icon, shows `elapsed / total` in `document.title`, and
  restores the title on pause. The suite also seeks to the end of each track to exercise the
  chain (track 1 → track 2) and the wrap back to track 1, and asserts that rapid clicking
  leaves `aria-pressed` agreeing with what is actually audible.
- **Hero composition** — block order is name → hairline → columns, the title is indented past
  15% of the viewport and sits on one line, the hairline spans the full width, four columns
  start left of the title, and the headings read `HCMC-OU` / `Châm ngôn` / `Ngành học` /
  `Sở thích`. The removed plate, badge and scroll cue are asserted absent.

Content was also diffed directly against the archived 2022 document: **31/31 long text
blocks reproduced verbatim**.

## 5. Keyboard and focus

- First <kbd>Tab</kbd> reaches the skip link; activating it sets `#main`.
- Every visible link/button shows a ≥ 1px outline on focus (checked programmatically
  across the whole DOM, not sampled).
- FAQ opens with <kbd>Enter</kbd>, closes with <kbd>Esc</kbd>, focus stays on the trigger.
- Mobile menu: `aria-expanded` toggles, body scroll locks, focus cannot leave the sheet
  (10 consecutive <kbd>Tab</kbd> presses stayed inside), <kbd>Esc</kbd> returns focus to
  the toggle and unlocks scrolling.
- All in-page anchors resolve to a real element.

## 6. Layout integrity

| Check | Result |
|---|---|
| Prose measure ≤ 78 characters/line at 1440/1024/768/375 | pass (max 70) |
| Hero plate horizontally centred | exact (720 = 720) |
| Radial diagram nodes inside bounds, no overlap with core | pass at all widths |
| Footer grid: 4 tracks wide, 2 tracks ≤ 60rem, no orphan cell | pass |
| Logo never exceeds its column | pass (176 px inside 157–257 px) |
| Portrait/role cards equal height in a row | pass (580 px all four) |

## 7. Deliberate deviations, and why

| # | Deviation | Reason |
|---|---|---|
| D1 | **Restored** at the owner's request: background-music player and the original favicon (was: both omitted) | The owner asked for the play button and icon back. Audio is their own content, re-encoded to 96 kbps and fetched only when the button is pressed — no autoplay, so the UX objection to the first pass no longer applies. |
| D2 | Next.js → hand-written HTML/CSS/JS | GitHub Pages has no build runtime; a framework bundle cannot meet the performance budget. |
| D3 | FAQ answer 03 still says "Next.js" | Verbatim historical content — restoration, not correction. |
| D4 | Romanised anchor ids + legacy aliases | `#gioi-thieu` etc. for readable URLs, while `#about`/`#role`/`#goal`/`#FAQ` remain so old inbound links still land. |
| D5 | Tidio chat widget not re-added | Third-party script; violates zero-third-party and the CSP. |
| D6 | Media re-encoded | 7.2 MB / 4 min → 293 KB / 12 s silent loop; originals kept in `assets-src/`. |
| D7 | Fonts subsetted to 164 glyphs | 180 KB of unused coverage → 107 KB; guarantees the LCP text renders sooner. Coverage is CI-enforced by `build-fonts.py --check`. |

## 8. Deployment

Live at **https://juniorthanhbq.github.io/Old-Website-Restoration/** — HTTP 200, and
`index.html`, CSS, JS, fonts, hero poster, `robots.txt`, `sitemap.xml` and `404.html` all
return 200 from the CDN (asserted by the workflow's `smoke` job).

Two things were only discoverable by actually deploying, and both are now fixed:

1. **The Pages host is the account that owns the repo** (`juniorthanhbq.github.io`), not
   the display handle (`thanh09junior`). Canonical, `og:url`, `og:image`,
   `twitter:image`, `sitemap.xml` and `robots.txt` all pointed at the wrong subdomain,
   which would have produced a canonical that 404s.
2. **`configure-pages` needs `enablement: true`** on a repository where Pages was never
   switched on. Without it the job dies at `Get Pages site failed ... Not Found` and the
   deploy never runs.

The 2022 site's own outbound link to `thanh09junior.github.io/BookShop360_ThanhAndPhong/`
is deliberately left untouched even though it 404s today — it is historical content, and
rewriting it would be editing the artefact rather than restoring it.

### Verified against the live deployment, not just locally

| Check | Result |
|---|---|
| Lighthouse mobile, production URL | perf **98–100** · a11y **100** · BP **100** · SEO **100**; LCP 1.8–2.3 s, CLS 0, ~220 KiB |
| Lighthouse desktop, production URL | **100 / 100 / 100 / 100**; FCP 0.4 s, LCP 0.5 s, TBT 0 ms |
| axe-core on production, both themes × desktop/mobile | **0 violations**, 42 rules passing |
| Theme switch live | bg `#EEF3F7` → `#0B0C0E`, `data-theme` set, choice persisted, survives reload |
| Clock | ticks (`06:20:30 PM` → `06:20:32 PM`) |
| FAQ | expands/collapses with `aria-expanded` and `hidden` in sync |
| Hero video | source attached and playing after load |
| Active nav | `aria-current` applied on scroll |
| Unknown path | returns **404** with the custom page |
| Console + network errors during normal browsing | **none** |
| Transfer budget (first load, video excluded) | **254 KiB** of a 1229 KiB limit |
| Third-party requests on load | **0** |
| Horizontal scroll at 320/375/414/768/1024/1280/1440/1920 px | none — `scrollWidth == clientWidth` at every width |

Mobile performance is reported as a range because it varies with CDN and network
conditions: three consecutive runs gave 98, 98 and 100, and one cold run gave 93 with
FCP == LCP, which is first-connection latency rather than a page defect. All runs stay
inside AC-10 (≥ 90, LCP ≤ 2.5 s, CLS ≤ 0.1).

One defect was found by auditing the criteria rather than by testing: at 320 px the header
needed 307 px inside a 283 px content box, so the menu button hung 5 px past the clipped
edge and part of it could not be tapped. A `max-width: 23rem` block now tightens the
wordmark, theme switch and gaps; the button ends at 302 px and the regression is covered by
six new assertions.

## 9. Known limitations

- GitHub Pages serves the site at `/Old-Website-Restoration/`, so `og:image` and
  `canonical` are hard-coded to that absolute URL. If the repo is renamed or a custom
  domain is attached, those three URLs in `index.html` must be updated.
- `frame-ancestors` cannot be expressed via `<meta>` CSP; clickjacking protection would
  require response headers, which Pages does not allow.
- The hero video is attached by JS only. With JavaScript disabled the poster remains,
  which is a complete design, not a degraded one.
- With JavaScript disabled the mobile nav button is gone, so mobile users get the footer
  navigation instead of the header sheet. The desktop nav is deliberately *not* hidden in
  the `<noscript>` block, because it is plain links that need no scripting.
