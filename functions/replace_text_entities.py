def replace_translated_texts(text_entities, translated_texts, log=None):
    """
    Replaces original text content in DXF entities with translated versions,
    preserving entity types (TEXT, MTEXT, ATTRIB, ATTDEF).

    Args:
        text_entities (list): List of DXF text-like entities
        translated_texts (list): List of translated strings
        log (function, optional): Function for logging (e.g., GUI log or print)
    """
    for ent, new_text in zip(text_entities, translated_texts):
        try:
            if ent.dxftype() == "MTEXT":
                # Replace Python line breaks with AutoCAD-compatible paragraph breaks
                safe_text = new_text.replace("\n", "\\P").replace("\\L", "\\P")
                ent.text = safe_text
                if log: log(f"↪️ MTEXT updated: {safe_text}")
            elif ent.dxftype() in {"TEXT", "ATTRIB", "ATTDEF"}:
                ent.dxf.text = new_text
                if log: log(f"↪️ {ent.dxftype()} updated: {new_text}")
            else:
                if log: log(f"⚠️ Skipped unknown entity type: {ent.dxftype()}")
        except Exception as e:
            if log: log(f"❌ Error updating entity: {e}")