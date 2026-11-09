import json
import os

import pdfplumber

from app.models import Record

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_FOLDER, "data", "raw", "unit2_schedule.pdf")
SAMPLE_PATH = os.path.join(BASE_FOLDER, "data", "sample_records.json")
OUT_PATH = os.path.join(BASE_FOLDER, "data", "records.json")

# the PDF table has no disease column, so we pick it from the vaccine name
DISEASES = [
    ("pentavalent", "Diphtheria, Pertussis, Tetanus, Hepatitis B, Hib"),
    ("dpt", "Diphtheria, Pertussis, Tetanus"),
    ("hepatitis b", "Hepatitis B"),
    ("bcg", "Tuberculosis"),
    ("opv", "Polio"),
    ("ipv", "Polio"),
    ("rotavirus", "Diarrhoeas due to rotavirus"),
    ("pcv", "Pneumococcal disease"),
    ("pneumococcal", "Pneumococcal disease"),
    ("measles", "Measles, Rubella"),
    ("japanese", "Japanese Encephalitis"),
    ("vitamin", "Not stated in Unit 2 PDF"),
    ("tt", "Tetanus"),
]


def find_disease(name):
    name = name.lower()
    for key, disease in DISEASES:
        if key in name:
            return disease
    return "Not stated in Unit 2 PDF"


def clean(text):
    # remove extra spaces and line breaks, None becomes empty text
    if text is None:
        return ""
    return " ".join(str(text).split())


def read_pdf_rows():
    rows = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    rows.append(row)
    return rows


def row_to_record(cells):
    cells = [clean(c) for c in cells]
    if len(cells) < 7:
        raise ValueError("row is too short")

    vaccine = cells[0]
    due_age = cells[1]
    if vaccine == "" or due_age == "" or vaccine == "Vaccine":
        raise ValueError("header or empty row")

    route_site = cells[5] + ", " + cells[6]
    return Record(vaccine, due_age, cells[2], cells[3], route_site, find_disease(vaccine))


def load_sample():
    records = []
    skipped = 0
    with open(SAMPLE_PATH, encoding="utf-8-sig") as f:
        rows = json.load(f)
    for row in rows:
        try:
            records.append(Record(
                row["vaccine"], row["due_age"], row["latest_age"],
                row["dose"], row["route_site"], row["protects_against"]))
        except KeyError:
            skipped = skipped + 1
    return records, skipped


def main():
    records = []
    skipped = 0
    source = "PDF"

    try:
        rows = read_pdf_rows()
    except Exception as e:
        print("Could not read the PDF:", e)
        rows = []

    for row in rows:
        try:
            records.append(row_to_record(row))
        except (ValueError, IndexError):
            skipped = skipped + 1

    print("PDF gave", len(records), "good rows and", skipped, "bad rows")

    if len(records) < 15:
        print("Too few rows from the PDF, using sample_records.json instead")
        records, skipped = load_sample()
        source = "sample_records.json"

    data = []
    number = 1
    for r in records:
        r.id = number
        data.append(r.to_dict())
        number = number + 1

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Source used:", source)
    print("Saved", len(data), "records to data/records.json, skipped", skipped)


if __name__ == "__main__":
    main()
