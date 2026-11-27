"""Live Lore Short 023 (Thanksgiving 2026 US box office: Focker In-Law, the 4th Meet the Parents film with Ben Stiller,
Robert De Niro and Ariana Grande, made ~$5.3M on Wednesday Nov 25 on a reported $90M budget; Disney's original witch
film Hexed made ~$7.6M; both tracking below forecasts while the Hunger Games prequel made ~$15M Wednesday in week 2).
Reuses render.py. Usage: python3 render023.py OUT.mp4 [start end]  |  python3 render023.py stills t1 t2 ...
All visuals drawn in code (marquee, tickets, generic silhouettes, witch hat, bar charts, counters, calendars, emoji,
titles/names as plain text; no posters, footage, stills, logos or celebrity likenesses).
Music: none (strategy.md music test: 23 mod 4 is 3).
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
SEG = json.load(open("segments023.json"))
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



# ---------- Short 023 art ----------
MAROON_BG = gradient((90, 14, 20), (10, 2, 3))
NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
NIGHT_BG = gradient((24, 16, 60), (3, 2, 10))
GREEN_BG = gradient((12, 70, 40), (2, 8, 4))
GOLD_BG = gradient((100, 66, 10), (10, 6, 2))
SLATE_BG = gradient((40, 44, 60), (6, 6, 10))
TEAL_BG = gradient((10, 60, 90), (2, 6, 12))
ORANGE_BG = gradient((130, 60, 10), (14, 6, 2))
E_TURKEY, E_POPCORN, E_TICKET, E_MONEY, E_DOWN, E_TROPHY, E_MOON, E_CAL, E_ARROWDN = (emoji(ch, 150) for ch in
    ["🦃", "🍿", "🎬", "💸", "📉", "🏆", "🌙", "📅", "⬇️"])

def marquee(c, g, text, sub, y=560):
    d = ImageDraw.Draw(c)
    x0, x1, h = 90, W - 90, 380
    d.rounded_rectangle([x0, y, x1, y + h], 30, fill=(250, 240, 210, 255), outline=GOLD + (255,), width=14)
    n = 22
    for k in range(n):
        for (yy) in (y - 26, y + h + 26):
            x = x0 + 20 + k * (x1 - x0 - 40) / (n - 1)
            on = (k + int(g * 8)) % 3 != 0
            d.ellipse([x - 13, yy - 13, x + 13, yy + 13], fill=((255, 230, 140, 255) if on else (90, 70, 40, 255)))
    for i, line in enumerate((text, sub)):
        im = T(("mq", line), line, 96 if i == 0 else 70, fill=(RED if i == 0 else DARK))
        while im.width > x1 - x0 - 60:
            im = im.resize((int(im.width * 0.92), int(im.height * 0.92)))
        paste_center(c, im, W / 2, y + 120 + i * 140)
    d.rectangle([W / 2 - 30, y + h + 40, W / 2 + 30, 1330], fill=(40, 30, 30, 255))

def ticket(text, col, w=430, h=230):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 24, fill=col + (255,))
    for y in (h // 2,):
        d.ellipse([-30, y - 30, 30, y + 30], fill=(0, 0, 0, 0))
        d.ellipse([w - 30, y - 30, w + 30, y + 30], fill=(0, 0, 0, 0))
    for k in range(8):
        d.rectangle([w - 110, 20 + k * 25, w - 104, 32 + k * 25], fill=(255, 255, 255, 140))
    tx = r.text_img(text, 56, fill=WHITE, weight="Black")
    if tx.width > w - 150:
        tx = tx.resize((w - 150, int(tx.height * (w - 150) / tx.width)))
    im.alpha_composite(tx, (30, (h - tx.height) // 2))
    return im

def counter(c, t, val, cy, size, col=GOLD, d=1.0, dec=1):
    v = val * ease(t / d)
    txt = f"${v:.{dec}f}M"
    paste_center(c, T(("ct", txt, size, col), txt, size, fill=col, stroke=8), W / 2, cy)

def bars(c, t, items, top=560, bottom=1300, maxv=None, hl=None):
    d = ImageDraw.Draw(c)
    maxv = maxv or max(v for _, v, _ in items)
    n = len(items)
    bw = 220 if n <= 3 else 180
    gap = (W - n * bw) / (n + 1)
    for i, (lab, v, col) in enumerate(items):
        x = gap + i * (bw + gap)
        hh = (bottom - top - 120) * (v / maxv) * ease((t - i * 0.12) / 0.5)
        d.rounded_rectangle([x, bottom - hh, x + bw, bottom], 18, fill=col + (255,))
        vt = f"${v:g}M"
        paste_center(c, T(("bv", vt), vt, 64, fill=WHITE, stroke=6), x + bw / 2, bottom - hh - 50, alpha=ease((t - i * 0.12 - 0.3) / 0.2))
        lt = T(("bl", lab), lab, 40, fill=WHITE, weight="ExtraBold")
        if lt.width > bw + gap - 10:
            lt = lt.resize((int(bw + gap - 10), int(lt.height * (bw + gap - 10) / lt.width)))
        paste_center(c, lt, x + bw / 2, bottom + 40)

def witch_hat(w=520, col=(40, 20, 70)):
    h = int(w * 1.05)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w * 0.5 + 40, 10), (w * 0.22, h * 0.8), (w * 0.78, h * 0.8)], fill=col + (255,))
    d.ellipse([0, h * 0.72, w, h * 0.96], fill=col + (255,))
    d.rectangle([w * 0.25, h * 0.66, w * 0.75, h * 0.76], fill=GOLD + (255,))
    return im


def person(col, h=420):
    w = int(h * 0.55)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hr = w * 0.22
    d.ellipse([w / 2 - hr, 6, w / 2 + hr, 6 + 2 * hr], fill=col + (255,))
    d.rounded_rectangle([w * 0.08, h * 0.36, w * 0.92, h], int(w * 0.2), fill=col + (255,))
    return im

def sparkle(c, g, seed=3, n=30, col=(255, 230, 160)):
    d = ImageDraw.Draw(c)
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(450, 1330)
        a = int(200 * (0.5 + 0.5 * math.sin(g * rnd.uniform(2, 5) + rnd.uniform(0, 6))))
        s = rnd.uniform(4, 10)
        d.ellipse([x - s, y - s, x + s, y + s], fill=col + (a,))

def glow(im, r_=24):
    g = Image.new("RGBA", (im.width + 4 * r_, im.height + 4 * r_), (0, 0, 0, 0))
    g.alpha_composite(im, (2 * r_, 2 * r_))
    out = g.filter(ImageFilter.GaussianBlur(r_))
    out.alpha_composite(g)
    return out
HAT = glow(witch_hat(), 16)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(MAROON_BG); sparkle(c, g, 1, 20)
    marquee(c, g, "WHO WON", "THANKSGIVING?")
    paste_center(c, E_TURKEY.resize((230, 230)), W / 2 + 330, 1120, *pop(t - 0.1))
    paste_center(c, E_POPCORN.resize((200, 200)), W / 2 - 330, 1140, *pop(t - 0.2))

def s_beat(c, t, g):
    c.paste(SLATE_BG)
    paste_center(c, ticket("ARIANA GRANDE", (200, 70, 140)), W / 2, 700, *pop(t))
    paste_center(c, ticket("DISNEY", (70, 90, 200)), W / 2, 1000, *pop(t - 0.12))
    if t > 0.3:
        paste_center(c, stamp("BEAT", 150, RED, -10), W / 2, 850, *pop(t - 0.3))

def s_notnew(c, t, g):
    c.paste(GOLD_BG); sparkle(c, g, 5, 40)
    paste_center(c, glow(E_TROPHY.resize((380, 380)), 20), W / 2, 980, *pop(t))
    paste_center(c, pill("WINNER: A WEEK-2 MOVIE", 56, GOLD), W / 2, 600, *pop(t, 0.2))

def s_focker(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, card("THE 4TH MEET THE PARENTS FILM", "FOCKER IN-LAW", (200, 70, 60)), W / 2, 880, *pop(t))

def s_cast(c, t, g):
    c.paste(gradient((60, 30, 70), (6, 3, 8))); spotlights(c, g)
    for i, (n, col) in enumerate((("BEN STILLER", (230, 230, 240)), ("ROBERT DE NIRO", (230, 230, 240)),
                                  ("+ ARIANA GRANDE", GOLD))):
        paste_center(c, pill(n, 78, col), W / 2 + (1 - ease((t - i * 0.12) / 0.3)) * 700, 650 + i * 200)
    label(c, "STARRING", 520, 56, WHITE, t)
    paste_center(c, person((25, 20, 35), 300), 230, 1240, alpha=0.9)
    paste_center(c, person((25, 20, 35), 330), W - 230, 1230, alpha=0.9)

def s_53(c, t, g):
    c.paste(MAROON_BG)
    paste_center(c, E_TICKET.resize((260, 260)), W / 2, 660, *pop(t))
    counter(c, t, 5.3, 960, 230, WHITE, 0.8)
    label(c, "OPENING DAY · WED NOV 25", 1180, 58, GOLD, t - 0.2)

def s_budget(c, t, g):
    c.paste(GREEN_BG)
    bars(c, t, [("BUDGET (REP.)", 90, (70, 190, 90)), ("DAY 1", 5.3, (215, 45, 45))])
    punch(c, "b90", "$90M BUDGET", 470, 110, t, color=WHITE, stroke=8)

def s_hexed(c, t, g):
    c.paste(NIGHT_BG); sparkle(c, g, 9, 50, (200, 170, 255))
    paste_center(c, E_MOON.resize((180, 180)), W - 170, 760)
    paste_center(c, HAT, W / 2, 950 + 10 * math.sin(g * 2), *pop(t))
    punch(c, "hx", "HEXED", 560, 170, t - 0.1, color=(200, 170, 255), stroke=8)
    label(c, "DISNEY ANIMATION · ORIGINAL", 1290, 54, WHITE, t - 0.25)

def s_76(c, t, g):
    c.paste(gradient((50, 30, 110), (5, 3, 12))); sparkle(c, g, 11, 30, (200, 170, 255))
    paste_center(c, HAT.resize((HAT.width // 2, HAT.height // 2)), W / 2, 680, *pop(t))
    counter(c, t, 7.6, 1020, 230, GOLD, 0.8)
    label(c, "OPENING DAY", 1200, 58, WHITE, t - 0.2)

def s_forecast(c, t, g):
    c.paste(SLATE_BG)
    d = ImageDraw.Draw(c)
    pts = [(140, 700), (380, 680), (600, 760), (800, 930), (960, 1100)]
    k = ease(t / 0.8) * (len(pts) - 1)
    for i in range(len(pts) - 1):
        if k > i:
            f = min(1.0, k - i)
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            d.line([(x0, y0), (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)], fill=RED + (255,), width=22)
    d.line([(140, 620), (960, 620)], fill=(150, 160, 180, 255), width=6)
    paste_center(c, T("fcl", "FORECAST", 44, fill=(170, 180, 200), weight="Bold", spacing=4), 260, 580)
    if t > 0.4:
        paste_center(c, stamp("BELOW FORECAST", 100, RED, -6), W / 2, 1180, *pop(t - 0.4))

def s_week2(c, t, g):
    c.paste(ORANGE_BG)
    paste_center(c, calendar("WEEK", "2", (200, 90, 30)), W / 2, 900, *pop(t))
    punch(c, "hg", "HUNGER GAMES PREQUEL", 520, 64, t, color=WHITE, stroke=8)

def s_15(c, t, g):
    c.paste(GOLD_BG); sparkle(c, g, 13, 30)
    bars(c, t, [("FOCKER", 5.3, (200, 70, 60)), ("HEXED", 7.6, (150, 90, 230)), ("HUNGER GAMES", 15, GOLD)], top=600)
    punch(c, "w15", "WEDNESDAY ALONE", 480, 80, t, color=WHITE, stroke=8)

def s_w(c, t, g):
    c.paste(TEAL_BG)
    punch(c, "bn", "BIG NAMES", 560, 130, t, color=WHITE, stroke=8)
    paste_center(c, T("neq", "≠", 200, fill=GOLD, stroke=6), W / 2, 790, *pop(t - 0.15))
    punch(c, "gw", "GUARANTEED W", 1020, 96, t - 0.3, color=GOLD, stroke=8)

def s_q(c, t, g):
    left = gradient((120, 30, 30), (14, 3, 3), W // 2, H)
    right = gradient((50, 30, 110), (5, 3, 12), W - W // 2, H)
    c.paste(left, (0, 0)); c.paste(right, (W // 2, 0))
    paste_center(c, E_TICKET.resize((220, 220)), W / 4, 900, *pop(t))
    paste_center(c, HAT.resize((HAT.width // 2, HAT.height // 2)), 3 * W / 4, 900, *pop(t - 0.12))
    paste_center(c, T("qf", "FOCKER IN-LAW", 54, fill=WHITE, stroke=6), W / 4, 1180)
    paste_center(c, T("qh", "HEXED", 76, fill=WHITE, stroke=6), 3 * W / 4, 1180)
    punch(c, "or", "OR", 640, 200, t - 0.2, color=GOLD, stroke=10)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun23", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def calendar(month, big, col=RED):
    cw, ch = 560, 560
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 150], 36, fill=col + (255,))
    dd.rectangle([0, 110, cw, 150], fill=col + (255,))
    sm = r.text_img(month, 80, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 30))
    bg_ = r.text_img(big, 260, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 200))
    return cd

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 3), ST[1], ST[2], at(2, 4), at(2, 7), ST[3], ST[4], at(4, 5), at(4, 7), ST[5], at(5, 4),
     ST[6], ST[7], ST[8], DUR + 0.1]
FNS = [s_hook, s_beat, punch_in(s_notnew), s_focker, s_cast, s_53, s_budget, s_hexed, s_76, s_forecast,
       s_week2, s_15, s_w, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (0.1, ST[1] - 0.1, "c1", "THANKSGIVING BOX OFFICE", None),
    (at(2, 7) + 0.05, ST[3] - 0.1, "c2", "FOCKER IN-LAW: ~$5.3M DAY 1", None),
    (at(4, 5) + 0.05, at(4, 7) - 0.05, "c3", "HEXED: ~$7.6M DAY 1", None),
    (at(5, 4) + 0.05, ST[6] - 0.1, "c4", "WEEK-2 WINNER: $15M WED", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s023_{s}.png")
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
