"""Score any reel: same instrument set as the first one, but the sections and
hit points are passed in per reel so the music lands on that reel's own cuts."""
import numpy as np, wave, sys

SR = 44100
NOTE = lambda s: 440.0 * 2 ** (s / 12)
Am = [NOTE(-12), NOTE(-9), NOTE(-5)]
F  = [NOTE(-16), NOTE(-9), NOTE(-5)]
C  = [NOTE(-21), NOTE(-9), NOTE(-2)]
G  = [NOTE(-14), NOTE(-10), NOTE(-7)]
PROG = [Am, F, C, G, Am, F, C, G, Am, F, C, G, Am, F]

# id: (duration, [(groove_start, groove_end), ...], [hit times], [riser times])
REELS = {
    'parents':   (24.0, [(4.6, 9.9), (13.9, 23.2)], [4.60, 10.00, 13.90, 21.00], [10.00, 21.00]),
    'rejection': (22.0, [(4.2, 16.1), (19.6, 21.3)], [4.20, 16.30, 19.60], [16.30, 19.60]),
    'compare':   (20.0, [(4.0, 9.4), (13.1, 19.3)], [4.00, 9.10, 13.10, 17.70], [9.10, 17.70]),
    # paper reel: chaos rustles, sweeps away at 12.3, then the ordered sheet
    'dio':       (26.0, [(1.6, 18.6), (19.0, 25.4)],
                  [1.55, 6.90, 12.90, 18.85, 22.95], [6.90, 12.90, 22.95]),
    'poster':    (27.0, [(1.5, 11.9), (12.2, 26.4)],
                  [1.55, 6.85, 12.25, 17.45, 22.60], [6.85, 12.25, 22.60]),
    'paper':     (31.0, [(1.3, 9.9), (13.4, 29.0)],
                  [1.30, 10.10, 12.55, 24.60, 29.05], [10.10, 12.55, 24.60]),
}


def build(rid):
    DUR, GROOVE, HITS, RISERS = REELS[rid]
    N = int(SR * DUR)
    L, R = np.zeros(N), np.zeros(N)
    rng = np.random.default_rng(11)

    def put(buf, st, sig, g=1.0):
        i = int(st * SR); j = min(N, i + len(sig))
        if i < N: buf[i:j] += sig[:j - i] * g

    def env(n, a, d, r, sus=0.75):
        e = np.zeros(n); ai = min(int(a * SR), n); di = int(d * SR); ri = int(r * SR)
        e[:ai] = np.linspace(0, 1, ai)
        d2 = max(0, min(di, n - ai)); e[ai:ai + d2] = np.linspace(1, sus, d2)
        si = n - ai - d2 - ri
        if si > 0: e[ai + d2:ai + d2 + si] = sus
        if ri > 0: e[n - ri:] = np.linspace(sus, 0, ri)
        return e

    playing = lambda t: any(a <= t < b for a, b in GROOVE)

    # chords every two seconds through the whole reel
    chords = [(i * 2.0, 2.0, PROG[i % len(PROG)]) for i in range(int(DUR / 2) + 1)]

    for st, dur, tones in chords:
        n = int((dur + 0.6) * SR); tt = np.arange(n) / SR
        sig = np.zeros(n)
        for f in tones:
            for det in (-0.12, 0.12):
                ph = 2 * np.pi * (f + det) * tt
                sig += (np.sin(ph) + 0.34 * np.sin(2 * ph) + 0.20 * np.sin(3 * ph)
                        + 0.10 * np.sin(5 * ph)) / (len(tones) * 2)
        sig *= env(n, 0.35, 0.25, 0.55)
        put(L, st, sig, 0.16); put(R, st, sig, 0.17)

        if playing(st):
            n2 = int(dur * SR); t2 = np.arange(n2) / SR
            root = tones[0] / 2
            bass = (np.sin(2 * np.pi * root * t2) + 0.25 * np.sin(4 * np.pi * root * t2)) \
                   * env(n2, 0.02, 0.1, 0.25, 0.85)
            put(L, st, bass, 0.20); put(R, st, bass, 0.20)
            for i in range(int(dur / 0.25)):
                f = tones[i % 3] * (2 if i % 4 == 3 else 1)
                n3 = int(0.30 * SR); t3 = np.arange(n3) / SR
                pl = (np.sin(2 * np.pi * f * t3) + 0.3 * np.sin(4 * np.pi * f * t3)) * np.exp(-t3 * 11)
                pan = 0.35 if i % 2 else 0.65
                put(L, st + i * 0.25, pl, 0.26 * (1 - pan)); put(R, st + i * 0.25, pl, 0.26 * pan)

    nk = int(0.34 * SR); tk = np.arange(nk) / SR
    K = np.sin(2 * np.pi * np.cumsum(118 * np.exp(-tk * 26) + 44) / SR) * np.exp(-tk * 7.5)
    for b in np.arange(0, DUR, 0.5):
        if not playing(b): continue
        bib = b % 2.0
        if bib not in (0.0, 1.0) and bib != 1.5: continue
        put(L, b, K, 0.80); put(R, b, K, 0.80)
    for b in np.arange(0, DUR, 0.25):
        if not playing(b): continue
        n4 = int(0.06 * SR)
        h = np.diff(rng.standard_normal(n4), prepend=0) * np.exp(-np.arange(n4) / SR * 70)
        g = 0.13 if (b * 4) % 2 else 0.21
        put(L, b, h, g * 0.9); put(R, b, h, g * 1.1)

    for turn in RISERS:
        n5 = int(0.85 * SR); t5 = np.arange(n5) / SR; p = t5 / t5[-1]
        sig = (0.5 * rng.standard_normal(n5) * p ** 2
               + np.sin(2 * np.pi * np.cumsum(240 + 1500 * p ** 2) / SR) * p ** 1.5) * np.hanning(n5) ** 0.5
        put(L, max(0, turn - 0.85), sig, 0.10); put(R, max(0, turn - 0.85), sig, 0.10)
    for hit in HITS:
        n6 = int(1.1 * SR); t6 = np.arange(n6) / SR
        sig = np.sin(2 * np.pi * (70 * np.exp(-t6 * 9) + 38) * t6) * np.exp(-t6 * 4.2) \
              + rng.standard_normal(n6) * np.exp(-t6 * 17) * 0.30
        put(L, hit, sig, 0.27); put(R, hit, sig, 0.27)

    ir_n = int(0.75 * SR)
    ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 6.5); ir[:int(0.012 * SR)] = 0
    ir /= np.abs(ir).sum() / 8
    def conv(x):
        m = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
        return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    L += 0.22 * conv(L); R += 0.22 * conv(R)

    def tilt(x):
        m = 1 << int(np.ceil(np.log2(len(x))))
        X = np.fft.rfft(x, m); fr = np.fft.rfftfreq(m, 1 / SR)
        pf = [0, 30, 55, 100, 220, 500, 1200, 3000, 7000, 12000, 20000, SR / 2]
        pdb = [-40, -26, -14, -7, -3.5, 0, 7.5, 10.5, 10.0, 6.5, 2, 0]
        g = np.interp(np.log10(np.maximum(fr, 10)), np.log10(np.maximum(pf, 10)), pdb)
        return np.fft.irfft(X * 10 ** (g / 20), m)[:len(x)]
    L, R = tilt(L), tilt(R)

    det = np.maximum(np.abs(L), np.abs(R))
    aa, ar = np.exp(-1 / (0.004 * SR)), np.exp(-1 / (0.12 * SR))
    out = np.empty_like(det); pk = 0.0
    for i in range(len(det)):
        c = aa if det[i] > pk else ar
        pk = (1 - c) * det[i] + c * pk
        out[i] = pk
    thr = 0.18
    over = np.maximum(out, thr)
    gg = (thr * (over / thr) ** 0.25) / over
    L *= gg; R *= gg

    mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L / mx * 0.99, R / mx * 0.99
    d = 2.2
    L, R = np.tanh(L * d) / np.tanh(d), np.tanh(R * d) / np.tanh(d)
    fi, fo = int(0.15 * SR), int(0.8 * SR)
    for buf in (L, R):
        buf[:fi] *= np.linspace(0, 1, fi); buf[-fo:] *= np.linspace(1, 0, fo)
    mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L / mx * 0.89, R / mx * 0.89

    inter = np.empty(N * 2); inter[0::2] = L; inter[1::2] = R
    with wave.open(f'music-{rid}.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((inter * 32767).astype('<i2').tobytes())
    mono = (L + R) / 2
    print(f'  {rid}: {DUR}s  RMS {20*np.log10(np.sqrt((mono**2).mean())):.1f} dBFS')


for rid in (sys.argv[1:] or list(REELS)):
    build(rid)
