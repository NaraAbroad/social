"""Generate the reel voice-over, one clip per scene, with a female voice."""
import base64, wave, sys
from gem import call

MODEL = sys.argv[2] if len(sys.argv) > 2 else "gemini-2.5-flash-preview-tts"
VOICE = sys.argv[1] if len(sys.argv) > 1 else "Kore"

# (id, scene start in the video, performance direction, line)
LINES = [
    ("l1", 0.30, "بنبرة ودّية وهادئة، كأنك بتسألي صاحبتك سؤال",
     "بدك تدرس برّا… وما بتعرف من وين تبلّش؟"),
    ("l2", 3.40, "بإيقاع أسرع وفيه شوية ضيق وإحباط",
     "التقديم لحاله متاهة. كل جامعة نظام مختلف، مواعيد بتفوتك، وأوراق بترجع مرفوضة."),
    ("l3", 6.95, "وقفة قصيرة قبل الجملة، وبعدين بنبرة هادية وواثقة فيها ارتياح",
     "بس في طريقة أسهل."),
    ("l4", 8.70, "بوضوح وثقة، وكل جملة منفصلة عن اللي بعدها",
     "ملف طالب واحد بتبنيه مرة وحدة. ترشيح حسب درجاتك وأهدافك. وبتقدّم لتلات برامج من نفس الشاشة."),
    ("l5", 12.60, "بنبرة دافية ومشجّعة، وشدّي على كلمة اليوم",
     "ابدأ اليوم. نارا أبرود."),
]


def synth(direction, text, out):
    prompt = f"اقرئي النص التالي باللهجة العربية {direction}:\n\n{text}"
    st, d = call(f"models/{MODEL}:generateContent", {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    })
    if st != 200:
        print(f"  !! HTTP {st}: {str(d)[:300]}")
        return None
    try:
        part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
    except (KeyError, IndexError):
        print(f"  !! unexpected response: {str(d)[:300]}")
        return None
    pcm = base64.b64decode(part["data"])
    with wave.open(out, "wb") as w:            # Gemini returns 24 kHz mono s16le
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(pcm)
    return len(pcm) / 2 / 24000


print(f"voice={VOICE}  model={MODEL}")
for lid, start, direction, text in LINES:
    dur = synth(direction, text, f"vo-{lid}.wav")
    if dur:
        print(f"  {lid}  @{start:5.2f}s  spoken {dur:5.2f}s   {text[:42]}…")
