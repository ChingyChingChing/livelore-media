# Caption timing: speech segments come from ffmpeg silencedetect (-32 dB, 0.09 s) on vo.m4a;
# words inside a segment are spread by syllable weight.
# shortcut: pause-based alignment, not ASR — upgrade to Picsart transcribe word timings if sync drifts.

SEGMENTS = [
    (0.00, 0.95, [("GODZILLA IS", 4), ("BACK…", 2)]),
    (1.13, 1.73, [("AND THIS TIME,", 3)]),
    (2.02, 2.80, [("HE DIDN'T", 3), ("COME ALONE.", 3)]),
    (3.48, 5.56, [("GODZILLA", 3), ("MINUS ZERO", 4), ("IS IN", 2), ("THEATERS NOW.", 4)]),
    (5.91, 7.76, [("IT OPENED", 3), ("IN JAPAN", 3), ("ON NOVEMBER 3RD,", 5)]),
    (8.01, 11.24, [("THE EXACT DATE", 4), ("THE ORIGINAL", 5), ("GODZILLA", 3), ("CAME OUT", 2), ("IN 1954,", 5)]),
    (11.67, 13.18, [("AND IT HIT", 3), ("THE US", 3), ("THIS WEEK.", 2)]),
    (13.94, 17.67, [("IT'S THE SEQUEL", 4), ("TO GODZILLA", 4), ("MINUS ONE,", 3), ("THE 2023", 6), ("MOVIE", 2)]),
    (18.08, 20.23, [("MADE FOR AROUND", 4), ("$15 MILLION,", 6)]),
    (20.54, 25.28, [("THAT WON", 2), ("THE OSCAR", 3), ("FOR VISUAL EFFECTS", 6), ("AND MADE", 2), ("$116 MILLION", 10), ("WORLDWIDE.", 2)]),
    (25.93, 28.79, [("MINUS ZERO", 4), ("PICKS UP", 2), ("IN 1949,", 5), ("TWO YEARS LATER.", 4)]),
    (29.27, 32.92, [("SAME DIRECTOR,", 4), ("TAKASHI YAMAZAKI,", 7), ("WHO DOES", 2), ("THE EFFECTS HIMSELF.", 5), ("SAME LEADS.", 2)]),
    (33.38, 36.07, [("AND IT'S", 2), ("THE FIRST", 2), ("JAPANESE MOVIE", 5), ("EVER FILMED", 3), ("FOR IMAX.", 3)]),
    (36.87, 38.88, [("THE TRAILERS", 3), ("ALSO TEASED", 3), ("A SECOND MONSTER…", 5)]),
    (39.32, 41.40, [("AND FANS", 2), ("ARE CONVINCED", 3), ("IT'S KING GHIDORAH.", 5)]),
    (42.07, 43.18, [("THE TAGLINE", 3), ("SAYS IT ALL:", 3)]),
    (43.42, 44.56, [("“THERE IS", 3), ("NO THIRD TIME.", 3)]),
    (44.79, 45.85, [("EVERYTHING", 3), ("ENDS HERE.”", 2)]),
    (46.58, 48.98, [("IF A", 2), ("$15-MILLION-DOLLAR", 6), ("MOVIE CAN", 3), ("WIN AN OSCAR,", 4)]),
    (49.34, 50.54, [("IMAGINE WHAT", 4), ("THIS ONE CAN DO.", 4)]),
    (51.15, 52.21, [("ARE YOU", 2), ("SEEING IT", 3), ("IN IMAX?", 3)]),
    (52.68, 53.98, [("FULL BREAKDOWN", 3), ("IN SUNDAY'S", 3), ("RECAP.", 2)]),
]


def captions():
    """Return [(start, end, text)]; a chunk holds until the next one, or 0.2 s past its segment."""
    out = []
    for s, e, chunks in SEGMENTS:
        total = sum(w for _, w in chunks)
        t = s
        for text, w in chunks:
            d = (e - s) * w / total
            out.append([t, t + d, text])
            t += d
    for i, c in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else c[1] + 0.4
        c[1] = min(nxt, c[1] + 0.2) if nxt - c[1] > 0.35 else nxt
    return out


if __name__ == "__main__":
    caps = captions()
    assert all(a[1] <= b[0] + 1e-6 for a, b in zip(caps, caps[1:])), "overlap"
    assert caps[-1][1] < 55.0
    for c in caps:
        print(f"{c[0]:6.2f}-{c[1]:6.2f}  {c[2]}")
