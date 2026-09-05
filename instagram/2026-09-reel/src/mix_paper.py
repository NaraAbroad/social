"""Place the paper-reel narration on the timeline and duck the bed under it."""
import numpy as np, wave

SR, DUR = 44100, 31.0
N = int(SR * DUR)

# (clip, start second) - two recorded lines are left out; the sheet already
# carries them as text and the reel should not read itself out loud.
VO = [('p1', 1.45), ('p2', 4.50), ('p3', 10.20), ('p4', 13.80),
      ('p5', 16.60), ('p6', 21.50), ('p8', 26.10), ('p9', 29.45)]

w = wave.open('music-paper.wav')
a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
L, R = a[0::2].copy(), a[1::2].copy()
L, R = L[:N], R[:N]
if len(L) < N:
    L = np.pad(L, (0, N - len(L))); R = np.pad(R, (0, N - len(R)))
L *= 0.78; R *= 0.78

voice = np.zeros(N)
for lid, start in VO:
    v = wave.open(f'pvt-{lid}.wav')
    x = np.frombuffer(v.readframes(v.getnframes()), '<i2').astype(np.float32) / 32768
    x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / 24000)), np.arange(len(x)), x)
    # a male voice needs less low end and a touch of presence to sit on the bed
    m = 1 << int(np.ceil(np.log2(len(x))))
    X = np.fft.rfft(x, m); fr = np.fft.rfftfreq(m, 1 / SR)
    g = np.interp(np.log10(np.maximum(fr, 10)),
                  np.log10([10, 80, 150, 400, 1000, 2800, 6000, 11000, SR / 2]),
                  [-30, -16, -6, -1.5, 0, 4.0, 3.0, 0, -6])
    x = np.fft.irfft(X * 10 ** (g / 20), m)[:len(x)]
    x = x / max(1e-9, np.abs(x).max()) * 0.93
    i = int(start * SR); j = min(N, i + len(x))
    voice[i:j] += x[:j - i]
    print(f'  {lid} @{start:5.2f}s  {len(x)/SR:5.2f}s  ends {start + len(x)/SR:5.2f}s')

# duck
h = 256
ne = len(voice) // h
e = np.repeat(np.sqrt((voice[:ne * h].reshape(ne, h) ** 2).mean(axis=1)), h)
e = np.pad(e, (0, N - len(e)))
duck = np.zeros(N); p = 0.0
aa, ar = np.exp(-1 / (0.010 * SR)), np.exp(-1 / (0.330 * SR))
for i in range(0, N, 64):
    c = aa if e[i] > p else ar
    p = (1 - c) * e[i] + c * p
    duck[i:i + 64] = p
gain = 10 ** (-10.0 * np.clip(duck / 0.06, 0, 1) / 20)
L *= gain; R *= gain
L += voice * 0.94; R += voice * 0.94

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
fo = int(0.75 * SR)
for buf in (L, R): buf[-fo:] *= np.linspace(1, 0, fo)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L / mx * 0.90, R / mx * 0.90

inter = np.empty(N * 2); inter[0::2] = L; inter[1::2] = R
with wave.open('paper-audio.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((inter * 32767).astype('<i2').tobytes())
mono = (L + R) / 2
print(f"\npeak {np.abs(inter).max():.3f}  RMS {20*np.log10(np.sqrt((mono**2).mean())):.1f} dBFS  {DUR}s")
