"""Voice-over for the parents' paper reel: a warm Palestinian woman, calm and
unhurried - talking to a worried father, not selling to a student."""
import base64, wave, sys, time
from gem import call

VOICE = sys.argv[1] if len(sys.argv) > 1 else "Sulafat"
MODELS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]

DIALECT = (
    "أنتِ سيدة فلسطينية ناضجة، بتحكي باللهجة الفلسطينية المحكية اليومية — "
    "لهجة رام الله ونابلس، مش فصحى ولا لهجة أخبار أبداً. "
    "بتحكي مع أب أو أم قلقانين على ابنهم — فنبرتك هادية ودافية ومطمئنة، "
    "بإيقاع بطيء شوي وواثق، بدون أي حماس إعلاني ولا نبرة بيع. "
    "انطقي: «بدّه» مثل biddo، «بتقلق» مثل btiʼlaʼ، «بس» مثل bass، «شو» مثل shoo، "
    "«قدامك» مثل ʼuddaamak، «تنبعت» مثل tinbaʼat، «بيتابعه» مثل bitaabʼo. "
    "خفّفي القاف نحو الهمزة، والجيم شامية ناعمة، ولا تنطقي الإعراب ولا التنوين. "
    "خلّي بصوتك حنية، كأنك بتحكي مع حدا بتحبيه"
)

LINES = [
    ("q1", "بهدوء وتفهّم، كأنك بتلمسي وجع بتعرفيه",
     "ابنك بدّه يسافر يدرس… وإنت اللي بتقلق."),
    ("q2", "بإيقاع هادي بس فيه ثقل، تعدّدي الهموم وحدة وحدة",
     "جامعة ما بتعرف عنها إشي، وأرقام بتتغيّر كل ما تسأل، ووسيط بيستعجلك توقّع."),
    ("q3", "وقفة قبلها، وبعدين بنبرة فيها ارتياح وأمل",
     "بس شو لو كل إشي كان قدامك؟"),
    ("q4", "بهدوء وثقة، ببطء",
     "قرار واضح… من غير قلق."),
    ("q5", "بوضوح وطمأنينة",
     "كل الأرقام قدامك — رسوم ومعيشة وتأشيرة."),
    ("q6", "بطمأنة، كأنك بتقولي لا تخاف",
     "ومختص قبول بيراجع كل ورقة قبل ما تنبعت للجامعة."),
    ("q7", "بدفا، وكأن الحمل انزاح",
     "وبعد القبول… تأشيرة وسكن وسفر."),
    ("q8", "بهدوء وابتسامة، ببطء",
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
            print(f"    {m} -> HTTP {st}", flush=True); time.sleep(2); continue
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
    dur, m = synth(direction, text, f"qv-{lid}.wav")
    print(f"  {lid}  {dur:5.2f}s via {m}" if dur else f"  {lid}  FAILED", flush=True)
