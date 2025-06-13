import csv
import os

def parse_glossary_to_map(path, source_lang, target_lang):
    glossary = {}

    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';', quotechar='"')

        # Normalize headers
        if reader.fieldnames:
            headers = [h.strip().lstrip('\ufeff') for h in reader.fieldnames]
            reader.fieldnames = headers
        else:
            raise ValueError("No headers found in glossary.")

        if source_lang not in headers or target_lang not in headers:
            raise ValueError(f"Glossary does not contain '{source_lang}' and '{target_lang}' columns.")

        for row in reader:
            source = row.get(source_lang, "").strip().lower()
            target = row.get(target_lang, "").strip()
            if source and target:
                glossary[source] = target

    return glossary