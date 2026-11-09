import json
import os

# the data folder is one level above the app folder
BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")


def load_records():
    # later we will create records.json, until then use the sample file
    path = os.path.join(DATA_FOLDER, "records.json")
    if not os.path.exists(path):
        path = os.path.join(DATA_FOLDER, "sample_records.json")

    with open(path, encoding="utf-8-sig") as f:
        records = json.load(f)

    # give every record an id, starting from 1
    number = 1
    for r in records:
        r["id"] = number
        number = number + 1
    return records


def search(records, keyword):
    keyword = keyword.lower()
    found = []
    for r in records:
        for value in r.values():
            if keyword in str(value).lower():
                found.append(r)
                break
    return found


def count_by(records, field):
    counts = {}
    for r in records:
        key = r.get(field, "unknown")
        if key in counts:
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    return counts


def get_by_id(records, record_id):
    for r in records:
        if r["id"] == record_id:
            return r
    return None
