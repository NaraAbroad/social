import numpy as np, wave, struct

SR, DUR = 44100, 15.0
N = int(SR * DUR)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def put(buf, start, sig, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[:j - i] * gain

def env(n, a, d, s=0.0, r=0.0, sus=0.7):
    """attack/decay/sustain/release envelope, lengths in seconds"""
    e = np.zeros(n); ai, di, ri = int(a*SR), int(d*SR), int(r*SR)
    ai = min(ai, n); e[:ai] = np.linspace(0, 1, ai)
    d2 = min(di, n - ai); e[ai:ai+d2] = np.linspace(1, sus, d2)
    si = n - ai - d2 - ri
    if si > 0: e[ai+d2:ai+d2+si] = sus
    if ri > 0: e[n-ri:] = np.linspace(sus, 0, ri)
    return e

def lp(x, cut):
    """one-pole lowpass"""
    a = np.exp(-2*np.pi*cut/SR); y = np.zeros_like(x); p = 0.0
    for i in range(len(x)):
        p = (1-a)*x[i] + a*p; y[i] = p
    return y

def lp_fast(x, cut):
    from scipy_stub import _  # not available; use vectorised IIR approximation
    return x

def onepole(x, cut):
    a = np.exp(-2*np.pi*cut/SR)
    b = np.empty_like(x)
    acc = 0.0
    # vectorised-ish loop in chunks (numpy lfilter unavailable)
    for i in range(len(x)):
        acc = (1-a)*x[i] + a*acc
        b[i] = acc
    return b

# ---------- musical material : A natural minor, 120 BPM (bar = 2s) ----------
NOTE = lambda s: 440.0 * 2 ** (s / 12)          # semitones from A4
A3, C4, E4, F3, A4c, C5, G3, B3, D4, E3 = (
    NOTE(-12), NOTE(-9), NOTE(-5), NOTE(-16), NOTE(0), NOTE(3), NOTE(-14), NOTE(-10), NOTE(-7), NOTE(-17))

# (start, dur, root, [chord tones])
CHORDS = [
    (0.0, 4.0, A3/2, [A3, C4, E4]),      # Am   - hook
    (4.0, 2.0, F3/2, [F3, NOTE(-9), NOTE(-5)]),   # F
    (6.0, 2.0, NOTE(-21), [NOTE(-9), NOTE(-5), NOTE(-2)]),  # C
    (8.0, 2.0, G3/2, [G3, B3, D4]),      # G
    (10.0, 2.0, A3/2, [A3, C4, E4]),     # Am
    (12.0, 3.0, F3/2, [F3, NOTE(-9), NOTE(-5)]),  # F -> resolve
]

# ---------- pad ----------
for (st, dur, root, tones) in CHORDS:
    n = int((dur + 0.6) * SR); tt = np.arange(n)/SR
    e = env(n, 0.35, 0.25, r=0.55, sus=0.75)
    sig = np.zeros(n)
    for k, f in enumerate(tones):
        for det in (-0.12, 0.12):
            ph = 2*np.pi*(f + det)*tt
            sig += (np.sin(ph) + 0.34*np.sin(2*ph) + 0.20*np.sin(3*ph) + 0.10*np.sin(5*ph)) / (len(tones)*2)
    sig *= e
    pan = 0.5 + 0.12*np.sin(st)
    put(L, st, sig, 0.16*(1-pan+0.5)); put(R, st, sig, 0.16*(pan+0.5-0.5+0.5))

# ---------- sub bass ----------
for (st, dur, root, tones) in CHORDS:
    if st < 3.2: g = 0.0                      # hold back during the hook
    elif st < 6.8: g = 0.5
    elif st < 8.0: g = 0.0                    # drop-out on "في طريقة أسهل"
    else: g = 1.0
    if g == 0: continue
    n = int(dur*SR); tt = np.arange(n)/SR
    e = env(n, 0.02, 0.1, r=0.25, sus=0.85)
    sig = (np.sin(2*np.pi*root*tt) + 0.25*np.sin(4*np.pi*root*tt)) * e
    put(L, st, sig, 0.20*g); put(R, st, sig, 0.20*g)

# ---------- arp pluck (8ths) ----------
for (st, dur, root, tones) in CHORDS:
    if st < 4.0 or st >= 14.0: continue       # carry the groove from the problem beat on
    step = 0.25
    for i in range(int(dur/step)):
        f = tones[i % len(tones)] * (2 if (i % 4) == 3 else 1)
        n = int(0.30*SR); tt = np.arange(n)/SR
        e = np.exp(-tt*11)
        sig = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(4*np.pi*f*tt)) * e
        pan = 0.35 if i % 2 else 0.65
        ag = 0.16 if st < 8.0 else 0.30
        put(L, st + i*step, sig, ag*(1-pan)); put(R, st + i*step, sig, ag*pan)

# ---------- kick ----------
def kick():
    n = int(0.34*SR); tt = np.arange(n)/SR
    f = 118*np.exp(-tt*26) + 44
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*7.5)
for b in np.arange(0, DUR, 0.5):
    if b < 3.5 or (6.9 <= b < 8.0) or b >= 14.2: continue
    beat_in_bar = (b % 2.0)
    if beat_in_bar not in (0.0, 1.0):
        if not (b >= 8.0 and beat_in_bar == 1.5): continue
    g = 0.55 if b < 8.0 else 0.85
    k = kick(); put(L, b, k, g); put(R, b, k, g)

# ---------- hats ----------
rng = np.random.default_rng(7)
for b in np.arange(0, DUR, 0.25):
    if b < 4.0 or (6.9 <= b < 8.0) or b >= 14.3: continue
    n = int(0.06*SR)
    nz = rng.standard_normal(n); nz = np.diff(nz, prepend=0)   # crude highpass
    sig = nz * np.exp(-np.arange(n)/SR*70)
    g = (0.13 if (b*4) % 2 else 0.21) * (0.7 if b < 8 else 1.0)
    put(L, b, sig, g*0.9); put(R, b, sig, g*1.1)

# ---------- risers into the two turns ----------
for turn in (6.85, 12.55):
    n = int(0.85*SR); tt = np.arange(n)/SR; p = tt/tt[-1]
    nz = rng.standard_normal(n)
    sweep = np.sin(2*np.pi*np.cumsum(240 + 1500*p**2)/SR)
    sig = (0.5*nz*p**2 + sweep*p**1.5) * np.hanning(n)**0.5
    put(L, turn-0.85, sig, 0.10); put(R, turn-0.85, sig, 0.10)

# ---------- impacts on scene changes ----------
for hit, g in ((3.30, 0.5), (6.85, 0.9), (8.60, 0.6), (12.55, 1.0)):
    n = int(1.1*SR); tt = np.arange(n)/SR
    boom = np.sin(2*np.pi*(70*np.exp(-tt*9)+38)*tt) * np.exp(-tt*4.2)
    nz = rng.standard_normal(n) * np.exp(-tt*17) * 0.30
    sig = boom + nz
    put(L, hit, sig, 0.30*g); put(R, hit, sig, 0.30*g)

# ---------- reverb (FFT convolution with an exponential noise tail) ----------
ir_n = int(0.75*SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n)/SR*6.5)
ir[:int(0.012*SR)] = 0
ir /= np.abs(ir).sum() / 8
def conv(x):
    m = 1 << int(np.ceil(np.log2(len(x)+ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return y
L = L + 0.22*conv(L); R = R + 0.22*conv(R)

# ---------- master tilt EQ : phone-speaker friendly ----------
def tilt(x):
    m = 1 << int(np.ceil(np.log2(len(x))))
    X = np.fft.rfft(x, m); fr = np.fft.rfftfreq(m, 1/SR)
    pts_f  = [0, 30, 55, 100, 220, 500, 1200, 3000, 7000, 12000, 20000, SR/2]
    pts_db = [-40, -26, -14, -7, -3.5, 0, 7.5, 10.5, 10.0, 6.5, 2, 0]
    g = np.interp(np.log10(np.maximum(fr, 10)), np.log10(np.maximum(pts_f, 10)), pts_db)
    return np.fft.irfft(X * 10**(g/20), m)[:len(x)]
L, R = tilt(L), tilt(R)

# ---------- master: gentle fade, soft limit, normalise ----------
fi, fo = int(0.10*SR), int(0.55*SR)
for buf in (L, R):
    buf[:fi] *= np.linspace(0, 1, fi)
    buf[-fo:] *= np.linspace(1, 0, fo)
mx = max(np.abs(L).max(), np.abs(R).max())
L, R = L/mx, R/mx

# envelope-follower compressor on the stereo bus, then soft clip
def compress(l, r, thr=0.18, ratio=4.0, atk=0.004, rel=0.12):
    det = np.maximum(np.abs(l), np.abs(r))
    aa, ar = np.exp(-1/(atk*SR)), np.exp(-1/(rel*SR))
    e = np.empty_like(det); p = 0.0
    for i in range(len(det)):
        c = aa if det[i] > p else ar
        p = (1-c)*det[i] + c*p
        e[i] = p
    over = np.maximum(e, thr)
    g = (thr * (over/thr) ** (1.0/ratio)) / over
    return l*g, r*g
L, R = compress(L, R)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L/mx*0.99, R/mx*0.99
drive = 2.6
L, R = np.tanh(L*drive)/np.tanh(drive), np.tanh(R*drive)/np.tanh(drive)
mx = max(np.abs(L).max(), np.abs(R).max())
L, R = L/mx*0.89, R/mx*0.89

inter = np.empty(N*2); inter[0::2] = L; inter[1::2] = R
pcm = (inter*32767).astype('<i2')
with wave.open('reel-music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"peak={np.abs(inter).max():.3f}  rms={np.sqrt((inter**2).mean()):.4f}  dur={DUR}s")
