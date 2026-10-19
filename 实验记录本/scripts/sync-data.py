"""Sync data.js from all .md files in the project."""
import json
import os
import shutil
from datetime import datetime, timezone

PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
WORKBENCH_DIR = r"D:\Users\ao\Documents\电脑操作\个人工作台"
FOLDERS = ["experiments", "plans", "methods", "notes", "data", "reminders"]

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

sync_meta = {
    "syncedAt": datetime.now(timezone.utc).isoformat(),
    "count": len(records),
    "folders": {folder: sum(1 for record in records if record["folder"] == folder) for folder in FOLDERS},
}
with open(os.path.join(PROJECT_DIR, "sync-meta.json"), "w", encoding="utf-8") as f:
    json.dump(sync_meta, f, ensure_ascii=False, indent=2)

# Refresh Pulsework's local fallback from the same authoritative Markdown source.
workbench_data = os.path.join(WORKBENCH_DIR, "data")
if os.path.isdir(WORKBENCH_DIR):
    os.makedirs(workbench_data, exist_ok=True)
    shutil.copy2(db_json, os.path.join(workbench_data, "research-records.json"))
    with open(os.path.join(workbench_data, "research-sync-meta.json"), "w", encoding="utf-8") as f:
        json.dump(sync_meta, f, ensure_ascii=False, indent=2)

# Keep the embedded fallback in index.html fresh for offline/cache-failure use.
index_html = os.path.join(PROJECT_DIR, "index.html")
with open(index_html, "r", encoding="utf-8") as f:
    html = f.read()
start_marker = '<script type="application/json" id="db-data">'
start = html.find(start_marker)
if start >= 0:
    data_start = start + len(start_marker)
    end = html.find("</script>", data_start)
    if end >= 0:
        embedded = "\n" + json.dumps(records, ensure_ascii=False, separators=(",", ":")) + "\n"
        html = html[:data_start] + embedded + html[end:]
        with open(index_html, "w", encoding="utf-8") as f:
            f.write(html)

mirror_html = os.path.join(PROJECT_DIR, "实验记录本.html")
with open(mirror_html, "w", encoding="utf-8") as f:
    f.write(html)

# Embed a read-only copy of the original notebook viewer inside Pulsework.
if os.path.isdir(WORKBENCH_DIR):
    workbench_notebook = os.path.join(WORKBENCH_DIR, "notebook")
    os.makedirs(workbench_notebook, exist_ok=True)
    readonly_style = """<style id="pulsework-readonly">
#pwGate,button[onclick*="doImport"],button[onclick*="showNewMenu"],button[onclick*="openEditor"],button[onclick*="doDelete"],button[onclick*="doSave"],#dirtyTag,#saveStatus{display:none!important}
.pulsework-readonly-note{padding:8px 16px;border-bottom:1px solid #d8e0e8;background:#eff6ff;color:#334155;font:700 12px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
</style>"""
    readonly_note = '<div class="pulsework-readonly-note">工作台内置只读视图 · 编辑和保存请使用工作台顶部“Windows 编辑”</div>'
    readonly_html = html.replace("</head>", readonly_style + "\n</head>", 1)
    readonly_html = readonly_html.replace('<div id="listView">', '<div id="listView">\n' + readonly_note, 1)
    readonly_html = readonly_html.replace("  checkPassword();", '  document.getElementById("pwGate").style.display = "none";\n  document.getElementById("listView").classList.remove("pw-locked");', 1)
    with open(os.path.join(workbench_notebook, "index.html"), "w", encoding="utf-8") as f:
        f.write(readonly_html)
    shutil.copy2(data_js, os.path.join(workbench_notebook, "data.js"))

print(f"Synced {len(records)} records to data.js and db-data.json")
if os.path.isdir(WORKBENCH_DIR):
    print(f"Refreshed Pulsework snapshot in {workbench_data}")
for r in records:
    print(f"  {r['folder']}/{r['name']}")
