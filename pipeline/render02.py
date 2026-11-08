"""Live Lore Short 002 (Resident Evil) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render02.py OUT.mp4 [start end]
All visuals drawn in code. No footage, posters, logos or music.
"""
import json, math, random, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient

RED = (205, 38, 38)
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments02.json"))
ST = [s[0] for s in SEG]

def chunk_t(i, j):
    """Start time of caption chunk j in sentence i (same weighting as timing.captions)."""
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

# ---------- art ----------
COLD = Image.blend(gradient((22, 28, 44), (3, 4, 9), W + 200, H + 200), r.clouds(21, (90, 100, 130)), 0.45).convert("RGBA")
_rs = random.Random(4)
FLAKES = [(_rs.uniform(0, W), _rs.uniform(0, H), _rs.uniform(60, 180), _rs.uniform(2, 6), _rs.uniform(0, 6.28)) for _ in range(240)]

def snow(c, g, alpha=1.0):
    d = ImageDraw.Draw(c, "RGBA")
    for x0, y0, sp, sz, ph in FLAKES:
        x = (x0 + 25 * math.sin(g * 0.8 + ph)) % W
        y = (y0 + sp * g) % H
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(235, 240, 255, int(200 * alpha)))

def cold_city(c, t, shift=0):
    c.paste(r.zoom_crop(COLD, 1.0 + 0.01 * t, ox=-15 * t))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = int(90 + 50 * math.sin(t * 4))
    ImageDraw.Draw(glow).ellipse([-100, 1250, W + 100, 2100], fill=(200, 30, 30, a))  # emergency glow
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    c.alpha_composite(r.CITY_MODERN.crop((80 + shift, 0, 80 + shift + W, H)))

def pill(text, size, fill, color=(15, 15, 18)):
    img = T(("pill", text, size, color), text, size, fill=color, weight="Black")
    p = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, p.width, p.height], 26, fill=fill + (255,))
    p.alpha_composite(img, (35, 14))
    return p

# ---------- scenes ----------
def s_hook(c, t, g):
    cold_city(c, t, int(20 * t))
    snow(c, g)
    punch(c, "re", "RESIDENT EVIL", 640, 110, t, color=RED, stroke=6)
    if t > 0.6:
        punch(c, "be", "BIGGEST EVER", 790, 88, t - 0.6, color=WHITE, stroke=5, emoji=r.EYES)
    if t > 2.6:
        label(c, "NOW ON DIGITAL", 940, 54, GOLD, t - 2.6)
    if t > 4.0:
        label(c, "BEAT EVERY FORECAST", 1020, 44, ICE, t - 4.0)

def s_sep18(c, t, g):
    r.date_card(c, t, "18", "SEP", "US RELEASE", (40, 14, 16))

BARS = [70, 95, 60, 110, 85, 75]
def s_money60(c, t, g):
    c.paste(gradient((18, 26, 18), (4, 6, 4)))
    val = int(60 * ease(t / 1.1))
    paste_center(c, T(("m60", val), f"${val}M", 250, fill=(120, 230, 140)), W / 2, 700)
    label(c, "US OPENING WEEKEND", 880, 54, WHITE, t - 0.2)
    d = ImageDraw.Draw(c, "RGBA")
    p = ease(t / 1.0)
    for i, bh in enumerate(BARS):
        x = 170 + i * 110
        d.rectangle([x, 1330 - bh * p, x + 80, 1330], fill=(90, 100, 110))
    x = 170 + len(BARS) * 110
    d.rectangle([x, 1330 - 300 * ease((t - 0.6) / 0.8), x + 80, 1330], fill=GOLD)

def s_world(c, t, g):
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    cx, cy, R = 540, 1050, 260
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=ICE + (160,), width=4)
    for k in range(1, 4):  # latitudes
        h = R * k / 4
        d.ellipse([cx - R, cy - h, cx + R, cy + h], outline=ICE + (70,), width=2)
    for k in range(6):  # rotating longitudes
        w_ = abs(R * math.cos(g * 0.6 + k * math.pi / 6))
        d.ellipse([cx - w_, cy - R, cx + w_, cy + R], outline=ICE + (70,), width=2)
    val = int(400 * ease(t / 1.6))
    paste_center(c, T(("w400", val), f">${val}M", 200, fill=GOLD), W / 2, 560)
    label(c, "WORLDWIDE • REPORTED", 720, 48, WHITE, t - 0.3)

def s_weapons(c, t, g):
    c.paste(r.THEATER)
    punch(c, "cbig", "CREGGER'S BIGGEST", 560, 84, t, color=GOLD)
    d = ImageDraw.Draw(c, "RGBA")
    for row, (name, val, px, col, delay) in enumerate((("WEAPONS (2025)", "$270M", 514, (110, 115, 125), 0.2),
                                                       ("RESIDENT EVIL", "$400M+", 762, GOLD, 0.6))):
        y = 820 + row * 240
        p = ease((t - delay) / 0.7)
        paste_center(c, T(("wn", name), name, 46, fill=WHITE, weight="Bold"), 140 + 300, y - 50, alpha=ease((t - delay) / 0.2))
        d.rectangle([140, y, 140 + px * p, y + 90], fill=col)
        if p > 0.95:
            paste_center(c, T(("wv", val), val, 56, fill=WHITE), 140 + px - 110, y + 45)

def s_home(c, t, g):
    c.paste(gradient((14, 12, 20), (3, 3, 6)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rectangle([110, 570, 970, 1110], fill=(220, 60, 60, 110))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([130, 590, 950, 1090], 24, fill=(20, 20, 24))
    d.rectangle([160, 620, 920, 1060], fill=(70, 18, 20))
    s = 1.0 + 0.08 * math.sin(t * 3)
    d.polygon([(500 - 40 * s, 760), (500 - 40 * s, 920), (500 + 90 * s, 840)], fill=WHITE)
    d.rounded_rectangle([200, 1200, 880, 1330], 50, fill=(25, 22, 30))  # couch
    d.rounded_rectangle([160, 1150, 300, 1330], 40, fill=(25, 22, 30))
    d.rounded_rectangle([780, 1150, 920, 1330], 40, fill=(25, 22, 30))
    punch(c, "rob", "RENT OR BUY", 460, 110, t, color=WHITE)
    label(c, "DIGITAL • NOV 3", 1140, 50, GOLD, t - 0.4)

def s_twist(c, t, g):
    c.paste(Image.new("RGB", (W, H), (4, 3, 5)))
    d = ImageDraw.Draw(c, "RGBA")
    rr = random.Random(int(g * FPS))
    for _ in range(10):  # glitch bars
        y = rr.randint(0, H)
        d.rectangle([0, y, W, y + rr.randint(2, 14)], fill=(200, 30, 30, rr.randint(20, 70)))
    split = ST[5] - ST[4]
    if t < split:
        punch(c, "tw", "THE TWIST", 760, 140, t, color=RED)
    else:
        lt = t - split
        punch(c, "nag", "NOT A GAME", 690, 110, lt, color=WHITE)
        punch(c, "rmk", "REMAKE", 860, 140, max(0, lt - 0.25), color=RED)
        if lt > 0.6:
            k = ease((lt - 0.6) / 0.25)
            d.line([(250, 860), (250 + 580 * k, 860)], fill=WHITE + (255,), width=16)

def figure(d, x, y, col):
    d.ellipse([x - 48, y - 48, x + 48, y + 48], fill=col)
    d.rounded_rectangle([x - 80, y + 58, x + 80, y + 270], 50, fill=col)
    d.rectangle([x - 60, y + 250, x - 18, y + 380], fill=col)
    d.rectangle([x + 18, y + 250, x + 60, y + 380], fill=col)

def s_original(c, t, g):
    cold_city(c, t)
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(beam).polygon([(600, 1040), (1100, 880), (1100, 1260)], fill=(255, 240, 180, 70))  # flashlight cone
    c.alpha_composite(beam.filter(ImageFilter.GaussianBlur(25)))
    d = ImageDraw.Draw(c, "RGBA")
    figure(d, 540, 960, (8, 9, 14, 255))
    snow(c, g, 0.8)
    pb = chunk_t(6, 4) - ST[6]
    if t < pb:
        label(c, "ORIGINAL STORY • NEW LEAD", 600, 46, GOLD, t - 0.2)
    else:
        lt = t - pb
        for i, (bx, by, txt) in enumerate(((250, 700, "?!"), (820, 640, "..."), (780, 820, "?!?"))):
            a = ease((lt - i * 0.2) / 0.2)
            if a > 0:
                b = pill(txt, 64, (240, 240, 245))
                paste_center(c, b, bx, by, scale=0.8 + 0.2 * a, alpha=a)
        label(c, "SOME GAMERS PUSHED BACK", 520, 48, WHITE, lt)

def s_1996(c, t, g):
    c.paste(gradient((30, 18, 40), (5, 4, 8)))
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([220, 760, 860, 1230], 40, fill=(58, 58, 68))
    d.rounded_rectangle([270, 800, 810, 1150], 30, fill=(20, 70, 70))
    for y in range(800, 1150, 7):  # scanlines
        d.line([(270, y), (810, y)], fill=(0, 0, 0, 60), width=2)
    if int(t * 2) % 2 == 0:
        paste_center(c, T("ps", "PRESS START", 54, fill=(200, 255, 230), weight="Bold", spacing=6), 540, 975)
    d.rectangle([480, 1230, 600, 1290], fill=(40, 40, 48))
    punch(c, "y96", "1996", 470, 240, t, color=(235, 230, 220))
    label(c, "JAPAN • CAPCOM", 650, 54, GOLD, t - 0.3)

GREY = [260, 330, 210, 380, 300, 240, 420]
def s_m100(c, t, g):
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    line_y = 760
    for x in range(60, W - 60, 46):  # dashed $100M line
        d.line([(x, line_y), (x + 26, line_y)], fill=ICE + (255,), width=6)
    paste_center(c, T("l100", "$100M • US BOX OFFICE", 40, fill=ICE, weight="Bold"), W / 2, line_y - 40)
    p = ease(t / 1.0)
    for i, bh in enumerate(GREY):
        x = 110 + i * 105
        d.rectangle([x, 1330 - bh * p, x + 75, 1330], fill=(90, 95, 110))
    did = ST[9] - ST[8]
    if t < did:
        label(c, "NO EARLIER FILM", 560, 60, WHITE, t - 0.3)
    else:
        lt = t - did
        x = 110 + len(GREY) * 105
        d.rectangle([x, 1330 - 700 * ease(lt / 0.5), x + 75, 1330], fill=GOLD)
        punch(c, "did", "THIS ONE DID", 560, 110, lt, color=GOLD)

def s_outro(c, t, g):
    c.paste(r.THEATER)
    paste_center(c, pill("RENT IT", 96, GOLD), 300, 760, scale=0.6 + 0.4 * ease(t / 0.25), alpha=ease(t / 0.15))
    paste_center(c, pill("WAIT?", 96, ICE), 780, 760, scale=0.6 + 0.4 * ease((t - 0.8) / 0.25), alpha=ease((t - 0.8) / 0.15))
    rc = ST[11] - ST[10]
    if t > rc:
        punch(c, "sun2", "SUNDAY RECAP", 980, 84, t - rc, color=GOLD)
    if t > rc + 1.0:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - rc - 1.0) / 0.3))

# ---------- wire into render.py's frame() ----------
r.SCENES = [
    (0.0, ST[1], s_hook), (ST[1], chunk_t(1, 3), s_sep18), (chunk_t(1, 3), ST[2], s_money60),
    (ST[2], chunk_t(2, 3), s_world), (chunk_t(2, 3), ST[3], s_weapons), (ST[3], ST[4], s_home),
    (ST[4], ST[6], s_twist), (ST[6], ST[7], s_original), (ST[7], ST[8], s_1996),
    (ST[8], ST[10], s_m100), (ST[10], DUR + 0.1, s_outro),
]
r.CALLOUTS = [
    (chunk_t(1, 3), ST[2] - 0.1, "c2", "$60M • FRANCHISE RECORD", None),
    (chunk_t(2, 2), chunk_t(2, 3), "c3", "PAST $400M WORLDWIDE", None),
    (ST[9], ST[10] - 0.05, "c4", "FIRST $100M IN THE US", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 60

if __name__ == "__main__":
    out = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    n = int(round((t1 - t0) * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-ss", str(t0), "-t", str(t1 - t0), "-i", AUDIO,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "10M",
           "-bufsize", "20M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(r.frame(t0 + i / FPS).tobytes())
        if i % 300 == 0:
            print(f"frame {i}/{n}", file=sys.stderr)
    p.stdin.close()
    sys.exit(p.wait())
