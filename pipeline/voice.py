"""Kokoro (Apache-2.0) narration with exact sentence timings for captions.
Usage: python3 voice.py SCRIPT.json VOICE SPEED OUT.wav SEGMENTS.json [LANG]
LANG is the espeak pronunciation set (default en-us; e.g. en-gb, en-gb-scotland, en-029). See VOICES.md.
The "energetic" FX (pitch +5%, presence EQ, compression, -14 LUFS) is applied to OUT.wav; duration is unchanged.
SCRIPT.json: [{"text": "...", "chunks": [["CAPTION TEXT", weight], ...], "pause": 0.2}, ...]
SEGMENTS.json is timing.SEGMENTS format: [[start, end, chunks], ...] (speech start/end per sentence).
"""
import json, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

def trim(x, thr=0.01, pad=0.03, sr=24000):
    idx = np.nonzero(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x[:0]
    p = int(pad * sr)
    return x[max(0, idx[0] - p): idx[-1] + p]

FX = ("asetrate=24000*1.05,aresample=24000,atempo=0.9524,equalizer=f=3500:t=q:w=1:g=4,"
      "acompressor=threshold=-20dB:ratio=4:attack=5:release=60,loudnorm=I=-14:TP=-1")

script, voice, speed, out_wav, out_seg = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
lang = sys.argv[6] if len(sys.argv) > 6 else "en-us"
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
parts, segs, t, sr = [], [], 0.0, 24000
for i, s in enumerate(json.load(open(script))):
    gap = 0.0 if i == 0 else s.get("pause", 0.12)
    parts.append(np.zeros(int(gap * sr), np.float32)); t += gap
    audio, sr = k.create(s["text"], voice=voice, speed=speed, lang=lang)
    audio = trim(audio, sr=sr)
    segs.append([round(t, 3), round(t + len(audio) / sr, 3), s["chunks"]])
    parts.append(audio.astype(np.float32)); t += len(audio) / sr
parts.append(np.zeros(int(0.5 * sr), np.float32))
sf.write("raw_vo.wav", np.concatenate(parts), sr)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "raw_vo.wav", "-af", FX, "-ar", "48000", out_wav], check=True)
assert abs(sf.info(out_wav).duration - sf.info("raw_vo.wav").duration) < 0.15, "FX changed duration; captions would drift"
json.dump(segs, open(out_seg, "w"), indent=1)
assert all(a[1] <= b[0] for a, b in zip(segs, segs[1:])), "segments overlap"
print(f"{out_wav}: {t + 0.5:.2f}s, {len(segs)} sentences")
