"""Live Lore Short 024 (Avengers: Doomsday, Dec 18 2026: US presales past $100M about three weeks out (Deadline);
NRG's first tracking reportedly ~$270M opening, its highest initial forecast; new teaser with Ian McKellen's Magneto trying
to pull off Doom's mask; Dune: Part Three opens the same day with US IMAX; opening record Spider-Man: Brand New Day ~$360M,
Endgame $357M).
Reuses render.py. Usage: python3 render024.py OUT.mp4 [start end]  |  python3 render024.py stills t1 t2 ...
All visuals drawn in code (tickets, counters, charts, a generic metal mask, sand dunes, calendars, a cinema screen, emoji,
titles/names as plain text; no posters, footage, stills, logos or character/celebrity likenesses).
Music: none (strategy.md music test: 24 mod 4 is 0).
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
SEG = json.load(open("segments024.json"))
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

# ---------- Short 024 art ----------
STEEL_BG = gradient((40, 48, 60), (5, 6, 9))
DOOM_BG = gradient((10, 60, 30), (2, 6, 3))
RED_BG = gradient((110, 16, 20), (10, 2, 3))
NAVY_BG = gradient((16, 18, 46), (3, 3, 10))
GOLD_BG = gradient((100, 66, 10), (10, 6, 2))
SAND_BG = gradient((200, 140, 70), (60, 30, 10))
PURPLE_BG = gradient((60, 26, 100), (5, 3, 12))
TEAL_BG = gradient((10, 60, 90), (2, 6, 12))
DGREEN = (60, 255, 120)
E_TICKET, E_POPCORN, E_MONEY, E_CHART, E_TROPHY, E_MAGNET, E_WARN, E_FILM, E_SPIDER, E_BOLT, E_CAL, E_EYES2 = (
    emoji(ch, 150) for ch in ["🎫", "🍿", "💸", "📈", "🏆", "🧲", "⚠️", "🎬", "🕷️", "⚡", "📅", "👀"])

def mask(w=460, glow_eyes=True):
    """Generic metal face mask (simple shapes; not any character's design)."""
    h = int(w * 1.25)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], int(w * 0.42), fill=(150, 158, 170, 255))
    d.rounded_rectangle([w * 0.06, h * 0.04, w * 0.94, h * 0.6], int(w * 0.36), fill=(175, 183, 195, 255))
    eye = (DGREEN + (255,)) if glow_eyes else (20, 22, 26, 255)
    for x0 in (0.17, 0.57):
        d.rounded_rectangle([w * x0, h * 0.34, w * (x0 + 0.26), h * 0.42], 12, fill=eye)
    for k in range(5):
        x = w * (0.3 + k * 0.1)
        d.rectangle([x - 6, h * 0.66, x + 6, h * 0.86], fill=(60, 64, 72, 255))
    d.line([(w * 0.5, h * 0.44), (w * 0.5, h * 0.6)], fill=(110, 116, 128, 255), width=10)
    return im
MASK = glow(mask(), 18)

def dunes(c, g, base=1150):
    d = ImageDraw.Draw(c)
    for k, (col, amp, off) in enumerate((((230, 170, 90), 60, 0), ((205, 140, 70), 80, 1.7), ((170, 105, 50), 70, 3.1))):
        y0 = base + k * 110
        pts = [(x, y0 + amp * math.sin(x / 260 + off + g * 0.15)) for x in range(0, W + 41, 40)]
        d.polygon(pts + [(W, H), (0, H)], fill=col + (255,))
    d.ellipse([W - 330, 300 + 0, W - 130, 500], fill=(255, 235, 190, 255))

def screen(c, t, text, col=WHITE):
    d = ImageDraw.Draw(c)
    s = 0.85 + 0.15 * ease(t / 0.3)
    w, h = int(920 * s), int(520 * s)
    x0, y0 = (W - w) // 2, 820 - h // 2
    d.rounded_rectangle([x0 - 16, y0 - 16, x0 + w + 16, y0 + h + 16], 20, fill=(20, 20, 26, 255))
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 220, 255, 255))
    paste_center(c, T(("scr", text), text, 110, fill=DARK), W / 2, 820, scale=s)
    for k in range(9):
        x = 140 + k * 100
        d.ellipse([x - 34, 1180, x + 34, 1248], fill=(10, 10, 14, 255))
        d.rectangle([x - 40, 1225, x + 40, 1320], fill=(10, 10, 14, 255))

def line_chart(c, t, pts, col=GREEN, width=22):
    d = ImageDraw.Draw(c)
    k = ease(t / 0.8) * (len(pts) - 1)
    for i in range(len(pts) - 1):
        if k > i:
            f = min(1.0, k - i)
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            d.line([(x0, y0), (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)], fill=col + (255,), width=width)
    for x in range(140, 961, 205):
        d.line([(x, 560), (x, 1290)], fill=(255, 255, 255, 30), width=2)

def counter0(c, t, val, cy, size, col=GOLD, d=1.0):
    v = int(round(val * ease(t / d)))
    txt = f"${v}M"
    paste_center(c, T(("ct0", txt, size, col), txt, size, fill=col, stroke=8), W / 2, cy)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(RED_BG); sparkle(c, g, 1, 30)
    lt = t + 0.3  # fully visible on frame 0 (mute-proof hook)
    punch(c, "ad", "AVENGERS: DOOMSDAY", 560, 80, lt, color=WHITE, stroke=8)
    punch(c, "h100", "$100M+", 860, 215, lt, color=GOLD, stroke=10)
    label(c, "IN TICKET SALES", 1040, 60, WHITE, 1.0)
    for i, (x, y, rot) in enumerate(((200, 1230, 14), (W - 200, 1240, -12), (W / 2, 1270, 4))):
        paste_center(c, E_TICKET.resize((190, 190)).rotate(rot + 10 * math.sin(g * 3 + i), expand=True), x, y, *pop(t + 0.3 - 0.1 * i))

def s_sales(c, t, g):
    c.paste(NAVY_BG)
    for i in range(6):
        y = 1250 - i * 90 * ease((t - i * 0.07) / 0.3)
        paste_center(c, ticket("ADMIT ONE", (200, 50, 60) if i % 2 else (230, 160, 30), 520, 140), W / 2 + (i % 2) * 30 - 15, y)
    paste_center(c, pill("TICKET SALES", 80, GOLD), W / 2, 560, *pop(t))

def s_3weeks(c, t, g):
    c.paste(PURPLE_BG); sparkle(c, g, 4, 40, (210, 180, 255))
    paste_center(c, calendar("WEEKS", "3", (150, 90, 230)), W / 2, 900, *pop(t))
    paste_center(c, pill("NOT EVEN OUT YET", 80, GOLD), W / 2, 520, *pop(t, 0.2))

def s_track(c, t, g):
    c.paste(STEEL_BG)
    line_chart(c, t, [(140, 1250), (345, 1150), (550, 1080), (755, 880), (960, 620)])
    paste_center(c, E_CHART.resize((200, 200)), 250, 760, *pop(t - 0.2))
    label(c, "EARLY TRACKING (REPORTED)", 500, 50, WHITE, t)

def s_270(c, t, g):
    c.paste(GOLD_BG); sparkle(c, g, 6, 40)
    counter0(c, t, 270, 850, 280, WHITE, 0.9)
    label(c, "PROJECTED US OPENING", 1080, 56, DARK, t - 0.2)

def s_highest(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, glow(E_TROPHY.resize((330, 330)), 20), W / 2, 760, *pop(t))
    punch(c, "hi", "HIGHEST FIRST", 1060, 100, t - 0.15, color=WHITE, stroke=8)
    punch(c, "fc", "FORECAST EVER", 1190, 100, t - 0.25, color=GOLD, stroke=8)

def s_rdj(c, t, g):
    c.paste(gradient((50, 40, 60), (6, 4, 8))); spotlights(c, g)
    paste_center(c, person((20, 18, 28), 520), W / 2, 1050, alpha=0.95)
    paste_center(c, pill("ROBERT DOWNEY JR.", 76, GOLD), W / 2, 560, *pop(t))
    label(c, "IS BACK", 680, 60, WHITE, t - 0.2)

def s_villain(c, t, g):
    c.paste(DOOM_BG); sparkle(c, g, 8, 40, (120, 255, 160))
    paste_center(c, MASK, W / 2, 880 + 8 * math.sin(g * 2), *pop(t))
    if t > 0.35:
        paste_center(c, stamp("VILLAIN", 130, RED, -8), W / 2, 1220, *pop(t - 0.35))

def s_teaser(c, t, g):
    c.paste(gradient((20, 20, 24), (2, 2, 4)))
    d = ImageDraw.Draw(c)
    s = 0.85 + 0.15 * ease(t / 0.3)
    w, h = int(880 * s), int(495 * s)
    x0, y0 = (W - w) // 2, 860 - h // 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 28, fill=(50, 54, 64, 255))
    d.polygon([(W / 2 - 60, 860 - 80), (W / 2 - 60, 860 + 80), (W / 2 + 90, 860)], fill=WHITE + (255,))
    d.rounded_rectangle([x0 + 40, y0 + h - 50, x0 + 40 + (w - 80) * ease(t / 2.0), y0 + h - 36], 7, fill=RED + (255,))
    punch(c, "nt", "NEW TEASER", 500, 120, t, color=GOLD, stroke=8)

def s_magnet(c, t, g):
    c.paste(gradient((60, 20, 80), (6, 2, 8)))
    pull = 40 * math.sin(g * 14) * min(1, t / 0.4)
    paste_center(c, MASK.resize((MASK.width * 3 // 4, MASK.height * 3 // 4)), W / 2 + pull * 0.3, 1000)
    paste_center(c, E_MAGNET.resize((260, 260)).rotate(-30, expand=True), W / 2 - 20, 520 + pull * 0.2, *pop(t))
    d = ImageDraw.Draw(c)
    for k in range(4):
        a = (g * 2 + k * 0.25) % 1.0
        y = 650 + a * 200
        d.arc([W / 2 - 200 * (1 - a) - 60, y - 40, W / 2 + 200 * (1 - a) + 60, y + 40], 0, 180, fill=(200, 160, 255, int(255 * (1 - a))), width=8)
    label(c, "MAGNETO VS. THE MASK", 1380 - 90, 50, WHITE, t - 0.2)

def s_badly(c, t, g):
    c.paste(DOOM_BG)
    r_ = 260 + 60 * ease(t / 0.6)
    d = ImageDraw.Draw(c)
    d.ellipse([W / 2 - r_, 880 - r_, W / 2 + r_, 880 + r_], fill=(60, 255, 120, 70))
    paste_center(c, MASK, W / 2, 880, scale=1.0 + 0.05 * ease(t / 0.3))
    paste_center(c, E_MAGNET.resize((150, 150)).rotate(160, expand=True), W - 200, 600 + 600 * ease((t - 0.2) / 0.8))
    if t > 0.3:
        paste_center(c, stamp("NOT GOOD", 110, RED, 7), W / 2, 1230, *pop(t - 0.3))

def s_catch(c, t, g):
    c.paste(gradient((120, 90, 10), (14, 10, 2)))
    paste_center(c, glow(E_WARN.resize((380, 380)), 22), W / 2, 880, *pop(t))
    punch(c, "catch", "BUT THERE'S A CATCH", 520, 86, t, color=WHITE, stroke=8)

def s_dune(c, t, g):
    c.paste(SAND_BG); dunes(c, g)
    punch(c, "dune", "DUNE: PART 3", 700, 140, t, color=WHITE, stroke=10)
    label(c, "OPENS THE SAME DAY", 860, 60, DARK, t - 0.2)

def s_dec18(c, t, g):
    c.paste(NAVY_BG)
    a = calendar("DEC", "18", RED); b = calendar("DEC", "18", (200, 140, 60))
    a = a.resize((380, 380)); b = b.resize((380, 380))
    paste_center(c, a, W / 2 - 220 - 120 * (1 - ease(t / 0.3)), 880)
    paste_center(c, b, W / 2 + 220 + 120 * (1 - ease(t / 0.3)), 880)
    paste_center(c, T("dd1", "DOOMSDAY", 54, fill=WHITE, stroke=6), W / 2 - 220, 1130)
    paste_center(c, T("dd2", "DUNE 3", 54, fill=WHITE, stroke=6), W / 2 + 220, 1130)
    punch(c, "sd", "SAME DAY", 560, 120, t - 0.2, color=GOLD, stroke=8)

def s_imax(c, t, g):
    c.paste(gradient((8, 8, 14), (1, 1, 3)))
    screen(c, t, "DUNE 3")
    paste_center(c, pill("US IMAX SCREENS", 76, GOLD), W / 2, 440, *pop(t))

def s_record(c, t, g):
    c.paste(GOLD_BG); sparkle(c, g, 12, 40)
    paste_center(c, glow(E_TROPHY.resize((360, 360)), 22), W / 2, 880, *pop(t))
    punch(c, "rtb", "THE RECORD TO BEAT", 540, 90, t, color=WHITE, stroke=8)

def s_360(c, t, g):
    c.paste(RED_BG)
    paste_center(c, E_SPIDER.resize((220, 220)), W / 2, 600, *pop(t))
    counter0(c, t, 360, 900, 250, WHITE, 0.8)
    label(c, "BRAND NEW DAY OPENING", 1100, 52, GOLD, t - 0.2)
    label(c, "ALL-TIME US RECORD (REPORTED)", 1190, 42, WHITE, t - 0.3)

def s_bars(c, t, g):
    c.paste(STEEL_BG)
    bars(c, t, [("BRAND NEW DAY", 360, (215, 45, 45)), ("ENDGAME", 357, (150, 90, 230)), ("DOOMSDAY*", 270, (60, 200, 110))], top=600)
    punch(c, "os", "OPENING WEEKENDS", 480, 80, t, color=WHITE, stroke=8)
    label(c, "*DOOMSDAY = EARLY TRACKING", 560, 36, (200, 200, 210), t - 0.4)

def s_dunesday(c, t, g):
    left = gradient((30, 90, 50), (3, 10, 5), W // 2, H)
    right = gradient((200, 140, 70), (60, 30, 10), W - W // 2, H)
    c.paste(left, (0, 0)); c.paste(right, (W // 2, 0))
    punch(c, "dsd", "DUNESDAY", 640, 150, t, color=WHITE, stroke=10)
    paste_center(c, T("eq", "≈", 180, fill=GOLD, stroke=6), W / 2, 860, *pop(t - 0.15))
    punch(c, "bbh", "BARBENHEIMER 2.0", 1080, 96, t - 0.3, color=GOLD, stroke=8)

def s_q(c, t, g):
    left = gradient((20, 80, 40), (2, 8, 4), W // 2, H)
    right = gradient((200, 140, 70), (60, 30, 10), W - W // 2, H)
    c.paste(left, (0, 0)); c.paste(right, (W // 2, 0))
    paste_center(c, MASK.resize((MASK.width // 2, MASK.height // 2)), W / 4, 920, *pop(t))
    d = ImageDraw.Draw(c)
    for k in range(3):
        y = 960 + k * 60
        d.ellipse([3 * W / 4 - 200 + k * 30, y - 30, 3 * W / 4 + 200 - k * 30, y + 30], fill=(170 - k * 30, 110 - k * 20, 50, 255))
    paste_center(c, T("qa", "DOOMSDAY", 60, fill=WHITE, stroke=6), W / 4, 1220)
    paste_center(c, T("qb", "DUNE 3", 70, fill=WHITE, stroke=6), 3 * W / 4, 1220)
    punch(c, "first", "FIRST?", 600, 170, t - 0.15, color=GOLD, stroke=10)

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun24", "SUNDAY RECAP", 760, 100, t, color=GOLD)
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

B = [0.0, at(0, 3), ST[1], ST[2], at(2, 3), at(2, 5), ST[3], at(3, 3), ST[4], at(4, 3), at(4, 6), ST[5], at(5, 2),
     at(5, 5), at(5, 6), ST[6], at(6, 2), ST[7], ST[8], ST[9], ST[10], DUR + 0.1]
FNS = [s_hook, s_sales, punch_in(s_3weeks), s_track, s_270, s_highest, s_rdj, s_villain, s_teaser, s_magnet, s_badly,
       s_catch, s_dune, s_dec18, s_imax, s_record, s_360, s_bars, s_dunesday, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (0.1, ST[1] - 0.1, "c1", "$100M+ IN US PRESALES", None),
    (at(2, 3) + 0.05, ST[3] - 0.1, "c2", "~$270M OPENING (TRACKING)", None),
    (at(4, 3) + 0.05, ST[5] - 0.1, "c3", "MAGNETO VS. DOOM", None),
    (at(5, 5) + 0.05, at(5, 6) - 0.05, "c4", "DEC 18: DUNESDAY", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s024_{s}.png")
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
