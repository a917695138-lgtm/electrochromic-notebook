# -*- coding: utf-8 -*-
"""把实验记录本全部实验记录导出为打印用 Word。

- 数据源：experiments/ 下全部 md（按 date、文件名排序）
- 同一天的记录连续排版；跨日期插入分页符（每天新起一页）
- frontmatter 转为标题下方一行元信息（体系/阶段/标签）
- 不含内嵌图片（打印版正文为文字与表格）
- 输出经本地 editor_sdk（create_doc + doc_insert_markdown + doc_insert_page_break）

用法：python scripts/export-print-docx.py [输出docx路径]
"""
import os
import re
import subprocess
import sys
import tempfile

EDSDK_DIR = r'C:\Users\ao\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\workbuddy-local-office-edit'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else r'D:\Desktop\实验记录\实验记录打印版.docx'


def call(tool, **kv):
    args = ['python3', os.path.join(EDSDK_DIR, 'edsdk.py'), 'call', tool]
    for k, v in kv.items():
        if v is not None:
            args.append('%s=%s' % (k, v))
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding='utf-8', cwd=EDSDK_DIR)
    if r.returncode != 0:
        print('ERROR calling %s: %s %s' % (tool, r.stdout[-300:], r.stderr[-300:]))
        sys.exit(1)
    return r.stdout


def get_idx(out):
    for key in ('last_edit_index', 'position', 'index'):
        m = re.search(r'"%s"\s*:\s*(\d+)' % key, out)
        if m:
            return int(m.group(1))
    return None


def parse_fm(raw):
    m = re.match(r'^---\n(.*?)\n---\n', raw, re.S)
    if not m:
        return {}, raw
    fm_text, body = m.group(1), raw[m.end():]

    def get(key):
        mm = re.search(r'^%s:\s*"([^"]*)"' % key, fm_text, re.M)
        return mm.group(1) if mm else ''
    fm = {k: get(k) for k in ('date', 'title', 'system', 'stage')}
    tm = re.search(r'^tags:\s*\[([^\]]*)\]' , fm_text, re.M)
    fm['tags'] = [t.strip() for t in tm.group(1).split(',') if t.strip()] if tm else []
    return fm, body


def record_md(path):
    raw = open(path, 'rb').read().decode('utf-8-sig').replace('\r\n', '\n')
    fm, body = parse_fm(raw)
    lines = body.split('\n')
    # 去内嵌图片行、代码围栏行
    lines = [l for l in lines
             if not re.match(r'\s*!\[[^\]]*\]\([^)]*\)\s*$', l)
             and not re.match(r'^\s*```\w*\s*$', l)]
    body = '\n'.join(lines)
    body = re.sub(r'\n{3,}', '\n\n', body).strip() + '\n'
    # H1 之后插入元信息行
    m = re.match(r'^(#[^\n]*\n)', body)
    meta = '体系：%s ｜ 阶段：%s ｜ 标签：%s' % (
        fm.get('system') or '—', fm.get('stage') or '—', '、'.join(fm.get('tags', [])) or '—')
    if m:
        body = m.group(1) + '\n' + meta + '\n' + body[m.end():]
    else:
        body = meta + '\n\n' + body
    return fm, body


def main():
    files = sorted(
        (os.path.join(ROOT, 'experiments', fn)
         for fn in os.listdir(os.path.join(ROOT, 'experiments'))
         if fn.endswith('.md')),
        key=lambda p: (os.path.basename(p)[:10] if re.match(r'\d{4}-\d{2}-\d{2}', os.path.basename(p)) else '9999', p))
    # 按日期分组
    groups = {}
    order = []
    for p in files:
        fm, md = record_md(p)
        d = fm.get('date') or os.path.basename(p)[:10]
        if d not in groups:
            groups[d] = []
            order.append(d)
        groups[d].append(md)
    print('共 %d 条记录、%d 个日期组' % (len(files), len(order)))

    out = call('create_doc')
    m = re.search(r'file_id[=:\s]+([^\s,"\']+)', out)
    file_id = m.group(1) if m else None
    print('file_id =', file_id)
    if not file_id:
        print('create_doc 输出异常：', out[:300])
        sys.exit(1)

    idx = 0
    for gi, d in enumerate(order):
        if gi > 0:
            out = call('doc_insert_page_break', file_id=file_id, idx=idx)
            new = get_idx(out)
            if new is not None:
                idx = new
            # 分页符后必须先插一个空段落，否则块级 markdown 插入会失败
            out = call('doc_insert_paragraph', file_id=file_id, idx=idx)
            new = get_idx(out)
            if new is not None:
                idx = new
        md = '**%s**\n\n' % d + '\n\n'.join(groups[d])
        tmp = os.path.join(tempfile.gettempdir(), 'nb-print-%03d.md' % gi)
        with open(tmp, 'wb') as f:
            f.write(md.encode('utf-8'))
        out = call('doc_insert_markdown', file_id=file_id, idx=idx,
                   **{'markdown': 'file://%s' % tmp})
        new = get_idx(out)
        if new is None:
            print('第 %d 组（%s）未返回插入位置：%s' % (gi, d, out[:300]))
            sys.exit(1)
        idx = new
        print('[%d/%d] %s 完成，idx=%d' % (gi + 1, len(order), d, idx))
        os.remove(tmp)

    call('save_file', file_id=file_id, file_path=OUT)
    print('已保存：', OUT)


if __name__ == '__main__':
    main()
