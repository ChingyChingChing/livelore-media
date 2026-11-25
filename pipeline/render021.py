"""Live Lore Short 021 (Miss Universe 2026: Puerto Rico's Jennifer Barreto, reportedly the first mother to win,
crowned Nov 24 2026 in San Juan on home soil; Puerto Rico's 6th crown, first in 20 years; mothers/married women
eligible since 2023; Philippines' Bea Millan-Windorski 3rd runner-up) - reuses render.py.
Usage: python3 render021.py OUT.mp4 [start end]  |  python3 render021.py stills t1 t2 ...
All visuals drawn in code (generic drawn crowns, stage, runway, calendar, rulebook, checklist, podium, simple drawn
national flags, emoji, names as plain text; no photos, pageant footage, logos or broadcast graphics).
Music: original lofi from music.py (strategy.md music test, Short 21).
"""

import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
CYAN, ORANGE, PURPLE = (90, 200, 255), (255, 140, 40), (150, 90, 230)
PAPER = (250, 244, 232)
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments021.json"))
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

E_EYES, E_THINK, E_GLOBE, E_PLANE, E_HEART, E_CHECK, E_FIRE, E_PIN, E_MIC, E_WAVE, E_SPARK = (emoji(ch, 150) for ch in
    ["👀", "🤔", "🌏", "✈️", "💜", "✅", "🔥", "📍", "🎤", "👋", "✨"])


def spotlights(c, t, cols=((255, 230, 150), (200, 120, 255), (120, 200, 255))):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, col in enumerate(cols):
        x0 = (i + 0.5) * W / len(cols)
        a = math.sin(t * 1.4 + i * 2.0) * 260
        d.polygon([(x0, -40), (x0 + a - 230, H * 0.85), (x0 + a + 230, H * 0.85)], fill=col + (46,))
    c.alpha_composite(layer.filter(ImageFilter.GaussianBlur(18)))

def card(head, name, col, sub=None, w=900, h=560):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=(250, 246, 238, 255))
    d.rounded_rectangle([0, 0, w, 140], 40, fill=col + (255,))
    d.rectangle([0, 100, w, 140], fill=col + (255,))
    hs = 58
    hd = r.text_img(head, hs, fill=WHITE, weight="ExtraBold", spacing=4)
    while hd.width > w - 60:
        hs -= 4
        hd = r.text_img(head, hs, fill=WHITE, weight="ExtraBold", spacing=4)
    im.alpha_composite(hd, ((w - hd.width) // 2, (140 - hd.height) // 2 + 4))
    lines = [name] if len(name) <= 12 else [" ".join(name.split()[:len(name.split()) // 2 + (1 if len(name.split()) % 2 else 0)]),
                                               " ".join(name.split()[len(name.split()) // 2 + (1 if len(name.split()) % 2 else 0):])]
    ns = 150 if len(lines) == 1 else 100
    imgs = [r.text_img(l, ns, fill=DARK) for l in lines]
    while max(i.width for i in imgs) > w - 80:
        ns -= 6
        imgs = [r.text_img(l, ns, fill=DARK) for l in lines]
    y = 200 if sub else 240
    if len(lines) == 2:
        y = 165 if sub else 190
    for i in imgs:
        im.alpha_composite(i, ((w - i.width) // 2, y))
        y += int(ns * 1.1)
    if sub:
        sb = r.text_img(sub, 52, fill=(110, 110, 120), weight="Bold", spacing=4)
        im.alpha_composite(sb, ((w - sb.width) // 2, 420))
    return im



NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
GOLD_BG = gradient((90, 60, 10), (10, 6, 2))
RED_BG = gradient((110, 20, 24), (12, 2, 3))
PURP_BG = gradient((60, 20, 100), (6, 3, 14))
ROSE_BG = gradient((120, 30, 80), (14, 3, 10))
TEAL_BG = gradient((10, 60, 90), (2, 6, 12))
JADE_BG = gradient((10, 70, 55), (2, 10, 8))
PINK = (255, 90, 170)
PR_BLUE, PH_BLUE = (0, 80, 200), (0, 56, 168)
E_CROWN, E_BABY, E_HOUSE, E_SCROLL, E_TROPHY, E_RING, E_SHOE, E_FLASH = (emoji(ch, 150) for ch in
    ["👑", "🍼", "🏠", "📜", "🏆", "💍", "👠", "📸"])

def crown(col=GOLD, w=520, glow=True):
    h = int(w * 0.72)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0.04, 0.85), (0.04, 0.30), (0.25, 0.55), (0.5, 0.06), (0.75, 0.55), (0.96, 0.30), (0.96, 0.85)]
    d.polygon([(x * w, y * h) for x, y in pts], fill=col + (255,))
    d.rounded_rectangle([0.04 * w, 0.78 * h, 0.96 * w, 0.98 * h], 14, fill=tuple(int(v * 0.8) for v in col) + (255,))
    for x, y, cc in ((0.04, 0.30, PINK), (0.5, 0.06, (120, 220, 255)), (0.96, 0.30, PINK)):
        rr = w * 0.055
        d.ellipse([x * w - rr, y * h - rr, x * w + rr, y * h + rr], fill=cc + (255,))
    for k, cc in enumerate((PINK, (120, 220, 255), (140, 255, 160), (120, 220, 255), PINK)):
        x = (0.16 + k * 0.17) * w
        d.ellipse([x - 14, 0.88 * h - 14, x + 14, 0.88 * h + 14], fill=cc + (255,))
    if not glow:
        return im
    g = Image.new("RGBA", (w + 160, h + 160), (0, 0, 0, 0))
    g.alpha_composite(im, (80, 80))
    halo = g.filter(ImageFilter.GaussianBlur(30))
    out = Image.new("RGBA", g.size, (0, 0, 0, 0))
    out.alpha_composite(halo); out.alpha_composite(halo); out.alpha_composite(g)
    return out
CROWN = crown()
CROWN_S = crown(w=170, glow=False)
CROWN_GREY = crown((90, 90, 105), w=170, glow=False)

def sparkles(c, g, n=14, seed=3):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(c)
    for i in range(n):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(420, 1300)
        a = (math.sin(g * 4 + i * 1.7) + 1) / 2
        s = 6 + 14 * a
        col = (255, 240, 190, int(200 * a))
        d.polygon([(x, y - s * 2), (x + s * 0.5, y), (x, y + s * 2), (x - s * 0.5, y)], fill=col)
        d.polygon([(x - s * 2, y), (x, y + s * 0.5), (x + s * 2, y), (x, y - s * 0.5)], fill=col)

def stage(c, g):
    d = ImageDraw.Draw(c)
    d.ellipse([-200, 1180, W + 200, 1560], fill=(40, 20, 60, 255))
    d.ellipse([-100, 1210, W + 100, 1500], fill=(70, 40, 100, 255))

def runway(c, g):
    d = ImageDraw.Draw(c)
    d.polygon([(W / 2 - 70, 560), (W / 2 + 70, 560), (W / 2 + 460, 1320), (W / 2 - 460, 1320)], fill=(60, 55, 72, 255))
    for k in range(9):  # runway edge lights
        f = k / 8
        y = 560 + f * 760
        hw = 70 + f * 390
        on = math.sin(g * 6 - k) > 0
        for x in (W / 2 - hw, W / 2 + hw):
            rr = 5 + 8 * f
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=((255, 230, 150, 255) if on else (120, 110, 90, 255)))

def flashes(c, g, seed_rate=6):
    rnd = random.Random(int(g * seed_rate))
    for i in range(5):
        if rnd.random() < 0.45:
            x, y = rnd.uniform(100, W - 100), rnd.uniform(480, 1200)
            fl = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
            ImageDraw.Draw(fl).ellipse([0, 0, 300, 300], fill=(255, 255, 255, 130))
            paste_center(c, fl.filter(ImageFilter.GaussianBlur(40)), x, y)

def star(d, cx, cy, ro, ri, col, rot=-90):
    pts = []
    for k in range(10):
        rr = ro if k % 2 == 0 else ri
        a = math.radians(rot + k * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)

def flag_pr(w=760):
    h = int(w * 2 / 3)
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    for k in (0, 2, 4):
        d.rectangle([0, k * h / 5, w, (k + 1) * h / 5], fill=(237, 0, 0, 255))
    d.polygon([(0, 0), (w * 0.43, h / 2), (0, h)], fill=PR_BLUE + (255,))
    star(d, w * 0.15, h / 2, h * 0.13, h * 0.05, (255, 255, 255, 255))
    return im

def flag_ph(w=760):
    h = w // 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h / 2], fill=PH_BLUE + (255,))
    d.rectangle([0, h / 2, w, h], fill=(206, 17, 38, 255))
    tw = h * 0.866
    d.polygon([(0, 0), (tw, h / 2), (0, h)], fill=(255, 255, 255, 255))
    cy, cx = h / 2, tw * 0.36
    sun = (252, 209, 22, 255)
    for k in range(8):
        a = math.radians(k * 45)
        d.line([(cx, cy), (cx + h * 0.15 * math.cos(a), cy + h * 0.15 * math.sin(a))], fill=sun, width=int(h * 0.04))
    d.ellipse([cx - h * 0.08, cy - h * 0.08, cx + h * 0.08, cy + h * 0.08], fill=sun)
    for sx, sy in ((h * 0.09, h * 0.1), (h * 0.09, h * 0.9), (tw * 0.86, h / 2)):
        star(d, sx, sy, h * 0.045, h * 0.018, sun)
    return im

def waved(flag, g):
    """Gentle vertical wave on a drawn flag."""
    out = Image.new("RGBA", (flag.width, flag.height + 60), (0, 0, 0, 0))
    for x in range(0, flag.width, 8):
        dy = int(22 * math.sin(g * 3 + x / 90))
        out.alpha_composite(flag.crop((x, 0, min(x + 8, flag.width), flag.height)), (x, 30 + dy))
    return out

FLAG_PR, FLAG_PH = flag_pr(), flag_ph()

def calendar(month, big, col=RED):
    cw, ch = 560, 560
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 150], 36, fill=col + (255,))
    dd.rectangle([0, 110, cw, 150], fill=col + (255,))
    sm = r.text_img(month, 80, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 30))
    bg_ = r.text_img(big, 230, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 220))
    return cd

def rulebook(t):
    w, h = 720, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(250, 246, 236, 255))
    hd = r.text_img("THE RULES", 80, fill=DARK)
    im.alpha_composite(hd, ((w - hd.width) // 2, 50))
    for k in range(9):
        y = 190 + k * 70
        d.rounded_rectangle([70, y, w - 70 - (k * 53 % 160), y + 22], 11, fill=(200, 196, 186, 255))
    return im

def checklist(t):
    w, h = 900, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 36, fill=(250, 246, 238, 255))
    for k, txt in enumerate(("MOMS", "MARRIED WOMEN")):
        y = 110 + k * 210
        tx = r.text_img(txt, 70, fill=DARK)
        im.alpha_composite(tx, (60, y))
        if t > 0.25 + 0.35 * k:
            ck = E_CHECK.resize((130, 130))
            im.alpha_composite(ck, (w - 190, y - 10))
    return im

def podium(t):
    w, h = 980, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    names = ["5", "4", "3", "2", "1"]  # placement from left: 4th RU, 3rd RU, 2nd RU, 1st RU, winner
    labs = ["4TH RU", "3RD RU", "2ND RU", "1ST RU", "WINNER"]
    hts = [0.32, 0.45, 0.58, 0.74, 1.0]
    for i in range(5):
        k = ease((t - i * 0.07) / 0.4)
        x = 30 + i * 190
        top = h - 110 - (h - 260) * hts[i] * k
        col = PH_BLUE if i == 1 else (GOLD if i == 4 else (90, 90, 120))
        d.rounded_rectangle([x, top, x + 160, h - 110], 16, fill=col + (255,))
        tx = r.text_img(labs[i], 34, fill=WHITE, weight="ExtraBold")
        im.alpha_composite(tx, (int(x + (160 - tx.width) / 2), h - 90))
    im.alpha_composite(FLAG_PH.resize((150, 75)), (30 + 190 + 5, int(h - 110 - (h - 260) * 0.45 * ease((t - 0.07) / 0.4)) - 95))
    im.alpha_composite(FLAG_PR.resize((120, 80)), (30 + 4 * 190 + 20, int(h - 110 - (h - 260) * ease((t - 0.28) / 0.4)) - 100))
    return im

def punch_in(fn, amt=0.08, d=0.3):
    """Hard-cut scene with a punch-in (scale 1.0 -> 1+amt over d s), per strategy.md's 5-11 s rule."""
    def wrapped(c, t, g):
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        fn(tmp, t, g)
        s = 1.0 + amt * ease(t / d)
        big = tmp.resize((int(W * s), int(H * s)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        c.paste(big.crop((ox, oy, ox + W, oy + H)))
    return wrapped

def big_num(c, key, text, cy, size, t, col=GOLD):
    punch(c, key, text, cy, size, t, color=col, stroke=8)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(PURP_BG); spotlights(c, g); stage(c, g); sparkles(c, g)
    paste_center(c, CROWN, W / 2, 1000 - 20 * math.sin(g * 2), scale=0.9 + 0.1 * ease(t / 0.25), alpha=ease(t / 0.08))
    punch(c, "h75", "75 YEARS", 560, 190, t, color=WHITE, stroke=8)

def s_firstmom(c, t, g):
    c.paste(ROSE_BG); spotlights(c, g, ((255, 200, 230), (255, 230, 150))); sparkles(c, g, seed=5)
    paste_center(c, CROWN, W / 2, 1080, scale=0.75, alpha=1.0)
    punch(c, "fm1", "FIRST MOM", 560, 170, t, color=GOLD, stroke=8)
    if t > 0.25:
        paste_center(c, stamp("EVER", 130, WHITE, -7), W / 2, 760, *pop(t - 0.25))

def s_runway(c, t, g):
    c.paste(gradient((30, 30, 40), (4, 4, 6))); flashes(c, g); runway(c, g)
    paste_center(c, E_SHOE.resize((240, 240)), W / 2, 1000 - 200 * ease(t / 1.5), scale=0.8 + 0.3 * ease(t / 1.5))
    big_num(c, "feb", "FEB 2026", 560, 150, t)

def s_cal(c, t, g):
    c.paste(TEAL_BG)
    k = ease(t / 0.5)
    paste_center(c, calendar("FEB", "1ST", (90, 110, 170)), W / 2 - 230 * k, 900, scale=0.8, alpha=1.0)
    if t > 0.45:
        paste_center(c, calendar("NOV", "👑" if False else "24", RED), W / 2 + 230, 900, *pop(t - 0.45))
    label(c, "FIRST RUNWAY → THE CROWN", 1260, 54, WHITE, t - 0.2)

def s_pr(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g)
    paste_center(c, waved(FLAG_PR, g), W / 2, 960, *pop(t))
    punch(c, "jb", "JENNIFER BARRETO", 560, 92, t - 0.1, color=WHITE, stroke=7)
    label(c, "MISS PUERTO RICO", 1280, 70, GOLD, t - 0.3)

def s_date(c, t, g):
    date_card2(c, t, "24", "NOV 2026", "SAN JUAN, PUERTO RICO", (110, 30, 90))

def s_home(c, t, g):
    c.paste(GOLD_BG); sparkles(c, g, seed=9)
    paste_center(c, E_HOUSE.resize((300, 300)), W / 2, 880, *pop(t))
    paste_center(c, E_PIN.resize((170, 170)), W / 2 + 190, 700 + 10 * math.sin(g * 6), *pop(t - 0.15))
    if t > 0.3:
        paste_center(c, stamp("HOME SOIL", 120, WHITE, -6), W / 2, 1200, *pop(t - 0.3))

def s_rules(c, t, g):
    c.paste(gradient((40, 34, 26), (8, 6, 4)))
    paste_center(c, rulebook(t), W / 2, 930, scale=0.9 + 0.02 * t, alpha=ease(t / 0.1))
    if t > 0.5:
        paste_center(c, stamp("NEW RULE: 2023", 100, RED, -9), W / 2, 980, *pop(t - 0.5))

def s_check(c, t, g):
    c.paste(JADE_BG)
    paste_center(c, checklist(t), W / 2, 900, *pop(t))
    label(c, "ALLOWED TO COMPETE", 1260, 64, GOLD, t - 0.2)

def s_six(c, t, g):
    c.paste(RED_BG); spotlights(c, g, ((255, 230, 150),))
    yrs = ["1970", "1985", "1993", "2001", "2006", "2026"]
    for i, y in enumerate(yrs):
        x = 175 + (i % 3) * 365
        yy = 760 + (i // 3) * 360
        lit = t > 0.15 + i * 0.22
        paste_center(c, CROWN_S if lit else CROWN_GREY, x, yy, *(pop(t - 0.15 - i * 0.22) if lit else (1.0, 1.0)))
        paste_center(c, T(("yr", y, lit and i == 5), y, 54, fill=GOLD if (lit and i == 5) else WHITE, weight="ExtraBold"), x, yy + 120)
    punch(c, "6th", "6TH CROWN", 500, 150, t, color=GOLD, stroke=8)

def s_twenty(c, t, g):
    c.paste(gradient((20, 40, 110), (3, 5, 14))); sparkles(c, g, seed=11)
    n = min(20, int(1 + 19 * ease(t / 0.9)))
    big_num(c, f"y{n}", f"{n} YEARS", 860, 180, 1.0 if t > 0.05 else t)
    label(c, "FIRST WIN SINCE 2006", 1080, 60, WHITE, t - 0.3)

def s_asia(c, t, g):
    c.paste(TEAL_BG); spotlights(c, g, ((120, 200, 255), (255, 230, 150)))
    paste_center(c, E_GLOBE.resize((360, 360)).rotate(-g * 25 % 360, resample=Image.BICUBIC), W / 2, 950, *pop(t))
    punch(c, "aw", "ASIA WATCH", 560, 150, t, color=WHITE, stroke=8)

def s_ph(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g)
    paste_center(c, waved(FLAG_PH, g), W / 2, 780, *pop(t))
    paste_center(c, card("PHILIPPINES", "BEA MILLAN-WINDORSKI", PH_BLUE, w=920, h=430), W / 2, 1150, *pop(t - 0.15))

def s_podium(c, t, g):
    c.paste(PURP_BG); spotlights(c, g)
    paste_center(c, podium(t), W / 2, 960, alpha=ease(t / 0.1))
    punch(c, "3ru", "3RD RUNNER-UP", 480, 120, t - 0.15, color=GOLD, stroke=7)

def s_five(c, t, g):
    c.paste(gradient((10, 40, 120), (2, 4, 14)))
    for i in range(5):
        x = 140 + i * 200
        if i < 4:
            paste_center(c, CROWN_S, x, 880, *pop(t - i * 0.12))
        else:
            a = 0.35 + 0.35 * (math.sin(g * 8) + 1) / 2
            paste_center(c, CROWN_GREY, x, 880, scale=1.0, alpha=a)
            if t > 0.6:
                paste_center(c, T("q5", "?", 130, fill=WHITE, stroke=6), x, 880, *pop(t - 0.6))
    label(c, "1969 · 1973 · 2015 · 2018", 1050, 52, WHITE, t - 0.3)
    punch(c, "so5", "SO CLOSE", 560, 160, t - 0.1, color=GOLD, stroke=8)

def s_rookie(c, t, g):
    c.paste(gradient((30, 30, 40), (4, 4, 6))); runway(c, g); flashes(c, g, 9)
    punch(c, "rk", "ROOKIE", 640, 150, t, color=WHITE, stroke=7)
    if t > 0.5:
        punch(c, "arr", "↓", 830, 140, t - 0.5, color=GOLD, stroke=0)
    if t > 0.8:
        punch(c, "qn", "QUEEN", 1020, 170, t - 0.8, color=GOLD, stroke=8)

def s_ate(c, t, g):
    c.paste(RED_BG); sparkles(c, g, seed=13)
    paste_center(c, E_FIRE.resize((300, 300)), W / 2, 820, *pop(t))
    if t > 0.15:
        paste_center(c, stamp("SHE ATE", 140, GOLD, -6), W / 2, 1170, *pop(t - 0.15))

def s_q(c, t, g):
    c.paste(PURP_BG); spotlights(c, g); stage(c, g)
    paste_center(c, CROWN, W / 2, 960, scale=0.7 + 0.02 * math.sin(g * 3))
    paste_center(c, E_THINK.resize((220, 220)), W / 2 + 300, 720, *pop(t - 0.15))
    punch(c, "rq", "RIGHT QUEEN?", 560, 140, t, color=WHITE, stroke=7)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun21", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 2), ST[1], at(1, 3), ST[2], at(2, 3), at(2, 5), ST[3], at(3, 2), ST[4], at(4, 2), ST[5], at(5, 2),
     at(5, 4), at(5, 6), ST[6], at(6, 4), ST[7], ST[8], DUR + 0.1]
FNS = [s_hook, s_firstmom, punch_in(s_runway), s_cal, s_pr, s_date, s_home, s_rules, s_check, s_six, s_twenty,
       s_asia, s_ph, s_podium, s_five, s_rookie, s_ate, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (0.1, ST[1] - 0.1, "c1", "MISS UNIVERSE: 1ST MOM WINS", None),
    (ST[1] + 0.05, ST[2] - 0.1, "c2", "1ST RUNWAY: FEB 2026", None),
    (ST[3] + 0.1, ST[4] - 0.1, "c3", "MOMS ALLOWED SINCE 2023", None),
    (at(5, 4), ST[6] - 0.1, "c4", "PHILIPPINES: 3RD RUNNER-UP", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s021_{s}.png")
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
