#!/usr/bin/env python3
"""Reproducible asset pipeline: assets-src/ (originals) -> assets/ (shipped).

Run: python3 tools/build-assets.py
"""
import subprocess, sys, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT = pathlib.Path("assets-src"), pathlib.Path("assets")
IMG, MEDIA = OUT / "img", OUT / "media"
for d in (IMG, MEDIA):
    d.mkdir(parents=True, exist_ok=True)


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


# ---------------------------------------------------------------- portrait
def portrait():
    src = Image.open(SRC / "me1.webp").convert("RGB")
    w, h = src.size
    # 3:4 crop centred on the horizontal middle, anchored slightly above centre
    target = 3 / 4
    new_w, new_h = (w, int(w / target)) if w / h > target else (int(h * target), h)
    left, top = (w - new_w) // 2, max(0, int((h - new_h) * 0.42))
    box = (max(0, left), max(0, top), min(w, left + new_w), min(h, top + new_h))
    cropped = src.crop(box)
    for width in (480, 780, 1120):
        img = cropped.resize((width, int(width / target)), Image.LANCZOS)
        img.save(IMG / f"portrait-{width}.webp", "WEBP", quality=82, method=6)
        img.save(IMG / f"portrait-{width}.avif", "AVIF", quality=55)
    # LQIP placeholder (inline as a data URI in CSS)
    tiny = cropped.resize((24, 32), Image.LANCZOS)
    tiny.save(IMG / "portrait-lqip.webp", "WEBP", quality=40)


# ---------------------------------------------------------------- hero poster
def poster():
    exe = ffmpeg()
    for t, name in (("6", "hero-poster.webp"),):
        subprocess.run([exe, "-ss", t, "-i", str(SRC / "train.mp4"), "-frames:v", "1",
                        "-vf", "scale=1280:-2:flags=lanczos", "-q:v", "3",
                        "-y", str(IMG / "_poster.png")],
                       check=True, capture_output=True)
    im = Image.open(IMG / "_poster.png").convert("RGB")
    im.save(IMG / "hero-poster.webp", "WEBP", quality=70, method=6)
    im.save(IMG / "hero-poster.avif", "AVIF", quality=45)
    im.resize((im.width // 20, im.height // 20), Image.LANCZOS).save(
        IMG / "hero-poster-lqip.webp", "WEBP", quality=35)
    (IMG / "_poster.png").unlink()


# ---------------------------------------------------------------- hero video
def hero_video():
    exe = ffmpeg()
    # 12 s seamless-ish loop taken from a quiet stretch, no audio, faststart
    base = [exe, "-ss", "3", "-t", "12", "-i", str(SRC / "train.mp4"),
            "-an", "-vf", "scale=1280:-2:flags=lanczos", "-r", "25",
            "-movflags", "+faststart"]
    subprocess.run(base + ["-c:v", "libx264", "-crf", "30", "-preset", "slow",
                           "-profile:v", "high", "-pix_fmt", "yuv420p",
                           "-y", str(MEDIA / "hero.mp4")], check=True, capture_output=True)
    subprocess.run(base + ["-c:v", "libvpx-vp9", "-crf", "40", "-b:v", "0",
                           "-row-mt", "1", "-y", str(MEDIA / "hero.webm")],
                   check=True, capture_output=True)


# ---------------------------------------------------------------- logo + monogram
def monogram(size=64, radius=14, bg="#14171C", fg="#F4F0E8", accent="#C3341F"):
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size * 4
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius * 4, fill=bg)
    d.rectangle((0, 0, s - 1, int(s * 0.055)), fill=accent)
    try:
        f = ImageFont.truetype(str(pathlib.Path("/usr/share/fonts") / "truetype/dejavu/DejaVuSerif-Bold.ttf"), int(s * 0.46))
    except OSError:
        f = ImageFont.load_default()
    text = "JT"
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text(((s - (r - l)) / 2 - l, (s - (b - t)) / 2 - t - s * 0.02), text, font=f, fill=fg)
    return im


def icons():
    monogram(64).resize((32, 32), Image.LANCZOS).save(IMG / "favicon-32.png")
    monogram(180).resize((180, 180), Image.LANCZOS).save(IMG / "apple-touch-icon.png")
    monogram(192).resize((192, 192), Image.LANCZOS).save(IMG / "icon-192.png")
    monogram(512).resize((512, 512), Image.LANCZOS).save(IMG / "icon-512.png")
    (OUT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="JT">'
        '<rect width="64" height="64" rx="14" fill="#14171C"/>'
        '<rect width="64" height="3.6" rx="1" fill="#C3341F"/>'
        '<text x="32" y="44" text-anchor="middle" font-family="Georgia,serif" font-size="30" '
        'font-weight="700" fill="#F4F0E8">JT</text></svg>\n')


def logo():
    src = Image.open(SRC / "ou-logo.webp").convert("RGBA")
    if src.width > 320:
        src = src.resize((320, round(src.height * 320 / src.width)), Image.LANCZOS)
    src.save(IMG / "ou-logo.webp", "WEBP", quality=88, method=6)


# ---------------------------------------------------------------- og card
def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#F4F0E8")
    d = ImageDraw.Draw(im)
    mono_b = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    mono_r = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    d.rectangle((0, 0, 14, H), fill="#C3341F")
    for x in range(0, W, 60):
        d.line((x, 0, x, 10), fill="#14171C", width=1)
    big = ImageFont.truetype(mono_b, 108)
    small = ImageFont.truetype(mono_r, 30)
    meta = ImageFont.truetype(mono_r, 22)
    d.text((84, 170), "Junior Thanh", font=big, fill="#14171C")
    d.text((84, 306), "Văn Trung Thành — K23 TM", font=small, fill="#5A5F68")
    d.line((84, 380, 700, 380), fill="#14171C", width=2)
    d.text((84, 410), "HCMC-OU · Sinh viên năm hai", font=meta, fill="#14171C")
    d.text((84, 446), "đại học Mở TP.Hồ Chí Minh", font=meta, fill="#14171C")
    d.text((84, 540), "juniorthanh09.com", font=meta, fill="#C3341F")
    im.save(IMG / "og.png", "PNG", optimize=True)


if __name__ == "__main__":
    steps = [portrait, poster, hero_video, icons, logo, og]
    for step in steps:
        step()
        print("ok:", step.__name__)
    for p in sorted(IMG.iterdir()):
        print(f"  img/{p.name:24} {p.stat().st_size/1024:7.1f} KB")
    for p in sorted(MEDIA.iterdir()):
        print(f"  media/{p.name:22} {p.stat().st_size/1024:7.1f} KB")
