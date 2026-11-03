#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校验实验记录本所有 .md 的 frontmatter 是否符合受控词表。

用法:
    python check-metadata.py
零告警才算通过。

2026-11-03 简化口径（用户确认）：
  旧的 category / electrolyte / additive / counter_electrode / encapsulation / baseline
  六个分面字段已全部废弃，改为 system(体系) + stage(阶段) 两级分类。
  旧字段的有信息量取值已移入 tags 与正文，因此列为 FORBIDDEN，发现残留即告警。
"""
import os
import re
import sys
import io

PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
FOLDERS = ["experiments", "notes", "plans", "methods", "data", "reminders"]

VOCAB = {
    "system": ["液态电解质", "DALE体系", "PAPB体系", "通用"],
    "stage": ["制备", "测试与表征", "不适用"],
    "status": ["completed", "needs_review", "in-progress", "planned"],
}

# 所有文件夹都要求体系与阶段；实验类额外要求状态与数据类型
FOLDER_RULES = {
    "experiments": {"required": ["type", "title", "date", "system", "stage", "status"],
                    "vocab": ["system", "stage", "status"], "lists": True},
    "notes": {"required": ["type", "title", "date", "system", "stage"],
              "vocab": ["system", "stage", "status"], "lists": True},
    "plans": {"required": ["type", "title", "date", "system", "stage"],
              "vocab": ["system", "stage", "status"], "lists": False},
    "methods": {"required": ["type", "title", "system", "stage"],
                "vocab": ["system", "stage", "status"], "lists": False},
    "data": {"required": ["system", "stage"],
             "vocab": ["system", "stage", "status"], "lists": False},
    "reminders": {"required": ["type", "title", "date", "system", "stage"],
                  "vocab": ["system", "stage", "status"], "lists": False},
}
LIST_FIELDS = {"data_types": ["response_time", "cycling", "uvvis", "thickness", "sem", "eds", "xps"]}
# 已废弃字段：发现残留即告警
FORBIDDEN_FIELDS = ["project", "category", "electrolyte", "additive",
                    "counter_electrode", "encapsulation", "baseline"]


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
                if k not in d:
                    continue  # 字段缺失由 required 管，这里只校验取值
                v = unq(d[k])
                if v and v not in VOCAB[k]:
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
