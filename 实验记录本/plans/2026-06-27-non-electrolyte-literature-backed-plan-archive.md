---
type: plan
title: "非凝胶电解质部分详细优化实验方案（文献依据归档版）"
date: "2026-06-27"
category: "实验方案"
tags: [电致变色, TiO2, PBI, ATO, 器件优化, 对比度, 响应时间, 稳定性, 文献依据]
project: "电致变色"
status: "completed"
modified: "2026-06-29"
---

# 非凝胶电解质部分详细优化实验计划（文献依据归档版）

> 说明：本文件保留 2026-06-27 版本中较完整的文献依据和变量分析，用作参考归档。2026-06-29 起，后续执行以 `2026-06-29-da-gel-device-performance-optimization-plan.md` 为主方案。

## 0. 研究目标与边界

本计划只优化凝胶电解质以外的部分，即：

1. 工作电极：FTO / TiO2 / PBI
2. 离子存储/对电极：ATO / FTO
3. 两电极面积与叠层结构
4. 封装与测试工况

凝胶电解质固定为 DA 凝胶体系后，再执行本计划。若后续 DA 凝胶配方大幅改变（例如 EMIMTFSI 含量、EO:Li 或交联密度改变），需要复核 TiO2 厚度、ATO 容量和电压窗口。

核心优化目标：

| 指标 | 目标方向 | 主要受控因素 |
|------|----------|--------------|
| 对比度 ΔT | 提高 | PBI负载量、TiO2比表面积、ATO电荷容量、电压窗口 |
| 响应时间 tc/tb | 降低 | TiO2厚度、膜孔隙、ATO电阻、面积匹配、凝胶接触 |
| 稳定性 | 提高 | PBI锚定牢固度、ATO容量匹配、封装、过电位控制 |
| 可重复性 | 提高 | 膜厚、退火、染浴、冲洗、叠层压力 |

---

## 1. 关键因素总览

| 模块 | 关键因素 | 为什么关键 | 建议优先级 |
|------|----------|------------|------------|
| TiO2层 | 膜厚/刮涂层数 | 决定PBI负载量、电子传输距离和离子扩散阻力 | 最高 |
| TiO2层 | 退火温度/孔结构 | 决定锐钛矿结晶度、比表面积、表面羟基和膜附着力 | 高 |
| TiO2层 | 表面预处理 | 影响PBI羧酸基锚定和膜均匀性 | 中 |
| PBI层 | PBI浓度 | 决定表面覆盖度和聚集风险 | 最高 |
| PBI层 | 浸泡时间/温度 | 决定吸附平衡、覆盖度和锚定质量 | 最高 |
| PBI层 | 冲洗与热处理 | 去除物理吸附PBI，降低残余峰和循环衰减 | 高 |
| ATO层 | 旋涂层数/厚度 | 决定电荷容量是否匹配PBI还原/氧化电荷 | 高 |
| ATO层 | 退火温度 | 决定ATO导电性、孔结构和界面阻抗 | 中高 |
| 器件结构 | 工作电极/对电极面积比 | 影响电荷平衡、无效电流和响应时间 | 高 |
| 器件结构 | 叠层对位与压力 | 影响凝胶接触、局部短路和光谱测试重复性 | 中高 |
| 测试工况 | 电压窗口/脉冲时间 | 决定PBI还原程度、副反应和循环稳定性 | 最高 |

---

## 2. 文献依据与可转化结论

### 2.1 TiO2/PBI 类染料锚定电极

**依据 A：染料锚定 TiO2 可实现快速电致变色，但 TiO2 厚度存在对比度/响应速度权衡。**

Kim 等在 viologen-anchored TiO2 电致变色器件中发现，引入致密/介孔 TiO2 后，器件可实现亚秒级快速切换；同时 TiO2 厚度增加会提高染料负载量和光学调制，但也增加电子/离子传输路径，响应变慢。  
来源：H. J. Kim, J. K. Seo, Y.-J. Kim et al., *Solar Energy Materials and Solar Cells*, 2009, 93, 1982-1987, DOI: 10.1016/j.solmat.2009.05.007.

**转化到本实验：** TiO2 厚度必须作为第一优先级变量，不宜单纯追求更厚；推荐用 1、2、3、4 次刮涂建立厚度-对比度-响应时间曲线。

**依据 B：TiO2 纳米结构的孔隙率和比表面积控制电解质渗透与变色中心负载。**

Nunes 等综述和实验讨论了纳米结构 TiO2 在电致变色纸器件中的作用，强调纳米颗粒/多孔结构可提升界面面积，但过厚或孔道不连通会限制电解质进入和离子传输。  
来源：D. Nunes et al., "TiO2 Nanostructured Films for Electrochromic Paper Based-Devices", *Applied Sciences*, 2020, 10, 1200, DOI: 10.3390/app10041200.

**转化到本实验：** TiO2 不只看厚度，还要看表面裂纹、孔隙连通性、膜脱落；建议每组做 SEM 或至少光学显微观察。

**依据 C：PBI 可通过羧酸盐形式化学吸附在 TiO2 上，吸附后会形成可逆的一电子/二电子还原过程。**

New Journal of Chemistry 的 amino-acid appended perylene bisimides 研究显示，PBI 衍生物可通过羧酸盐化学吸附固定在纳米晶 TiO2 薄膜上，并保持可逆的电致变色还原行为；PBI/TiO2 杂化体系的吸收和电化学响应受分子堆积与表面覆盖度影响。  
来源：R. Lundy, E. R. Draper, J. J. Walsh et al., "Amino acid appended perylene bisimides: self-assembly, immobilization on nanocrystalline TiO2, and electrochromic properties", *New Journal of Chemistry*, 2018, 42, 19020-19025, DOI: 10.1039/C8NJ04214D.

**转化到本实验：** PBI 的“有效锚定量”比“总浸泡量”更重要。必须加入 DCM 冲洗强度、二次浸泡、热处理这类变量，避免物理吸附 PBI 造成残留负一价峰。

### 2.2 TiO2/ATO 互补杂化电极与厚度比

**依据 D：互补结构中，TiO2 和 ATO 厚度比会显著影响对比度、响应时间和稳定性。**

Nature Communications 2021 的柔性高性能电致变色器件使用 self-assembled 2D TiO2/Ti3C2Tx MXene 异质结构，强调孔隙率和电子连通性的平衡对高着色效率、快速离子/电子传输和稳定性至关重要。该文以达到 90% 光学调制的时间定义着色/褪色响应时间。  
来源：R. Li, X. Ma, J. Li et al., "Flexible and high-performance electrochromic devices enabled by self-assembled 2D TiO2/MXene heterostructures", *Nature Communications*, 2021, 12, 1587, DOI: 10.1038/s41467-021-21852-7.

**转化到本实验：** 不应只独立优化 TiO2 和 ATO，而要最终用“工作电极电荷 Q_PBI 与对电极容量 Q_ATO 的匹配”来判断。建议 Q_ATO/Q_PBI 目标为 1.0-1.5。

### 2.3 离子存储层与对电极容量

**依据 E：离子存储层容量不足会限制变色层完全反应，容量过剩会提高内阻和降低响应速度。**

Choi 等比较多种干法沉积氧化物离子存储层，指出对电极/离子存储层需要与电致变色层电荷容量匹配，否则会出现电荷限制、残余着色或响应变慢。  
来源：D. Choi, M. Lee, H. Kim et al., "Investigation of dry-deposited ion storage layers using various oxide particles to enhance electrochemical performance", *Solar Energy Materials and Solar Cells*, 2017, 179, 422-428, DOI: 10.1016/j.solmat.2017.10.001.

**转化到本实验：** ATO 层数应以电荷容量为评价标准，不是越厚越好。至少测试 1、2、3 层 ATO，并通过 CV/CA 积分估算容量。

**依据 F：ATO/SnO2 类透明导电氧化物的退火温度影响导电性和结构。**

Sb 掺杂 SnO2 纳米粒子研究表明，退火有助于提高晶化和导电性，但过高温度导致晶粒长大、比表面积下降。  
来源：S. Lee et al., "Polymer-Assisted Generation of Antimony-Doped SnO2 Nanoparticles with High...", *Small*, 2008, 4, 1906-1912.

**转化到本实验：** 目前 ATO 400 °C 退火是合理基准，但值得增加 450/500 °C 条件，观察响应是否加快；550 °C 以上谨慎，因为 FTO 和膜孔结构可能受损。

### 2.4 染料吸附动力学与表面处理

**依据 G：TiO2 染料吸附通常遵循覆盖度饱和模型，浓度和时间都有平台期。**

DSSC 领域大量研究表明，羧酸/膦酸类染料在 TiO2 上的吸附随时间增加趋于饱和；过高浓度和过长浸泡会增加分子聚集或多层物理吸附，反而降低电子传输和稳定性。  
来源：M. Grätzel, "Dye-sensitized solar cells", *Journal of Photochemistry and Photobiology C*, 2003, 4, 145-153, DOI: 10.1016/S1389-5567(03)00026-1.

**转化到本实验：** 你的 1 mM/24 h（实验记录写作 1M，但计算实际为 1 mM）是合理基准。建议把浓度统一校正为 mM 记录，并做 0.25、0.5、1、2 mM 梯度。

**依据 H：温和升温可加快染料吸附，但高温可能造成聚集或降解。**

染料吸附温度研究表明，升高 sensitizer adsorption temperature 会显著影响 TiO2 表面覆盖度、界面复合和器件性能。温和升温可加快吸附，但温度过高或吸附状态不佳会带来界面副作用。  
来源：F. Sauvage, J.-D. Decoppet, M. Zhang, S. M. Zakeeruddin, P. Comte, M. K. Nazeeruddin, P. Wang, M. Grätzel, "Effect of Sensitizer Adsorption Temperature on the Performance of Dye-Sensitized Solar Cells", *Journal of the American Chemical Society*, 2011, 133, 9304-9310, DOI: 10.1021/ja110541t.

**转化到本实验：** PBI 可做室温 24 h 与 50 °C 6/12 h 对照；若 50 °C 样品对比度相当但响应更快，说明表面覆盖更均匀。

### 2.5 器件结构、面积与测试判据

**依据 I：凝胶型 ECD 的性能不仅由材料决定，也强烈受电极面积、间距、封装和离子通道影响。**

Alesanco 等综述了 all-in-one gel-based electrochromic devices，指出凝胶厚度、电极接触、封装和电极平衡会影响响应时间、稳定性和光学调制。  
来源：Y. Alesanco, A. Viñuales, J. Rodríguez et al., "All-in-One Gel-Based Electrochromic Devices: Strengths and Recent Developments", *Materials*, 2018, 11, 414, DOI: 10.3390/ma11030414.

**转化到本实验：** 固定凝胶后还要优化重叠面积、压力和封装，尤其要避免 ATO 面积远大于 PBI 面积导致边缘/旁路电流。

**依据 J：响应时间应统一按 90% 光学调制定义。**

多篇 ECD 文献采用达到最终光学调制 90% 所需时间作为着色/褪色时间定义，这比“肉眼看完全变色”更可重复。  
来源：Chen et al., "Fast response of complementary electrochromic device based on WO3/NiO electrodes", *Scientific Reports*, 2020, 10, 8431, DOI: 10.1038/s41598-020-65191-x；以及 Nature Communications 2021 互补杂化器件。

**转化到本实验：** 后续所有响应时间用 90% ΔT 定义，并把光谱采集间隔降到 0.1-0.2 s。

---

## 3. 实验总体路线

建议采用“先单电极，再全器件；先粗筛，再精筛”的顺序。

### Stage 1：工作电极 TiO2/PBI 快速筛选

目的：找出兼具高 PBI 有效负载和快响应的 TiO2/PBI 条件。

固定条件：

- ATO：当前双层 ATO，400 °C 退火
- 凝胶：固定基准 DA 凝胶
- 器件面积：PBI 活性区 1 cm × 1 cm，ATO 重叠面积先控制为 1.2 cm × 1.2 cm
- 测试：CV + CA 光谱，先 200 cycles 快速筛选

### Stage 2：ATO 对电极容量匹配

目的：让 Q_ATO/Q_PBI 在 1.0-1.5，减少 PBI 氧化不完全和长期衰减。

### Stage 3：器件结构与电压窗口

目的：在材料条件确定后，优化面积比、封装压力、操作电压和脉冲时间。

### Stage 4：长循环与失效分析

目的：验证最优器件能否超过液态电解质器件的 8000 cycles / 80% 保持率。

---

## 4. 详细实验矩阵

## 4.1 TiO2 膜厚优化

### 变量设计

| 样品 | 刮涂层数 | 预计厚度 | 设计依据 |
|------|----------|----------|----------|
| Ti-1 | 1层 | 2-3 μm | 薄膜响应快，验证最低负载下限 |
| Ti-2 | 2层 | 4-6 μm | 当前/近当前基准 |
| Ti-3 | 3层 | 6-9 μm | 提高PBI负载，测试对比度平台 |
| Ti-4 | 4层 | 8-12 μm | 接近厚膜上限，观察扩散限制 |

### 每组操作

1. FTO 清洗和臭氧处理保持当前工艺。
2. TiO2 每刮一层后 80-100 °C 预干燥 5 min，再刮下一层，避免层间流动。
3. 最终统一 500 °C 退火 30 min。
4. PBI 统一使用 1 mM，室温 24 h，DCM 冲洗，110 °C 10 min。

### 测试与判据

| 测试 | 判据 |
|------|------|
| 台阶仪/截面SEM | 实测厚度；若无仪器，至少称重或光学显微比较 |
| UV-vis 初始态 | PBI吸收峰强度反映负载量 |
| CV | 峰电流积分估算 Q_PBI；峰形越尖锐、峰间距越小越好 |
| CA 光谱 | ΔT、tc/tb（90%定义） |
| 200 cycles | 保持率 >90% 进入下一轮 |

### 预期结果

- Ti-1：响应最快，但对比度可能不足。
- Ti-2/Ti-3：最可能为最佳区间。
- Ti-4：若对比度提升很小且响应明显变慢，则说明 PBI 负载已进入平台。

---

## 4.2 TiO2 退火温度优化

### 变量设计

使用 4.1 中表现最好的 TiO2 厚度。

| 样品 | 退火温度 | 保温时间 | 预期 |
|------|----------|----------|------|
| Ta-400 | 400 °C | 30 min | 比表面积和羟基多，但结晶/导电性可能不足 |
| Ta-450 | 450 °C | 30 min | 兼顾表面羟基和结晶度 |
| Ta-500 | 500 °C | 30 min | 当前基准，锐钛矿结晶较好 |
| Ta-550 | 550 °C | 30 min | 结晶好但比表面积/羟基下降，膜裂风险增大 |

### 关键判据

优先看：

1. PBI 负载量是否下降
2. CV 峰电流和峰间距
3. 膜是否开裂/脱落
4. 响应时间是否改善

### 预期选择

若 450 °C 对比度接近 500 °C 但响应更快或循环更稳，优先选 450 °C；若 400 °C 峰形宽、电荷转移慢，则淘汰。

---

## 4.3 PBI 浓度优化

### 注意：浓度单位校正

实验记录中写“1M”，但根据 6.35 mg / 856.35 g mol^-1 / 7.42 mL 计算，实际为约 1.0 mM。后续建议全部记录为 mM，避免文档误差。

### 变量设计

| 样品 | PBI浓度 | 浸泡条件 | 目的 |
|------|---------|----------|------|
| P-0.25 | 0.25 mM | RT 24 h | 低覆盖度对照 |
| P-0.5 | 0.5 mM | RT 24 h | 中低覆盖 |
| P-1 | 1.0 mM | RT 24 h | 当前基准 |
| P-2 | 2.0 mM | RT 24 h | 高覆盖/聚集风险 |
| P-0.5x2 | 0.5 mM | RT 12 h + 换液 12 h | 二次浸泡减少聚集 |

### 测试

1. 浸泡前后溶液 UV-vis：估算吸附量。
2. DCM 冲洗液 UV-vis：估算物理吸附/未锚定 PBI 被洗掉量。
3. 电极 UV-vis：PBI 特征峰强度。
4. CV：峰面积估算电活性 PBI 量。

### 选择判据

最佳浓度不是吸收最强，而是：

- ΔT 高
- tc/tb 不明显变慢
- CV 褪色后残余峰最小
- 200 cycles 后保持率最高

如果 P-2 的电极颜色更深但残余负一价峰更明显，说明聚集/物理吸附过多，应放弃。

---

## 4.4 PBI 浸泡时间与温度优化

### 变量设计

使用 4.3 最优浓度。

| 样品 | 温度 | 时间 | 目的 |
|------|------|------|------|
| Ads-6 | RT | 6 h | 吸附早期 |
| Ads-12 | RT | 12 h | 接近饱和 |
| Ads-24 | RT | 24 h | 当前基准 |
| Ads-48 | RT | 48 h | 长时间是否有额外收益 |
| Ads-50C-6 | 50 °C | 6 h | 加速吸附 |
| Ads-50C-12 | 50 °C | 12 h | 温和热吸附 |

### 判据

1. 若 Ads-12 与 Ads-24 对比度接近，但响应更快，选择 12 h。
2. 若 Ads-48 没有增加 ΔT 或残余峰变强，说明过度吸附。
3. 若 50 °C 样品对比度高且稳定，后续可用 50 °C 缩短制备时间。

---

## 4.5 冲洗与后处理优化

### 变量设计

| 样品 | DCM冲洗 | 后处理 | 目的 |
|------|---------|--------|------|
| W1 | 轻柔冲洗 10 s | 110 °C 10 min | 保留更多PBI |
| W2 | 标准冲洗 30 s | 110 °C 10 min | 当前基准 |
| W3 | 强冲洗 60 s | 110 °C 10 min | 去除物理吸附 |
| W4 | 标准冲洗 30 s | 80 °C 10 min | 降低热影响 |
| W5 | 标准冲洗 30 s | 130 °C 10 min | 促进锚定/干燥 |

### 重点观察

- 初始对比度是否因强冲洗下降
- CV 后是否有负一价残余峰
- 循环后电极是否发生不可逆变色

若强冲洗样品 ΔT 略降但稳定性明显提升，优先选择强冲洗，因为你的目标包括长期稳定性。

---

## 4.6 ATO 层数与容量匹配

### 变量设计

使用已优化的 TiO2/PBI 工作电极。

| 样品 | ATO旋涂层数 | 预期 |
|------|-------------|------|
| ATO-1 | 1层 | 低容量/低阻抗，验证是否足够 |
| ATO-2 | 2层 | 当前基准 |
| ATO-3 | 3层 | 高容量但内阻可能增加 |
| ATO-4 | 4层 | 容量过剩对照 |

### 测试与计算

1. 在三电极或对称近似条件下测 ATO 的 CV/CA。
2. 对 ATO 和 PBI 电极分别积分得到 Q_ATO 与 Q_PBI。
3. 计算：R_Q = Q_ATO / Q_PBI。

### 选择规则

| R_Q | 判断 |
|-----|------|
| <1.0 | 对电极容量不足，容易氧化/还原不完全 |
| 1.0-1.5 | 推荐区间 |
| 1.5-2.5 | 可接受，但注意响应变慢 |
| >2.5 | 容量过剩，可能增加内阻和无效电流 |

---

## 4.7 ATO 退火温度优化

### 变量设计

使用 4.6 最优层数。

| 样品 | 退火温度 | 保温时间 |
|------|----------|----------|
| AT-400 | 400 °C | 30 min |
| AT-450 | 450 °C | 30 min |
| AT-500 | 500 °C | 30 min |
| AT-550 | 550 °C | 30 min |

### 判据

1. 片电阻/四探针：越低越好，但不是唯一指标。
2. CV 电荷容量：不能因高温致密化而明显下降。
3. 器件 CA：响应时间是否缩短。
4. 透过率：ATO 太厚或烧结不佳会影响初始透明度。

---

## 4.8 面积匹配与叠层结构

### 变量设计

固定最优 TiO2/PBI、ATO 与 DA 凝胶。

| 样品 | PBI面积 | ATO有效重叠面积 | 面积比 A_ATO/A_PBI |
|------|---------|----------------|--------------------|
| AR-0.8 | 1.0 cm2 | 0.8 cm2 | 0.8 |
| AR-1.0 | 1.0 cm2 | 1.0 cm2 | 1.0 |
| AR-1.2 | 1.0 cm2 | 1.2 cm2 | 1.2 |
| AR-1.5 | 1.0 cm2 | 1.5 cm2 | 1.5 |
| AR-2.0 | 1.0 cm2 | 2.0 cm2 | 2.0 |

### 操作建议

- 不一定要改变 ATO 实际涂布面积，可用绝缘胶带/掩膜限制有效重叠区域。
- 光谱测试必须对准同一工作区中心，避免边缘区域影响。

### 预期

面积比 1.0-1.2 最可能最优；过大面积可能引入无效电流，过小面积可能容量不足。

---

## 4.9 电压窗口与脉冲时间优化

### 变量设计

使用已优化器件。

| 条件 | 着色电压 | 褪色电压 | 脉冲时间 | 目的 |
|------|----------|----------|----------|------|
| V1 | -1.5 V | 0 V | 5 s | 温和低副反应 |
| V2 | -2.0 V | 0 V | 5 s | 液态体系基准附近 |
| V3 | -2.5 V | 0 V | 5 s | 提高负二价比例 |
| V4 | -2.5 V | +0.3 V | 5 s | 改善氧化恢复 |
| V5 | -3.0 V | +0.5 V | 5 s | 完全还原/氧化上限 |
| V6 | -2.0 V | +0.3 V | 3 s | 快循环条件 |

### 选择原则

1. 若 -3.0 V 可提高 ΔT 但 500 cycles 衰减明显，不采用。
2. 若 +0.3/+0.5 V 能消除负一价残余峰，优先使用正向褪色电压。
3. 脉冲时间以达到 95% 稳态 ΔT 的最短时间为准，不盲目固定 5 s。

---

## 5. 推荐执行顺序与样品量

### 第一轮：粗筛（约 32 个器件）

| 步骤 | 条件数 | 平行数 | 器件数 |
|------|--------|--------|--------|
| TiO2厚度 | 4 | 2 | 8 |
| TiO2退火 | 4 | 2 | 8 |
| PBI浓度 | 5 | 2 | 10 |
| PBI时间/温度 | 6 | 1 | 6 |

第一轮结束后，确定工作电极最佳条件。

### 第二轮：对电极与结构（约 24 个器件）

| 步骤 | 条件数 | 平行数 | 器件数 |
|------|--------|--------|--------|
| ATO层数 | 4 | 2 | 8 |
| ATO退火 | 4 | 2 | 8 |
| 面积比 | 5 | 1 | 5 |
| 封装/压力微调 | 3 | 1 | 3 |

### 第三轮：操作窗口与长循环（约 10 个器件）

| 步骤 | 条件数 | 平行数 | 器件数 |
|------|--------|--------|--------|
| 电压窗口 | 6 | 1 | 6 |
| 最优条件复现 | 2 | 2 | 4 |

---

## 6. 数据记录模板

### 6.1 单器件性能记录

| 样品 | TiO2厚度 | TiO2退火 | PBI浓度 | PBI时间 | ATO层数 | ATO退火 | ΔT(λmax) | tc | tb | 200cy保持率 | 备注 |
|------|----------|----------|---------|---------|---------|---------|----------|----|----|-------------|------|
| | | | | | | | | | | | |

### 6.2 电荷匹配记录

| 样品 | Q_PBI (mC/cm2) | Q_ATO (mC/cm2) | Q_ATO/Q_PBI | ΔT | tc | tb | 判断 |
|------|----------------|----------------|-------------|----|----|----|------|
| | | | | | | | |

### 6.3 循环稳定性记录

| 样品 | 初始ΔT | 500cy | 1000cy | 3000cy | 5000cy | 8000cy | T80循环数 | 失效现象 |
|------|--------|-------|--------|--------|--------|--------|-----------|----------|
| | | | | | | | | |

---

## 7. 统一测试标准

1. 光谱采集间隔：0.1-0.2 s，避免之前 0.8 s 分辨率不足。
2. 响应时间：采用达到 90% ΔT 的时间。
3. 对比度：优先使用 λmax 处 ΔT，同时记录 300-800 nm 的最大 ΔT。
4. CV：扫描窗口先用 0.5 V 到 -3.0 V 确认完整氧化/还原，再确定 CA 电压。
5. 循环稳定性：短筛 200/500 cycles；入选样品做 8000 cycles。
6. 每次重新放置样品都必须重新扣背景，并记录样品角度，避免之前“2000次后角度变化导致对比度上升”的误差。

---

## 8. 参考文献

1. H. J. Kim, J. K. Seo, Y.-J. Kim et al. Formation of ultrafast-switching viologen-anchored TiO2 electrochromic device. *Solar Energy Materials and Solar Cells*, 2009, 93, 1982-1987. DOI: 10.1016/j.solmat.2009.05.007.

2. D. Nunes, T. L. Freire, A. Barranger et al. TiO2 Nanostructured Films for Electrochromic Paper Based-Devices. *Applied Sciences*, 2020, 10, 1200. DOI: 10.3390/app10041200.

3. M. Grätzel. Dye-sensitized solar cells. *Journal of Photochemistry and Photobiology C*, 2003, 4, 145-153. DOI: 10.1016/S1389-5567(03)00026-1.

4. D. Choi, M. Lee, H. Kim et al. Investigation of dry-deposited ion storage layers using various oxide particles to enhance electrochemical performance. *Solar Energy Materials and Solar Cells*, 2017, 179, 422-428. DOI: 10.1016/j.solmat.2017.10.001.

5. S. Lee et al. Polymer-Assisted Generation of Antimony-Doped SnO2 Nanoparticles with High Conductivity. *Small*, 2008, 4, 1906-1912.

6. Y. Alesanco, A. Viñuales, J. Rodríguez et al. All-in-One Gel-Based Electrochromic Devices: Strengths and Recent Developments. *Materials*, 2018, 11, 414. DOI: 10.3390/ma11030414.

7. P.-W. Chen, C.-T. Chang, T.-F. Ko et al. Fast response of complementary electrochromic device based on WO3/NiO electrodes. *Scientific Reports*, 2020, 10, 8431. DOI: 10.1038/s41598-020-65191-x.

8. R. Li, X. Ma, J. Li et al. Flexible and high-performance electrochromic devices enabled by self-assembled 2D TiO2/MXene heterostructures. *Nature Communications*, 2021, 12, 1587. DOI: 10.1038/s41467-021-21852-7.

9. R. Lundy, E. R. Draper, J. J. Walsh et al. Amino acid appended perylene bisimides: self-assembly, immobilization on nanocrystalline TiO2, and electrochromic properties. *New Journal of Chemistry*, 2018, 42, 19020-19025. DOI: 10.1039/C8NJ04214D.

10. V. K. Thakur, G. Ding, J. Ma, P. S. Lee, X. Lu. Hybrid Materials and Polymer Electrolytes for Electrochromic Device Applications. *Advanced Materials*, 2012, 24, 4071-4096. DOI: 10.1002/adma.201200213.

11. R. J. Mortimer. Electrochromic materials. *Chemical Society Reviews*, 1997, 26, 147-156.

12. P. M. S. Monk, R. J. Mortimer, D. R. Rosseinsky. *Electrochromism and Electrochromic Devices*. Cambridge University Press, 2007.

13. C. G. Granqvist. Electrochromics for smart windows: Oxide-based thin films and devices. *Thin Solid Films*, 2014, 564, 1-38.

14. F. Sauvage, J.-D. Decoppet, M. Zhang, S. M. Zakeeruddin, P. Comte, M. K. Nazeeruddin, P. Wang, M. Grätzel. Effect of Sensitizer Adsorption Temperature on the Performance of Dye-Sensitized Solar Cells. *Journal of the American Chemical Society*, 2011, 133, 9304-9310. DOI: 10.1021/ja110541t.

---

## 9. 下一步

建议从 **TiO2厚度优化 + PBI浓度单位校正** 开始。原因是这两项最直接决定有效 PBI 负载量，也是当前器件对比度、响应速度和残余峰问题的共同根源。

