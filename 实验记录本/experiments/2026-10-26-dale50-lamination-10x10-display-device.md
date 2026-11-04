---
type: "experiment"
title: "2026-10-26 10×10 展示器件 DALE50 贴合并 60 ℃ 烘箱处理 3 天"
date: "2026-10-26"
system: "DALE体系"
stage: "制备"
data_types: []
status: "completed"
tags: [10x10阵列, 展示器件, DALE50, 贴合组装, 烘箱固化, 器件组装与封装, DALE, EMIMTFSI, 2层ATO]
modified: "2026-11-03"
related:
  - experiments/2026-10-12-cleaning-10x10-array-devices.md
  - experiments/2026-10-14-double-layer-ato-and-10x10-array-ato.md
  - experiments/2026-10-20-post-dye-treatment-16-plus-3.md
  - experiments/2026-11-02-10x10-device-power-on-test.md
  - methods/device-fabrication.md
---

# 2026-10-26 10×10 展示器件 DALE50 贴合并 60 ℃ 烘箱处理 3 天

## 内容

10×10 阵列展示器件（10-12 清洗、10-13 烧制 TiO₂、10-14 制 ATO、10-19 染浴、10-20 后处理）
用 **DALE50** 固态电解质**贴合**组装，随后置入 **60 ℃ 烘箱烘 3 天**。

## 与标准固态组装方案的偏差

固态电解质器件组装方案为：电解质加热至 **120 ℃**
后**刮涂**到变色层，放上 ATO 对电极用透明胶稍微固定，烘箱 2–3 天。本次偏差：

| 项目 | 标准方案 | 本次 |
|------|---------|------|
| 电解质施加方式 | 120 ℃ 加热后刮涂 | **贴合**（DALE50 膜直接贴合） |
| 烘箱温度 | 未限定（2–3 天） | **60 ℃，3 天** |

对电极 2 层 ATO（固态电解质体系默认层数）；固态电解质器件不封装（encapsulation 不涉及）。

## 结果

器件于 10-29 出炉，11-02 通电测试（见 `experiments/2026-11-02-10x10-device-power-on-test.md`）。
