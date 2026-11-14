"""Live Lore Short 012 (Dead-End Job: Korean horror series hits No. 1 on Netflix's non-English TV chart) - reuses render.py's engine/style.
Usage: python3 render012.py OUT.mp4 [start end]  |  python3 render012.py stills t1 t2 ...
All visuals drawn in code (a generic night convenience store, a hand-made flyer, bar charts, date cards, emoji, a generic skyline;
no show footage, posters, key art, logos or actor images). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
PINK, CYAN, MINT = (255, 120, 170), (90, 200, 255), (120, 225, 190)
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments012.json"))
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

NEON = (90, 255, 190)     # store-sign mint
BLOOD = (230, 50, 60)
HONEY = (255, 190, 40)
E_GHOST, E_SHH, E_SKULL, E_HONEY, E_GLOBE, E_EYES, E_MONEY, E_CLOCK, E_FLYER = (emoji(c, 150) for c in "👻🤫💀🍯🌍👀💸⏰📄")

# ---------- art ----------
NIGHT_STORE = gradient((10, 22, 30), (2, 4, 6))
SICK = gradient((20, 40, 30), (3, 6, 5))
RED_BG = gradient((60, 10, 16), (6, 2, 3))
CHART_BG = gradient((16, 18, 34), (3, 3, 8))
HK_SKY = gradient((40, 20, 60), (6, 4, 12))
CITY = r.skyline(12, 1330, (6, 6, 12, 255))

def flicker(g, seed=0):
    """Fluorescent-light flicker: mostly on, brief dips."""
    v = random.Random(int(g * 12) + seed).random()
    return 0.35 if v < 0.12 else 1.0

def store(w=900, h=780, lit=1.0):
    """Generic 24h convenience store front (no brand): glass doors, shelves, neon OPEN 24H sign."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 120, w, h], fill=(30, 34, 40, 255))                                  # building
    d.rectangle([0, 0, w, 130], fill=(24, 28, 32, 255))                                  # sign band
    sign = r.text_img("OPEN 24H", 84, fill=tuple(int(c * lit) for c in NEON))
    im.alpha_composite(sign, ((w - sign.width) // 2, 18))
    gx0, gy0, gx1, gy1 = 50, 180, w - 50, h - 40
    glow = tuple(int(c * lit) for c in (200, 255, 230))
    d.rectangle([gx0, gy0, gx1, gy1], fill=glow + (255,))                                # lit interior
    for k in range(4):                                                                   # shelves
        y = gy0 + 90 + k * 120
        d.rectangle([gx0 + 30, y, gx1 - 30, y + 14], fill=(110, 120, 120, 255))
        rr = random.Random(k)
        x = gx0 + 40
        while x < gx1 - 80:
            bw = rr.randint(28, 60)
            col = rr.choice([(220, 80, 80), (80, 140, 220), (240, 200, 60), (90, 190, 120), (230, 230, 230)])
            d.rectangle([x, y - rr.randint(40, 80), x + bw, y], fill=tuple(int(c * lit) for c in col) + (255,))
            x += bw + 10
    d.line([(w // 2, gy0), (w // 2, gy1)], fill=(30, 34, 40, 255), width=14)             # door split
    d.rectangle([gx0, gy0, gx1, gy1], outline=(60, 66, 72, 255), width=14)
    return im

STORE_ON, STORE_DIM = store(lit=1.0), store(lit=0.35)

def flyer(rot=-5):
    """Hand-made job flyer with tear-off tabs."""
    w, h = 640, 820
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h - 150], fill=(250, 246, 230, 255))
    for k in range(8):                                                                    # tear-off tabs
        d.rectangle([8 + k * 79, h - 150, 79 + k * 79, h], fill=(250, 246, 230, 255), outline=(200, 195, 180, 255), width=3)
    a = r.text_img("NIGHT SHIFT", 70, fill=DARK)
    im.alpha_composite(a, ((w - a.width) // 2, 50))
    b = r.text_img("50X", 260, fill=BLOOD)
    im.alpha_composite(b, ((w - b.width) // 2, 150))
    c_ = r.text_img("MINIMUM WAGE", 62, fill=DARK, weight="ExtraBold")
    im.alpha_composite(c_, ((w - c_.width) // 2, 470))
    e = r.text_img("NO EXPERIENCE", 44, fill=(90, 90, 90), weight="Bold", spacing=4)
    im.alpha_composite(e, ((w - e.width) // 2, 570))
    d.ellipse([w // 2 - 16, 12, w // 2 + 16, 44], fill=BLOOD + (255,))                      # pin
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

FLYER = flyer()

def bills():
    im = Image.new("RGBA", (800, 640), (0, 0, 0, 0))
    for k, (x, y, rot) in enumerate(((60, 80, -12), (220, 40, 8), (120, 220, -4), (300, 200, 14), (200, 330, -9))):
        b = Image.new("RGBA", (360, 240), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.rectangle([0, 0, 360, 240], fill=(245, 245, 240, 255), outline=(180, 180, 175, 255), width=4)
        t1 = r.text_img("OVERDUE", 58, fill=BLOOD)
        b.alpha_composite(t1, ((360 - t1.width) // 2, 40))
        for j in range(3):
            bd.rectangle([40, 140 + j * 28, 320 - j * 50, 154 + j * 28], fill=(170, 170, 170, 255))
        b = b.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(b, (x, y))
    return im

BILLS = bills()

def rule_card():
    w, h = 820, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(20, 20, 22, 255), outline=BLOOD + (255,), width=10)
    a = r.text_img("RULE #1", 120, fill=BLOOD)
    im.alpha_composite(a, ((w - a.width) // 2, 50))
    for k, line in enumerate(("NEVER TELL ANYONE", "WHAT HAPPENS ON", "THE JOB")):
        b = r.text_img(line, 62, fill=WHITE, weight="ExtraBold")
        im.alpha_composite(b, ((w - b.width) // 2, 230 + k * 82))
    return im

RULE = rule_card()

def name_tag(text):
    w, h = 900, 380
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(245, 245, 245, 255))
    d.rounded_rectangle([0, 0, w, 110], 30, fill=NEON + (255,))
    d.rectangle([0, 70, w, 110], fill=NEON + (255,))
    a = r.text_img("HELLO, MY JOB IS", 50, fill=DARK, weight="ExtraBold", spacing=4)
    im.alpha_composite(a, ((w - a.width) // 2, 28))
    b = r.text_img(text, 104, fill=DARK)
    im.alpha_composite(b, ((w - b.width) // 2, 170))
    return im

TAG = name_tag("DEAD-END JOB")

def warning_sign():
    s = 560
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(s / 2, 20), (s - 20, s - 60), (20, s - 60)], fill=HONEY + (255,), outline=DARK + (255,))
    d.polygon([(s / 2, 70), (s - 70, s - 90), (70, s - 90)], outline=DARK + (255,), width=14)
    ex = r.text_img("!", 260, fill=DARK)
    im.alpha_composite(ex, ((s - ex.width) // 2, 150))
    return im

WARN = warning_sign()

def store_bg(c, g, dim=False):
    c.paste(NIGHT_STORE)
    lit = flicker(g) if not dim else 0.35
    paste_center(c, STORE_ON if lit > 0.5 else STORE_DIM, W / 2, 900, 1.0 + 0.015 * math.sin(g))

def date_card2(c, t, big, small, sub, tint, size=260):
    c.paste(gradient(tint, (4, 4, 8)))
    cw, ch = 680, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=BLOOD + (255,))
    dd.rectangle([0, 120, cw, 170], fill=BLOOD + (255,))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 250 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1290, 52, WHITE, t - 0.25)

def vbar_chart(c, t, vals, names, hi, top=560, base=1220):
    d = ImageDraw.Draw(c, "RGBA")
    n = len(vals)
    bw, gap = 150, 50
    x0 = (W - (n * bw + (n - 1) * gap)) // 2
    k = ease(t / 0.8)
    for i, (v, nm) in enumerate(zip(vals, names)):
        x = x0 + i * (bw + gap)
        hgt = (base - top) * v * k
        col = BLOOD if i == hi else (90, 100, 130)
        d.rounded_rectangle([x, base - hgt, x + bw, base], 16, fill=col + (255,))
        lb = T(("vb", nm), nm, 44, fill=WHITE, weight="Black")
        c.alpha_composite(lb, (int(x + (bw - lb.width) / 2), base + 16))

def dots_map(c, t, n_lit, n_gold, seed=7):
    """Abstract world of dots (not a real map): n_lit light up, n_gold turn gold."""
    d = ImageDraw.Draw(c, "RGBA")
    rr = random.Random(seed)
    pts = [(rr.randint(90, W - 90), rr.randint(560, 1220)) for _ in range(110)]
    lit = int(n_lit * ease(t / 1.0))
    gold = int(n_gold * ease((t - 0.8) / 0.8))
    for i, (x, y) in enumerate(pts):
        col, rad = (60, 70, 90), 12
        if i < lit:
            col, rad = NEON, 16
        if i < gold:
            col, rad = GOLD, 22
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col + (255,))

# ---------- scenes ----------
def s_hook(c, t, g):
    store_bg(c, g)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(0, 0, 0, 120))
    punch(c, "h1", "NO. 1", 640, 330, t, color=GOLD, stroke=12)
    label(c, "NETFLIX · NON-ENGLISH TV", 860, 60, WHITE, t - 0.3)

def s_korean(c, t, g):
    store_bg(c, g)
    paste_center(c, E_GHOST.resize((220, 220)), 820, 560 + 20 * math.sin(g * 5), *pop(t - 0.2))
    paste_center(c, pill("K-HORROR", 92, BLOOD, WHITE), W / 2, 1250, *pop(t))

def s_parttime(c, t, g):
    c.paste(SICK)
    paste_center(c, STORE_ON, W / 2, 880, 0.75 + 0.03 * t)
    paste_center(c, stamp("PART-TIME JOB", 110, GOLD, -7), W / 2, 1220, *pop(t))

def s_title(c, t, g):
    c.paste(NIGHT_STORE)
    paste_center(c, TAG, W / 2, 820, *pop(t, 0.3))

def s_warning(c, t, g):
    c.paste(RED_BG)
    paste_center(c, WARN, W / 2, 820, 1.0 + 0.04 * math.sin(g * 14), ease(t / 0.15))
    label(c, "LOWKEY A WARNING", 1200, 64, WHITE, t - 0.2)

def s_week(c, t, g):
    date_card2(c, t, "2–8", "NOV 2026", "NETFLIX TOP 10 TRACKING WEEK", (90, 20, 30))

def s_87m(c, t, g):
    c.paste(CHART_BG)
    v = 8.7 * ease(t / 0.9)
    punch(c, ("m87", round(v, 1)), f"{v:.1f}M", 760, 260, min(t, 0.3) if t < 0.9 else t, color=GOLD, stroke=10)
    label(c, "VIEWS IN ONE WEEK", 1000, 64, WHITE, t - 0.3)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 1200, *pop(t - 0.5))

def s_chart(c, t, g):
    c.paste(CHART_BG)
    vbar_chart(c, t, [1.0, 0.55, 0.45, 0.43], ["#1", "#2", "#3", "#4"], 0)
    label(c, "GLOBAL NON-ENGLISH TV", 480, 56, WHITE, t)
    label(c, "ILLUSTRATIVE · NOT TO SCALE", 1330, 36, ICE, t)
    if t > 0.8:
        paste_center(c, pill("DEAD-END JOB", 70, GOLD), W / 2, 640, *pop(t - 0.8))

def s_76(c, t, g):
    c.paste(CHART_BG)
    dots_map(c, t, 76, 0)
    punch(c, "c76", "TOP 10 IN 76", 470, 120, t, color=NEON, stroke=6)

def s_22(c, t, g):
    c.paste(CHART_BG)
    dots_map(c, 1.0 + t, 76, 22)
    punch(c, "c22", "NO. 1 IN 22", 470, 120, t, color=GOLD, stroke=6)

def s_hk(c, t, g):
    c.paste(HK_SKY)
    c.alpha_composite(CITY, (-100, 0))
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(14):  # window lights
        rr = random.Random(k)
        x, y = rr.randint(60, W - 60), rr.randint(1100, 1300)
        d.rectangle([x, y, x + 16, y + 22], fill=(255, 220, 140, 200 if (int(g * 3) + k) % 4 else 60))
    paste_center(c, pill("HONG KONG: NO. 1", 84, GOLD), W / 2, 700, *pop(t))
    paste_center(c, cjk("香港", 170, WHITE), W / 2, 930, *pop(t - 0.3))

def s_week2(c, t, g):
    c.paste(SICK)
    paste_center(c, stamp("WEEK 2", 220, NEON, -6), W / 2, 820, *pop(t))

def s_oct30(c, t, g):
    date_card2(c, t, "30", "OCT 2026", "PREMIERE DAY ON NETFLIX", (60, 20, 70), size=300)

def s_5m(c, t, g):
    c.paste(CHART_BG)
    paste_center(c, E_CLOCK.resize((200, 200)), W / 2, 620, *pop(t))
    punch(c, "m5", "5M IN 3 DAYS", 960, 150, t, color=GOLD, stroke=8)

def s_premise(c, t, g):
    c.paste(NIGHT_STORE)
    punch(c, "pr", "THE PREMISE", 600, 140, t, color=WHITE, stroke=6)
    paste_center(c, pill("LEE JAE-WOOK", 84, NEON), W / 2, 900, *pop(t - 0.5))
    label(c, "STARS AS A WORKER IN DEBT", 1060, 50, WHITE, t - 0.7)

def s_debt(c, t, g):
    c.paste(RED_BG)
    paste_center(c, BILLS, W / 2, 860, 0.9 + 0.1 * ease(t / 0.4) + 0.02 * t)
    paste_center(c, E_MONEY.resize((170, 170)), 880, 520, *pop(t - 0.4))

def s_flyer(c, t, g):
    c.paste(gradient((40, 36, 30), (8, 7, 6)))
    paste_center(c, FLYER, W / 2, 860 + 30 * (1 - ease(t / 0.4)), 0.9 + 0.03 * t, ease(t / 0.15))

def s_night(c, t, g):
    store_bg(c, g)
    paste_center(c, pill("NIGHT SHIFT", 90, NEON), W / 2, 1270, *pop(t))

def s_50x(c, t, g):
    c.paste(RED_BG)
    punch(c, "x50", "50X", 760, 400, t, color=GOLD, stroke=12)
    label(c, "THE MINIMUM WAGE", 1050, 70, WHITE, t - 0.2)

def s_rule(c, t, g):
    c.paste(gradient((20, 6, 8), (2, 1, 1)))
    paste_center(c, RULE, W / 2, 820, *pop(t, 0.3))

def s_shh(c, t, g):
    c.paste(gradient((20, 6, 8), (2, 1, 1)))
    paste_center(c, E_SHH.resize((360, 360)), W / 2, 820, *pop(t))

def s_shift(c, t, g):
    store_bg(c, g * 3, dim=False)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(60, 0, 0, 90))
    paste_center(c, E_SKULL.resize((260, 260)), W / 2, 760, 1.0 + 0.05 * math.sin(g * 12), ease(t / 0.15))
    paste_center(c, stamp("EVERY SHIFT", 110, BLOOD, 7), W / 2, 1200, *pop(t - 0.3))

def s_honey(c, t, g):
    c.paste(gradient((70, 46, 8), (10, 6, 2)))
    paste_center(c, cjk("꿀알바", 220, HONEY), W / 2, 640, *pop(t))
    paste_center(c, E_HONEY.resize((240, 240)), W / 2, 980, *pop(t - 0.4))

def s_dream(c, t, g):
    c.paste(gradient((70, 46, 8), (10, 6, 2)))
    paste_center(c, pill("THE DREAM JOB?", 88, HONEY), W / 2, 700, *pop(t))
    paste_center(c, E_EYES.resize((180, 180)), W / 2, 980, *pop(t - 0.3))

def s_trap(c, t, g):
    c.paste(RED_BG)
    paste_center(c, E_HONEY.resize((200, 200)), W / 2, 980, 1.0)
    # cage dropping over the honey
    k = ease(t / 0.35)
    cage = Image.new("RGBA", (420, 460), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cage)
    for x in range(10, 420, 58):
        cd.line([(x, 20), (x, 460)], fill=(200, 200, 210, 255), width=12)
    cd.rectangle([0, 0, 420, 30], fill=(200, 200, 210, 255))
    paste_center(c, cage, W / 2, 400 + 540 * k)
    paste_center(c, stamp("TRAP", 160, BLOOD, -8), W / 2, 560, *pop(t - 0.4))

def s_take(c, t, g):
    c.paste(NIGHT_STORE)
    punch(c, "mt12", "MY TAKE", 600, 160, t, color=WHITE, stroke=6)
    paste_center(c, BILLS, W / 2, 1050, 0.55)

def s_real(c, t, g):
    c.paste(SICK)
    paste_center(c, E_GHOST.resize((260, 260)), W / 2, 700 + 20 * math.sin(g * 4), *pop(t))
    paste_center(c, pill("TOO REAL", 96, GOLD), W / 2, 1050, *pop(t - 0.3))

def s_nocap(c, t, g):
    store_bg(c, g)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(0, 0, 0, 140))
    paste_center(c, stamp("NO CAP", 170, NEON, 6), W / 2, 900, *pop(t))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq12", "TAKE THE SHIFT?", 540, 110, t, color=WHITE, stroke=6)
    paste_center(c, pill("BET, 50X", 100, GOLD), W / 2, 820, *pop(t - 0.15))
    paste_center(c, pill("HARD PASS", 90, CYAN), W / 2, 1060, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun12", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.7:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.7) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 4), at(0, 6), ST[1], at(1, 4), ST[2], at(2, 2), at(2, 5), ST[3], at(3, 2), at(3, 4),
     ST[4], at(4, 2), at(4, 4), ST[5], at(5, 2), at(5, 4), at(5, 8), ST[6], at(6, 2), at(6, 6),
     ST[7], at(7, 3), at(7, 5), ST[8], at(8, 3), at(8, 7), ST[9], ST[10], DUR + 0.1]
FNS = [s_hook, s_korean, s_parttime, s_title, s_warning, s_week, s_87m, s_chart, s_76, s_22, s_hk,
       s_week2, s_oct30, s_5m, s_premise, s_debt, s_flyer, s_50x, s_rule, s_shh, s_shift,
       s_honey, s_dream, s_trap, s_take, s_real, s_nocap, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "NETFLIX TOP 10 DATA", None),
    (ST[3], ST[4] - 0.1, "c2", "WEEK OF NOV 2–8", None),
    (ST[4], ST[5] - 0.1, "c3", "8 EPISODES · FANTASY HORROR", None),
    (ST[5], ST[6] - 0.1, "c4", "FICTION, NOT A REAL JOB AD", None),
    (ST[7], ST[8] - 0.1, "c5", "KOREAN TITLE ≈ \"HONEY GIG\"", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s012_{s}.png")
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
