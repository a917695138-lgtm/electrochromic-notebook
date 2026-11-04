# -*- coding: utf-8 -*-
"""清理实验记录正文中的提示词内容（2026-11-04 用户口径）。

删除目标：
1. 「## 原始数据」下仅含「本条为XX步骤，无结构化数据文件。」或「待补本地路径」占位的整节
2. 待补清单中无意义行：染浴时长与温度 / 片子数量与编号类 / 打孔与否类 /
   原始数据路径类 / 「沿用前期工艺」类；清空后整节删除
3. 口径作废说明、命名口径引用块、「数据只留本地」提示行、「本记录仅含XX数据」提示行等
4. 正文中「见 notes/xxx.md」路径引用（保留口径事实本身）

用法：python cleanup-prompt-blocks.py [--apply]（默认预演）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = '--apply' in sys.argv


def read_file(p):
    with open(p, 'rb') as f:
        b = f.read()
    bom = b.startswith(b'\xef\xbb\xbf')
    s = b.decode('utf-8-sig')
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    return s, bom, crlf


def write_file(p, s, bom, crlf):
    if crlf:
        s = s.replace('\n', '\r\n')
    data = s.encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    with open(p, 'wb') as f:
        f.write(data)


# ---------- 单行/多行精确删除块（全文通用或按文件指定） ----------
# (文件名片段或 None=任意, 待删除的多行精确文本)
EXACT_BLOCKS = [
    # 口径更正块（07-09）
    ('2026-07-09-dale50', '> **口径更正（2026-10-24 确认）**：DALE50 的 50 指 **EO : Li 摩尔比 = 50**；原标题中的\n> "50% 离子液体"是旧口径，已作废。**DALE00 = 未添加 EMIMTFSI 的 DA 体系对照**，不是"无 DA"对照。\n> 详见 `notes/2026-10-19-naming-convention-and-cross-batch-summary.md`。\n\n'),
    # 命名口径块（09-08）
    ('2026-09-08-electrolyte', '> 命名口径：**1FTO / 0FTO** 指光谱是否用 1 片 FTO 校正基线；**1ATO / 2ATO** 指对电极 ATO 层数，\n> 两者是不同变量，不可混淆。\n\n'),
    # 09-22 两行提示
    ('2026-09-22-dale-progress', '> 讨论材料只保留在本地，记录本与 GitHub 上**仅登记存放路径**，不上传文件本身。\n> 讨论结论待整理后补记，本条先固定资料位置。\n\n'),
    # 10-13 合并记录说明行
    ('2026-10-13-new-pbi', '> 同一天的三项工作合并记录：新 PBI-Cl 批次响应时间测试、XRD 物相测试、10×10 阵列展示器件 TiO₂ 烧制。\n\n'),
    # notes 口径作废说明块
    ('2026-10-19-naming', '> **口径作废说明**：2026-10-23 及更早的记录把数字解释为"EMIMTFSI 离子液体含量百分比"\n> （DALE50 = 50% IL）。该解释**已作废**，按 EO : Li 摩尔比理解。\n> EMIMTFSI 的用量仍按"锂盐 : EMIMTFSI = 1 : 2"的摩尔比单独给出，不由编号数字决定。\n'),
    ('2026-10-19-naming', '> **注意**：DALE00 是"不添加离子液体"的对照，编号 00 不代表 EO : Li = 0。\n'),
    # plans 归档说明
    ('2026-06-27-non-electrolyte', '> 说明：本文件保留 2026-06-27 版本中较完整的文献依据和变量分析，用作参考归档。2026-06-29 起，后续执行以 `2026-06-29-da-gel-device-performance-optimization-plan.md` 为主方案。\n\n'),
]

# 单行正则删除（任意 experiments 文件）
LINE_PATTERNS = [
    r'> 备注：原始染料名称笔误已统一更正为 PBI-Cl。\n',
    r'> 本记录仅含响应时间与光学对比度数据，[^>\n]*未录入。\n',
    r'> 数据只保留在本地，记录本与 GitHub 上仅登记存放路径，不上传数据文件。\n',
    r'> 原始数据只保留在本地，记录本与 GitHub 上仅记录存放路径，不上传任何谱图数据文件。\n',
]

# 见 notes 路径引用改写（保留事实、去路径）
REF_REWRITES = [
    ('2026-09-22-dale-progress', 'DALE 编号口径见 `notes/2026-10-19-naming-convention-and-cross-batch-summary.md`：', 'DALE 编号口径：'),
    ('2026-07-21-dale-tensile', '，见\n`notes/2026-10-19-naming-convention-and-cross-batch-summary.md`。', '。'),
    ('2026-10-10-raman', '，见\n`notes/2026-10-19-naming-convention-and-cross-batch-summary.md`。', '。'),
]

# ---------- 节级删除：原始数据占位节 ----------
SECTION_PATTERNS = [
    # 仅含占位句的整节
    re.compile(r'\n## 原始数据\n\n本条为[^\n]*无结构化数据文件。\n(?=\n|$)'),
    # 仅含待补路径占位的整节
    re.compile(r'\n## 原始数据\n\n- (?:SEM 图片：\*\*待补充\*\*（路径未提供）|SEM 图像：\*\*待补本地路径\*\*[^\n]*|EIS 数据：\*\*待补本地路径\*\*[^\n]*)\n(?=\n|$)'),
]

BULLET_LINE_PATTERNS = [
    re.compile(r'- 无结构化数据（制样步骤）；制样本身不产生数据文件，谱图数据见 2026-10-22 测试记录。\n'),
]

# ---------- 10-23 命名口径节整体删除 ----------
NAMING_SECTION = re.compile(
    r'\n### 命名口径（2026-10-24 更正，以此为准）\n\n(?:[^\n]*\n)+?(?=\n)')

# ---------- 待补清单行过滤 ----------
DELETE_EXACT_ITEMS = {
    '片子数量', '片子编号', '片子数量与编号', 'TiO₂ 片子数量与编号',
    '双层 ATO 片数', '常规双层 ATO 的片数', '后处理片子数量', '清洗片数',
    '封装数量', '编号 43/54/60/63 的具体含义',
    '打孔与否', '打孔与否、片子编号', '基底类型',
    'EIS 原始数据路径', '原始数据存放路径', 'SEM 原始图片', 'SEM 原始图像路径',
    'Raman 原始数据存放路径', '位置 3 的 40.png', '位置 4 采集点',
    '烧结温度与保温时间', '浆料配比与旋涂参数',
}
# 待补项含这些子串即删
DELETE_SUBSTR = ['染浴时长', '染浴温度']
# 行内改写：待补项 -> 新待补项
ROW_REWRITE = {'成膜方式、打孔与否': ('成膜方式', '刮涂还是旋涂未记录')}


def fix_pending_list(s):
    """过滤待补清单表格行，行重编号，空表删整节。返回 (新文本, 变更说明列表)"""
    notes = []
    m = re.search(r'\n## 待补清单\n\n(\| # \| 待补项 \| 说明 \|\n\|[-|]+\n)((?:\|[^\n]*\n)+)', s)
    if not m:
        return s, notes
    header, rows = m.group(1), m.group(2)
    row_list = [r for r in rows.split('\n') if r]
    kept = []
    for r in row_list:
        cells = [c.strip() for c in r.strip('|').split('|')]
        if len(cells) < 2:
            kept.append(r)
            continue
        item = cells[1]
        if item in ROW_REWRITE:
            new_item, new_desc = ROW_REWRITE[item]
            kept.append('| ? | %s | %s |' % (new_item, new_desc))
            notes.append('改写行: %s -> %s' % (item, new_item))
            continue
        if item in DELETE_EXACT_ITEMS or any(sub in item for sub in DELETE_SUBSTR):
            notes.append('删除行: %s' % item)
            continue
        kept.append(r)
    if not kept:
        # 整节删除
        s = s[:m.start()] + '\n' + s[m.end():]
        notes.append('待补清单清空，整节删除')
    else:
        renum = []
        for i, r in enumerate(kept, 1):
            r2 = re.sub(r'^\| \d+ \|', '| %d |' % i, r)
            renum.append(r2)
        new_block = header + '\n'.join(renum) + '\n'
        s = s[:m.start()] + '\n## 待补清单\n\n' + new_block + s[m.end():]
    return s, notes


def process(p):
    s, bom, crlf = read_file(p)
    orig = s
    fname = os.path.basename(p)
    log = []
    for key, block in EXACT_BLOCKS:
        if key in fname and block in s:
            s = s.replace(block, '')
            log.append('删块: %s...' % block[:18])
    # 07-09 周期段句改写（删提示语保数据句）
    if '2026-07-09-dale50' in fname:
        s = re.sub(
            r'> 注：双面胶围腔体结构 2026-10 起已停用[^\n]*本条为 2026-07 的历史工艺，保留原样。本次长循环数据来自 ([^\n]*)',
            r'本次长循环数据来自 \1', s)
    for pat in LINE_PATTERNS:
        s2 = re.sub(pat, '', s)
        if s2 != s:
            log.append('删行: %s' % pat[:30])
            s = s2
    for key, old, new in REF_REWRITES:
        if key in fname and old in s:
            s = s.replace(old, new)
            log.append('去引用: %s' % key)
    for pat in SECTION_PATTERNS:
        s2 = pat.sub('\n', s)
        if s2 != s:
            log.append('删占位节: 原始数据')
            s = s2
    for pat in BULLET_LINE_PATTERNS:
        s2 = pat.sub('', s)
        if s2 != s:
            log.append('删占位行')
            s = s2
    if '2026-10-23-sem' in fname:
        s2 = NAMING_SECTION.sub('\n', s)
        if s2 != s:
            log.append('删节: 命名口径')
            s = s2
    s, notes = fix_pending_list(s)
    log.extend(notes)
    s = re.sub(r'\n{3,}', '\n\n', s)
    if s != orig:
        if APPLY:
            write_file(p, s, bom, crlf)
        print('%s: %d 处' % (fname, len(log)))
        for n in log:
            print('   - %s' % n)
    return s != orig


def main():
    total = 0
    for sub in ('experiments', 'notes', 'plans', 'methods'):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.md'):
                continue
            if process(os.path.join(d, fn)):
                total += 1
    print('---')
    print('%s：共修改 %d 个文件' % ('已写盘' if APPLY else '预演（未写盘，加 --apply 执行）', total))


if __name__ == '__main__':
    main()
