import asyncio
from io import BytesIO

from gtts import gTTS

try:
    import edge_tts
except ImportError:  # edge-tts is optional: without it, the default voice is used
    edge_tts = None

# (female voice, male voice) for each language code
VOICES = {
    "en": ("en-US-JennyNeural", "en-US-GuyNeural"),
    "fr": ("fr-FR-DeniseNeural", "fr-FR-HenriNeural"),
    "es": ("es-ES-ElviraNeural", "es-ES-AlvaroNeural"),
    "de": ("de-DE-KatjaNeural", "de-DE-ConradNeural"),
    "it": ("it-IT-ElsaNeural", "it-IT-DiegoNeural"),
    "pt": ("pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"),
    "ar": ("ar-SA-ZariyahNeural", "ar-SA-HamedNeural"),
    "zh-CN": ("zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"),
    "zh-TW": ("zh-TW-HsiaoChenNeural", "zh-TW-YunJheNeural"),
    "ja": ("ja-JP-NanamiNeural", "ja-JP-KeitaNeural"),
    "ko": ("ko-KR-SunHiNeural", "ko-KR-InJoonNeural"),
    "ru": ("ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"),
    "hi": ("hi-IN-SwaraNeural", "hi-IN-MadhurNeural"),
    "tr": ("tr-TR-EmelNeural", "tr-TR-AhmetNeural"),
    "nl": ("nl-NL-ColetteNeural", "nl-NL-MaartenNeural"),
    "pl": ("pl-PL-ZofiaNeural", "pl-PL-MarekNeural"),
    "sw": ("sw-KE-ZuriNeural", "sw-KE-RafikiNeural"),
}


def get_voice(lang_code, gender):
    """Return the voice name for a language and gender, or None if unavailable."""
    entry = VOICES.get(lang_code) or VOICES.get(lang_code.split("-")[0])
    if entry is None:
        return None
    return entry[0] if gender == "Female" else entry[1]


async def _edge_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def text_to_speech(text, lang_code, gender="Female"):
    """Return (mp3 bytes, description of the voice used)."""
    voice = get_voice(lang_code, gender)
    if voice and edge_tts is not None:
        try:
            audio = asyncio.run(asyncio.wait_for(_edge_audio(text, voice), timeout=25))
            if audio:
                name = voice.split("-")[2].replace("Neural", "")
                return audio, f"Voice: {name} ({gender.lower()})"
        except Exception:
            pass  # fall back to the default voice below

    buffer = BytesIO()
    gTTS(text=text, lang=lang_code).write_to_fp(buffer)
    return buffer.getvalue(), "Default voice (male/female choice not available here)"