import os, shutil
import re
from functions.convert_dwg_to_dxf import convert_dwg_to_dxf
from functions.convert_dxf_to_dwg import convert_dxf_to_dwg
from functions.extract_text_from_dxf import extract_text_entities
from functions.replace_text_entities import replace_translated_texts
from functions.translate_text import translate_text_list
from functions.file_utils import ensure_translated_folder


SKIP_PHRASES = [
    "industry automation",
    "manufacturing & service s.r.l.",
    "ams s.r.l.",
    "ams srl",
    "industry automation manufacturing & service s.r.l.",
    "ams srl.",
    "this drawing is the property of industry ams srl.",
    "any reproduction, exploitation or communication to",
    "third parties will result in civil and penal consequences.",
    "do not manually modify the cad drawing.",
    "diese zeichnung ist eigentum von industry ams srl.",
    "jede vervielfältigung, verwertung oder mitteilung an",
    "dritte personen hat zivilund strafrechtliche folgen.",
    "cad-erstellte zeichnung nicht manuell ändern.",
    "author / verfasser",
    "date / datum",
    "approval / genehmigung",
    "description / beschreibung",
    "description / benennung",
    "drawing no. / zeichnungs-nr.",
    "general tolerances",
    "allgemeintoleranzen",
    "size",
    "format",
    "sheet n.",
    "blatt-nr",
    "scale",
    "maßstab",
    "weight (kg)",
    "gewicht (kg)",
]
SKIP_PHRASES = set(' '.join(p.lower().split()) for p in SKIP_PHRASES)


def process_file(
    dwg_path,
    source_lang,
    target_lang,
    glossary_map,
    output_folder,
    log=print,
):
    try:
        original_name = os.path.splitext(os.path.basename(dwg_path))[0]
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        dxf_folder = os.path.join(desktop, "translated_dxfs_delete")
        os.makedirs(dxf_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        dxf_filename = f"{original_name}_{target_lang}.dxf"
        dxf_path = os.path.join(dxf_folder, dxf_filename)

        log(f"🔹 Converting DWG to DXF...")
        convert_dwg_to_dxf(dwg_path, dxf_folder)

        converted_basename = os.path.splitext(os.path.basename(dwg_path))[0] + ".dxf"
        converted_dxf_path = os.path.join(dxf_folder, converted_basename)
        if not os.path.exists(converted_dxf_path):
            raise FileNotFoundError("DXF conversion failed.")

        os.rename(converted_dxf_path, dxf_path)

        log(f"🔹 Extracting text...")
        doc, msp, text_entities, original_texts, text_items = extract_text_entities(dxf_path)

        final_texts = []
        for text in original_texts:
            original = text
            text = text.strip()
            lower_text = text.lower()
            matched = False

            normalized_text = ' '.join(lower_text.split())  # Normalize whitespace
            if normalized_text in SKIP_PHRASES:
                log(f"⏭️ Skipped (excluded phrase): '{original}'")
                final_texts.append(original)
                continue


            if lower_text in glossary_map:
                replacement = glossary_map[lower_text]
                log(f"📕 Trovata nel glossario: '{original}' → '{replacement}'")
                final_texts.append(replacement)
                matched = True

            if not matched:
                best_match = None
                best_replacement = None
                for phrase, replacement in glossary_map.items():
                    if phrase in lower_text:
                        if best_match is None or len(phrase) > len(best_match):
                            best_match = phrase
                            best_replacement = replacement

                if best_match:
                    log(f"📙 Partial glossary context: using '{best_match}' ➜ '{best_replacement}' as context for '{original}'")
                    translated = translate_text_list(
                        [original],
                        source_lang,
                        target_lang,
                        glossary_id=None,
                        log=log,
                        context=best_match  # 🧠 new
                    )
                    final_texts.append(translated[0])
                    matched = True


            if not matched:
                translated = translate_text_list([original], source_lang, target_lang, log=log)
                final_texts.append(translated[0])

        replace_translated_texts(text_entities, final_texts, log)
        translated_dxf_path = os.path.join(dxf_folder, f"{original_name}_{target_lang}.dxf")
        doc.saveas(translated_dxf_path)

        log(f"✅ DXF saved: {translated_dxf_path}")
        final_dwg_path = os.path.join(output_folder, f"{original_name}_{target_lang}.dwg")
        convert_dxf_to_dwg(translated_dxf_path, output_folder)

        inner_dwg = os.path.join(output_folder, os.path.splitext(os.path.basename(dwg_path))[0], f"{original_name}_{target_lang}.dwg")
        if os.path.exists(inner_dwg):
            shutil.move(inner_dwg, final_dwg_path)
            shutil.rmtree(os.path.join(output_folder, os.path.splitext(os.path.basename(dwg_path))[0]))

        if os.path.exists(dxf_folder):
            shutil.rmtree(dxf_folder)

        log(f"✅ Final DWG saved: {final_dwg_path}")

        translated_folder = ensure_translated_folder(target_lang)
        final_copy_path = os.path.join(translated_folder, f"{original_name}_{target_lang}.dwg")

        shutil.copy2(final_dwg_path, final_copy_path)
        log(f"📁 Copied to translated folder: {final_copy_path}")

        return True

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return False