# Verification — acceptance evidence

Every claim below was produced by running the command shown, against the local build
served by `python3 -m http.server 8080` in the repository root. Nothing here is estimated.

Reproduce with:

```bash
python3 tools/build-fonts.py --check   # font glyph coverage gate
python3 tools/qa.py                    # 63 functional/structural checks
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
| First Contentful Paint | 1.5 s |
| Largest Contentful Paint | 2.5 s |
| Total Blocking Time | 70 ms |
| Cumulative Layout Shift | **0** |
| Speed Index | 1.5 s |
| Total byte weight | 278 KiB |

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

Run with all ten FAQ panels forced open so collapsed content is audited too:

| Theme | Viewport | Violations | Passing rules |
|---|---|---|---|
| Now | 1440×900 | **0** | 42 |
| Now | 375×812 | **0** | 42 |
| Then | 1440×900 | **0** | 42 |
| Then | 375×812 | **0** | 42 |

## 3. Contrast — measured from composited pixels, not assumed

The hero sits on video, so ratio was computed from real screenshot pixels behind each
text block, not from declared CSS colours.

| Element | Ratio | Required |
|---|---|---|
| Hero title | 17.3 | 3.0 (large) |
| Hero standfirst | 17.4 | 3.0 (large) |
| Hero motto | 17.1 | 4.5 |
| Fact list `dt` | 18.9 | 4.5 |
| Fact list `dd` | 16.1 | 4.5 |
| Byline | 19.3 | 4.5 |
| Working hours | 19.1 | 4.5 |
| Clock label | 18.5 | 4.5 |
| Clock value (amber) | 9.6 | 4.5 |
| Eyebrow (amber) | 11.1 | 4.5 |

Body copy on canvas: 15.8 (Now) / 17.1 (Then). Muted `--ink-soft`: 5.65 / 8.77.
All secondary text also clears 4.5.

The frosted hero plate was additionally verified to be *visible as an object*: media
behind it renders at RGB ≈ 8–13, the plate at 19–33, with a 75–88 edge highlight.

## 4. Structural and content fidelity (`tools/qa.py`)

63 checks, all passing. Coverage:

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
- **Responsive** — no horizontal overflow at 320 / 375 / 768 / 1024 / 1440 / 1920 px.
- **Reduced motion** — no video sources attached, all revealed content visible.
- **Security posture** — exactly one `<script>` tag and it has `src`; CSP meta present;
  no root-absolute `src`; no inline scripts.

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
| D1 | Background-music player omitted | Third-party commercial recordings; autoplay audio also fails the UX bar. |
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

## 9. Known limitations

- GitHub Pages serves the site at `/Old-Website-Restoration/`, so `og:image` and
  `canonical` are hard-coded to that absolute URL. If the repo is renamed or a custom
  domain is attached, those three URLs in `index.html` must be updated.
- `frame-ancestors` cannot be expressed via `<meta>` CSP; clickjacking protection would
  require response headers, which Pages does not allow.
- The hero video is attached by JS only. With JavaScript disabled the poster remains,
  which is a complete design, not a degraded one.
