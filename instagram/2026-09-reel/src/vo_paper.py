"""Voice-over for the paper reel: a young man, warm and unhurried, Palestinian."""
import base64, wave, sys, time
from gem import call

VOICE = sys.argv[1] if len(sys.argv) > 1 else "Umbriel"
MODELS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]

DIALECT = (
    "أنت شاب فلسطيني بالعشرينات، بتحكي باللهجة الفلسطينية المحكية اليومية — "
    "لهجة رام الله ونابلس، مش لهجة أخبار ولا فصحى أبداً. "
    "نبرتك لطيفة ودافية وهادية، كأنك بتحكي مع صاحبك على القهوة — مش بائع ولا مذيع. "
    "انطق: «شو» مثل shoo، «بس» مثل bass، «هاي» مثل hayy، «بتفوتك» مثل btfootak، "
    "«بيرشّحلك» مثل birash-shahlak، «تنبعت» مثل tinba3at، «تلات» مثل talaat. "
    "خفّف القاف نحو الهمزة، والجيم شامية ناعمة، ولا تنطق الإعراب ولا التنوين. "
    "احكي بإيقاع طبيعي مرتاح، وخلّي فيه دفا وابتسامة بالصوت"
)

LINES = [
    ("p1", "بهدوء وفضول، كأنك بتسأل صاحبك سؤال بسيط",
     "دراستك برّا؟ هاي فوضى ورق."),
    ("p2", "بإيقاع أسرع شوي وفيه تعاطف، كأنك عارف القصة من جوا",
     "كل جامعة بطلب مختلف، ومواعيد بتفوتك، وأوراق بترجع مرفوضة."),
    ("p3", "وقفة صغيرة قبلها، وبعدين بنبرة دافية فيها أمل",
     "بس شو لو كلهم صاروا ورقة وحدة؟"),
    ("p4", "بهدوء وثقة، كأنك بتفتح إشي قدام صاحبك",
     "ملف واحد… وكل شي جواه."),
    ("p5", "بوضوح وبساطة، بدون مبالغة",
     "خمسين ألف برنامج، وستمية جامعة، وخمسة وتلاتين دولة."),
    ("p6", "بنبرة عملية ومريحة",
     "ترشيح حسب علاماتك، وبتقدّم لتلات برامج من نفس الشاشة."),
    ("p7", "بطمأنة، كأنك بتقول لصاحبك لا تقلق",
     "ومختص قبول بيراجع كل ورقة قبل ما تنبعت."),
    ("p8", "بدفا، وكأن الرحلة كملت",
     "وبعد القبول… تأشيرة وسكن وسفر."),
    ("p9", "بهدوء وابتسامة، ببطء شوي",
     "نارا أبرود."),
]


def synth(direction, text, out):
    prompt = f"{DIALECT}، {direction}.\n\nالنص:\n{text}"
    for m in MODELS:
        st, d = call(f"models/{m}:generateContent", {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
            },
        })
        if st != 200:
            print(f"    {m} -> HTTP {st} {str(d)[:90]}", flush=True)
            time.sleep(2); continue
        try:
            pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        except (KeyError, IndexError):
            print(f"    {m} -> no audio", flush=True); continue
        with wave.open(out, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
            w.writeframes(pcm)
        return len(pcm) / 2 / 24000, m
    return None, None


print(f"voice = {VOICE}")
for lid, direction, text in LINES:
    dur, m = synth(direction, text, f"pv-{lid}.wav")
    print(f"  {lid}  {dur:5.2f}s via {m}" if dur else f"  {lid}  FAILED", flush=True)
