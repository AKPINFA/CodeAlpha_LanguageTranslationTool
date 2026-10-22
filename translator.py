import html
from urllib.parse import quote

import requests
from deep_translator import GoogleTranslator

TIMEOUT = 12
HEADERS = {"User-Agent": "Mozilla/5.0"}
LINGVA_INSTANCES = ["https://lingva.ml", "https://lingva.thedaviddelta.com"]


def get_languages():
    """Return a dictionary of supported languages: {'french': 'fr', ...}."""
    return GoogleTranslator().get_supported_languages(as_dict=True)


# ---------- Translation engines ----------
# Each engine takes (text, source, target) and returns the translated text,
# or raises an exception if it fails.

def _google(text, source, target):
    response = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return "".join(part[0] for part in data[0] if part[0])


def _mymemory(text, source, target):
    if source == "auto":
        raise ValueError("MyMemory needs an explicit source language")
    response = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": f"{source}|{target}"},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    translated = (data.get("responseData") or {}).get("translatedText", "")
    if str(data.get("responseStatus")) != "200" or not translated \
            or "MYMEMORY WARNING" in translated.upper():
        raise RuntimeError(translated or data.get("responseDetails") or "no result")
    return html.unescape(translated)


def _lingva(text, source, target):
    last_error = None
    for base in LINGVA_INSTANCES:
        try:
            url = f"{base}/api/v1/{source}/{target}/{quote(text, safe='')}"
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()["translation"]
        except Exception as error:
            last_error = error
    raise last_error


ENGINES = [("Google", _google), ("MyMemory", _mymemory), ("Lingva", _lingva)]


# ---------- Public function ----------
def translate_text(text, source="auto", target="en"):
    """Translate text, trying each engine in turn until one works."""
    text = text.strip()
    if not text:
        raise ValueError("The text to translate is empty.")
    if source == target:
        return text

    errors = []
    for name, engine in ENGINES:
        try:
            result = engine(text, source, target)
            if result and result.strip():
                return result.strip()
            errors.append(f"{name}: empty result")
        except Exception as error:
            errors.append(f"{name}: {error}")
    raise RuntimeError("All translation services failed. " + " | ".join(errors))


# ---------- Quick test: python translator.py ----------
if __name__ == "__main__":
    sample = "Bonjour, comment allez-vous ?"
    print("Testing each translation service (French -> English):\n")
    for name, engine in ENGINES:
        try:
            print(f"[OK]     {name}: {engine(sample, 'fr', 'en')}")
        except Exception as error:
            print(f"[FAILED] {name}: {error}")
    print()
    try:
        print("Final result:", translate_text(sample, "fr", "en"))
    except Exception as error:
        print("Final result: FAILED ->", error)
    print(len(get_languages()), "languages available")