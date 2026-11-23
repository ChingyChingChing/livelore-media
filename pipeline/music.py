"""Original background music, synthesized in code (no samples, no copyrighted audio), mixed under the narration.
Usage: python3 music.py STYLE VOICE.wav OUT.wav [SEED]
STYLE: pulse (120 BPM house-ish), lofi (86 BPM chill hip-hop), drive (140 BPM trap-ish), or "list".
OUT has exactly VOICE's length, so segments/caption timings stay valid. OUT may equal VOICE (mixes in place).
The music ducks under the voice (sidechain) and the mix is normalised to -14 LUFS.
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf

SR = 48000
STYLES = {  # bpm, chord roots (semitones from A2) with minor/major flag
    "pulse": (120, [(0, "m"), (8, "M"), (3, "M"), (10, "M")]),     # Am F C G
    "lofi": (86, [(5, "m7"), (10, "7"), (3, "M7"), (0, "m7")]),    # Dm7 G7 Cmaj7 Am7
    "drive": (140, [(0, "m"), (0, "m"), (8, "M"), (7, "M")]),      # Am Am F E
}
SHAPES = {"m": [0, 3, 7], "M": [0, 4, 7], "m7": [0, 3, 7, 10], "7": [0, 4, 7, 10], "M7": [0, 4, 7, 11]}

def hz(semi, base=110.0):
    return base * 2 ** (semi / 12)

def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i: i + len(x)] += x

def kick(sub=False):
    n = int(SR * (0.9 if sub else 0.35))
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.5 if sub else 0.12)

def noise_hit(rng, d, hp=True):
    n = int(SR * d * 4)
    x = rng.standard_normal(n)
    if hp:
        x = np.diff(x, prepend=0)
    return x * env(n, 0.001, d) * 0.5

def pad(semis, dur, bright=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for s in semis:
        f = hz(s + 12)
        for det in (-0.08, 0.08):  # two slightly detuned saws -> width
            ph = (f * (1 + det / 100) * t) % 1
            out += (2 * ph - 1) * 0.5
        out += np.sin(2 * np.pi * f / 2 * t) * 0.6
    k = max(1, int(60 / bright))  # crude low-pass: moving average
    out = np.convolve(out, np.ones(k) / k, "same")
    fade = np.minimum(1, np.minimum(t / 0.05, (dur - t) / 0.08))
    return out * fade / len(semis)

def pluck(f, d=0.25):
    n = int(SR * d)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(n, 0.003, d / 3)

def track(style, dur, seed=0):
    bpm, prog = STYLES[style]
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bar = 4 * beat
    buf = np.zeros(int(SR * dur) + SR)
    nb = int(dur / bar) + 1
    for b in range(nb):
        root, shape = prog[b % len(prog)]
        semis = [root + s for s in SHAPES[shape]]
        t0 = b * bar
        add(buf, pad(semis, bar, 0.6 if style == "lofi" else 1.0) * (0.35 if style == "lofi" else 0.25), t0)
        for q in range(16):  # 16th-note grid
            at = t0 + q * beat / 4
            if style == "pulse":
                if q % 4 == 0: add(buf, kick() * 0.9, at)
                if q % 4 == 2: add(buf, noise_hit(rng, 0.04) * 0.35, at)
                if q % 2 == 1: add(buf, pluck(hz(root - 12), 0.18) * 0.35, at)
                if q in (6, 14) and b % 2: add(buf, pluck(hz(semis[q % 3] + 24), 0.3) * 0.15, at)
            elif style == "lofi":
                swing = beat / 4 * 0.12 if q % 2 else 0
                if q in (0, 7, 10): add(buf, kick() * 0.8, at + swing)
                if q in (4, 12): add(buf, noise_hit(rng, 0.09, hp=False) * 0.45, at + swing)
                if q % 2 == 0: add(buf, noise_hit(rng, 0.02) * 0.18, at + swing)
                if q in (0, 8): add(buf, pluck(hz(root - 12), 0.6) * 0.4, at)
            else:  # drive
                if q in (0, 10) or (q == 7 and b % 2): add(buf, kick(sub=True) * 0.8, at)
                if q in (4, 12): add(buf, noise_hit(rng, 0.12, hp=False) * 0.5, at)
                hats = 3 if (q >= 12 and b % 4 == 3) else 1  # hat roll at the end of every 4th bar
                for r in range(hats):
                    add(buf, noise_hit(rng, 0.015) * 0.22, at + r * beat / 8)
                if q % 8 == 0: add(buf, pluck(hz(semis[0] + 24), 0.15) * 0.18, at)
    buf += rng.standard_normal(len(buf)) * (0.004 if style == "lofi" else 0.0)  # light vinyl hiss
    buf = buf[: int(SR * dur)]
    t = np.arange(len(buf)) / SR
    buf *= np.minimum(1, np.minimum(t / 1.0, (dur - t) / 1.5))  # fade in/out
    return buf / (np.abs(buf).max() + 1e-9) * 0.8

if __name__ == "__main__":
    if sys.argv[1] == "list":
        print(" ".join(STYLES)); sys.exit(0)
    style, voice, out = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    assert style in STYLES, f"unknown style {style}; choose from {list(STYLES)}"
    dur = sf.info(voice).duration
    tmp = tempfile.mkdtemp()
    mus, mix = os.path.join(tmp, "music.wav"), os.path.join(tmp, "mix.wav")
    sf.write(mus, track(style, dur, seed).astype(np.float32), SR)
    # music at -17 dB, ducked a further ~6 dB while the voice speaks, then the whole mix to -14 LUFS
    fc = ("[1:a]aresample=48000,volume=-17dB[m];[0:a]aresample=48000,asplit=2[v][key];"
          "[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1[o]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", voice, "-i", mus, "-filter_complex", fc,
                    "-map", "[o]", "-ar", "48000", mix], check=True)
    assert abs(sf.info(mix).duration - dur) < 0.05, "mix length changed; captions would drift"
    os.replace(mix, out)
    print(f"{out}: {style} music mixed under {dur:.2f}s of voice")
