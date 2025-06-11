import ezdxf
import re

def clean_autocad_formatting(text):
    # Remove inline underline codes like \L, \l
    text = text.replace("\\L", "").replace("\\l", "")
    # Remove group underline formatting like {\L...\l}
    text = re.sub(r"\{\\L(.*?)\\l\}", r"\1", text)
    return text

def extract_text_entities(dxf_file_path):
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()

    text_items = []

    # ────────────────────────────────────────────────────────────
    # Modelspace text entities
    for e in msp.query("TEXT MTEXT ATTRIB DIMENSION"):
        text = getattr(e.dxf, "text", None)
        if text:
            text_items.append({
                "text": clean_autocad_formatting(text),
                "entity": e,
                "source": "modelspace",
                "position": getattr(e.dxf, "insert", None)
            })

    # ────────────────────────────────────────────────────────────
    # Tables (cells)
    for table in msp.query("TABLE"):
        try:
            for row in range(table.dxf.n_rows):
                for col in range(table.dxf.n_cols):
                    cell = table.get_cell(row, col)
                    txt = cell.text
                    if txt:
                        text_items.append({
                            "text": clean_autocad_formatting(txt),
                            "entity": cell,
                            "source": f"table:{table.dxf.name}",
                            "position": None
                        })
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # Multileaders
    for e in msp.query("MULTILEADER"):
        try:
            mtext = e.get_mtext()
            if mtext:
                text_items.append({
                    "text": clean_autocad_formatting(mtext.plain_text()),
                    "entity": e,
                    "source": "multileader",
                    "position": getattr(e.dxf, "insert", None)
                })
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # Scan block definitions (inside INSERTs)
    for block_name in doc.blocks.block_names():
        block = doc.blocks[block_name]
        for e in block:
            if e.dxftype() in {"TEXT", "MTEXT", "ATTRIB"}:
                try:
                    txt = e.dxf.text
                    if txt:
                        text_items.append({
                            "text": clean_autocad_formatting(txt),
                            "entity": e,
                            "source": f"block:{block_name}",
                            "position": getattr(e.dxf, "insert", None)
                        })
                except AttributeError:
                    pass

    # ────────────────────────────────────────────────────────────
    # Nested ATTDEF inside block definitions (for Trattamento-style blocks)
    for block_name in doc.blocks.block_names():
        block = doc.blocks[block_name]
        for e in block:
            if e.dxftype() == "ATTDEF":
                try:
                    txt = e.dxf.text
                    if txt:
                        text_items.append({
                            "text": clean_autocad_formatting(txt),
                            "entity": e,
                            "source": f"attdef:{block_name}",
                            "position": getattr(e.dxf, "insert", None)
                        })
                except AttributeError:
                    pass

    # ────────────────────────────────────────────────────────────
    # Final data split (for legacy logic)
    text_entities = [item["entity"] for item in text_items]
    original_texts = [item["text"] for item in text_items]

    return doc, msp, text_entities, original_texts, text_items