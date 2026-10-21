---
type: "experiment"
title: "[含光谱电化学数据] 2026-09-08 四款电解液及加EMIM版本响应时间筛选（1FTO 基线校正）"
date: "2026-09-08"
category: "响应时间测试"
electrolyte: "多体系对比"
additive: "EMIMTFSI"
counter_electrode: "单层+双层对比"
encapsulation: "未标注"
data_types: [response_time]
status: "completed"
tags: [电解液筛选, 响应时间, 1FTO, 基线校正, 1ATO, 2ATO, PBI-Cl]
project: "电致变色"
modified: "2026-10-19"
related:
  - experiments/2026-09-08-electrolyte-screening-air-baseline-response-time.md
  - experiments/2026-09-14-spacer-120um-surlyn-vs-100um-tape-response-time.md
---

# [含光谱电化学数据] 2026-09-08 四款电解液及加EMIM版本响应时间筛选（1FTO 基线校正）

## 测试体系与数据来源

与空气基线组同一天、同一批电极体系，光谱测试改为**用 1 片 FTO 玻璃做参比扣除（1FTO 基线）**，用于判断基线处理方式对数据的影响幅度。其中 LITFSI-ACN 与 LITFSI-ACN-EMIMTFSI 两组改用**1 层 ATO（1ATO）对电极**，其余组仍为 2ATO(NEW)。

原始数据位于 `D:\Desktop\光谱电化学\ASL\20260908 1FTO校正后四款电解液及加EMIM的响应时间测试\20260908 1FTO校正`。汇总表为该文件夹下的 `20260908 1FTO校正后四款电解液及加EMIM的响应时间测试响应时间汇总.xlsx`（13 条记录，6 个体系分组）。

## 器件与测试条件

| 项目 | 内容 |
|------|------|
| 器件结构 | FTO / 介孔 TiO₂–PBI-Cl / 电解质 / ATO / FTO |
| 工作电极 | 介孔 TiO₂–PBI-Cl（旧批次） |
| 对电极 | 2ATO(NEW)（KLDTF33-EMIMTFSI、LiClO4、S50、S50-EMIMTFSI）；1ATO（LITFSI-ACN、LITFSI-ACN-EMIMTFSI） |
| 电解质浓度 | 锂盐统一 1 mol/L；含 EMIMTFSI 版本摩尔比 锂盐:EMIMTFSI = 1:2 |
| 基线校正 | 1FTO（用 1 片 FTO 玻璃做参比扣除） |
| 电位程序 | −1.8→0 V、−2→−1 V |
| 步时 | 3 s |

命名口径：**1FTO / 0FTO** 指光谱是否用 1 片 FTO 校正基线；**1ATO / 2ATO** 指对电极 ATO 层数，两者是不同变量。

## 结果

| 样品 / 条件 | 波长 (nm) | 循环 | 着色 t90 (s) | 褪色 t90 (s) | 着色 ΔT (%) | 褪色 ΔT (%) |
|---|---|---|---|---|---|---|
| KLDTF33-EMIMTFSI 1FTO −1.8-0（3S）-2 | 658.0 | 3 | 1.73 | 1.94 | 54.9 | 54.7 |
| KLDTF33-EMIMTFSI 1FTO −2-1（3S） | 647.4 | 4 | 1.50 | 0.86 | 63.2 | 63.2 |
| LITFSI-ACN 1ATO −1.8-0（3S） | 639.0 | 4 | 0.65 | 0.76 | 58.2 | 58.2 |
| LITFSI-ACN 1ATO −2-1（3S）-2 | 605.5 | 4 | 0.73 | 0.31 | 59.9 | 59.9 |
| LITFSI-ACN-EMIMTFSI 1ATO −1.8-0（3S） | 653.4 | 6 | 1.90 | 1.31 | 60.3 | 60.1 |
| LITFSI-ACN-EMIMTFSI 1ATO −2-1（3S） | 648.1 | 3 | 1.73 | 0.54 | 64.2 | 64.0 |
| LiClO4 1FTO −1.8-0（3S） | 643.6 | 4 | 0.86 | 0.99 | 62.4 | 62.4 |
| LiClO4 1FTO −2-1（3S） | 642.0 | 3 | 0.52 | 0.47 | 63.9 | 63.9 |
| S50 1FTO −1.8-0（3S） | 643.6 | 3 | 1.71 | 1.19 | 59.5 | 59.5 |
| S50 1FTO −2-1（3S）-2 | 642.8 | 4 | 0.73 | 1.29 | 68.1 | 68.1 |
| S50 1FTO −2-1（3S） | 642.8 | 3 | 1.13 | 1.51 | 64.1 | 64.8 |
| S50-EMIMTFSI-1FTO −1.8-0（3S） ⚠ | 642.8 | 3 | 0.61 | 2.16 | 33.8 | 32.7 |
| S50-EMIMTFSI-1FTO −2-1（3S） ⚠ | 642.8 | 3 | 0.44 | 1.98 | 41.8 | 38.7 |

## 关键结论

- **对比度整体抬升**：同体系在 1FTO 基线下 ΔT 普遍由 45–57% 抬到 55–68%。LiClO4 −2-1 由 55.7% → 63.9%，S50 −2-1 由 57.8% → 64–68%。**跨批次比较必须固定基线方式**，否则 ΔT 不可比。
- **注意变量混杂**：LITFSI-ACN 与 LITFSI-ACN-EMIMTFSI 两组同时改用了 1ATO 对电极，与空气基线组之间的差异包含"基线 + 对电极层数"两个变量，不能单独归因于基线。
- **本组响应最快**：LiClO4 1FTO −2-1（3S），0.52 s / 0.47 s，ΔT 63.9%。
- **对比度最高**：S50 1FTO −2-1（3S）-2，ΔT 68.1%，但褪色 1.29 s 偏慢。

## 异常

- `S50-EMIMTFSI-1FTO` 两条 ΔT 仅 33.8% 与 41.8%，褪色 2.16 / 1.98 s，显著劣于同组其他体系；与空气基线组的低 ΔT 方向一致，**S50 + EMIMTFSI 的稳定性问题在两组数据中重复出现**。
- `LITFSI-ACN 1ATO −2-1（3S）-2` 波长 605.5 nm，低于同体系另一条 639.0 nm，波长漂移较大。

## 下一步

- 后续实验统一记录基线方式（0FTO / 1FTO）与对电极层数（1ATO / 2ATO），避免变量混杂。
- S50 系列单独做封装与浸润检查。
- 主攻体系取舍须在同一种基线方式下重测。

> 本记录仅含响应时间与光学对比度数据，长循环数据未录入。
