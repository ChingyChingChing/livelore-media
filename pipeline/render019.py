"""Live Lore Short 019 (63rd Golden Horse Awards, Taipei, Nov 22 2026: Hong Kong's "We Are Born Good" wins Best
Narrative Feature + Best Original Screenplay; Angela Yuen Best Leading Actress; Anson Kong Best Supporting Actor;
Shu Qi Best New Director) - reuses render.py.
Usage: python3 render019.py OUT.mp4 [start end]  |  python3 render019.py stills t1 t2 ...
All visuals drawn in code (a generic takeout box, order ticket, generic trophies, generic skyline, award cards with
names as plain text, emoji; no posters, stills, trailers, photos or logos). No music.
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
SEG = json.load(open("segments019.json"))
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
SUN_BG = gradient((120, 50, 20), (14, 6, 4))
TEAL_BG = gradient((10, 50, 80), (2, 6, 12))
TROPHY = r.AWARD
TROPHY_S = TROPHY.resize((156, 192), Image.LANCZOS)
HK_SKY = r.skyline(7, 1500, (8, 10, 20, 255))
E_ANGRY, E_HUFF, E_ZAP, E_CLAP, E_PEN, E_LOCK, E_POP, E_STAR, E_X, E_NOODLE = (emoji(ch, 150) for ch in
    ["😠", "😤", "⚡", "🎬", "✍️", "🔒", "🍿", "⭐", "❌", "🍜"])

def takeout(t, flaps=True):
    """Generic Chinese takeout box drawn from shapes."""
    w, h = 520, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc([110, -40, 410, 230], 200, 340, fill=(160, 160, 170, 255), width=10)   # wire handle
    d.polygon([(40, 150), (480, 150), (420, 540), (100, 540)], fill=(250, 248, 242, 255))
    d.polygon([(40, 150), (140, 60), (260, 150)], fill=(232, 228, 220, 255))
    d.polygon([(260, 150), (380, 60), (480, 150)], fill=(232, 228, 220, 255))
    for k in range(3):
        y = 270 + k * 60
        x0 = 40 + (y - 150) * 60 / 390
        d.line([(x0 + 10, y), (w - x0 - 10, y)], fill=RED + (255,), width=16)
    return im
BOX = takeout(0)

def ticket(t):
    """Order ticket with a wrong item crossed out."""
    w, h = 640, 820
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0, 0), (w, 0), (w, h - 30)]
    for i in range(16, -1, -1):
        pts.append((i * w / 16, h - (0 if i % 2 else 30)))
    d.polygon(pts, fill=PAPER + (255,))
    hd = r.text_img("ORDER #47", 70, fill=DARK)
    im.alpha_composite(hd, ((w - hd.width) // 2, 40))
    d.line([(40, 140), (w - 40, 140)], fill=(180, 170, 150, 255), width=4)
    items = ["1x NOODLES", "1x DUMPLINGS", "1x MILK TEA"]
    for i, it in enumerate(items):
        tx = r.text_img(it, 58, fill=(60, 60, 70), weight="Bold")
        im.alpha_composite(tx, (60, 190 + i * 130))
    k = ease((t - 0.4) / 0.3)
    if k > 0:
        y = 190 + 130 + 34
        d.line([(50, y), (50 + (w - 100) * k, y)], fill=RED + (255,), width=14)
    k2 = ease((t - 0.8) / 0.25)
    if k2 > 0:
        wr = r.text_img("WRONG!", 90, fill=RED)
        wr = wr.rotate(-10, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(wr, ((w - wr.width) // 2, 590))
    return im

def spiral(g, col=GOLD):
    s = 900
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    for i in range(520):
        a = i * 0.06 + g * 3.5
        rr = 6 + i * 0.82
        pts.append((s / 2 + rr * math.cos(a), s / 2 + rr * math.sin(a)))
    d.line(pts, fill=col + (255,), width=18)
    return im

def nine_dots(t):
    im = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    for i in range(9):
        k = ease((t - i * 0.09) / 0.18)
        if k <= 0:
            continue
        x, y = 150 + (i % 3) * 300, 150 + (i // 3) * 300
        tr = TROPHY_S.resize((int(156 * k) or 1, int(192 * k) or 1))
        im.alpha_composite(tr, (int(x - tr.width / 2), int(y - tr.height / 2)))
    return im

C_FILM = card("BEST NARRATIVE FEATURE", "WE ARE BORN GOOD", RED, "HONG KONG")
C_SCRIPT = card("BEST ORIGINAL SCREENPLAY", "WE ARE BORN GOOD", (40, 120, 200), "WIN #2")
C_YUEN = card("BEST LEADING ACTRESS", "ANGELA YUEN", (190, 60, 130), "\"AFTERPIECE\"")
C_KONG = card("BEST SUPPORTING ACTOR", "ANSON KONG", (40, 140, 120), "\"WE'RE NOTHING AT ALL\"")
C_SHU = card("BEST NEW DIRECTOR", "SHU QI", (120, 70, 200), "\"GIRL\"")

def slide(c, t, crd, bg, y=860):
    c.paste(bg)
    paste_center(c, crd, W / 2 + 700 * (1 - ease(t / 0.3)), y, alpha=ease(t / 0.1))

# ---------- scenes ----------
def s_hook(c, t, g):
    c.paste(RED_BG)
    wob = 6 * math.sin(g * 9)
    paste_center(c, BOX.rotate(wob, resample=Image.BICUBIC), W / 2, 960, scale=1.0 + 0.03 * t, alpha=ease(t / 0.1))
    if t > 0.5:
        paste_center(c, E_X.resize((220, 220)), W / 2 + 230, 760, *pop(t - 0.5))

def s_win(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150), (255, 200, 120)))
    paste_center(c, BOX, W / 2, 1180, scale=0.8, alpha=ease(t / 0.1))
    paste_center(c, TROPHY, W / 2, 1000 - 180 * ease(t / 0.5), scale=0.6, alpha=ease(t / 0.15))
    punch(c, "bf", "BEST FILM?!", 560, 140, t, color=WHITE, stroke=7)

def s_date(c, t, g):
    date_card2(c, t, "22", "NOV 2026", "TAIPEI MUSIC CENTER", (30, 40, 110))

def s_title(c, t, g):
    c.paste(NAVY_BG); spotlights(c, g)
    paste_center(c, C_FILM, W / 2, 860, *pop(t))

def s_horse(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150), (255, 230, 150), (255, 230, 150)))
    paste_center(c, TROPHY, W / 2, 1000, scale=0.85 + 0.04 * math.sin(g * 4), alpha=ease(t / 0.15))
    punch(c, "gh", "GOLDEN HORSE", 520, 120, t, color=WHITE, stroke=7)
    label(c, "63RD EDITION", 1350, 60, WHITE, t - 0.3)

def s_oscars(c, t, g):
    c.paste(PURP_BG); spotlights(c, g, ((200, 120, 255), (255, 230, 150)))
    for i in range(5):
        paste_center(c, E_STAR.resize((120, 120)), 220 + i * 160, 700 + 30 * math.sin(g * 4 + i), *pop(t - i * 0.08))
    punch(c, "osc", "CHINESE-LANGUAGE", 960, 100, t - 0.1, color=WHITE, stroke=6)
    punch(c, "osc2", "OSCARS", 1110, 170, t - 0.25, color=GOLD, stroke=7)

def s_ticket(c, t, g):
    c.paste(SUN_BG)
    paste_center(c, ticket(t), W / 2, 900, scale=0.95, alpha=ease(t / 0.12))

def s_feud(c, t, g):
    c.paste(RED_BG)
    sh = 18 * math.sin(g * 30) * (1 if t > 0.4 else 0)
    paste_center(c, E_ANGRY.resize((330, 330)), W * 0.27 + sh, 900, *pop(t))
    paste_center(c, E_HUFF.resize((330, 330)), W * 0.73 - sh, 900, *pop(t - 0.15))
    if t > 0.35:
        paste_center(c, E_ZAP.resize((200, 200)), W / 2, 900, *pop(t - 0.35))
    punch(c, "feud", "PETTY FEUD", 560, 130, t, color=WHITE, stroke=6)

def s_spiral(c, t, g):
    c.paste(PURP_BG)
    paste_center(c, spiral(g), W / 2, 950, scale=0.8 + 0.15 * ease(t / 1.0), alpha=ease(t / 0.15))
    paste_center(c, E_NOODLE.resize((170, 170)).rotate(g * 200 % 360, resample=Image.BICUBIC), W / 2, 950, alpha=ease(t / 0.2))
    if t > 0.5:
        paste_center(c, stamp("OUT OF CONTROL", 92, (255, 120, 120), -7), W / 2, 520, *pop(t - 0.5))

def s_debut(c, t, g):
    c.paste(NAVY_BG)
    paste_center(c, E_CLAP.resize((360, 360)), W / 2, 880, *pop(t))
    if t > 0.3:
        paste_center(c, stamp("FIRST FEATURE", 100, GOLD, -6), W / 2, 1240, *pop(t - 0.3))

def s_script(c, t, g):
    slide(c, t, C_SCRIPT, TEAL_BG)
    if t > 0.4:
        paste_center(c, E_PEN.resize((180, 180)), W / 2 + 360, 1170, *pop(t - 0.4))

def s_nine(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g, ((255, 230, 150),))
    paste_center(c, nine_dots(t), W / 2, 960, scale=0.9)
    punch(c, "nine", "9 NOMINATIONS", 470, 120, t, color=WHITE, stroke=6)

def s_hk(c, t, g):
    c.paste(TEAL_BG); spotlights(c, g, ((120, 200, 255), (255, 230, 150)))
    c.alpha_composite(HK_SKY, (-100 + int(40 * ease(t / 2)), 0))
    punch(c, "hk", "HONG KONG", 620, 150, t, color=GOLD, stroke=7)
    label(c, "KEPT WINNING", 800, 90, WHITE, t - 0.2)

def s_yuen(c, t, g): slide(c, t, C_YUEN, gradient((80, 20, 60), (8, 2, 6)))
def s_kong(c, t, g): slide(c, t, C_KONG, JADE_BG)

def s_shu(c, t, g):
    slide(c, t, C_SHU, PURP_BG)

def s_ate(c, t, g):
    c.paste(GOLD_BG); spotlights(c, g)
    for i in range(4):
        paste_center(c, TROPHY.resize((220, 272)), 190 + i * 233, 980 + 20 * math.sin(g * 5 + i), *pop(t - i * 0.1))
    punch(c, "ate", "THEY ALL ATE", 560, 130, t, color=WHITE, stroke=6)

def s_take(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "mt19", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    c.alpha_composite(HK_SKY, (-100, 160))

def s_lock(c, t, g):
    c.paste(TEAL_BG)
    paste_center(c, E_LOCK.resize((340, 340)), W / 2, 900, *pop(t))
    if t > 0.25:
        paste_center(c, stamp("LOCKED IN", 120, GOLD, -7), W / 2, 1230, *pop(t - 0.25))

def s_q(c, t, g):
    c.paste(gradient((90, 40, 20), (10, 4, 2)))
    paste_center(c, E_POP.resize((360, 360)), W / 2, 920, *pop(t))
    paste_center(c, E_THINK.resize((200, 200)), W / 2 + 280, 700, *pop(t - 0.2))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun19", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.4:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.4) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 3), ST[1], at(1, 2), at(1, 6), at(1, 8), ST[2], at(2, 2), at(2, 4), at(2, 7), ST[3], at(3, 3),
     ST[4], at(4, 2), at(4, 6), ST[5], at(5, 5), ST[6], at(6, 3), ST[7], ST[8], DUR + 0.1]
FNS = [s_hook, s_win, s_date, s_title, s_horse, s_oscars, s_feud, s_ticket, s_spiral, s_debut, s_script, s_nine,
       s_hk, s_yuen, s_kong, s_shu, s_ate, s_take, s_lock, s_q, s_outro]
assert len(B) == len(FNS) + 1, (len(B), len(FNS))
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (at(0, 4) + 0.05, ST[1] - 0.1, "c1", "HONG KONG FILM", None),
    (at(1, 8), ST[2] - 0.1, "c2", "TAIPEI · NOV 22", None),
    (at(2, 7), ST[3] - 0.1, "c3", "DIRECTING DEBUT", None),
    (at(4, 2), ST[5] - 0.1, "c4", "63RD GOLDEN HORSE", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58
if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s019_{s}.png")
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
