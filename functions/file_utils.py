import os

def ensure_translated_folder(target_lang=None):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translated_base = os.path.join(project_root, "translated")

    if not os.path.exists(translated_base):
        os.makedirs(translated_base)

    if target_lang:
        lang_folder = os.path.join(translated_base, target_lang.upper())
        if not os.path.exists(lang_folder):
            os.makedirs(lang_folder)
        return lang_folder

    return translated_base

