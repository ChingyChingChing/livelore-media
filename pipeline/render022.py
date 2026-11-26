"""Live Lore Short 022 (K-pop's AI/virtual debut week, Nov 2026: fully AI-generated five-member boy group H3ARUS
debuts with "CRUSH"; HYBE's NEWEPICBASE + four North American VTubers (AmaLee, Dokibird, ironmouse, Rin Penrose) launch
The Wildcard Club, "Click Flick" MV passed 1M YouTube views in 3 days; virtual boy band WINKX debuts Nov 27 with "HALO";
AI boy group muuo:23's October pre-debut single drew "AI slop" backlash) - reuses render.py.
Usage: python3 render022.py OUT.mp4 [start end]  |  python3 render022.py stills t1 t2 ...
All visuals drawn in code (generic drawn idol silhouettes, wireframes, code rain, playing card, screens, counters,
calendars, chat bubbles, emoji, names as plain text; no photos, avatars, MV footage, logos or album art).
Music: original lofi from music.py (strategy.md music test: Short 22 = 22 mod 4 is 2).
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
SEG = json.load(open("segments022.json"))
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
NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
PURP_BG = gradient((60, 20, 100), (6, 3, 14))
CODE_BG = gradient((4, 30, 22), (1, 4, 3))
RED_BG = gradient((110, 20, 24), (12, 2, 3))
TEAL_BG = gradient((10, 60, 90), (2, 6, 12))
PINK_BG = gradient((120, 30, 90), (14, 3, 10))
GOLD_BG = gradient((90, 60, 10), (10, 6, 2))
SLATE_BG = gradient((40, 44, 60), (6, 6, 10))
PINK, MINT = (255, 90, 170), (80, 255, 170)
E_ROBOT, E_PLAY, E_THUMB, E_HOUR, E_CARD, E_HEADSET, E_SPEECH = (emoji(ch, 150) for ch in
    ["🤖", "▶️", "👎", "⏳", "🃏", "🎧", "💬"])

def idol(col, h=520, alpha=255, wire=False):
    """Generic drawn idol silhouette (head, shoulders, body, mic-less pose)."""
    w = int(h * 0.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (alpha,)
    hr = w * 0.2
    if wire:
        lw = max(3, h // 90)
        d.ellipse([w / 2 - hr, 10, w / 2 + hr, 10 + 2 * hr], outline=c, width=lw)
        d.polygon([(w * 0.12, h * 0.36), (w * 0.88, h * 0.36), (w * 0.72, h * 0.98), (w * 0.28, h * 0.98)], outline=c, width=lw)
        for k in range(1, 6):
            y = h * 0.36 + k * h * 0.1
            d.line([(w * 0.14 + k * 4, y), (w * 0.86 - k * 4, y)], fill=col + (alpha // 2,), width=2)
        d.line([(w / 2, h * 0.36), (w / 2, h * 0.98)], fill=col + (alpha // 2,), width=2)
    else:
        d.ellipse([w / 2 - hr, 10, w / 2 + hr, 10 + 2 * hr], fill=c)
        d.rounded_rectangle([w * 0.12, h * 0.33, w * 0.88, h * 0.98], int(w * 0.18), fill=c)
    return im

def glow(im, r_=24):
    g = Image.new("RGBA", (im.width + 2 * r_ * 2, im.height + 2 * r_ * 2), (0, 0, 0, 0))
    g.alpha_composite(im, (r_ * 2, r_ * 2))
    out = g.filter(ImageFilter.GaussianBlur(r_))
    out.alpha_composite(g)
    return out

IDOL_D = idol((25, 25, 35), 560)
IDOL_W = glow(idol(CYAN, 560, wire=True), 16)
IDOL_M = glow(idol(MINT, 420, wire=True), 14)
IDOL_P = glow(idol(PINK, 420, wire=True), 14)

GLYPHS = "01アイコード<>/{}#"
def code_rain(c, g, col=MINT, seed=7, n=26):
    d = ImageDraw.Draw(c)
    f = r.font(34, "Bold")
    rnd = random.Random(seed)
    for i in range(n):
        x = 20 + i * (W - 40) / n
        sp = rnd.uniform(160, 420)
        off = rnd.uniform(0, H)
        y0 = (off + g * sp) % (H + 600) - 600
        for k in range(12):
            a = int(220 * (1 - k / 12))
            ch = GLYPHS[(i * 7 + k * 3 + int(g * 8)) % len(GLYPHS)]
            d.text((x, y0 - k * 42), ch, font=f, fill=col + (a,))

def glitch(c, g, strength=1.0):
    rnd = random.Random(int(g * 20))
    if rnd.random() > 0.55 * strength:
        return
    for _ in range(3):
        y = rnd.randint(300, 1350)
        h = rnd.randint(10, 50)
        dx = rnd.randint(-60, 60)
        band = c.crop((0, y, W, y + h))
        c.paste(band, (dx, y))

def spot_stage(c, g):
    d = ImageDraw.Draw(c)
    d.ellipse([-200, 1180, W + 200, 1560], fill=(30, 20, 50, 255))
    d.ellipse([-100, 1210, W + 100, 1500], fill=(55, 40, 90, 255))

def screen(w, h, col, inner=None):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 28, fill=(20, 22, 30, 255), outline=col + (255,), width=8)
    if inner is not None:
        paste_center(im, inner, w / 2, h / 2 + 10)
    return im

def wildcard(w=520):
    h = int(w * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 36, fill=(250, 246, 238, 255), outline=GOLD + (255,), width=10)
    d.rounded_rectangle([40, 40, w - 40, h - 40], 24, outline=PURPLE + (255,), width=6)
    star(d, w / 2, h / 2 - 40, w * 0.26, w * 0.11, PURPLE + (255,))
    tx = r.text_img("WILD", 96, fill=DARK)
    im.alpha_composite(tx, ((w - tx.width) // 2, int(h * 0.66)))
    for (x, y) in ((70, 60), (w - 110, h - 130)):
        d.text((x, y), "W", font=r.font(70), fill=PURPLE + (255,))
    return im

def star(d, cx, cy, ro, ri, col, rot=-90):
    pts = []
    for k in range(10):
        rr = ro if k % 2 == 0 else ri
        a = math.radians(rot + k * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)

def calendar(month, big, col=RED):
    cw, ch = 560, 560
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 150], 36, fill=col + (255,))
    dd.rectangle([0, 110, cw, 150], fill=col + (255,))
    sm = r.text_img(month, 80, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 30))
    bg_ = r.text_img(big, 230 if len(big) <= 2 else 150, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 220 if len(big) <= 2 else 270))
    return cd

def bubble(text, col, w=760):
    tx = r.text_img(text, 62, fill=DARK, weight="ExtraBold")
    h = tx.height + 70
    w = max(w, tx.width + 80) if tx.width + 80 <= 1000 else 1000
    im = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 34, fill=col + (255,))
    d.polygon([(60, h - 2), (130, h - 2), (70, h + 38)], fill=col + (255,))
    im.alpha_composite(tx, (40, 32))
    return im

def halo_ring(w=200, col=GOLD):
    im = Image.new("RGBA", (w, w // 3), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([4, 4, w - 4, w // 3 - 4], outline=col + (255,), width=12)
    return glow(im, 10)

def big_num(c, key, text, cy, size, t, col=GOLD):
    punch(c, key, text, cy, size, t, color=col, stroke=8)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(PURP_BG); spotlights(c, g); spot_stage(c, g)
    for i, x in enumerate((W / 2 - 300, W / 2, W / 2 + 300)):
        paste_center(c, IDOL_W, x, 1000 + (40 if i != 1 else 0), scale=0.75 if i != 1 else 0.9, alpha=ease((t - i * 0.08) / 0.15))
    punch(c, "hk", "NEW K-POP DEBUTS", 520, 92, t, color=WHITE, stroke=8)

def s_nothuman(c, t, g):
    c.paste(CODE_BG); code_rain(c, g)
    paste_center(c, E_ROBOT.resize((360, 360)), W / 2, 1000, *pop(t))
    if t > 0.15:
        paste_center(c, stamp("NOT HUMAN", 130, RED, -7), W / 2, 640, *pop(t - 0.15))
    glitch(c, g)

def s_emptymic(c, t, g):
    c.paste(gradient((20, 20, 30), (2, 2, 4))); spotlights(c, g, ((255, 240, 200),)); spot_stage(c, g)
    d = ImageDraw.Draw(c)
    d.line([(W / 2, 760), (W / 2, 1280)], fill=(150, 150, 160, 255), width=14)
    d.line([(W / 2 - 120, 1290), (W / 2 + 120, 1290)], fill=(150, 150, 160, 255), width=14)
    d.rounded_rectangle([W / 2 - 40, 650, W / 2 + 40, 790], 36, fill=(60, 60, 70, 255))
    punch(c, "nob", "NO ONE THERE?", 520, 120, t, color=WHITE, stroke=8)

def s_zero(c, t, g):
    c.paste(RED_BG); code_rain(c, g, (255, 120, 120), seed=3, n=18)
    big_num(c, "z0", "0 HUMANS", 820, 150, t, WHITE)
    label(c, "BEHIND THE MIC", 1060, 64, GOLD, t - 0.25)

def s_five(c, t, g):
    c.paste(CODE_BG); code_rain(c, g, seed=11, n=14)
    for i in range(5):
        x = 140 + i * 200
        paste_center(c, IDOL_M, x, 1000 + (i % 2) * 40, scale=0.62, alpha=ease((t - i * 0.08) / 0.2))
    punch(c, "5m", "5 MEMBERS", 520, 160, t, color=GOLD, stroke=8)

def s_ai(c, t, g):
    c.paste(SLATE_BG)
    chip = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    d.rounded_rectangle([70, 70, 450, 450], 40, fill=(30, 34, 46, 255), outline=MINT + (255,), width=10)
    for k in range(5):
        p = 110 + k * 75
        for (a, b, c2, d2) in ((p, 10, p, 70), (p, 450, p, 510), (10, p, 70, p), (450, p, 510, p)):
            d.line([(a, b), (c2, d2)], fill=MINT + (255,), width=10)
    tx = r.text_img("AI", 170, fill=MINT)
    chip.alpha_composite(tx, ((520 - tx.width) // 2, (520 - tx.height) // 2 - 10))
    paste_center(c, glow(chip, 14), W / 2, 900, *pop(t))
    punch(c, "100", "100% AI", 480, 150, t - 0.1, color=WHITE, stroke=8)

def s_crush(c, t, g):
    c.paste(PINK_BG); sparkles = random.Random(5)
    d = ImageDraw.Draw(c)
    cx, cy, R = W / 2, 900, 330
    rot = g * 90
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(18, 18, 22, 255))
    for k in range(6):
        rr = R - 30 - k * 40
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(45, 45, 55, 255), width=3)
    d.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=PINK + (255,))
    a = math.radians(rot)
    d.ellipse([cx + 70 * math.cos(a) - 14, cy + 70 * math.sin(a) - 14, cx + 70 * math.cos(a) + 14, cy + 70 * math.sin(a) + 14], fill=WHITE + (255,))
    punch(c, "cr", "“CRUSH”", 460, 150, t, color=WHITE, stroke=8)
    label(c, "H3ARUS · DEBUT SINGLE", 1310, 60, GOLD, t - 0.2)

def s_hybe(c, t, g):
    c.paste(NAVY_BG)
    d = ImageDraw.Draw(c)
    bw = 520
    top = 1300 - 700 * ease(t / 0.4)
    d.rectangle([W / 2 - bw / 2, top, W / 2 + bw / 2, 1300], fill=(40, 46, 70, 255))
    for row in range(int((1300 - top) // 70)):
        for col_ in range(5):
            on = (row * 5 + col_ + int(g * 3)) % 4 != 0
            x = W / 2 - bw / 2 + 40 + col_ * 92
            y = 1300 - 60 - row * 70
            d.rectangle([x, y, x + 56, y + 40], fill=((255, 220, 140, 255) if on else (25, 28, 44, 255)))
    punch(c, "hy", "HYBE", 470, 200, t, color=WHITE, stroke=8)

def s_bts(c, t, g):
    c.paste(PURP_BG); spotlights(c, g)
    paste_center(c, card("THE COMPANY BEHIND", "BTS", PURPLE), W / 2, 920, *pop(t))

def s_vtubers(c, t, g):
    c.paste(TEAL_BG)
    cols = (PINK, CYAN, GOLD, MINT)
    for i in range(4):
        x = 290 + (i % 2) * 500
        y = 760 + (i // 2) * 470
        inner = idol(cols[i], 300, wire=True)
        paste_center(c, screen(420, 400, cols[i], inner), x, y, *pop(t - i * 0.1))
    punch(c, "4v", "4 VTUBERS", 420, 150, t, color=WHITE, stroke=8)

def s_names(c, t, g):
    c.paste(gradient((20, 50, 80), (2, 6, 12)))
    names = ["AMALEE", "DOKIBIRD", "IRONMOUSE", "RIN PENROSE"]
    for i, n in enumerate(names):
        y = 640 + i * 170
        hl = n == "IRONMOUSE"
        p = pill(n, 80, GOLD if hl else (230, 230, 240))
        paste_center(c, p, W / 2 + (1 - ease((t - i * 0.1) / 0.3)) * 600, y)
    label(c, "NORTH AMERICAN VTUBERS", 1300, 56, WHITE, t - 0.3)

def s_wildcard(c, t, g):
    c.paste(PURP_BG); spotlights(c, g, ((255, 230, 150), (200, 120, 255)))
    flip = ease(t / 0.4)
    wc = wildcard()
    sx = max(0.05, abs(math.cos(math.pi * (1 - flip))))
    wc2 = wc.resize((max(4, int(wc.width * sx)), wc.height))
    paste_center(c, glow(wc2, 12), W / 2, 920, scale=0.85, alpha=1.0)
    punch(c, "wc", "THE WILDCARD CLUB", 420, 86, t - 0.2, color=WHITE, stroke=8)

def s_mocap(c, t, g):
    c.paste(SLATE_BG)
    paste_center(c, idol((150, 150, 175), 560).resize((300, 600)), 280, 950, *pop(t))
    paste_center(c, IDOL_P, 800, 950, *pop(t - 0.35))
    if t > 0.2:
        punch(c, "arr2", "→", 950, 150, t - 0.2, color=GOLD, stroke=0)
    label(c, "REAL PEOPLE", 1300, 56, WHITE, t - 0.1)
    punch(c, "av", "AVATARS", 480, 150, t - 0.35, color=PINK, stroke=8)

def s_views(c, t, g):
    c.paste(RED_BG)
    paste_center(c, screen(800, 460, WHITE, E_PLAY.resize((200, 200))), W / 2, 760, *pop(t))
    n = int(1_000_000 * ease(t / 1.2))
    txt = f"{n:,}"
    paste_center(c, T(("vc", txt), txt, 140, fill=GOLD, stroke=8), W / 2, 1150)
    label(c, "YOUTUBE VIEWS · “CLICK FLICK”", 1290, 52, WHITE, t - 0.2)

def s_3days(c, t, g):
    c.paste(GOLD_BG)
    for i in range(3):
        paste_center(c, calendar("DAY", str(i + 1), (200, 60, 60)).resize((300, 300)), 220 + i * 320, 900, *pop(t - i * 0.15))
    big_num(c, "3d", "3 DAYS", 520, 170, t, WHITE)

def s_friday(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, calendar("FRI · NOV", "27", PURPLE), W / 2, 880, *pop(t))
    label(c, "VIRTUAL BOY BAND DEBUT", 1260, 56, WHITE, t - 0.2)

def s_halo(c, t, g):
    c.paste(gradient((30, 20, 70), (3, 2, 8))); spotlights(c, g, ((255, 240, 200),))
    hr = halo_ring(200)
    for i in range(4):
        x = 180 + i * 240
        y = 1020 + (i % 2) * 30
        paste_center(c, IDOL_W, x, y, scale=0.52, alpha=ease((t - i * 0.08) / 0.2))
        paste_center(c, hr, x, y - 190 + 8 * math.sin(g * 3 + i), alpha=ease((t - 0.2 - i * 0.08) / 0.2))
    punch(c, "hl", "“HALO”", 470, 170, t, color=GOLD, stroke=8)
    label(c, "WINKX · 4 MEMBERS", 1310, 58, WHITE, t - 0.3)

def s_vibing(c, t, g):
    c.paste(gradient((40, 30, 30), (6, 4, 4)))
    paste_center(c, E_THUMB.resize((340, 340)), W / 2, 900, *pop(t))
    punch(c, "nv", "NOT EVERYONE", 480, 110, t, color=WHITE, stroke=8)

def s_oct(c, t, g):
    c.paste(SLATE_BG); code_rain(c, g, (150, 160, 200), seed=21, n=12)
    paste_center(c, calendar("2026", "OCT", (90, 110, 170)), W / 2 - 220, 900, scale=0.7, alpha=ease(t / 0.15))
    paste_center(c, IDOL_M, W / 2 + 230, 920, *pop(t - 0.2))
    punch(c, "pd", "ANOTHER AI GROUP", 480, 88, t, color=WHITE, stroke=8)
    label(c, "PRE-DEBUT SINGLE", 1270, 60, GOLD, t - 0.3)
    if t > 2.3:
        c.paste(gradient((60, 50, 110), (6, 5, 14))); code_rain(c, g, (150, 160, 200), seed=22, n=12)
        paste_center(c, pill("PRE-DEBUT SINGLE", 90, GOLD), W / 2, 900, *pop(t - 2.3))
        punch(c, "oc", "OCTOBER", 560, 150, t - 2.3, color=WHITE, stroke=8)

def s_slop(c, t, g):
    c.paste(gradient((50, 20, 30), (6, 2, 4)))
    msgs = [("“AI slop”", (250, 246, 238)), ("what about real trainees?", (210, 230, 255))]
    for i, (m, col) in enumerate(msgs):
        if t > i * 0.3:
            paste_center(c, bubble(m, col), W / 2 + (i % 2) * 30 - 15, 650 + i * 230, *pop(t - i * 0.3))
    label(c, "SOME FANS REACTED", 1330, 56, GOLD, t - 0.1)
    glitch(c, g, 0.5)

def s_trainees(c, t, g):
    c.paste(NAVY_BG)
    d = ImageDraw.Draw(c)
    rnd = random.Random(4)
    n = int(260 * ease(t / 1.0))
    for i in range(n):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(700, 1330)
        d.ellipse([x - 9, y - 22, x + 9, y - 4], fill=(170, 180, 210, 255))
        d.rounded_rectangle([x - 14, y - 2, x + 14, y + 30], 8, fill=(120, 130, 170, 255))
    paste_center(c, E_HOUR.resize((200, 200)), W / 2, 560, scale=1.0, alpha=1.0)
    punch(c, "tw", "THOUSANDS WAITING", 380, 84, t, color=WHITE, stroke=8)

def s_vs(c, t, g):
    left = gradient((120, 40, 90), (14, 4, 10), W // 2, H)
    right = gradient((10, 70, 50), (1, 8, 6), W - W // 2, H)
    c.paste(left, (0, 0)); c.paste(right, (W // 2, 0))
    code_rain(c, g, seed=31, n=10)
    c.paste(left.crop((0, 0, W // 2, H)), (0, 0))
    paste_center(c, IDOL_P, W / 4, 950, *pop(t))
    paste_center(c, IDOL_M, 3 * W / 4, 950, *pop(t - 0.15))
    d = ImageDraw.Draw(c)
    paste_center(c, T("hum", "HUMANS", 76, fill=WHITE, stroke=6), W / 4, 1260)
    paste_center(c, T("cod", "CODE", 76, fill=WHITE, stroke=6), 3 * W / 4, 1260)
    punch(c, "vs", "VS", 600, 220, t - 0.2, color=GOLD, stroke=10)

def s_q(c, t, g):
    c.paste(PURP_BG); spotlights(c, g); spot_stage(c, g)
    paste_center(c, IDOL_W, W / 2, 1000, scale=0.85 + 0.02 * math.sin(g * 3))
    paste_center(c, E_THINK.resize((220, 220)), W / 2 + 300, 720, *pop(t - 0.15))
    punch(c, "stan", "WOULD YOU STAN?", 480, 96, t, color=WHITE, stroke=8)
    glitch(c, g, 0.4)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun22", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 2), ST[1], at(1, 3), ST[2], at(2, 3), at(2, 5), ST[3], at(3, 2), at(3, 4), at(3, 7), at(3, 9),
     ST[4], at(4, 3), at(4, 6), ST[5], at(5, 3), ST[6], at(6, 2), at(6, 7), at(6, 10), ST[7], ST[8], ST[9], DUR + 0.1]
FNS = [s_hook, s_nothuman, s_emptymic, punch_in(s_zero), s_five, s_ai, s_crush, s_hybe, s_bts, s_vtubers, s_names,
       s_wildcard, s_mocap, s_views, s_3days, s_friday, s_halo, s_vibing, s_oct, s_slop, s_trainees, s_vs, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (0.1, ST[1] - 0.1, "c1", "K-POP'S AI DEBUT WEEK", None),
    (ST[2] + 0.05, ST[3] - 0.1, "c2", "H3ARUS: 100% AI-MADE", None),
    (at(4, 3), ST[5] - 0.1, "c3", "1M VIEWS IN 3 DAYS", None),
    (ST[5] + 0.05, ST[6] - 0.1, "c4", "WINKX DEBUT: FRI NOV 27", None),
    (at(6, 7), at(6, 10) - 0.05, "c5", "FANS: “AI SLOP”", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s022_{s}.png")
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
