---
type: "experiment"
title: "2026-10-15 组会讨论（ATO 串扰 / DALE 烷基链）+ EIS 测试（DALE00-50 等）"
date: "2026-10-15"
category: "电化学阻抗测试"
electrolyte: "DALE"
additive: "不涉及"
counter_electrode: "不涉及"
encapsulation: "不涉及"
baseline: "不涉及"
data_types: []
status: "needs_review"
tags: [组会, EIS, 电化学阻抗, ATO串扰, 10x10阵列, DALE, 烷基链, 黏度]
modified: "2026-10-26"
related:
  - experiments/2026-10-10-raman-dale-and-dye-bath.md
  - experiments/2026-10-13-new-pbi-cl-batch-baseline-response-time.md
  - methods/eis.md
  - notes/2026-10-19-naming-convention-and-cross-batch-summary.md
---

# 2026-10-15 组会讨论与 EIS 测试

## 一、组会讨论要点

### 1. 能否用电压脉冲方案解决 ATO 串扰问题

针对 **10×10 阵列展示器件的行列干扰问题**，讨论用**电压脉冲驱动方案**来抑制 ATO 串扰
（相邻像素/行列之间的离子或电荷串扰）。尚未形成结论，属待验证方案。

### 2. 能否通过延长 DALE 的烷基链调节黏度，代替 EMIMTFSI 的作用

讨论思路：EMIMTFSI 离子液体的作用之一是增塑、降低体系黏度。
提出的问题是**能否通过延长 DALE 的烷基链来调节黏度**，从而在少用或不用 EMIMTFSI 的情况下
达到相近的离子传输性能。同样属待验证设想。

## 二、EIS 测试

对 **DALE00 – DALE50** 等样品进行 **EIS（电化学阻抗谱）** 测试。

### 方法资料（只登记位置，不上传文件）

| 类型 | 位置 |
|---|---|
| 教程视频 | https://www.bilibili.com/video/BV1fgK8zUEZS/?spm_id_from=333.1391.0.0&vd_source=c336829353cfeaac005ab4c1ff5e7b50 |
| 整理文本 | `D:\Desktop\光谱电化学\EIS\EIS电化学阻抗谱分析流程_含关键截图_打印版_含实验记录表.docx` |

操作流程与拟合步骤另见 `methods/eis.md`。

## 结果

EIS 数据已采集，**未处理**（未做等效电路拟合与离子电导计算）。

## 待补清单

| # | 待补项 | 说明 |
|---|---|---|
| 1 | EIS 原始数据路径 | 未提供，需补记本地路径 |
| 2 | 测试条件 | 频率范围、振幅、偏置电位、温度 |
| 3 | 等效电路拟合 | 未做；拟合结果待补 |
| 4 | 组会两个设想的结论 | 电压脉冲方案、延长烷基链方案均未定论 |

## 原始数据

- EIS 数据：**待补本地路径**（数据只留本地，记录本不上传数据文件）
