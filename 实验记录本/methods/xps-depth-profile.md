---
type: method
title: "XPS 深度剖析（变色层/界面 SEI 分析）"
category: "表面成分分析"
tags: [XPS, 深度剖析, Ar离子溅射, SEI层, LiF, Li3N, 荷电校正, 真空转移]
modified: "2026-10-24"
---

# 测试方法：XPS 深度剖析（用于循环后变色层表面 SEI 分析）

## 目的

用 X 射线光电子能谱（XPS）配合 Ar⁺ 离子溅射深度剖析，测定循环后**变色层（TiO₂–PBI-Cl）表面 SEI 层**的
元素组成与化学态，并给出由外到内的成分梯度，回答"循环后界面到底生成了什么"的问题。

选择 XPS 而不是继续做形貌表征的原因：2026-10-23 的 SEM 观察未能明确分辨出 SEI 层形貌，
而 XPS 对**纳米级薄层的化学态**比表面形貌衬度敏感得多。

## 适用范围

- 循环后器件拆解得到的变色层玻璃片（TiO₂–PBI-Cl / FTO）
- 重点关注含 Li 化合物（LiF、Li₃N、Li₂CO₃）与 TFSI⁻ 分解产物（C–F）

## 一、样品制备

### 1.1 实验室实际流程（2026-10-21 采用）

1. 拆解循环后的器件，取出**变色层一侧的玻璃片**。
2. **冲洗去除表面固态电解质**——这是本步的关键，残留电解质会完全掩盖 SEI 信号
   （聚合物骨架与锂盐的 C、F、O、S 信号远强于 nm 级界面层）。
   - 最初按文献做法用**碳酸二甲酯（DMC）**冲洗，**效果不理想**（固态 DA 交联网络难以溶胀去除）。
   - 后续**全部改用二氯甲烷（DCM）**冲洗，DA 网络去除效果明显改善。
3. 将冲洗后的玻璃片**掰成小片**，尺寸以能贴在 XPS 样品托上为准。
4. 干燥后上样。

> 补充：文献流程（见下）强调 SEI 对水氧极其敏感、需惰性气氛转移。本次样品为
> **空气暴露状态**下制样与转移，因此外层的 Li₂CO₃ / LiOH / 吸附碳信号可能部分来自大气二次反应，
> 判读时以此为前提（见"注意事项"）。

### 1.2 文献流程（调研依据，2026-10-21 整理）

来源：WO₃ 薄膜表面 SEI 的研究（对应图 5a/d、S16–S18），原文 Experimental Section：

1. 薄膜工作电极在三电极电解池中**循环 30 圈**，保证 SEI 充分生长。
2. 取出后用**无水 NMP 快速冲洗**表面，去除吸附的游离锂盐与残留电解液。
3. 转移至**氩气手套箱内干燥**。原文明确指出：SEI 层对水、氧气极其敏感，**全程隔绝大气**，
   避免 SEI 氧化水解。
4. 在手套箱中将样品固定在 XPS 样品托上，**真空密封转移**进 XPS 仪器，全程不接触空气。

## 二、仪器与测试条件

### 2.1 文献条件（调研依据）

| 项目 | 参数 |
|------|------|
| 仪器 | Kratos AXIS SUPRA X 射线光电子能谱仪 |
| 激发源 | 单色 Al Kα X 射线源 |
| 模式 | Ar⁺ 离子溅射深度剖析 |
| 溅射采集点 | 0 s（原始表面）、60 s 溅射后 |
| 采集谱区 | F 1s、C 1s、Li 1s |

### 2.2 本次实测条件（2026-10-22，从数据包 VAMAS 头读出）

| 项目 | 参数 |
|------|------|
| 仪器型号 | MI-600-BE9240AA（Kratos AXIS SUPRA 系列） |
| 激发源 | 单色 Al Kα，1486.69 eV，发射电流 5.00 mA |
| 透镜/光阑 | Lens: Hybrid；Collimation: Slot；Tuning: Spectroscopy |
| 电荷中和 | 开（Filament 0.42 A，Bias 1 V，Charge Balance 5 V） |
| Survey | 通能 160 eV，步长 1.0 eV，驻留 120 ms，1 sweep，扫谱 145 s，X 射线 75 W；动能窗口 286.69–1491.69 eV（结合能约 −5 ~ 1200 eV） |
| 窄扫 | 通能 40 eV，步长 0.1 eV，1 sweep，扫谱 60 s，X 射线 150 W |
| 窄扫谱区 | C 1s（BE 275–298 eV）、F 1s（BE 673–693 eV）、O 1s（BE 523–541 eV）、N 1s（BE 388–408 eV）、Li 1s（BE 43–63 eV） |
| 深度剖析 | 4 个样品，按溅射时间分目录：样品 1/2/3 为 0、20、60、180 s；样品 4 仅 1 个采集点 |

> 数据包（VAMAS 文件头）中**未记录**溅射离子能量、束流、溅射速率等参数，
> 因此本次以**溅射时间**为深度轴，不做时间到 nm 的换算。

## 三、关注的特征峰（文献调研汇总）

| 物种 | 谱区 | 结合能 / eV | 出处与说明 |
|------|------|-------------|-----------|
| **LiF** | F 1s | **685.0 / 685.3** | 电致变色准固态电解质 SEI；WO₃/PVTC 体系溅射 60 s 后出现 |
| **LiF** | Li 1s | **55.6** | 同上，与 F 1s 的 685 eV 互相印证 |
| **Li₃N** | N 1s | **398.7 / 399.3** | 原文 OCR 作 "Li₃N"；TFSI⁻ 分解产物 |
| **Li₃N** | Li 1s | **55.1** | 与 LiF 的 Li 1s 仅差约 0.5 eV，需谨慎分峰 |
| C–F（TFSI⁻） | C 1s | 292.8；另一文献记 290.6 | 指示 TFSI⁻ 阴离子存在 |
| C–F（TFSI⁻） | F 1s | 688.6 | 与 LiF 685 eV 区分是本次判读核心 |
| C–C | C 1s | 284.8 | 常用作荷电校正内标 |
| C–O | C 1s | ≈286.8 | 聚合物电解质 |
| C=O | C 1s | 288.8 | 聚合物电解质 |
| Li₂CO₃ | C 1s | ≈290.03 | 聚合物电解质/SEI 常见组分 |

调研覆盖的文献（用于确定扫描条件与判读口径）：

1. *In Situ Formation of LiF-Rich SEI in Quasi-Solid Electrolytes Enables Long-Life Electrochromic Devices*
2. *Design of Quasi-Metal–Organic Frameworks for Solid Polymer Electrolytes Enabling an Ultra-Stable Interface with Li Metal Anode*
3. *A Dielectric MXene-Induced Self-Built Electric Field in Polymer Electrolyte Triggering Fast Lithium-Ion Transport and High-Voltage Cycling Stability*
4. *A self-healing Li-crosslinked elastomer promotes a highly robust and conductive solid–electrolyte interphase*
5. *Highly Efficient Aligned Ion‑Conducting Network and Interface Chemistries for Depolarized All‑Solid‑State Lithium Metal Batteries*
6. *Hybrid Crosslinked Solid Polymer Electrolyte via In-Situ Solidification Enables High-Performance Solid-State Lithium Metal Batteries*

调研原稿：`D:\Desktop\XPS\界面 深度XPS扫描条件调研.docx`
实测数据：`D:\Desktop\XPS\XPS-2-20125110-23634-155419-20261021_1.zip`

> 原始数据只保留在本地，记录本与 GitHub 上仅记录存放路径，不上传任何谱图数据文件。

## 四、数据分析要点

1. **荷电校正**：先以 C–C 284.8 eV 校准全谱结合能，再分峰。
2. **F 1s 分峰是关键判据**：688.6 eV（C–F，残留 TFSI⁻）与 685 eV（LiF）的相对强度，
   直接反映 TFSI⁻ 是否分解、分解程度如何。
3. **深度梯度**：比较 0 / 20 / 60 / 180 s 各谱区的峰位与强度变化，
   判断 SEI 是否为"外层有机、内层无机富 LiF/Li₃N"的结构（文献普遍报道的结构）。
4. **残留干扰判读**：冲洗效果直接决定数据可信度。若 C 1s 中聚合物特征峰（C–O/C=O/C–F）
   在溅射后仍很强，说明电解质残留严重，需考虑重复制样或延长冲洗。

## 五、注意事项

- **SEI 对水氧敏感**：理想流程是惰性气氛冲洗、干燥、真空转移。本次为空气暴露转移，
  外层含 Li 物种可能已部分转化为 Li₂CO₃ / LiOH，**外层结论需保守**，内层（溅射后）相对可信。
- **Ar⁺ 溅射的副效应**：长时间溅射可能引起含 Li 化合物的择优溅射与还原，
  深度方向的"成分变化"要与溅射损伤区分开。
- **荷电**：样品为玻璃基底上的分子层，导电性差，必须开电荷中和，且分峰前务必做荷电校正。
- **样品尺寸**：掰片时避免手直接接触变色区域，避免机械划伤测试面。

## 相关记录

- experiments/2026-10-21-xps-sample-preparation-sei.md（制样）
- experiments/2026-10-22-xps-depth-profile-sei.md（测试）
- experiments/2026-10-23-sem-molecular-layer-sei-after-100-cycles.md（同批样品 SEM 观察）
