"""Live Lore Short 005 (Ocarina of Time remake reviews) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render005.py OUT.mp4 [start end]  |  python3 render005.py stills t1 t2 ...
All visuals drawn in code (generic shapes, no game art, logos or footage). No music.
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
SEG = json.load(open("segments005.json"))
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

E_PAD, E_TROPHY, E_ART, E_FILM, E_VIOLIN, E_EYES, E_SNAIL = (emoji(c, 150) for c in "🎮🏆🎨🎬🎻👀🐌")

def pill(text, size, fill, color=DARK):
    img = T(("pill", text, size, color), text, size, fill=color, weight="Black")
    p = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, p.width, p.height], 26, fill=fill + (255,))
    p.alpha_composite(img, (35, 14))
    return p

def pop(lt, d=0.25):
    return 0.6 + 0.4 * ease(lt / d), ease(lt / 0.12)

# ---------- art ----------
_rp = random.Random(5)
PIX = [[_rp.choice([(40, 110, 60), (60, 140, 70), (90, 70, 40), (70, 120, 200), (30, 80, 50)]) for _ in range(16)] for _ in range(12)]

def crt(c, cx, cy, s, t, hi=False):
    """Chunky old TV; screen shows a blocky low-poly landscape (or a smooth one if hi)."""
    d = ImageDraw.Draw(c, "RGBA")
    w, h = 420 * s, 330 * s
    d.rounded_rectangle([cx - w - 40 * s, cy - h - 40 * s, cx + w + 40 * s, cy + h + 90 * s], int(50 * s), fill=(48, 46, 52))
    d.rectangle([cx - w, cy - h, cx + w, cy + h], fill=(20, 30, 50))
    if hi:
        scr = gradient((120, 180, 255), (40, 120, 70), int(2 * w), int(2 * h)).convert("RGBA")
        sd = ImageDraw.Draw(scr)
        sd.polygon([(0, h * 1.3), (w * 0.6, h * 0.6), (w * 1.2, h * 1.2), (w * 1.6, h * 0.5), (2 * w, h * 1.1), (2 * w, 2 * h), (0, 2 * h)],
                   fill=(40, 100, 60))
        sd.ellipse([w * 1.5, h * 0.15, w * 1.75, h * 0.4], fill=(255, 240, 180))
        c.alpha_composite(scr, (int(cx - w), int(cy - h)))
    else:
        bw, bh = 2 * w / 16, 2 * h / 12
        for j, row in enumerate(PIX):
            for i, col in enumerate(row):
                d.rectangle([cx - w + i * bw, cy - h + j * bh, cx - w + (i + 1) * bw, cy - h + (j + 1) * bh], fill=col)
    for y in range(int(cy - h), int(cy + h), 8):  # scanlines
        d.line([(cx - w, y), (cx + w, y)], fill=(0, 0, 0, 50), width=2)
    d.ellipse([cx + w - 60 * s, cy + h + 25 * s, cx + w - 20 * s, cy + h + 65 * s], fill=(200, 60, 60))

def score_box(c, cx, cy, val, size=300, col=GREEN, alpha=1.0, scale=1.0):
    b = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, size, size], int(size * 0.12), fill=col + (255,))
    n = T(("sb", val, size), str(val), int(size * 0.55), fill=WHITE)
    b.alpha_composite(n, ((size - n.width) // 2, (size - n.height) // 2 - int(size * 0.04)))
    paste_center(c, b, cx, cy, scale=scale, alpha=alpha)

def stars(c, t, n=40):
    d = ImageDraw.Draw(c, "RGBA")
    rs = random.Random(3)
    for _ in range(n):
        x, y, ph = rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0, 6)
        a = int(120 + 120 * math.sin(t * 3 + ph))
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 230, 150, max(0, a)))

# ---------- scenes ----------
def s_hook(c, t, g):
    split = chunk_t(0, 2) - ST[0]
    c.paste(r.NIGHT)
    if t < split:
        crt(c, W / 2, 860, 1.0 + 0.02 * t, t)
        punch(c, "1998", "1998", 440, 170, t, color=WHITE, stroke=7)
        paste_center(c, E_PAD, W / 2, 1230, *pop(t - 0.3))
    else:
        lt = t - split
        stars(c, lt)
        paste_center(c, E_TROPHY.resize((300, 300)), W / 2, 820, *pop(lt))
        punch(c, "best26", "BEST OF 2026", 520, 120, lt, color=GOLD, stroke=6, emoji=E_EYES.resize((96, 96)))

def s_remade(c, t, g):
    split = chunk_t(1, 3) - ST[1]
    if t < split:
        c.paste(r.NIGHT)
        p = ease(t / max(0.1, split - 0.3))
        crt(c, W / 2, 880, 0.95, t, hi=p > 0.5)
        punch(c, "rm", "REMADE", 520, 140, t, color=GOLD, stroke=6)
        label(c, "OCARINA OF TIME", 1240, 64, WHITE, t - 0.3)
    else:
        r.date_card(c, t - split, "5", "NOV", "SWITCH 2 ONLY", (40, 22, 26))

def s_upgrades(c, t, g):
    c.paste(gradient((26, 22, 44), (5, 4, 10)))
    items = [(E_ART, "NEW GRAPHICS", 0), (E_FILM, "VOICED CUTSCENES", 1), (E_VIOLIN, "FULL ORCHESTRA", 2)]
    for k, (em, txt, j) in enumerate(items):
        lt = g - chunk_t(2, j)
        if lt <= 0:
            continue
        y = 560 + k * 270
        sc, a = pop(lt)
        paste_center(c, em.resize((130, 130)), 230, y, sc, a)
        d = ImageDraw.Draw(c, "RGBA")
        paste_center(c, pill(txt, 60, (245, 240, 228)), 640, y, sc, a)

def s_score(c, t, g):
    c.paste(r.THEATER)
    stars(c, t, 25)
    v = int(round(96 * ease(t / 1.2)))
    score_box(c, W / 2, 800, v, 380, scale=0.8 + 0.2 * ease(t / 0.3), alpha=ease(t / 0.15))
    rank = chunk_t(3, 3) - ST[3]
    if t > rank:
        lt = t - rank
        punch(c, "no1", "#1 OF THE YEAR", 1150, 104, lt, color=GOLD, stroke=5)
    else:
        label(c, "METASCORE", 520, 60, WHITE, t)

def reviewer(d, x, y, col):
    d.ellipse([x - 50, y - 50, x + 50, y + 50], fill=col)
    d.rounded_rectangle([x - 80, y + 60, x + 80, y + 260], 50, fill=col)

def s_japan(c, t, g):
    c.paste(gradient((60, 20, 26), (8, 4, 6)))
    d = ImageDraw.Draw(c, "RGBA")
    paste_center(c, pill("JAPAN REVIEW", 64, (245, 240, 228)), W / 2, 520, *pop(t))
    for k, sc_ in enumerate((9, 9, 9, 10)):
        lt = t - 0.3 - k * 0.3
        if lt <= 0:
            continue
        x = 180 + k * 240
        reviewer(d, x, 760, (24, 24, 30, 255))
        score_box(c, x, 1120, sc_, 150, col=GOLD if sc_ == 10 else GREEN, scale=pop(lt)[0], alpha=pop(lt)[1])
    if t > 1.8:
        punch(c, "37", "37 / 40", 1300 - 30, 110, t - 1.8, color=WHITE, stroke=6)

def s_twist(c, t, g):
    split = chunk_t(5, 2) - ST[5]
    if t < split:
        r_why(c, t, g, "THE TWIST…")
        return
    lt = t - split
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    tilt = 60 * ease(lt / 0.6)  # original side drops: it weighs more
    cx, cy = W / 2, 760
    d.polygon([(cx - 40, 1200), (cx + 40, 1200), (cx, cy)], fill=(150, 150, 160))
    lx, ly, rx, ry = cx - 330, cy - tilt, cx + 330, cy + tilt
    d.line([(lx, ly), (rx, ry)], fill=(200, 200, 210), width=14)
    for x, y, val, txt in ((lx, ly, 96, "REMAKE"), (rx, ry, 99, "ORIGINAL")):
        d.line([(x, y), (x, y + 120)], fill=(200, 200, 210), width=6)
        score_box(c, x, y + 230, val, 200, col=GREEN if val == 96 else GOLD)
        paste_center(c, T(("tw", txt), txt, 52, fill=WHITE, weight="Black"), x, y + 380)

def s_original(c, t, g):
    split = chunk_t(6, 2) - ST[6]
    c.paste(r.SEPIA)
    crt(c, W / 2, 830, 0.9, t)
    score_box(c, W / 2, 830, 99, 320, col=GOLD, scale=pop(t)[0], alpha=pop(t)[1])
    if t < split:
        punch(c, "98v", "THE 1998 VERSION", 470, 92, t, color=WHITE, stroke=5)
    else:
        punch(c, "ever", "TOP-RATED. EVER.", 470, 100, t - split, color=GOLD, stroke=6)

def s_perfect(c, t, g):
    c.paste(r.THEATER)
    stars(c, t, 60)
    for k in range(4):
        lt = t - 0.2 - k * 0.2
        if lt > 0:
            score_box(c, 180 + k * 240, 820, 10, 170, col=GOLD, scale=pop(lt)[0], alpha=pop(lt)[1])
    punch(c, "40", "40 / 40", 560, 150, t, color=GOLD, stroke=6)
    label(c, "FIRST-EVER PERFECT SCORE", 1110, 54, WHITE, t - 0.6)

def r_why(c, t, g, text="WHY IT MATTERS?"):
    c.paste(Image.new("RGB", (W, H), (6, 6, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    rr = random.Random(int(g * FPS))
    for _ in range(8):
        y = rr.randint(0, H)
        d.rectangle([0, y, W, y + rr.randint(2, 12)], fill=GOLD + (rr.randint(20, 60),))
    punch(c, ("why", text), text, 760, 110, t, color=GOLD, stroke=5)

def s_why(c, t, g):
    r_why(c, t, g)

def s_critics(c, t, g):
    split = chunk_t(9, 3) - ST[9]
    if t < split:
        c.paste(gradient((22, 22, 30), (4, 4, 6)))
        d = ImageDraw.Draw(c, "RGBA")
        for k in range(5):  # film strip sliding
            x = 100 + k * 220 - (t * 120) % 220
            d.rectangle([x, 620, x + 200, 900], fill=(40, 40, 48))
            d.rectangle([x + 20, 650, x + 180, 870], fill=(90, 80, 70))
        d.rounded_rectangle([190, 1040, 890, 1090], 25, fill=(50, 50, 58))
        d.rounded_rectangle([190, 1040, 190 + 700 * min(0.4, t / 6), 1090], 25, fill=GOLD)
        paste_center(c, E_SNAIL, W / 2, 1200, *pop(t - 0.3))
        punch(c, "slow", "TOO SLOW?", 470, 120, t, color=WHITE, stroke=6)
    else:
        lt = t - split
        c.paste(Image.new("RGB", (W, H), (20, 6, 10)))
        d = ImageDraw.Draw(c, "RGBA")
        hp = 1 - 0.15 * ease(lt / 1.5)  # boss barely scratched
        d.rectangle([140, 600, 940, 670], fill=(60, 20, 20))
        d.rectangle([140, 600, 140 + 800 * hp, 670], fill=RED)
        d.rectangle([140, 600, 940, 670], outline=WHITE, width=6)
        punch(c, "boss", "BOSS: NOSTALGIA", 500, 92, lt, color=WHITE, stroke=6)
        crt(c, W / 2, 1000, 0.55 + 0.03 * math.sin(lt * 6), lt)

def s_take(c, t, g):
    c.paste(r.THEATER)
    punch(c, "mt", "MY TAKE", 520, 90, t, color=WHITE)
    d2 = chunk_t(10, 1) - ST[10]
    if t > d2:
        lt = t - d2
        score_box(c, 330, 820, 96, 220, scale=pop(lt)[0], alpha=pop(lt)[1])
        paste_center(c, T("vs", "VS", 90, fill=WHITE), W / 2, 820, alpha=ease(lt / 0.2))
        score_box(c, 750, 820, 99, 220, col=GOLD, scale=pop(lt - 0.3)[0], alpha=pop(lt - 0.3)[1])
    d3 = chunk_t(10, 4) - ST[10]
    if t > d3:
        punch(c, "lose", "LOSES TO ITSELF", 1120, 90, t - d3, color=GOLD, stroke=5)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    stars(c, t, 30)
    punch(c, "ro", "REMAKE OR ORIGINAL?", 520, 84, t, color=WHITE, stroke=6)
    paste_center(c, pill("REMAKE", 76, GOLD), 280, 800, *pop(t - 0.2))
    paste_center(c, pill("ORIGINAL", 76, ICE), 790, 800, *pop(t - 0.5))
    rc = ST[12] - ST[11]
    if t > rc:
        punch(c, "sun5", "SUNDAY RECAP", 1060, 84, t - rc, color=GOLD)
    if t > rc + 1.0:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - rc - 1.0) / 0.3))

# ---------- wire into render.py's frame() ----------
r.SCENES = [
    (0.0, ST[1], s_hook), (ST[1], ST[2], s_remade), (ST[2], ST[3], s_upgrades), (ST[3], ST[4], s_score),
    (ST[4], ST[5], s_japan), (ST[5], ST[6], s_twist), (ST[6], ST[7], s_original), (ST[7], ST[8], s_perfect),
    (ST[8], ST[9], s_why), (ST[9], ST[10], s_critics), (ST[10], ST[11], s_take), (ST[11], DUR + 0.1, s_outro),
]
r.CALLOUTS = [
    (chunk_t(1, 4), ST[2] - 0.1, "c1", "SWITCH 2 ONLY • NOV 5", None),
    (chunk_t(3, 1), ST[4] - 0.1, "c2", "96 ON METACRITIC", None),
    (ST[4] + 0.3, ST[5] - 0.1, "c3", "FAMITSU: 37/40", None),
    (chunk_t(6, 1), ST[7] - 0.1, "c4", "ORIGINAL: 99", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":  # python3 render005.py stills t1 t2 ...
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s005_{s}.png")
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
