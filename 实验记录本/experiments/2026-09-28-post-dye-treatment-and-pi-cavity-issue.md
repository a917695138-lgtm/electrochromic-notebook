---
type: "experiment"
title: "2026-09-28 染浴后处理 + PI 膜腔体失效（无法吸附 PBI-Cl 且 PI 膜溶胀）"
date: "2026-09-28"
category: "染料配制与染浴"
electrolyte: "不涉及"
additive: "不涉及"
counter_electrode: "不涉及"
encapsulation: "不涉及"
baseline: "不涉及"
data_types: []
status: "completed"
tags: [后处理, DCM冲洗, PBI-Cl, PI膜, 腔体失效, 溶胀]
modified: "2026-10-26"
related:
  - experiments/2026-09-24-double-layer-ato-and-pi-cavity.md
  - experiments/2026-09-27-dye-bath-tio2-and-pi-fto.md
  - experiments/2026-06-02-post-dye.md
---

# 2026-09-28 染浴后处理与 PI 膜腔体失效

## 一、染浴后处理

对 2026-09-27 染浴后的片子做标准后处理，**工艺同之前**：

- DCM（二氯甲烷）充分冲洗，去除未共价锚定的游离 PBI-Cl
- 加热干燥

后处理的具体参数见 `methods/device-fabrication.md`。

## 二、发现的问题：PI 膜腔体方案失效

在 FTO 上用 **PI 膜围出的腔体无法吸附 PBI-Cl 分子，且 PI 膜发生溶胀**。

| 现象 | 说明 |
|---|---|
| 无法吸附 PBI-Cl | 围腔区域未见分子锚定，推测染液未能有效接触 TiO₂ 表面 |
| PI 膜溶胀 | PI 膜在 DMF 染液中发生溶胀，腔体几何形状与密封性被破坏 |

两个现象互相印证：PI 膜在染浴溶剂中溶胀导致腔体失效，进而使 PBI-Cl 无法在围腔内正常吸附。

## 结论与下一步建议

1. **PI 膜不适合作为本体系染浴/注液腔体材料**：在 DMF 中溶胀，且阻碍分子吸附。
   后续腔体材料需避开 PI 膜，或改用不接触染浴溶剂的结构方案。
2. **编号 43 / 54 / 60 / 63 的四个 PI 膜 FTO 判为无效样品**，不计入有效数据。
3. 若仍需限定染浴区域，可考虑改用耐 DMF 的隔层材料，或改为整片染浴后再做区域定义。

## 原始数据

本条为后处理步骤与现象记录，无结构化数据文件。
