#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理实验记录正文中的"工艺参数见 methods/xxx.md"类内部文件指引（2026-11-04 用户要求：
看记录本网页的人不知道 methods 文件夹在哪，此类提示语对外无意义）。
括号内的具体工艺参数保留；frontmatter related 字段里的 methods 链接保留不动。

用法:
    python cleanup-methods-refs.py          # 预演，打印每处改动
    python cleanup-methods-refs.py --apply  # 写盘
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = ["experiments", "notes", "plans"]

# 顺序敏感：特化规则在前，兜底在后
RULES = [
    # "按 m/d 的标准流程" -> "按标准流程"（先于通用"按 m/d 的"）
    (re.compile(r'按 `methods/device-fabrication\.md` 的标准流程'), '按标准流程'),
    (re.compile(r'工艺同 `methods/device-fabrication\.md` 的'), '工艺同常规'),
    (re.compile(r'`methods/device-fabrication\.md` 登记的'), ''),
    (re.compile(r'按 `methods/device-fabrication\.md` 的'), '按标准'),
    # 保留括号内参数的形态
    (re.compile(r'，工艺参数见 `methods/device-fabrication\.md`（'), '（'),
    (re.compile(r'参数见 `methods/device-fabrication\.md`（'), '参数（'),
    (re.compile(r'染浴工艺见 `methods/device-fabrication\.md`（([^）]*)）'), r'染浴工艺：\1'),
    (re.compile(r'烧结程序见 `methods/device-fabrication\.md`（([^）]*)）'), r'烧结程序：\1'),
    (re.compile(r'操作步骤见 `methods/sem-operation\.md`（依据'), '操作步骤依据'),
    # 带后文
    (re.compile(r'，工艺参数见 `methods/device-fabrication\.md`。'), '。'),
    (re.compile(r'，工艺参数见 `methods/device-fabrication\.md`，'), '，'),
    (re.compile(r'^工艺参数见 `methods/device-fabrication\.md`；', re.M), ''),
    (re.compile(r'工艺参数见 `methods/device-fabrication\.md`，本次无改动。'), '本次无工艺改动。'),
    (re.compile(r'，\s*流程见 `methods/device-fabrication\.md`，无改动。'), '，无工艺改动。'),
    (re.compile(r'^制膜与烧结工艺见 `methods/device-fabrication\.md`，无改动。', re.M), '制膜与烧结按常规工艺，无改动。'),
    (re.compile(r'^染浴与后处理流程见 `methods/device-fabrication\.md`。', re.M), ''),
    # 整行删除
    (re.compile(r'^工艺参数见 `methods/device-fabrication\.md`。\s*\n?', re.M), ''),
    (re.compile(r'^.*的具体参数见 `methods/device-fabrication\.md`。\s*\n?', re.M), ''),
    (re.compile(r'^.*具体工艺参数统一见 `methods/device-fabrication\.md`，\s*\n?', re.M), ''),
    (re.compile(r'^清洗流程见 `methods/device-fabrication\.md`。\s*\n?', re.M), ''),
    (re.compile(r'^打孔型器件的封装流程见 `methods/device-fabrication\.md`「[^」]*」。\s*\n?', re.M), ''),
    (re.compile(r'^操作流程与拟合步骤(另)?见 `methods/eis\.md`。\s*\n?', re.M), ''),
    (re.compile(r'^- 参考操作流程：`methods/sem-operation\.md`\s*\n?', re.M), ''),
    (re.compile(r'^- (相关方法|方法文档)：`methods/xps-depth-profile\.md`\s*\n?', re.M), ''),
]

FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n?(.*)$', re.S)


def squeeze_blank(body):
    return re.sub(r'\n{3,}', '\n\n', body)


def process(path, apply):
    raw = io.open(path, 'r', encoding='utf-8-sig', newline='').read()
    crlf = '\r\n' in raw
    text = raw.replace('\r\n', '\n').replace('\r', '\n')
    m = FM_RE.match(text)
    if not m:
        return None
    fm, body = m.group(1), m.group(2)
    changed = []
    for pat, rep in RULES:
        def cb(mm, _rep=rep, _pat=pat, _ch=changed):
            old = mm.group(0)
            new = _pat.sub(_rep, old)
            return mm.group(0)
        newbody = pat.sub(rep, body)
        if newbody != body:
            changed.append((pat.pattern, rep))
            body = newbody
    if not changed:
        return None
    body = squeeze_blank(body)
    new_text = '---\n' + fm + '\n---\n' + body
    if crlf:
        new_text = new_text.replace('\n', '\r\n')
    if apply and new_text != raw:
        io.open(path, 'w', encoding='utf-8', newline='').write(new_text)
    return changed


def main():
    apply = '--apply' in sys.argv
    nfiles = 0
    total = 0
    for folder in FOLDERS:
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.md'):
                continue
            res = process(os.path.join(d, fn), apply)
            if res:
                nfiles += 1
                total += len(res)
                print('%s/%s  (%d 处)' % (folder, fn, len(res)))
                for pat, rep in res:
                    print('    %s  ->  %s' % (pat[:60], rep))
    print('\n模式: %s  改动文件: %d  改动处: %d' % ('APPLY' if apply else 'DRY-RUN', nfiles, total))


if __name__ == '__main__':
    main()
