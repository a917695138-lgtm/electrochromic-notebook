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
    # 去代码围栏行（图片行保留，由 insert_group 分段插入）
    lines = [l for l in lines if not re.match(r'^\s*```\w*\s*$', l)]
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


IMG_LINE = re.compile(r'^\s*!\[([^\]]*)\]\(([^)\n]+)\)\s*$')


def insert_group(file_id, md, idx, n_groups):
    """按行扫描：文本段走 markdown 插入，图片行走 doc_insert_image（后补段落分隔符）。"""
    buf = []
    n_img = 0
    for line in md.split('\n'):
        m = IMG_LINE.match(line)
        if not m:
            buf.append(line)
            continue
        text = '\n'.join(buf).strip('\n')
        buf = []
        if text:
            tmp = os.path.join(tempfile.gettempdir(), 'nb-print-seg-%03d.md' % n_groups)
            with open(tmp, 'wb') as f:
                f.write(text.encode('utf-8'))
            out = call('doc_insert_markdown', file_id=file_id, idx=idx,
                       **{'markdown': 'file://%s' % tmp})
            new = get_idx(out)
            if new is None:
                raise RuntimeError('markdown 插入未返回位置: %s' % out[:200])
            idx = new
            os.remove(tmp)
        # 图片：assets/ 相对路径转绝对路径；限制宽度 450px 防超版心
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
            # 图片文件不存在时降级为文字说明
            buf.append('*（图：%s）*' % m.group(1))
    text = '\n'.join(buf).strip('\n')
    if text:
        tmp = os.path.join(tempfile.gettempdir(), 'nb-print-seg-%03d.md' % n_groups)
        with open(tmp, 'wb') as f:
            f.write(text.encode('utf-8'))
        out = call('doc_insert_markdown', file_id=file_id, idx=idx,
                   **{'markdown': 'file://%s' % tmp})
        new = get_idx(out)
        if new is None:
            raise RuntimeError('markdown 插入未返回位置: %s' % out[:200])
        idx = new
        os.remove(tmp)
    return idx, n_img


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
        idx, n_img = insert_group(file_id, md, idx, gi)
        print('[%d/%d] %s 完成，idx=%d，图 %d 张' % (gi + 1, len(order), d, idx, n_img))

    call('save_file', file_id=file_id, file_path=OUT)
    print('已保存：', OUT)


if __name__ == '__main__':
    main()
