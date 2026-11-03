---
type: "experiment"
title: "2026-11-02 10×10 阵列展示器件通电测试（列变色与相邻列传导现象）"
date: "2026-11-02"
category: "器件展示与现象观察"
electrolyte: "DALE"
additive: "EMIMTFSI"
counter_electrode: "2层ATO"
encapsulation: "不涉及"
baseline: "不涉及"
data_types: []
status: "completed"
tags: [10x10阵列, 展示器件, DALE50, 通电变色, 串扰, 列间传导]
modified: "2026-11-03"
related:
  - experiments/2026-10-26-dale50-lamination-10x10-display-device.md
  - experiments/2026-10-15-group-meeting-and-eis-test.md
---

# 2026-11-02 10×10 阵列展示器件通电测试

## 器件

10-26 以 DALE50 贴合组装、60 ℃ 烘箱处理 3 天的 10×10 阵列展示器件
（见 `experiments/2026-10-26-dale50-lamination-10x10-display-device.md`）。
阵列 FTO 设计（C1–C10 触点，3 × 4 cm）：

![10×10 阵列 FTO 像素设计图](assets/10x10-fto-pixel-array.png)

## 现象

在 PBI 侧与 ATO 侧**各夹一个接触点**通电：

1. **PBI 整条线所在列变色** —— ATO 层连续、导电，所夹触点对应的一列整体变色；
2. **一段时间后相邻列开始变色** —— TiO₂–PBI 层连续导致横向传导，变色从目标列扩散到相邻列。

## 关键结论

10×10 阵列器件可按列驱动变色，验证了 DALE50 贴合照展示器件的可行性；
但**列间串扰明显**，与 10-15 组会讨论的 ATO 串扰/行列干扰问题一致，
是阵列无像素间隔离的固有问题。后续像素级独立驱动需结合组会提出的
**电压脉冲方案**或结构隔离（像素隔断）解决。
