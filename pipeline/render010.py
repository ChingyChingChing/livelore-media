"""Live Lore Short 010 (Chiikawa the Movie: Japan's #1 film of 2026, ¥18.79B, #12 all-time) — reuses render.py's engine/style.
Usage: python3 render010.py OUT.mp4 [start end]  |  python3 render010.py stills t1 t2 ...
All visuals drawn in code (generic sparkles, hearts, tickets, cinema seats, bar charts, gift boxes, a generic skyline;
no character art, film footage, posters or logos). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
PINK, CYAN, MINT = (255, 120, 170), (90, 200, 255), (120, 225, 190)
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments010.json"))
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

E_TROPHY, E_BOOM, E_SPARK, E_FILM, E_TICKET, E_GLASS, E_GIFT, E_HEART, E_EYES, E_POP = (
    emoji(c, 150) for c in "🏆💥✨🎬🎟🔍🎁💖👀🍿")

# ---------- art ----------
PASTEL = gradient((255, 214, 230), (170, 210, 255))
CANDY = gradient((60, 30, 90), (10, 6, 24))
HK_SKY = gradient((40, 30, 90), (8, 6, 20))
CITY = r.skyline(7, 1350, (6, 6, 16, 255))

def candy(c, t):
    c.paste(CANDY)
    d = ImageDraw.Draw(c, "RGBA")
    rnd = random.Random(4)
    for k in range(26):  # drifting dots
        x = (rnd.random() * W + t * 30 * (1 + k % 3)) % W
        y = (rnd.random() * H - t * 40 * (1 + k % 2)) % H
        rad = 6 + k % 4 * 4
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(PINK if k % 2 else CYAN) + (70,))

def pastel(c, t):
    c.paste(PASTEL)
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(9):
        y = (k * 230 + t * 60) % (H + 200) - 100
        d.ellipse([-80 + (k % 3) * 420, y, 220 + (k % 3) * 420, y + 160], fill=(255, 255, 255, 70))

def heart(d, cx, cy, s, col):
    d.ellipse([cx - s, cy - s * 0.8, cx, cy + s * 0.2], fill=col)
    d.ellipse([cx, cy - s * 0.8, cx + s, cy + s * 0.2], fill=col)
    d.polygon([(cx - s * 0.97, cy - s * 0.15), (cx + s * 0.97, cy - s * 0.15), (cx, cy + s)], fill=col)

def ticket(c, cx, cy, s, col, rot, txt="ADMIT ONE"):
    im = Image.new("RGBA", (420, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 420, 200], 22, fill=col + (255,))
    for y in (0, 200):
        d.ellipse([290, y - 26, 342, y + 26], fill=(0, 0, 0, 0))
    for y in range(20, 190, 22):
        d.line([(316, y), (316, y + 10)], fill=DARK + (160,), width=4)
    tt = r.text_img(txt, 34, fill=DARK)
    im.alpha_composite(tt, (150 - tt.width // 2, 100 - tt.height // 2))
    paste_center(c, im.rotate(rot, expand=True, resample=Image.BICUBIC), cx, cy, s)

def cinema(c, t, lit=1.0):
    c.paste(r.THEATER)
    d = ImageDraw.Draw(c, "RGBA")
    glow = int(200 + 40 * math.sin(t * 6))
    d.rounded_rectangle([110, 380, W - 110, 900], 18, fill=(glow, glow, min(255, glow + 30), int(255 * lit)))
    for row in range(4):
        y = 1120 + row * 110
        for k in range(9):
            x = 80 + k * 115 + (row % 2) * 30
            d.rounded_rectangle([x, y, x + 90, y + 90], 22, fill=(170, 30, 60, 255))
            d.ellipse([x + 15, y - 50, x + 75, y + 10], fill=(20, 18, 30, 255))  # heads

def date_card(c, t, big, small, sub, tint, size=300):
    c.paste(gradient(tint, (4, 4, 8)))
    cw, ch = 640, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=PINK + (255,))
    dd.rectangle([0, 120, cw, 170], fill=PINK + (255,))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 230 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1290, 56, WHITE, t - 0.25)

def hbar(c, x0, y, w, h, frac, col, name, val, t):
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([x0, y, x0 + w * frac, y + h], 20, fill=col + (255,))
    nm = T(("bn", name), name, 52, fill=WHITE, weight="Black")
    c.alpha_composite(nm, (x0, y - nm.height - 14))
    if frac > 0.25:
        v = T(("bv", val), val, 56, fill=DARK, weight="Black")
        c.alpha_composite(v, (int(x0 + w * frac - v.width - 24), int(y + (h - v.height) / 2)))

# ---------- scenes (local t = seconds since scene start) ----------
def s_big(c, t, g):
    candy(c, g)
    punch(c, "b1", "#1 IN JAPAN", 520, 150, t, color=GOLD, stroke=8)
    paste_center(c, E_TROPHY.resize((300, 300)), W / 2, 860, *pop(t - 0.2))
    label(c, "2026 BOX OFFICE", 1110, 62, WHITE, t - 0.4)

def s_notaction(c, t, g):
    candy(c, g)
    paste_center(c, E_BOOM.resize((300, 300)), W / 2, 760, *pop(t))
    paste_center(c, pill("ACTION BLOCKBUSTER?", 72, WHITE), W / 2, 1040, *pop(t - 0.1))
    if t > 0.5:
        d = ImageDraw.Draw(c, "RGBA")
        k = ease((t - 0.5) / 0.25)
        d.line([(W / 2 - 360, 1080), (W / 2 - 360 + 720 * k, 1080 - 520 * k)], fill=RED + (255,), width=24)
        if t > 0.75:
            paste_center(c, stamp("NOPE", 120, RED, 10), W / 2, 520, *pop(t - 0.75))

def s_small(c, t, g):
    pastel(c, g)
    d = ImageDraw.Draw(c, "RGBA")
    for k, (x, y) in enumerate(((300, 700), (780, 760), (540, 1000))):
        if t > k * 0.25:
            s = 70 * pop(t - k * 0.25)[0] * (1 + 0.06 * math.sin(g * 5 + k))
            heart(d, x, y, s, PINK + (255,))
    paste_center(c, E_SPARK.resize((140, 140)), 860, 520, *pop(t - 0.3))
    paste_center(c, pill("SMALL + CUTE", 96, WHITE, PINK), W / 2, 1220, *pop(t - 0.2))

def s_name(c, t, g):
    pastel(c, g)
    card = Image.new("RGBA", (920, 300), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, 920, 300], 36, fill=(255, 255, 255, 240))
    jp = cjk("なんか小さくてかわいいやつ", 66)
    card.alpha_composite(jp, ((920 - jp.width) // 2, 50))
    ro = r.text_img("nanka CHIIsakute KAWAii yatsu", 44, fill=(120, 80, 140), weight="Bold")
    card.alpha_composite(ro, ((920 - ro.width) // 2, 190))
    paste_center(c, card, W / 2, 620, *pop(t))
    if t > 0.7:
        paste_center(c, pill("CHII + KAWA", 96, GOLD), W / 2, 920, *pop(t - 0.7))
    label(c, "= \"SOMETHING SMALL AND CUTE\"", 1110, 50, DARK, t - 1.1)

def s_jul24(c, t, g):
    date_card(c, t, "24", "JUL", "OPENING DAY · JAPAN", (120, 50, 110))

def s_cinema(c, t, g):
    cinema(c, g)
    paste_center(c, E_POP.resize((150, 150)), W / 2, 640, *pop(t))
    paste_center(c, stamp("STILL SHOWING", 100, GOLD, -6), W / 2, 960, *pop(t - 0.5))

def s_yen(c, t, g):
    candy(c, g)
    v = 18.79 * ease(t / 1.1)
    punch(c, ("yen", round(v, 2)), f"¥{v:.2f}B", 760, 200, min(t, 0.3) if t < 1.1 else t, color=GOLD, stroke=8)
    label(c, "JAPAN BOX OFFICE · NOV 8", 960, 54, WHITE, t - 0.3)
    paste_center(c, pill("BILLION YEN", 70, WHITE), W / 2, 520, *pop(t))

def s_tickets(c, t, g):
    candy(c, g)
    rnd = random.Random(10)
    for k in range(8):
        d0 = k * 0.12
        if t > d0:
            x = 160 + rnd.random() * 760
            y = 1250 - 600 * ease((t - d0) / 0.8) + rnd.random() * 120
            ticket(c, x, y, 0.8, (PINK, GOLD, CYAN, MINT)[k % 4], rnd.uniform(-25, 25))
    punch(c, "tk", "12.86M TICKETS", 520, 100, t, color=WHITE, stroke=8)

def s_vs(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "vs", "2026 IN JAPAN", 540, 100, t, color=WHITE, stroke=6)
    k = ease(t / 0.9)
    hbar(c, 110, 760, 860, 140, 0.98 * k, PINK, "CHIIKAWA", "¥18.79B", t)
    hbar(c, 110, 1040, 860, 140, 0.72 * k, CYAN, "THIS YEAR'S CONAN", "", t)
    if t > 1.0:
        paste_center(c, pill("WAY AHEAD", 70, GOLD), W / 2, 1290, *pop(t - 1.0))

def s_boss(c, t, g):
    candy(c, g)
    paste_center(c, E_GLASS.resize((260, 260)), W / 2, 720, *pop(t))
    paste_center(c, stamp("BOX OFFICE BOSS", 100, CYAN, -6), W / 2, 1040, *pop(t - 0.4))

def s_rank(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "at", "ALL-TIME · JAPAN", 520, 90, t, color=WHITE, stroke=6)
    for k, n in enumerate(range(9, 15)):
        y = 660 + k * 115
        d0 = k * 0.08
        if t > d0:
            hit = n == 12
            col = GOLD if hit else (60, 60, 80)
            p = pill(f"#{n}" + ("  CHIIKAWA" if hit else "  · · · · ·"), 64 if hit else 54, col, DARK if hit else WHITE)
            paste_center(c, p, W / 2 + (0 if hit else 0), y, *(pop(t - d0) if not hit else (1.05 + 0.05 * math.sin(g * 6), 1)))

def s_goal(c, t, g):
    candy(c, g)
    punch(c, "goal", "GOAL: ¥20B", 520, 150, t, color=GOLD, stroke=8)
    d = ImageDraw.Draw(c, "RGBA")
    x0, x1, y = 110, W - 110, 900
    d.rounded_rectangle([x0, y - 60, x1, y + 60], 60, fill=(40, 30, 60, 255), outline=WHITE + (255,), width=6)
    f = 0.9395 * ease(t / 1.0)
    d.rounded_rectangle([x0 + 12, y - 48, x0 + 12 + (x1 - x0 - 24) * f, y + 48], 48, fill=PINK + (255,))
    label(c, "NOW ¥18.79B", 1040, 56, WHITE, t - 0.4)
    label(c, "TARGET: END OF 2026", 1140, 50, ICE, t - 0.7)

def s_gifts(c, t, g):
    pastel(c, g)
    punch(c, "sw", "SECRET WEAPON", 470, 96, t, color=DARK)
    n = min(12, int(t / 0.14) + 1)
    for k in range(n):
        x = 200 + (k % 4) * 227
        y = 700 + (k // 4) * 200
        paste_center(c, E_GIFT.resize((150, 150)), x, y, *pop(t - k * 0.14, 0.2))
    if t > 1.8:
        paste_center(c, pill("12 ROUNDS", 90, GOLD), W / 2, 1250, *pop(t - 1.8))

def s_hk(c, t, g):
    c.paste(HK_SKY)
    c.alpha_composite(CITY, (-100, 0))
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(10):  # harbour reflections
        y = 1380 + k * 26
        d.line([(60 + k * 30, y), (W - 60 - k * 20, y)], fill=(PINK if k % 2 else CYAN) + (60,), width=6)
    punch(c, "hk", "HONG KONG", 540, 130, t, color=WHITE, stroke=8)
    paste_center(c, pill("HK$25M+", 120, GOLD), W / 2, 780, *pop(t - 0.4))
    paste_center(c, pill("REPORTEDLY", 54, WHITE), W / 2, 960, *pop(t - 0.7))

def s_take(c, t, g):
    pastel(c, g)
    punch(c, "mt10", "MY TAKE", 560, 150, t, color=DARK)
    paste_center(c, E_HEART.resize((240, 240)), W / 2, 860, *pop(t - 0.4))
    label(c, "CUTE = UNDEFEATED", 1080, 64, DARK, t - 0.8)

def s_ate(c, t, g):
    candy(c, g)
    paste_center(c, stamp("IT ATE", 170, GOLD, -8), W / 2, 700, *pop(t))
    paste_center(c, stamp("NO CAP", 110, PINK, 6), W / 2, 1000, *pop(t - 0.6))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq10", "SEEN IT YET?", 540, 110, t, color=WHITE, stroke=6)
    paste_center(c, pill("YES", 90, GOLD), 320, 860, *pop(t - 0.15))
    paste_center(c, pill("NOT YET", 90, CYAN), 740, 860, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun10", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.9:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.9) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

# scene boundaries (global seconds): each starts at a spoken chunk so visuals match the words
B = [0.0, at(0, 3), at(0, 5), ST[1], ST[2], at(2, 3), ST[3], at(3, 3), ST[4], at(4, 4), ST[5], at(5, 4),
     ST[6], ST[7], ST[8], at(8, 3), ST[9], ST[10], DUR + 0.1]
FNS = [s_big, s_notaction, s_small, s_name, s_jul24, s_cinema, s_yen, s_tickets, s_vs, s_boss, s_rank, s_goal,
       s_gifts, s_hk, s_take, s_ate, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "IN CINEMAS SINCE JUL 24", None),
    (ST[3], ST[4] - 0.1, "c2", "AS OF NOV 8", None),
    (ST[4], ST[5] - 0.1, "c3", "#1 FILM OF 2026 IN JAPAN", None),
    (at(5, 4), ST[6] - 0.1, "c4", "PER TOHO", None),
    (ST[7], ST[8] - 0.1, "c5", "IN HK CINEMAS SINCE AUG 6", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s010_{s}.png")
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
