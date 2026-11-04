# -*- coding: utf-8 -*-
"""
按用户确认的打孔判定规则，重判 experiments/ 下 system="通用" 的实验记录：
  明确打孔            -> 液态电解质
  明确不打孔/完全没提   -> DALE体系
  两种基底都做/未记录    -> 保持 通用（待用户确认）
已归 液态/DALE/PAPB 的记录与文档类不动。

用法:
    python reassign-system-by-perforation.py          # 预演
    python reassign-system-by-perforation.py --apply  # 写盘
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "experiments")

# 明确打孔（正文明确"在打孔FTO上"/"打孔器件"）-> 液态电解质
LIQUID = [
    "2026-06-06-re-test.md",
    "2026-09-04-perforated-fto-tio2-prep.md",
    "2026-09-06-dye-bath-5ml.md",
    "2026-09-09-tio2-layer-on-perforated-fto.md",
    "2026-09-11-pbi-cl-dye-bath-10ml.md",
    "2026-10-09-tio2-sintering-perforated-fto.md",
]
# 明确不打孔（"本次为不打孔FTO"）或完全未提打孔 -> DALE体系
DALE = [
    "2026-09-23-fto-cleaning-and-tio2-prep.md",
    "2026-09-24-double-layer-ato-and-pi-cavity.md",
    "2026-09-26-tio2-sintering.md",
    "2026-09-27-dye-bath-tio2-and-pi-fto.md",
    "2026-09-28-post-dye-treatment-and-pi-cavity-issue.md",
    "2026-06-15-ato-layer-prep.md",
    "2026-07-02-pure-pbi-ato-fto-transmittance.md",
    "2026-07-06-spincoat-thickness-pbi-cl.md",
    "2026-07-19-dye-bath-10ml.md",
    "2026-07-20-post-dye-treatment-and-double-ato.md",
    "2026-07-23-dye-bath-10ml.md",
    "2026-09-01-dye-bath-10ml.md",
    "2026-10-12-cleaning-10x10-array-devices.md",
    "2026-10-14-double-layer-ato-and-10x10-array-ato.md",
    "2026-10-19-dye-bath-16-plus-3.md",
    "2026-10-20-post-dye-treatment-16-plus-3.md",
    "2026-10-29-dye-bath-tio2-24pcs.md",
    "2026-10-30-post-dye-treatment-and-35pixel-fto-cleaning.md",
    "2026-10-31-35pixel-fto-tio2-blade-coating.md",
]
# 两种基底都做 / "打孔与否未记录" / 组会内容缺失 -> 保持通用
KEEP_GENERAL = [
    "2026-06-01-tio2-prep.md",
    "2026-06-02-post-dye.md",
    "2026-06-09-tio2-film-prep.md",
    "2026-07-01-pbi-cl-thickness-meeting.md",
    "2026-07-11-tio2-spin-coating-film.md",
    "2026-07-13-pbi-cl-dye-soak-thickness.md",
    "2026-07-17-tio2-sintering.md",
    "2026-07-22-tio2-prep-16pcs.md",
    "2026-08-31-tio2-prep.md",
    "2026-10-16-tio2-sintering-16pcs.md",
    "2026-07-15-group-meeting.md",
]

PLAN = {}
for n in LIQUID:
    PLAN[n] = "液态电解质"
for n in DALE:
    PLAN[n] = "DALE体系"

SYSTEM_RE = re.compile(r'^system:\s*".*?"\s*$', re.M)


def main():
    apply = "--apply" in sys.argv
    changed = 0
    for n, target in sorted(PLAN.items()):
        p = os.path.join(EXP, n)
        raw = io.open(p, encoding="utf-8-sig", newline="").read()
        m = SYSTEM_RE.search(raw)
        cur = m.group(0) if m else "(none)"
        curval = re.search(r'"(.*?)"', m.group(0)).group(1) if m else "?"
        status = "OK" if curval == "通用" else "!! 当前=" + curval
        print("%-56s 通用 -> %-10s %s" % (n, target, status))
        if curval != "通用":
            continue
        if apply:
            new = SYSTEM_RE.sub('system: "%s"' % target, raw, count=1)
            io.open(p, "w", encoding="utf-8", newline="").write(new)
            changed += 1
    print("\n模式: %s  计划改动: %d 条  保持通用: %d 条"
          % ("APPLY" if apply else "DRY-RUN",
             changed if apply else len(PLAN), len(KEEP_GENERAL)))
    print("保持通用清单:")
    for n in KEEP_GENERAL:
        print("  ", n)


if __name__ == "__main__":
    main()
