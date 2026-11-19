"""Live Lore Short 015 (2026 Words of the Year: Dictionary.com "maxxing", Collins "mogging", Cambridge "human",
plus Japan's buzzword-award shortlist) - reuses render.py's engine/style.
Usage: python3 render015.py OUT.mp4 [start end]  |  python3 render015.py stills t1 t2 ...
All visuals drawn in code (generic dictionary-entry cards, books, bars, tags, figures, grass, emoji; dictionary and
award names as plain text only; no logos, photos, characters or mascots). No music.
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
SEG = json.load(open("segments015.json"))
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

E_THINK, E_BOOKS, E_UP, E_ROBOT, E_PERSON, E_CLOCK, E_MONKEY, E_FIRE, E_WAVE, E_PHONE, E_EYES, E_HERB = (
    emoji(c, 150) for c in ["🤔", "📚", "📈", "🤖", "🧑", "⏳", "🐒", "🔥", "👋", "📱", "👀", "🌿"])

NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
PURP_BG = gradient((50, 24, 80), (6, 3, 14))
WARM_BG = gradient((90, 40, 20), (10, 4, 2))
TEAL_BG = gradient((10, 60, 70), (2, 8, 12))
JP_BG = gradient((246, 244, 240), (210, 206, 200))
GRASS_SKY = gradient((140, 200, 255), (220, 240, 255))

def entry_card(word, syll, pos, defn, source, accent):
    """Generic dictionary-entry card (our own design, no publisher branding)."""
    cw, ch = 900, 760
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(cd)
    d.rounded_rectangle([0, 0, cw, ch], 40, fill=PAPER + (255,))
    d.rounded_rectangle([0, 0, cw, 120], 40, fill=accent + (255,))
    d.rectangle([0, 80, cw, 120], fill=accent + (255,))
    src = r.text_img(source, 50, fill=WHITE, weight="ExtraBold", spacing=6)
    if src.width > cw - 60:
        src = src.resize((cw - 60, int(src.height * (cw - 60) / src.width)), Image.LANCZOS)
    cd.alpha_composite(src, ((cw - src.width) // 2, 30))
    wd = r.text_img(syll, 150, fill=DARK)
    if wd.width > cw - 80:
        wd = wd.resize((cw - 80, int(wd.height * (cw - 80) / wd.width)), Image.LANCZOS)
    cd.alpha_composite(wd, (50, 170))
    ps = r.text_img(pos, 50, fill=accent, weight="Bold")
    cd.alpha_composite(ps, (56, 370))
    y = 460
    for line in defn:
        li = r.text_img(line, 52, fill=(60, 60, 66), weight="Bold")
        cd.alpha_composite(li, (56, y)); y += 76
    return cd

CARD_MAX = entry_card("maxxing", "max·xing", "noun · slang", ["doing something to the", "fullest; optimizing it"],
                      "DICTIONARY.COM · WORD OF 2026", (40, 90, 200))
CARD_MOG = entry_card("mogging", "mog·ging", "noun · Gen Z slang", ["outshining someone", "or something"],
                      "COLLINS · WORD OF 2026", RED)
CARD_HUM = entry_card("human", "hu·man", "adjective", ["having the qualities and", "feelings of people, not machines"],
                      "CAMBRIDGE · WORD OF 2026", (30, 140, 90))

def book(col, txt):
    w, h = 230, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 18, fill=col + (255,))
    d.rectangle([0, 0, 28, h], fill=tuple(int(v * 0.7) for v in col) + (255,))
    d.rectangle([w - 14, 12, w, h - 12], fill=PAPER + (255,))
    q = r.text_img(txt, 170, fill=WHITE)
    im.alpha_composite(q, ((w - q.width) // 2 + 8, (h - q.height) // 2))
    return im
BOOKS = [book((40, 90, 200), "?"), book(RED, "?"), book((30, 140, 90), "?")]

def figure(h, col):
    w = int(h * 0.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hr = h * 0.13
    d.ellipse([w / 2 - hr, 0, w / 2 + hr, 2 * hr], fill=col)
    d.rounded_rectangle([w * 0.12, 2 * hr + h * 0.03, w * 0.88, h * 0.62], int(w * 0.18), fill=col)
    d.rounded_rectangle([w * 0.22, h * 0.55, w * 0.47, h], int(w * 0.1), fill=col)
    d.rounded_rectangle([w * 0.53, h * 0.55, w * 0.78, h], int(w * 0.1), fill=col)
    return im
FIG_DIM = figure(420, (70, 74, 96, 255))
FIG_GOLD = figure(560, GOLD + (255,))

def tag(text, col):
    img = r.text_img(text, 78, fill=DARK)
    w, h = img.width + 150, img.height + 60
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, h / 2), (60, 0), (w, 0), (w, h), (60, h)], fill=col + (255,))
    d.ellipse([34, h / 2 - 14, 62, h / 2 + 14], fill=(0, 0, 0, 0))
    im.alpha_composite(img, (110, 30))
    return im
TAG1, TAG2 = tag("HUMAN-MADE", GOLD), tag("HUMAN-WRITTEN", (240, 240, 235))

def word_card(text, col, rot):
    img = r.text_img(text, 84, fill=DARK)
    im = Image.new("RGBA", (img.width + 80, img.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width, im.height], 24, fill=col + (255,))
    im.alpha_composite(img, (40, 25))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)
CONT = [word_card("AGENT", CYAN, -6), word_card("WHOLESOME", GOLD, 4), word_card("ANALOGUE", (240, 240, 235), -3)]

def grass_layer(seed, base, col, n=260, hmax=260):
    rng = random.Random(seed)
    im = Image.new("RGBA", (W + 200, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, base, W + 200, H], fill=col)
    for _ in range(n):
        x = rng.uniform(0, W + 200); h = rng.uniform(80, hmax); lean = rng.uniform(-40, 40)
        d.polygon([(x - 14, base + 5), (x + 14, base + 5), (x + lean, base - h)], fill=col)
    return im
GRASS_B = grass_layer(2, 1250, (60, 150, 60, 255))
GRASS_F = grass_layer(7, 1450, (40, 120, 45, 255), hmax=320)

def shortlist(t):
    w, h = 820, 860
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 36, fill=(255, 255, 255, 255), outline=(200, 40, 50, 255), width=8)
    hd = r.text_img("30 NOMINEES", 70, fill=(200, 40, 50))
    im.alpha_composite(hd, ((w - hd.width) // 2, 40))
    rows = ["ちいかわ（現象）", "りくりゅう", "AI暴走", "パンチくん", "…+26"]
    for i, txt in enumerate(rows):
        if t < 0.25 + i * 0.22:
            break
        y = 180 + i * 130
        if i == 0:
            d.rounded_rectangle([40, y - 10, w - 40, y + 100], 20, fill=GOLD + (255,))
        im.alpha_composite(cjk(txt, 76, DARK), (80, y))
    return im

def meter(c, t, y, name, frac, col):
    d = ImageDraw.Draw(c, "RGBA")
    lb = T(("mt", name), name, 54, fill=WHITE, weight="Black")
    c.alpha_composite(lb, (120, y))
    d.rounded_rectangle([120, y + 80, W - 120, y + 150], 30, fill=(50, 54, 80, 255))
    k = ease(t / 0.7) * frac
    d.rounded_rectangle([120, y + 80, 120 + max(60, (W - 240) * k), y + 150], 30, fill=col + (255,))
    if k > 0.98 * frac:
        mx = T(("mx",), "MAX", 44, fill=DARK, weight="Black")
        c.alpha_composite(mx, (W - 120 - mx.width - 26, y + 92))

# ---------- scenes ----------
def s_quiz(c, t, g):
    c.paste(NAVY_BG)
    label(c, "QUICK QUIZ", 520, 60, GOLD, t)
    punch(c, "q1", "WORD OF", 700, 150, t, color=WHITE, stroke=6)
    punch(c, "q2", "THE YEAR?", 860, 150, max(0, t - 0.2), color=WHITE, stroke=6)
    paste_center(c, E_THINK.resize((170, 170)), W / 2, 1100, *pop(t - 0.4))

def s_books(c, t, g):
    c.paste(PURP_BG)
    for i, (b, x) in enumerate(zip(BOOKS, (250, 540, 830))):
        y = 820 - 700 * (1 - ease((t - i * 0.15) / 0.35))
        paste_center(c, b, x, y, alpha=ease((t - i * 0.15) / 0.12))
    label(c, "3 DICTIONARIES", 1110, 64, WHITE, t - 0.5)

def s_diff(c, t, g):
    c.paste(PURP_BG)
    paste_center(c, stamp("3 DIFFERENT", 130, GOLD, -6), W / 2, 680, *pop(t))
    paste_center(c, stamp("ANSWERS", 150, WHITE, 4), W / 2, 960, *pop(t - 0.25))

def s_cardmax(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, CARD_MAX, W / 2, 860 + 300 * (1 - ease(t / 0.35)), scale=1.0 + 0.02 * t, alpha=ease(t / 0.15))
    label(c, "ANNOUNCED OCT 26", 1320, 50, WHITE, t - 0.4)

def s_max(c, t, g):
    c.paste(NAVY_BG)
    punch(c, "tm", "TO THE MAX", 540, 120, t, color=GOLD, stroke=6)
    for i, (nm, col) in enumerate((("SLEEP", CYAN), ("STEPS", GREEN), ("FOCUS", ORANGE))):
        meter(c, t - 0.2 - i * 0.15, 720 + i * 200, nm, 1.0, col)

def s_online(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, E_PHONE.resize((420, 420)), W / 2, 850, scale=1.0 + 0.03 * math.sin(g * 4), alpha=ease(t / 0.15))
    label(c, "DEEPLY ONLINE", 1180, 70, WHITE, t - 0.2)

def s_opt(c, t, g):
    c.paste(TEAL_BG)
    d = ImageDraw.Draw(c, "RGBA")
    items = ["MORNING ROUTINE", "SKIN CARE", "GYM SPLIT", "SCREEN TIME"]
    for i, it in enumerate(items):
        lt = t - i * 0.25
        if lt < 0:
            break
        y = 560 + i * 170
        a = int(255 * ease(lt / 0.15))
        d.rounded_rectangle([130, y, 230, y + 100], 20, outline=(255, 255, 255, a), width=8)
        if lt > 0.2:
            d.line([(150, y + 50), (175, y + 80), (215, y + 20)], fill=GREEN + (a,), width=14)
        c.alpha_composite(T(("op", it), it, 64, fill=WHITE, weight="Black"), (270, y + 14))
    label(c, "OPTIMIZE EVERYTHING", 1260, 56, GOLD, t - 0.8)

def s_cardmog(c, t, g):
    c.paste(WARM_BG)
    paste_center(c, CARD_MOG, W / 2, 860 + 300 * (1 - ease(t / 0.35)), scale=1.0 + 0.02 * t, alpha=ease(t / 0.15))
    label(c, "ANNOUNCED NOV 3", 1320, 50, WHITE, t - 0.4)

def s_outshine(c, t, g):
    c.paste(r.THEATER)
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(spot).polygon([(W * 0.62 - 60, 300), (W * 0.62 + 60, 300), (W * 0.62 + 300, 1300), (W * 0.62 - 300, 1300)],
                                 fill=(255, 240, 190, int(90 * ease(t / 0.4))))
    c.alpha_composite(spot.filter(ImageFilter.GaussianBlur(30)))
    paste_center(c, FIG_DIM, W * 0.3, 1090, alpha=1 - 0.5 * ease((t - 0.3) / 0.5))
    paste_center(c, FIG_GOLD, W * 0.64, 1020, scale=0.9 + 0.1 * ease(t / 0.5))
    paste_center(c, pill("OUTSHINING SOMEONE", 74, GOLD), W / 2, 560, *pop(t - 0.2))

def s_210(c, t, g):
    c.paste(WARM_BG)
    d = ImageDraw.Draw(c, "RGBA")
    base, top = 1250, 680
    k = ease((t - 0.2) / 0.8)
    for x, v, col, lab in ((W * 0.3, 100, (110, 110, 130), "BEFORE"), (W * 0.7, 310, GOLD, "2026")):
        hgt = (base - top) * v / 310 * (k if v > 100 else 1)
        d.rounded_rectangle([x - 130, base - hgt, x + 130, base], 24, fill=col + (255,))
        lb = T(("b2", lab), lab, 54, fill=WHITE, weight="Black")
        c.alpha_composite(lb, (int(x - lb.width / 2), base + 20))
    if k > 0.7:
        paste_center(c, T("p210", "+210%", 130, fill=GOLD, stroke=8), W * 0.7, top - 80, *pop(t - 0.75))

def s_nah(c, t, g):
    c.paste(TEAL_BG)
    label(c, "CAMBRIDGE", 560, 66, WHITE, t)
    paste_center(c, stamp("NAH…", 230, GOLD, -7), W / 2, 820, *pop(t - 0.1))
    paste_center(c, E_WAVE.resize((150, 150)), W / 2, 1110, scale=1.0, alpha=ease((t - 0.3) / 0.15))

def s_cardhum(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, CARD_HUM, W / 2, 860 + 300 * (1 - ease(t / 0.3)), scale=1.0 + 0.02 * t, alpha=ease(t / 0.12))
    label(c, "ANNOUNCED NOV 17", 1320, 50, WHITE, t - 0.4)

def s_tags(c, t, g):
    c.paste(NAVY_BG)
    label(c, "WHAT PEOPLE KEEP WRITING", 520, 52, WHITE, t)
    for i, (tg, x, y, rot) in enumerate(((TAG1, W / 2, 780, -4), (TAG2, W / 2, 1040, 3))):
        lt = t - 0.2 - i * 0.6
        paste_center(c, tg.rotate(rot, expand=True, resample=Image.BICUBIC), x, y - 300 * (1 - ease(lt / 0.3)), alpha=ease(lt / 0.12))

def s_vs(c, t, g):
    c.paste(NAVY_BG)
    d = ImageDraw.Draw(c, "RGBA")
    d.rectangle([W / 2 - 6, 500, W / 2 + 6, 1250], fill=(255, 255, 255, int(200 * ease(t / 0.3))))
    paste_center(c, E_PERSON.resize((300, 300)), W * 0.26, 860, *pop(t))
    paste_center(c, E_ROBOT.resize((300, 300)), W * 0.74, 860, *pop(t - 0.2))
    paste_center(c, T("vsp", "PEOPLE", 60, fill=GOLD, weight="Bold", spacing=6), W * 0.26, 1100, alpha=ease((t - 0.3) * 3))
    paste_center(c, T("vsai", "AI", 60, fill=CYAN, weight="Bold", spacing=6), W * 0.74, 1100, alpha=ease((t - 0.4) * 3))

def s_cont(c, t, g):
    c.paste(PURP_BG)
    label(c, "THE OTHER CONTENDERS", 500, 56, WHITE, t)
    for i, (cd, y) in enumerate(zip(CONT, (720, 930, 1140))):
        lt = t - 0.15 - i * 0.45
        paste_center(c, cd, W / 2 + 500 * (1 - ease(lt / 0.3)), y, alpha=ease(lt / 0.1))

def s_grass(c, t, g):
    c.paste(GRASS_SKY)
    c.alpha_composite(GRASS_B.crop((int(40 * t), 0, int(40 * t) + W, H)))
    c.alpha_composite(GRASS_F.crop((int(100 - 60 * t) if 100 - 60 * t > 0 else 0, 0, (int(100 - 60 * t) if 100 - 60 * t > 0 else 0) + W, H)))
    paste_center(c, stamp("TOUCH GRASS", 105, (20, 80, 30), -5), W / 2, 700, *pop(t - 0.1))
    paste_center(c, E_HERB.resize((150, 150)), W / 2, 960, *pop(t - 0.35))

def s_japan(c, t, g):
    c.paste(JP_BG)
    d = ImageDraw.Draw(c, "RGBA")
    rad = 230 * (0.8 + 0.2 * ease(t / 0.4))
    d.ellipse([W / 2 - rad, 760 - rad, W / 2 + rad, 760 + rad], fill=(200, 30, 45, 255))
    paste_center(c, cjk("日本", 170, WHITE), W / 2, 760, *pop(t - 0.15))
    paste_center(c, pill("STILL DECIDING", 76, GOLD), W / 2, 1120, *pop(t - 0.35))
    paste_center(c, E_CLOCK.resize((120, 120)), W / 2, 1290, *pop(t - 0.5))

def s_list(c, t, g):
    c.paste(JP_BG)
    paste_center(c, shortlist(t), W / 2, 860, scale=0.95 + 0.05 * ease(t / 0.4), alpha=ease(t / 0.15))

def s_monkey(c, t, g):
    c.paste(gradient((255, 230, 200), (230, 180, 140)))
    paste_center(c, E_MONKEY.resize((380, 380)), W / 2, 820 + 20 * math.sin(g * 6), *pop(t))
    paste_center(c, cjk("パンチくん", 110, DARK), W / 2, 1120, alpha=ease((t - 0.3) / 0.15))
    label(c, "A BABY MONKEY", 560, 60, DARK, t - 0.1)

def s_dec1(c, t, g):
    date_card2(c, t, "1", "DEC 2026", "JAPAN'S WINNER REVEALED", (120, 30, 40))

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt15", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 900, *pop(t - 0.3))

def s_cooked(c, t, g):
    c.paste(WARM_BG)
    paste_center(c, stamp("LOWKEY COOKED", 95, GOLD, -6), W / 2, 760, *pop(t))
    paste_center(c, E_FIRE.resize((160, 160)), W / 2, 1080, 1.0 + 0.05 * math.sin(g * 5), ease((t - 0.3) / 0.2))

def s_vote(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "v15", "YOUR VOTE?", 520, 120, t, color=WHITE, stroke=6)
    for i, (txt, col, y) in enumerate((("MAXXING", (90, 140, 255), 740), ("MOGGING", RED, 940), ("HUMAN", GREEN, 1140))):
        paste_center(c, pill(txt, 84, col, WHITE), W / 2, y, *pop(t - 0.15 - i * 0.15))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun15", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 4), at(0, 6), ST[1], at(1, 3), ST[2], at(2, 3), ST[3], at(3, 3), at(3, 6), ST[4], at(4, 3), ST[5],
     at(5, 5), ST[6], at(6, 6), ST[7], at(7, 3), at(7, 8), at(7, 11), ST[8], at(8, 5), ST[9], ST[10], DUR + 0.1]
FNS = [s_quiz, s_books, s_diff, s_cardmax, s_max, s_online, s_opt, s_cardmog, s_outshine, s_210, s_nah, s_cardhum,
       s_tags, s_vs, s_cont, s_grass, s_japan, s_list, s_monkey, s_dec1, s_take, s_cooked, s_vote, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[3], ST[4] - 0.1, "c1", "PER COLLINS' OWN DATA", None),
    (ST[5], ST[6] - 0.1, "c2", "\"HUMAN\" = THE NEW PREMIUM", None),
    (ST[7], ST[8] - 0.1, "c3", "JAPAN'S BUZZWORD AWARD", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s015_{s}.png")
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
