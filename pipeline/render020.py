"""Live Lore Short 020 (The Weeknd's region-locked single "Hong Kong", sampling Faye Wong's 1993 Cantopop ballad
"Monsoon"; debuted live Oct 24 2026 at Kai Tak Stadium; Apple Music HK No. 1; Nov 12 video shot in Mong Kok;
label-reported NetEase first-day record) - reuses render.py.
Usage: python3 render020.py OUT.mp4 [start end]  |  python3 render020.py stills t1 t2 ...
All visuals drawn in code (generic neon signs, generic stadium bowl, generic cassette, vinyl, tickets, bar chart,
phone, karaoke screen, emoji, names as plain text; no photos, posters, cover art, logos, footage or audio samples).
No music.
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
SEG = json.load(open("segments020.json"))
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
JADE_BG = gradient((10, 60, 50), (2, 10, 8))
PURP_BG = gradient((50, 20, 90), (6, 3, 14))
NEON_BG = gradient((40, 8, 50), (4, 2, 10))
TEAL_BG = gradient((10, 50, 80), (2, 6, 12))
E_LOCK, E_ROCKET, E_HEAD, E_TICKET, E_NOTE, E_CAM, E_TROPHY, E_EARTH, E_SAUCE, E_PLAY = (emoji(ch, 150) for ch in
    ["🔒", "🚀", "🎧", "🎟️", "🎵", "📸", "🏆", "🌍", "🤫", "▶️"])
HK_SKY = r.skyline(7, 1500, (8, 10, 20, 255))
PINK, NEONB = (255, 70, 170), (80, 220, 255)

def neon(text, size, col, font_cjk=False):
    """Glowing neon-tube text (generic sign, not a logo)."""
    base = cjk(text, size, col + (255,)) if font_cjk else r.text_img(text, size, fill=col, weight="Bold", spacing=6)
    pad = 60
    im = Image.new("RGBA", (base.width + 2 * pad, base.height + 2 * pad), (0, 0, 0, 0))
    im.alpha_composite(base, (pad, pad))
    glow = im.filter(ImageFilter.GaussianBlur(22))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for _ in range(3):
        out.alpha_composite(glow)
    core = Image.new("RGBA", im.size, (0, 0, 0, 0))
    core.alpha_composite(base.point(lambda v: min(255, v + 0)), (pad, pad))
    out.alpha_composite(core)
    white = r.text_img(text, size, fill=(255, 255, 255), weight="Bold", spacing=6) if not font_cjk else cjk(text, size, (255, 255, 255, 255))
    w2 = Image.new("RGBA", im.size, (0, 0, 0, 0))
    w2.alpha_composite(white, (pad, pad))
    out = Image.blend(out, Image.alpha_composite(out, w2), 0.35)
    return out

def stadium(t, lit=4):
    w, h = 940, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([20, 120, w - 20, h - 20], fill=(40, 44, 70, 255))
    d.ellipse([110, 190, w - 110, h - 90], fill=(70, 150, 90, 255))
    d.ellipse([110, 190, w - 110, h - 90], outline=(230, 230, 230, 255), width=6)
    for i in range(60):  # crowd lights
        a = i / 60 * 2 * math.pi
        x = w / 2 + (w / 2 - 55) * math.cos(a)
        y = (h + 100) / 2 + ((h - 140) / 2 - 25) * math.sin(a)
        on = (math.sin(t * 6 + i * 1.3) > -0.3)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=((255, 240, 180, 255) if on else (90, 90, 120, 255)))
    for k in range(4):  # floodlight towers
        x = 120 + k * 233
        d.rectangle([x - 6, 0, x + 6, 130], fill=(120, 120, 140, 255))
        col = GOLD if k < lit else (80, 80, 90)
        d.rounded_rectangle([x - 40, 0, x + 40, 40], 8, fill=col + (255,))
    return im
STADIUM_IMG = {}

def ticket_img(col):
    w, h = 340, 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 18, fill=col + (255,))
    for y in (h // 2,):
        d.ellipse([-24, y - 24, 24, y + 24], fill=(0, 0, 0, 0))
        d.ellipse([w - 24, y - 24, w + 24, y + 24], fill=(0, 0, 0, 0))
    d.line([(250, 12), (250, h - 12)], fill=(255, 255, 255, 160), width=4)
    tx = r.text_img("ADMIT 1", 44, fill=DARK, weight="Black")
    im.alpha_composite(tx, (40, (h - tx.height) // 2))
    return im
TICKETS = [ticket_img(c) for c in (GOLD, PINK, NEONB, (255, 160, 60))]

def vinyl(g):
    s = 720
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s, s], fill=(18, 18, 22, 255))
    for k in range(8):
        rr = 340 - k * 26
        d.ellipse([s / 2 - rr, s / 2 - rr, s / 2 + rr, s / 2 + rr], outline=(45, 45, 55, 255), width=3)
    d.ellipse([s / 2 - 120, s / 2 - 120, s / 2 + 120, s / 2 + 120], fill=PINK + (255,))
    d.ellipse([s / 2 - 14, s / 2 - 14, s / 2 + 14, s / 2 + 14], fill=(10, 10, 12, 255))
    d.pieslice([30, 30, s - 30, s - 30], -70, -50, fill=(255, 255, 255, 40))
    return im.rotate(-g * 120 % 360, resample=Image.BICUBIC)

def cassette():
    w, h = 820, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(235, 225, 205, 255))
    d.rounded_rectangle([50, 40, w - 50, 300], 18, fill=(255, 250, 240, 255))
    d.rectangle([50, 110, w - 50, 140], fill=PINK + (255,))
    lab = cjk("季候風", 110, DARK + (255,))
    im.alpha_composite(lab, ((w - lab.width) // 2, 150))
    yr = r.text_img("1993", 64, fill=PINK)
    im.alpha_composite(yr, (w - 50 - yr.width - 20, 46))
    d.rounded_rectangle([180, 330, w - 180, 470], 60, fill=(60, 55, 50, 255))
    for x in (290, w - 290):
        d.ellipse([x - 50, 350, x + 50, 450], fill=(240, 240, 240, 255))
        d.ellipse([x - 22, 378, x + 22, 422], fill=(60, 55, 50, 255))
    return im
CASSETTE = cassette()

def chart(t, labels=("#5", "#4", "#3", "#2", "#1"), heights=(0.35, 0.45, 0.55, 0.68, 1.0)):
    w, h = 900, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bw = 130
    for i, (lb, hh) in enumerate(zip(labels, heights)):
        k = ease((t - i * 0.08) / 0.4)
        x = 60 + i * 170
        top = h - 120 - (h - 220) * hh * k
        col = GOLD if i == len(labels) - 1 else (90, 110, 170)
        d.rounded_rectangle([x, top, x + bw, h - 120], 16, fill=col + (255,))
        tx = r.text_img(lb, 54, fill=WHITE)
        im.alpha_composite(tx, (int(x + (bw - tx.width) / 2), h - 100))
    d.line([(30, h - 120), (w - 30, h - 120)], fill=(200, 200, 220, 255), width=6)
    return im

def phone(t, inner):
    w, h = 520, 980
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 70, fill=(20, 20, 26, 255))
    d.rounded_rectangle([22, 22, w - 22, h - 22], 54, fill=(245, 245, 250, 255))
    d.rounded_rectangle([w / 2 - 70, 40, w / 2 + 70, 72], 16, fill=(20, 20, 26, 255))
    im.alpha_composite(inner, ((w - inner.width) // 2, (h - inner.height) // 2))
    return im

def screen_lock():
    im = Image.new("RGBA", (440, 700), (0, 0, 0, 0))
    lk = E_LOCK.resize((240, 240))
    im.alpha_composite(lk, ((440 - 240) // 2, 120))
    tx = r.text_img("NOT AVAILABLE", 46, fill=(200, 40, 60))
    im.alpha_composite(tx, ((440 - tx.width) // 2, 420))
    tx2 = r.text_img("IN YOUR REGION", 40, fill=(90, 90, 100), weight="Bold")
    im.alpha_composite(tx2, ((440 - tx2.width) // 2, 490))
    return im
PHONE_LOCK = phone(0, screen_lock())

def mongkok(g):
    """Generic stacked neon street signs."""
    im = Image.new("RGBA", (W, 1100), (0, 0, 0, 0))
    signs = [("旺角", PINK, 150, 120, 80), ("MONG KOK", NEONB, 110, 560, 220), ("卡拉OK", GOLD, 120, 140, 520),
             ("NOODLES", (120, 255, 140), 80, 600, 700), ("夜", PINK, 180, 820, 420)]
    for i, (tx, col, sz, x, y) in enumerate(signs):
        flick = 1.0 if math.sin(g * 7 + i * 2.1) > -0.85 else 0.35
        n = neon(tx, sz, col, font_cjk=any(ord(ch) > 0x3000 for ch in tx))
        if flick < 1:
            n.putalpha(n.getchannel("A").point(lambda v: int(v * flick)))
        im.alpha_composite(n, (int(x - n.width / 2 + 100), int(y)))
    return im

def karaoke(t):
    w, h = 940, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(20, 22, 60, 255))
    d.rounded_rectangle([0, 0, w, h], 30, outline=(120, 130, 220, 255), width=8)
    line = "LA LA LA..."
    base = r.text_img(line, 100, fill=WHITE, weight="Black")
    hi = r.text_img(line, 100, fill=PINK, weight="Black")
    x0, y0 = (w - base.width) // 2, 220
    im.alpha_composite(base, (x0, y0))
    k = ease(t / 2.2)
    cw = int(hi.width * k)
    if cw > 0:
        im.alpha_composite(hi.crop((0, 0, cw, hi.height)), (x0, y0))
    return im

def big_num(c, key, text, cy, size, t, col=GOLD):
    punch(c, key, text, cy, size, t, color=col, stroke=8)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(NEON_BG)
    c.alpha_composite(HK_SKY, (-100, 200))
    paste_center(c, neon("HONG KONG", 135, PINK), W / 2, 700, scale=1.0 + 0.03 * t, alpha=ease(t / 0.08))
    for i in range(3):
        paste_center(c, E_NOTE.resize((120, 120)), 200 + i * 340, 1130 + 30 * math.sin(g * 5 + i), *pop(t - 0.2 - i * 0.1))
    punch(c, "hk_q", "ONLY IN ASIA?!", 920, 110, t - 0.15, color=WHITE, stroke=7)

def s_lock(c, t, g):
    c.paste(RED_BG)
    paste_center(c, PHONE_LOCK, W / 2, 930, scale=0.85 + 0.03 * t, alpha=ease(t / 0.1))
    if t > 0.5:
        paste_center(c, stamp("ASIA ONLY", 110, GOLD, -8), W / 2, 1180, *pop(t - 0.5))

def s_date24(c, t, g):
    date_card2(c, t, "24", "OCT 2026", "KAI TAK STADIUM", (110, 30, 90))

def s_stadium(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g)
    lit = min(4, 1 + int(t / 0.45))
    paste_center(c, stadium(g, lit), W / 2, 950, scale=1.0, alpha=ease(t / 0.1))
    punch(c, f"4n{lit}", f"NIGHT {lit} / 4", 560, 110, t, color=WHITE, stroke=6)
    if t > 1.4:
        paste_center(c, stamp("SOLD OUT", 110, (255, 90, 90), -7), W / 2, 1240, *pop(t - 1.4))

def s_tickets(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150),))
    rnd = random.Random(20)
    for i in range(9):
        x = rnd.uniform(60, W - 60)
        sp = rnd.uniform(500, 800)
        y = -200 + ((t * sp + rnd.uniform(0, 1700)) % 1900)
        tk = TICKETS[i % 4].rotate(rnd.uniform(-30, 30) + g * 20 * (1 if i % 2 else -1), expand=True, resample=Image.BICUBIC)
        paste_center(c, tk, x, y, scale=0.8)
    n = int(179547 * ease(t / 1.6)) if t < 1.6 else 180000
    big_num(c, f"tk{n}", f"~{n:,}" if t >= 1.6 else f"{n:,}", 860, 190, 1.0)
    label(c, "TICKETS · REPORTEDLY", 1050, 56, WHITE, t - 0.2)

def s_nocap(c, t, g):
    c.paste(RED_BG)
    paste_center(c, E_FIRE.resize((300, 300)), W / 2, 820, *pop(t))
    if t > 0.2:
        paste_center(c, stamp("NO CAP", 140, GOLD, -6), W / 2, 1160, *pop(t - 0.2))

def s_sauce(c, t, g):
    c.paste(PURP_BG); spotlights(c, g, ((255, 70, 170), (120, 200, 255)))
    paste_center(c, vinyl(g), W / 2, 920, scale=0.9 + 0.05 * ease(t / 0.4), alpha=ease(t / 0.1))
    paste_center(c, E_SAUCE.resize((200, 200)), W / 2 + 330, 640, *pop(t - 0.3))
    punch(c, "sauce", "THE SAMPLE", 500, 120, t, color=WHITE, stroke=6)

def s_cassette(c, t, g):
    c.paste(gradient((120, 40, 80), (14, 4, 10)))
    paste_center(c, CASSETTE, W / 2, 900, scale=0.95 + 0.02 * math.sin(g * 3), alpha=ease(t / 0.1))
    punch(c, "mon", "\"MONSOON\"", 520, 130, t - 0.15, color=WHITE, stroke=7)
    label(c, "CANTOPOP · 1993", 1260, 64, GOLD, t - 0.3)

def s_faye(c, t, g):
    c.paste(TEAL_BG); spotlights(c, g, ((255, 230, 150), (120, 200, 255), (255, 70, 170)))
    paste_center(c, E_MIC.resize((300, 300)), W / 2, 960, *pop(t))
    punch(c, "fw", "FAYE WONG", 560, 160, t - 0.1, color=GOLD, stroke=8)

def s_chungking(c, t, g):
    c.paste(NEON_BG)
    c.alpha_composite(HK_SKY, (-60, 300))
    paste_center(c, neon("CHUNGKING", 130, NEONB), W / 2, 760, alpha=ease(t / 0.1))
    paste_center(c, neon("EXPRESS", 130, PINK), W / 2, 960, alpha=ease((t - 0.25) / 0.1))
    label(c, "1994 FILM ICON", 1180, 60, WHITE, t - 0.4)

def s_date31(c, t, g):
    date_card2(c, t, "31", "OCT 2026", "PARTS OF ASIA ONLY", (20, 90, 110))

def s_chart(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g, ((255, 230, 150),))
    paste_center(c, chart(t), W / 2, 960, alpha=ease(t / 0.1))
    punch(c, "n1", "NO. 1 IN HK", 480, 130, t - 0.2, color=GOLD, stroke=7)
    if t > 0.8:
        paste_center(c, E_TROPHY.resize((140, 140)), W / 2 + 280, 640, *pop(t - 0.8))

def s_date12(c, t, g):
    c.paste(gradient((60, 20, 20), (8, 3, 3)))
    w, h = 880, 500
    scr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(scr)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(15, 15, 18, 255))
    d.rounded_rectangle([0, 0, w, h], 30, outline=(80, 80, 90, 255), width=6)
    d.rectangle([30, h - 50, 30 + (w - 60) * ease(t / 2), h - 38], fill=(230, 50, 50, 255))
    scr.alpha_composite(E_PLAY.resize((200, 200)), ((w - 200) // 2, (h - 200) // 2 - 20))
    paste_center(c, scr, W / 2, 900, *pop(t))
    punch(c, "nov12", "NOV 12", 520, 150, t - 0.1, color=WHITE, stroke=7)
    label(c, "THE MUSIC VIDEO", 1230, 60, GOLD, t - 0.3)

def s_model(c, t, g):
    c.paste(gradient((30, 30, 36), (4, 4, 6)))
    rnd = random.Random(int(g * 6))
    for i in range(5):  # camera flashes
        if rnd.random() < 0.5:
            x, y = rnd.uniform(100, W - 100), rnd.uniform(500, 1200)
            fl = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
            ImageDraw.Draw(fl).ellipse([0, 0, 300, 300], fill=(255, 255, 255, 140))
            paste_center(c, fl.filter(ImageFilter.GaussianBlur(40)), x, y)
    # runway
    ImageDraw.Draw(c).polygon([(W / 2 - 60, 600), (W / 2 + 60, 600), (W / 2 + 420, 1300), (W / 2 - 420, 1300)], fill=(70, 70, 80, 255))
    paste_center(c, E_CAM.resize((170, 170)), 190, 760, *pop(t - 0.1))
    paste_center(c, E_CAM.resize((170, 170)).transpose(Image.FLIP_LEFT_RIGHT), W - 190, 760, *pop(t - 0.2))
    punch(c, "mx", "MING XI", 960, 170, t - 0.15, color=WHITE, stroke=8)
    label(c, "SUPERMODEL CO-STAR", 1140, 56, GOLD, t - 0.3)

def s_mongkok(c, t, g):
    c.paste(NEON_BG)
    c.alpha_composite(HK_SKY, (-100 + int(50 * ease(t / 2)), 250))
    c.alpha_composite(mongkok(g), (0, 380 - int(40 * ease(t / 2))))

def s_karaoke(c, t, g):
    c.paste(PURP_BG); spotlights(c, g, ((255, 70, 170), (80, 220, 255)))
    paste_center(c, karaoke(t), W / 2, 900, *pop(t))
    paste_center(c, E_MIC.resize((200, 200)), W / 2 + 360, 1200, *pop(t - 0.3))

def s_china(c, t, g):
    c.paste(RED_BG)
    paste_center(c, E_HEAD.resize((320, 320)), W / 2, 900, *pop(t))
    punch(c, "mc", "MAINLAND CHINA", 560, 110, t - 0.1, color=GOLD, stroke=6)

def s_day1(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g, ((255, 230, 150),))
    paste_center(c, chart(t, ("", "", "", "", "DAY 1"), (0.3, 0.4, 0.35, 0.45, 1.0)), W / 2, 1000)
    # gold bar: relabel
    if t > 0.5:
        paste_center(c, E_ROCKET.resize((150, 150)), W / 2 + 330, 760 - 40 * ease((t - 0.5) / 0.6), *pop(t - 0.5))
    punch(c, "bd1", "BIGGEST DAY 1", 460, 120, t - 0.1, color=WHITE, stroke=6)
    label(c, "PER UNIVERSAL MUSIC", 570, 50, GOLD, t - 0.3)

def s_five(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g)
    big_num(c, "5y", "5 YEARS", 860, 220, t)
    label(c, "NON-MANDARIN SONG RECORD", 1080, 54, WHITE, t - 0.25)

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt20", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    c.alpha_composite(HK_SKY, (-100, 160))

def s_w(c, t, g):
    c.paste(TEAL_BG); spotlights(c, g)
    paste_center(c, neon("W", 520, GOLD), W / 2, 820, *pop(t))
    label(c, "FOR CANTOPOP", 1180, 80, WHITE, t - 0.2)

def s_q(c, t, g):
    c.paste(gradient((20, 70, 110), (3, 8, 14)))
    paste_center(c, E_EARTH.resize((380, 380)).rotate(-g * 30 % 360, resample=Image.BICUBIC), W / 2, 920, *pop(t))
    paste_center(c, E_THINK.resize((200, 200)), W / 2 + 290, 690, *pop(t - 0.2))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun20", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 4), ST[1], at(1, 3), ST[2], at(2, 5), ST[3], at(3, 3), at(3, 7), at(3, 10), ST[4], at(4, 4),
     ST[5], at(5, 3), at(5, 7), at(5, 11), ST[6], at(6, 3), at(6, 8), ST[7], at(7, 4), ST[8], ST[9], DUR + 0.1]
FNS = [s_hook, s_lock, s_date24, s_stadium, s_tickets, s_nocap, s_sauce, s_cassette, s_faye, s_chungking, s_date31,
       s_chart, s_date12, s_model, s_mongkok, s_karaoke, s_china, s_day1, s_five, s_take, s_w, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (0.1, ST[1] - 0.1, "c1", "THE WEEKND × FAYE WONG", None),
    (ST[1] + 0.1, ST[2] - 0.1, "c2", "4 NIGHTS AT KAI TAK", None),
    (at(3, 7), ST[4] - 0.1, "c3", "A 1993 CANTOPOP CLASSIC", None),
    (at(6, 3), ST[7] - 0.1, "c4", "NETEASE CLOUD MUSIC", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s020_{s}.png")
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
