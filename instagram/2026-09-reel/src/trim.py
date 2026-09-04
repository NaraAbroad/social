"""Trim leading/trailing silence from each VO clip and report real speech length."""
import numpy as np, wave

SR = 24000
def read(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32)/32768
    return a

def write(p, a):
    with wave.open(p, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1)*32767).astype('<i2').tobytes())

total = 0.0
for lid in ('l1','l2','l3','l4','l5'):
    a = read(f'vo-{lid}.wav')
    # 20 ms RMS envelope, keep everything above -46 dBFS
    h = 480
    n = len(a)//h
    e = np.sqrt((a[:n*h].reshape(n, h)**2).mean(axis=1))
    loud = np.where(e > 10**(-46/20))[0]
    if len(loud) == 0:
        print(f'{lid}: silent?'); continue
    s, t = max(0, loud[0]-3)*h, min(len(a), (loud[-1]+4)*h)
    b = a[s:t]
    # gentle 8 ms fades so cuts never click
    f = int(0.008*SR)
    b[:f] *= np.linspace(0, 1, f); b[-f:] *= np.linspace(1, 0, f)
    write(f'vot-{lid}.wav', b)
    d = len(b)/SR; total += d
    print(f'{lid}  raw {len(a)/SR:5.2f}s  ->  speech {d:5.2f}s   (cut {len(a)/SR-d:4.2f}s of silence)')
print(f'\ntotal speech: {total:.2f}s')
