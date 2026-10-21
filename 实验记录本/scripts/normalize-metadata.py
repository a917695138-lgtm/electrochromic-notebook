#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
按受控词表改造实验记录本既有记录的 frontmatter。

用法:
    python normalize-metadata.py          预演，只打印改动清单，不写盘
    python normalize-metadata.py --apply  写盘

词表定义见:
    C:\\Users\\ao\\.workbuddy\\skills\\nature-experiment-log\\references\\notebook-metadata-schema.md
"""
import os
import re
import sys
import io

PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
FOLDERS = ["experiments", "notes", "plans", "methods"]

# ---- 受控词表 ----
CATEGORY = ["薄膜制备", "染料配制与染浴", "器件组装与封装", "响应时间测试",
            "循环稳定性测试", "透过率与光谱表征", "膜厚与形貌表征",
            "规范与汇总", "组会与讨论"]
ELECTROLYTE = ["LiClO4-ACN", "LiTFSI-ACN", "DALE", "PMMA凝胶", "多体系对比", "不涉及", "未标注"]
ADDITIVE = ["EMIMTFSI", "无", "不涉及"]
COUNTER = ["1层ATO", "2层ATO", "单层+双层对比", "未标注", "不涉及"]
ENCAP = ["沙林膜60μm", "沙林膜120μm", "双面胶100μm", "打孔注液", "多方式对比", "未标注", "不涉及"]
STATUS = ["completed", "needs_review", "in-progress", "planned"]
DATA_TYPES = ["response_time", "cycling", "uvvis", "thickness"]

# ---- 每条记录的映射（依据正文明写内容；无法判断的一律"未标注"，不猜测）----
MAP = {
    "experiments/2026-06-01-tio2-prep.md":
        ("薄膜制备", "不涉及", "不涉及", "2层ATO", "不涉及", [], "completed"),
    "experiments/2026-06-02-post-dye.md":
        ("染料配制与染浴", "不涉及", "不涉及", "不涉及", "不涉及", [], "completed"),
    "experiments/2026-06-03-pmma-gel.md":
        ("器件组装与封装", "PMMA凝胶", "无", "未标注", "沙林膜60μm", [], "completed"),
    "experiments/2026-06-04-liquid-electrolyte.md":
        ("循环稳定性测试", "LiClO4-ACN", "无", "未标注", "打孔注液", ["cycling", "response_time"], "completed"),
    "experiments/2026-06-06-re-test.md":
        ("循环稳定性测试", "未标注", "无", "未标注", "打孔注液", ["cycling", "response_time"], "completed"),
    "experiments/2026-06-07-da50e-gel-device.md":
        ("循环稳定性测试", "DALE", "无", "未标注", "未标注", ["cycling", "response_time"], "completed"),
    "experiments/2026-06-09-tio2-film-prep.md":
        ("薄膜制备", "不涉及", "不涉及", "不涉及", "不涉及", [], "completed"),
    "experiments/2026-06-10-da50e-pbi-cl-supplement.md":
        ("循环稳定性测试", "DALE", "无", "2层ATO", "未标注", ["cycling", "response_time"], "completed"),
    "experiments/2026-06-15-ato-layer-prep.md":
        ("薄膜制备", "不涉及", "不涉及", "不涉及", "不涉及", [], "completed"),
    "experiments/2026-06-16-dye-bath-uptake.md":
        ("响应时间测试", "LiClO4-ACN", "无", "未标注", "未标注", ["response_time"], "completed"),
    "experiments/2026-06-17-da-emimtfsi-gel-response-time.md":
        ("响应时间测试", "DALE", "EMIMTFSI", "未标注", "未标注", ["response_time"], "completed"),
    "experiments/2026-06-30-tio2-film-device-test.md":
        ("响应时间测试", "LiClO4-ACN", "无", "未标注", "未标注", ["response_time", "cycling"], "completed"),
    "experiments/2026-07-01-pbi-cl-thickness-meeting.md":
        ("膜厚与形貌表征", "不涉及", "不涉及", "不涉及", "不涉及", ["thickness"], "completed"),
    "experiments/2026-07-02-pure-pbi-ato-fto-transmittance.md":
        ("透过率与光谱表征", "不涉及", "不涉及", "未标注", "不涉及", ["uvvis"], "completed"),
    "experiments/2026-07-04-ato-liquid-device-spincoat.md":
        ("响应时间测试", "LiClO4-ACN", "无", "单层+双层对比", "未标注", ["response_time"], "completed"),
    "experiments/2026-07-06-spincoat-thickness-pbi-cl.md":
        ("膜厚与形貌表征", "不涉及", "不涉及", "不涉及", "不涉及", ["thickness"], "completed"),
    "experiments/2026-07-09-dale50-il50-solid-cycling-stability.md":
        ("循环稳定性测试", "DALE", "EMIMTFSI", "未标注", "未标注", ["cycling"], "completed"),
    "experiments/2026-07-10-dale-solid-electrolyte-transmittance.md":
        ("透过率与光谱表征", "DALE", "无", "未标注", "未标注", ["uvvis"], "completed"),
    "experiments/2026-07-10-spectroechem-ato.md":
        ("响应时间测试", "LiClO4-ACN", "无", "1层ATO", "打孔注液", ["response_time"], "completed"),
    "experiments/2026-07-11-dale50-il50-voltage-response-time.md":
        ("响应时间测试", "DALE", "EMIMTFSI", "1层ATO", "未标注", ["response_time"], "completed"),
    "experiments/2026-07-11-tio2-spin-coating-film.md":
        ("薄膜制备", "不涉及", "不涉及", "不涉及", "不涉及", [], "needs_review"),
    "experiments/2026-07-13-pbi-cl-dye-soak-thickness.md":
        ("膜厚与形貌表征", "不涉及", "不涉及", "不涉及", "不涉及", ["thickness"], "completed"),
    "experiments/2026-09-08-electrolyte-screening-1fto-baseline-response-time.md":
        ("响应时间测试", "多体系对比", "EMIMTFSI", "单层+双层对比", "未标注", ["response_time"], "completed"),
    "experiments/2026-09-08-electrolyte-screening-air-baseline-response-time.md":
        ("响应时间测试", "多体系对比", "EMIMTFSI", "2层ATO", "未标注", ["response_time"], "completed"),
    "experiments/2026-09-14-spacer-120um-surlyn-vs-100um-tape-response-time.md":
        ("响应时间测试", "多体系对比", "EMIMTFSI", "未标注", "多方式对比", ["response_time"], "needs_review"),
    "experiments/2026-09-18-liclo4-acn-emim-response-time.md":
        ("响应时间测试", "LiClO4-ACN", "EMIMTFSI", "未标注", "沙林膜120μm", ["response_time"], "completed"),
    "experiments/2026-09-19-liclo4-acn-step-time-and-fade-voltage-response-time.md":
        ("响应时间测试", "LiClO4-ACN", "无", "未标注", "沙林膜120μm", ["response_time"], "completed"),
    "experiments/2026-10-13-new-pbi-cl-batch-baseline-response-time.md":
        ("响应时间测试", "LiClO4-ACN", "无", "2层ATO", "沙林膜120μm", ["response_time"], "needs_review"),
    "notes/2026-10-19-naming-convention-and-cross-batch-summary.md":
        ("规范与汇总", "不涉及", "不涉及", "不涉及", "不涉及", [], "completed"),
}

# 旧标签里属于"数据类型标记"的，转 data_types 后从 tags 移除
DATA_MARK_TAGS = ["含光谱电化学数据", "含循环稳定性数据", "含UV-Vis透过率数据",
                  "含膜厚数据", "数据已整理"]

FIELD_ORDER = ["type", "title", "date", "category", "electrolyte", "additive",
               "counter_electrode", "encapsulation", "data_types", "status",
               "tags", "modified", "related"]


def split_fm(text):
    """返回 (frontmatter 原文, 正文)"""
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_simple(fm_text):
    """解析 frontmatter 为 dict，保留 related 的原始行"""
    out = {}
    order = []
    cur = None
    buf = []
    for line in fm_text.split("\n"):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            if cur:
                out[cur] = buf
            cur = m.group(1)
            buf = [m.group(2)]
            order.append(cur)
        elif cur and (line.startswith("  ") or line.startswith("- ") or line.strip() == ""):
            buf.append(line)
    if cur:
        out[cur] = buf
    return out, order


def strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def parse_tags(raw):
    raw = str(raw).strip().strip("[]")
    return [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]


def norm_date(v):
    v = strip_quotes(v)
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", v)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    return v


def build_fm(fields, order):
    lines = []
    for k in FIELD_ORDER:
        if k not in fields:
            continue
        val = fields[k]
        if k == "tags":
            lines.append("tags: [%s]" % ", ".join(val))
        elif k == "data_types":
            lines.append("data_types: [%s]" % ", ".join(val))
        elif k == "related":
            lines.append("related:")
            for r in val:
                lines.append("  - %s" % r)
        else:
            lines.append('%s: "%s"' % (k, val))
    return "\n".join(lines)


def normalize(content, mapping, rel):
    fm_text, body = split_fm(content)
    if fm_text is None:
        return None, ["跳过：无 frontmatter"]
    fields, _ = parse_simple(fm_text)
    # 除 related 外，全部折叠成单个字符串，避免列表被当字符串写出
    for k in list(fields.keys()):
        if k == "related":
            continue
        fields[k] = " ".join(fields[k]).strip()
    changes = []

    cat, ele, add, ce, enc, dts, st = mapping

    def setf(key, new):
        old = strip_quotes(fields.get(key, ""))
        if old != new:
            changes.append("  %-18s %s  ->  %s" % (key, old or "(空)", new))
        fields[key] = new

    setf("category", cat)
    setf("electrolyte", ele)
    setf("additive", add)
    setf("counter_electrode", ce)
    setf("encapsulation", enc)
    setf("status", st)

    old_dt = parse_tags(fields.get("data_types", ""))
    if sorted(old_dt) != sorted(dts):
        changes.append("  %-18s %s  ->  %s" % ("data_types", old_dt or "(空)", dts))
    fields["data_types"] = dts

    tags = parse_tags(fields.get("tags", ""))
    removed = [t for t in tags if t in DATA_MARK_TAGS]
    tags2 = [t for t in tags if t not in DATA_MARK_TAGS]
    if removed:
        changes.append("  %-18s 移除数据类型标记 %s" % ("tags", removed))
    fields["tags"] = tags2

    d = norm_date(fields.get("date", ""))
    if strip_quotes(fields.get("date", "")) != d:
        changes.append("  %-18s %s  ->  %s" % ("date", fields.get("date", "") or "(空)", d))
    fields["date"] = d

    if "modified" in fields:
        fields["modified"] = norm_date(fields["modified"])

    for k in ("title", "type"):
        if k in fields:
            fields[k] = strip_quotes(fields[k])

    if "related" in fields:
        rels = []
        for line in fields["related"]:
            s = line.strip()
            if s.startswith("- "):
                rels.append(s[2:].strip())
            elif s and s != "[]":
                rels.append(s)
        fields["related"] = rels

    new_fm = build_fm(fields, FIELD_ORDER)
    return "---\n%s\n---\n%s" % (new_fm, body), changes


def main():
    apply = "--apply" in sys.argv
    total = 0
    changed_files = 0
    for rel in sorted(MAP):
        path = os.path.join(PROJECT_DIR, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            print("[缺失] %s" % rel)
            continue
        with io.open(path, "r", encoding="utf-8") as f:
            content = f.read()
        new, changes = normalize(content, MAP[rel], rel)
        total += 1
        if new is None:
            print("[跳过] %s -- %s" % (rel, changes[0]))
            continue
        if changes:
            changed_files += 1
            print("=== %s" % rel)
            for c in changes:
                print(c)
            if apply:
                with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)
        else:
            print("[无变化] %s" % rel)
    print("\n共处理 %d 个文件，%d 个有改动。%s" %
          (total, changed_files, "已写盘。" if apply else "（预演模式，未写盘；加 --apply 生效）"))


if __name__ == "__main__":
    main()
