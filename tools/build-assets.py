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


def portrait():
    src = Image.open(SRC / "me1.webp").convert("RGB")
    w, h = src.size
    target = 3 / 4
    new_w, new_h = (w, int(w / target)) if w / h > target else (int(h * target), h)
    left, top = (w - new_w) // 2, max(0, int((h - new_h) * 0.42))
    box = (max(0, left), max(0, top), min(w, left + new_w), min(h, top + new_h))
    cropped = src.crop(box)
    for width in (480, 780, 1120):
        img = cropped.resize((width, int(width / target)), Image.LANCZOS)
        img.save(IMG / f"portrait-{width}.webp", "WEBP", quality=82, method=6)
        img.save(IMG / f"portrait-{width}.avif", "AVIF", quality=55)
    tiny = cropped.resize((24, 32), Image.LANCZOS)
    tiny.save(IMG / "portrait-lqip.webp", "WEBP", quality=40)


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


def music():
    """The 2022 player's two songs, re-encoded for streaming. Provenance stays
    in assets-src/song.mp3 + song2.mp3; these are the shipped derivatives."""
    exe = ffmpeg()
    for src, dest in (("song.mp3", "as-it-was-1.mp3"), ("song2.mp3", "as-it-was-2.mp3")):
        subprocess.run(
            [exe, "-i", str(SRC / src), "-map_metadata", "-1",
             "-ac", "2", "-ar", "44100", "-b:a", "96k", "-y", str(MEDIA / dest)],
            check=True, capture_output=True)


def hero_video():
    exe = ffmpeg()
    base = [exe, "-ss", "3", "-t", "12", "-i", str(SRC / "train.mp4"),
            "-an", "-vf", "scale=1280:-2:flags=lanczos", "-r", "25",
            "-movflags", "+faststart"]
    subprocess.run(base + ["-c:v", "libx264", "-crf", "30", "-preset", "slow",
                           "-profile:v", "high", "-pix_fmt", "yuv420p",
                           "-y", str(MEDIA / "hero.mp4")], check=True, capture_output=True)
    subprocess.run(base + ["-c:v", "libvpx-vp9", "-crf", "40", "-b:v", "0",
                           "-row-mt", "1", "-y", str(MEDIA / "hero.webm")],
                   check=True, capture_output=True)


def icons():
    """The 2022 favicon, restored. assets-src/icon.png is byte-identical to the
    original site's /icon.png, so every size is cut straight from it — no
    redrawn replacement, which is what the owner asked for."""
    src = Image.open(SRC / "icon.png").convert("RGBA")
    (src.resize((32, 32), Image.LANCZOS).save(IMG / "favicon-32.png", "PNG", optimize=True))
    for size, name in ((192, "icon-192.png"), (512, "icon-512.png")):
        (src.resize((size, size), Image.LANCZOS)
            .quantize(colors=192, method=Image.FASTOCTREE)
            .save(IMG / name, "PNG", optimize=True))
    src.resize((16, 16), Image.LANCZOS).save(IMG / "favicon-16.png", "PNG", optimize=True)

    plate = Image.new("RGBA", src.size, (21, 23, 23, 255))
    plate.alpha_composite(src)
    plate.convert("RGB").resize((180, 180), Image.LANCZOS).save(
        IMG / "apple-touch-icon.png", "PNG", optimize=True)

    src.resize((256, 256), Image.LANCZOS).save(
        OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


def logo():
    src = Image.open(SRC / "ou-logo.webp").convert("RGBA")
    if src.width > 320:
        src = src.resize((320, round(src.height * 320 / src.width)), Image.LANCZOS)
    src.save(IMG / "ou-logo.webp", "WEBP", quality=88, method=6)


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
    steps = [portrait, poster, hero_video, music, icons, logo, og]
    for step in steps:
        step()
        print("ok:", step.__name__)
    for p in sorted(IMG.iterdir()):
        print(f"  img/{p.name:24} {p.stat().st_size/1024:7.1f} KB")
    for p in sorted(MEDIA.iterdir()):
        print(f"  media/{p.name:22} {p.stat().st_size/1024:7.1f} KB")
