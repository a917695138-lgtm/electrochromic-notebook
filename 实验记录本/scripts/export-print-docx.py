# -*- coding: utf-8 -*-
"""把实验记录本全部实验记录导出为打印用 Word（美化版，按月分文件）。

- 数据源：experiments/ 下全部 md（按日期排序）
- 输出目录：默认 D:\\Desktop\\实验记录\\实验记录打印版\\，每月一个 YYYY-MM.docx
- 增量更新：某月任一 md 的 mtime 晚于该月 docx（或 docx 不存在）才重建该月，
  其余月份跳过；删除/大改历史记录后用 --force 或 --month 重建
- 每个日期一页：日期放大居中加粗置顶（H1）；当天记录标题不重复日期
- 记录标题（H2 青色）→ 数据类型标签行 → 体系/阶段/标签元信息行 → 正文（H3 橙色）
- 正文加粗文本用网页着重色 #1D4ED8；内嵌图片（assets/），跨日期分页
- 样式/表格/列表后处理全部在 print_docx_post.py（python-docx，Word 可直接打开）；
  禁止用 editor_sdk 的 doc_update_named_style 改标题样式（会写出损坏文件）

用法：
  python scripts/export-print-docx.py                  # 增量：只重建有变更的月份
  python scripts/export-print-docx.py --force          # 全部月份强制重建
  python scripts/export-print-docx.py --month 2026-11  # 指定月份强制重建
  python scripts/export-print-docx.py --dir <目录>      # 指定输出目录
  python scripts/export-print-docx.py <单文件.docx>    # 旧版单文件全量导出
  python scripts/export-print-docx.py --post <docx>    # 只重跑某个 docx 的后处理
调试开关：环境变量 NB_PRINT_LIMIT=N（单文件模式只导前 N 个日期组）、NB_NO_POST=1（跳过后处理）。
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
DEFAULT_DIR = r'D:\Desktop\实验记录\实验记录打印版'

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


def export_doc(order, groups, out_path):
    """把 order 里的日期组导出为一个 docx（每月一个文件 / 单文件全量共用）。"""
    out = call('create_doc')
    m = re.search(r'file_id=([^\s,]+)', out)
    file_id = m.group(1) if m else None
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
        print('  [%d/%d] %s 完成，图 %d 张' % (gi + 1, len(order), d, n_img))

    call('save_file', file_id=file_id, file_path=out_path)
    if os.environ.get('NB_NO_POST'):
        print('（调试）跳过后处理：', out_path)
    else:
        postprocess_xml(out_path)
        print('已保存：', out_path)


def parse_args(argv):
    post_path = None
    month = None
    force = False
    out_dir = DEFAULT_DIR
    single = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--post' and i + 1 < len(argv):
            post_path = argv[i + 1]
            i += 1
        elif a == '--month' and i + 1 < len(argv):
            month = argv[i + 1]
            i += 1
        elif a == '--dir' and i + 1 < len(argv):
            out_dir = argv[i + 1]
            i += 1
        elif a == '--force':
            force = True
        elif a.endswith('.docx') and single is None:
            single = a
        else:
            print('无法识别参数：', a)
            sys.exit(2)
        i += 1
    return post_path, month, force, out_dir, single


def main():
    post_path, month, force, out_dir, single = parse_args(sys.argv[1:])
    if post_path:
        postprocess_xml(post_path)
        print('仅后处理完成：', post_path)
        return
    if month and not re.match(r'^\d{4}-\d{2}$', month):
        print('--month 需要 YYYY-MM 格式，收到：', month)
        sys.exit(2)

    files = list_files()
    groups = {}
    order = []
    date_src = {}
    for p in files:
        fm, md = record_md(p)
        d = fm.get('date') or os.path.basename(p)[:10]
        groups.setdefault(d, []).append(md)
        date_src.setdefault(d, []).append(p)
        if d not in order:
            order.append(d)
    print('共 %d 条记录、%d 个日期组' % (len(files), len(order)))

    # 旧版单文件全量模式
    if single:
        limit = int(os.environ.get('NB_PRINT_LIMIT', '0') or 0)
        if limit:
            order = order[:limit]
            print('（调试）仅导出前 %d 个日期组' % len(order))
        export_doc(order, groups, single)
        return

    # 按月分文件
    months = {}
    for d in order:
        months.setdefault(d[:7], []).append(d)
    if month:
        if month not in months:
            print('该月份没有实验记录：', month)
            return
        months = {month: months[month]}
        force = True
    os.makedirs(out_dir, exist_ok=True)

    todo = []
    for mo in sorted(months):
        outp = os.path.join(out_dir, '%s.docx' % mo)
        if force or not os.path.exists(outp):
            todo.append((mo, outp))
            continue
        newest_md = max(os.path.getmtime(p) for d in months[mo] for p in date_src[d])
        if newest_md > os.path.getmtime(outp):
            todo.append((mo, outp))
        else:
            print('跳过（无变更）：', os.path.basename(outp))
    if not todo:
        print('所有月份均已是最新，无需重建。目录：%s' % out_dir)
        return

    for mo, outp in todo:
        print('重建 %s（%d 个日期组）' % (os.path.basename(outp), len(months[mo])))
        export_doc(months[mo], groups, outp)
    print('完成：%d 个月份文件已更新于 %s' % (len(todo), out_dir))


if __name__ == '__main__':
    main()
