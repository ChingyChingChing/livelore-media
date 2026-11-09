"""Live Lore Short 007 (Grammys' Asian pop category / BTS) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render007.py OUT.mp4 [start end]  |  python3 render007.py stills t1 t2 ...
All visuals drawn in code (generic shapes; no logos, photos, footage or the Grammy statuette). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
from PIL import ImageFont
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)

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

def pop(lt, d=0.25):
    return 0.6 + 0.4 * ease(lt / d), ease(lt / 0.12)

def stars(c, t, n=40):
    d = ImageDraw.Draw(c, "RGBA")
    rs = random.Random(3)
    for _ in range(n):
        x, y, ph = rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0, 6)
        a = int(120 + 120 * math.sin(t * 3 + ph))
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 230, 150, max(0, a)))

def person(d, x, y, col, s=1.0):
    d.ellipse([x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s], fill=col)
    d.rounded_rectangle([x - 100 * s, y + 75 * s, x + 100 * s, y + 330 * s], int(60 * s), fill=col)

AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments007.json"))
ST = [s[0] for s in SEG]
PURPLE = (150, 90, 230)

def chunk_t(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

def rel(i, j):  # chunk start relative to its scene start
    return chunk_t(i, j) - ST[i]

E_EYES, E_HEART, E_SAD, E_SHIELD, E_SPOT, E_BOX, E_BELL = (emoji(c, 150) for c in "👀💜😔🛡🔦📦🔔")

def seven(c, cx, cy, t, col=PURPLE, rad=46, gap=130):
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(7):
        lt = t - 0.08 * k
        if lt > 0:
            x = cx + (k - 3) * gap
            rr = rad * (0.6 + 0.4 * ease(lt / 0.25))
            d.ellipse([x - rr, cy - rr, x + rr, cy + rr], fill=col + (255,))

def card(w, h, head, fill=(245, 240, 228), headcol=(70, 40, 140)):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=fill + (255,))
    d.rounded_rectangle([0, 0, w, 120], 40, fill=headcol + (255,))
    d.rectangle([0, 80, w, 120], fill=headcol + (255,))
    tt = T(("ch", head, w), head, 52, fill=WHITE, weight="Black")
    im.alpha_composite(tt, ((w - tt.width) // 2, 28))
    return im

def stamp(text, size, col, rot=-8):
    img = T(("st", text, size, col), text, size, fill=col, weight="Black")
    im = Image.new("RGBA", (img.width + 70, img.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 20, outline=col + (255,), width=10)
    im.alpha_composite(img, (35, 20))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

# ---------- scenes ----------
def s_hook(c, t, g):
    split = rel(0, 3)
    c.paste(r.NIGHT)
    stars(c, t, 25)
    if t < split:
        paste_center(c, r.AWARD, W / 2, 900, 1.0 + 0.04 * t, ease(t / 0.2))
        punch(c, "ap", "ASIAN POP AWARD", 520, 86, t, color=GOLD, stroke=6)
    else:
        lt = t - split
        c.paste(gradient((50, 24, 80), (6, 4, 14)))
        seven(c, W / 2, 800, lt)
        paste_center(c, stamp("NO THANKS", 130, RED), W / 2, 1000, *pop(lt - 0.3))
        punch(c, "bts", "BTS", 520, 150, lt, color=WHITE, stroke=7, emoji=E_HEART.resize((130, 130)))

def s_june(c, t, g):
    a, b = rel(1, 3), rel(1, 5)
    if t < a:
        r.date_card(c, t, "JUN", "2026", "NEW GRAMMY CATEGORY", (40, 28, 70))
    elif t < b:
        lt = t - a
        c.paste(gradient((34, 22, 60), (6, 4, 12)))
        paste_center(c, card(860, 560, "NEW AWARD"), W / 2, 900, *pop(lt))
        for k, txt in enumerate(("BEST ASIAN", "POP MUSIC", "PERFORMANCE")):
            paste_center(c, T(("cat", txt), txt, 92, fill=DARK, weight="Black"), W / 2, 830 + k * 105, alpha=ease((lt - 0.1 * k) / 0.2))
        punch(c, "n100", "ONE OF 100 CATEGORIES", 520, 56, lt, color=GOLD, stroke=5) if False else None
    else:
        lt = t - b
        c.paste(r.NIGHT)
        stars(c, t, 30)
        for k, (txt, col) in enumerate((("K-POP", (255, 90, 140)), ("J-POP", (255, 190, 70)), ("C-POP", (90, 200, 255)))):
            paste_center(c, pill(txt, 110, col), W / 2, 700 + k * 230, *pop(lt - 0.25 * k))
        label(c, "ITS FIRST AWARD FOR", 480, 54, WHITE, lt)

def s_catch(c, t, g):
    a = rel(2, 2)
    c.paste(gradient((26, 22, 34), (5, 4, 10)))
    if t < a:
        punch(c, "catch", "THE CATCH?", 800, 140, t, color=GOLD, stroke=7)
        paste_center(c, E_EYES.resize((170, 170)), W / 2, 1050, *pop(t - 0.5))
    else:
        lt = t - a
        d = ImageDraw.Draw(c, "RGBA")
        paste_center(c, card(760, 340, "ASIAN LANGUAGE", headcol=(40, 140, 80)), W / 2, 700, *pop(lt))
        paste_center(c, T("ok", "✓" , 180, fill=GREEN, weight="Black") if False else pill("MEANINGFUL USE", 70, GREEN, WHITE), W / 2, 760, *pop(lt - 0.2))
        e = rel(2, 4) - a
        paste_center(c, card(760, 340, "ENGLISH HITS", headcol=(150, 40, 40)), W / 2, 1120, *pop(lt - 0.5))
        if lt > e:
            paste_center(c, stamp("LEFT OUT", 110, RED), W / 2, 1120, *pop(lt - e))

def s_july(c, t, g):
    a, b = rel(3, 3), rel(3, 5)
    if t < a:
        r.date_card(c, t, "JUL", "2026", "BTS SAYS NO", (50, 24, 80))
        if t > 1.2:
            paste_center(c, stamp("NOT SUBMITTING", 80, RED), W / 2, 820, *pop(t - 1.2))
    elif t < b:
        lt = t - a
        c.paste(gradient((28, 20, 50), (5, 4, 10)))
        paste_center(c, card(760, 560, "2027 GRAMMYS"), W / 2, 880, *pop(lt))
        paste_center(c, T("ent", "ENTRY", 130, fill=(190, 190, 200), weight="Black"), W / 2, 880, alpha=ease(lt / 0.3))
        paste_center(c, stamp("WON'T SUBMIT", 100, RED), W / 2, 960, *pop(lt - 0.5))
    else:
        lt = t - b
        c.paste(r.NIGHT)
        d = ImageDraw.Draw(c, "RGBA")
        for k, (txt, y) in enumerate((("REGION", 700), ("LANGUAGE", 960))):
            x = 540 + 40 * math.sin(lt * 2 + k) * (1 - ease(lt / 1.6))
            paste_center(c, card(700, 200, "SORTED BY") if False else pill(txt, 90, (245, 240, 228)), x, y, *pop(lt - 0.3 * k))
        paste_center(c, stamp("NO LABELS", 100, GOLD, -4), W / 2, 1230, *pop(lt - 0.9))
        label(c, "HOPING SONGS AREN'T", 520, 56, WHITE, lt)

def s_ceo(c, t, g):
    a = rel(4, 3)
    c.paste(gradient((30, 28, 40), (5, 5, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    layer = Image.new("RGBA", (340, 520), (0, 0, 0, 0))
    person(ImageDraw.Draw(layer), 170, 120, (120, 130, 160, 255), 1.2)
    if t < a:
        paste_center(c, layer, W / 2, 1000, *pop(t))
        paste_center(c, E_SAD.resize((190, 190)), W / 2, 700, *pop(t - 0.4))
        label(c, "GRAMMY CEO", 1250, 64, WHITE, t - 0.2)
        punch(c, "sad", "SADDENED", 500, 110, t - 0.3, color=GOLD, stroke=6) if t > 0.3 else None
    else:
        lt = t - a
        paste_center(c, E_SHIELD.resize((330, 330)), W / 2, 860, *pop(lt))
        punch(c, "def", "DEFENDS IT", 520, 120, lt, color=WHITE, stroke=6)
        label(c, "THE NEW CATEGORY", 1180, 60, GOLD, lt - 0.2)

def s_ph(c, t, g):
    c.paste(r.NIGHT)
    stars(c, t, 30)
    names = (("CUP OF JOE", (255, 190, 70)), ("SB19", (90, 200, 255)), ("BINI", (255, 110, 160)))
    for k, (n, col) in enumerate(names):
        lt = t - 0.5 - 0.9 * k
        if lt > 0:
            paste_center(c, pill(n, 100, col), W / 2, 760 + 190 * k, *pop(lt))

def s_nov16(c, t, g):
    r.date_card(c, t, "16", "NOV", "NOMINATIONS DROP", (60, 28, 18))
    paste_center(c, E_BELL.resize((170, 170)), 850, 560, *pop(t - 0.6))

def s_take(c, t, g):
    a, b = rel(7, 2), rel(7, 3)
    c.paste(r.THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    if t < a:
        punch(c, "mt", "MY TAKE", 640, 130, t, color=WHITE)
        paste_center(c, E_EYES.resize((170, 170)), W / 2, 900, *pop(t - 0.3))
    elif t < b:
        lt = t - a
        d.polygon([(W / 2 - 60, 600), (W / 2 + 60, 600), (W / 2 + 380, 1250), (W / 2 - 380, 1250)], fill=(255, 235, 160, int(90 * ease(lt / 0.4))))
        paste_center(c, E_SPOT.resize((220, 220)), W / 2, 560, *pop(lt))
        paste_center(c, person_img(), W / 2, 1060, *pop(lt - 0.2))
        punch(c, "spot", "SPOTLIGHT", 420, 90, lt, color=GOLD, stroke=5)
    else:
        lt = t - b
        d.rounded_rectangle([W / 2 - 330, 760, W / 2 + 330, 1240], 24, fill=(120, 90, 60, 255), outline=(70, 50, 30, 255), width=8)
        d.rectangle([W / 2 - 330, 820, W / 2 + 330, 840], fill=(90, 65, 40, 255))
        paste_center(c, person_img(), W / 2, 1010, *pop(lt))
        punch(c, "box", "OR A BOX", 560, 100, lt, color=WHITE, stroke=6, emoji=E_BOX.resize((110, 110)))

_PI = None
def person_img():
    global _PI
    if _PI is None:
        _PI = Image.new("RGBA", (340, 520), (0, 0, 0, 0))
        person(ImageDraw.Draw(_PI), 170, 120, PURPLE + (255,), 1.2)
    return _PI

def s_q(c, t, g):
    c.paste(r.NIGHT)
    stars(c, t, 30)
    punch(c, "sq", "SPOTLIGHT OR BOX?", 520, 66, t, color=WHITE, stroke=6)
    paste_center(c, pill("SPOTLIGHT", 62, GOLD), 270, 860, *pop(t - 0.2))
    paste_center(c, pill("BOX", 62, ICE), 810, 860, *pop(t - 0.5))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    stars(c, t, 30)
    punch(c, "sun7", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.9:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.9) / 0.3))

r.SCENES = [
    (0.0, ST[1], s_hook), (ST[1], ST[2], s_june), (ST[2], ST[3], s_catch), (ST[3], ST[4], s_july),
    (ST[4], ST[5], s_ceo), (ST[5], ST[6], s_ph), (ST[6], ST[7], s_nov16), (ST[7], ST[8], s_take),
    (ST[8], ST[9], s_q), (ST[9], DUR + 0.1, s_outro),
]
r.CALLOUTS = [
    (chunk_t(1, 3), ST[2] - 0.1, "c1", "BEST ASIAN POP MUSIC PERFORMANCE", None),
    (chunk_t(2, 1), ST[3] - 0.1, "c2", "ASIAN-LANGUAGE RULE (REPORTED)", None),
    (chunk_t(3, 1), ST[4] - 0.1, "c3", "BTS: NO 2027 SUBMISSION", None),
    (ST[5] + 0.3, ST[6] - 0.1, "c4", "REPORTEDLY ENTERED", None),
    (ST[6], ST[7] - 0.1, "c5", "NOMINATIONS: NOV 16", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s007_{s}.png")
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
