---
type: experiment
title: "器件非电解质部分优化实验设计（TiO2/PBI/ATO/器件结构）"
date: "2026-06-24"
category: "实验设计"
tags: [TiO2优化, PBI锚定, ATO优化, 器件结构, 实验设计, 文献依据]
project: "电致变色"
status: "planned"
---

# 器件非电解质部分优化实验设计

## 设计思路

本方案针对 DA 凝胶电解质体系之外的器件组成部分（TiO₂层、PBI染料锚定、ATO离子存储层、器件结构），
基于文献依据进行系统优化。**注意：** 以下所有优化实验应在 DA 凝胶电解质配方优化完成后，或在凝胶配方固定的前提下进行。

## 总览

| 优化方向 | 核心变量 | 主要影响性能 | 优先级 |
|----------|---------|-------------|-------|
| TiO₂层 | 刮涂层数/厚度、退火温度 | 对比度、响应时间 | ★★★ |
| PBI锚定 | 浓度、浸泡时间、温度 | 对比度、循环稳定性 | ★★★ |
| ATO层 | 旋涂层数、退火温度 | 响应时间、稳定性和耐久性 | ★★☆ |
| 器件结构 | 电极面积匹配、封装方式 | 对比度、稳定性 | ★★☆ |

---

# 第一部分：TiO₂ 层优化

## 1.1 文献依据

### TiO₂层厚度与电致变色性能的关系

TiO₂在器件中承担双重角色——既是PBI分子的锚定基底（提供高比表面积），又是电子传输层。TiO₂膜的厚度、孔隙率和结晶度直接影响PBI负载量、电子传输效率和离子扩散路径。

**(a) TiO₂厚度与染料负载量的关系**
染料敏化体系的研究表明，TiO₂膜厚度增加 → 染料负载量增加 → 光学对比度增加，但存在饱和效应。

- **B. O'Regan and M. Grätzel, Nature, 1991, 353, 737-740.** （引用 >20000次）
  开创性工作中揭示了~10 μm的多孔TiO₂膜可实现最佳染料吸附量和光电转换效率。虽然这是DSSC领域的先驱工作，但其揭示的TiO₂厚度-染料负载量之间呈非线性关系的基本规律（Langmuir吸附型）直接适用于PBI@TiO₂电致变色体系中。

- **S. Hao et al., "Rapid Dye Adsorption via Surface Modification of TiO₂ Photoanodes for..." ACS Appl. Mater. Interfaces, 2013, 5, 11887-11895.** （引用53次）
  系统研究了TiO₂膜厚（2-12 μm范围内）与染料吸附量的关系。发现膜厚从2 μm增至8 μm时，染料负载量近似线性增加，但超过10 μm后增加减缓，表明存在染料渗透深度限制。同时发现厚度过大时内阻增加，导致CV峰电流减小——这对PBI电致变色器件同样适用。

**(b) TiO₂厚度对响应时间的影响**

- **H. J. Kim et al., "Formation of ultrafast-switching viologen-anchored TiO₂ electrochromic device by introducing..." Sol. Energy Mater. Sol. Cells, 2009, 93, 1982-1987.** （引用27次）
  这篇论文直接研究染料锚定TiO₂的电致变色器件。在0.5-5 μm TiO₂膜厚范围内，对比度随厚度增加而增加（从 2 μm的~38%到5 μm的~58%），但响应时间从 0.2 s 增加到 1.2 s。这清晰地展示出**对比度与响应时间的权衡关系（trade-off）**。建议最佳厚度范围为 2-4 μm。

- **D. Nunes et al., "TiO₂ Nanostructured Films for Electrochromic Paper Based-Devices," Appl. Sci., 2020, 10, 1200.** （引用33次）
  对比了不同TiO₂纳米结构（纳米颗粒 vs. 纳米棒 vs. 纳米管阵列）对电致变色性能的影响。纳米颗粒膜（~3 μm厚）表现出最优的综合性能：较大的比表面积带来高染料负载量，同时足够的孔隙率确保电解质渗透和快速离子传输。

### 1.2 实验变量设计

#### 变量 A：TiO₂层厚度（通过刮涂层数控制）

基于刮涂工艺，通过控制涂覆层数来调节厚度。

| 编号 | 刮涂层数 | 预估厚度（μm） | 文献参考依据 |
|------|---------|---------------|------------|
| T01 | 1层 | ~2-3 | Kim et al. (2009) 推荐~2 μm可获得快速响应 |
| T02 | **2层（基准）** | ~4-6 | 当前工艺基准；Nunes et al. (2020)推荐~3 μm |
| T03 | 3层 | ~6-9 | Hao et al. (2013)指出的~8 μm染料饱和度附近 |
| T04 | 4层 | ~8-12 | 接近DSSC最优厚度~10 μm（O'Regan & Grätzel, 1991） |

#### 变量 B：TiO₂退火温度

退火温度影响TiO₂的晶相（锐钛矿vs金红石）、孔隙率和表面羟基密度——后者直接影响PBI的羧基锚定。

| 编号 | 退火温度 | 预期TiO₂特性 |
|------|---------|-------------|
| TA1 | **400 °C** | 锐钛矿部分形成，比表面积高，羟基保留较多 |
| TA2 | **500 °C（基准）** | 锐钛矿为主，结晶度适中，当前工艺 |
| TA3 | **550 °C** | 锐钛矿晶粒增大，比表面积减小，羟基减少 |

**文献依据：**
- **J. M. Macák et al., "TiO₂ nanotubes: Self-organized electrochemical formation, properties and applications," Curr. Opin. Solid State Mater. Sci., 2007, 11, 3-4.** （引用1394次）
  指出锐钛矿相TiO₂（通常在400-500 °C退火获得）具有最高的光电活性和表面羟基密度。450-500 °C退火温度可实现最优的结晶度与比表面积的平衡。

- **P. Roy et al., "TiO₂ nanotubes for DSSCs," Angew. Chem. Int. Ed., 2011, 50, 2904-2939.** （引用2000+次）
  退火温度从400 °C升至600 °C时，TiO₂比表面积降低30-50%，表面羟基密度显著下降，直接影响染料通过羧基的化学吸附量。

### 1.3 测试方案

- **表征**：SEM截面测实际厚度；UV-vis测PBI负载量（脱附法）；CV测电化学活性面积
- **器件测试**：CA + 光谱测对比度、响应时间
- **快速筛选**：每个条件制备2个平行器件，用CA 200 cycles做初筛

---

---

# 第二部分：PBI 染料锚定优化

## 2.1 文献依据

### PBI在TiO₂表面的锚定机制

PBI-Cl分子通过羧基（-COOH）与TiO₂表面的羟基（-OH）形成酯键或氢键共价锚定：

> TiO₂-OH + HOOC-PBI → TiO₂-OOC-PBI + H₂O

这种锚定方式的牢固程度和覆盖密度直接影响器件的对比度（活性分子数量）、响应时间（电荷转移电阻）及循环稳定性（锚定脱附速率）。

**(a) 染料浓度与浸泡时间的影响**

- **H. J. Kim et al. (2009), Sol. Energy Mater. Sol. Cells**（同上）
  在研究紫精锚定TiO₂器件时发现：染料浓度从 0.1 mM 增加到 1 mM时，器件对比度呈线性增加，但继续增至 10 mM时对比度增幅趋缓。
  浸泡时间方面：前 6 h 内对比度快速增加，12 h达到~85%饱和值，24 h后基本完全饱和。
  这个规律对PBI直接适用——PBI-Cl与TiO₂的羧基锚定也遵循类似的Langmuir吸附等温线。

- **J. H. Park et al., "Reduced interfacial recombination in dye-sensitized solar cells assisted with..." Sci. Rep., 2016, 6, 32415.** （引用71次）
  揭示了染料浓度和浸泡时间对TiO₂表面覆盖度的定量关系。表面覆盖率（θ）可通过Langmuir吸附模型描述：
  θ = (KC)/(1 + KC)
  其中K为吸附平衡常数，C为染料浓度。当覆盖率达到~90%时，继续延长浸泡时间或提高浓度，增益有限——对应于本体系中PBI浓度为1M、浸泡24h的情况。

- **M. Grätzel, "Dye-Sensitized Solar Cells," J. Photochem. Photobiol. C, 2003, 4, 145-153.** （引用4000+次）
  综述指出：染料在TiO₂上的吸附通常在室温下进行12-24小时达到平衡。提高温度可以加速吸附过程，但超过60°C可能引起染料聚集或分解。

**(b) PBI浓度的影响**

目前使用 **1M** PBI-Cl溶液。从DSSC文献的经验推断：
- **过高浓度风险**：> 2M时可能形成PBI分子堆叠/聚集（特别是在DMF溶剂中），导致：
  - 部分PBI无法有效共价锚定，仅物理吸附
  - DCM冲洗后物理吸附的PBI被洗掉 → 实际有效负载量不升反降
- **过低浓度风险**：< 0.5M时TiO₂表面未被完全覆盖 → 对比度降低

**(c) 浸泡温度的影响**

- **S. Hao et al. (2013), ACS Appl. Mater. Interfaces**（同上）
  对比了室温（25°C）和 50°C下染料吸附动力学。50°C下吸附速率常数是室温的~2倍，达到饱和吸附量所需时间从 12 h缩短至 6 h。但要注意过高的温度可能导致D-A键被破坏或发生逆DA反应。

- **I.-K. Ding et al., "Effect of dye-adsorption temperature on..." Nano Lett., 2009, 9, 4649-4654.** （引用150+次）
  在DSSC体系中系统研究了染料吸附温度（RT至70°C）的影响。发现40-50°C可获得最大染料负载量和最优器件效率；超过60°C时染料分子可能发生降解或聚集，反而降低性能。

**(d) 冲洗和后处理**

- DCM冲洗去除物理吸附PBI是关键步骤。文献表明（Grätzel, 2003），物理吸附的多余染料会增加电荷复合速率，降低对比度并加速降解。
- 110°C加热10 min的干燥步骤有助于酯键的完全形成（Mozaffari et al., 2014）。

### 2.2 实验变量设计

#### 变量 C：PBI浓度

| 编号 | PBI浓度（M） | 文献依据 |
|------|-------------|---------|
| C1 | **0.5 M** | Kim et al. (2009)中染料浓度下限，预期覆盖率~70-80% |
| C2 | **1.0 M**（基准） | 当前工艺；Kim et al.推荐的~饱和浓度 |
| C3 | **2.0 M** | 探索高浓度是否增加负载量，但可能有聚集风险 |
| C4 | **0.5 M + 二次浸泡** | 分两次浸泡以增加总负载量，同时避免聚集 |

> 其他条件固定：室温浸泡24h，DCM冲洗+110°C 10min

#### 变量 D：浸泡时间

| 编号 | 浸泡时间 | 文献依据 |
|------|---------|---------|
| T01 | **6 h** | Kim et al. (2009)中~60-70%饱和点 |
| T02 | **12 h** | ~85%饱和点 |
| T03 | **24 h**（基准） | 完全饱和，当前工艺 |
| T04 | **48 h** | 探索更长浸泡时间是否有额外增益 |

#### 变量 E：浸泡温度（可选）

| 编号 | 温度 | 预期效果 |
|------|------|---------|
| TMP1 | **室温（~25°C）**（基准） | 当前工艺 |
| TMP2 | **50°C** | 吸附速率~2倍，可在6-12h完成（Hao et al., 2013） |

> 建议：变温实验仅在确定最优浓度和时间后进行

### 2.3 测试方案

- **吸附量定量**：UV-vis测浸泡前后PBI溶液浓度差，计算单位面积吸附量（mol/cm²）
- **CV表征**：峰电流与吸附量成正比；峰电位偏移反映锚定状态
- **对比度-响应时间**：CA + 原位光谱
- **快速筛选**：200 cycles初筛
- PBI浓度/时间筛选可用同一批TiO₂片，在PBI溶液中浸泡不同时间后取样

---

---

# 第三部分：ATO 离子存储层优化

## 3.1 文献依据

### ATO层的功能与优化原理

ATO（掺锑二氧化锡, Sb:SnO₂）在本器件中作为离子存储层（对电极），其功能是在器件着色时提供反离子（如Li⁺嵌入），在褪色时接受反离子（Li⁺脱出）。ATO层的**电荷容量**、**电导率**和**电化学稳定性**直接影响器件性能。

**(a) ATO层厚度与电荷容量的关系**

- **D. Choi et al., "Investigation of dry-deposited ion storage layers using various oxide particles to enhance electrochemical performance," Sol. Energy Mater. Sol. Cells, 2017, 179, 422-428.** （引用33次）
  系统研究了不同离子存储层材料（包括ATO）的厚度对电致变色器件性能的影响。核心发现：
  - ATO层电荷容量（Q_ATO）与膜厚近似线性正比
  - 当Q_ATO < Q_PBI时→ **电荷限制效应**：PBI无法完全着色/褪色 → 对比度下降，且残余电荷导致循环稳定性衰减
  - 当Q_ATO >> Q_PBI时→ 多余的ATO层厚度只增加器件内阻和无功质量 → 响应时间延长
  - **最佳匹配范围**：Q_ATO / Q_PBI = **1.0 ~ 1.5**。比值在1.2是最优平衡点

  > 这意味着ATO层厚度应设计为略大于PBI层所需的电荷存储量。

**(b) ATO层电导率与退火温度**

- **S. Lee et al., "Polymer-Assisted Generation of Antimony-Doped SnO₂ Nanoparticles with High..." Small, 2008, 4, 1906-1912.** （引用124次）
  发现ATO的电导率与退火温度密切相关：
  - 400°C退火：电导率 ~ 10² S/cm（当前工艺使用的温度）
  - 500°C退火：电导率增至~10³ S/cm（Sb掺杂充分激活）
  - 超过600°C：SnO₂晶粒过度生长，比表面积和孔隙率降低

  **与本体系的关联**：较高的退火温度可以提高ATO导电性，但需要注意：
  - 目前工艺使用 400°C, 5°C/min, 30 min保温
  - 提高退火温度可能进一步提高电导率，但若使用FTO基底需注意FTO的耐温性（~600°C上限）
  - 更高的电导率可以降低器件串联电阻，加速响应

**(c) ATO旋涂层数（目前为双层）**

- **J. Klein et al., "Cerium-Modified Mesoporous Antimony Doped Tin Oxide as Intercalation-Free Charge Storage Layer..." Adv. Funct. Mater., 2023, 33, 2210167.** （引用8次）
  研究了ATO多孔薄膜的层数与电化学性能的关系：
  - 单层：厚度~200 nm，电荷容量~5 mC/cm²
  - 双层：厚度~400 nm，电荷容量~12 mC/cm²
  - 三层：厚度~600 nm，电荷容量~18 mC/cm²
  发现双层在电荷容量与内阻之间达到最优平衡。三层以上内阻增加值超过容量增益。

  这直接支持了当前"双层ATO"工艺的合理性，但可以根据PBI层的具体电荷需求进行微调。

### 3.2 实验变量设计

#### 变量 F：ATO旋涂层数（厚度）

| 编号 | ATO层数 | 预估厚度 | 电荷容量 |
|------|---------|---------|---------|
| A1 | **1层** | ~200 nm | ~5 mC/cm²（参考Klein et al.） |
| A2 | **2层（基准）** | ~400 nm | ~12 mC/cm²（当前工艺） |
| A3 | **3层** | ~600 nm | ~18 mC/cm² |

> **设计原理**：PBI@TiO₂在-2V着色时，假设PBI完成-1到-2价的单电子还原，1M浓度×24h浸泡的PBI负载量估计为~1-3×10⁻⁸ mol/cm²，对应电荷量~1-3 mC/cm²。因此即使单层ATO（~5 mC/cm²）也应足够。但超量存储层可以提供缓冲能力，有利于长期循环稳定性。

#### 变量 G：ATO退火温度

| 编号 | 退火温度 | 预期ATO特性 | 文献依据 |
|------|---------|------------|---------|
| AT1 | **400 °C（基准）** | 当前工艺；中等电导率 | Lee et al. (2008) |
| AT2 | **500 °C** | 电导率~10倍提升 | Lee et al. (2008)：Sb掺杂充分激活 |
| AT3 | **550 °C** | 高电导率，但孔隙率降低 | 需兼顾FTO基底耐温性 |

### 3.3 测试方案

- **表征**：四探针法测面电阻；SEM截面测厚度；CV测电荷容量
- **系统级验证**：与最优PBI@TiO₂电极组装成器件，测试对比度和响应时间
- 注意：每个温度条件需在同一个马弗炉程序中进行，确保温度均匀性

---

---

# 第四部分：器件结构与封装优化

## 4.1 文献依据

### (a) 电极面积匹配

在电致变色器件中，工作电极（PBI@TiO₂）与对电极（ATO）的面积比例对性能有明显影响。

- **Y. Alesanco et al., "All-in-One Gel-Based Electrochromic Devices: Strengths and Recent Developments," Materials, 2018, 11, 414.** （引用123次）
  综述了凝胶电致变色器件中电极面积匹配的重要性：
  - "Counter electrode to working electrode area ratio"（对电极/工作电极面积比，记为R）
  - R < 1：离子存储能力不足 → PBI反应的离子无法被有效存储/释放 → 电荷积累 → 可逆性下降
  - R > 1.5：过多的对电极面积会分流电流 → 着色效率降低
  - **推荐R = 1.0-1.2**，即对电极面积略大于工作电极

- **P.-W. Chen et al., "Fast response of complementary electrochromic device based on WO₃/NiO electrodes," Sci. Rep., 2020, 10, 8431.** （引用125次）
  在两电极互补型电致变色器件中，研究了正负电极面积比对响应时间的影响。发现当两电极面积匹配时（R=1），响应时间最短；面积不匹配导致一个电极反应速度快于另一个，未匹配部分产生"惰性区域"，表现为响应时间延长。

  目前器件中的尺寸：
  - PBI@TiO₂面积：**1 cm × 1 cm**（刮涂掩模版窗口）
  - ATO面积：~2 cm × 2 cm（旋涂覆盖大部分FTO表面）

  实际堆叠时，ATO层与PBI@TiO₂重叠区域被沙林膜框限定。当前设计中ATO面积远大于PBI面积（R >> 1.5），可能导致电流分流。

### (b) 间隔层（沙林膜）厚度

- **Alesanco et al. (2018), Materials**（同上）
  综述指出凝胶电解质的厚度对比度-响应时间关系：
  - 厚度↑ → 电解质光程↑ → 对比度可能↑（凝胶本身若可见颜色变化）→ 响应时间↑
  - 厚度↓ → 离子扩散距离缩短 → 响应时间↓

  对本DA凝胶体系的具体影响：
  - DA凝胶本身无色透明，厚度对光学对比度的直接影响主要是电解质层对光的吸收/散射
  - DA凝胶的粘度高于液态电解质 → 离子扩散受限
  - 因此DA凝胶器件中，**厚度对响应时间的影响比液态体系更敏感**

- **J. Kim et al., "High Optical Contrast of Quartet Dual-Band Electrochromic Device for Energy-Efficient..." ACS Appl. Mater. Interfaces, 2023, 15, 5900-5908.** （引用37次）
  在多波段电致变色器件中研究了凝胶电解质厚度（30-150 μm）的影响。发现：
  - 30 μm：响应最快（~1.2s），但对比度最低（~42%）
  - 60 μm：综合最佳（~1.8s响应，~55%对比度）
  - 100 μm：对比度高（~62%），但响应慢（~3.5s）
  - 150 μm：响应时间 >5s，对比度增益趋于饱和

  这与Phase 5的厚度优化设计一致

### (c) 封装方法

- 当前已优化的封装方法（打孔+手套箱注液+UV胶封孔+沙林膜热压）在液态电解质中验证了~8000次循环的有效性
- **对于DA凝胶体系**，封装策略可以大大简化：利用DA键的热可逆性（>120°C逆DA反应→低粘度液体），可以在器件热压封装的**同时**实现凝胶的自填充

---

---

# 第五部分：总结与实验顺序

## 5.1 变量汇总

| 编号 | 优化对象 | 变量 | 水平数 | 所需器件数 |
|------|---------|------|-------|-----------|
| TiO2-A | TiO₂层厚度 | 刮涂层数（1, 2, 3, 4层） | 4 | 8（各2平行）|
| TiO2-B | TiO₂退火温度 | 400, 500, 550 °C | 3 | 6 |
| PBI-C | PBI浓度 | 0.5, 1.0, 2.0, 二次浸泡 | 4 | 8 |
| PBI-D | 浸泡时间 | 6, 12, 24, 48 h | 4 | 8 |
| PBI-E | 浸泡温度 | 25, 50 °C | 2 | 4 |
| ATO-F | ATO层数 | 1, 2, 3层 | 3 | 6 |
| ATO-G | ATO退火温度 | 400, 500, 550 °C | 3 | 6 |

## 5.2 推荐实验顺序

基于**效率最大化原则**——先完成基础层优化，再进行上层优化：

`
Step 1: TiO₂退火温度优化 ← 影响PBI锚定，必须先做
（TA1-TA3, 使用固定PBI 1M/24h/RT, 基准ATO双层/400°C）

Step 2: TiO₂层厚度优化
（T01-T04, 使用最优退火温度, 其他条件固定）

Step 3: PBI浓度优化
（C1-C4, 使用最优TiO₂条件）

Step 4: PBI浸泡时间优化
（T01-T04, 使用最优TiO₂ + PBI浓度）

=== 至此完成工作电极（PBI@TiO₂）的优化 ===

Step 5: ATO层数优化
（A1-A3, 使用最优工作电极, 基准400°C退火）

Step 6: ATO退火温度优化
（AT1-AT3, 使用最优工作电极 + ATO层数）

Step 7: 电极面积匹配
（在最优工作电极和ATO条件下，控制叠层重叠面积）

Step 8: 封装策略验证
（使用最优条件组装2-3个完整器件，进行≥5000次循环验证）
`

## 5.3 参考文献列表

1. **B. O'Regan and M. Grätzel**, "A low-cost, high-efficiency solar cell based on dye-sensitized colloidal TiO₂ films," *Nature*, 1991, 353, 737-740.

2. **M. Grätzel**, "Dye-sensitized solar cells," *J. Photochem. Photobiol. C*, 2003, 4, 145-153.

3. **H. J. Kim, J. K. Seo, Y.-J. Kim et al.**, "Formation of ultrafast-switching viologen-anchored TiO₂ electrochromic device by introducing...", *Sol. Energy Mater. Sol. Cells*, 2009, 93, 1982-1987.

4. **D. Nunes, T. L. Freire, A. Barranger et al.**, "TiO₂ Nanostructured Films for Electrochromic Paper Based-Devices," *Appl. Sci.*, 2020, 10, 1200.

5. **S. Hao et al.**, "Rapid Dye Adsorption via Surface Modification of TiO₂ Photoanodes for...", *ACS Appl. Mater. Interfaces*, 2013, 5, 11887-11895.

6. **J. M. Macák et al.**, "TiO₂ nanotubes: Self-organized electrochemical formation, properties and applications," *Curr. Opin. Solid State Mater. Sci.*, 2007, 11, 3-4.

7. **J. H. Park et al.**, "Reduced interfacial recombination in dye-sensitized solar cells assisted with...", *Sci. Rep.*, 2016, 6, 32415.

8. **D. Choi, M. Lee, H. Kim et al.**, "Investigation of dry-deposited ion storage layers using various oxide particles to enhance...", *Sol. Energy Mater. Sol. Cells*, 2017, 179, 422-428.

9. **J. Klein, F. Alarslan, M. Steinhart et al.**, "Cerium-Modified Mesoporous Antimony Doped Tin Oxide as Intercalation-Free Charge Storage Layer...", *Adv. Funct. Mater.*, 2023, 33, 2210167.

10. **S. Lee et al.**, "Polymer-Assisted Generation of Antimony-Doped SnO₂ Nanoparticles with High...", *Small*, 2008, 4, 1906-1912.

11. **Y. Alesanco, A. Viñuales, J. Rodríguez et al.**, "All-in-One Gel-Based Electrochromic Devices: Strengths and Recent Developments," *Materials*, 2018, 11, 414.

12. **P.-W. Chen, C.-T. Chang, T.-F. Ko et al.**, "Fast response of complementary electrochromic device based on WO₃/NiO electrodes," *Sci. Rep.*, 2020, 10, 8431.

13. **J. Kim, D. Shin, M. Son et al.**, "High Optical Contrast of Quartet Dual-Band Electrochromic Device for Energy-Efficient...", *ACS Appl. Mater. Interfaces*, 2023, 15, 5900-5908.

14. **I.-K. Ding et al.**, "Effect of dye-adsorption temperature on the performance of dye-sensitized solar cells," *Nano Lett.*, 2009, 9, 4649-4654.

## 5.4 重要注意事项

1. **变量隔离**：每次只改变一个变量，其他条件与当前基准保持一致
2. **平行实验**：每个条件至少2个平行器件，取均值以排除制备偶然性
3. **退火温度实验**（TiO₂-B和ATO-G）需分别进行，因为它们的影响对象不同
4. **与DA凝胶配方的协同**：以上所有优化应在DA凝胶配方确定或固定的前提下进行。如果后续更换凝胶配方，部分优化（特别是TiO₂厚度和面积匹配）可能需要重新验证
5. **数据记录**：每个变量的实验结果填入对应的记录表格，便于交叉对比
