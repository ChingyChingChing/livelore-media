"""Live Lore Short 008 (Hong Kong's Symphony of Lights ends) — reuses render.py's engine/style; only scenes, callouts and timings differ.
Usage: python3 render008.py OUT.mp4 [start end]  |  python3 render008.py stills t1 t2 ...
All visuals drawn in code (generic skyline, beams, fireworks; no logos, photos, footage or real building likenesses). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments008.json"))
ST = [s[0] for s in SEG]
CY, MAG, GRN = (90, 220, 255), (255, 90, 190), (120, 255, 150)

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

E_MOON, E_QUEST, E_SPARK, E_BULB, E_EYES = (emoji(c, 150) for c in "🌙❓✨💡👀")

# ---------- harbour art ----------
def skyline_layer(seed, base, color, w=W + 200):
    return r.skyline(seed, base, color, w)
BACK = skyline_layer(5, 1330, (12, 16, 34, 255))
FRONT = skyline_layer(9, 1420, (5, 7, 16, 255))
WATER = gradient((8, 12, 30), (2, 3, 8), W, 520).convert("RGBA")

def harbour(c, t, lit=1.0, beams=True):
    """Night harbour: back skyline, sweeping colour beams, front skyline, water with reflections. lit in 0..1 = beams/lights on."""
    c.paste(gradient((10, 14, 34), (3, 4, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    c.alpha_composite(BACK, (-100, 0))
    if beams and lit > 0.02:
        cols = (CY, MAG, GRN, GOLD)
        for k in range(8):
            x0 = 80 + k * 130
            ang = math.sin(t * 1.7 + k * 0.9) * 170
            col = cols[k % 4]
            a = int(70 * lit)
            d.polygon([(x0 - 8, 1330), (x0 + 8, 1330), (x0 + ang + 55, 380), (x0 + ang - 55, 380)], fill=col + (a,))
    c.alpha_composite(FRONT, (-100, 0))
    c.alpha_composite(WATER, (0, 1400))
    if lit > 0.02:
        for k in range(8):  # reflections
            x0 = 80 + k * 130 + math.sin(t * 2 + k) * 14
            d.rectangle([x0 - 10, 1430, x0 + 10, 1900], fill=((CY, MAG, GRN, GOLD)[k % 4]) + (int(40 * lit),))

def stars(c, t, n=30, seed=3):
    d = ImageDraw.Draw(c, "RGBA")
    rs = random.Random(seed)
    for _ in range(n):
        x, y, ph = rs.uniform(0, W), rs.uniform(0, 700), rs.uniform(0, 6)
        a = int(110 + 110 * math.sin(t * 3 + ph))
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 235, 170, max(0, a)))

def card(w, h, head, fill=(245, 240, 228), headcol=(70, 40, 140)):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=fill + (255,))
    d.rounded_rectangle([0, 0, w, 120], 40, fill=headcol + (255,))
    d.rectangle([0, 80, w, 120], fill=headcol + (255,))
    tt = T(("ch", head, w), head, 52, fill=WHITE, weight="Black")
    im.alpha_composite(tt, ((w - tt.width) // 2, 28))
    return im

def fireworks(c, t, n=5):
    d = ImageDraw.Draw(c, "RGBA")
    cols = (GOLD, CY, MAG, GRN, WHITE)
    for k in range(n):
        lt = (t * 0.9 + k * 0.37) % 1.6
        rs = random.Random(k * 7 + int((t * 0.9 + k * 0.37) // 1.6) * 31)
        cx, cy = rs.uniform(200, 880), rs.uniform(520, 1000)
        col = cols[rs.randint(0, 4)]
        e = ease(lt / 0.9)
        al = int(255 * max(0, 1 - lt / 1.5))
        for j in range(18):
            ang = j * math.pi / 9
            r0, r1 = 20 + 150 * e, 60 + 230 * e
            d.line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)],
                   fill=col + (al,), width=7)

def date_card(c, t, big, small, sub, tint, size=300):
    c.paste(gradient(tint, (4, 4, 8)))
    d = ImageDraw.Draw(c, "RGBA")
    for y in range(0, H, 46):
        off = int(t * 20) % 46
        d.line([(0, y + off), (W, y + off)], fill=(255, 255, 255, 10), width=2)
    cw, ch = 640, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(245, 240, 228, 255))
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=(200, 40, 40, 255))
    dd.rectangle([0, 120, cw, 170], fill=(200, 40, 40, 255))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 230 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1310, 56, WHITE, t - 0.25)

# ---------- scenes (local t = seconds since scene start) ----------
def s_hook_a(c, t, g):
    harbour(c, g)
    stars(c, g)
    punch(c, "hk", "HONG KONG", 560, 150, t, color=WHITE, stroke=7)
    paste_center(c, pill("LIGHT SHOW", 90, GOLD), W / 2, 760, *pop(t - 0.5))

def s_hook_b(c, t, g):
    lit = max(0.0, 1 - t / 2.2)
    harbour(c, g, lit)
    stars(c, g)
    punch(c, "end", "IS ENDING", 560, 150, t, color=WHITE, stroke=7)
    paste_center(c, E_MOON.resize((150, 150)), W / 2, 760, *pop(t - 0.4))

def s_twist(c, t, g):
    c.paste(gradient((34, 22, 60), (5, 4, 12)))
    stars(c, g)
    punch(c, "twist", "THE TWIST", 520, 130, t, color=GOLD, stroke=6)
    q = lt = t - 0.9
    paste_center(c, pill("REPLACEMENT", 100, WHITE), W / 2, 900, *pop(t - 0.7))
    for k, x in enumerate((320, 540, 760)):
        paste_center(c, E_QUEST.resize((190, 190)), x, 1130, *pop(t - 1.2 - 0.25 * k))

def s_2004(c, t, g):
    date_card(c, t, "2004", "SINCE", "EVERY NIGHT", (20, 40, 70), size=190)

def s_nightly(c, t, g):
    harbour(c, g)
    stars(c, g)
    punch(c, "vh", "VICTORIA HARBOUR", 520, 100, t, color=WHITE, stroke=6)
    paste_center(c, pill("EVERY NIGHT", 80, CY), W / 2, 700, *pop(t - 0.4))

def s_dozens(c, t, g):
    c.paste(gradient((10, 14, 34), (3, 4, 10)))
    d = ImageDraw.Draw(c, "RGBA")
    rs = random.Random(21)
    n = 0
    for col in range(9):
        for row in range(7):
            lt = t - 0.05 * (col * 7 + row)
            x, y = 80 + col * 110, 600 + row * 115
            w_, h_ = 80, 90
            on = lt > 0
            fill = ((CY, MAG, GRN, GOLD)[(col + row) % 4] + (255,)) if on else (30, 36, 60, 255)
            d.rounded_rectangle([x, y, x + w_, y + h_], 12, fill=fill)
            n += on
    punch(c, "dz", "DOZENS OF BUILDINGS", 480, 76, t, color=WHITE, stroke=6)

def s_sides(c, t, g):
    harbour(c, g)
    d = ImageDraw.Draw(c, "RGBA")
    paste_center(c, pill("BOTH SIDES OF THE HARBOUR", 50, WHITE), W / 2, 560, *pop(t))
    if t > 0.9:
        paste_center(c, pill("LOCALS", 80, GOLD), 300, 760, *pop(t - 0.9))
    if t > 1.7:
        paste_center(c, pill("VISITORS", 80, CY), 760, 900, *pop(t - 1.7))

def s_record(c, t, g):
    c.paste(r.NIGHT)
    stars(c, g)
    paste_center(c, r.AWARD, W / 2, 900, 1.0 + 0.03 * t, ease(t / 0.2))
    punch(c, "wr", "WORLD RECORD", 480, 110, t, color=GOLD, stroke=6)
    paste_center(c, stamp("2005", 120, GOLD, -6), W / 2, 1220, *pop(t - 0.6))

def s_largest(c, t, g):
    c.paste(gradient((40, 26, 60), (6, 4, 12)))
    stars(c, g)
    for k, (txt, col) in enumerate((("LARGEST", GOLD), ("PERMANENT", WHITE), ("LIGHT + SOUND SHOW", CY))):
        paste_center(c, pill(txt, 84 if k < 2 else 62, col), W / 2, 700 + k * 190, *pop(t - 0.25 * k))

def s_feb(c, t, g):
    date_card(c, t, "FEB", "2026", "HONG KONG BUDGET", (60, 24, 24), size=210)

def s_retired(c, t, g):
    harbour(c, g, max(0.0, 0.8 - t * 0.3))
    paste_center(c, stamp("RETIRED", 140, RED, -8), W / 2, 760, *pop(t))
    paste_center(c, pill("THIS YEAR", 90, WHITE), W / 2, 1010, *pop(t - 0.4))

def s_nov18(c, t, g):
    date_card(c, t, "18", "NOV", "WEDNESDAY · FINAL NIGHT", (28, 30, 70))

def s_fire(c, t, g):
    harbour(c, g, 0.5, beams=True)
    fireworks(c, t)
    punch(c, "fw", "WITH FIREWORKS", 520, 100, t, color=WHITE, stroke=6)
    paste_center(c, pill("REPORTEDLY", 60, GOLD), W / 2, 680, *pop(t - 0.5))

def s_new(c, t, g):
    c.paste(gradient((14, 30, 50), (3, 4, 10)))
    stars(c, g)
    punch(c, "nls", "NEW LIGHT SHOWS", 520, 100, t, color=WHITE, stroke=6)
    for k, (col, x) in enumerate(((CY, 250), (MAG, 540), (GOLD, 830))):
        paste_center(c, E_BULB.resize((190, 190)), x, 900, *pop(t - 0.5 - 0.3 * k))
        d = ImageDraw.Draw(c, "RGBA")
        d.ellipse([x - 100, 1040, x + 100, 1060], fill=col + (180,))

def s_tba(c, t, g):
    c.paste(gradient((26, 22, 34), (5, 4, 10)))
    paste_center(c, pill("DETAILS", 100, WHITE), W / 2, 700, *pop(t))
    paste_center(c, stamp("NOT SHARED YET", 100, RED, -6), W / 2, 960, *pop(t - 0.5))
    paste_center(c, E_EYES.resize((170, 170)), W / 2, 1180, *pop(t - 1.0))

def s_take(c, t, g):
    harbour(c, g, 0.6)
    paste_center(c, E_MOON.resize((190, 190)), 820, 380, *pop(t))
    punch(c, "mt", "MY TAKE", 640, 140, t, color=WHITE, stroke=7)

def s_goodnight(c, t, g):
    harbour(c, g, max(0.0, 0.7 - t * 0.25))
    stars(c, g)
    punch(c, "gn", "HOW THE HARBOUR", 520, 80, t, color=WHITE, stroke=6)
    paste_center(c, pill("SAYS GOODNIGHT", 84, GOLD), W / 2, 700, *pop(t - 0.4))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    stars(c, g)
    punch(c, "sq", "WILL YOU MISS IT?", 560, 76, t, color=WHITE, stroke=6)
    paste_center(c, pill("YES", 80, GOLD), 300, 860, *pop(t - 0.15))
    paste_center(c, pill("NOT REALLY", 80, ICE), 760, 860, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    stars(c, g)
    punch(c, "sun8", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.9:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.9) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

# scene boundaries (global seconds): each starts at a spoken chunk so visuals match the words
B = [0.0, at(0, 2), ST[1], ST[2], at(2, 2), ST[3], at(3, 3), ST[4], at(4, 2), ST[5], at(5, 2),
     ST[6], at(6, 3), ST[7], at(7, 3), ST[8], at(8, 3), ST[9], ST[10], DUR + 0.1]
FNS = [s_hook_a, s_hook_b, s_twist, s_2004, s_nightly, s_dozens, s_sides, s_record, s_largest, s_feb, s_retired,
       s_nov18, s_fire, s_new, s_tba, s_take, s_goodnight, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[4] - 0.1, "c1", "LIT UP SINCE 2004", None),
    (ST[4], ST[5] - 0.1, "c2", "GUINNESS RECORD · 2005", None),
    (ST[5], ST[6] - 0.1, "c3", "RETIRING IN 2026", None),
    (ST[6], ST[7] - 0.1, "c4", "FINAL NIGHT: NOV 18 (REPORTED)", None),
    (ST[7], ST[8] - 0.1, "c5", "NEW SHOWS: DETAILS TBA", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s008_{s}.png")
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
