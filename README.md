 Language Translation Tool



[Language Translation Tool](screenshots/banner.png)



A clean and fast web app to translate text between 130+ languages, built with Python and Streamlit.



 Features



 Translate text between 130+ languages

Multi-language mode: translate one text into up to 4 languages at once, one tab per language

 Swap source and target languages in one click

Copy the translation to the clipboard

Text-to-speech with a choice of female or male voice

 Reliable translation: several free translation services are tried in turn until one answers

 Input validation and clear error messages



Screenshot



[App screenshot](screenshots/app.png)



 Tech stack



Purpose  Library 



 User interface  \[Streamlit](https://streamlit.io) 

 Translation Google Translate, MyMemory and Lingva public APIs, called with \[requests](https://requests.readthedocs.io) 

 Language list  [deep-translator](https://github.com/nidhaloff/deep-translator) 

 Text-to-speech  [edge-tts](https://github.com/rany2/edge-tts) (neural voices), \[gTTS](https://github.com/pndurette/gTTS) (fallback) 



Getting started



Prerequisites



Python 3.10 or newer

An internet connection (translation and audio use online services)



 Installation



```bash

git clone https://github.com/AKPINFA/CodeAlpha\_LanguageTranslationTool.git

cd CodeAlpha\_LanguageTranslationTool



python -m venv venv

\# Windows

venv\\Scripts\\activate

\# macOS / Linux

source venv/bin/activate



pip install -r requirements.txt

```



 Run the app



```bash

streamlit run app.py

```



The app opens at http://localhost:8501.



 Project structure



```

.

|-- app.py            # Streamlit user interface

|-- translator.py     # Translation engine with automatic fallback

|-- tts.py            # Text-to-speech (female / male voices)

|-- requirements.txt  # Python dependencies

|-- .streamlit/

|   `-- config.toml   # Theme settings

`-- screenshots/      # README images

```



 How it works



1. The user enters a text and chooses the source and target language(s).

2. `translator.py` sends the text to Google Translate. If that service refuses the request, it automatically tries MyMemory, then Lingva.

3. The result is displayed in a card, with a copy button and a text-to-speech player.

4. In multi-language mode, the same process runs once per selected language and the results appear in tabs.



 Notes and limitations



 Input is limited to 500 characters per translation.

 The translation services are free public services: availability and rate limits are outside the app's control.

 Text-to-speech needs an internet connection. When no male/female voice exists for a language, a default voice is used.







Created by \[AKPINFA](https://github.com/AKPINFA).

