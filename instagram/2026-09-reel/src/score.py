"""Rebuild the 27s music bed against the new scene timings, then mix the
voice-over on top with the music ducked underneath it."""
import numpy as np, wave

SR, DUR = 44100, 27.0
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(7)

NOTE = lambda s: 440.0 * 2 ** (s / 12)
Am = [NOTE(-12), NOTE(-9), NOTE(-5)]
F  = [NOTE(-16), NOTE(-9), NOTE(-5)]
C  = [NOTE(-21), NOTE(-9), NOTE(-2)]
G  = [NOTE(-14), NOTE(-10), NOTE(-7)]

#           start  dur  root          tones
CHORDS = [(0.0, 4.0, Am[0]/2, Am),                       # hook: pad only
          (4.0, 2.0, F[0]/2, F), (6.0, 2.0, C[0]/2, C),  # problem
          (8.0, 2.2, G[0]/2, G),
          (10.2, 2.8, Am[0]/2, Am),                      # the turn: drop out
          (13.0, 2.0, Am[0]/2, Am), (15.0, 2.0, F[0]/2, F),
          (17.0, 2.0, C[0]/2, C), (19.0, 2.0, G[0]/2, G),
          (21.0, 2.0, Am[0]/2, Am),                      # solution groove
          (23.0, 4.0, F[0]/2, F)]                        # CTA + tail

GROOVE = [(4.0, 10.2), (13.0, 26.2)]      # where drums and bass play
TURN   = (10.2, 13.0)                     # breathing space under "في طريقة أسهل"
IMPACTS = [(4.00, 0.55), (10.45, 0.95), (12.95, 0.6), (22.90, 1.0)]
RISERS  = [10.45, 22.90]

def put(buf, start, sig, g=1.0):
    i = int(start*SR); j = min(N, i+len(sig))
    if i < N: buf[i:j] += sig[:j-i]*g

def env(n, a, d, r, sus=0.75):
    e = np.zeros(n); ai, di, ri = min(int(a*SR), n), int(d*SR), int(r*SR)
    e[:ai] = np.linspace(0, 1, ai)
    d2 = max(0, min(di, n-ai)); e[ai:ai+d2] = np.linspace(1, sus, d2)
    si = n-ai-d2-ri
    if si > 0: e[ai+d2:ai+d2+si] = sus
    if ri > 0: e[n-ri:] = np.linspace(sus, 0, ri)
    return e

def playing(t):
    return any(a <= t < b for a, b in GROOVE)

# ---- pad ----
for st, dur, root, tones in CHORDS:
    n = int((dur+0.6)*SR); tt = np.arange(n)/SR
    sig = np.zeros(n)
    for f in tones:
        for det in (-0.12, 0.12):
            ph = 2*np.pi*(f+det)*tt
            sig += (np.sin(ph) + 0.34*np.sin(2*ph) + 0.20*np.sin(3*ph) + 0.10*np.sin(5*ph))/(len(tones)*2)
    sig *= env(n, 0.35, 0.25, int(0.55*SR)/SR)
    put(L, st, sig, 0.16); put(R, st, sig, 0.17)

# ---- sub bass ----
for st, dur, root, tones in CHORDS:
    if not playing(st): continue
    n = int(dur*SR); tt = np.arange(n)/SR
    sig = (np.sin(2*np.pi*root*tt) + 0.25*np.sin(4*np.pi*root*tt)) * env(n, 0.02, 0.1, int(0.25*SR)/SR, 0.85)
    put(L, st, sig, 0.20); put(R, st, sig, 0.20)

# ---- arp ----
for st, dur, root, tones in CHORDS:
    if not playing(st): continue
    for i in range(int(dur/0.25)):
        f = tones[i % 3] * (2 if i % 4 == 3 else 1)
        n = int(0.30*SR); tt = np.arange(n)/SR
        sig = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(4*np.pi*f*tt)) * np.exp(-tt*11)
        pan = 0.35 if i % 2 else 0.65
        g = 0.16 if st < 12 else 0.28
        put(L, st+i*0.25, sig, g*(1-pan)); put(R, st+i*0.25, sig, g*pan)

# ---- kick + hats ----
def kick():
    n = int(0.34*SR); tt = np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(118*np.exp(-tt*26)+44)/SR)*np.exp(-tt*7.5)
K = kick()
for b in np.arange(0, DUR, 0.5):
    if not playing(b) or b > 26.0: continue
    bib = b % 2.0
    if bib not in (0.0, 1.0) and not (b >= 13.0 and bib == 1.5): continue
    g = 0.55 if b < 12 else 0.85
    put(L, b, K, g); put(R, b, K, g)
for b in np.arange(0, DUR, 0.25):
    if not playing(b) or b > 26.2: continue
    n = int(0.06*SR)
    sig = np.diff(rng.standard_normal(n), prepend=0)*np.exp(-np.arange(n)/SR*70)
    g = (0.13 if (b*4) % 2 else 0.21)*(0.7 if b < 12 else 1.0)
    put(L, b, sig, g*0.9); put(R, b, sig, g*1.1)

# ---- risers and impacts on the cuts ----
for turn in RISERS:
    n = int(0.85*SR); tt = np.arange(n)/SR; p = tt/tt[-1]
    sig = (0.5*rng.standard_normal(n)*p**2
           + np.sin(2*np.pi*np.cumsum(240+1500*p**2)/SR)*p**1.5) * np.hanning(n)**0.5
    put(L, turn-0.85, sig, 0.10); put(R, turn-0.85, sig, 0.10)
for hit, g in IMPACTS:
    n = int(1.1*SR); tt = np.arange(n)/SR
    sig = np.sin(2*np.pi*(70*np.exp(-tt*9)+38)*tt)*np.exp(-tt*4.2) + rng.standard_normal(n)*np.exp(-tt*17)*0.30
    put(L, hit, sig, 0.30*g); put(R, hit, sig, 0.30*g)

# ---- reverb ----
ir_n = int(0.75*SR)
ir = rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*6.5); ir[:int(0.012*SR)] = 0
ir /= np.abs(ir).sum()/8
def conv(x):
    m = 1 << int(np.ceil(np.log2(len(x)+ir_n)))
    return np.fft.irfft(np.fft.rfft(x, m)*np.fft.rfft(ir, m), m)[:len(x)]
L += 0.22*conv(L); R += 0.22*conv(R)

# ---- tilt EQ for phone speakers ----
def tilt(x):
    m = 1 << int(np.ceil(np.log2(len(x))))
    X = np.fft.rfft(x, m); fr = np.fft.rfftfreq(m, 1/SR)
    pf  = [0, 30, 55, 100, 220, 500, 1200, 3000, 7000, 12000, 20000, SR/2]
    pdb = [-40, -26, -14, -7, -3.5, 0, 7.5, 10.5, 10.0, 6.5, 2, 0]
    g = np.interp(np.log10(np.maximum(fr, 10)), np.log10(np.maximum(pf, 10)), pdb)
    return np.fft.irfft(X*10**(g/20), m)[:len(x)]
L, R = tilt(L), tilt(R)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L/mx*0.75, R/mx*0.75

# ================= voice-over =================
VO = [('l1', 0.40), ('l2', 3.97), ('l3', 10.55), ('l4', 12.95), ('l5', 22.95)]
voice = np.zeros(N)
for lid, start in VO:
    w = wave.open(f'vot-{lid}.wav')
    a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32)/32768
    # 24 kHz -> 44.1 kHz
    n2 = int(len(a)*SR/24000)
    a = np.interp(np.linspace(0, len(a)-1, n2), np.arange(len(a)), a)
    # presence lift so the voice sits above the bed
    m = 1 << int(np.ceil(np.log2(len(a))))
    X = np.fft.rfft(a, m); fr = np.fft.rfftfreq(m, 1/SR)
    g = np.interp(np.log10(np.maximum(fr, 10)),
                  np.log10([10, 90, 180, 900, 2500, 5500, 11000, SR/2]),
                  [-30, -14, -3, 0, 4.5, 3.5, 0, -6])
    a = np.fft.irfft(X*10**(g/20), m)[:len(a)]
    a = a/max(1e-9, np.abs(a).max())*0.92
    i = int(start*SR); j = min(N, i+len(a))
    voice[i:j] += a[:j-i]
    print(f'  {lid} @{start:5.2f}s  len {len(a)/SR:5.2f}s  ends {start+len(a)/SR:5.2f}s')

# ---- duck the music under the voice ----
h = 256
ne = len(voice)//h
e = np.sqrt((voice[:ne*h].reshape(ne, h)**2).mean(axis=1))
e = np.repeat(e, h); e = np.pad(e, (0, N-len(e)), constant_values=0)
key = np.maximum.accumulate(e[::-1])[::-1]*0          # placeholder, replaced below
# attack/release follower on the voice envelope
duck = np.zeros(N); p = 0.0
aa, ar = np.exp(-1/(0.010*SR)), np.exp(-1/(0.320*SR))
for i in range(0, N, 64):
    x = e[i]
    c = aa if x > p else ar
    p = (1-c)*x + c*p
    duck[i:i+64] = p
amt = np.clip(duck/0.06, 0, 1)                        # full duck once voice is present
gain = 10 ** (-9.5*amt/20)                            # up to -9.5 dB
L *= gain; R *= gain

L += voice*0.92; R += voice*0.92

# ---- master ----
def compress(l, r, thr=0.18, ratio=4.0, atk=0.004, rel=0.12):
    det = np.maximum(np.abs(l), np.abs(r))
    aa, ar = np.exp(-1/(atk*SR)), np.exp(-1/(rel*SR))
    out = np.empty_like(det); p = 0.0
    for i in range(len(det)):
        c = aa if det[i] > p else ar
        p = (1-c)*det[i] + c*p
        out[i] = p
    over = np.maximum(out, thr)
    g = (thr*(over/thr)**(1/ratio))/over
    return l*g, r*g
L, R = compress(L, R)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L/mx*0.99, R/mx*0.99
d = 2.2
L, R = np.tanh(L*d)/np.tanh(d), np.tanh(R*d)/np.tanh(d)
fo = int(0.7*SR)
for buf in (L, R): buf[-fo:] *= np.linspace(1, 0, fo)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L/mx*0.90, R/mx*0.90

inter = np.empty(N*2); inter[0::2] = L; inter[1::2] = R
with wave.open('reel-audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((inter*32767).astype('<i2').tobytes())
mono = (L+R)/2
print(f"\npeak {np.abs(inter).max():.3f}   RMS {20*np.log10(np.sqrt((mono**2).mean())):.1f} dBFS   {DUR}s")
