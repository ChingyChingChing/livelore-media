"""Live Lore Short 016 (Japan's "dopagaki" buzzword: dopamine + "gaki"/brat, on the 2026 buzzword-award shortlist,
plus the Children and Families Agency's first national draft guidelines on kids' internet use) - reuses render.py.
Usage: python3 render016.py OUT.mp4 [start end]  |  python3 render016.py stills t1 t2 ...
All visuals drawn in code (generic phone/feed mock-ups, cards, timelines, meters, figures, emoji; agency, app and award
names as plain text only; no logos, photos, characters or mascots). No music.
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
SEG = json.load(open("segments016.json"))
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


E_POINT, E_BRAIN, E_PLAY, E_CHAT, E_GAME, E_WEARY, E_ADULT, E_DASH, E_PHONE, E_BABY, E_HANDS, E_TEEN, E_SCALE, E_HOUSE, \
    E_FIRE, E_EYES, E_DOC, E_CAL = (emoji(ch, 150) for ch in
    ["👉", "🧠", "▶️", "💬", "🎮", "😩", "🧑", "💨", "📱", "👶", "🤝", "🧑‍🎓", "⚖️", "🏠", "🔥", "👀", "📄", "📅"])

NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
PINK_BG = gradient((90, 20, 70), (10, 2, 10))
TEAL_BG = gradient((10, 60, 70), (2, 8, 12))
WARM_BG = gradient((90, 40, 20), (10, 4, 2))
GREEN_BG = gradient((20, 70, 40), (2, 10, 5))
JP_BG = gradient((246, 244, 240), (210, 206, 200))
NEON = (255, 70, 160)

FEED_COLS = [(255, 120, 90), (90, 200, 255), (255, 210, 80), (150, 110, 240), (90, 220, 150), (255, 90, 150)]
def feed_card(i):
    w, h = 520, 820
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = FEED_COLS[i % len(FEED_COLS)]
    d.rounded_rectangle([0, 0, w, h], 30, fill=tuple(int(v * 0.55) for v in col) + (255,))
    rng = random.Random(i)
    for _ in range(5):
        x, y, rr = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(60, 180)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (140,))
    d.polygon([(w / 2 - 50, h / 2 - 60), (w / 2 - 50, h / 2 + 60), (w / 2 + 60, h / 2)], fill=(255, 255, 255, 200))
    for k, yy in enumerate((h - 150, h - 100)):
        d.rounded_rectangle([40, yy, 40 + (300 if k == 0 else 200), yy + 26], 13, fill=(255, 255, 255, 170))
    for k in range(3):
        d.ellipse([w - 90, 380 + k * 110, w - 30, 440 + k * 110], fill=(255, 255, 255, 160))
    return im
FEED = [feed_card(i) for i in range(8)]

def phone_feed(t, speed=1.6):
    """A generic phone with a feed that keeps swiping up."""
    pw, ph = 600, 1000
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw, ph], 70, fill=(20, 20, 24, 255))
    scr = Image.new("RGBA", (520, 820), (0, 0, 0, 255))
    pos = t * speed
    k, f = int(pos), ease((pos % 1) / 0.35)
    scr.alpha_composite(FEED[k % 8], (0, int(-820 * f)))
    scr.alpha_composite(FEED[(k + 1) % 8], (0, int(820 - 820 * f)))
    mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 520, 820], 30, fill=255)
    im.paste(scr, (40, 90), mask)
    d.rounded_rectangle([pw / 2 - 70, 30, pw / 2 + 70, 56], 13, fill=(0, 0, 0, 255))
    return im

def word_badge(t):
    w, h = 900, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=(255, 255, 255, 255), outline=NEON + (255,), width=10)
    jp = cjk("ドパガキ", 190, DARK)
    im.alpha_composite(jp, ((w - jp.width) // 2, 60))
    ro = r.text_img("DOPAGAKI", 96, fill=NEON)
    im.alpha_composite(ro, ((w - ro.width) // 2, 330))
    return im
BADGE = word_badge(1)

def eq_part(text, col, sub):
    img = r.text_img(text, 92, fill=DARK)
    sb = r.text_img(sub, 40, fill=(60, 60, 70), weight="Bold")
    w = max(img.width, sb.width) + 70
    im = Image.new("RGBA", (w, img.height + sb.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width, im.height], 28, fill=col + (255,))
    im.alpha_composite(img, ((w - img.width) // 2, 24))
    im.alpha_composite(sb, ((w - sb.width) // 2, img.height + 44))
    return im
EQ1, EQ2 = eq_part("DOPAMINE", (90, 200, 255), "THE BRAIN'S REWARD BUZZ"), eq_part("GAKI", GOLD, "ROUGH WORD FOR \"BRAT\"")

def bubble(text, col):
    img = cjk(text, 80, DARK)
    w, h = img.width + 70, img.height + 40
    im = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=col + (255,))
    d.polygon([(60, h - 2), (110, h - 2), (55, h + 38)], fill=col + (255,))
    im.alpha_composite(img, (35, 20))
    return im
BUBS = [bubble(tx, col) for tx, col in (("ドパガキすぎる", (255, 255, 255)), ("完全にドパガキ", GOLD),
                                         ("ドパガキ定期", (90, 200, 255)), ("ドパガキ…", (255, 150, 200)))]

def shortlist(t):
    w, h = 820, 860
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 36, fill=(255, 255, 255, 255), outline=(200, 40, 50, 255), width=8)
    hd = r.text_img("30 NOMINEES", 70, fill=(200, 40, 50))
    im.alpha_composite(hd, ((w - hd.width) // 2, 40))
    rows = ["…", "ドパガキ", "…", "…+27"]
    for i, txt in enumerate(rows):
        if t < 0.15 + i * 0.18:
            break
        y = 200 + i * 150
        if txt == "ドパガキ":
            d.rounded_rectangle([40, y - 14, w - 40, y + 110], 20, fill=GOLD + (255,))
        im.alpha_composite(cjk(txt, 84, DARK), (90, y))
    return im

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
FIG_S = figure(300, (120, 130, 170, 255))
FIG_L = figure(560, GOLD + (255,))

def doc_card():
    w, h = 720, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=PAPER + (255,))
    hd = r.text_img("GUIDELINES", 80, fill=DARK)
    im.alpha_composite(hd, ((w - hd.width) // 2, 70))
    sb = r.text_img("KIDS + THE INTERNET", 44, fill=(90, 90, 100), weight="Bold", spacing=4)
    im.alpha_composite(sb, ((w - sb.width) // 2, 190))
    for k in range(8):
        y = 310 + k * 66
        d.rounded_rectangle([70, y, w - 70 - (k % 3) * 90, y + 26], 13, fill=(200, 196, 188, 255))
    return im
DOC = doc_card()

AGES = [("0-2", (255, 150, 120)), ("", (255, 200, 90)), ("", (150, 220, 120)), ("", (90, 200, 255)),
        ("", (150, 120, 240)), ("16-18", (255, 110, 170))]
def timeline(c, t, y=860):
    d = ImageDraw.Draw(c, "RGBA")
    x0, x1 = 90, W - 90
    sw = (x1 - x0) / 6
    for i, (lab, col) in enumerate(AGES):
        k = ease((t - 0.1 - i * 0.12) / 0.2)
        if k <= 0:
            continue
        xa = x0 + i * sw + 6
        d.rounded_rectangle([xa, y - 70 * k, xa + sw - 12, y + 70 * k], 18, fill=col + (255,))
        n = T(("tn", i), str(i + 1), 72, fill=DARK, weight="Black")
        c.alpha_composite(n, (int(xa + (sw - 12 - n.width) / 2), y - 45))
    for txt, x in (("AGE 0", x0), ("AGE 18", x1)):
        im = T(("ta", txt), txt, 50, fill=WHITE, weight="Black")
        c.alpha_composite(im, (int(min(max(x - im.width / 2, 20), W - 20 - im.width)), y + 110))

def ban_sign(t):
    s = 460
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, s - 10, s - 10], outline=RED + (255,), width=46)
    d.line([(90, 90), (s - 90, s - 90)], fill=RED + (255,), width=46)
    return im
BAN = ban_sign(1)

def tile(text, col):
    img = r.text_img(text, 80, fill=WHITE)
    w, h = max(img.width + 100, 600), img.height + 90
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w, h], 40, fill=col + (255,), outline=(255, 255, 255, 120), width=4)
    im.alpha_composite(img, ((w - img.width) // 2, 45))
    return im
TILES = [tile("INSTAGRAM", (50, 54, 80)), tile("TIKTOK", (50, 54, 80))]

def gauge(c, t, val=8.5):
    d = ImageDraw.Draw(c, "RGBA")
    cx, cy, R = W / 2, 1060, 360
    for i in range(10):
        a0, a1 = 180 + i * 18, 180 + (i + 1) * 18 - 2
        col = tuple(int(a + (b - a) * i / 9) for a, b in zip((90, 220, 150), (235, 50, 40)))
        d.arc([cx - R, cy - R, cx + R, cy + R], a0, a1, fill=col + (255,), width=70)
    for v in (1, 10):
        a = math.radians(180 + (v - 0.5) * 18)
        im = T(("gv", v), str(v), 60, fill=WHITE, weight="Black")
        c.alpha_composite(im, (int(cx + (R + 70) * math.cos(a) - im.width / 2), int(cy + (R + 70) * math.sin(a) - im.height / 2)))
    k = ease(t / 0.9)
    v = 0.5 + (val - 0.5) * k + 0.25 * math.sin(t * 9) * k
    a = math.radians(180 + v * 18)
    d.line([(cx, cy), (cx + (R - 60) * math.cos(a), cy + (R - 60) * math.sin(a))], fill=WHITE, width=22)
    d.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], fill=WHITE)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(PINK_BG)
    paste_center(c, phone_feed(t), W / 2, 960, scale=0.92 + 0.04 * ease(t / 0.4))
    punch(c, "h1", "JAPAN'S NEW WORD", 330, 90, t, color=WHITE, stroke=7)
    punch(c, "h2", "IS ABOUT YOU", 460, 100, max(0, t - 0.15), color=GOLD, stroke=7)

def s_you(c, t, g):
    c.paste(PINK_BG)
    paste_center(c, phone_feed(t + 3, 2.4), W * 0.6, 940, scale=0.85)
    paste_center(c, E_POINT.resize((260, 260)), W * 0.2 + 30 * math.sin(g * 8), 900, *pop(t))
    paste_center(c, stamp("YES, YOU", 110, GOLD, -6), W / 2, 420, *pop(t - 0.2))

def s_word(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, BADGE, W / 2, 820, scale=0.7 + 0.3 * ease(t / 0.3) + 0.015 * t, alpha=ease(t / 0.12))

def s_eq(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, EQ1, W / 2, 620, *pop(t))
    paste_center(c, T("plus", "+", 140, fill=WHITE), W / 2, 830, alpha=ease((t - 0.25) / 0.1))
    paste_center(c, EQ2, W / 2, 1040, *pop(t - 0.45))

def s_hooked(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, E_BRAIN.resize((330, 330)), W / 2, 860, scale=1.0 + 0.04 * math.sin(g * 6))
    for i, (e, ph) in enumerate(((E_PLAY, 0), (E_CHAT, 2.1), (E_GAME, 4.2))):
        a = g * 2.2 + ph
        lt = t - i * 0.2
        paste_center(c, e.resize((160, 160)), W / 2 + 330 * math.cos(a), 860 + 330 * math.sin(a), *pop(lt))
    label(c, "VIDEOS · SOCIAL · GAMES", 1290, 54, WHITE, t - 0.2)

def s_bored(c, t, g):
    c.paste(TEAL_BG)
    d = ImageDraw.Draw(c, "RGBA")
    punch(c, "b1", "1 BORING SECOND", 560, 104, t, color=WHITE, stroke=6)
    k = 1 - ease((t - 0.2) / 1.2)
    d.rounded_rectangle([140, 760, W - 140, 860], 50, fill=(40, 44, 60, 255))
    d.rounded_rectangle([140, 760, 140 + max(100, (W - 280) * k), 860], 50, fill=(RED if k < 0.4 else GOLD) + (255,))
    paste_center(c, E_WEARY.resize((230, 230)), W / 2, 1080, *pop(t - 0.5))

def s_every(c, t, g):
    c.paste(NAVY_BG)
    for i, (b, x, y) in enumerate(zip(BUBS, (330, 700, 360, 720), (560, 760, 960, 1160))):
        paste_center(c, b, x, y, *pop(t - i * 0.18))

def s_nov5(c, t, g):
    date_card2(c, t, "5", "NOV 2026", "30 WORDS NOMINATED", (120, 30, 40))

def s_list(c, t, g):
    c.paste(JP_BG)
    paste_center(c, shortlist(t), W / 2, 860, scale=0.95 + 0.05 * ease(t / 0.4), alpha=ease(t / 0.15))

def s_adults(c, t, g):
    c.paste(WARM_BG)
    paste_center(c, FIG_S, W * 0.3, 1000, alpha=ease(t / 0.15))
    paste_center(c, FIG_L, W * 0.66, 920, *pop(t - 0.2))
    paste_center(c, pill("NOT JUST KIDS", 84, GOLD), W / 2, 500, *pop(t - 0.1))

def s_dryer(c, t, g):
    c.paste(WARM_BG)
    paste_center(c, E_ADULT.resize((300, 300)), W * 0.36, 860, *pop(t))
    for k in range(3):
        paste_center(c, E_DASH.resize((130, 130)), W * 0.36 - 230 - 40 * ((g * 3 + k * 0.33) % 1), 700 + k * 90,
                     alpha=0.8 * ease(t / 0.2))
    sc, al = pop(t - 0.2)
    paste_center(c, phone_feed(t, 2.0), W * 0.72, 900 + 20 * math.sin(g * 5), scale=0.42 * sc, alpha=al)
    label(c, "THE 'ARU ARU' (SO RELATABLE)", 1250, 48, WHITE, t - 0.3)

def s_nov10(c, t, g):
    date_card2(c, t, "10", "NOV 2026", "CHILDREN & FAMILIES AGENCY", (20, 50, 110))

def s_doc(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, DOC, W / 2, 900 + 300 * (1 - ease(t / 0.35)), scale=1.0 + 0.02 * t, alpha=ease(t / 0.15))
    if t > 0.6:
        paste_center(c, stamp("1ST NATIONAL DRAFT", 76, RED, -8), W / 2, 1160, *pop(t - 0.6))

def s_ages(c, t, g):
    c.paste(NAVY_BG)
    punch(c, "ag", "6 AGE GROUPS", 560, 120, t, color=GOLD, stroke=6)
    timeline(c, t)

def s_baby(c, t, g):
    c.paste(gradient((255, 230, 205), (235, 190, 150)))
    paste_center(c, E_BABY.resize((300, 300)), W * 0.32, 860, *pop(t))
    paste_center(c, E_HANDS.resize((240, 240)), W * 0.7, 870, *pop(t - 0.2))
    label(c, "UNDER 2", 560, 70, DARK, t)
    paste_center(c, pill("REAL HUMANS FIRST", 76, GOLD), W / 2, 1150, *pop(t - 0.35))

def s_teen(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, E_TEEN.resize((320, 320)), W / 2, 850, *pop(t))
    label(c, "AGE 16 TO 18", 560, 70, WHITE, t)
    paste_center(c, pill("MOSTLY THEIR OWN CALL", 70, GOLD), W / 2, 1150, *pop(t - 0.3))

def s_noban(c, t, g):
    c.paste(GREEN_BG)
    paste_center(c, phone_feed(t, 1.5), W / 2, 860, scale=0.45, alpha=ease(t / 0.1))
    k = 1 - ease((t - 0.3) / 0.3)
    paste_center(c, BAN, W / 2, 860, scale=1.0 + 0.3 * (1 - ease(t / 0.2)), alpha=max(0.0, k) if t > 0.3 else ease(t / 0.1))
    if t > 0.45:
        paste_center(c, stamp("NO BLANKET BANS", 96, (120, 240, 140), -5), W / 2, 1170, *pop(t - 0.45))

def s_scale(c, t, g):
    c.paste(NAVY_BG)
    c2 = E_SCALE.resize((340, 340)).rotate(6 * math.sin(g * 3), resample=Image.BICUBIC)
    paste_center(c, c2, W / 2, 880, alpha=ease(t / 0.15))
    punch(c, "al", "AGE LIMITS?", 540, 130, t, color=WHITE, stroke=6)

def s_apps(c, t, g):
    c.paste(NAVY_BG)
    label(c, "APPS LIKE", 560, 60, WHITE, t)
    for i, (tl, y) in enumerate(zip(TILES, (780, 1000))):
        lt = t - 0.1 - i * 0.3
        paste_center(c, tl, W / 2 + 600 * (1 - ease(lt / 0.3)), y, alpha=ease(lt / 0.1))

def s_yearend(c, t, g):
    date_card2(c, t, "31", "DEC 2026", "DECISION BY YEAR-END", (60, 30, 100))

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt16", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 900, *pop(t - 0.3))

def s_home(c, t, g):
    c.paste(PINK_BG)
    paste_center(c, E_HOUSE.resize((330, 330)), W / 2, 880, *pop(t))
    paste_center(c, stamp("TOO CLOSE TO HOME", 84, GOLD, -6), W / 2, 560, *pop(t - 0.2))

def s_gauge(c, t, g):
    c.paste(WARM_BG)
    punch(c, "hc", "HOW COOKED?", 470, 130, t, color=WHITE, stroke=6)
    gauge(c, t)
    paste_center(c, E_FIRE.resize((130, 130)), W / 2, 1200, *pop(t - 0.6))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun16", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 4), ST[1], at(1, 2), ST[2], at(2, 4), ST[3], at(3, 2), at(3, 5), ST[4], at(4, 4), ST[5], at(5, 4),
     ST[6], at(6, 3), at(6, 6), at(6, 9), ST[7], at(7, 4), at(7, 6), ST[8], at(8, 3), ST[9], ST[10], DUR + 0.1]
FNS = [s_hook, s_you, s_word, s_eq, s_hooked, s_bored, s_every, s_nov5, s_list, s_adults, s_dryer, s_nov10, s_doc,
       s_ages, s_baby, s_teen, s_noban, s_scale, s_apps, s_yearend, s_take, s_home, s_gauge, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "SLANG, NOT A DIAGNOSIS", None),
    (ST[3] + 0.1, ST[4] - 0.1, "c2", "JAPAN'S BUZZWORD AWARD", None),
    (ST[5], ST[6] - 0.1, "c3", "STILL A DRAFT", None),
    (ST[7], ST[8] - 0.1, "c4", "REPORTEDLY", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s016_{s}.png")
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
