"""Live Lore Short 011 (Xbox Series X25: $899.99 translucent green console, Xbox turns 25, Japan sales) — reuses render.py's engine/style.
Usage: python3 render010.py OUT.mp4 [start end]  |  python3 render010.py stills t1 t2 ...
All visuals drawn in code (a generic translucent tower, a generic gamepad, a CRT TV, price tags, bar charts, a generic skyline;
no product photos, logos, game art or footage). No music.
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
SEG = json.load(open("segments011.json"))
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

OG = (120, 220, 60)       # "OG green" accent
LIME = (170, 255, 90)
E_CART, E_CLOCK, E_FIRE, E_GLOBE, E_TROPHY, E_EYES, E_MONEY, E_JP = (emoji(c, 150) for c in "🛒⏰🔥🌍🏆👀💸🗾")

# ---------- art ----------
GREEN_BG = gradient((20, 60, 24), (4, 10, 6))
DEEP = gradient((10, 30, 16), (2, 4, 3))
RETRO = gradient((40, 20, 70), (6, 4, 14))
JP_SKY = gradient((70, 24, 40), (8, 4, 10))
CITY = r.skyline(9, 1330, (6, 6, 12, 255))

def grid_bg(c, t, base=GREEN_BG):
    c.paste(base)
    d = ImageDraw.Draw(c, "RGBA")
    off = (t * 60) % 120
    for x in range(-120, W + 120, 120):
        d.line([(x + off, 0), (x + off, H)], fill=OG + (28,), width=3)
    for y in range(-120, H + 120, 120):
        d.line([(0, y + off), (W, y + off)], fill=OG + (28,), width=3)

def tower(t=0.0, w=420, h=760):
    """Generic translucent green tower console (no logo): see-through shell with visible parts inside."""
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    # inner parts
    d.rounded_rectangle([60, 120, w - 20, h - 140], 16, fill=(30, 70, 40, 230))          # board
    for k in range(6):
        d.rectangle([90 + k * 45, 160, 115 + k * 45, 300], fill=(200, 200, 160, 200))    # chips
    d.rounded_rectangle([110, 360, w - 70, 470], 10, fill=(60, 60, 70, 230))            # heatsink
    for k in range(8):
        d.line([(120 + k * 28, 365), (120 + k * 28, 465)], fill=(150, 150, 160, 230), width=6)
    d.rectangle([90, h - 260, w - 50, h - 190], fill=(40, 40, 50, 230))                 # drive
    # fan on top (spins)
    cx, cy, rad = w // 2 + 20, 70, 150
    d.ellipse([cx - rad, cy - 40, cx + rad, cy + 40], fill=(20, 40, 24, 230))
    for k in range(7):
        a = t * 8 + k * 2 * math.pi / 7
        d.line([(cx, cy), (cx + rad * 0.9 * math.cos(a), cy + 34 * math.sin(a))], fill=(140, 220, 120, 230), width=10)
    # translucent shell
    shell = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shell, "RGBA")
    sd.rounded_rectangle([20, 20, w + 20, h + 20], 40, fill=OG + (110,), outline=LIME + (255,), width=8)
    sd.polygon([(60, 40), (160, 40), (60, h - 40)], fill=(255, 255, 255, 40))          # glare
    im = Image.alpha_composite(im, shell)
    return im

TOWER = tower()

def gamepad(col=OG, s=1.0):
    w, h = 620, 380
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([0, 60, 300, 380], fill=col + (200,))
    d.ellipse([320, 60, 620, 380], fill=col + (200,))
    d.rounded_rectangle([120, 40, 500, 260], 90, fill=col + (220,), outline=LIME + (255,), width=6)
    d.ellipse([150, 110, 230, 190], fill=(30, 30, 36, 255))     # stick
    d.ellipse([360, 200, 440, 280], fill=(30, 30, 36, 255))     # stick
    for dx, dy, cc in ((470, 110, (90, 200, 90)), (510, 150, (215, 45, 45)), (430, 150, (60, 120, 230)), (470, 190, (240, 200, 40))):
        d.ellipse([dx - 18, dy - 18, dx + 18, dy + 18], fill=cc + (255,))
    d.rectangle([215, 205, 245, 285], fill=(30, 30, 36, 255)); d.rectangle([190, 230, 270, 260], fill=(30, 30, 36, 255))
    return im if s == 1.0 else im.resize((int(w * s), int(h * s)))

PAD = gamepad()

def price_tag(text, col=GOLD, rot=-10, size=110):
    tt = T(("pt", text, size), text, size, fill=DARK, weight="Black")
    w, h = tt.width + 170, tt.height + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, h / 2), (70, 0), (w, 0), (w, h), (70, h)], fill=col + (255,))
    d.ellipse([40, h / 2 - 16, 72, h / 2 + 16], fill=(0, 0, 0, 0))
    im.alpha_composite(tt, (110, 35))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

def crt(c, cx, cy, s, glow_t):
    im = Image.new("RGBA", (640, 540), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([0, 0, 640, 480], 50, fill=(70, 60, 55, 255))
    g = int(160 + 60 * math.sin(glow_t * 7))
    d.rounded_rectangle([50, 45, 590, 420], 60, fill=(40, g, 60, 255))
    for y in range(50, 420, 12):
        d.line([(60, y), (580, y)], fill=(0, 0, 0, 50), width=4)
    d.rectangle([250, 480, 390, 540], fill=(50, 45, 40, 255))
    yr = r.text_img("2001", 150, fill=(230, 255, 210), stroke=4, stroke_fill=(20, 60, 20))
    im.alpha_composite(yr, (320 - yr.width // 2, 230 - yr.height // 2))
    paste_center(c, im, cx, cy, s)

def date_card(c, t, big, small, sub, tint, size=300):
    c.paste(gradient(tint, (4, 4, 8)))
    cw, ch = 640, 700
    s = 0.85 + 0.15 * ease(t / 0.3) + 0.02 * t
    cd = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dd = ImageDraw.Draw(cd)
    dd.rounded_rectangle([0, 0, cw, ch], 36, fill=(250, 244, 236, 255))
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=OG + (255,))
    dd.rectangle([0, 120, cw, 170], fill=OG + (255,))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 230 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1290, 56, WHITE, t - 0.25)

def plate(text, sub):
    im = Image.new("RGBA", (760, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 760, 330], 30, fill=(190, 190, 180, 255), outline=(240, 240, 230, 255), width=8)
    for x, y in ((30, 30), (710, 30), (30, 280), (710, 280)):
        d.ellipse([x, y, x + 22, y + 22], fill=(120, 120, 110, 255))
    a = r.text_img(text, 130, fill=(40, 40, 40))
    im.alpha_composite(a, ((760 - a.width) // 2, 50))
    b = r.text_img(sub, 50, fill=(80, 80, 80), weight="Bold", spacing=6)
    im.alpha_composite(b, ((760 - b.width) // 2, 230))
    return im

def hbar(c, x0, y, w, h, frac, col, name, val, t):
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([x0, y, x0 + max(h, w * frac), y + h], 20, fill=col + (255,))
    nm = T(("bn", name), name, 52, fill=WHITE, weight="Black")
    c.alpha_composite(nm, (x0, y - nm.height - 14))
    v = T(("bv", val), val, 56, fill=WHITE if frac < 0.25 else DARK, weight="Black")
    vx = x0 + w * frac - v.width - 24 if frac >= 0.25 else x0 + max(h, w * frac) + 20
    c.alpha_composite(v, (int(vx), int(y + (h - v.height) / 2)))

# ---------- scenes ----------
def s_hook(c, t, g):
    grid_bg(c, g)
    paste_center(c, TOWER, W / 2, 1000, 0.8 * pop(t, 0.3)[0], pop(t, 0.3)[1])
    punch(c, "h900", "$900?", 500, 210, t, color=GOLD, stroke=10)

def s_seethru(c, t, g):
    grid_bg(c, g, DEEP)
    paste_center(c, TOWER, W / 2 - 40, 860, 1.12 + 0.05 * t)
    if t > 0.2:
        d = ImageDraw.Draw(c, "RGBA")
        k = ease((t - 0.2) / 0.3)
        d.ellipse([W / 2 + 60, 560, W / 2 + 60 + 300 * k, 560 + 300 * k], outline=WHITE + (255,), width=12)
        d.line([(W / 2 + 290, 830), (W / 2 + 290 + 120 * k, 830 + 160 * k)], fill=WHITE + (255,), width=18)
    paste_center(c, pill("SEE-THROUGH", 80, LIME), W / 2, 1250, *pop(t - 0.3))

def s_lowkey(c, t, g):
    grid_bg(c, g)
    for k in range(5):
        if t > k * 0.18:
            paste_center(c, E_CART.resize((150, 150)), 170 + k * 185, 980 + 30 * math.sin(g * 6 + k), *pop(t - k * 0.18))
    paste_center(c, stamp("PEOPLE DID", 130, GOLD, -7), W / 2, 680, *pop(t - 0.4))

def s_name(c, t, g):
    c.paste(DEEP)
    paste_center(c, TOWER, W / 2, 900, 0.9 + 0.04 * t)
    punch(c, "nm", "SERIES X25", 500, 150, t, color=LIME, stroke=8)
    label(c, "25TH ANNIVERSARY · LIMITED EDITION", 1290, 46, WHITE, t - 0.3)

def s_nov13(c, t, g):
    date_card(c, t, "13", "NOV", "LAUNCH DAY · 2026", (30, 90, 40))

def s_price(c, t, g):
    grid_bg(c, g)
    paste_center(c, price_tag("$899.99", GOLD, -8, 140), W / 2, 760, *pop(t))
    label(c, "US PRICE", 1010, 64, WHITE, t - 0.3)
    paste_center(c, E_MONEY.resize((160, 160)), 860, 1150, *pop(t - 0.5))

def s_translucent(c, t, g):
    grid_bg(c, g, DEEP)
    rot = 6 * math.sin(g * 2)
    paste_center(c, TOWER.rotate(rot, expand=True, resample=Image.BICUBIC), W / 2, 880, 1.0 + 0.04 * t)
    punch(c, "tl", "TRANSLUCENT", 480, 130, t, color=LIME, stroke=8)

def s_2001(c, t, g):
    c.paste(RETRO)
    crt(c, W / 2, 820, 0.85 + 0.15 * ease(t / 0.3), g)
    paste_center(c, pill("THE OG LOOK", 80, LIME), W / 2, 1220, *pop(t - 0.4))

def s_numbered(c, t, g):
    c.paste(DEEP)
    num = random.Random(int(t * 15)).randint(1, 25000) if t < 1.0 else 25
    paste_center(c, plate(f"#{num:05d}", "OF 25,000"), W / 2, 800, *pop(t))
    label(c, "INDIVIDUALLY NUMBERED", 1100, 58, WHITE, t - 0.3)

def s_25k(c, t, g):
    grid_bg(c, g)
    d = ImageDraw.Draw(c, "RGBA")
    cols, rows = 10, 8
    shown = int(cols * rows * ease(t / 1.2))
    for k in range(shown):
        x = 130 + (k % cols) * 92
        y = 560 + (k // cols) * 80
        d.rounded_rectangle([x, y, x + 50, y + 66], 8, fill=OG + (200,), outline=LIME + (255,), width=3)
    paste_center(c, pill("ONLY 25,000?", 96, GOLD), W / 2, 1250, *pop(t - 0.3))
    label(c, "PER RETAILER LISTINGS", 470, 44, WHITE, t - 0.5)

def s_bundle(c, t, g):
    grid_bg(c, g, DEEP)
    paste_center(c, PAD, W / 2, 700 + 10 * math.sin(g * 4), *pop(t))
    if t > 0.9:
        paste_center(c, pill("+ HALO: CAMPAIGN EVOLVED", 64, WHITE), W / 2, 1060, *pop(t - 0.9))
    label(c, "MATCHING CONTROLLER", 470, 52, LIME, t - 0.2)

def s_soldout(c, t, g):
    grid_bg(c, g)
    paste_center(c, E_CLOCK.resize((240, 240)), W / 2, 700, 1.0 + 0.06 * math.sin(g * 20), ease(t / 0.15))
    paste_center(c, stamp("SOLD OUT", 160, RED, -9), W / 2, 1040, *pop(t - 0.4))

def s_scalp(c, t, g):
    c.paste(r.NIGHT)
    d = ImageDraw.Draw(c, "RGBA")
    k = ease(t / 1.4)
    pts = [(120 + i * 105, 1300 - (40 + i * i * 4.5) * k) for i in range(9)]
    d.line(pts, fill=RED + (255,), width=16, joint="curve")
    paste_center(c, price_tag("$2,500", RED, 8, 130), W / 2 + 60, 640, *pop(t - 0.5))
    paste_center(c, E_FIRE.resize((140, 140)), 180, 600, *pop(t - 0.8))
    label(c, "REPORTED RESALE ASKS", 860, 50, WHITE, t - 0.7)

def s_whynow(c, t, g):
    c.paste(RETRO)
    punch(c, "wn", "WHY NOW?", 560, 170, t, color=WHITE, stroke=8)
    paste_center(c, E_EYES.resize((200, 200)), W / 2, 900, *pop(t - 0.3))

def s_nov15(c, t, g):
    date_card(c, t, "15", "NOV 2001", "THE ORIGINAL XBOX LAUNCHES", (70, 30, 110), size=300)

def s_299(c, t, g):
    c.paste(RETRO)
    crt(c, W / 2, 1020, 0.7, g)
    paste_center(c, price_tag("$299", GOLD, -6, 150), W / 2, 600, *pop(t))

def s_24m(c, t, g):
    c.paste(r.NIGHT)
    paste_center(c, E_GLOBE.resize((260, 260)), W / 2, 680, 1.0 + 0.03 * math.sin(g * 3), ease(t / 0.2))
    v = 24 * ease(t / 0.9)
    punch(c, ("m24", int(v)), f"~{int(v)}M", 980, 190, min(t, 0.3) if t < 0.9 else t, color=GOLD, stroke=8)
    label(c, "SOLD WORLDWIDE (MICROSOFT)", 1170, 48, WHITE, t - 0.4)

def s_japan(c, t, g):
    c.paste(JP_SKY)
    paste_center(c, E_JP.resize((170, 170)), W / 2, 520, *pop(t))
    k = ease(t / 0.9)
    hbar(c, 110, 760, 860, 130, 1.0 * k, OG, "WORLDWIDE", "~24M", t)
    hbar(c, 110, 1040, 860, 130, max(0.02, 0.0197 * k), (255, 120, 170), "JAPAN", "~473K", t)
    label(c, "FAMITSU DATA", 1260, 46, ICE, t - 0.6)

def s_tough(c, t, g):
    c.paste(JP_SKY)
    c.alpha_composite(CITY, (-100, 0))
    paste_center(c, stamp("TOUGHEST MARKET", 100, GOLD, -6), W / 2, 700, *pop(t))
    label(c, "ASIA · SINCE DAY ONE", 940, 56, WHITE, t - 0.4)

def s_take(c, t, g):
    grid_bg(c, g, DEEP)
    punch(c, "mt11", "MY TAKE", 560, 160, t, color=WHITE, stroke=6)
    paste_center(c, TOWER, W / 2, 1000, 0.55 + 0.02 * t)

def s_trophy(c, t, g):
    grid_bg(c, g)
    paste_center(c, E_TROPHY.resize((320, 320)), W / 2, 760, *pop(t))
    paste_center(c, pill("NOSTALGIA TROPHY", 84, GOLD), W / 2, 1100, *pop(t - 0.4))

def s_vibes(c, t, g):
    c.paste(RETRO)
    crt(c, W / 2, 760, 0.8, g)
    paste_center(c, stamp("NO CAP", 120, LIME, 6), W / 2, 1170, *pop(t - 0.6))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq11", "$900 FOR ONE?", 540, 120, t, color=WHITE, stroke=6)
    paste_center(c, pill("BET", 100, GOLD), W / 2, 820, *pop(t - 0.15))
    paste_center(c, pill("HARD PASS", 90, CYAN), W / 2, 1060, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun11", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.7:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.7) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

B = [0.0, at(0, 2), ST[1], ST[2], at(2, 2), at(2, 4), ST[3], at(3, 4), ST[4], at(4, 3), ST[5], ST[6], at(6, 3),
     ST[7], at(7, 2), at(7, 4), at(7, 6), ST[8], at(8, 4), ST[9], at(9, 3), at(9, 5), ST[10], ST[11], DUR + 0.1]
FNS = [s_hook, s_seethru, s_lowkey, s_name, s_nov13, s_price, s_translucent, s_2001, s_numbered, s_25k, s_bundle,
       s_soldout, s_scalp, s_whynow, s_nov15, s_299, s_24m, s_japan, s_tough, s_take, s_trophy, s_vibes, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "OUT NOW · NOV 13", None),
    (ST[4], ST[5] - 0.1, "c2", "UNIT COUNT: REPORTEDLY", None),
    (ST[5], ST[6] - 0.1, "c3", "INCLUDED IN THE BOX", None),
    (ST[6], ST[7] - 0.1, "c4", "PRE-ORDERS OPENED IN AUGUST", None),
    (ST[7], ST[8] - 0.1, "c5", "XBOX TURNS 25", None),
    (ST[8], ST[9] - 0.1, "c6", "JAPAN LAUNCH: FEB 2002", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s011_{s}.png")
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
