"""Live Lore Short 004 (Namdaemun scarf seller) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render004.py OUT.mp4 [start end]
All visuals drawn in code. No footage, photos, logos or music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient

RED, BLUE = (215, 45, 45), (40, 90, 230)
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments004.json"))
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

E_SCARF, E_MONEY, E_PHONE, E_POLICE, E_EYES = (emoji(c, 150) for c in "🧣💸📱🚨👀")

def pill(text, size, fill, color=(15, 15, 18)):
    img = T(("pill", text, size, color), text, size, fill=color, weight="Black")
    p = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, p.width, p.height], 26, fill=fill + (255,))
    p.alpha_composite(img, (35, 14))
    return p

# ---------- art ----------
SCARF_COLS = [(220, 70, 90), (240, 170, 60), (70, 160, 200), (130, 90, 200), (90, 190, 120), (240, 120, 160),
              (230, 220, 200), (60, 80, 160)]
_rs = random.Random(4)

def market_bg(w=W + 200):
    """Covered market lane: warm lamps, awning stripes, stalls fading into the distance."""
    img = gradient((46, 30, 22), (10, 7, 6), w, H).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(12):  # awning stripes overhead
        d.polygon([(i * w / 12, 0), ((i + 0.5) * w / 12, 0), (w / 2 + (i - 5.75) * 40, 520), (w / 2 + (i - 6.25) * 40, 520)],
                  fill=(150, 40, 40, 90) if i % 2 else (230, 220, 200, 45))
    for k in range(6):  # stall boxes receding
        y = 1500 - k * 130; s = 1 - k * 0.14
        for side in (-1, 1):
            x = w / 2 + side * (360 * s + 60)
            d.rectangle([x - 150 * s, y - 380 * s, x + 150 * s, y], fill=(30 + 8 * k, 20 + 6 * k, 16 + 5 * k, 255))
            for j in range(5):
                col = _rs.choice(SCARF_COLS)
                xx = x - 120 * s + j * 55 * s
                d.rectangle([xx, y - 360 * s, xx + 36 * s, y - 120 * s], fill=col + (int(200 - 25 * k),))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for x in range(120, w, 260):
        ImageDraw.Draw(glow).ellipse([x - 110, 380, x + 110, 600], fill=(255, 190, 110, 120))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    return img

MARKET = market_bg()

def scarf_rack(c, t, y0=560):
    d = ImageDraw.Draw(c, "RGBA")
    d.rectangle([120, y0 - 18, 960, y0], fill=(150, 150, 160))  # rail
    for i in range(8):
        x = 160 + i * 100
        sway = 14 * math.sin(t * 2.2 + i)
        col = SCARF_COLS[i]
        d.polygon([(x, y0), (x + 70, y0), (x + 74 + sway, y0 + 560), (x + 4 + sway, y0 + 560)], fill=col + (255,))
        for k in range(4):  # fringe
            d.line([(x + 8 + k * 18 + sway, y0 + 560), (x + 8 + k * 18 + sway, y0 + 600)], fill=col + (255,), width=5)
        d.line([(x + 35, y0 + 20), (x + 37 + sway * 0.5, y0 + 540)], fill=(255, 255, 255, 40), width=6)

def person(d, x, y, s, col):
    d.ellipse([x - 34 * s, y - 34 * s, x + 34 * s, y + 34 * s], fill=col)
    d.rounded_rectangle([x - 58 * s, y + 42 * s, x + 58 * s, y + 230 * s], int(40 * s), fill=col)

_rc = random.Random(9)
CROWD = [(_rc.uniform(-40, W + 40), _rc.uniform(0, 1), _rc.uniform(0, 6.3)) for _ in range(46)]

def crowd(c, t, density=1.0, phones=True):
    d = ImageDraw.Draw(c, "RGBA")
    n = int(len(CROWD) * density)
    for x, depth, ph in sorted(CROWD[:n], key=lambda v: v[1]):
        s = 0.6 + depth * 0.9
        y = 1050 + depth * 520 + 6 * math.sin(t * 3 + ph)
        shade = int(14 + 26 * (1 - depth))
        person(d, x, y, s, (shade, shade, shade + 6, 255))
        if phones and depth > 0.3:  # raised phone with glowing screen
            px, py = x + 30 * s, y - 70 * s
            d.line([(x + 40 * s, y + 60 * s), (px, py + 30 * s)], fill=(shade, shade, shade + 6, 255), width=int(20 * s))
            d.rounded_rectangle([px - 18 * s, py - 30 * s, px + 18 * s, py + 30 * s], int(6 * s), fill=(200, 225, 255, 230))

def police_glow(c, t):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    on = int(t * 4) % 2
    ImageDraw.Draw(g).ellipse([-300, 200, 600, 1100], fill=(RED if on else BLUE) + (120,))
    ImageDraw.Draw(g).ellipse([480, 200, 1380, 1100], fill=(BLUE if on else RED) + (120,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(140)))

def market(c, t, pan=20):
    c.paste(r.zoom_crop(MARKET, 1.0 + 0.012 * t, ox=-pan * t))

# ---------- scenes ----------
def s_hook(c, t, g):
    market(c, t)
    scarf_rack(c, t, 620)
    nb = chunk_t(0, 3)
    punch(c, "viral", "WENT VIRAL", 470, 120, t, color=WHITE, stroke=6, emoji=E_EYES.resize((96, 96)))
    if g > nb:
        lt = g - nb
        paste_center(c, pill("DON'T BUY!", 130, RED, WHITE), W / 2, 1180, scale=0.7 + 0.3 * ease(lt / 0.2), alpha=ease(lt / 0.12))

def s_stall(c, t, g):
    market(c, t, 30)
    scarf_rack(c, t, 640)
    paste_center(c, pill("NAMDAEMUN MARKET • SEOUL", 54, (20, 16, 14), GOLD), W / 2, 450, alpha=ease(t / 0.2))
    paste_center(c, E_SCARF, W / 2, 1290, scale=0.7 + 0.3 * ease(t / 0.3), alpha=ease(t / 0.2))

def s_price(c, t, g):
    c.paste(gradient((40, 24, 30), (6, 4, 6)))
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(6):  # six folded scarves fanning in
        p = ease((t - i * 0.12) / 0.35)
        if p <= 0:
            continue
        x = 190 + i * 140
        y = 1050 - 60 * math.sin(i / 5 * math.pi)
        d.rounded_rectangle([x - 55, y - 140 * p, x + 55, y + 140 * p], 18, fill=SCARF_COLS[i] + (255,))
        d.line([(x - 55, y), (x + 55, y)], fill=(0, 0, 0, 60), width=6)
    punch(c, "6for", "6 FOR ₩10,000", 620, 120, t, color=WHITE, stroke=5)
    label(c, "≈ US$7", 760, 70, GOLD, t - 0.4)

def bubble(c, text_key, text, cy, lt, size=96, col=WHITE):
    img = T(text_key, text, size, fill=(18, 18, 22))
    b = Image.new("RGBA", (img.width + 110, img.height + 90), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle([0, 0, b.width, b.height - 40], 50, fill=col + (255,))
    bd.polygon([(120, b.height - 42), (200, b.height - 42), (110, b.height)], fill=col + (255,))
    b.alpha_composite(img, (55, 20))
    paste_center(c, b, W / 2, cy, scale=min(0.6 + 0.4 * ease(lt / 0.22), (W - 60) / b.width), alpha=ease(lt / 0.12))

def s_pitch(c, t, g):
    market(c, t, -20)
    scarf_rack(c, t, 900)
    pitch = chunk_t(2, 1) - ST[2]
    if t < pitch:
        punch(c, "sp", "HIS SALES PITCH?", 560, 104, t, color=GOLD, stroke=5)
    else:
        lt = t - pitch
        bubble(c, "b1", "YOU'RE OVERSPENDING!", 520, lt, 84)
        w2 = chunk_t(2, 3) - chunk_t(2, 1)
        if lt > w2:
            bubble(c, "b2", "YOU WON'T WEAR THEM!", 780, lt - w2, 76, (255, 225, 140))

def s_views(c, t, g):
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([290, 380, 790, 1300], 60, fill=(25, 27, 34))
    d.rounded_rectangle([315, 420, 765, 1260], 40, fill=(40, 30, 28))
    for i in range(5):  # tiny scarf rack inside the clip
        d.rectangle([370 + i * 75, 560, 420 + i * 75, 820 + 15 * math.sin(t * 3 + i)], fill=SCARF_COLS[i])
    d.polygon([(500, 960), (500, 1080), (600, 1020)], fill=(255, 255, 255, 220))
    p = ease(t / 2.4)
    hearts = random.Random(int(t * 6))
    for k in range(int(8 * p)):
        y = 1200 - ((t * 300 + k * 140) % 800)
        d.ellipse([820 + 40 * math.sin(k + t), y, 870 + 40 * math.sin(k + t), y + 50], fill=(240, 80, 110, 200))
    punch(c, "mil", "MILLIONS", 1190, 150, t, color=GOLD, stroke=6)
    label(c, "OF VIEWS • REPORTED", 1325, 50, WHITE, t - 0.3)

def s_crowd(c, t, g):
    market(c, t)
    crowd(c, t, min(1.0, 0.3 + t / 1.5))
    punch(c, "cc", "THE CROWDS CAME", 520, 88, t, color=WHITE, stroke=6)

def shutter(c, t, closed=1.0):
    d = ImageDraw.Draw(c, "RGBA")
    top, bot = 420, 1300
    y = top + (bot - top) * closed
    d.rectangle([150, top, 930, y], fill=(120, 124, 132))
    for yy in range(top, int(y), 34):
        d.line([(150, yy), (930, yy)], fill=(70, 72, 78), width=6)
    d.rectangle([130, top - 30, 950, top], fill=(60, 60, 66))

def s_oct31(c, t, g):
    market(c, 0, 0)
    scarf_rack(c, t, 520)
    shutter(c, t, ease(t / 0.6))
    if t > 0.5:
        paste_center(c, pill("CLOSED • OCT 31", 80, RED, WHITE), W / 2, 860, scale=0.7 + 0.3 * ease((t - 0.5) / 0.2))

def s_nov4(c, t, g):
    split = chunk_t(5, 2) - ST[5]
    if t < split:
        r.date_card(c, t, "4", "NOV", "REOPENED", (28, 30, 46))
    else:
        lt = t - split
        market(c, lt)
        police_glow(c, lt)
        crowd(c, lt, 1.0)
        paste_center(c, E_POLICE, W / 2, 520, scale=0.8 + 0.2 * math.sin(lt * 8) ** 2)
        label(c, "POLICE CALLED", 700, 64, WHITE, lt - 0.2)

def s_quote(c, t, g):
    c.paste(gradient((20, 16, 14), (4, 3, 3)))
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([90, 470, 990, 1200], 40, fill=(245, 240, 228))
    paste_center(c, T("qm", "“", 260, fill=GOLD), 210, 600)
    lines = ["I WANT TO", "MAKE MONEY TOO,", "BUT THIS", "ISN'T RIGHT."]
    for i, ln in enumerate(lines):
        a = ease((t - 0.25 - i * 0.45) / 0.2)
        paste_center(c, T(("ql", ln), ln, 86, fill=RED if i == 3 else (20, 20, 24)), W / 2, 690 + i * 120, alpha=a)
    label(c, "— THE SCARF SELLER", 1280, 46, WHITE, t - 0.4)

def guard(d, x, y, s):
    person(d, x, y, s, (12, 14, 22, 255))
    d.rectangle([x - 58 * s, y + 90 * s, x + 58 * s, y + 130 * s], fill=(230, 200, 60, 255))  # hi-vis band

def s_safety(c, t, g):
    split = chunk_t(7, 3) - ST[7]
    if t < split:
        c.paste(r.NIGHT)
        shutter(c, 0, 1.0)
        sign = pill("CLOSED TODAY • SAFETY CHECK", 52, (245, 240, 228))
        paste_center(c, sign, W / 2, 820, scale=0.8 + 0.2 * ease(t / 0.25), alpha=ease(t / 0.15))
    else:
        lt = t - split
        market(c, lt, 10)
        d = ImageDraw.Draw(c, "RGBA")
        for i, x in enumerate((260, 540, 820)):
            a = ease((lt - 0.8 - i * 0.25) / 0.2)
            if a > 0:
                guard(d, x, 900 + 30 * (1 - a), 1.6)
                paste_center(c, T("sec", "SECURITY", 30, fill=(15, 15, 18), weight="Black"), x, 900 + 30 * (1 - a) + 176)
        punch(c, "3g", "3 GUARDS", 520, 130, lt, color=GOLD, stroke=6)

def s_why(c, t, g):
    c.paste(Image.new("RGB", (W, H), (6, 6, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    rr = random.Random(int(g * FPS))
    for _ in range(8):
        y = rr.randint(0, H)
        d.rectangle([0, y, W, y + rr.randint(2, 12)], fill=GOLD + (rr.randint(20, 60),))
    punch(c, "why", "WHY IT MATTERS?", 760, 98, t, color=GOLD, stroke=5)

def gate(d, cx, base, s, col):
    """Generic tiered roof gate silhouette."""
    d.rectangle([cx - 300 * s, base - 260 * s, cx + 300 * s, base], fill=col)
    d.rectangle([cx - 80 * s, base - 200 * s, cx + 80 * s, base], fill=(0, 0, 0, 0))
    for k, (w_, h_) in enumerate(((380, 120), (300, 110))):
        y = base - 260 * s - k * 150 * s
        d.polygon([(cx - w_ * s - 40 * s, y), (cx + w_ * s + 40 * s, y), (cx + w_ * 0.7 * s, y - h_ * s), (cx - w_ * 0.7 * s, y - h_ * s)], fill=col)
        d.rectangle([cx - w_ * 0.6 * s, y + 0, cx + w_ * 0.6 * s, y + 40 * s], fill=col)

def s_oldest(c, t, g):
    split = chunk_t(9, 3) - ST[9]
    if t < split:
        c.paste(gradient((70, 40, 30), (10, 8, 12)))
        d = ImageDraw.Draw(c, "RGBA")
        d.ellipse([340, 340, 740, 740], fill=(255, 190, 110, 90))
        gate(d, W / 2, 1300, 1.2 + 0.02 * t, (12, 10, 14, 255))
        punch(c, "old", "ONE OF SEOUL'S OLDEST", 500, 74, t, color=WHITE, stroke=5)
        label(c, "TRADITIONAL MARKETS", 610, 54, GOLD, t - 0.3)
    else:
        lt = t - split
        market(c, lt, -15)
        crowd(c, lt, 1.0, phones=False)
        d = ImageDraw.Draw(c, "RGBA")
        for x in (200, 880):  # neighbours' doors blocked
            d.rectangle([x - 110, 700, x + 110, 1060], outline=RED + (255,), width=10)
            d.line([(x - 110, 700), (x + 110, 1060)], fill=RED + (255,), width=10)
        label(c, "NEIGHBOURS: DOORS BLOCKED", 520, 54, WHITE, lt - 0.1)

def s_take(c, t, g):
    c.paste(r.THEATER)
    punch(c, "mt", "MY TAKE", 520, 90, t, color=WHITE)
    d2 = chunk_t(10, 1) - ST[10]
    if t > d2:
        lt = t - d2
        punch(c, "bs", "BEST SALESMAN", 740, 100, lt, color=GOLD, stroke=5)
        paste_center(c, E_MONEY, W / 2, 1050, scale=0.7 + 0.3 * ease(lt / 0.3), alpha=ease(lt / 0.2))
    d3 = chunk_t(10, 4) - ST[10]
    if t > d3:
        label(c, "SAYS: SAVE YOUR MONEY", 1220, 56, WHITE, t - d3)

def s_outro(c, t, g):
    market(c, t, 10)
    punch(c, "wyg", "WOULD YOU GO?", 520, 110, t, color=WHITE, stroke=6)
    paste_center(c, pill("YES", 96, GOLD), 330, 800, scale=0.6 + 0.4 * ease((t - 0.2) / 0.25), alpha=ease((t - 0.2) / 0.15))
    paste_center(c, pill("NO WAY", 96, ICE), 760, 800, scale=0.6 + 0.4 * ease((t - 0.5) / 0.25), alpha=ease((t - 0.5) / 0.15))
    rc = ST[12] - ST[11]
    if t > rc:
        punch(c, "sun4", "SUNDAY RECAP", 1060, 84, t - rc, color=GOLD)
    if t > rc + 1.0:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - rc - 1.0) / 0.3))

# ---------- wire into render.py's frame() ----------
r.SCENES = [
    (0.0, ST[1], s_hook), (ST[1], chunk_t(1, 3), s_stall), (chunk_t(1, 3), ST[2], s_price),
    (ST[2], ST[3], s_pitch), (ST[3], chunk_t(3, 3), s_views), (chunk_t(3, 3), ST[4], s_crowd),
    (ST[4], ST[5], s_oct31), (ST[5], ST[6], s_nov4), (ST[6], ST[7], s_quote), (ST[7], ST[8], s_safety),
    (ST[8], ST[9], s_why), (ST[9], ST[10], s_oldest), (ST[10], ST[11], s_take), (ST[11], DUR + 0.1, s_outro),
]
r.CALLOUTS = [
    (chunk_t(1, 3), ST[2] - 0.1, "c1", "6 SCARVES ≈ $7", None),
    (chunk_t(3, 1), chunk_t(3, 3), "c2", "MILLIONS OF VIEWS", None),
    (chunk_t(5, 2), ST[6] - 0.05, "c3", "POLICE CALLED • NOV 4", None),
    (chunk_t(7, 3), ST[8] - 0.05, "c4", "3 SECURITY GUARDS", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":  # python3 render004.py stills t1 t2 ...
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s004_{s}.png")
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
