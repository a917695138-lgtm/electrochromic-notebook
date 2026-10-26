---
type: "experiment"
title: "2026-10-10 Raman 光谱测试（DALE00–50，考察 LiTFSI 解离程度）+ PBI-Cl 染浴（5 mL 体系）"
date: "2026-10-10"
category: "结构与物相表征"
electrolyte: "DALE"
additive: "不涉及"
counter_electrode: "不涉及"
encapsulation: "不涉及"
baseline: "不涉及"
data_types: []
status: "needs_review"
tags: [Raman, LiTFSI, 解离程度, DALE, PBI-Cl, 染浴, 5mL体系]
modified: "2026-10-26"
related:
  - experiments/2026-10-09-tio2-sintering-perforated-fto.md
  - experiments/2026-10-11-post-dye-treatment-and-device-encapsulation.md
  - notes/2026-10-19-naming-convention-and-cross-batch-summary.md
---

# 2026-10-10 Raman 测试与 PBI-Cl 染浴

## 一、Raman 光谱测试

| 项目 | 内容 |
|---|---|
| 样品 | **DALE00 – DALE50** 系列 |
| 目的 | **证明 LiTFSI 解离程度的变化** |

通过 TFSI⁻ 特征振动峰（尤其是 S–N–S 弯曲 / CF₃ 相关模式）随配方的变化，
判断 LiTFSI 在不同 EO : Li 比例下的解离状态，为离子电导与界面行为提供分子层面依据。

DALE 编号口径：**数字 = EO : Li 摩尔比**（DALE50 = 50），见
`notes/2026-10-19-naming-convention-and-cross-batch-summary.md`。

## 二、PBI-Cl 染浴（5 mL 体系）

| 项目 | 理论值 | 实际值 |
|---|---|---|
| DMF 体积 | 5 mL（计划） | **5045 µL** |
| PBI-Cl 质量 | 4.28175 mg（按 1×10⁻³ mol/L 计） | **4.32 mg** |
| 实际浓度 | 1.00×10⁻³ mol/L | **1.00×10⁻³ mol/L** |

实际称样 4.32 mg 略高于理论 4.28175 mg，DMF 同步调整为 5045 µL，
**最终浓度仍为 1.00×10⁻³ mol/L**（4.32 mg / 856.35 g·mol⁻¹ ÷ 5.045 mL = 1.000×10⁻³ mol/L）。

染浴工艺见 `methods/device-fabrication.md`（浸泡 24 h）。

## 结果

Raman 谱图已采集，尚未处理与分析；染浴进行中，10-11 做后处理。

## 待补清单

| # | 待补项 | 说明 |
|---|---|---|
| 1 | Raman 原始数据存放路径 | 未提供，需补记本地路径 |
| 2 | Raman 测试参数 | 激光波长、功率、曝光时间、扫描次数 |
| 3 | 解离程度判读 | TFSI⁻ 特征峰归属与解离比例的计算方法待定 |

## 原始数据

- Raman 谱图：**待补本地路径**（数据只留本地，记录本不上传数据文件）
