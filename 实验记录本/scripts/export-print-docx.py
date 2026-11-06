# -*- coding: utf-8 -*-
"""把实验记录本全部实验记录导出为打印用 Word（美化版）。

- 数据源：experiments/ 下全部 md（按日期排序）
- 每个日期一页：日期放大居中加粗置顶（H1）；当天记录标题不重复日期
- 记录标题（H2 青色）→ 数据类型标签行 → 体系/阶段/标签元信息行 → 正文（H3 橙色）
- 正文加粗文本用网页着重色 #1D4ED8（XML 后处理，标题除外）
- 内嵌图片（assets/），跨日期分页

流程：editor_sdk 插入（markdown + 图片 + 分页符）→ 命名样式整体配色 →
保存 → XML 后处理正文粗体上色与元信息行灰斜体。

用法：python scripts/export-print-docx.py [输出docx路径]
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

EDSDK_DIR = r'C:\Users\ao\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\workbuddy-local-office-edit'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST_ONLY = len(sys.argv) > 2 and sys.argv[1] == '--post'
OUT = (sys.argv[2] if POST_ONLY else
       (sys.argv[1] if len(sys.argv) > 1 else r'D:\Desktop\实验记录\实验记录打印版.docx'))

# 配色（对齐网页版 read-content：h1 蓝 / h2 青 / h3 橙 / 加粗着重蓝）
C_H1, C_H2, C_H3, C_H4 = '1E3A8A', '115E59', '9A3412', '374151'
C_BOLD = '1D4ED8'
C_META = '6B7280'


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


def calljson(tool, payload):
    tf = os.path.join(tempfile.gettempdir(), 'edsdk-args.json')
    with open(tf, 'w', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False))
    r = subprocess.run(['python3', os.path.join(EDSDK_DIR, 'edsdk.py'), 'call',
                        tool, '--json-file', tf],
                       capture_output=True, text=True, encoding='utf-8', cwd=EDSDK_DIR)
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
    tm = re.search(r'^tags:\s*\[([^\]]*)\]', fm_text, re.M)
    fm['tags'] = [t.strip() for t in tm.group(1).split(',') if t.strip()] if tm else []
    return fm, body


IMG_LINE = re.compile(r'^\s*!\[([^\]]*)\]\(([^)\n]+)\)\s*$')
TAG_PREFIX = re.compile(r'^(\[[^\]]+\])\s*')


def record_md(path):
    raw = open(path, 'rb').read().decode('utf-8-sig').replace('\r\n', '\n')
    fm, body = parse_fm(raw)
    lines = body.split('\n')
    # 去代码围栏行
    lines = [l for l in lines if not re.match(r'^\s*```\w*\s*$', l)]
    body = '\n'.join(lines)
    body = re.sub(r'\n{3,}', '\n\n', body).strip() + '\n'

    # H1 拆出：[含XX数据] 标签前缀 + 日期前缀剥离
    m = re.match(r'^#\s*([^\n]*)\n', body)
    title = m.group(1).strip() if m else fm.get('title', '')
    rest = body[m.end():] if m else body
    tag = None
    tag_parts = []
    while True:
        tm = TAG_PREFIX.match(title)
        if not tm:
            break
        tag_parts.append(tm.group(1))
        title = title[tm.end():].strip()
    if tag_parts:
        tag = ' '.join(tag_parts)
    title = re.sub(r'^\d{4}-\d{2}-\d{2}\s*', '', title).strip()

    # 正文标题降一级（## -> ### 等）
    rest = re.sub(r'^(#{1,6}) ', lambda mm: mm.group(1) + '# ', rest, flags=re.M)

    meta = '体系：%s ｜ 阶段：%s ｜ 标签：%s' % (
        fm.get('system') or '—', fm.get('stage') or '—', '、'.join(fm.get('tags', [])) or '—')
    parts = ['## %s' % title]
    if tag:
        parts.append('**%s**' % tag)
    parts.append(meta)
    parts.append(rest.strip())
    return fm, '\n\n'.join(parts)


SEG_SEQ = [0]


def insert_markdown(file_id, text, idx):
    text = text.strip('\n')
    if not text:
        return idx
    SEG_SEQ[0] += 1
    tmp = os.path.join(tempfile.gettempdir(), 'nb-print-seg-%03d.md' % SEG_SEQ[0])
    with open(tmp, 'wb') as f:
        f.write(text.encode('utf-8'))
    out = call('doc_insert_markdown', file_id=file_id, idx=idx,
               **{'markdown': 'file://%s' % tmp})
    os.remove(tmp)
    new = get_idx(out)
    if new is None:
        raise RuntimeError('markdown 插入未返回位置: %s' % out[:200])
    return new


def insert_group(file_id, md, idx):
    """按行扫描：文本段走 markdown 插入，图片行走 doc_insert_image（后补段落分隔符）。"""
    buf = []
    n_img = 0
    for line in md.split('\n'):
        m = IMG_LINE.match(line)
        if not m:
            buf.append(line)
            continue
        idx = insert_markdown(file_id, '\n'.join(buf), idx)
        buf = []
        rel = m.group(2)
        abs_path = rel if os.path.isabs(rel) else os.path.join(ROOT, rel.replace('/', os.sep))
        if os.path.exists(abs_path):
            out = call('doc_insert_image', file_id=file_id, idx=idx,
                       image_path=abs_path, w=450)
            new = get_idx(out)
            idx = new if new is not None else idx + 1
            out = call('doc_insert_paragraph', file_id=file_id, idx=idx)
            new = get_idx(out)
            idx = new if new is not None else idx + 1
            n_img += 1
        else:
            buf.append('*（图：%s）*' % m.group(1))
    idx = insert_markdown(file_id, '\n'.join(buf), idx)
    return idx, n_img


def apply_styles(file_id):
    for h, color, size, jc in [(1, C_H1, 16, 'center'), (2, C_H2, 14, 'left'),
                               (3, C_H3, 12, 'left'), (4, C_H4, 11, 'left')]:
        calljson('doc_update_named_style', {
            'file_id': file_id, 'named_style_type': 'HEADING_%d' % h,
            'paragraph_style': {'jc': jc},
            'text_style': {'font_size': size, 'bold': True, 'color': color,
                           'font_family': '黑体'}})
    calljson('doc_update_named_style', {
        'file_id': file_id, 'named_style_type': 'NORMAL_TEXT',
        'paragraph_style': {'line_spacing': 1.4, 'line_spacing_rule': 1},
        'text_style': {'font_size': 10.5, 'font_family': '宋体'}})


VENV_PY = r'C:/Users/ao/.workbuddy/binaries/python/envs/default/Scripts/python.exe'


def postprocess_xml(path):
    """交给 python-docx 后处理（元素顺序符合 schema，Word 可直接打开）。"""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'print_docx_post.py')
    r = subprocess.run([VENV_PY, script, path], capture_output=True, text=True, encoding='utf-8')
    msg = (r.stdout or '').strip()
    if msg:
        print(msg)
    if r.returncode != 0:
        print('后处理失败：', (r.stderr or '')[-800:])
        sys.exit(1)


def list_files():
    return sorted(
        (os.path.join(ROOT, 'experiments', fn)
         for fn in os.listdir(os.path.join(ROOT, 'experiments'))
         if fn.endswith('.md')),
        key=lambda p: (os.path.basename(p)[:10] if re.match(r'\d{4}-\d{2}-\d{2}', os.path.basename(p)) else '9999', p))


def main():
    files = list_files()
    if POST_ONLY:
        postprocess_xml(OUT)
        print('仅后处理完成：', OUT)
        return
    groups = {}
    order = []
    for p in files:
        fm, md = record_md(p)
        d = fm.get('date') or os.path.basename(p)[:10]
        if d not in groups:
            groups[d] = []
            order.append(d)
        groups[d].append(md)
    limit = int(os.environ.get('NB_PRINT_LIMIT', '0') or 0)
    if limit:
        order = order[:limit]
        print('（调试）仅导出前 %d 个日期组' % len(order))
    print('共 %d 条记录、%d 个日期组' % (len(files), len(order)))

    out = call('create_doc')
    m = re.search(r'file_id=([^\s,]+)', out)
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
        md = '# %s\n\n' % d + '\n\n'.join(groups[d])
        idx, n_img = insert_group(file_id, md, idx)
        print('[%d/%d] %s 完成，idx=%d，图 %d 张' % (gi + 1, len(order), d, idx, n_img))

    # 样式改由 print_docx_post.py 用 python-docx 设置（editor_sdk 改标题样式会产出 Word 不认的文件）
    call('save_file', file_id=file_id, file_path=OUT)
    if os.environ.get('NB_NO_POST'):
        print('（调试）跳过后处理：', OUT)
    else:
        postprocess_xml(OUT)
        print('已保存并后处理：', OUT)


if __name__ == '__main__':
    main()
