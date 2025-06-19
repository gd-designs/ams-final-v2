import os, shutil
import re
from pathlib import Path
from functions.convert_dwg_to_dxf import convert_dwg_to_dxf
from functions.convert_dxf_to_dwg import convert_dxf_to_dwg
from functions.extract_text_from_dxf import extract_text_entities
from functions.replace_text_entities import replace_translated_texts
from functions.translate_text import translate_text_list

SKIP_PHRASES = {
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
}
SKIP_PHRASES = set(' '.join(p.lower().split()) for p in SKIP_PHRASES)


def process_file(
    dwg_path,
    source_lang,
    target_lang,
    glossary_map,
    output_folder,  # ignored
    log=print,
):
    try:
        original_name = Path(dwg_path).stem
        desktop = Path.home() / "Desktop"
        dxf_folder = desktop / "translated_dxfs_delete"
        translated_folder = desktop / "AMS-Applicazione-Tradotto"

        dxf_folder.mkdir(exist_ok=True)
        translated_folder.mkdir(exist_ok=True)

        dxf_path = dxf_folder / f"{original_name}_{target_lang}.dxf"

        log("🔹 Converting DWG to DXF...")
        convert_dwg_to_dxf(dwg_path, str(dxf_folder))

        converted_dxf = dxf_folder / f"{original_name}.dxf"
        if not converted_dxf.exists():
            raise FileNotFoundError("DXF conversion failed.")
        converted_dxf.rename(dxf_path)

        log("🔹 Extracting text...")
        doc, msp, text_entities, original_texts, _ = extract_text_entities(str(dxf_path))

        final_texts = []
        for original in original_texts:
            text = original.strip()
            norm = ' '.join(text.lower().split())

            if norm in SKIP_PHRASES:
                log(f"⏭️ Skipped: '{original}'")
                final_texts.append(original)
                continue

            if norm in glossary_map:
                repl = glossary_map[norm]
                log(f"📕 Glossary: '{original}' → '{repl}'")
                final_texts.append(repl)
                continue

            partial = None
            for phrase in glossary_map:
                if phrase in norm and (not partial or len(phrase) > len(partial)):
                    partial = phrase

            if partial:
                repl = glossary_map[partial]
                log(f"📙 Partial glossary match: '{partial}' for '{original}'")
                translated = translate_text_list([original], source_lang, target_lang, glossary_id=None, log=log, context=partial)
                final_texts.append(translated[0])
            else:
                translated = translate_text_list([original], source_lang, target_lang, log=log)
                final_texts.append(translated[0])

        replace_translated_texts(text_entities, final_texts, log)
        doc.saveas(str(dxf_path))
        log(f"✅ DXF saved: {dxf_path}")

        final_dwg_path = translated_folder / f"{original_name}_{target_lang}.dwg"
        convert_dxf_to_dwg(str(dxf_path), str(translated_folder))  # <- directly into final location

        # Handle cases where it still nests in a subfolder
        inner_folder = translated_folder / Path(dwg_path).stem
        nested_dwg = inner_folder / f"{original_name}_{target_lang}.dwg"
        if nested_dwg.exists():
            nested_dwg.rename(final_dwg_path)
            shutil.rmtree(inner_folder)

        if dxf_folder.exists():
            shutil.rmtree(dxf_folder)

        log(f"✅ Final DWG saved: {final_dwg_path}")
        return str(final_dwg_path)

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        raise
