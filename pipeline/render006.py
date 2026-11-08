"""Live Lore Short 006 (Ramayana Part 1 opening) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render006.py OUT.mp4 [start end]  |  python3 render006.py stills t1 t2 ...
All visuals drawn in code (generic shapes; no film footage, posters, logos or celebrity images). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient

RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments006.json"))
ST = [s[0] for s in SEG]

def chunk_t(i, j):
    """Start time of caption chunk j in sentence i (same weighting as timing.captions)."""
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

def emoji(ch, size):
    f = ImageFont.truetype(r.EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(size * im.width / im.height), size), Image.LANCZOS)

E_COIN, E_EYES, E_GLOBE, E_FIRE, E_POPCORN, E_DIYA, E_SCROLL = (emoji(c, 150) for c in "💰👀🌍🔥🍿🪔📜")

def pill(text, size, fill, color=DARK):
    img = T(("pill", text, size, color), text, size, fill=color, weight="Black")
    p = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, p.width, p.height], 26, fill=fill + (255,))
    p.alpha_composite(img, (35, 14))
    return p

def pop(lt, d=0.25):
    return 0.6 + 0.4 * ease(lt / d), ease(lt / 0.12)

# ---------- art ----------
def stars(c, t, n=40):
    d = ImageDraw.Draw(c, "RGBA")
    rs = random.Random(3)
    for _ in range(n):
        x, y, ph = rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0, 6)
        a = int(120 + 120 * math.sin(t * 3 + ph))
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 230, 150, max(0, a)))

SAFFRON = (255, 153, 51)

def coins(c, cx, base, n, t):
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(n):
        y = base - i * 34
        for dx in (-130, 130) if i % 2 == 0 else (0,):
            d.ellipse([cx + dx - 130, y - 40, cx + dx + 130, y + 40], fill=(185, 140, 30, 255))
            d.ellipse([cx + dx - 130, y - 52, cx + dx + 130, y + 28], fill=(240, 195, 60, 255), outline=(150, 105, 15, 255), width=4)

def temple(c, cx, base, s, col=(8, 6, 10, 255)):
    d = ImageDraw.Draw(c, "RGBA")
    d.rectangle([cx - 330 * s, base - 150 * s, cx + 330 * s, base], fill=col)
    for k, (w, h) in enumerate(((260, 260), (190, 200), (120, 160), (60, 120))):
        top = base - 150 * s - sum(x[1] for x in ((260, 260), (190, 200), (120, 160), (60, 120))[:k]) * s * 0.6
        d.polygon([(cx - w * s, top), (cx + w * s, top), (cx, top - h * s * 0.9)], fill=col)
    d.rectangle([cx - 8 * s, base - 150 * s - 520 * s, cx + 8 * s, base - 150 * s - 420 * s], fill=col)

def sun(c, cx, cy, r_, t):
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(4, 0, -1):
        d.ellipse([cx - r_ * k * 0.5, cy - r_ * k * 0.5, cx + r_ * k * 0.5, cy + r_ * k * 0.5],
                  fill=(255, 150, 50, 28 + 10 * (4 - k)))
    d.ellipse([cx - r_ * 0.4, cy - r_ * 0.4, cx + r_ * 0.4, cy + r_ * 0.4], fill=(255, 215, 120, 255))

def person(d, x, y, col, s=1.0):
    d.ellipse([x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s], fill=col)
    d.rounded_rectangle([x - 100 * s, y + 75 * s, x + 100 * s, y + 330 * s], int(60 * s), fill=col)

def diya(c, cx, cy, s, t, lit=1.0):
    d = ImageDraw.Draw(c, "RGBA")
    d.pieslice([cx - 90 * s, cy - 50 * s, cx + 90 * s, cy + 70 * s], 0, 180, fill=(190, 85, 40, 255))
    if lit > 0.1:
        fl = 1 + 0.08 * math.sin(t * 14 + cx)
        for k, (w, a) in enumerate(((60, 60), (38, 140), (22, 255))):
            d.ellipse([cx - w * s * 0.6 * fl, cy - 10 * s - w * 2.4 * fl * s * lit, cx + w * s * 0.6 * fl, cy - 10 * s],
                      fill=((255, 190, 60, a) if k < 2 else (255, 240, 170, a)))

# ---------- scenes ----------
def s_hook(c, t, g):
    split = chunk_t(0, 2) - ST[0]
    if t < split:
        c.paste(r.NIGHT)
        stars(c, t, 25)
        coins(c, W / 2, 1050, min(9, 2 + int(t * 7)), t)
        punch(c, "400m", "$400 MILLION+", 520, 100, t, color=GOLD, stroke=7)
        paste_center(c, E_COIN.resize((190, 190)), W / 2, 1230, *pop(t - 0.3))
    else:
        lt = t - split
        c.paste(gradient((60, 24, 20), (10, 6, 12)))
        sun(c, W / 2, 1000, 700 + 20 * lt, lt)
        temple(c, W / 2, 1180, 1.25)
        punch(c, "anc", "ONE ANCIENT STORY", 540, 70, lt, color=WHITE, stroke=6, emoji=E_SCROLL.resize((100, 100)))

def s_cost(c, t, g):
    split = chunk_t(1, 4) - ST[1]
    if t < split:
        c.paste(gradient((26, 22, 44), (5, 4, 10)))
        d = ImageDraw.Draw(c, "RGBA")
        punch(c, "rep", "REPORTEDLY", 560, 100, t, color=WHITE, stroke=5)
        for k, (x, txt) in enumerate(((290, "PART 1"), (790, "PART 2"))):
            lt = t - 0.6 - k * 0.4
            if lt <= 0:
                continue
            sc_, a_ = pop(lt)
            card = Image.new("RGBA", (400, 520), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle([0, 0, 400, 520], 40, fill=(245, 240, 228, 255))
            cd.rounded_rectangle([0, 0, 400, 130], 40, fill=SAFFRON + (255,))
            cd.rectangle([0, 90, 400, 130], fill=SAFFRON + (255,))
            tt = T(("pt", txt), txt, 62, fill=DARK, weight="Black")
            card.alpha_composite(tt, ((400 - tt.width) // 2, 30))
            cd.polygon([(120, 380), (200, 190), (280, 380)], fill=(60, 50, 60, 255))
            cd.ellipse([170, 160, 230, 220], fill=(60, 50, 60, 255))
            paste_center(c, card, x, 1000, sc_, a_)
        label(c, "2-FILM BUDGET", 1400 - 120, 56, GOLD, t - 1.4)
    else:
        lt = t - split
        r.date_card(c, lt, "5", "NOV", "2 DAYS BEFORE DIWALI", (60, 28, 18))
        paste_center(c, E_DIYA.resize((150, 150)), 830, 560, *pop(lt - 1.0))

def s_cast(c, t, g):
    c.paste(gradient((34, 20, 26), (6, 4, 8)))
    d = ImageDraw.Draw(c, "RGBA")
    roles = [("RAM", 200, (70, 120, 200)), ("SITA", 540, (230, 120, 150)), ("RAVANA", 880, (190, 50, 50))]
    for k, (name, x, col) in enumerate(roles):
        start = chunk_t(2, (1, 3, 5)[k] - 1) - ST[2] if k else 0.0
        lt = t - (0 if k == 0 else chunk_t(2, (0, 2, 4)[k]) - ST[2])
        if lt <= 0:
            continue
        sc_, a_ = pop(lt)
        layer = Image.new("RGBA", (340, 700), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        person(ld, 170, 150, col + (255,), 1.2)
        if name == "RAVANA":
            ld.polygon([(70, 120), (30, 20), (110, 80)], fill=(40, 10, 10, 255))
            ld.polygon([(270, 120), (310, 20), (230, 80)], fill=(40, 10, 10, 255))
        paste_center(c, layer, x, 920, sc_, a_)
        paste_center(c, pill(name, 54, (245, 240, 228)), x, 1240, sc_, a_)
    punch(c, "cast", "THE CAST", 540, 100, t, color=GOLD, stroke=5)

def s_crore(c, t, g):
    c.paste(r.THEATER)
    stars(c, t, 30)
    d = ImageDraw.Draw(c, "RGBA")
    v = int(round(150 * ease(t / 1.6)))
    n = T(("cr", v), str(v), 360, fill=GOLD, stroke=8)
    paste_center(c, n, W / 2, 800, scale=0.9 + 0.1 * ease(t / 0.3))
    label(c, "CRORE RUPEES", 1010, 66, WHITE, t - 0.2)
    d.rounded_rectangle([140, 1120, 940, 1180], 30, fill=(50, 50, 58))
    d.rounded_rectangle([140, 1120, 140 + 800 * ease(t / 1.6), 1180], 30, fill=SAFFRON)
    paste_center(c, pill("3 DAYS • INDIA", 56, (245, 240, 228)), W / 2, 560, *pop(t - 0.1))

def s_overseas(c, t, g):
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    cx, cy = W / 2, 820
    d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=(30, 70, 140, 255))
    for (x, y, w, h) in ((-120, -150, 200, 150), (50, -60, 170, 210), (-230, 20, 130, 110), (120, 120, 120, 90)):
        d.ellipse([cx + x - w / 2, cy + y - h / 2, cx + x + w / 2, cy + y + h / 2], fill=(60, 140, 80, 255))
    for k, (x, y) in enumerate(((-120, -150), (50, -60), (-230, 20), (120, 120))):
        lt = t - 0.3 - k * 0.2
        if lt > 0:
            rr = 20 + 60 * ease(lt / 0.8) * (1 - ease((lt - 0.8) / 0.8) * 0.6)
            d.ellipse([cx + x - rr, cy + y - rr, cx + x + rr, cy + y + rr], outline=GOLD + (200,), width=6)
            d.ellipse([cx + x - 12, cy + y - 12, cx + x + 12, cy + y + 12], fill=GOLD + (255,))
    punch(c, "10m", "$10 MILLION", 1240, 104, t, color=GOLD, stroke=6)
    label(c, "OVERSEAS • 2 DAYS", 1340, 50, WHITE, t - 0.6)

def s_why(c, t, g):
    r_why(c, t, g)

def s_diwali(c, t, g):
    c.paste(gradient((50, 20, 10), (8, 4, 8)))
    stars(c, t, 40)
    for k in range(5):
        lt = t - 0.15 * k
        diya(c, 140 + k * 200, 860, 0.9, t, lit=ease(lt / 0.4))
    calw = Image.new("RGBA", (700, 380), (0, 0, 0, 0))
    cd = ImageDraw.Draw(calw)
    cd.rounded_rectangle([0, 0, 700, 380], 30, fill=(245, 240, 228, 255))
    cd.rounded_rectangle([0, 0, 700, 90], 30, fill=SAFFRON + (255,))
    cd.rectangle([0, 60, 700, 90], fill=SAFFRON + (255,))
    for i in range(7):
        for j in range(3):
            col = (SAFFRON if (i, j) in ((0, 0), (1, 0), (2, 0)) else (200, 195, 185))
            cd.rounded_rectangle([30 + i * 92, 120 + j * 80, 100 + i * 92, 180 + j * 80], 12, fill=col + (255,))
    paste_center(c, calw, W / 2, 1160, *pop(t - 0.3))
    punch(c, "dw", "DIWALI WEEKEND", 520, 82, t, color=GOLD, stroke=6)
    b = chunk_t(6, 5) - ST[6]
    if t > b:
        paste_center(c, E_POPCORN.resize((170, 170)), 880, 640, *pop(t - b))

def s_catch(c, t, g):
    c.paste(gradient((26, 22, 30), (5, 5, 8)))
    d = ImageDraw.Draw(c, "RGBA")
    punch(c, "trk", "TRACKERS DISAGREE", 520, 74, t, color=WHITE, stroke=6)
    vals = [(250, 360, "?"), (540, 450, "?"), (830, 260, "?")]
    for k, (x, h, q) in enumerate(vals):
        lt = t - 0.3 - k * 0.25
        if lt <= 0:
            continue
        hh = h * ease(lt / 0.5) + 14 * math.sin(t * 5 + k) * ease(lt / 0.5)
        d.rounded_rectangle([x - 90, 1160 - hh, x + 90, 1160], 20, fill=SAFFRON + (255,))
        paste_center(c, T(("q", k), q, 120, fill=WHITE, stroke=5), x, 1160 - hh - 100)
    d.line([(120, 1170), (960, 1170)], fill=(200, 200, 210), width=6)
    e = chunk_t(7, 3) - ST[7]
    if t > e:
        paste_center(c, pill("ESTIMATES", 70, GOLD), W / 2, 1290, *pop(t - e))

def s_take(c, t, g):
    c.paste(r.THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    punch(c, "mt", "MY TAKE", 480, 90, t, color=WHITE)
    paste_center(c, E_SCROLL.resize((200, 200)), W / 2, 760, *pop(t - 0.2))
    b = chunk_t(8, 4) - ST[8]
    if t > b:
        lt = t - b
        p = min(1.0, ease(lt / 1.0))
        d.rounded_rectangle([160, 1000, 920, 1080], 40, fill=(50, 50, 58))
        d.rounded_rectangle([160, 1000, 160 + 760 * p, 1080], 40, fill=GOLD)
        paste_center(c, T(("inst", int(p * 100)), f"HYPE {int(p * 100)}%", 80, fill=WHITE, stroke=5), W / 2, 1180)
    else:
        label(c, "THOUSANDS OF YEARS OLD", 1040, 56, WHITE, t - 0.6)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    stars(c, t, 30)
    punch(c, "ro", "BIG SCREEN OR STREAMING?", 520, 56, t, color=WHITE, stroke=6)
    paste_center(c, pill("BIG SCREEN", 58, GOLD), 270, 800, *pop(t - 0.2))
    paste_center(c, pill("STREAMING", 58, ICE), 810, 800, *pop(t - 0.5))
    rc = ST[10] - ST[9]
    if t > rc:
        punch(c, "sun6", "SUNDAY RECAP", 1060, 84, t - rc, color=GOLD)
    if t > rc + 1.0:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - rc - 1.0) / 0.3))

def r_why(c, t, g, text="WHY IT MATTERS?"):
    c.paste(Image.new("RGB", (W, H), (6, 6, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    rr = random.Random(int(g * FPS))
    for _ in range(8):
        y = rr.randint(0, H)
        d.rectangle([0, y, W, y + rr.randint(2, 12)], fill=GOLD + (rr.randint(20, 60),))
    punch(c, ("why", text), text, 760, 90, t, color=GOLD, stroke=5)

# ---------- wire into render.py's frame() ----------
r.SCENES = [
    (0.0, ST[1], s_hook), (ST[1], ST[2], s_cost), (ST[2], ST[3], s_cast), (ST[3], ST[4], s_crore),
    (ST[4], ST[5], s_overseas), (ST[5], ST[6], s_why), (ST[6], ST[7], s_diwali), (ST[7], ST[8], s_catch),
    (ST[8], ST[9], s_take), (ST[9], DUR + 0.1, s_outro),
]
# outro covers CTA + recap sentences (indices 9, 10)
r.CALLOUTS = [
    (chunk_t(1, 0), ST[2] - 0.1, "c1", "RAMAYANA: PART 1 • NOV 5", None),
    (chunk_t(3, 3), ST[4] - 0.1, "c2", "150 CRORE • 3 DAYS", None),
    (ST[4] + 0.2, ST[5] - 0.1, "c3", "~$10M OVERSEAS", None),
    (chunk_t(7, 3), ST[8] - 0.1, "c4", "ESTIMATES VARY", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":  # python3 render006.py stills t1 t2 ...
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s006_{s}.png")
        sys.exit(0)
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
