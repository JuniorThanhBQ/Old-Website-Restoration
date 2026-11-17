# 06 — Operations (deploy, run, maintain)

## Run locally

```bash
python3 -m http.server 8080     # then open http://localhost:8080/
```

No build step, no dependencies. The repository *is* the deployable artefact.

## Deploy

`.github/workflows/pages.yml` runs on every push to `main`:

1. **verify** — five guards that fail the build rather than ship a broken site:
   required files exist; no root-absolute internal URLs (they would 404 on a project
   site); no inline `<script>`; no third-party asset host; no credential-like strings.
   Then it stages `_site/` and enforces a 12 MB artefact budget.
2. **deploy** — publishes `_site/` via GitHub Pages.
3. **smoke** — curls the live URL and asserts 200 for the document plus CSS, JS, fonts,
   hero poster, `robots.txt` and `404.html`.

### One-time repository setting

Pages must be pointed at "GitHub Actions" as the source, not "Deploy from a branch".
That is a repository-settings action; the API returns 404 until it is done:

```
Settings → Pages → Build and deployment → Source: GitHub Actions
```

Until then the workflow's `deploy` job fails at `configure-pages`.

## Rebuild derived assets

Both tools are reproducible and idempotent; run them after changing source media, copy,
or the design tokens.

```bash
python3 tools/build-assets.py     # images + video, from assets-src/
python3 tools/build-fonts.py      # subsetted webfonts + fonts.css
python3 tools/build-fonts.py --check   # coverage gate only (no network) — CI uses this
```

`build-fonts.py --check` is the important one: it re-derives the required character set
from the shipped HTML and fails if any glyph would be missing. **If you add copy, run it.**
Without it, a new Vietnamese character could silently render as tofu, because the fonts
are subset deliberately.

The audio is rebuilt by the same `build-assets.py`: `assets-src/song.mp3` →
`assets/media/as-it-was.mp3` (Then room) and `assets-src/song2.mp3` →
`assets/media/everything-i-wanted.mp3` (Now room), metadata stripped at 96 kbps. The workflow's
smoke step asserts both files return 200, so renaming one without updating the other fails
the deploy rather than shipping a silent player.

## Where the theme lives

Three places, all of which must agree when a palette changes:

1. `assets/css/style.css` — the `[data-theme="now"|"then"]` token blocks. Everything visual reads
   from these; there are no component-level colour literals outside the print and 404 blocks.
2. `assets/js/main.js` — `applyTheme()` writes `<meta name="theme-color">` (`#EEF3F7` / `#0B0C0E`).
3. `<meta name="theme-color">` in `index.html`, `404.html` and `site.webmanifest` — the value a
   browser uses before the script runs.

## Verify

```bash
python3 tools/qa.py               # 163 checks; non-zero exit on failure
```

Local QA needs Playwright once: `pip install playwright && python3 -m playwright install chromium`.

## Routine maintenance

| Task | Action |
|---|---|
| Add or change copy | Edit `index.html`, then `python3 tools/build-fonts.py` and `python3 tools/qa.py`. |
| Change a colour/space token | Edit the token blocks at the top of `assets/css/style.css` only — no other file holds a raw colour. |
| Replace the portrait or video | Drop the new file in `assets-src/`, then `python3 tools/build-assets.py`. |
| Re-run performance | Lighthouse mobile preset; the budget is documented in `05-verification.md`. |

## Rollback

Every deploy is a commit on `main`. `git revert <sha>` and push — the workflow
redeploys the reverted tree. There is no database and no runtime state, so rollback is
only ever a file-state question.

## Cost and longevity

Static hosting on Pages, zero dependencies, zero third-party requests at runtime. The
site has no package manifest to rot: it will still open from a filesystem in ten years.
