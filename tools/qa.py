#!/usr/bin/env python3
"""Local QA sweep for the static site.

Usage:  python3 tools/qa.py [base_url] [outdir]
Checks content fidelity, console/network health, responsive overflow,
interactive behaviour, aria wiring, and captures screenshots.
"""
import json, pathlib, re, sys, html
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/"
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/qa")
OUT.mkdir(parents=True, exist_ok=True)

failures, notes = [], []


def check(cond, msg):
    (notes if cond else failures).append(("PASS" if cond else "FAIL") + " " + msg)
    return cond


# Quotes and attribution must be byte-faithful to the 2022 source, not "improved".
FIDELITY = [
    '"Gió đẩy chiều nào thì ta theo chiều đó.',        # straight quote, not "
    'điều chân quý nhất rồi."',
    '"Chúng ta có thể không thay đổi được quá khứ.',
    '"Khi nghiệp vụ không chỉ nằm ở sự chuyên nghiệp',
    '"Mục tiêu cá nhân là thứ gì đó có thể thúc đẩy',
    '"Học, học nữa, học mãi.',
    '"Nếu không có mục tiêu thì hãy có động lực.',
    '- Junior Thành -',                                # not em-dashes
    'HTML,CSS, JavaScript',                            # original spacing quirk
    'cuộc sống .Còn lại mọi quyết định',               # original spacing quirk
    'trong thời gian rảnh .',                          # original spacing quirk
]

# Every normative string from docs/ai-dlc/02-content-inventory.md that must appear.
REQUIRED = [
    "Junior Thành", "Văn Trung Thành - K23", "HCMC-OU",
    "Sinh viên năm hai tại trường đại học Mở TP.HCM", "Thời gian làm việc: 9h30-23h",
    "Gió đẩy chiều nào thì ta theo chiều đó",
    "Ngành học", "Công nghệ thông tin", "Chuyên ngành", "ATTT & ĐGHT",
    "Chứng chỉ", "Level B1 Certificate", "Sở thích", "Nghe nhạc, Coding",
    "Trình độ", "HTML,CSS, JavaScript", "Khác", "Sẵn sàng hỗ trợ",
    "Giới thiệu", "Mình tên là Thành (Biệt danh: Junior Thành)",
    "Hiện tại mình đang là sinh viên năm hai của trường đại học Mở TP.Hồ Chí Minh.",
    "chủ yếu Billie Eilish và Imagine Dragons",
    "tiếp tục phấn đấu cải thiện kỹ năng chuyên ngành",
    "Câu nói của mình",
    "Chúng ta có thể không thay đổi được quá khứ",
    "Podcast - Blogger", "mình chưa xem xét đến việc viết Blog lại",
    "Học kì 2 - Cơ sở: Nhà Bè.",
    "Khi nghiệp vụ không chỉ nằm ở sự chuyên nghiệp mà còn là sự phá cách",
    "Nghiệp vụ bản thân",
    "Web Designer", "Thiết kế website", "Bookshop 360",
    "Project Management", "Quản lý dự án", "Firewall pfSense",
    "Psychology", "Tâm sự và trò chuyện",
    "Blogging", "Viết lách", "mình viết khá là kì cục",
    "Mục tiêu cá nhân", "Thứ gì định nghĩa mình?",
    "Nghiệp vụ", "Kỹ năng", "Ngôn ngữ", "Giao tiếp", "Mục tiêu",
    "Học, học nữa, học mãi",
    "Nếu không có mục tiêu thì hãy có động lực",
    "FAQ", "Tại đây mình sẽ giải đáp các câu hỏi mà mình thường gặp nhé.",
    "Ý nghĩa tên Junior Thành?", "Vì trình độ của mình chưa có tốt lắm chỉ tạm ở Junior thôi",
    "Người mong chờ?", "Hiện tại thì mình còn độc thân và chưa có người mong chờ",
    "Cách hoạt động Website?", "Mình hiện tại đang thử nghiệm làm website này trên Next.js",
    "Trường đại học?", "Hiện tại thì mình đang học tại trường đại học Mở TP.HCM",
    "Bạn có mấy dự án?", "Hiện tại mình có hai dự án chính là Bookshop 360 và đây",
    "Bạn tính học ATTT?", "Mình đang xem xét học thêm chuyên ngành là ATTT",
    "Đại học Mở TP.HCM?", "Để biết thêm về trường thì cái này bạn phải tự tìm hiểu nhé",
    "Địa điểm yêu thích?", "Chủ yếu là các quán cafe như Guta hoặc Highland nhé",
    "Sở thích bí mật?", "Này mình có á nhưng bạn lấy được lòng tin mình đã hehe",
    "Mạng xã hội?", "Hiện tại, mình hoạt động trên nền tảng Facebook và LinkedIn",
    "P/S: Ngoài ra còn nhiều thông tin khác nữa",
    "Sinh viên trường đại học Mở TP.Hồ Chí Minh",
    "Chúc mọi người một ngày làm việc năng suất",
    "Sổ tay sinh viên", "Fanpage", "Tuyển sinh",
    "Vậy đến đây là kết thúc rồi",
    "Facebook", "Linkedin", "Điều hướng", "Liên kết ngoài",
    "Wikipedia", "Youtube",
    "Mọi quyền được bảo lưu", "Thời gian hiện tại:",
    "Ý tưởng Design:", "The Art Of Documentary",
]

EXTERNAL_LINKS = [
    "https://ou.edu.vn/",
    "https://www.oucommunity.dev/",
    "https://www.facebook.com/profile.php?id=100066781932277",
    "https://tuyensinh.ou.edu.vn/",
    "https://www.facebook.com/profile.php?id=61551715783777",
    "https://www.linkedin.com/in/juniorthanh09/",
    "https://thanh09junior.github.io/BookShop360_ThanhAndPhong/",
    "https://wikipedia.vn/",
    "https://juniorthanh09.com/",
    "https://www.youtube.com/@Juniorthanh09_OU",
    "https://theartofdocumentary.com/",
]


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  device_scale_factor=1, locale="vi-VN")
        page = ctx.new_page()
        console, bad = [], []
        page.on("console", lambda m: console.append((m.type, m.text)))
        page.on("pageerror", lambda e: bad.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: bad.append(f"failed: {r.url} {r.failure}"))
        page.on("response", lambda r: bad.append(f"HTTP {r.status}: {r.url}")
                if r.status >= 400 else None)

        page.goto(BASE, wait_until="networkidle")
        page.wait_for_timeout(600)

        check(not bad, f"no failed requests / HTTP errors ({bad[:5]})")
        errs = [c for c in console if c[0] == "error"]
        check(not errs, f"no console errors ({errs[:5]})")

        # ── structure ──
        for sid in ["trang-chu", "gioi-thieu", "nghiep-vu", "muc-tieu", "faq"]:
            check(page.locator(f"#{sid}").count() == 1, f"section #{sid} exists")
        for aid in ["about", "role", "goal", "FAQ"]:
            check(page.locator(f"#{aid}").count() >= 1, f"alias anchor #{aid} exists")
        check(page.locator("h1").count() == 1, "exactly one h1")
        check(page.locator("main").count() == 1, "one main landmark")
        check(page.locator("header.site-header").count() == 1, "one header")
        check(page.locator("footer.site-footer").count() == 1, "one site footer")
        check(page.locator('html[lang="vi"]').count() == 1, "lang=vi")

        # ── content ──
        # read raw DOM text (unaffected by text-transform) plus the DOM alt/labels
        text = page.evaluate("document.body.textContent || ''")
        flat = re.sub(r"\s+", " ", text)
        missing = [s for s in REQUIRED if re.sub(r"\s+", " ", s) not in flat]
        check(not missing, f"all normative copy present (missing: {missing})")

        offspec = [s for s in FIDELITY if s not in text]
        check(not offspec, f"quotes/attribution verbatim, not restyled (differs: {offspec})")
        check("\u201c" not in text and "\u201d" not in text,
              "no smart quotes substituted for the original straight quotes")

        # ── FAQ ──
        check(page.locator(".faq-item__trigger").count() == 10, "10 FAQ triggers")
        first = page.locator(".faq-item__trigger").first
        check(first.get_attribute("aria-expanded") == "false", "FAQ starts closed")
        panel_id = first.get_attribute("aria-controls")
        check(page.locator(f"#{panel_id}").is_hidden(), "FAQ panel hidden initially")
        first.click()
        page.wait_for_timeout(150)
        check(first.get_attribute("aria-expanded") == "true", "FAQ opens")
        check(page.locator(f"#{panel_id}").is_visible(), "FAQ panel visible after click")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        check(first.get_attribute("aria-expanded") == "false", "Escape closes FAQ")

        # ── theme ──
        html_el = page.locator("html")
        page.click('[data-set-theme="then"]')
        page.wait_for_timeout(350)
        check(html_el.get_attribute("data-theme") == "then", "theme switches to then")
        check(page.locator('[data-set-theme="then"]').get_attribute("aria-pressed") == "true",
              "then button aria-pressed")
        bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
        check(bg in ("rgb(11, 12, 14)",), f"then canvas applied ({bg})")
        page.screenshot(path=str(OUT / "then-desktop.png"), full_page=True)
        page.click('[data-set-theme="now"]')
        page.wait_for_timeout(350)
        check(html_el.get_attribute("data-theme") == "now", "theme switches back to now")

        # ── external links ──
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
        for url in EXTERNAL_LINKS:
            check(any(h.rstrip("/") == url.rstrip("/") for h in hrefs), f"link preserved: {url}")
        unsafe = page.eval_on_selector_all(
            "a[target='_blank']",
            "els => els.filter(e => !(e.rel||'').includes('noopener')).map(e => e.href)")
        check(not unsafe, f"all _blank links have noopener ({unsafe[:3]})")

        # ── images ──
        no_dim = page.eval_on_selector_all(
            "img", "els => els.filter(e => !e.getAttribute('width') || !e.getAttribute('height')).map(e => e.src)")
        check(not no_dim, f"all images have width/height ({no_dim[:3]})")
        broken = page.eval_on_selector_all(
            "img", "els => els.filter(e => e.complete && e.naturalWidth === 0).map(e => e.src)")
        check(not broken, f"no broken images ({broken[:3]})")
        alts = page.eval_on_selector_all("img", "els => els.map(e => e.getAttribute('alt'))")
        check(all(a is not None for a in alts), "every img has an alt attribute")

        # ── clock ──
        clock = page.locator("#hero-clock").inner_text()
        check(bool(re.match(r"\d{2}:\d{2}:\d{2} (AM|PM)$", clock)), f"hero clock formatted ({clock})")

        # ── video lazily attached ──
        srcs = page.eval_on_selector("#hero-video", "v => Array.from(v.querySelectorAll('source')).map(s=>s.src)")
        check(len(srcs) >= 1, f"hero video sources attached ({len(srcs)})")

        # ── every referenced local asset actually resolves ──
        import urllib.parse
        refs = page.eval_on_selector_all(
            "link[href], script[src], img[src], source[src], source[srcset], video[data-src], video[data-src-webm]",
            """els => els.flatMap(e => {
                 const out = [];
                 if (e.href && e.tagName === 'LINK') out.push(e.href);
                 if (e.src) out.push(e.src);
                 if (e.dataset && e.dataset.src) out.push(e.dataset.src);
                 if (e.dataset && e.dataset.srcWebm) out.push(e.dataset.srcWebm);
                 if (e.srcset) e.srcset.split(',').forEach(p => out.push(p.trim().split(' ')[0]));
                 return out;
               })""")
        asset_refs = [r for r in refs if BASE.rstrip("/").split("//")[-1] in r]
        broken_refs = [r for r in asset_refs if "fonts.googleapis" not in r and
                       page.request.get(r).status >= 400]
        check(not broken_refs, f"every local asset reference resolves (broken: {broken_refs[:5]})")

        # ── security posture ──
        html_src = page.content()
        check(html_src.count("<script") == 1, "exactly one script tag")
        check('Content-Security-Policy' in html_src, "CSP meta present")
        check("src=\"/" not in html_src, "no root-absolute src")
        no_inline = page.eval_on_selector_all("script", "els => els.filter(e=>!e.src).length")
        check(no_inline == 0, "no inline scripts")

        # ── desktop screenshot ──
        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "now-desktop.png"), full_page=True)
        page.screenshot(path=str(OUT / "now-hero.png"))

        # ── responsive ──
        for w, h in [(320, 700), (375, 812), (768, 1024), (1024, 768), (1440, 900), (1920, 1080)]:
            page.set_viewport_size({"width": w, "height": h})
            page.wait_for_timeout(250)
            sw = page.evaluate("document.documentElement.scrollWidth")
            check(sw <= w, f"no horizontal overflow at {w}px (scrollWidth={sw})")

        # ── mobile menu ──
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(250)
        page.evaluate("window.scrollTo(0,0)")
        toggle = page.locator("#menu-toggle")
        check(toggle.is_visible(), "menu toggle visible on mobile")
        toggle.click()
        page.wait_for_timeout(250)
        check(toggle.get_attribute("aria-expanded") == "true", "menu opens")
        check(page.locator("#mobile-menu").is_visible(), "mobile menu visible")
        page.screenshot(path=str(OUT / "mobile-menu.png"))
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        check(toggle.get_attribute("aria-expanded") == "false", "Escape closes menu")

        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "now-mobile.png"), full_page=True)
        page.click('[data-set-theme="then"]')
        page.wait_for_timeout(400)
        page.evaluate("window.scrollTo(0,0)")
        page.screenshot(path=str(OUT / "then-mobile.png"), full_page=True)

        # ── favicon: the 2022 icon, not a redrawn mark ──
        page.set_viewport_size({"width": 1440, "height": 900})
        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(200)
        fav = page.evaluate(
            """() => {
              const links = [...document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')];
              return links.map(l => ({ rel: l.rel, href: l.getAttribute('href') }));
            }""")
        check(len(fav) >= 3, f"favicon: {len(fav)} icon links declared")
        check(not any("favicon.svg" in f["href"] for f in fav),
              "favicon: the invented SVG monogram is gone")
        served = page.evaluate(
            """async (urls) => {
              const out = [];
              for (const u of urls) {
                const r = await fetch(u, { cache: "no-store" });
                const b = await r.blob();
                out.push({ url: u, ok: r.ok, type: b.type, size: b.size });
              }
              return out;
            }""", [f["href"] for f in fav if f["href"]])
        check(all(s["ok"] for s in served),
              f"favicon: every declared icon resolves ({len(served)} fetched)")
        check(all(s["size"] > 100 for s in served), "favicon: icons are non-empty files")
        check(any(s["type"] == "image/png" for s in served), "favicon: a PNG icon is served")
        # a 32px favicon cut from the 2022 artwork is mostly amber-on-transparent;
        # a redrawn dark plate would read as opaque. Sample its alpha coverage.
        cov = page.evaluate(
            """async (url) => {
              const img = new Image();
              img.src = url;
              await img.decode();
              const c = document.createElement('canvas');
              c.width = img.naturalWidth; c.height = img.naturalHeight;
              const g = c.getContext('2d');
              g.drawImage(img, 0, 0);
              const d = g.getImageData(0, 0, c.width, c.height).data;
              let opaque = 0, amber = 0;
              for (let i = 0; i < d.length; i += 4) {
                if (d[i + 3] > 200) opaque++;
                if (d[i] > 180 && d[i + 1] > 140 && d[i + 2] < 140 && d[i + 3] > 200) amber++;
              }
              const n = d.length / 4;
              return { opaquePct: opaque / n, amberPct: amber / n, w: c.width, h: c.height };
            }""", next(f["href"] for f in fav if "favicon-32" in (f["href"] or "")))
        check(cov["w"] == 32 and cov["h"] == 32, f"favicon: 32px icon is 32×32 ({cov['w']}×{cov['h']})")
        check(cov["amberPct"] > 0.15,
              f"favicon: carries the 2022 amber glyph ({cov['amberPct']*100:.0f}% of pixels)")
        check(cov["opaquePct"] < 0.95,
              f"favicon: transparent background kept, not an opaque plate ({cov['opaquePct']*100:.0f}% opaque)")

        # ── music player: present, inert until pressed, then two chained tracks ──
        mt = page.locator("#music-toggle")
        check(mt.is_visible(), "music: header play button is visible")
        check(mt.get_attribute("aria-pressed") == "false",
              "music: starts in the paused state")
        check(mt.get_attribute("aria-label") not in (None, ""),
              "music: control has an accessible name")
        check(page.eval_on_selector_all("audio", "els => els.length") == 2,
              "music: two tracks wired (as in 2022: song.mp3 then song2.mp3)")
        check(page.evaluate(
            """() => [...document.querySelectorAll('audio')]
                     .every(a => a.preload === 'none' && !a.getAttribute('src'))"""),
            "music: no track is fetched until the visitor presses play")
        check(page.title().strip() == "Junior Thành",
              "music: document.title untouched before playing")

        page.click("#music-toggle")
        page.wait_for_function(
            "() => !document.getElementById('music-a').paused", timeout=5000)
        page.wait_for_timeout(1600)
        check(mt.get_attribute("aria-pressed") == "true",
              "music: pressing play sets aria-pressed=true")
        playing_title = page.title()
        check(bool(re.match(r"^\d+:\d{2} / \d+:\d{2}$", playing_title)),
              f"music: title shows elapsed / total while playing ({playing_title!r})")
        check(page.eval_on_selector("#music-a", "a => a.currentTime > 0"),
              "music: the first track actually advanced")
        check(page.evaluate(
            """() => {
              const p = document.querySelector('.music-toggle__icon--play');
              const q = document.querySelector('.music-toggle__icon--pause');
              return getComputedStyle(p).display === 'none' && getComputedStyle(q).display !== 'none';
            }"""), "music: icon swaps to pause while playing")
        check(page.eval_on_selector("#music-a", "a => a.volume < 1"),
              "music: plays at a reduced volume, not full blast")

        page.click("#music-toggle")
        page.wait_for_timeout(500)
        check(mt.get_attribute("aria-pressed") == "false",
              "music: pressing again pauses")
        check(page.evaluate(
            """() => { const a = document.getElementById('music-a'), b = document.getElementById('music-b');
                     return a.paused && b.paused; }"""), "music: both tracks are stopped")
        check(page.title().strip() == "Junior Thành",
              "music: document.title restored on pause")
        page.screenshot(path=str(OUT / "music-paused.png"), clip={"x": 0, "y": 0, "width": 1440, "height": 120})

        # chaining and wrap — the 2022 player played song.mp3 then song2.mp3.
        # Seeking to the end is the only practical way to reach `ended` in a
        # test, and it is exactly the code path the chain runs through.
        page.click("#music-toggle")
        page.wait_for_function("() => !document.getElementById('music-a').paused", timeout=5000)
        page.evaluate("""() => { const a = document.getElementById('music-a');
                             a.currentTime = Math.max(0, a.duration - 0.4); }""")
        page.wait_for_function("() => !document.getElementById('music-b').paused", timeout=10000)
        page.wait_for_timeout(600)
        check(page.evaluate(
            """() => { const a = document.getElementById('music-a'), b = document.getElementById('music-b');
                     return a.paused && !b.paused; }"""),
            "music: track 1 chains into track 2")
        check(mt.get_attribute("aria-pressed") == "true",
              "music: button stays pressed across the track change")
        page.evaluate("""() => { const b = document.getElementById('music-b');
                             b.currentTime = Math.max(0, b.duration - 0.4); }""")
        page.wait_for_function(
            """() => { const a = document.getElementById('music-a'), b = document.getElementById('music-b');
                    return !a.paused && b.paused; }""", timeout=10000)
        check(mt.get_attribute("aria-pressed") == "true",
              "music: the pair loops back to track 1")
        page.click("#music-toggle")
        page.wait_for_timeout(400)

        # rapid toggling must not leave aria-pressed claiming the opposite
        page.click("#music-toggle"); page.click("#music-toggle"); page.click("#music-toggle")
        page.wait_for_timeout(1200)
        consistent = page.evaluate(
            """() => { const a = document.getElementById('music-a'), b = document.getElementById('music-b');
                     const pressed = document.getElementById('music-toggle').getAttribute('aria-pressed') === 'true';
                     return pressed === (!a.paused || !b.paused); }""")
        check(consistent, "music: rapid clicks leave aria-pressed matching the audio")
        if page.evaluate("() => [...document.querySelectorAll('audio')].some(a => !a.paused)"):
            page.click("#music-toggle")
        page.wait_for_timeout(400)

        # ── hero composition: the 2022 prototype's shape, not the frosted plate ──
        check(page.locator(".hero__plate").count() == 0,
              "hero: frosted plate removed")
        check(page.locator(".hero__badge").count() == 0,
              "hero: rotating badge removed")
        check(page.locator(".hero__scroll").count() == 0,
              "hero: scroll cue removed")
        order = page.evaluate(
            """() => {
              const layout = document.querySelector('.hero__layout');
              return [...layout.children].map(e => e.className.split(' ')[0]);
            }""")
        check(order == ["hero__name", "hero__rule", "hero__columns"],
              f"hero: name → hairline → columns, in that order ({order})")
        geom = page.evaluate(
            """() => {
              const r = (s) => { const e = document.querySelector(s);
                const b = e.getBoundingClientRect();
                return { x: b.x, y: b.y, w: b.width, h: b.height, right: b.right }; };
              const title = r('.hero__title'), rule = r('.hero__rule');
              const cols = [...document.querySelectorAll('.hero__col')].map(e => {
                const b = e.getBoundingClientRect(); return { x: b.x, w: b.width }; });
              return { title, rule, cols, vw: innerWidth,
                       nameX: r('.hero__name').x + parseFloat(getComputedStyle(document.querySelector('.hero__name')).paddingLeft) };
            }""")
        check(abs(geom["title"]["x"] - geom["nameX"]) < 2,
              "hero: title starts at the indented name block's text edge")
        check(geom["title"]["x"] > geom["vw"] * 0.15,
              f"hero: title indented from the left edge, as in 2022 ({round(geom['title']['x'])}px of {geom['vw']})")
        check(geom["rule"]["w"] > geom["vw"] * 0.9,
              f"hero: hairline runs the full width ({round(geom['rule']['w'])} of {geom['vw']})")
        check(geom["rule"]["y"] > geom["title"]["y"],
              "hero: hairline sits below the name block")
        check(len(geom["cols"]) == 4, f"hero: four fact columns, as in 2022 ({len(geom['cols'])})")
        check(geom["cols"][0]["x"] < geom["title"]["x"],
              "hero: the column row starts left of the indented title, as in 2022")
        check(geom["title"]["h"] < 100,
              f"hero: 'Junior Thành' fits on one line ({round(geom['title']['h'])}px tall)")
        hero_text = page.evaluate(
            """() => {
              const t = document.querySelector('.hero__title');
              const b = document.querySelector('.hero__byline');
              /* columns 3-4 are <dl> fact lists, so their leading label is a <dt> */
              const cols = [...document.querySelectorAll('.hero__col')].map(c => {
                const h = c.querySelector('.hero__col-title');
                const dt = c.querySelector('.facts dt');
                return (h || dt).textContent.trim();
              });
              return { title: t.textContent.replace(/\\s+/g,' ').trim(),
                       byline: b.textContent.replace(/\\s+/g,' ').trim(),
                       cols };
            }""")
        check(hero_text["title"] == "Junior Thành",
              f"hero: title reads 'Junior Thành' verbatim ({hero_text['title']!r})")
        check(hero_text["byline"].startswith("Văn Trung Thành - K23"),
              f"hero: byline verbatim ({hero_text['byline']!r})")
        check(hero_text["cols"] == ["HCMC-OU", "Châm ngôn", "Ngành học", "Sở thích"],
              f"hero: the four column headings are the original's ({hero_text['cols']})")
        check(page.locator(".hero .facts").count() == 2,
              "hero: both fact lists kept (3 rows each)")

        # ── reduced motion ──
        rm = browser.new_context(viewport={"width": 1280, "height": 900},
                                 reduced_motion="reduce")
        rp = rm.new_page()
        rp.goto(BASE, wait_until="networkidle")
        rp.wait_for_timeout(400)
        vsrc = rp.eval_on_selector("#hero-video", "v => v.querySelectorAll('source').length")
        check(vsrc == 0, "reduced motion: no video sources attached")
        vis = rp.eval_on_selector_all(".reveal", "els => els.filter(e=>getComputedStyle(e).opacity!=='1').length")
        check(vis == 0, f"reduced motion: all reveal content visible ({vis} hidden)")
        rp.screenshot(path=str(OUT / "reduced-motion.png"), full_page=True)
        rm.close()

        # ── no JavaScript: the page must still be complete ──
        nj = browser.new_context(viewport={"width": 1440, "height": 900},
                                 java_script_enabled=False, locale="vi-VN")
        np = nj.new_page()
        np.goto(BASE, wait_until="load")
        np.wait_for_timeout(300)
        check(np.locator(".nav a").first.is_visible(),
              "no-JS: desktop header nav still usable (it needs no scripting)")
        check(np.locator(".faq-item__panel").first.is_visible(),
              "no-JS: FAQ answers are readable without the accordion")
        check(np.locator(".site-footer nav a").count() >= 5,
              "no-JS: footer navigation present as a fallback")
        check(np.locator(".hero__title").is_visible(),
              "no-JS: hero renders (poster, not video)")
        nj.close()

        # ── narrowest supported width: header controls must stay inside ──
        for w in (320, 360, 375):
            nc = browser.new_context(viewport={"width": w, "height": 800}, locale="vi-VN")
            wp = nc.new_page()
            wp.goto(BASE, wait_until="networkidle")
            wp.wait_for_timeout(400)
            over = wp.evaluate(
                """(vw) => {
                  const right = (s) => {
                    const e = document.querySelector(s);
                    return e ? Math.round(e.getBoundingClientRect().right) : 0;
                  };
                  return { vw,
                           menu: right('.menu-toggle'),
                           tools: right('.header-tools'),
                           scroll: document.documentElement.scrollWidth,
                           client: document.documentElement.clientWidth };
                }""", w)
            check(over["menu"] <= w and over["tools"] <= w,
                  f"{w}px: header controls inside viewport (menu {over['menu']}, tools {over['tools']} <= {w})")
            check(over["scroll"] <= over["client"] + 1,
                  f"{w}px: no horizontal scroll ({over['scroll']} vs {over['client']})")
            nc.close()

        # ── per-section screenshots for design review ──
        ctx2 = browser.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        p2 = ctx2.new_page()
        p2.goto(BASE, wait_until="networkidle")
        p2.wait_for_timeout(500)
        for sid in ["trang-chu", "gioi-thieu", "nghiep-vu", "muc-tieu", "faq"]:
            el = p2.locator(f"#{sid}")
            el.scroll_into_view_if_needed()
            p2.wait_for_timeout(500)
            el.screenshot(path=str(OUT / f"section-{sid}.png"))
        p2.locator("footer.site-footer").scroll_into_view_if_needed()
        p2.wait_for_timeout(400)
        p2.locator("footer.site-footer").screenshot(path=str(OUT / "section-footer.png"))
        ctx2.close()
        browser.close()


run()

print("\n===== PASSES =====")
for n in notes:
    print(" ", n)
if failures:
    print("\n===== FAILURES =====")
    for f in failures:
        print(" ", f)
print(f"\n{len(notes)} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
