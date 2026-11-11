"""Live Lore Short 009 (GTA 6 launch week: 212 GB preload, code-in-a-box, 30 fps) — reuses render.py's engine/style.
Usage: python3 render009.py OUT.mp4 [start end]  |  python3 render009.py stills t1 t2 ...
All visuals drawn in code (generic storage bars, plain boxes, generic controllers, sunset/palms; no game logos, art,
footage, screenshots or console likenesses). No music.
"""
import json, math, random, subprocess, sys
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
import render as r
import timing as tm
from render import W, H, FPS, GOLD, ICE, WHITE, ease, label, punch, paste_center, T, gradient
RED, GREEN, DARK = (215, 45, 45), (70, 190, 90), (15, 15, 18)
PINK, CYAN, PURPLE = (255, 80, 170), (60, 220, 255), (90, 40, 150)
AUDIO = "in/vo.wav"
DUR = round(sf.info(AUDIO).duration, 2)
SEG = json.load(open("segments009.json"))
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

E_DISK, E_BOX, E_CD, E_PAD, E_UP, E_EYES, E_QUEST, E_HOURG, E_FIRE = (emoji(c, 150) for c in "💾📦💿🎮📈👀❓⏳🔥")

# ---------- art ----------
SUNSET = gradient((255, 120, 90), (60, 20, 90))
NEON_BG = gradient((40, 14, 70), (6, 4, 16))

def palm(c, x, base, h, col=(10, 6, 22, 255), sway=0.0):
    d = ImageDraw.Draw(c, "RGBA")
    pts = [(x + math.sin(i / 10 * 1.2) * 40 + sway * i * 3, base - h * i / 10) for i in range(11)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([(x0, y0), (x1, y1)], fill=col, width=26)
    tx, ty = pts[-1]
    for k in range(7):
        ang = -math.pi + k * math.pi / 6 + sway * 0.1
        ex, ey = tx + math.cos(ang) * 210, ty + math.sin(ang) * 110 + 60
        d.line([(tx, ty), ((tx + ex) / 2, ty - 40), (ex, ey)], fill=col, width=20, joint="curve")

def sunset(c, t):
    c.paste(SUNSET)
    d = ImageDraw.Draw(c, "RGBA")
    sy = 1050 + 10 * math.sin(t)
    d.ellipse([W / 2 - 260, sy - 260, W / 2 + 260, sy + 260], fill=(255, 215, 120, 255))
    for k in range(7):  # retro sun stripes
        y = sy + 40 + k * 34
        d.rectangle([W / 2 - 270, y, W / 2 + 270, y + 8 + k * 2], fill=(255, 120, 90, 255))
    d.rectangle([0, 1250, W, H], fill=(30, 14, 60, 255))
    for k in range(12):  # grid floor
        y = 1250 + (k ** 1.7) * 9 + (t * 40) % 30
        d.line([(0, y), (W, y)], fill=PINK + (120,), width=3)
    for k in range(-8, 9):
        d.line([(W / 2 + k * 30, 1250), (W / 2 + k * 260, H)], fill=PINK + (90,), width=3)
    palm(c, 110, 1300, 620, sway=math.sin(t * 1.5) * 0.4)
    palm(c, 960, 1320, 540, sway=math.sin(t * 1.3 + 1) * 0.4)

def neon(c, t):
    c.paste(NEON_BG)
    d = ImageDraw.Draw(c, "RGBA")
    for y in range(0, H, 60):
        off = int(t * 25) % 60
        d.line([(0, y + off), (W, y + off)], fill=(255, 255, 255, 10), width=2)

def bar(c, cx, cy, w, h, frac, col, back=(40, 30, 60)):
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h // 2, fill=back + (255,), outline=WHITE + (255,), width=6)
    if frac > 0.01:
        d.rounded_rectangle([cx - w / 2 + 12, cy - h / 2 + 12, cx - w / 2 + 12 + (w - 24) * min(1, frac), cy + h / 2 - 12],
                            (h - 24) // 2, fill=col + (255,))

def box(c, cx, cy, s, lid=0.0, col=(30, 30, 40)):
    """Plain game-case box (no branding). lid 0..1 opens it."""
    d = ImageDraw.Draw(c, "RGBA")
    w, h = 420 * s, 560 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 24, fill=col + (255,), outline=WHITE + (255,), width=6)
    d.rectangle([cx - w / 2 + 30, cy - h / 2 + 30, cx + w / 2 - 30, cy - h / 2 + 90], fill=PINK + (255,))
    if lid > 0:
        o = lid * w * 0.8
        d.rounded_rectangle([cx - w / 2 - o, cy - h / 2, cx + w / 2 - o, cy + h / 2], 24, fill=(60, 60, 80, 235), outline=WHITE + (255,), width=6)

def controller(c, cx, cy, col):
    d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle([cx - 200, cy - 90, cx + 200, cy + 90], 80, fill=col + (255,))
    d.ellipse([cx - 230, cy - 40, cx - 90, cy + 160], fill=col + (255,))
    d.ellipse([cx + 90, cy - 40, cx + 230, cy + 160], fill=col + (255,))
    d.rectangle([cx - 140, cy - 12, cx - 80, cy + 12], fill=DARK + (255,))
    d.rectangle([cx - 122, cy - 30, cx - 98, cy + 30], fill=DARK + (255,))
    for dx, dy in ((110, -25), (140, 5), (80, 5), (110, 35)):
        d.ellipse([cx + dx - 14, cy + dy - 14, cx + dx + 14, cy + dy + 14], fill=DARK + (255,))

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
    dd.rounded_rectangle([0, 0, cw, 170], 36, fill=PINK + (255,))
    dd.rectangle([0, 120, cw, 170], fill=PINK + (255,))
    sm = r.text_img(small, 70, fill=WHITE, weight="ExtraBold", spacing=8)
    cd.alpha_composite(sm, ((cw - sm.width) // 2, 40))
    bg_ = r.text_img(big, size, fill=(20, 20, 24))
    cd.alpha_composite(bg_, ((cw - bg_.width) // 2, 230 + (300 - size) // 2))
    paste_center(c, cd, W / 2, 820, scale=s)
    label(c, sub, 1290, 56, WHITE, t - 0.25)

# ---------- scenes (local t = seconds since scene start) ----------
def s_212(c, t, g):
    neon(c, g)
    n = int(212 * ease(t / 1.2))
    punch(c, ("gb", n), f"{n} GB", 700, 230, min(t, 0.3) if t < 1.2 else t, color=GOLD, stroke=8)
    bar(c, W / 2, 980, 860, 120, ease(t / 1.2), PINK)
    label(c, "UP TO", 520, 70, WHITE, t)

def s_space(c, t, g):
    neon(c, g)
    paste_center(c, E_DISK.resize((220, 220)), W / 2, 620, *pop(t))
    bar(c, W / 2, 900, 860, 110, 0.35 + 0.6 * ease(t / 1.4), RED if t > 0.9 else GOLD)
    paste_center(c, pill("STORAGE FULL?", 80, WHITE), W / 2, 1110, *pop(t - 0.8))

def s_notout(c, t, g):
    sunset(c, g)
    punch(c, "noy", "NOT EVEN OUT", 520, 120, t, color=WHITE, stroke=8)
    paste_center(c, E_HOURG.resize((190, 190)), W / 2, 760, *pop(t - 0.4))

def s_twist(c, t, g):
    neon(c, g)
    punch(c, "twist", "THE TWIST", 500, 130, t, color=GOLD, stroke=6)
    box(c, W / 2 + 60, 920, 1.0, lid=ease((t - 0.6) / 0.6) if t > 0.6 else 0)
    if t > 1.3:
        paste_center(c, stamp("NO DISC", 130, RED, -10), W / 2, 920, *pop(t - 1.3))

def s_preload(c, t, g):
    neon(c, g)
    punch(c, "pl", "PRELOADS OPEN", 520, 110, t, color=WHITE, stroke=6)
    bar(c, W / 2, 800, 860, 110, 0.05 + 0.5 * ease(t / 1.6), CYAN)
    label(c, "DOWNLOADING…", 940, 56, CYAN, t - 0.3)

def s_nov10(c, t, g):
    date_card(c, t, "10", "NOV", "PRELOAD DAY", (60, 20, 70))

def s_pads(c, t, g):
    neon(c, g)
    controller(c, 330, 720, (235, 235, 245)) if t > 0 else None
    if t > 0.5:
        controller(c, 750, 980, (40, 200, 120))
    paste_center(c, pill("DIGITAL PRE-ORDERS", 66, GOLD), W / 2, 520, *pop(t))
    paste_center(c, pill("PS5 + XBOX SERIES", 60, WHITE), W / 2, 1220, *pop(t - 0.8))

def s_nov19(c, t, g):
    date_card(c, t, "19", "NOV", "THURSDAY · LAUNCH DAY", (24, 30, 80))

def s_delays(c, t, g):
    neon(c, g)
    punch(c, "dl", "2 DELAYS", 480, 130, t, color=WHITE, stroke=6)
    rows = (("2025", 0.3, True), ("MAY 2026", 1.0, True), ("NOV 19, 2026", 1.9, False))
    for k, (txt, d0, cross) in enumerate(rows):
        y = 680 + k * 190
        if t > d0:
            paste_center(c, pill(txt, 80, WHITE if cross else GOLD), W / 2, y, *pop(t - d0))
            if cross and t > d0 + 0.35:
                dr = ImageDraw.Draw(c, "RGBA")
                dr.line([(W / 2 - 260, y + 40), (W / 2 + 260, y - 40)], fill=RED + (255,), width=16)

def s_codebox(c, t, g):
    neon(c, g)
    box(c, 360, 860, 0.85, lid=0.0)
    d = ImageDraw.Draw(c, "RGBA")
    cx, cy = 720 + 30 * (1 - ease(t / 0.5)), 860
    d.rounded_rectangle([cx - 190, cy - 120, cx + 190, cy + 120], 20, fill=(245, 240, 228, 255))
    code = T("code", "XXXX-XXXX", 52, fill=DARK, weight="Black")
    paste_center(c, code, cx, cy + 20)
    paste_center(c, T("codelbl", "DOWNLOAD CODE", 30, fill=PINK, weight="Black"), cx, cy - 70)
    punch(c, "cib", "CODE IN A BOX", 520, 110, t, color=WHITE, stroke=6)

def s_massive(c, t, g):
    neon(c, g)
    paste_center(c, pill("STILL A", 70, WHITE), W / 2, 560, *pop(t))
    punch(c, "md", "212 GB", 760, 200, t, color=GOLD, stroke=8)
    bar(c, W / 2, 1010, 860, 100, 0.1 + 0.4 * ease(t / 1.5), PINK)

def s_30(c, t, g):
    neon(c, g)
    punch(c, "fps", "30 FPS", 720, 240, t, color=CYAN, stroke=8)
    label(c, "CONSOLE TARGET", 920, 60, WHITE, t - 0.3)
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(30):  # frame ticks
        on = (int(g * 30) % 30) >= k
        x = 120 + k * 28
        d.rectangle([x, 1060, x + 18, 1110], fill=(CYAN if on else (60, 50, 90)) + (255,))

def s_pro(c, t, g):
    neon(c, g)
    controller(c, W / 2, 780, (235, 235, 245))
    paste_center(c, pill("EVEN ON PS5 PRO", 80, GOLD), W / 2, 1080, *pop(t))
    paste_center(c, pill("30 FPS", 70, CYAN), W / 2, 520, *pop(t - 0.3))

def tag(c, cx, cy, txt, col, s, a):
    im = Image.new("RGBA", (560, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 150), (90, 0), (560, 0), (560, 300), (90, 300)], fill=col + (255,))
    d.ellipse([60, 130, 100, 170], fill=(0, 0, 0, 0))
    tt = r.text_img(txt, 130 if len(txt) <= 4 else 96, fill=DARK)
    im.alpha_composite(tt, (120 + (430 - tt.width) // 2, (300 - tt.height) // 2))
    paste_center(c, im, cx, cy, s, a)

def s_us(c, t, g):
    neon(c, g)
    punch(c, "pc", "PRICE CHECK", 480, 110, t, color=WHITE, stroke=6)
    tag(c, W / 2, 800, "$80", GOLD, *pop(t - 0.4))
    label(c, "US · STANDARD", 1030, 56, WHITE, t - 0.6)

def s_jp(c, t, g):
    neon(c, g)
    tag(c, W / 2, 640, "$80", (150, 150, 160), 0.7, 0.8)
    tag(c, W / 2, 960, "¥9,800", CYAN, *pop(t))
    label(c, "JAPAN · STANDARD", 1190, 56, WHITE, t - 0.3)

def s_preorders(c, t, g):
    neon(c, g)
    d = ImageDraw.Draw(c, "RGBA")
    pts = [(140 + k * 95, 1200 - (k ** 1.6) * 12 * ease(t / 1.4)) for k in range(9)]
    d.line(pts, fill=GREEN + (255,), width=18, joint="curve")
    paste_center(c, E_UP.resize((170, 170)), pts[-1][0] + 20, pts[-1][1] - 60, *pop(t - 0.8))
    punch(c, "po", "PRE-ORDERS", 460, 120, t, color=WHITE, stroke=6)
    paste_center(c, pill("REPORTEDLY", 60, GOLD), W / 2, 610, *pop(t - 0.4))

def s_take(c, t, g):
    sunset(c, g)
    punch(c, "mt9", "MY TAKE", 560, 150, t, color=WHITE, stroke=8)
    if t > 0.6:
        paste_center(c, E_CD.resize((210, 210)), W / 2, 820, *pop(t - 0.6))
        d = ImageDraw.Draw(c, "RGBA")
        k = ease((t - 0.9) / 0.3) if t > 0.9 else 0
        d.line([(W / 2 - 130, 820 + 130), (W / 2 - 130 + 260 * k, 820 + 130 - 260 * k)], fill=RED + (255,), width=20)

def s_era(c, t, g):
    neon(c, g)
    paste_center(c, pill("DIGITAL-ONLY ERA?", 80, WHITE), W / 2, 620, *pop(t))
    paste_center(c, stamp("NO CAP", 150, GOLD, -8), W / 2, 920, *pop(t - 1.0))
    if t > 1.5:
        paste_center(c, E_FIRE.resize((150, 150)), 860, 1130, *pop(t - 1.5))

def s_q(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sq9", "DISC OR DIGITAL?", 540, 90, t, color=WHITE, stroke=6)
    paste_center(c, pill("DISC", 90, GOLD), 300, 860, *pop(t - 0.15))
    paste_center(c, pill("DIGITAL", 90, CYAN), 760, 860, *pop(t - 0.3))

def s_outro(c, t, g):
    c.paste(r.NIGHT)
    punch(c, "sun9", "SUNDAY RECAP", 760, 100, t, color=GOLD)
    if t > 0.9:
        paste_center(c, T("brand", "LIVE LORE", 96, fill=WHITE, spacing=14), W / 2, 1640, alpha=ease((t - 0.9) / 0.3))

def at(i, j):
    s, e, ch = SEG[i]
    tot = sum(w for _, w in ch)
    return s + (e - s) * sum(w for _, w in ch[:j]) / tot

# scene boundaries (global seconds): each starts at a spoken chunk so visuals match the words
B = [0.0, at(0, 2), at(0, 5), ST[1], ST[2], at(2, 2), at(2, 3), ST[3], at(3, 3), ST[4], at(4, 4),
     ST[5], at(5, 5), ST[6], at(6, 3), ST[7], ST[8], at(8, 3), ST[9], ST[10], DUR + 0.1]
FNS = [s_212, s_space, s_notout, s_twist, s_preload, s_nov10, s_pads, s_nov19, s_delays, s_codebox, s_massive,
       s_30, s_pro, s_us, s_jp, s_preorders, s_take, s_era, s_q, s_outro]
assert len(B) == len(FNS) + 1
r.SCENES = [(B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
r.CALLOUTS = [
    (ST[2], ST[3] - 0.1, "c1", "PRELOAD LIVE SINCE NOV 10", None),
    (ST[3], ST[4] - 0.1, "c2", "LAUNCH: NOV 19", None),
    (ST[4], ST[5] - 0.1, "c3", "BOXED COPY = CODE ONLY", None),
    (ST[5], ST[6] - 0.1, "c4", "30 FPS TARGET", None),
    (ST[6], ST[7] - 0.1, "c5", "STANDARD EDITION", None),
]
tm.SEGMENTS = SEG
r.CAPS = tm.captions()
assert all(a[1] <= b[0] + 1e-6 for a, b in zip(r.CAPS, r.CAPS[1:])), "caption overlap"
assert all(a[1] <= b[0] for a, b in zip(r.SCENES, r.SCENES[1:])) and DUR < 58

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            r.frame(float(s)).save(f"stills/s009_{s}.png")
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
