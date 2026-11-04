---
type: "experiment"
title: "2026-10-30 后处理 PBI 片 + 清洗 35 像素 FTO（带漆铁夹掉漆异常）"
date: "2026-10-30"
system: "DALE体系"
stage: "制备"
data_types: []
status: "completed"
tags: [后处理, 35像素FTO, FTO清洗, 掉漆异常, 带漆铁夹, 染料配制与染浴]
modified: "2026-11-03"
related:
  - experiments/2026-10-29-dye-bath-tio2-24pcs.md
  - experiments/2026-10-31-35pixel-fto-tio2-blade-coating.md
  - methods/device-fabrication.md
---

# 2026-10-30 后处理 PBI 片 + 清洗 35 像素 FTO

## 一、后处理 PBI 片

对 10-29 染浴的 24 个 PBI 片做后处理，流程见 `methods/device-fabrication.md`，无改动。

## 二、清洗 35 像素 FTO

清洗 35 像素 FTO（R9 版，左侧双列错位接触区设计，见下图），
清洗流程见 `methods/device-fabrication.md`。

![35 像素 FTO 设计图（R9 左侧双列错位接触区）](assets/35pixel-r9-layout.png)

## 异常

清洗过程中**没有塑料支架**，临时采用**带漆铁夹**夹住 FTO；洗完后发现铁夹**掉漆**。

- 风险：漆片脱落可能污染 FTO 表面及清洗液，影响后续制膜与器件性能。
- 结论：**后续不可采用带漆铁夹夹持的方法**，清洗前必须先备好塑料支架。

## 结果

35 像素 FTO 于 10-31 刮涂 TiO₂ 层（见 `experiments/2026-10-31-35pixel-fto-tio2-blade-coating.md`）。
