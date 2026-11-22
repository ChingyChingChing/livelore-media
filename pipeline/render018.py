"""Live Lore Short 018 (The Game Awards 2026 nominees: GTA VI leads with 8 nominations two days before launch;
Phantom Blade Zero from Beijing studio S-Game is one of six Game of the Year nominees) - reuses render.py.
Usage: python3 render018.py OUT.mp4 [start end]  |  python3 render018.py stills t1 t2 ...
All visuals drawn in code (generic star trophies, a generic sword, generic console/PC shapes, a generic city grid,
calendar cards, emoji; game, studio and show names as plain text only; no logos, key art, screenshots or trailers). No music.
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
SEG = json.load(open("segments018.json"))
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


NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
MAGENTA = (255, 70, 160)
GOLD_BG = gradient((90, 60, 10), (10, 6, 2))
INK_BG = gradient((40, 8, 10), (6, 2, 2))          # dark red ink for the kung-fu scenes
JADE_BG = gradient((10, 60, 50), (2, 10, 8))
PURP_BG = gradient((50, 20, 90), (6, 3, 14))
SUN_BG = gradient((120, 50, 20), (14, 6, 4))
TROPHY = r.AWARD
TROPHY_S = TROPHY.resize((156, 192), Image.LANCZOS)
E_LOCK, E_ROCKET, E_X, E_CLOCK, E_SCALE, E_STAR, E_TV, E_PC = (emoji(ch, 150) for ch in ["🔒", "🚀", "❌", "⏱️", "⚖️", "⭐", "📺", "💻"])
E_GAME = emoji("🎮", 150)

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
    hd = r.text_img(head, 58, fill=WHITE, weight="ExtraBold", spacing=4)
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
C_GTA = card("GOTY NOMINEE", "GTA VI", (40, 120, 200), "8 NOMINATIONS")
C_PBZ = card("GOTY NOMINEE", "PHANTOM BLADE ZERO", RED, "5 NOMINATIONS")
C_RE = card("GOTY NOMINEE", "RESIDENT EVIL REQUIEM", (90, 90, 100))
C_OOT = card("GOTY NOMINEE", "OCARINA OF TIME", GREEN, "REMAKE")
C_WK = card("GOTY 2024", "BLACK MYTH: WUKONG", (150, 100, 20), "NOMINATED")

def blade(t):
    """Original generic straight sword (jian) drawn from shapes."""
    w, h = 220, 1000
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w / 2, 0), (w / 2 + 34, 90), (w / 2 + 34, 700), (w / 2 - 34, 700), (w / 2 - 34, 90)], fill=(220, 228, 238, 255))
    d.line([(w / 2, 40), (w / 2, 690)], fill=(160, 170, 190, 255), width=6)
    d.rounded_rectangle([10, 700, w - 10, 740], 14, fill=GOLD + (255,))
    d.rounded_rectangle([w / 2 - 24, 740, w / 2 + 24, 930], 10, fill=(90, 30, 30, 255))
    d.ellipse([w / 2 - 40, 920, w / 2 + 40, 1000], fill=GOLD + (255,))
    sh = int((t * 0.7 % 1) * 700)
    d.line([(w / 2 + 20, sh), (w / 2 + 20, sh + 90)], fill=(255, 255, 255, 200), width=10)
    return im

def ink_strokes(c, g):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(5):
        y = 420 + i * 220 + 30 * math.sin(g * 1.3 + i)
        d.line([(-50, y), (W + 50, y - 160)], fill=(0, 0, 0, 90), width=70)
    c.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))

def city_map(t):
    w, h = 880, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=(235, 228, 210, 255))
    for k in range(1, 5):   # generic ring-road grid
        m = k * 80
        d.rounded_rectangle([w / 2 - m * 1.2, h / 2 - m, w / 2 + m * 1.2, h / 2 + m], 30, outline=(190, 175, 150, 255), width=8)
    d.line([(0, h / 2), (w, h / 2)], fill=(190, 175, 150, 255), width=8)
    d.line([(w / 2, 0), (w / 2, h)], fill=(190, 175, 150, 255), width=8)
    lb = r.text_img("BEIJING", 84, fill=DARK)
    im.alpha_composite(lb, ((w - lb.width) // 2, h - 140))
    return im

def device(kind):
    w, h = 380, 300
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "pc":
        d.rounded_rectangle([20, 10, w - 20, 220], 18, fill=(40, 44, 60, 255))
        d.rounded_rectangle([40, 30, w - 40, 200], 10, fill=(80, 140, 220, 255))
        d.rectangle([w / 2 - 20, 220, w / 2 + 20, 260], fill=(40, 44, 60, 255))
        d.rounded_rectangle([w / 2 - 100, 255, w / 2 + 100, 280], 10, fill=(40, 44, 60, 255))
    else:   # generic console tower
        d.rounded_rectangle([w / 2 - 60, 10, w / 2 + 60, 280], 30, fill=(240, 240, 245, 255))
        d.rounded_rectangle([w / 2 - 22, 20, w / 2 + 22, 270], 14, fill=(30, 30, 40, 255))
    return im
DEV_PC, DEV_CON = device("pc"), device("con")

def slot_grid(t, hi=None):
    im = Image.new("RGBA", (900, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(6):
        x, y = (i % 3) * 300, (i // 3) * 320
        k = ease((t - i * 0.08) / 0.2)
        if k <= 0:
            continue
        fill = (RED if i == hi else (60, 60, 80)) + (255,)
        d.rounded_rectangle([x + 10, y + 10, x + 290, y + 310], 26, fill=fill, outline=GOLD + (255,), width=6)
        n = r.text_img(str(i + 1), 120, fill=WHITE)
        im.alpha_composite(n, (x + 150 - n.width // 2, y + 160 - n.height // 2))
    return im

def counter(t, target=4000000):
    v = int(target * ease(t / 1.2))
    return r.text_img(f"{v:,}", 150, fill=GOLD, stroke=6)

def year_box(year, col=RED):
    w, h = 420, 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(250, 246, 238, 255))
    d.rounded_rectangle([0, 0, w, 110], 30, fill=col + (255,))
    d.rectangle([0, 80, w, 110], fill=col + (255,))
    y = r.text_img(year, 70, fill=WHITE, weight="ExtraBold")
    im.alpha_composite(y, ((w - y.width) // 2, 18))
    return im

def tag(text, col, w=700):
    im = Image.new("RGBA", (w, 170), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w, 170], 30, fill=col + (255,))
    tx = r.text_img(text, 84, fill=WHITE)
    im.alpha_composite(tx, ((w - tx.width) // 2, (170 - tx.height) // 2))
    return im
TAG_LOST = tag("DIDN'T WIN", (90, 90, 100))

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g)
    paste_center(c, TROPHY, W / 2, 1020, scale=0.8 + 0.04 * math.sin(g * 4), alpha=ease(t / 0.15))
    sc = 1.0 + 0.8 * (1 - ease(t / 0.3)) + 0.03 * t
    paste_center(c, T("x8", "8", 380, fill=GOLD, stroke=10), W / 2, 560, scale=sc, alpha=ease(t / 0.1))

def s_row(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150), (255, 200, 120)))
    for i in range(8):
        paste_center(c, TROPHY_S, 170 + (i % 4) * 247, 720 + (i // 4) * 300, *pop(t - i * 0.1, 0.2))
    label(c, "GTA VI · THE GAME AWARDS 2026", 1250, 52, WHITE, t)

def s_lock(c, t, g):
    c.paste(PURP_BG)
    paste_center(c, E_GAME.resize((420, 420)), W / 2, 880, alpha=ease(t / 0.15))
    if t > 0.3:
        paste_center(c, E_LOCK.resize((220, 220)), W / 2 + 180, 1020, *pop(t - 0.3))
    if t > 0.6:
        paste_center(c, stamp("NOT OUT YET", 96, MAGENTA, -7), W / 2, 580, *pop(t - 0.6))

def s_d17(c, t, g):
    date_card2(c, t, "17", "NOV 2026", "NOMINEES ANNOUNCED", (30, 40, 110))

def s_d19(c, t, g):
    date_card2(c, t, "19", "NOV 2026", "GTA VI LAUNCH DAY", (30, 90, 120))
    if t > 0.4:
        paste_center(c, stamp("+2 DAYS", 90, GOLD, -6), W / 2, 1215, *pop(t - 0.4))

def s_eyes(c, t, g):
    c.paste(INK_BG); ink_strokes(c, g)
    paste_center(c, E_EYES.resize((300, 300)), W / 2, 850, *pop(t))
    punch(c, "watch", "THE ONE TO WATCH", 560, 96, t, color=WHITE, stroke=6)

def s_blade(c, t, g):
    c.paste(INK_BG); ink_strokes(c, g)
    ang = -35 + 10 * ease(t / 0.4)
    paste_center(c, blade(g).rotate(ang, expand=True, resample=Image.BICUBIC), W / 2, 870, scale=0.85, alpha=ease(t / 0.12))
    punch(c, "pbz", "PHANTOM BLADE ZERO", 560, 78, t, color=WHITE, stroke=7)
    label(c, "KUNG-FU ACTION RPG", 1300, 56, GOLD, t - 0.3)

def s_beijing(c, t, g):
    c.paste(JADE_BG)
    paste_center(c, city_map(t), W / 2, 860, scale=0.9 + 0.04 * ease(t / 0.5), alpha=ease(t / 0.12))
    paste_center(c, E_PIN.resize((170, 170)), W / 2, 760 + 14 * math.sin(g * 5), *pop(t - 0.2))
    if t > 0.5:
        paste_center(c, pill("S-GAME", 80, GOLD), W / 2, 1060, *pop(t - 0.5))

def s_d29(c, t, g):
    date_card2(c, t, "29", "OCT 2026", "LAUNCH DAY", (110, 25, 30))

def s_dev(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, DEV_CON, W * 0.3, 880, *pop(t))
    paste_center(c, DEV_PC, W * 0.68, 900, *pop(t - 0.15))
    label(c, "PS5 + PC", 1180, 80, WHITE, t - 0.2)

def s_rocket(c, t, g):
    c.paste(SUN_BG); spotlights(c, g, ((255, 200, 120),))
    paste_center(c, E_ROCKET.resize((340, 340)), W / 2 + 40 * math.sin(g * 9), 1150 - 380 * ease(t / 1.0), alpha=ease(t / 0.12))
    punch(c, "bl", "BIG LEAGUES", 560, 130, t, color=WHITE, stroke=6)

def s_grid(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150), (255, 230, 150)))
    paste_center(c, slot_grid(t, hi=1 if t > 0.9 else None), W / 2, 900)
    punch(c, "goty", "GAME OF THE YEAR", 520, 96, t, color=WHITE, stroke=6)

def slide(c, t, crd, bg):
    c.paste(bg)
    paste_center(c, crd, W / 2 + 700 * (1 - ease(t / 0.3)), 880, alpha=ease(t / 0.1))

def s_gta(c, t, g): slide(c, t, C_GTA, NAVY_BG)
def s_re(c, t, g): slide(c, t, C_RE, gradient((40, 40, 48), (5, 5, 8)))
def s_oot(c, t, g): slide(c, t, C_OOT, JADE_BG)

def s_five(c, t, g):
    c.paste(INK_BG); ink_strokes(c, g)
    paste_center(c, C_PBZ, W / 2, 760, *pop(t))
    for i in range(5):
        paste_center(c, E_STAR.resize((120, 120)), 220 + i * 160, 1180, *pop(t - 0.3 - i * 0.1))

def s_sold(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150),))
    paste_center(c, counter(t), W / 2, 760, alpha=ease(t / 0.1))
    label(c, "COPIES SOLD", 950, 80, WHITE, t - 0.2)
    paste_center(c, E_GAME.resize((200, 200)), W / 2, 1170, *pop(t - 0.4))

def s_72(c, t, g):
    c.paste(SUN_BG)
    paste_center(c, E_CLOCK.resize((300, 300)), W / 2, 760, *pop(t))
    label(c, "72 HOURS", 1000, 110, WHITE, t - 0.1)
    if t > 0.7:
        paste_center(c, stamp("BIG W", 120, GOLD, -7), W / 2, 1220, *pop(t - 0.7))

def s_2024(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, year_box("2024", (150, 100, 20)), W / 2, 820, *pop(t))
    paste_center(c, TROPHY.resize((180, 222)), W / 2, 880, *pop(t - 0.2))

def s_wukong(c, t, g):
    c.paste(gradient((60, 40, 10), (6, 4, 2)))
    paste_center(c, C_WK, W / 2, 740, *pop(t))
    paste_center(c, TAG_LOST, W / 2, 1170, *pop(t - 0.5))
    if t > 0.8:
        paste_center(c, E_X.resize((130, 130)), W / 2 + 390, 1170, *pop(t - 0.8))

def s_first(c, t, g):
    c.paste(INK_BG); ink_strokes(c, g); spotlights(c, g, ((255, 230, 150),))
    paste_center(c, TROPHY, W / 2, 960, scale=0.75 + 0.05 * ease(t / 0.4), alpha=ease(t / 0.15))
    punch(c, "first", "A FIRST?", 540, 170, t, color=GOLD, stroke=7)

def s_d10(c, t, g):
    date_card2(c, t, "10", "DEC 2026", "WINNERS · LOS ANGELES", (90, 60, 10))

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt18", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 900, *pop(t - 0.3))

def s_scale(c, t, g):
    c.paste(PURP_BG)
    paste_center(c, E_SCALE.resize((360, 360)).rotate(8 * math.sin(g * 3), resample=Image.BICUBIC), W / 2, 920, *pop(t))
    paste_center(c, pill("FAVORITE: GTA VI", 66, GOLD), W / 2, 600, *pop(t - 0.15))
    if t > 0.9:
        paste_center(c, pill("UNDERDOG: PBZ", 66, (255, 120, 120)), W / 2, 1200, *pop(t - 0.9))

def s_flex(c, t, g):
    c.paste(INK_BG); ink_strokes(c, g)
    paste_center(c, slot_grid(9, hi=1), W / 2, 900, scale=0.8)
    if t > 0.3:
        paste_center(c, stamp("FINAL 6 = FLEX", 92, GOLD, -6), W / 2, 560, *pop(t - 0.3))

def s_q(c, t, g):
    c.paste(gradient((90, 40, 20), (10, 4, 2)))
    paste_center(c, C_GTA.resize((500, 311)), W * 0.33, 820, *pop(t))
    paste_center(c, C_PBZ.resize((500, 311)), W * 0.67, 1110, *pop(t - 0.2))
    punch(c, "vs", "VS", 960, 140, t - 0.3, color=GOLD, stroke=8)
    paste_center(c, E_THINK.resize((200, 200)), W / 2, 560, *pop(t - 0.1))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun18", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 1), at(0, 4), ST[1], at(1, 2), ST[2], at(2, 2), at(2, 5), ST[3], at(3, 2), at(3, 3), ST[4],
     at(4, 3), at(4, 5), at(4, 7), ST[5], at(5, 2), at(5, 6), ST[6], at(6, 2), at(6, 4), ST[7], ST[8], at(8, 1),
     at(8, 6), ST[9], ST[10], DUR + 0.1]
FNS = [s_hook, s_row, s_lock, s_d17, s_d19, s_eyes, s_blade, s_beijing, s_d29, s_dev, s_rocket, s_grid, s_gta, s_re,
       s_oot, s_five, s_sold, s_72, s_2024, s_wukong, s_first, s_d10, s_take, s_scale, s_flex, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (at(0, 2), ST[1] - 0.1, "c1", "MOST OF ANY GAME", None),
    (at(2, 5), ST[3] - 0.1, "c2", "BEIJING, CHINA", None),
    (at(5, 2), ST[6] - 0.1, "c3", "PER THE STUDIO", None),
    (ST[7] + 0.05, ST[8] - 0.1, "c4", "THE GAME AWARDS 2026", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s018_{s}.png")
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
