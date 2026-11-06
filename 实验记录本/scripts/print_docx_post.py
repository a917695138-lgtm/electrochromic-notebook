# -*- coding: utf-8 -*-
"""打印版 docx 后处理（python-docx 版，元素顺序符合 OOXML schema，Word 可直接打开）。

从 export-print-docx.py 调用，也可单独跑：
    python scripts/print_docx_post.py <docx路径>

做的事：
1. 正文加粗 run → 着重蓝 1D4ED8；体系元信息行 → 灰 6B7280 + 斜体（标题不动）
2. 标题段 keep_with_next（不落页底）
3. 数字编号（任意层级）→ 同层级圆点，去掉 1.2.3. 序号
4. 表格：固定布局撑满版心、按内容分配列宽、表头浅蓝底、整行不跨页、按列数降字号
"""
import re
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Pt, RGBColor

C_BOLD = '1D4ED8'
C_META = '6B7280'
C_HEADER_BG = 'EFF6FF'

TWIP_PER_EMU = 635          # 1 twip = 635 EMU


def emu(twips):
    return Emu(int(twips * TWIP_PER_EMU))


def is_heading(p):
    try:
        name = p.style.name or ''
    except Exception:
        name = ''
    return name.startswith('Heading') or name.startswith('标题')


def apply_styles(doc):
    """标题与正文样式。原先走 editor_sdk 的 doc_update_named_style，会写出 Word 判为损坏的结构。"""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    spec = [('Heading 1', 16, '1E3A8A', WD_ALIGN_PARAGRAPH.CENTER),
            ('Heading 2', 14, '115E59', None),
            ('Heading 3', 12, '9A3412', None),
            ('Heading 4', 11, '374151', None)]
    for name, size, color, align in spec:
        try:
            st = doc.styles[name]
        except KeyError:
            continue
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(color)
        st.font.name = '黑体'
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '黑体')
        if align is not None:
            st.paragraph_format.alignment = align

    # 正文默认：模板没有 Normal 样式，改 docDefaults（正文段落的样式 id 是自动命名的空壳）
    styles_el = doc.styles.element
    dd = styles_el.find(qn('w:docDefaults'))
    if dd is None:
        dd = OxmlElement('w:docDefaults')
        styles_el.insert(0, dd)

    rpr_def = dd.find(qn('w:rPrDefault'))
    if rpr_def is None:
        rpr_def = OxmlElement('w:rPrDefault')
        dd.insert(0, rpr_def)
    rpr = rpr_def.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        rpr_def.append(rpr)
    rfonts = rpr.get_or_add_rFonts()
    for attr in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rfonts.set(qn(attr), '宋体')
    rpr.get_or_add_sz().set(qn('w:val'), '21')

    ppr_def = dd.find(qn('w:pPrDefault'))
    if ppr_def is None:
        ppr_def = OxmlElement('w:pPrDefault')
        dd.append(ppr_def)
    ppr = ppr_def.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        ppr_def.append(ppr)
    spacing = ppr.get_or_add_spacing()
    spacing.set(qn('w:line'), '336')       # 1.4 倍行距
    spacing.set(qn('w:lineRule'), 'auto')
    spacing.set(qn('w:after'), '60')


def numbering_maps(numbering_el):
    """numId -> {ilvl: numFmt}，以及每个 ilvl 的 bullet numId。"""
    if numbering_el is None:
        return {}, {}
    aid_lvls = {}
    for ab in numbering_el.findall(qn('w:abstractNum')):
        lvls = {}
        for lvl in ab.findall(qn('w:lvl')):
            ilvl = int(lvl.get(qn('w:ilvl')) or 0)
            fmt = lvl.find(qn('w:numFmt'))
            lvls[ilvl] = fmt.get(qn('w:val')) if fmt is not None else 'bullet'
        aid_lvls[ab.get(qn('w:abstractNumId'))] = lvls
    num_map = {}
    for num in numbering_el.findall(qn('w:num')):
        aid = num.find(qn('w:abstractNumId'))
        num_map[num.get(qn('w:numId'))] = aid_lvls.get(aid.get(qn('w:val')), {})
    bullets = {}
    for num_id, lvls in num_map.items():
        for ilvl, fmt in lvls.items():
            if fmt == 'bullet' and ilvl not in bullets:
                bullets[ilvl] = num_id
    return num_map, bullets


def strip_heading_direct(p):
    """清掉标题 run 上的直接格式，让标题样式（字号/颜色）生效。"""
    for r in p.runs:
        r.font.size = None
        r.font.bold = None
        r.font.color.rgb = None


def color_runs(p):
    text = p.text.strip()
    if text.startswith('体系：'):
        for r in p.runs:
            r.font.color.rgb = RGBColor.from_string(C_META)
            r.font.italic = True
        return
    for r in p.runs:
        if r.bold:
            r.font.color.rgb = RGBColor.from_string(C_BOLD)


def convert_numbers(doc):
    """列表统一成“一级圆点”：模板的编号定义只有 ilvl 0，嵌套层级无从生效。

    decimal 编号一律改圆点，ilvl 归 0，避免出现没有标记的孤立缩进行。
    """
    num_map, bullets = numbering_maps(doc.part.numbering_part.element
                                      if doc.part.numbering_part else None)
    target = bullets.get(0)
    if target is None:
        return 0
    changed = 0
    for p in doc.paragraphs:
        pPr = p._p.pPr
        if pPr is None or pPr.numPr is None:
            continue
        numPr = pPr.numPr
        ilvl_el = numPr.find(qn('w:ilvl'))
        numid_el = numPr.find(qn('w:numId'))
        cur_id = numid_el.get(qn('w:val')) if numid_el is not None else ''
        cur_lvl = int(ilvl_el.get(qn('w:val'))) if ilvl_el is not None else 0
        if cur_id == target and cur_lvl == 0:
            continue
        if numid_el is None:
            numid_el = OxmlElement('w:numId')
            numPr.append(numid_el)
        numid_el.set(qn('w:val'), target)
        if ilvl_el is not None:
            ilvl_el.set(qn('w:val'), '0')
        changed += 1
    return changed


CELL_TXT = re.compile(r'<w:t[^>]*>([^<]*)</w:t>')


def col_widths(table, avail):
    rows = table.rows
    if not rows:
        return None
    ncol = len(rows[0].cells)
    if ncol < 2:
        return None
    units = [0] * ncol
    toks = [0] * ncol
    for row in rows:
        cells = row.cells
        if len(cells) != ncol:
            return None
        for ci, cell in enumerate(cells):
            txt = cell.text.strip()
            u = min(sum(2 if ord(ch) > 127 else 1 for ch in txt), 60)
            units[ci] = max(units[ci], u)
            for tok in txt.split():
                toks[ci] = max(toks[ci], min(sum(2 if ord(ch) > 127 else 1 for ch in tok), 14))

    size = 19 if ncol <= 5 else (18 if ncol <= 7 else (17 if ncol <= 9 else 16))
    char_tw = int(12.2 * size / 2)
    pad = 130 if ncol <= 5 else 110
    cap = int(avail * 0.42)
    need = [min(max(540, u * char_tw + pad), cap) for u in units]
    floors = [min(max(540, t * char_tw + pad), int(avail * 0.34)) for t in toks]

    if sum(floors) >= avail:
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
            widths[units.index(max(units))] += avail - sum(widths)
    widths[units.index(max(units))] += avail - sum(widths)
    return widths, size


def set_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.insert_element_before(shd, 'w:noWrap', 'w:tcMar', 'w:textDirection',
                               'w:tcFitText', 'w:vAlign', 'w:hideMark')


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn('w:cantSplit')) is not None:
        return
    trPr.insert_element_before(OxmlElement('w:cantSplit'), 'w:trHeight', 'w:tblHeader',
                               'w:tblCellSpacing', 'w:jc', 'w:hidden')


def fix_tables(doc, avail):
    for table in doc.tables:
        got = col_widths(table, avail)
        if not got:
            continue
        widths, size = got
        try:
            table.autofit = False
        except Exception:
            pass
        for ci, w in enumerate(widths):
            try:
                table.columns[ci].width = emu(w)
            except Exception:
                pass
        for ri, row in enumerate(table.rows):
            no_split(row)
            for ci, cell in enumerate(row.cells):
                try:
                    cell.width = emu(widths[ci])
                except Exception:
                    pass
                if ri == 0:
                    set_shading(cell, C_HEADER_BG)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(size / 2.0)


def page_text_width(doc):
    sec = doc.sections[0]

    def tw(v, default):
        return int(v.twips) if v is not None else default

    w = tw(sec.page_width, 11906)
    l = tw(sec.left_margin, 1800)
    r = tw(sec.right_margin, 1800)
    return max(4000, w - l - r)


def main():
    path = sys.argv[1]
    doc = Document(path)
    apply_styles(doc)
    avail = page_text_width(doc)
    n_num = convert_numbers(doc)
    for p in doc.paragraphs:
        if is_heading(p):
            p.paragraph_format.keep_with_next = True
            strip_heading_direct(p)
        else:
            color_runs(p)
    fix_tables(doc, avail)
    doc.save(path)
    print('后处理完成：%s（编号改写 %d 段）' % (path, n_num))


if __name__ == '__main__':
    main()
