"""Live Lore Short 013 (Godzilla Minus Zero: record US opening, 73% drop, past $100M worldwide) - reuses render.py's engine/style.
Usage: python3 render013.py OUT.mp4 [start end]  |  python3 render013.py stills t1 t2 ...
All visuals drawn in code (generic kaiju silhouette, storm clouds, skyline, bar/line charts, date cards, ticket stubs, emoji;
no film footage, posters, key art, logos or photos). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
CYAN = (90, 200, 255)
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments013.json"))
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

ATOMIC = (110, 200, 255)
E_GLOBE, E_FIRE, E_POPCORN, E_EYES, E_DOWN, E_TROPHY, E_CROWD = (emoji(c, 150) for c in "🌍🔥🍿👀📉🏆🎟")

# ---------- art ----------
CHART_BG = gradient((16, 18, 34), (3, 3, 8))
RED_BG = gradient((60, 10, 16), (6, 2, 3))
JP_BG = gradient((245, 240, 232), (205, 198, 188))
GLOW_BG = gradient((10, 30, 50), (2, 5, 10))
CITY = r.skyline(21, 1650, (5, 7, 14, 255))

def screen(c, t, sub=None):
    """Generic cinema: dark room, glowing screen with the kaiju silhouette, rows of seat backs."""
    c.paste(r.THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    sx0, sy0, sx1, sy1 = 80, 380, W - 80, 1000
    scr = gradient((60, 110, 170), (20, 40, 70), sx1 - sx0, sy1 - sy0).convert("RGBA")
    k = r.kaiju(0.75, (6, 10, 20, 255))
    scr.alpha_composite(k, (int(220 + 20 * t), 30))
    c.alpha_composite(scr, (sx0, sy0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon([(sx0, sy1), (sx1, sy1), (W + 200, H), (-200, H)], fill=(80, 130, 200, 40))
    c.alpha_composite(glow)
    if sub:
        s_img = T(("sub", sub), sub, 46, fill=(255, 245, 160), weight="Bold", stroke=4)
        c.alpha_composite(s_img, (int(W / 2 - s_img.width / 2), sy1 - 90))
    for row in range(3):
        y = 1120 + row * 120
        for x in range(-40 + (row % 2) * 60, W + 40, 120):
            d.rounded_rectangle([x, y, x + 100, y + 160], 24, fill=(8, 8, 12, 255))

def kaiju_storm(c, t, flash=(0.0,)):
    r.storm_base(c, t, flash_times=flash)
    rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rim).ellipse([100, 700, 900, 1500], fill=(110, 170, 255, 220))
    c.alpha_composite(rim.filter(ImageFilter.GaussianBlur(90)))
    paste_center(c, r.KAIJU, 480 + 20 * t, 1240, scale=1.0 + 0.04 * t)
    c.alpha_composite(CITY.crop((60, 0, 60 + W, H)))

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

def hbars(c, t, rows, top=560, gap=230, maxw=600):
    """rows: [(name, value, max, color, value_label)] horizontal bars, real proportions."""
    d = ImageDraw.Draw(c, "RGBA")
    k = ease(t / 0.8)
    for i, (nm, v, mx, col, vl) in enumerate(rows):
        y = top + i * gap
        lb = T(("hb", nm), nm, 52, fill=WHITE, weight="Black")
        c.alpha_composite(lb, (120, y))
        w = int(maxw * v / mx * k)
        d.rounded_rectangle([120, y + 75, 120 + max(w, 20), y + 165], 18, fill=col + (255,))
        if k > 0.6:
            vt = T(("hv", vl), vl, 60, fill=GOLD if col != GOLD else WHITE, weight="Black")
            c.alpha_composite(vt, (min(120 + w + 24, W - vt.width - 30), y + 88))

def line_drop(c, t):
    """Weekend 1 -> weekend 2 line, real proportion (100% -> ~27%)."""
    d = ImageDraw.Draw(c, "RGBA")
    x0, x1, base, top = 220, 860, 1250, 560
    y0 = top
    y1 = base - (base - top) * 0.27
    k = ease(t / 0.7)
    d.line([(x0 - 40, base), (x1 + 60, base)], fill=(80, 90, 120, 255), width=6)
    xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    d.line([(x0, y0), (xe, ye)], fill=RED + (255,), width=18)
    for (x, y) in ((x0, y0), (xe, ye)):
        d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=WHITE + (255,))
    for txt, x in (("WKND 1", x0), ("WKND 2", x1)):
        lb = T(("ld", txt), txt, 44, fill=WHITE, weight="Bold")
        c.alpha_composite(lb, (int(x - lb.width / 2), base + 24))

def podium(c, t):
    d = ImageDraw.Draw(c, "RGBA")
    k = ease(t / 0.5)
    spec = [(W / 2 - 300, 300, "2", (170, 170, 185)), (W / 2, 420, "1", (170, 170, 185)), (W / 2 + 300, 200, "3", RED)]
    for cx, h, n, col in spec:
        hh = h * k
        d.rectangle([cx - 135, 1250 - hh, cx + 135, 1250], fill=col + (255,))
        if k > 0.7:
            lb = T(("pd", n), n, 120, fill=WHITE, weight="Black")
            c.alpha_composite(lb, (int(cx - lb.width / 2), int(1250 - hh + 20)))
    paste_center(c, r.kaiju(0.28, (230, 230, 240, 255)), W / 2 + 300, 1250 - 200 * k - 120, alpha=ease((t - 0.4) / 0.2))

def ticket(text, col=GOLD, rot=0):
    w, h = 520, 230
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 24, fill=col + (255,))
    for y in range(18, h, 36):
        d.ellipse([w - 150 - 8, y, w - 150 + 8, y + 16], fill=(0, 0, 0, 0))
    d.ellipse([-30, h / 2 - 30, 30, h / 2 + 30], fill=(0, 0, 0, 0))
    d.ellipse([w - 30, h / 2 - 30, w + 30, h / 2 + 30], fill=(0, 0, 0, 0))
    a = r.text_img(text, 70, fill=DARK)
    im.alpha_composite(a, ((w - 150 - a.width) // 2, (h - a.height) // 2))
    adm = r.text_img("ADMIT 1", 30, fill=DARK, weight="Bold")
    adm = adm.rotate(90, expand=True)
    im.alpha_composite(adm, (w - 75 - adm.width // 2, (h - adm.height) // 2))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

TICKETS = [ticket("KAIJU", GOLD, -10), ticket("GODZ", (240, 240, 235), 6), ticket("IMAX", CYAN, -4)]

# ---------- scenes ----------
def s_hook(c, t, g):
    kaiju_storm(c, t, flash=(0.0, 1.6))
    c.alpha_composite(r.BOLTS[1 if t < 1.6 else 2])
    punch(c, "h1", "$30M+", 700, 200, t, color=GOLD, stroke=12)
    label(c, "ONE WEEKEND · NORTH AMERICA", 880, 46, WHITE, t - 0.3)

def s_subs(c, t, g):
    screen(c, t, sub="[Japanese dialogue · English subtitles]")
    paste_center(c, pill("SUBTITLED", 90, GOLD), W / 2, 560, *pop(t))

def s_crash(c, t, g):
    c.paste(RED_BG)
    punch(c, "c73", "-73%", 780, 330, t, color=WHITE, stroke=12)
    paste_center(c, E_DOWN.resize((200, 200)), W / 2, 1120, *pop(t - 0.3))

def s_title(c, t, g):
    c.paste(r.NIGHT)
    c.alpha_composite(CITY.crop((100, 120, 100 + W, H + 120)))
    punch(c, "t1", "GODZILLA", 700, 150, t, color=WHITE)
    punch(c, "t2", "MINUS ZERO", 870, 150, max(0, t - 0.4), color=ATOMIC)

def s_nov6(c, t, g):
    date_card2(c, t, "6", "NOV 2026", "NORTH AMERICA RELEASE", (20, 40, 70))

def s_record(c, t, g):
    c.paste(GLOW_BG)
    paste_center(c, r.AWARD, W / 2, 760, *pop(t, 0.35))
    paste_center(c, pill("ALL-TIME US RECORD", 80, GOLD), W / 2, 1150, *pop(t - 0.4))

def s_foreign(c, t, g):
    screen(c, t, sub="[English subtitles]")
    paste_center(c, E_GLOBE.resize((170, 170)), 860, 520, *pop(t - 0.2))
    paste_center(c, pill("NON-ENGLISH", 90, GOLD), W / 2, 560, *pop(t))

def s_3x(c, t, g):
    c.paste(GLOW_BG)
    punch(c, "x3", "~3X", 760, 380, t, color=GOLD, stroke=12)
    label(c, "VS THE LAST ONE'S OPENING", 1040, 52, WHITE, t - 0.3)

def s_m1a(c, t, g):
    kaiju_storm(c, t, flash=(0.1,))
    c.alpha_composite(r.BOLTS[0])
    punch(c, "m1q", "MINUS ONE?", 640, 150, t, color=ICE, stroke=8)
    label(c, "2023 · WHOLE WORLDWIDE RUN", 820, 52, WHITE, t - 0.3)

def s_hero(c, t, g):
    c.paste(CHART_BG)
    label(c, "US OPENING WEEKEND", 480, 56, WHITE, t)
    hbars(c, t, [("HERO (2004)", 17.8, 31.6, (90, 100, 130), "~$18M"),
                 ("MINUS ZERO (2026)", 31.6, 31.6, RED, "$30M+")], top=600)

def s_triple(c, t, g):
    c.paste(CHART_BG)
    label(c, "US OPENING WEEKEND", 480, 56, WHITE, t)
    hbars(c, t, [("MINUS ONE (2023)", 11.4, 31.6, (90, 100, 130), "$11.4M"),
                 ("MINUS ZERO (2026)", 31.6, 31.6, RED, "$30M+")], top=600)

def s_w(c, t, g):
    c.paste(GLOW_BG)
    punch(c, "bigw", "W", 800, 520, t, color=GREEN, stroke=14)

def s_wk2(c, t, g):
    c.paste(r.NIGHT)
    paste_center(c, stamp("WEEKEND 2", 170, RED, -6), W / 2, 820, *pop(t))

def s_drop(c, t, g):
    c.paste(CHART_BG)
    line_drop(c, t)
    if t > 0.6:
        paste_center(c, pill("~$8.3M", 90, GOLD), 700, 1000, *pop(t - 0.6))
    label(c, "US WEEKEND GROSS", 480, 56, WHITE, t)

def s_third(c, t, g):
    c.paste(CHART_BG)
    podium(c, t)
    label(c, "WEEKEND OF NOV 13–15", 480, 56, WHITE, t)

def s_zoom(c, t, g):
    r.storm_base(c, t)
    paste_center(c, r.KAIJU, W / 2, 1100, scale=1.3 - 0.45 * ease(t / 1.2))
    c.alpha_composite(CITY.crop((60, 0, 60 + W, H)))
    paste_center(c, stamp("NOT COOKED", 130, GREEN, 6), W / 2, 620, *pop(t - 0.3))

def s_100m(c, t, g):
    c.paste(GLOW_BG)
    v = 100 * ease(t / 0.9)
    punch(c, ("m100", int(v)), f"${int(v)}M", 740, 260, min(t, 0.3) if t < 0.9 else t, color=GOLD, stroke=10)
    paste_center(c, E_GLOBE.resize((200, 200)), W / 2, 1060, 1.0 + 0.05 * math.sin(g * 4), ease(t / 0.2))
    label(c, "WORLDWIDE", 1230, 64, WHITE, t - 0.3)

def s_japan(c, t, g):
    c.paste(JP_BG)
    d = ImageDraw.Draw(c, "RGBA")
    rad = 260 * (0.8 + 0.2 * ease(t / 0.4))
    d.ellipse([W / 2 - rad, 820 - rad, W / 2 + rad, 820 + rad], fill=(200, 30, 45, 255))
    paste_center(c, cjk("日本", 200, WHITE), W / 2, 820, *pop(t - 0.2))

def s_yen(c, t, g):
    c.paste(gradient((80, 14, 22), (12, 3, 4)))
    punch(c, "yen4", "¥4B+", 740, 300, t, color=GOLD, stroke=10)
    label(c, "JAPAN BOX OFFICE · PER TOHO", 980, 52, WHITE, t - 0.3)

def s_tickets(c, t, g):
    c.paste(gradient((40, 30, 20), (8, 6, 4)))
    for i, (tk, x, y) in enumerate(zip(TICKETS, (320, 760, 540), (640, 700, 940))):
        paste_center(c, tk, x, y - 400 * (1 - ease((t - i * 0.15) / 0.35)), alpha=ease((t - i * 0.15) / 0.15))
    if t > 0.6:
        paste_center(c, pill("2.5M TICKETS · 13 DAYS", 70, GOLD), W / 2, 1220, *pop(t - 0.6))

def s_m1(c, t, g):
    c.paste(CHART_BG)
    cw, ch = 760, 560
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 150], 36, fill=(70, 80, 110, 255))
    dd.rectangle([0, 110, cw, 150], fill=(70, 80, 110, 255))
    a = r.text_img("MINUS ONE · 2023", 64, fill=WHITE, weight="ExtraBold")
    cd.alpha_composite(a, ((cw - a.width) // 2, 40))
    b = r.text_img("~$105M", 150, fill=DARK)
    cd.alpha_composite(b, ((cw - b.width) // 2, 200))
    e = r.text_img("WHOLE WORLDWIDE RUN", 46, fill=(90, 90, 90), weight="Bold", spacing=4)
    cd.alpha_composite(e, ((cw - e.width) // 2, 450))
    paste_center(c, cd, W / 2, 820, scale=0.85 + 0.15 * ease(t / 0.3) + 0.02 * t)

def s_neck(c, t, g):
    c.paste(CHART_BG)
    label(c, "WORLDWIDE GROSS", 480, 56, WHITE, t)
    hbars(c, t, [("MINUS ONE (FULL RUN)", 105, 105, (90, 100, 130), "~$105M"),
                 ("MINUS ZERO (2 WKNDS)", 100, 105, RED, "$100M+")], top=600)
    if t > 1.0:
        paste_center(c, E_EYES.resize((170, 170)), W / 2, 1200, *pop(t - 1.0))

def s_take(c, t, g):
    screen(c, t)
    d = ImageDraw.Draw(c, "RGBA"); d.rectangle([0, 0, W, H], fill=(0, 0, 0, 110))
    punch(c, "mt13", "MY TAKE", 640, 170, t, color=WHITE, stroke=6)
    paste_center(c, E_POPCORN.resize((180, 180)), W / 2, 880, *pop(t - 0.3))

def s_hype(c, t, g):
    c.paste(RED_BG)
    paste_center(c, stamp("FLOP", 150, (150, 150, 160), -6), W / 2, 640, *pop(t))
    if t > 0.35:
        d = ImageDraw.Draw(c, "RGBA")
        k = ease((t - 0.35) / 0.2)
        d.line([(W / 2 - 260, 560), (W / 2 - 260 + 520 * k, 560 + 160 * k)], fill=RED + (255,), width=22)
    if t > 0.7:
        paste_center(c, stamp("HYPE", 200, GOLD, 7), W / 2, 1010, *pop(t - 0.7))
        paste_center(c, E_FIRE.resize((150, 150)), 860, 820, *pop(t - 0.9))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq13", "SEEN IT YET?", 540, 120, t, color=WHITE, stroke=6)
    paste_center(c, pill("OPENING WEEKEND", 84, GOLD), W / 2, 820, *pop(t - 0.15))
    paste_center(c, pill("STILL WAITING", 84, CYAN), W / 2, 1060, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun13", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.5:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.5) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 2), at(0, 5), ST[1], at(1, 2), ST[2], at(2, 2), at(2, 5), ST[3], at(3, 2), at(3, 5), ST[4], at(4, 2),
     at(4, 5), ST[5], at(5, 4), ST[6], at(6, 3), at(6, 5), ST[7], at(7, 3), at(7, 5), ST[8], at(8, 6), ST[9], ST[10],
     DUR + 0.1]
FNS = [s_hook, s_subs, s_crash, s_title, s_nov6, s_record, s_foreign, s_hero, s_3x, s_triple, s_w, s_wk2, s_drop,
       s_third, s_zoom, s_100m, s_japan, s_yen, s_tickets, s_m1a, s_m1, s_neck, s_take, s_hype, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "LIVE-ACTION · NOT IN ENGLISH", None),
    (ST[4], ST[5] - 0.1, "c2", "SECOND WEEKEND · ESTIMATE", None),
    (ST[6], ST[7] - 0.1, "c3", "JAPAN · FIRST 13 DAYS", None),
    (ST[7], ST[8] - 0.1, "c4", "FIGURES ROUNDED", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s013_{s}.png")
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
