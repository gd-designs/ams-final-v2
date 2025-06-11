import os
import requests

os.environ["DEEPL_API_KEY"] = "9c701752-ed68-4d01-b1cb-8e389d3fcf16"

DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]

def translate_text_list(text_list, source_lang=None, target_lang="EN", glossary_id=None, log=None):
    translated = []
    for text in text_list:
        if len(text.strip()) <= 1 or not any(c.isalpha() for c in text):
            translated.append(text)
            print(f"🔹 Skipped: {text}")
            continue

        data = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": target_lang,
        }

        if source_lang:
            data["source_lang"] = source_lang

        if glossary_id:
            data["glossary_id"] = glossary_id

        response = requests.post("https://api.deepl.com/v2/translate", data=data)

        if response.ok:
            translated_text = response.json()["translations"][0]["text"]
            translated.append(translated_text)
            print(f"✅ {text} ➜ {translated_text}")
        else:
            print(f"❌ Error translating '{text}': {response.text}")
            translated.append(text)

    return translated