#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一次性迁移：把旧的 6 个受控分面字段
(category / electrolyte / additive / counter_electrode / encapsulation / baseline)
替换为 system(体系) + stage(阶段) 两个字段，并把旧字段里有信息量的取值追加到 tags。

用法:
    python migrate-system-stage.py            # 预演，只打印统计与抽样
    python migrate-system-stage.py --apply    # 写盘

2026-11-03 用户确认口径：
  system: 液态电解质 / DALE体系 / PAPB体系 / 通用
  stage : 制备 / 测试与表征 / 不适用
"""
import os
import re
import io
import sys
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = ["experiments", "notes", "plans", "methods", "data", "reminders"]

OLD_FIELDS = ["category", "electrolyte", "additive",
              "counter_electrode", "encapsulation", "baseline"]
SKIP_VALS = {"", "不涉及", "未标注", "无", "-", "未标注"}

SYSTEM_MAP = {
    "DALE": "DALE体系",
    "PAPB": "PAPB体系",
    "LiClO4-ACN": "液态电解质",
    "LiTFSI-ACN": "液态电解质",
    "PMMA凝胶": "液态电解质",
    "多体系对比": "液态电解质",
}

PREP_CATS = {
    "薄膜制备", "染料配制与染浴", "器件组装与封装", "电解质配制", "器件制备",
}
TEST_CATS = {
    "响应时间测试", "循环稳定性测试", "膜厚与形貌表征", "形貌表征",
    "透过率与光谱表征", "电化学阻抗测试", "表面与界面表征", "力学性能测试",
    "结构与物相表征", "器件展示与现象观察", "光学性能", "元素分析",
    "电化学分析", "分子结构分析", "表面成分分析", "比表面积与孔结构",
}
DOC_CATS = {"规范与汇总", "组会与讨论", "实验方案", "数据管理"}
DOC_FOLDERS = {"plans", "methods", "data", "reminders", "notes"}

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.S)
LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def unq(v):
    v = str(v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_tags(v):
    v = str(v).strip().strip("[]")
    return [x.strip().strip("\"'") for x in v.split(",") if x.strip()]


def decide(folder, d):
    if folder in DOC_FOLDERS:
        return "通用", "不适用"
    ele = unq(d.get("electrolyte", ""))
    system = SYSTEM_MAP.get(ele, "通用")
    cat = unq(d.get("category", ""))
    if cat in PREP_CATS:
        stage = "制备"
    elif cat in TEST_CATS:
        stage = "测试与表征"
    else:
        stage = "不适用"
    return system, stage


def collect_extras(d):
    out = []
    for k in OLD_FIELDS:
        v = unq(d.get(k, ""))
        if not v or v in SKIP_VALS:
            continue
        if v not in out:
            out.append(v)
    return out


def process(path, folder, apply):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        raw = f.read()
    crlf = "\r\n" in raw
    bom = False
    with open(path, "rb") as f:
        bom = f.read(3) == b"\xef\xbb\xbf"
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    m = FM_RE.match(text)
    if not m:
        return None, "NO-FM"
    fm, body = m.group(1), m.group(2)

    d = {}
    for ln in fm.split("\n"):
        mm = LINE_RE.match(ln)
        if mm:
            d[mm.group(1)] = mm.group(2).strip()

    system, stage = decide(folder, d)
    extras = collect_extras(d)

    out_lines = []
    has_system = has_stage = False
    for ln in fm.split("\n"):
        mm = LINE_RE.match(ln)
        if mm and mm.group(1) in OLD_FIELDS:
            continue
        if mm and mm.group(1) == "system":
            has_system = True
            out_lines.append('system: "%s"' % system)
            continue
        if mm and mm.group(1) == "stage":
            has_stage = True
            out_lines.append('stage: "%s"' % stage)
            continue
        if mm and mm.group(1) == "tags":
            tags = parse_tags(mm.group(2))
            for x in extras:
                if x not in tags:
                    tags.append(x)
            out_lines.append("tags: [" + ", ".join(tags) + "]")
            continue
        out_lines.append(ln)

    new_fields = []
    if not has_system:
        new_fields.append('system: "%s"' % system)
    if not has_stage:
        new_fields.append('stage: "%s"' % stage)
    if new_fields:
        pos = None
        for pref in ("date", "title", "type"):
            for i, ln in enumerate(out_lines):
                if ln.startswith(pref + ":"):
                    pos = i + 1
                    break
            if pos is not None:
                break
        if pos is None:
            pos = 0
        out_lines[pos:pos] = new_fields

    new_text = "---\n" + "\n".join(out_lines) + "\n---\n" + body
    if crlf:
        new_text = new_text.replace("\n", "\r\n")
    if apply and new_text != raw:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            if bom:
                f.write(u"\ufeff")
            f.write(new_text)
    return (system, stage, len(extras)), None


def main():
    apply = "--apply" in sys.argv
    stats = collections.Counter()
    samples = []
    errors = []
    n = 0
    for folder in FOLDERS:
        p = os.path.join(ROOT, folder)
        if not os.path.isdir(p):
            continue
        for fn in sorted(os.listdir(p)):
            if not fn.endswith(".md"):
                continue
            n += 1
            res, err = process(os.path.join(p, fn), folder, apply)
            if err:
                errors.append("%s/%s: %s" % (folder, fn, err))
                continue
            system, stage, nx = res
            stats[(folder, system, stage)] += 1
            if len(samples) < 6:
                samples.append("%-12s %-12s %-10s %s" % (folder, system, stage, fn))
    print("文件数: %d  模式: %s" % (n, "APPLY" if apply else "DRY-RUN"))
    print("\n== 映射分布 ==")
    for (folder, system, stage), c in sorted(stats.items()):
        print("  %-12s %-12s %-10s %d" % (folder, system, stage, c))
    print("\n== 抽样 ==")
    for s in samples:
        print("  " + s)
    if errors:
        print("\n== 异常 ==")
        for e in errors:
            print("  " + e)
    print("\n合计: %d 条" % sum(stats.values()))


if __name__ == "__main__":
    main()
