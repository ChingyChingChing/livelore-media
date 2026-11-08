"""Live Lore Short 001 — original motion graphics rendered frame by frame, piped to ffmpeg.
Usage: python3 render.py OUT.mp4 [start_s end_s]   (optional range for quick previews)
All visuals are drawn here (shapes + Inter / Noto Color Emoji fonts). No footage, stills, logos or music.
"""
import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timing import captions

W, H, FPS = 1080, 1920, 30
AUDIO = "in/vo.m4a"
DUR = 55.02
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
NAVY, GOLD, ICE, WHITE = (8, 12, 24), (232, 178, 74), (120, 190, 255), (255, 255, 255)

_fonts = {}
def font(size, weight="Black"):
    k = (size, weight)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(INTER.format(weight), size)
    return _fonts[k]

def ease(x):  # easeOutCubic, clamped
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

# ---------- reusable layers ----------
def gradient(top, bottom, w=W, h=H):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(a, w, axis=1).astype(np.uint8))

VIGNETTE = None
def vignette():
    global VIGNETTE
    if VIGNETTE is None:
        y, x = np.ogrid[:H, :W]
        d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
        VIGNETTE = np.clip(1.15 - d * 0.75, 0.25, 1.0)[..., None].astype(np.float32)
    return VIGNETTE

rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 7, (H // 2, W // 2, 1)).astype(np.float32) for _ in range(6)]

def clouds(seed, tint, w=W + 200, h=H + 200):
    r = np.random.default_rng(seed)
    img = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(70):
        x, y = r.integers(-200, w), r.integers(-100, int(h * 0.75))
        rad = r.integers(120, 380)
        k = r.uniform(0.25, 0.6); c = tuple(int(v * k) for v in tint)
        d.ellipse([x - rad, y - rad * 0.55, x + rad, y + rad * 0.55], fill=c)
    return img.filter(ImageFilter.GaussianBlur(60))

def skyline(seed, base_y, color, w=W + 200, modern=True):
    r = random.Random(seed)
    img = Image.new("RGBA", (w, H + 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = -20
    while x < w:
        bw = r.randint(50, 140) if modern else r.randint(70, 160)
        bh = r.randint(160, 620) if modern else r.randint(60, 190)
        d.rectangle([x, base_y - bh, x + bw, H + 200], fill=color)
        if not modern:  # low pitched roofs + utility poles for postwar streets
            d.polygon([(x - 12, base_y - bh), (x + bw / 2, base_y - bh - 55), (x + bw + 12, base_y - bh)], fill=color)
            if r.random() < 0.35:
                d.rectangle([x + bw - 6, base_y - bh - 260, x + bw, base_y], fill=color)
                d.line([(x + bw - 40, base_y - bh - 230), (x + bw + 34, base_y - bh - 230)], fill=color, width=5)
        elif r.random() < 0.5:
            for wy in range(base_y - bh + 25, base_y - 20, 38):
                for wx in range(x + 12, x + bw - 12, 26):
                    if r.random() < 0.18:
                        d.rectangle([wx, wy, wx + 9, wy + 14], fill=(255, 205, 120, 150))
        x += bw + r.randint(-10, 12)
    return img

def kaiju(scale=1.0, color=(4, 6, 12, 255)):
    """Generic hulking reptile silhouette (original shape, no franchise design)."""
    S = 900
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = [(300, 900), (260, 640), (280, 470), (330, 360), (380, 300), (430, 250), (470, 215), (520, 210),
            (560, 235), (575, 275), (545, 300), (520, 330), (560, 380), (610, 470), (640, 600), (700, 700),
            (820, 760), (900, 800), (900, 850), (720, 830), (640, 800), (620, 900)]
    d.polygon(body, fill=color)
    for i in range(7):  # rough back ridges
        bx, by = 300 + i * 14, 640 - i * 62
        d.polygon([(bx, by), (bx - 70 + i * 4, by - 40), (bx + 10, by - 70)], fill=color)
    d.polygon([(470, 215), (420, 150), (500, 205)], fill=color)
    img = img.resize((int(S * scale), int(S * scale)), Image.LANCZOS)
    return img

def dragon3(color=(6, 6, 10, 255)):
    """Original generic three-headed winged dragon silhouette."""
    Wd, Hd = 1100, 1000
    img = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 550, 640
    d.ellipse([cx - 150, cy - 110, cx + 150, cy + 170], fill=color)
    for side in (-1, 1):  # wings
        pts = [(cx + side * 80, cy - 40), (cx + side * 330, cy - 300), (cx + side * 540, cy - 230),
               (cx + side * 470, cy - 120), (cx + side * 520, cy - 40), (cx + side * 400, cy + 10),
               (cx + side * 430, cy + 90), (cx + side * 120, cy + 60)]
        d.polygon(pts, fill=color)
    for k, ang in enumerate((-35, 0, 35)):  # three necks
        a = math.radians(ang)
        prev = (cx, cy - 60)
        for s in range(1, 12):
            t = s / 11
            px = cx + math.sin(a) * 260 * t + math.sin(t * 5 + k) * 22
            py = cy - 60 - 430 * t
            d.line([prev, (px, py)], fill=color, width=int(70 - 34 * t))
            prev = (px, py)
        hx, hy = prev
        d.ellipse([hx - 42, hy - 30, hx + 42, hy + 30], fill=color)
        dirx = 1 if ang >= 0 else -1
        d.polygon([(hx, hy - 20), (hx + dirx * 95, hy + 8), (hx, hy + 26)], fill=color)
        d.polygon([(hx - 10, hy - 25), (hx - dirx * 30 - 5, hy - 85), (hx + 12, hy - 28)], fill=color)
    d.line([(cx + 60, cy + 150), (cx + 260, cy + 290), (cx + 420, cy + 300)], fill=color, width=40)
    return img

def award(color=GOLD):
    """Original generic gold star award on a plinth (not the Academy statuette)."""
    img = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, R, r = 260, 230, 210, 88
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    d.polygon(pts, fill=color)
    d.rectangle([215, 430, 305, 500], fill=color)
    d.rectangle([130, 500, 390, 600], fill=(170, 120, 40))
    return img

def eyes_emoji(size=110):
    try:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), "👀", font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        return im.resize((int(size * im.width / im.height), size), Image.LANCZOS)
    except Exception:
        return None

def text_img(text, size, fill=WHITE, weight="Black", stroke=0, stroke_fill=(0, 0, 0), spacing=0, emoji=None):
    f = font(size, weight)
    widths = [f.getlength(ch) + spacing for ch in text]
    tw = int(sum(widths)) + stroke * 2 + 4
    asc, desc = f.getmetrics()
    th = asc + desc + stroke * 2
    extra = (emoji.width + 18) if emoji is not None else 0
    img = Image.new("RGBA", (tw + extra, max(th, emoji.height if emoji else 0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = stroke
    for ch, wch in zip(text, widths):
        d.text((x, stroke), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += wch
    if emoji is not None:
        img.alpha_composite(emoji, (tw + 18, (img.height - emoji.height) // 2))
    return img

_cache = {}
def T(key, *a, **k):
    if key not in _cache:
        _cache[key] = text_img(*a, **k)
    return _cache[key]

def paste_center(canvas, layer, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy(); layer.putalpha(a)
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))

def zoom_crop(img, s, ox=0, oy=0):
    """Scale img by s and center-crop to W x H (Ken Burns)."""
    w, h = int(img.width * s), int(img.height * s)
    im = img.resize((w, h), Image.BILINEAR)
    x0 = (w - W) // 2 + int(ox); y0 = (h - H) // 2 + int(oy)
    return im.crop((x0, y0, x0 + W, y0 + H))

def label(canvas, text, cy, size=44, color=GOLD, t=1.0):
    paste_center(canvas, T(("lbl", text, size, color), text, size, fill=color, weight="Bold", spacing=6), W / 2, cy,
                 alpha=ease(t * 3))

def punch(canvas, key, text, cy, size, lt, color=WHITE, stroke=0, emoji=None):
    """Headline that slams in: scale 1.6 -> 1.0 over ~0.25 s, then slow drift."""
    s = 1.0 + 0.6 * (1 - ease(lt / 0.25)) + 0.03 * lt
    paste_center(canvas, T(key, text, size, fill=color, stroke=stroke, emoji=emoji), W / 2, cy, scale=s,
                 alpha=ease(lt / 0.12))

# ---------- static art ----------
print("building art…", file=sys.stderr)
STORM = Image.blend(gradient((10, 16, 34), (2, 3, 8), W + 200, H + 200), clouds(1, (70, 110, 190)), 0.5).convert("RGBA")
CITY_MODERN = skyline(3, 1650, (5, 7, 14, 255))
CITY_1949 = skyline(5, 1600, (12, 12, 14, 255), modern=False)
KAIJU = kaiju(1.35)
KAIJU_FAR = kaiju(0.9, (14, 20, 36, 255))
DRAGON = dragon3()
AWARD = award()
EYES = eyes_emoji(84)
NIGHT = gradient((14, 20, 40), (3, 4, 9))
SEPIA = gradient((48, 40, 30), (14, 12, 10))
THEATER = gradient((10, 10, 16), (2, 2, 4))

def lightning_bolt(seed, x0, color=(255, 230, 150)):
    r = random.Random(seed)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = x0, 0
    while y < 900:
        nx, ny = x + r.randint(-70, 70), y + r.randint(50, 110)
        d.line([(x, y), (nx, ny)], fill=color + (255,), width=7)
        if r.random() < 0.25:
            d.line([(nx, ny), (nx + r.randint(-120, 120), ny + r.randint(60, 160))], fill=color + (200,), width=3)
        x, y = nx, ny
    glow = img.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(glow, img)

BOLTS = [lightning_bolt(s, x) for s, x in ((11, 260), (12, 780), (13, 520))]

# ---------- scenes: (start, end, fn(canvas, t_local, t_global)) ----------
def storm_base(c, t, flash_times=()):
    bg = zoom_crop(STORM, 1.0 + 0.012 * t, ox=-20 * t)
    c.paste(bg.convert("RGBA"))
    for ft in flash_times:
        if 0 <= t - ft < 0.18:
            c.alpha_composite(Image.new("RGBA", (W, H), (200, 220, 255, int(140 * (1 - (t - ft) / 0.18)))))

def s_hook(c, t, g):
    storm_base(c, t, flash_times=(0.0, 2.0))
    paste_center(c, KAIJU_FAR, 860, 1180 - 10 * t, alpha=ease((t - 1.9) / 0.3) * 0.9)  # second shadow
    rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rim).ellipse([0, 700, 760, 1500], fill=(90, 150, 255, 150))
    c.alpha_composite(rim.filter(ImageFilter.GaussianBlur(110)))
    paste_center(c, KAIJU, 360 + 25 * t, 1240, scale=1.0 + 0.04 * t)
    c.alpha_composite(CITY_MODERN.crop((60, 0, 60 + W, H)))
    if t >= 2.0:
        c.alpha_composite(BOLTS[1])
    punch(c, "cb1", "GODZILLA IS BACK", 420, 80, t, stroke=6, emoji=EYES)

def s_title(c, t, g):
    c.paste(NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    for i, ang in enumerate((-18, -6, 6, 18)):  # projector beams
        a = math.radians(ang + 3 * math.sin(g * 1.3 + i))
        d.polygon([(W / 2, 1900), (W / 2 + math.sin(a) * 1900 - 70, -50), (W / 2 + math.sin(a) * 1900 + 70, -50)],
                  fill=(60, 90, 150, 38))
    c.alpha_composite(CITY_MODERN.crop((100, 120, 100 + W, H + 120)))
    punch(c, "t1", "GODZILLA", 760, 150, t, color=WHITE)
    punch(c, "t2", "MINUS ZERO", 920, 150, max(0, t - 0.45), color=ICE)
    if t > 1.3:
        label(c, "IN THEATERS NOW", 1080, 50, GOLD, t - 1.3)

def date_card(c, t, big, small, sub, tint):
    c.paste(gradient(tint, (4, 4, 8)))
    d = ImageDraw.Draw(c, "RGBA")
    for y in range(0, H, 46):  # newsprint lines
        d.line([(0, y + (g_off := int(t * 20) % 46)), (W, y + g_off)], fill=(255, 255, 255, 10), width=2)
    cardw, cardh = 640, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    card = Image.new("RGBA", (cardw, cardh), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cardw, cardh], 36, fill=(245, 240, 228, 255))
    cd.rounded_rectangle([0, 0, cardw, 170], 36, fill=(200, 40, 40, 255))
    cd.rectangle([0, 120, cardw, 170], fill=(200, 40, 40, 255))
    sm = text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    card.alpha_composite(sm, ((cardw - sm.width) // 2, 40))
    bg_ = text_img(big, 300, fill=(20, 20, 24))
    card.alpha_composite(bg_, ((cardw - bg_.width) // 2, 230))
    paste_center(c, card, W / 2, 820, scale=s)
    label(c, sub, 1310, 56, WHITE, t - 0.25)

def s_nov3(c, t, g):
    date_card(c, t, "3", "NOV", "JAPAN RELEASE", (40, 20, 24))

def s_1954(c, t, g):
    c.paste(SEPIA)
    d = ImageDraw.Draw(c, "RGBA")
    for y in range(260, 1500, 54):
        d.line([(110, y), (970, y)], fill=(90, 78, 60), width=6)
    punch(c, "y54", "1954", 760, 260, t, color=(240, 225, 190))
    label(c, "THE ORIGINAL • NOV 3", 960, 52, GOLD, t - 0.3)
    paste_center(c, KAIJU_FAR, 540, 1350, scale=0.7 + 0.03 * t, alpha=0.55)

def s_route(c, t, g):
    c.paste(NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    for gx in range(0, W, 90):
        d.line([(gx, 0), (gx, H)], fill=(30, 45, 80), width=1)
    for gy in range(0, H, 90):
        d.line([(0, gy), (W, gy)], fill=(30, 45, 80), width=1)
    a, b = (820, 1050), (240, 820)
    p = ease(t / 1.2)
    pts = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - math.sin(u * math.pi) * 300) for u in np.linspace(0, p, 40)]
    if len(pts) > 1:
        d.line(pts, fill=GOLD, width=10)
    for (x, y), name in ((a, "JAPAN"), (b, "NORTH AMERICA")):
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=ICE)
    paste_center(c, T("jp", "JAPAN • NOV 3", 44, weight="Bold", fill=WHITE), 820, 1120)
    paste_center(c, T("na", "NORTH AMERICA • NOV 6", 44, weight="Bold", fill=WHITE), 360, 740, alpha=ease((t - 0.9) / 0.3))
    punch(c, "wk", "THIS WEEK", 480, 120, max(0, t - 0.8), color=GOLD)

def s_sequel(c, t, g):
    storm_base(c, t * 0.5)
    c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 110)))
    paste_center(c, KAIJU, 540, 1350, scale=0.9 + 0.02 * t, alpha=0.8)
    punch(c, "m1", "MINUS ONE", 640, 130, t, color=WHITE)
    if t > 1.5:
        paste_center(c, T("arr", "↓", 120, fill=GOLD), W / 2, 790, alpha=ease((t - 1.5) / 0.2))
        punch(c, "m0", "MINUS ZERO", 950, 130, t - 1.6, color=ICE)
    if t > 2.6:
        label(c, "2023  →  2026", 1110, 54, GOLD, t - 2.6)

def s_budget(c, t, g):
    c.paste(gradient((18, 26, 18), (4, 6, 4)))
    punch(c, "b15", "~$15M", 820, 250, t, color=(120, 230, 140))
    label(c, "TOTAL BUDGET", 1010, 56, WHITE, t - 0.3)

def s_award(c, t, g):
    c.paste(gradient((40, 30, 10), (6, 4, 2)))
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(16):
        a = i * math.pi / 8 + g * 0.3
        d.polygon([(540, 820), (540 + math.cos(a) * 1500, 820 + math.sin(a) * 1500),
                   (540 + math.cos(a + 0.12) * 1500, 820 + math.sin(a + 0.12) * 1500)], fill=(80, 60, 20))
    paste_center(c, AWARD, 540, 900, scale=0.6 + 0.4 * ease(t / 0.35) + 0.02 * t)
    label(c, "BEST VISUAL EFFECTS", 1310, 54, WHITE, t - 0.3)

def s_gross(c, t, g):
    c.paste(NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    p = ease(t / 1.8)
    for i in range(7):
        bh = (120 + i * 95) * p
        d.rectangle([150 + i * 115, 1500 - bh, 230 + i * 115, 1500], fill=(60, 120, 200) if i < 6 else GOLD)
    val = int(116 * ease(t / 1.6))
    paste_center(c, text_img(f">${val}M", 210, fill=GOLD), W / 2, 720)
    label(c, "WORLDWIDE", 880, 60, WHITE, t - 0.2)

def s_1949(c, t, g):
    c.paste(gradient((40, 44, 50), (10, 10, 12)))
    c.alpha_composite(Image.blend(Image.new("RGB", (W, H)), clouds(9, (120, 120, 120), W, H), 0.6).convert("RGBA"),)
    c.alpha_composite(CITY_1949.crop((40 + int(20 * t), 0, 40 + int(20 * t) + W, H)))
    d = ImageDraw.Draw(c, "RGBA")
    r = random.Random(int(g * FPS))
    for _ in range(140):  # rain
        x, y = r.randint(0, W), r.randint(0, H)
        d.line([(x, y), (x - 12, y + 50)], fill=(170, 180, 200, 90), width=2)
    punch(c, "y49", "1949", 640, 240, t, color=(235, 230, 220))
    label(c, "TWO YEARS LATER", 820, 56, GOLD, t - 0.4)

def s_director(c, t, g):
    c.paste(THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    for gx in range(140, 960, 100):  # VFX grid
        d.line([(gx, 500), (gx, 1300)], fill=(40, 60, 100), width=2)
    for gy in range(500, 1310, 100):
        d.line([(140, gy), (940, gy)], fill=(40, 60, 100), width=2)
    sweep = 500 + (t * 400) % 800
    d.line([(140, sweep), (940, sweep)], fill=ICE, width=4)
    punch(c, "dn", "TAKASHI YAMAZAKI", 640, 78, t, color=WHITE)
    label(c, "DIRECTOR • WRITER • VFX SUPERVISOR", 760, 38, GOLD, t - 0.2)
    if t > 2.9:  # "same leads": two generic figures
        a = ease((t - 2.9) / 0.3)
        for x in (420, 660):
            d.ellipse([x - 50, 900, x + 50, 1000], fill=(200, 210, 230, int(255 * a)))
            d.rounded_rectangle([x - 85, 1010, x + 85, 1220], 55, fill=(200, 210, 230, int(255 * a)))
        label(c, "SAME LEADS", 1280, 54, WHITE, t - 2.9)

def s_imax(c, t, g):
    c.paste(THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    grow = ease((t - 0.6) / 1.2)
    sw = 900
    sh = sw / 2.39 + (sw / 1.43 - sw / 2.39) * grow  # widescreen -> taller 1.43:1 framing
    top = 760 - sh / 2
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rectangle([90, top - 30, 990, top + sh + 30], fill=(150, 200, 255, 120))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    d.rectangle([90, top, 990, top + sh], fill=(215, 235, 255))
    for row in range(5):  # seats
        y = 1350 + row * 90
        for x in range(60 + (row % 2) * 40, W, 80):
            d.ellipse([x, y, x + 62, y + 70], fill=(18, 18, 26))
    label(c, "1.43 : 1 FULL-HEIGHT FRAME", 1250, 40, ICE, t - 1.0)

def s_dragon(c, t, g):
    storm_base(c, t, flash_times=(0.3, 2.45, 3.6))
    reveal = ease((t - 2.4) / 1.0)
    backlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(backlight).ellipse([140, 380, 940, 1180], fill=(255, 200, 90, int(160 * reveal)))
    c.alpha_composite(backlight.filter(ImageFilter.GaussianBlur(90)))
    paste_center(c, DRAGON, 540, 860, scale=0.85 + 0.06 * t, alpha=0.25 + 0.75 * reveal)
    for i, ft in enumerate((0.3, 2.45, 3.6)):
        if 0 <= t - ft < 0.25:
            c.alpha_composite(BOLTS[i])
    c.alpha_composite(CITY_MODERN.crop((0, 0, W, H)))
    if t < 2.4:
        label(c, "A SECOND MONSTER?", 1320, 58, WHITE, t - 0.4)

def s_tagline(c, t, g):
    c.paste(Image.new("RGB", (W, H), (3, 4, 8)))
    paste_center(c, KAIJU_FAR, 540, 1450, scale=1.2, alpha=0.35)
    if t > 1.3:
        paste_center(c, T("tg1", "THERE IS NO", 96, fill=WHITE), W / 2, 700, alpha=ease((t - 1.3) / 0.4))
        paste_center(c, T("tg2", "THIRD TIME.", 96, fill=WHITE), W / 2, 810, alpha=ease((t - 1.5) / 0.4))
    if t > 2.7:
        paste_center(c, T("tg3", "EVERYTHING ENDS HERE.", 70, fill=GOLD), W / 2, 960, alpha=ease((t - 2.7) / 0.4))
    if t < 1.3:
        label(c, "THE TAGLINE", 760, 60, GOLD, t)

def s_callback(c, t, g):
    c.paste(gradient((30, 22, 8), (4, 4, 6)))
    paste_center(c, AWARD, 540, 980, scale=0.55 + 0.02 * t, alpha=0.9)
    punch(c, "cb15", "~$15M → OSCAR", 600, 110, t, color=GOLD)
    if t > 2.75:
        punch(c, "imag", "NOW IMAGINE THIS ONE", 1240, 72, t - 2.75, color=WHITE)

def s_outro(c, t, g):
    c.paste(THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    d.rectangle([90, 500, 990, 1130], fill=(30, 50, 90))
    for row in range(4):
        y = 1280 + row * 95
        for x in range(50 + (row % 2) * 40, W, 80):
            d.ellipse([x, y, x + 62, y + 72], fill=(10, 10, 16))
    punch(c, "imq", "IMAX?", 760, 210, t, color=WHITE)
    if t > 1.5:
        punch(c, "sun", "SUNDAY RECAP", 980, 84, t - 1.5, color=GOLD)
    if t > 2.6:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 2.6) / 0.3))

SCENES = [
    (0.00, 3.48, s_hook), (3.48, 5.91, s_title), (5.91, 8.01, s_nov3), (8.01, 11.60, s_1954),
    (11.60, 13.94, s_route), (13.94, 18.08, s_sequel), (18.08, 20.54, s_budget), (20.54, 22.40, s_award),
    (22.40, 25.93, s_gross), (25.93, 29.27, s_1949), (29.27, 33.38, s_director), (33.38, 36.87, s_imax),
    (36.87, 42.07, s_dragon), (42.07, 46.58, s_tagline), (46.58, 51.15, s_callback), (51.15, DUR + 0.1, s_outro),
]
CALLOUTS = [  # (start, end, key, text, emoji) — exact wording from the brief, in order
    (0.15, 3.40, None, None, None),  # #1 is drawn inside the hook scene with the emoji
    (20.54, 25.80, "co2", "$15M → OSCAR WINNER", None),
    (33.45, 36.80, "co3", "FIRST JAPANESE FILM IN IMAX", None),
    (39.32, 42.00, "co4", "KING GHIDORAH?!", None),
]
CAPS = captions()

def draw_callout(c, g):
    for s, e, key, text, _ in CALLOUTS:
        if key and s <= g < e:
            lt = g - s
            img = T(key, text, 76 if len(text) < 22 else 60, fill=(15, 15, 18), weight="Black")
            pill = Image.new("RGBA", (img.width + 70, img.height + 34), (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill.width, pill.height], 26, fill=GOLD + (255,))
            pill.alpha_composite(img, (35, 14))
            sc = min(1.0 + 0.5 * (1 - ease(lt / 0.22)), (W - 60) / pill.width)  # never wider than the frame
            paste_center(c, pill, W / 2, 330, scale=sc, alpha=min(ease(lt / 0.1), ease((e - g) / 0.15)))

def draw_caption(c, g):
    for s, e, text in CAPS:
        if s <= g < e:
            img = T(("cap", text), text, 84 if len(text) <= 16 else 66, fill=WHITE, weight="Black", stroke=9)
            sc = 1.0 + 0.12 * (1 - ease((g - s) / 0.12))
            paste_center(c, img, W / 2, 1430, scale=sc)
            return

def draw_bug(c):
    paste_center(c, T("bug", "LIVE LORE", 30, fill=(255, 255, 255), weight="Bold", spacing=6), 150, 205, alpha=0.7)

def frame(g):
    c = Image.new("RGBA", (W, H), NAVY + (255,))
    for s, e, fn in SCENES:
        if s <= g < e:
            fn(c, g - s, g)
            cut_age = g - s
            break
    # post: vignette + grain
    arr = np.asarray(c.convert("RGB"), dtype=np.float32) * vignette()
    gr = GRAIN[int(g * FPS) % len(GRAIN)]
    arr += np.repeat(np.repeat(gr, 2, 0), 2, 1)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    if cut_age < 0.1 and g > 0.2:  # quick white flash on every cut
        out.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - cut_age / 0.1)))))
    draw_callout(out, g)
    draw_caption(out, g)
    draw_bug(out)
    return out.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    n = int(round((t1 - t0) * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-ss", str(t0), "-t", str(t1 - t0), "-i", AUDIO,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "10M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(t0 + i / FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{n}", file=sys.stderr)
    p.stdin.close()
    sys.exit(p.wait())
