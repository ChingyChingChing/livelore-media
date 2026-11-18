"""Live Lore Short 014 (Hunger Games: Sunrise on the Reaping - record presales ahead of its Nov 20 opening) - reuses render.py's engine/style.
Usage: python3 render014.py OUT.mp4 [start end]  |  python3 render014.py stills t1 t2 ...
All visuals drawn in code (generic sunrise/mountains/forest arena, generic figure silhouettes, bar charts, date cards,
ticket stubs, search bar, emoji; no film footage, posters, key art, logos, symbols or photos). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
CYAN = (90, 200, 255)
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments014.json"))
ST = [s[0] for s in SEG]

def emoji(ch, size):
    f = ImageFont.truetype(r.EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(size * im.width / im.height), size), Image.LANCZOS)

def pill(text, size, fill, color=DARK):
    img = T(("pill", text, size, color), text, size, fill=color, weight="Black")
    p = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([0, 0, p.width, p.height], 26, fill=fill + (255,))
    p.alpha_composite(img, (35, 14))
    return p

def stamp(text, size, col, rot=-8):
    img = T(("st", text, size, col), text, size, fill=col, weight="Black")
    im = Image.new("RGBA", (img.width + 70, img.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 20, outline=col + (255,), width=10)
    im.alpha_composite(img, (35, 20))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

def pop(lt, d=0.25):
    return 0.6 + 0.4 * ease(lt / d), ease(lt / 0.12)

def cjk(text, size, col=DARK):
    f = ImageFont.truetype(CJK, size)
    bb = f.getbbox(text)
    im = Image.new("RGBA", (bb[2] + 10, bb[3] + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((5, 5), text, font=f, fill=col)
    return im
def date_card2(c, t, big, small, sub, tint, size=300):
    c.paste(gradient(tint, (4, 4, 8)))
    cw, ch = 680, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=RED + (255,))
    dd.rectangle([0, 120, cw, 170], fill=RED + (255,))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 250 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1290, 52, WHITE, t - 0.25)

def hbars(c, t, rows, top=560, gap=230, maxw=600):
    """rows: [(name, value, max, color, value_label)] horizontal bars, real proportions."""
    d = ImageDraw.Draw(c, "RGBA")
    k = ease(t / 0.8)
    for i, (nm, v, mx, col, vl) in enumerate(rows):
        y = top + i * gap
        lb = T(("hb", nm), nm, 52, fill=WHITE, weight="Black")
        c.alpha_composite(lb, (120, y))
        w = int(maxw * v / mx * k)
        d.rounded_rectangle([120, y + 75, 120 + max(w, 20), y + 165], 18, fill=col + (255,))
        if k > 0.6:
            vt = T(("hv", vl), vl, 60, fill=GOLD if col != GOLD else WHITE, weight="Black")
            c.alpha_composite(vt, (min(120 + w + 24, W - vt.width - 30), y + 88))
def ticket(text, col=GOLD, rot=0):
    w, h = 520, 230
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 24, fill=col + (255,))
    for y in range(18, h, 36):
        d.ellipse([w - 150 - 8, y, w - 150 + 8, y + 16], fill=(0, 0, 0, 0))
    d.ellipse([-30, h / 2 - 30, 30, h / 2 + 30], fill=(0, 0, 0, 0))
    d.ellipse([w - 30, h / 2 - 30, w + 30, h / 2 + 30], fill=(0, 0, 0, 0))
    a = r.text_img(text, 70, fill=DARK)
    im.alpha_composite(a, ((w - 150 - a.width) // 2, (h - a.height) // 2))
    adm = r.text_img("ADMIT 1", 30, fill=DARK, weight="Bold")
    adm = adm.rotate(90, expand=True)
    im.alpha_composite(adm, (w - 75 - adm.width // 2, (h - adm.height) // 2))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

ORANGE, EMBER = (255, 140, 40), (255, 90, 30)
E_FIRE, E_POPCORN, E_EYES, E_UP, E_CHART, E_THINK, E_CLOCK = (emoji(c, 150) for c in "🔥🍿👀⬆📈🤔⏳")

# ---------- art ----------
CHART_BG = gradient((16, 18, 34), (3, 3, 8))
EMBER_BG = gradient((70, 22, 8), (8, 3, 2))
GLOW_BG = gradient((30, 20, 50), (4, 3, 10))
KR_BG = gradient((240, 240, 246), (200, 204, 214))

def mountains(seed, base, amp, col, step=90):
    rng = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [(0, H)]
    for x in range(-step, W + 2 * step, step):
        pts.append((x, base - rng.uniform(0.2, 1.0) * amp))
    pts.append((W, H))
    ImageDraw.Draw(im).polygon(pts, fill=col)
    return im

def forest(seed, base, col, n=26, hmin=140, hmax=320):
    rng = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x = rng.uniform(-40, W + 40); h = rng.uniform(hmin, hmax); w = h * 0.38
        for k in range(3):
            y0 = base - h + k * h * 0.28
            d.polygon([(x, y0), (x - w * (0.5 + 0.2 * k), y0 + h * 0.45), (x + w * (0.5 + 0.2 * k), y0 + h * 0.45)], fill=col)
        d.rectangle([x - 8, base - 20, x + 8, base + 10], fill=col)
    d.rectangle([0, base, W, H], fill=col)
    return im

SKY = gradient((255, 170, 90), (60, 30, 70))
MTN_FAR = mountains(5, 1050, 380, (120, 60, 90, 255))
MTN_NEAR = mountains(9, 1250, 300, (60, 30, 55, 255), step=140)
TREES = forest(14, 1500, (14, 10, 20, 255))

def arena(c, t, sun=True):
    c.paste(SKY)
    if sun:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        y = 1000 - 120 * ease(t / 2.5)
        ImageDraw.Draw(glow).ellipse([W / 2 - 330, y - 330, W / 2 + 330, y + 330], fill=(255, 220, 140, 200))
        c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
        ImageDraw.Draw(c).ellipse([W / 2 - 170, y - 170, W / 2 + 170, y + 170], fill=(255, 236, 190, 255))
    c.alpha_composite(MTN_FAR)
    c.alpha_composite(MTN_NEAR.transform((W, H), Image.AFFINE, (1, 0, -12 * t, 0, 1, 0)))
    c.alpha_composite(TREES.transform((W, H), Image.AFFINE, (1, 0, -30 * t, 0, 1, 0)))

def figure(h, col):
    """Generic person silhouette (no likeness)."""
    w = int(h * 0.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hr = h * 0.13
    d.ellipse([w / 2 - hr, 0, w / 2 + hr, 2 * hr], fill=col)
    d.rounded_rectangle([w * 0.12, 2 * hr + h * 0.03, w * 0.88, h * 0.62], int(w * 0.18), fill=col)
    d.rounded_rectangle([w * 0.22, h * 0.55, w * 0.47, h], int(w * 0.1), fill=col)
    d.rounded_rectangle([w * 0.53, h * 0.55, w * 0.78, h], int(w * 0.1), fill=col)
    return im

FIG_BIG = figure(720, (12, 8, 16, 255))
FIG_S = figure(110, (255, 230, 200, 255))
FIG_G = figure(110, GOLD + (255,))
TICKETS = [ticket("PRE", GOLD, -10), ticket("SALE", (240, 240, 235), 6), ticket("IMAX", ORANGE, -4)]

def search_bar(c, t):
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([100, 520, W - 100, 680], 80, fill=(255, 255, 255, 255), outline=(180, 185, 200, 255), width=4)
    d.ellipse([150, 560, 220, 630], outline=(120, 125, 140, 255), width=10)
    d.line([(210, 622), (240, 652)], fill=(120, 125, 140, 255), width=12)
    txt = "헝거게임"
    n = min(len(txt), int(t / 0.12) + 1)
    c.alpha_composite(cjk(txt[:n], 90, DARK), (280, 545))

def trend_line(c, t):
    d = ImageDraw.Draw(c, "RGBA")
    rng = random.Random(3)
    pts = []
    for i in range(14):
        x = 140 + i * 60
        y = 1180 - (20 + rng.uniform(0, 40) if i < 10 else 60 + (i - 9) ** 2 * 14)
        pts.append((x, y))
    k = ease(t / 0.9)
    m = max(2, int(len(pts) * k))
    d.line([(120, 1200), (W - 120, 1200)], fill=(170, 175, 190, 255), width=4)
    d.line(pts[:m], fill=(60, 120, 230, 255), width=14, joint="curve")
    x, y = pts[m - 1]
    d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=(60, 120, 230, 255))

def gauge(c, t):
    """Tracking rising: 60 -> 80+ on a vertical bar (real proportions vs 100)."""
    d = ImageDraw.Draw(c, "RGBA")
    x0, x1, base, top = W / 2 - 120, W / 2 + 120, 1250, 550
    d.rounded_rectangle([x0, top, x1, base], 30, outline=(90, 95, 130, 255), width=6)
    v = 60 + 20 * ease((t - 0.3) / 0.9)
    y = base - (base - top) * v / 100
    d.rounded_rectangle([x0 + 12, y, x1 - 12, base - 12], 22, fill=(GREEN if v > 75 else ORANGE) + (255,))
    for mark, lab in ((60, "$60M"), (80, "$80M"), (100, "$100M")):
        ym = base - (base - top) * mark / 100
        d.line([(x1 + 10, ym), (x1 + 50, ym)], fill=WHITE + (255,), width=5)
        lb = T(("gm", lab), lab, 48, fill=WHITE, weight="Bold")
        c.alpha_composite(lb, (int(x1 + 66), int(ym - lb.height / 2)))
    vt = T(("gv", int(v)), f"${int(v)}M" + ("+" if v >= 79.5 else ""), 72, fill=GOLD, weight="Black")
    c.alpha_composite(vt, (int(x0 - vt.width - 40), int(y - vt.height / 2)))

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(CHART_BG)
    label(c, "LAST MOVIE'S US OPENING", 560, 48, WHITE, t)
    punch(c, "h1", "UNDER $45M", 760, 140, t, color=WHITE, stroke=10)
    paste_center(c, E_THINK.resize((170, 170)), W / 2, 1040, *pop(t - 0.4))

def s_wicked(c, t, g):
    c.paste(EMBER_BG)
    for i, (tk, x, y) in enumerate(zip(TICKETS, (320, 760, 540), (600, 660, 900))):
        paste_center(c, tk, x, y - 400 * (1 - ease((t - i * 0.12) / 0.3)), alpha=ease((t - i * 0.12) / 0.12))
    if t > 0.5:
        paste_center(c, stamp("OUT-SELLING WICKED?", 92, GOLD, -5), W / 2, 1150, *pop(t - 0.5))

def s_title(c, t, g):
    arena(c, t)
    punch(c, "t1", "SUNRISE ON", 560, 130, t, color=WHITE, stroke=8)
    punch(c, "t2", "THE REAPING", 720, 130, max(0, t - 0.35), color=GOLD, stroke=8)

def s_date(c, t, g):
    date_card2(c, t, "20", "NOV 2026", "US RELEASE · THIS FRIDAY", (90, 40, 20))

def s_presale(c, t, g):
    c.paste(GLOW_BG)
    for i, (tk, x, y) in enumerate(zip(TICKETS, (300, 780, 540), (700, 760, 980))):
        paste_center(c, tk, x, y - 500 * (1 - ease((t - i * 0.15) / 0.35)), alpha=ease((t - i * 0.15) / 0.15))
    if t > 0.6:
        paste_center(c, pill("LIONSGATE POST-COVID RECORD", 62, GOLD), W / 2, 1220, *pop(t - 0.6))

def s_ahead(c, t, g):
    c.paste(CHART_BG)
    punch(c, "ah1", "AHEAD OF", 600, 150, t, color=WHITE, stroke=6)
    punch(c, "ah2", "WICKED", 780, 190, max(0, t - 0.3), color=GREEN, stroke=8)
    label(c, "PRESALES · PER DEADLINE", 960, 46, WHITE, t - 0.5)
    paste_center(c, E_UP.resize((150, 150)), W / 2, 1140, *pop(t - 0.7))

def s_track(c, t, g):
    c.paste(CHART_BG)
    label(c, "OPENING WEEKEND TRACKING", 470, 54, WHITE, t)
    gauge(c, t)

def s_100(c, t, g):
    c.paste(EMBER_BG)
    v = 100 * ease(t / 0.9)
    punch(c, ("m100", int(v)), f"${int(v)}M?", 760, 250, min(t, 0.3) if t < 0.9 else t, color=GOLD, stroke=10)
    label(c, "SOME TRACKERS' FORECAST", 990, 56, WHITE, t - 0.3)
    paste_center(c, E_FIRE.resize((170, 170)), W / 2, 1180, 1.0 + 0.05 * math.sin(g * 5), ease(t / 0.2))

def s_2023(c, t, g):
    date_card2(c, t, "2023", "PREQUEL", "BALLAD OF SONGBIRDS & SNAKES", (50, 30, 60), size=230)

def s_bars(c, t, g):
    c.paste(CHART_BG)
    label(c, "US OPENING WEEKEND", 480, 56, WHITE, t)
    hbars(c, t, [("BALLAD (2023)", 44.6, 80, (90, 100, 130), "$44.6M"),
                 ("NEW ONE · TRACKING", 80, 80, ORANGE, "$80M+?")], top=600)

def s_why(c, t, g):
    c.paste(GLOW_BG)
    punch(c, "why", "WHY THE HYPE?", 760, 118, t, color=WHITE, stroke=8)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 1000, *pop(t - 0.3))

def s_teen(c, t, g):
    arena(c, t, sun=True)
    paste_center(c, FIG_BIG, W / 2, 1150 + 40 * (1 - ease(t / 0.5)), scale=1.0 + 0.03 * t)
    paste_center(c, pill("A TEENAGE HAYMITCH", 80, GOLD), W / 2, 520, *pop(t - 0.2))

def s_24(c, t, g):
    c.paste(CHART_BG)
    d = ImageDraw.Draw(c, "RGBA")
    k = ease(t / 0.7)
    d.line([(140, 900), (140 + (W - 280) * k, 900)], fill=WHITE + (255,), width=10)
    for x, lab, col in ((160, "THIS STORY", GOLD), (W - 160, "KATNISS", WHITE)):
        if k > (0 if x < 500 else 0.9):
            d.ellipse([x - 30, 870, x + 30, 930], fill=col + (255,))
            lb = T(("tl", lab), lab, 50, fill=col, weight="Black")
            c.alpha_composite(lb, (int(min(max(x - lb.width / 2, 40), W - 40 - lb.width)), 960))
    punch(c, "y24", "24 YEARS", 680, 170, t, color=GOLD, stroke=8)
    paste_center(c, E_CLOCK.resize((130, 130)), W / 2, 1160, *pop(t - 0.4))

def s_50(c, t, g):
    arena(c, t, sun=False)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(0, 0, 0, 90))
    punch(c, "n50", "50TH", 720, 330, t, color=GOLD, stroke=12)
    label(c, "HUNGER GAMES · A QUARTER QUELL", 950, 50, WHITE, t - 0.3)

def s_double(c, t, g):
    c.paste(EMBER_BG)
    for i in range(48):
        row, col = divmod(i, 8)
        x, y = 175 + col * 105, 520 + row * 140
        ap = ease((t - (0 if i < 24 else 0.5 + (i - 24) * 0.02)) / 0.15)
        paste_center(c, FIG_S if i < 24 else FIG_G, x, y, alpha=ap)
    if t > 0.9:
        paste_center(c, pill("24 → 48 TRIBUTES", 84, GOLD), W / 2, 1330 - 30, *pop(t - 0.9))

def s_korea(c, t, g):
    c.paste(KR_BG)
    d = ImageDraw.Draw(c, "RGBA")
    rad = 260 * (0.8 + 0.2 * ease(t / 0.4))
    d.ellipse([W / 2 - rad, 820 - rad, W / 2 + rad, 820 + rad], fill=(30, 60, 140, 255))
    paste_center(c, cjk("한국", 190, WHITE), W / 2, 820, *pop(t - 0.2))
    paste_center(c, pill("NOT JUST THE US", 72, GOLD), W / 2, 1200, *pop(t - 0.4))

def s_trend(c, t, g):
    c.paste(KR_BG)
    search_bar(c, t)
    trend_line(c, t - 0.3)
    label(c, "TRENDING SEARCHES · KOREA", 790, 50, (40, 50, 80), t - 0.2)

def s_take(c, t, g):
    arena(c, t)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(0, 0, 0, 110))
    punch(c, "mt14", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_POPCORN.resize((180, 180)), W / 2, 880, *pop(t - 0.3))

def s_2015(c, t, g):
    c.paste(CHART_BG)
    label(c, "BIGGEST US OPENING SINCE...", 480, 52, WHITE, t)
    hbars(c, t, [("MOCKINGJAY PT 2 (2015)", 102.7, 102.7, (90, 100, 130), "$102.7M"),
                 ("BALLAD (2023)", 44.6, 102.7, (90, 100, 130), "$44.6M"),
                 ("NEW ONE IF $100M+", 100, 102.7, ORANGE, "?")], top=580, gap=220)

def s_back(c, t, g):
    c.paste(EMBER_BG)
    paste_center(c, stamp("SO BACK", 200, GOLD, -7), W / 2, 760, *pop(t))
    paste_center(c, E_FIRE.resize((160, 160)), 820, 1020, *pop(t - 0.3))
    paste_center(c, stamp("NO CAP", 110, WHITE, 5), W / 2, 1100, *pop(t - 0.6))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq14", "WHO'S YOUR PICK?", 540, 96, t, color=WHITE, stroke=6)
    paste_center(c, pill("TEAM YOUNG HAYMITCH", 76, GOLD), W / 2, 820, *pop(t - 0.15))
    paste_center(c, pill("TEAM KATNISS", 76, ORANGE), W / 2, 1060, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun14", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.5:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.5) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 4), ST[1], at(1, 3), ST[2], at(2, 5), ST[3], at(3, 3), ST[4], at(4, 5), ST[5], at(5, 2), at(5, 7),
     ST[6], at(6, 3), ST[7], at(7, 2), ST[8], at(8, 3), at(8, 6), ST[9], ST[10], DUR + 0.1]
FNS = [s_hook, s_wicked, s_title, s_date, s_presale, s_ahead, s_track, s_100, s_2023, s_bars, s_why, s_teen, s_24,
       s_50, s_double, s_korea, s_trend, s_take, s_2015, s_back, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[3], ST[4] - 0.1, "c1", "PROJECTIONS · NOT RESULTS", None),
    (ST[6], ST[7] - 0.1, "c2", "BASED ON THE 2025 NOVEL", None),
    (ST[7], ST[8] - 0.1, "c3", "SOURCE: GOOGLE TRENDS KR", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s014_{s}.png")
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
