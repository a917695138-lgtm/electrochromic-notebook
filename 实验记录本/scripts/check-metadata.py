#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校验实验记录本所有 .md 的 frontmatter 是否符合受控词表。

用法:
    python check-metadata.py
零告警才算通过。
"""
import os
import re
import sys
import io

PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
FOLDERS = ["experiments", "notes", "plans", "methods", "data", "reminders"]

VOCAB = {
    "category": ["薄膜制备", "染料配制与染浴", "器件组装与封装", "响应时间测试",
                 "循环稳定性测试", "透过率与光谱表征", "膜厚与形貌表征",
                 "表面与界面表征", "结构与物相表征", "电化学阻抗测试",
                 "规范与汇总", "组会与讨论"],
    "electrolyte": ["LiClO4-ACN", "LiTFSI-ACN", "DALE", "PMMA凝胶", "多体系对比", "不涉及", "未标注"],
    "additive": ["EMIMTFSI", "无", "不涉及"],
    "counter_electrode": ["1层ATO", "2层ATO", "单层+双层对比", "未标注", "不涉及"],
    "encapsulation": ["沙林膜60μm", "沙林膜120μm", "双面胶100μm", "打孔注液", "多方式对比", "未标注", "不涉及"],
    "baseline": ["空气基线", "1FTO校正", "多基线对比", "不涉及", "未标注"],
    "status": ["completed", "needs_review", "in-progress", "planned"],
}
# 按文件夹分级：实验类要全套受控字段，方法/方案类不要求电解质与器件字段
FOLDER_RULES = {
    "experiments": {"required": ["type", "title", "date", "category"],
                    "vocab": ["category", "electrolyte", "additive",
                              "counter_electrode", "encapsulation", "baseline", "status"],
                    "lists": True},
    "notes": {"required": ["type", "title", "date", "category"],
              "vocab": ["category", "electrolyte", "additive",
                        "counter_electrode", "encapsulation", "status"],
              "lists": True},
    "plans": {"required": ["type", "title", "date"], "vocab": [], "lists": False},
    "methods": {"required": ["type", "title"], "vocab": [], "lists": False},
    "data": {"required": [], "vocab": [], "lists": False},
    "reminders": {"required": ["type", "title", "date"], "vocab": [], "lists": False},
}
LIST_FIELDS = {"data_types": ["response_time", "cycling", "uvvis", "thickness", "sem", "eds", "xps"]}
# project 字段已于 2026-10-21 废弃；发现残留即告警
FORBIDDEN_FIELDS = ["project"]


def split_fm(text):
    if not text.startswith("---"):
        return None
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    return m.group(1) if m else None


def parse(fm):
    out = {}
    cur = None
    for line in fm.split("\n"):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and line.strip().startswith("- "):
            out[cur] += "\n" + line.strip()
    return out


def unq(v):
    v = str(v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def main():
    warnings = []
    files = 0

    for folder in FOLDERS:
        p = os.path.join(PROJECT_DIR, folder)
        if not os.path.isdir(p):
            continue
        for fn in sorted(os.listdir(p)):
            if not fn.endswith(".md"):
                continue
            files += 1
            rel = "%s/%s" % (folder, fn)
            with io.open(os.path.join(p, fn), "r", encoding="utf-8-sig") as f:
                text = f.read()
            fm = split_fm(text)
            if fm is None:
                warnings.append("[%s] 缺少 frontmatter" % rel)
                continue
            rule = FOLDER_RULES.get(folder, {"required": [], "vocab": [], "lists": False})
            d = parse(fm)
            for k in FORBIDDEN_FIELDS:
                if k in d:
                    warnings.append("[%s] 含已废弃字段 %s（请删除）" % (rel, k))
            for k in rule["required"]:
                if k not in d or not unq(d.get(k, "")):
                    warnings.append("[%s] 缺少必填字段 %s" % (rel, k))
            for k in rule["vocab"]:
                allowed = VOCAB[k]
                if k not in d:
                    warnings.append("[%s] 缺少受控字段 %s" % (rel, k))
                    continue
                v = unq(d[k])
                if v not in allowed:
                    warnings.append("[%s] %s 取值不在词表内: %s" % (rel, k, v))
            if rule["lists"]:
                for k, allowed in LIST_FIELDS.items():
                    if k not in d:
                        warnings.append("[%s] 缺少列表字段 %s" % (rel, k))
                        continue
                    raw = d[k].strip().strip("[]")
                    for item in [x.strip().strip("\"'") for x in raw.split(",")]:
                        if item and item not in allowed:
                            warnings.append("[%s] %s 取值不在词表内: %s" % (rel, k, item))
            dt = unq(d.get("date", ""))
            if dt and not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                warnings.append("[%s] date 格式不是 YYYY-MM-DD: %s" % (rel, dt))

    print("校验文件数: %d" % files)
    if warnings:
        print("发现 %d 条告警:" % len(warnings))
        for w in warnings:
            print("  " + w)
        sys.exit(1)
    print("零告警，全部符合受控词表。")


if __name__ == "__main__":
    main()
