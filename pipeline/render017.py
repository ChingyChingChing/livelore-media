"""Live Lore Short 017 (2026 MAMA Awards night 1 at Kyocera Dome Osaka: BTS Artist of the Year, reportedly an 8th win,
while on tour in Kaohsiung; ENHYPEN Fans' Choice of the Year two years running; IVE, Yeonjun) - reuses render.py.
Usage: python3 render017.py OUT.mp4 [start end]  |  python3 render017.py stills t1 t2 ...
All visuals drawn in code (generic star trophies, stage lights, a generic dome, a simple map route, lightsticks, cards,
emoji; artist, award and venue names as plain text only; no logos, photos, likenesses or broadcast footage). No music.
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
SEG = json.load(open("segments017.json"))
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

STAGE_BG = gradient((40, 14, 70), (4, 2, 10))
GOLD_BG = gradient((90, 60, 10), (10, 6, 2))
NAVY_BG = gradient((16, 18, 40), (3, 3, 10))
TEAL_BG = gradient((10, 60, 70), (2, 8, 12))
PINK_BG = gradient((90, 20, 70), (10, 2, 10))
SEA_BG = gradient((20, 60, 110), (4, 12, 30))
MAGENTA = (255, 70, 160)

TROPHY = r.AWARD
TROPHY_S = TROPHY.resize((156, 192), Image.LANCZOS)

def spotlights(c, t, cols=((255, 230, 150), (200, 120, 255), (120, 200, 255))):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, col in enumerate(cols):
        x0 = (i + 0.5) * W / len(cols)
        a = math.sin(t * 1.4 + i * 2.0) * 260
        d.polygon([(x0, -40), (x0 + a - 230, H * 0.85), (x0 + a + 230, H * 0.85)], fill=col + (46,))
    c.alpha_composite(layer.filter(ImageFilter.GaussianBlur(18)))

def stage_floor(c):
    d = ImageDraw.Draw(c, "RGBA")
    d.ellipse([-200, 1180, W + 200, 1700], fill=(30, 20, 50, 255))
    d.ellipse([60, 1220, W - 60, 1560], fill=(60, 40, 90, 255))

def dome(t):
    w, h = 980, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.pieslice([40, 60, w - 40, h * 2 - 80], 180, 360, fill=(200, 205, 220, 255))
    for k in range(1, 7):
        x = 40 + k * (w - 80) / 7
        d.line([(x, h - 20), (w / 2 + (x - w / 2) * 0.35, 90)], fill=(150, 156, 175, 255), width=6)
    for k in range(3):
        y = h - 20 - k * 120
        d.arc([40 + k * 60, 60 + k * 120, w - 40 - k * 60, h * 2 - 80 - k * 120], 180, 360, fill=(150, 156, 175, 255), width=6)
    d.rectangle([20, h - 30, w - 20, h], fill=(90, 96, 120, 255))
    for k in range(12):
        x = 60 + k * (w - 120) / 11
        on = (math.sin(t * 6 + k) > 0)
        d.rectangle([x - 14, h - 26, x + 14, h - 6], fill=((255, 220, 120) if on else (60, 60, 80)) + (255,))
    return im

def kcard(head, name, col, sub=None):
    w, h = 900, 600
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=(250, 246, 238, 255))
    d.rounded_rectangle([0, 0, w, 150], 40, fill=col + (255,))
    d.rectangle([0, 110, w, 150], fill=col + (255,))
    hs = 62
    hd = r.text_img(head, hs, fill=WHITE, weight="ExtraBold", spacing=4)
    while hd.width > w - 80:
        hs -= 4
        hd = r.text_img(head, hs, fill=WHITE, weight="ExtraBold", spacing=4)
    im.alpha_composite(hd, ((w - hd.width) // 2, (150 - hd.height) // 2 + 4))
    nm = r.text_img(name, 170 if len(name) <= 7 else 130, fill=DARK)
    im.alpha_composite(nm, ((w - nm.width) // 2, 220 if sub else 260))
    if sub:
        sb = r.text_img(sub, 54, fill=(110, 110, 120), weight="Bold", spacing=4)
        im.alpha_composite(sb, ((w - sb.width) // 2, 450))
    im.alpha_composite(TROPHY_S.resize((80, 98)), (w - 120, h - 125))
    return im
CARD_IVE = kcard("BEST FEMALE GROUP", "IVE", (200, 60, 120))
CARD_YJ = kcard("BEST MALE ARTIST", "YEONJUN", (60, 110, 200), "OF TXT")
CARD_EN = kcard("FANS' CHOICE OF THE YEAR", "ENHYPEN", (190, 40, 50))
CARD_BTS = kcard("ARTIST OF THE YEAR", "BTS", (150, 100, 20))

def map_route(t):
    w, h = 900, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=(30, 80, 140, 255))
    land = (70, 150, 110, 255)
    d.polygon([(470, 120), (640, 60), (860, 150), (820, 300), (640, 330), (560, 260)], fill=land)   # generic island arc
    d.polygon([(60, 260), (300, 200), (380, 420), (260, 640), (90, 700), (0, 500)], fill=land)      # generic mainland
    d.ellipse([360, 600, 440, 760], fill=land)                                                     # generic island
    a, b = (700, 210), (400, 690)
    k = ease((t - 0.2) / 0.9)
    pts = [(a[0] + (b[0] - a[0]) * u - 160 * math.sin(math.pi * u), a[1] + (b[1] - a[1]) * u) for u in [i / 40 * k for i in range(41)]]
    for p0, p1 in zip(pts[::2], pts[1::2]):
        d.line([p0, p1], fill=(255, 255, 255, 255), width=10)
    for (x, y), txt in ((a, "OSAKA"), (b, "KAOHSIUNG")):
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=GOLD + (255,), outline=(255, 255, 255, 255), width=6)
        lb = r.text_img(txt, 50, fill=WHITE, weight="Black")
        im.alpha_composite(lb, (int(min(max(x - lb.width / 2, 20), w - 20 - lb.width)), y + 34))
    if k > 0:
        pl = E_PLANE.resize((100, 100))
        paste_center(im, pl, *pts[-1])
    return im

def screen(t):
    w, h = 860, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(20, 20, 26, 255))
    d.rounded_rectangle([24, 24, w - 24, h - 24], 18, fill=(60, 30, 100, 255))
    d.polygon([(w / 2 - 60, h / 2 - 75), (w / 2 - 60, h / 2 + 75), (w / 2 + 75, h / 2)], fill=(255, 255, 255, 230))
    d.rectangle([60, h - 70, w - 60, h - 58], fill=(255, 255, 255, 90))
    d.rectangle([60, h - 70, 60 + (w - 120) * min(1, t / 2.2), h - 58], fill=MAGENTA + (255,))
    return im

def lightstick(col, h=520):
    im = Image.new("RGBA", (220, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 180, 130, h], 18, fill=(40, 40, 50, 255))
    glow = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([10, 10, 210, 210], fill=col + (150,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)), (0, 0))
    d.ellipse([45, 45, 175, 175], fill=col + (255,))
    d.ellipse([75, 70, 115, 105], fill=(255, 255, 255, 170))
    return im
STICKS = [lightstick(c) for c in ((255, 80, 80), (255, 210, 90), (150, 120, 255), (90, 200, 255), (255, 120, 200))]

def year_box(year, t):
    w, h = 380, 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 30, fill=(250, 246, 238, 255))
    d.rounded_rectangle([0, 0, w, 110], 30, fill=RED + (255,))
    d.rectangle([0, 80, w, 110], fill=RED + (255,))
    y = r.text_img(year, 70, fill=WHITE, weight="ExtraBold")
    im.alpha_composite(y, ((w - y.width) // 2, 18))
    return im
Y25, Y26 = year_box("2025", 0), year_box("2026", 0)

def hangul(text, size, col=WHITE):
    f = ImageFont.truetype(CJK, size)
    bb = f.getbbox(text)
    im = Image.new("RGBA", (bb[2] + 10, bb[3] + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((5, 5), text, font=f, fill=col)
    return im
DAESANG = hangul("대상", 230, GOLD)

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(STAGE_BG)
    spotlights(c, g)
    stage_floor(c)
    paste_center(c, TROPHY, W / 2, 1000, scale=0.85 + 0.05 * math.sin(g * 4), alpha=ease(t / 0.15))
    sc = 1.0 + 0.8 * (1 - ease(t / 0.3)) + 0.03 * t
    paste_center(c, T("x8", "8×", 330, fill=GOLD, stroke=10), W / 2, 520, scale=sc, alpha=ease(t / 0.1))

def s_row(c, t, g):
    c.paste(GOLD_BG)
    spotlights(c, g, ((255, 230, 150), (255, 200, 120)))
    for i in range(8):
        x = 170 + (i % 4) * 247
        y = 760 + (i // 4) * 300
        paste_center(c, TROPHY_S, x, y, *pop(t - i * 0.12, 0.2))
    label(c, "ARTIST OF THE YEAR", 520, 64, WHITE, t)

def s_empty(c, t, g):
    c.paste(STAGE_BG)
    spotlights(c, g, ((255, 240, 200),))
    stage_floor(c)
    paste_center(c, E_MIC.resize((240, 240)), W / 2, 1080, alpha=ease(t / 0.15))
    if t > 0.35:
        paste_center(c, stamp("NOT IN THE BUILDING", 82, MAGENTA, -7), W / 2, 700, *pop(t - 0.35))

def s_date(c, t, g):
    date_card2(c, t, "20", "NOV 2026", "KYOCERA DOME · OSAKA", (90, 30, 110))

def s_dome(c, t, g):
    c.paste(gradient((30, 20, 70), (200, 90, 80)))
    spotlights(c, g, ((255, 230, 150), (200, 120, 255), (120, 200, 255), (255, 150, 200)))
    paste_center(c, dome(g), W / 2, 960, scale=0.95 + 0.05 * ease(t / 0.5) + 0.01 * t, alpha=ease(t / 0.15))
    paste_center(c, E_PIN.resize((140, 140)), W / 2, 560 + 12 * math.sin(g * 5), *pop(t - 0.2))
    label(c, "OSAKA, JAPAN", 1300, 60, WHITE, t - 0.3)

def s_two(c, t, g):
    c.paste(NAVY_BG)
    spotlights(c, g, ((255, 230, 150), (255, 230, 150)))
    paste_center(c, TROPHY.resize((300, 369)), W * 0.3, 1000, *pop(t))
    paste_center(c, TROPHY.resize((300, 369)), W * 0.7, 1000, *pop(t - 0.2))
    punch(c, "two", "2 GRAND PRIZES", 560, 96, t, color=WHITE, stroke=6)

def s_daesang(c, t, g):
    c.paste(GOLD_BG)
    paste_center(c, DAESANG, W / 2, 800, scale=0.8 + 0.2 * ease(t / 0.3) + 0.02 * t, alpha=ease(t / 0.12))
    label(c, "\"DAESANG\" = GRAND PRIZE", 1120, 60, WHITE, t - 0.2)

def s_bts(c, t, g):
    c.paste(STAGE_BG)
    spotlights(c, g)
    paste_center(c, CARD_BTS, W / 2, 880, *pop(t))
    if t > 0.5:
        paste_center(c, E_SPARK.resize((130, 130)), W * 0.15, 560, *pop(t - 0.5))
        paste_center(c, E_SPARK.resize((110, 110)), W * 0.86, 1220, *pop(t - 0.6))

def s_map(c, t, g):
    c.paste(SEA_BG)
    paste_center(c, map_route(t), W / 2, 860, scale=0.86 + 0.03 * ease(t / 0.4), alpha=ease(t / 0.12))

def s_video(c, t, g):
    c.paste(PINK_BG)
    paste_center(c, screen(t), W / 2, 900, *pop(t))
    for i in range(5):
        u = (g * 0.6 + i * 0.2) % 1
        paste_center(c, E_HEART.resize((90, 90)), 160 + i * 190, 1250 - 600 * u, alpha=0.9 * (1 - u) * ease(t / 0.3))

def s_fans(c, t, g):
    c.paste(gradient((10, 8, 24), (40, 10, 50)))
    for i, st in enumerate(STICKS):
        x = 130 + i * 205
        ang = 14 * math.sin(g * 5 + i * 1.3)
        paste_center(c, st.rotate(ang, resample=Image.BICUBIC, expand=True), x, 1080 + 30 * math.sin(g * 5 + i), alpha=ease((t - i * 0.08) / 0.15))
    punch(c, "fc", "FANS' CHOICE", 560, 120, t, color=WHITE, stroke=6)

def s_en(c, t, g):
    c.paste(NAVY_BG)
    spotlights(c, g, ((255, 120, 120), (255, 230, 150)))
    paste_center(c, CARD_EN, W / 2, 880, *pop(t))

def s_row2(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, Y25, W * 0.3, 860, *pop(t))
    paste_center(c, Y26, W * 0.7, 860, *pop(t - 0.25))
    for x, d0 in ((W * 0.3, 0.2), (W * 0.7, 0.45)):
        paste_center(c, E_CHECK.resize((170, 170)), x, 920, *pop(t - d0))
    if t > 0.7:
        paste_center(c, stamp("LOWKEY A W", 96, GOLD, -6), W / 2, 1200, *pop(t - 0.7))

def s_others(c, t, g):
    c.paste(STAGE_BG)
    spotlights(c, g)
    punch(c, "oth", "MORE NIGHT 1 WINS", 600, 96, t, color=WHITE, stroke=6)
    for i in range(3):
        paste_center(c, TROPHY_S, W * (0.25 + 0.25 * i), 950, *pop(t - 0.2 - i * 0.12))

def s_ive(c, t, g):
    c.paste(PINK_BG)
    paste_center(c, CARD_IVE, W / 2 + 700 * (1 - ease(t / 0.3)), 880, alpha=ease(t / 0.1))

def s_yj(c, t, g):
    c.paste(SEA_BG)
    paste_center(c, CARD_YJ, W / 2 + 700 * (1 - ease(t / 0.3)), 880, alpha=ease(t / 0.1))
    if t > 0.9:
        paste_center(c, stamp("BOTH ATE", 100, GOLD, -7), W / 2, 1220, *pop(t - 0.9))

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt17", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 900, *pop(t - 0.3))

def s_globe(c, t, g):
    c.paste(SEA_BG)
    paste_center(c, E_GLOBE.resize((420, 420)).rotate(6 * math.sin(g * 2), resample=Image.BICUBIC), W / 2, 900, *pop(t))
    paste_center(c, TROPHY.resize((200, 246)), W / 2 + 230, 1050, *pop(t - 0.3))
    paste_center(c, pill("FROM ANOTHER COUNTRY", 70, GOLD), W / 2, 560, *pop(t - 0.15))

def s_q(c, t, g):
    c.paste(WARM := gradient((90, 40, 20), (10, 4, 2)))
    punch(c, "dq", "DESERVED?", 560, 150, t, color=WHITE, stroke=6)
    paste_center(c, E_THINK.resize((280, 280)), W / 2, 950, *pop(t - 0.1))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun17", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 2), at(0, 7), ST[1], at(1, 3), ST[2], at(2, 3), at(2, 5), ST[3], at(3, 4), ST[4], at(4, 2), at(4, 5),
     ST[5], at(5, 2), at(5, 5), ST[6], at(6, 1), ST[7], ST[8], DUR + 0.1]
FNS = [s_hook, s_row, s_empty, s_date, s_dome, s_two, s_daesang, s_bts, s_map, s_video, s_fans, s_en, s_row2,
       s_others, s_ive, s_yj, s_take, s_globe, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (at(0, 5), ST[1] - 0.1, "c1", "REPORTEDLY 8TH WIN", None),
    (at(1, 3), ST[2] - 0.1, "c2", "NIGHT 1 OF 2", None),
    (ST[3] + 0.1, ST[4] - 0.1, "c3", "ACCEPTED BY VIDEO", None),
    (at(4, 5), ST[5] - 0.1, "c4", "BACK-TO-BACK", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s017_{s}.png")
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
