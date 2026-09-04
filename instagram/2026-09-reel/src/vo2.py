"""Regenerate the voice-over pushing hard for a Jordanian/Palestinian Levantine
delivery rather than the Modern Standard Arabic reading the model defaults to."""
import base64, wave, sys, time
from gem import call

MODEL = sys.argv[2] if len(sys.argv) > 2 else "gemini-3.1-flash-tts-preview"
VOICE = sys.argv[1] if len(sys.argv) > 1 else "Leda"

DIALECT = (
    "تكلّمي باللهجة الشامية المحكية (أردنية فلسطينية) — لهجة عمّان ورام الله اليومية، "
    "مثل بنت شابة بتحكي مع صاحبتها، مش قراءة أخبار ولا لغة فصحى أبداً. "
    "لازم تنطقي: «بدك» مثل bid-dak، «بتعرف» مثل bti3raf، «بتبلّش» مثل btballesh، "
    "«بس» مثل bass، «في» بمعنى يوجد مثل fee، «هاي» مثل hayy، «تلات» مثل talaat. "
    "لا تنطقي الإعراب ولا التنوين، ولا تشدّدي على أواخر الكلمات. "
    "خفّفي القاف نحو الهمزة والجيم شامية ناعمة. "
    "خلّي الإيقاع سريع وطبيعي وعفوي مثل الحكي اليومي"
)

LINES = [
    ("l1", "بنبرة ودّية وفضولية، كأنك بتسألي صاحبتك",
     "بدك تدرسي برّا… وما بتعرفي من وين تبلّشي؟"),
    ("l2", "أسرع شوي، وفيها ضيق وتذمّر خفيف",
     "التقديم لحاله متاهة. كل جامعة إلها نظام مختلف، مواعيد بتفوتك، وأوراق بترجع مرفوضة."),
    ("l3", "وقفة قصيرة، وبعدين بهدوء وثقة وارتياح",
     "بس في طريقة أسهل."),
    ("l4", "بوضوح وحماس هادي، كل جملة لحالها",
     "ملف طالب واحد بتعمليه مرة وحدة. وترشيح حسب علاماتك وأهدافك. وبتقدّمي لتلات برامج من نفس الشاشة."),
    ("l5", "بنبرة دافية ومشجّعة، وشدّي على كلمة اليوم",
     "ابدأي اليوم. نارا أبرود."),
]


def synth(direction, text, out, model):
    prompt = f"{DIALECT}، {direction}.\n\nالنص:\n{text}"
    st, d = call(f"models/{model}:generateContent", {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    })
    if st != 200:
        return None, f"HTTP {st}: {str(d)[:150]}"
    try:
        pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    except (KeyError, IndexError):
        return None, f"bad response: {str(d)[:150]}"
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(pcm)
    return len(pcm) / 2 / 24000, None


if __name__ == "__main__":
    print(f"voice={VOICE}")
    FALLBACKS = [MODEL, "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]
    for lid, direction, text in LINES:
        for m in FALLBACKS:
            dur, err = synth(direction, text, f"vo-{lid}.wav", m)
            if dur:
                print(f"  {lid}  {dur:5.2f}s  via {m}")
                break
            print(f"  {lid}  .. {m} -> {err}")
            time.sleep(2)
        else:
            print(f"  {lid}  ALL MODELS FAILED")
