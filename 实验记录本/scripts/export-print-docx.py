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


def numid_format(numbering):
    """numId -> 一级编号格式（decimal / bullet / ...）。"""
    ab = {}
    for m in re.finditer(r'<w:abstractNum [^>]*w:abstractNumId="(\d+)"[^>]*>(.*?)</w:abstractNum>',
                         numbering, re.S):
        lvl = re.search(r'<w:lvl [^>]*w:ilvl="0"[^>]*>(.*?)</w:lvl>', m.group(2), re.S)
        fmt = re.search(r'<w:numFmt w:val="([^"]+)"', lvl.group(1)) if lvl else None
        ab[m.group(1)] = fmt.group(1) if fmt else 'bullet'
    out = {}
    for m in re.finditer(r'<w:num w:numId="(\d+)"[^>]*>\s*<w:abstractNumId w:val="(\d+)"', numbering):
        out[m.group(1)] = ab.get(m.group(2), 'bullet')
    return out


def literalize_numbering(doc, fmt_of, heading_ids=None):
    """把 decimal 自动编号改成字面量数字。

    同一段连续的列表（中间不插标题/正文）从 1 连续编号，遇到其他段落就重新起算；
    这样既不会跨记录累加，也不会出现 5 之后跳到 3 的断档。
    """
    heading_ids = heading_ids or set()
    state = {'n': 0}

    def handle(pm):
        pm_text = pm.group(0)
        sm = re.search(r'<w:pStyle w:val="([^"]+)"', pm_text)
        if sm and sm.group(1) in heading_ids:      # 标题一定断开列表
            state['n'] = 0
            return pm_text
        nm = re.search(r'<w:numPr>(.*?)</w:numPr>', pm_text, re.S)
        body = nm.group(1) if nm else ''
        im = re.search(r'<w:ilvl w:val="(\d+)"', body)
        idm = re.search(r'<w:numId w:val="(\d+)"', body)
        ilvl = im.group(1) if im else '0'
        num_id = idm.group(1) if idm else ''
        is_decimal = bool(nm) and fmt_of.get(num_id, 'bullet') == 'decimal'

        if not is_decimal:
            state['n'] = 0            # 标题、正文、项目符号都断开列表
            return pm_text

        state['n'] += 1
        n = state['n']

        indent = '<w:ind w:left="%d" w:hanging="420"/>' % (420 * (int(ilvl) + 1))
        ppr = re.search(r'<w:pPr>(.*?)</w:pPr>', pm_text, re.S)
        if ppr:
            inner = re.sub(r'<w:numPr>.*?</w:numPr>', '', ppr.group(1), flags=re.S)
            if '<w:ind ' not in inner:
                inner += indent
            new_ppr = '<w:pPr>%s</w:pPr>' % inner
            pm_text = pm_text[:ppr.start()] + new_ppr + pm_text[ppr.end():]
        else:
            pm_text = pm_text.replace('<w:p ', '<w:p><w:pPr>%s</w:pPr>' % indent, 1)
        run = ('<w:r><w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr>'
               '<w:t xml:space="preserve">%d.</w:t><w:tab/></w:r>' % n)
        m_ppr = re.search(r'</w:pPr>', pm_text)
        if m_ppr:
            return pm_text[:m_ppr.end()] + run + pm_text[m_ppr.end():]
        return pm_text

    return re.sub(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>', handle, doc, flags=re.S)


def doc_avail_width(doc):
    """版心宽度（twips）：页宽 − 左右页边距。"""
    wm = re.search(r'<w:pgSz [^>]*w:w="(\d+)"', doc)
    lm = re.search(r'<w:pgMar [^>]*w:left="(\d+)"', doc)
    rm = re.search(r'<w:pgMar [^>]*w:right="(\d+)"', doc)
    w = int(wm.group(1)) if wm else 11906
    l = int(lm.group(1)) if lm else 1800
    r = int(rm.group(1)) if rm else 1800
    return max(4000, w - l - r)


CELL_TXT = re.compile(r'<w:t[^>]*>([^<]*)</w:t>')


def table_col_widths(table_xml, avail, char_tw=116, pad=130):
    """按每列内容估算宽度：先保住不可断开的短 token（数字/单位），再按需求分配余量。"""
    rows = re.findall(r'<w:tr[ >](?:(?!</w:tr>).)*?</w:tr>', table_xml, re.S)
    if not rows:
        return None
    ncol = None
    units = []
    toks = []
    for row in rows:
        cells = re.findall(r'<w:tc>(?:(?!</w:tc>).)*?</w:tc>', row, re.S)
        if not cells or any('<w:gridSpan' in c for c in cells):
            return None
        if ncol is None:
            ncol = len(cells)
            units = [0] * ncol
            toks = [0] * ncol
        if len(cells) != ncol:
            return None
        for ci, c in enumerate(cells):
            txt = ''.join(CELL_TXT.findall(c)).strip()
            u = min(sum(2 if ord(ch) > 127 else 1 for ch in txt), 60)
            units[ci] = max(units[ci], u)
            for tok in txt.split():
                t = min(sum(2 if ord(ch) > 127 else 1 for ch in tok), 14)
                toks[ci] = max(toks[ci], t)
    if not ncol or ncol == 1:
        return None

    cap = int(avail * 0.42)
    need = [min(max(540, u * char_tw + pad), cap) for u in units]
    floors = [min(max(540, tk * char_tw + pad), int(avail * 0.34)) for tk in toks]

    if sum(floors) >= avail:                       # 极端情形：只按保底等比压缩
        scale = avail / float(sum(floors))
        widths = [max(360, int(f * scale)) for f in floors]
    else:
        widths = list(floors)
        extra = avail - sum(widths)
        demand = [max(0, need[i] - floors[i]) for i in range(ncol)]
        dsum = float(sum(demand))
        if dsum <= 0:
            widths[units.index(max(units))] += extra
        else:
            widths = [widths[i] + int(extra * demand[i] / dsum) for i in range(ncol)]
            left = avail - sum(widths)
            widths[units.index(max(units))] += left
    widths[units.index(max(units))] += avail - sum(widths)
    return widths


def fix_tables(doc):
    """表格：撑满版心、按内容分配列宽、表头浅蓝底、整行不跨页。"""
    avail = doc_avail_width(doc)

    def one(tm):
        t = tm.group(0)
        widths = table_col_widths(t, avail)
        ncol = len(widths) if widths else 0
        size = 19 if ncol <= 5 else (18 if ncol <= 7 else (17 if ncol <= 9 else 16))  # 9.5/9/8.5/8 pt
        if ncol >= 6:
            widths = table_col_widths(t, avail, char_tw=int(12.2 * size / 2), pad=110)
        if widths:
            wi = {'i': 0}

            def next_w(gm):
                w = widths[wi['i'] % len(widths)]
                wi['i'] += 1
                return '<w:gridCol w:w="%d"/>' % w
            t = re.sub(r'<w:gridCol w:w="\d+"/>', next_w, t)
        t = t.replace('<w:tblW w:w="0" w:type="auto"/>',
                      '<w:tblW w:w="%d" w:type="dxa"/>' % avail)
        t = t.replace('<w:tblLayout w:type="autofit"/>',
                      '<w:tblLayout w:type="fixed"/>')
        if widths:
            ci_box = {'i': 0}

            def fix_row(rowm):
                ci_box['i'] = 0

                def fix_tc(cm):
                    i = ci_box['i']
                    ci_box['i'] += 1
                    cell = cm.group(0)
                    return re.sub(r'<w:tcW w:w="\d+" w:type="(?:dxa|auto)"/>',
                                  '<w:tcW w:w="%d" w:type="dxa"/>' % widths[i % len(widths)],
                                  cell, count=1)
                return re.sub(r'<w:tc>(?:(?!</w:tc>).)*?</w:tc>', fix_tc, rowm.group(0), flags=re.S)
            t = re.sub(r'<w:tr[ >](?:(?!</w:tr>).)*?</w:tr>', fix_row, t, flags=re.S)
        else:
            t = re.sub(r'<w:tcW w:w="\d+" w:type="(?:dxa|auto)"/>',
                       '<w:tcW w:w="0" w:type="auto"/>', t)
        t = re.sub(r'<w:tblCellMar>.*?</w:tblCellMar>',
                   '<w:tblCellMar><w:top w:w="30" w:type="dxa"/>'
                   '<w:left w:w="60" w:type="dxa"/><w:bottom w:w="30" w:type="dxa"/>'
                   '<w:right w:w="60" w:type="dxa"/></w:tblCellMar>', t, flags=re.S)
        # 单元格文字按列数缩到 8.5–9.5pt，段落间距收紧，减少换行
        sz_xml = '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size)

        def small_cell(cm):
            cell = cm.group(0)
            if '<w:sz ' not in cell:
                cell = cell.replace('<w:rPr>', '<w:rPr>' + sz_xml)
            cell = cell.replace('<w:spacing w:before="0" w:after="0"',
                                '<w:spacing w:before="0" w:after="20"')
            return cell
        t = re.sub(r'<w:tc>(?:(?!</w:tc>).)*?</w:tc>', small_cell, t, flags=re.S)
        rows = list(re.finditer(r'<w:tr[ >](?:(?!</w:tr>).)*?</w:tr>', t, re.S))
        out = []
        last = 0
        for ri, rm in enumerate(rows):
            row = rm.group(0)
            if '<w:trPr>' in row:
                row = row.replace('<w:trPr>', '<w:trPr><w:cantSplit/>', 1)
            else:
                row = re.sub(r'(<w:tr[^>]*>)', r'\1<w:trPr><w:cantSplit/></w:trPr>', row, count=1)
            if ri == 0:
                row = re.sub(r'<w:tcPr>',
                             '<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="EFF6FF"/>', row)
            out.append(t[last:rm.start()])
            out.append(row)
            last = rm.end()
        out.append(t[last:])
        return ''.join(out)

    return re.sub(r'<w:tbl>.*?</w:tbl>', one, doc, flags=re.S)


def keep_headings(doc, heading_ids):
    """标题段不落在页面底部（keepNext）；日期页顶不留段前空隙。"""
    def handle(pm):
        p = pm.group(0)
        sm = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        if not (sm and sm.group(1) in heading_ids):
            return p
        if '<w:keepNext' in p:
            return p
        if '<w:pPr>' in p:
            return p.replace('<w:pPr>', '<w:pPr><w:keepNext/>', 1)
        return p
    return re.sub(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>', handle, doc, flags=re.S)


def postprocess_xml(path):
    """保存后对 document.xml 着色：非标题段粗体 run 上着重色；体系元信息行灰斜体。"""
    with zipfile.ZipFile(path) as z:
        styles = z.read('word/styles.xml').decode('utf-8')
        doc = z.read('word/document.xml').decode('utf-8')
        numbering = (z.read('word/numbering.xml').decode('utf-8')
                     if 'word/numbering.xml' in z.namelist() else '')
        others = [(i.filename, z.read(i.filename)) for i in z.infolist()
                  if i.filename != 'word/document.xml']
    heading_ids = set(re.findall(
        r'<w:style [^>]*w:styleId="([^"]+)"[^>]*>(?:(?!</w:style>).)*?<w:name w:val="heading [1-9]"',
        styles, re.S))

    def fix_run_color(run, color, italic=False):
        color_xml = '<w:color w:val="%s"/>' % color
        italic_xml = '<w:i/>' if italic else ''
        if '<w:rPr>' in run:
            if re.search(r'<w:color w:val="[^"]+"/>', run):
                return re.sub(r'<w:color w:val="[^"]+"/>', color_xml, run, count=1)
            return run.replace('<w:rPr>', '<w:rPr>%s%s' % (color_xml, italic_xml), 1)
        return run.replace('<w:r>', '<w:r><w:rPr>%s%s</w:rPr>' % (color_xml, italic_xml), 1)

    def fix_para(pm):
        sm = re.search(r'<w:pStyle w:val="([^"]+)"', pm)
        is_heading = bool(sm and sm.group(1) in heading_ids)
        text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', pm))
        is_meta = text.startswith('体系：')
        if is_heading and not is_meta:
            return pm

        if is_meta:
            return re.sub(r'<w:r>(?:(?!</w:r>).)*?</w:r>',
                          lambda rm: fix_run_color(rm.group(0), C_META, True), pm, flags=re.S)

        def fix_bold_run(rm):
            run = rm.group(0)
            if '<w:b/>' in run or '<w:b ' in run:
                return fix_run_color(run, C_BOLD)
            return run
        return re.sub(r'<w:r>(?:(?!</w:r>).)*?</w:r>', fix_bold_run, pm, flags=re.S)

    doc = re.sub(r'<w:p[ >](?:(?!</w:p>).)*?</w:p>',
                 lambda mm: fix_para(mm.group(0)), doc, flags=re.S)

    # 版式修补：编号字面化 → 表格 → 标题 keepNext
    if numbering:
        doc = literalize_numbering(doc, numid_format(numbering), heading_ids)
    doc = fix_tables(doc)
    doc = keep_headings(doc, heading_ids)

    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        zo.writestr('word/document.xml', doc)
        for name, data in others:
            zo.writestr(name, data)
    os.replace(tmp, path)


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

    apply_styles(file_id)
    call('save_file', file_id=file_id, file_path=OUT)
    postprocess_xml(OUT)
    print('已保存并后处理：', OUT)


if __name__ == '__main__':
    main()
