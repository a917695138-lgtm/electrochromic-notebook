---
type: "experiment"
title: "[含光谱电化学数据] 2026-09-18 LiClO4-ACN-EMIM 三元电解液不同电位程序响应时间"
date: "2026-09-18"
category: "响应时间测试"
electrolyte: "LiClO4-ACN"
additive: "EMIMTFSI"
counter_electrode: "未标注"
encapsulation: "沙林膜120μm"
baseline: "空气基线"
data_types: [response_time]
status: "completed"
metrics: {"contrast": "59.0%", "coloring": "0.59 s", "bleaching": "0.42 s", "wavelength": "635.2 nm", "basis": "本批最优 LICLO4-ACN-EMIM −2-1（3S）after cv"}
tags: [LiClO4, EMIMTFSI, 三元电解液, 响应时间, CV预处理, 0FTO, 沙林膜]
modified: "2026-10-19"
related:
  - experiments/2026-09-14-spacer-120um-surlyn-vs-100um-tape-response-time.md
  - experiments/2026-09-19-liclo4-acn-step-time-and-fade-voltage-response-time.md
---

# [含光谱电化学数据] 2026-09-18 LiClO4-ACN-EMIM 三元电解液不同电位程序响应时间

## 测试体系与数据来源

在 120 μm 沙林膜 + 0FTO 条件下系统测试 LiClO4-ACN-EMIM（EMIMTFSI 离子液体）三元电解液在 −1.8→0 V、−2→0 V、−2→−1 V 三种电位程序下的响应时间与对比度，并考察 CV 预处理的影响。

原始数据位于 `D:\Desktop\光谱电化学\ASL\20260918 LiCLO4 ACN EMIM\202620918 LiCLO4 ACN EMIM`。汇总表为 `20260918 LiCLO4 ACN EMIM响应时间汇总.xlsx`（7 条记录，1 个体系分组）。

## 器件与测试条件

| 项目 | 内容 |
|------|------|
| 器件结构 | FTO / 介孔 TiO₂–PBI-Cl / 电解质 / ATO / FTO |
| 电解质 | LiClO4 / ACN / EMIMTFSI；LiClO4 1 mol/L（1×10⁻³ mol/mL），LiClO4:EMIMTFSI = 1:2（摩尔比） |
| 隔层 | 120 μm 沙林膜 |
| 电位程序 | −1.8→0 V、−2→0 V、−2→−1 V |
| 步时 | 3 s |
| 预处理 | 部分样品先跑 CV（−2.5~1 V，20 mV/s）再测响应时间 |
| 基线 | 0FTO（空气基线） |

## 结果

| 样品 / 条件 | 波长 (nm) | 循环 | 着色 t90 (s) | 褪色 t90 (s) | 着色 ΔT (%) | 褪色 ΔT (%) |
|---|---|---|---|---|---|---|
| LICLO4-ACN-EMIM −1.8-0（3S） | 639.8 | 5 | 0.92 | 0.68 | 57.6 | 57.6 |
| LICLO4-ACN-EMIM −1.8-0（3S）-3 | 639.8 | 4 | 0.96 | 0.61 | 57.4 | 57.4 |
| LICLO4-ACN-EMIM −1.8-0（3S）after cv | 635.2 | 2 | 0.88 | 0.67 | 58.5 | 58.2 |
| LICLO4-ACN-EMIM −1.8-0（3S）after cv -2 | 639.0 | 3 | 0.90 | 0.68 | 57.8 | 57.8 |
| LICLO4-ACN-EMIM −2-0（3S）after cv | 632.9 | 5 | 0.76 | 0.63 | 58.1 | 58.0 |
| LICLO4-ACN-EMIM −2-1（3S） | 638.2 | 4 | 0.75 | 0.50 | 58.8 | 58.5 |
| LICLO4-ACN-EMIM −2-1（3S）after cv | 635.2 | 4 | 0.59 | 0.42 | 59.0 | 59.0 |

## 关键结论

- **本批次最优**：−2-1（3S）after cv，着色 0.59 s / 褪色 0.42 s，ΔT 59.0%。这是 9 月批次中着色与褪色两端最均衡的一组。
- **电位越负、褪色电位越高，两端越快**：−1.8-0（0.92/0.68 s）→ −2-0（0.76/0.63 s）→ −2-1（0.59/0.42 s），符合电位驱动预期。
- **CV 预处理影响很小**：−1.8-0 未处理 0.92/0.68 s 与 after cv 0.88/0.67 s 差异在循环波动内；−2-1 略有改善（0.75/0.50 → 0.59/0.42 s）。**该体系不需要依赖 CV 活化即可达到秒级以下响应**。
- **对比度最稳定**：7 条 ΔT 全部落在 57.4–59.0%，离散仅 1.6 个百分点，是 9 月批次中重复性最好的体系。
- 与 0914 的 LITFSI-ACN-EMIM（120 μm 沙林膜，0.31/1.34 s，ΔT 59.5%）相比，本体系着色略慢（0.59 vs 0.31 s）但**褪色快得多**（0.42 vs 1.34 s），两端更平衡。

## 异常

无判定为异常的数据。

## 下一步

- 以 LiClO4-ACN-EMIM 为基准体系，推进长循环稳定性测试（同目录 long cycle 数据尚未处理）。
- 固定 120 μm 沙林膜 + 0FTO 组合，与后续 DALE 固态体系做同条件对照。

> 本记录仅含响应时间与光学对比度数据，长循环数据未录入。
