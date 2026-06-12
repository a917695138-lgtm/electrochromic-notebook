"""Sync data.js from all .md files in the project."""
import json
import os

PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
FOLDERS = ["experiments", "methods", "notes", "data", "reminders"]

records = []
for folder in FOLDERS:
    folder_path = os.path.join(PROJECT_DIR, folder)
    if not os.path.isdir(folder_path):
        continue
    for fname in os.listdir(folder_path):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(folder_path, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        records.append({"folder": folder, "name": fname, "content": content})

data_js = os.path.join(PROJECT_DIR, "data.js")
with open(data_js, "w", encoding="utf-8") as f:
    f.write("var DB = ")
    f.write(json.dumps(records, ensure_ascii=False, indent=2))
    f.write(";\n")

# Also update db-data.json
db_json = os.path.join(PROJECT_DIR, "db-data.json")
with open(db_json, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False)

print(f"Synced {len(records)} records to data.js and db-data.json")
for r in records:
    print(f"  {r['folder']}/{r['name']}")
