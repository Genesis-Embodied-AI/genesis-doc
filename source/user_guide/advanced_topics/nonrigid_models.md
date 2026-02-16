# 🧩 非刚体动力学

本页简要概述了 Genesis 的连续介质和离散求解器实现的物理模型。重点在于*正在求解哪些方程以及如何求解*，而不是 Python API。耦合理论请参见专门的*求解器与耦合*章节。

---

## 1. 欧拉稳定流体求解器 (`SFSolver`)

**目的。** 在固定网格上进行快速烟雾/气体仿真。

**控制方程** – 不可压缩 Navier–Stokes 方程。

**算法** – Jos Stam 的*稳定流体*：

1. **对流** – 速度用三阶 RK 回溯并插值（`backtrace` + `trilerp`）。数值上无条件稳定。
2. **外部脉冲** – 喷射源在对流后注入动量。
3. **粘度/衰减** – 可选的指数阻尼项。
4. **压力投影** – 用 Jacobi 迭代求解 Poisson 方程（`pressure_jacobi`）。

5. **边界条件** – 通过在固体面镜像分量强制执行法向速度为零。

因为所有步骤都是显式或对角隐式的，该方法在大时间步长下极其鲁棒，适合实时效果。

---

## 2. 物质点法求解器 (`MPMSolver`)

**目的。** 使用粒子 + 背景网格统一仿真固体、液体和颗粒介质。

**核心思想。** 连续介质动量方程在欧拉网格上求解，而材料历史（变形梯度、塑性应变等）存储在拉格朗日粒子上。

### 2.1 更新序列（APIC / CPIC 变体）

| 阶段 | 描述 |
|-------|-------------|
| P2G | 用 B-样条权重将质量和动量传输到相邻网格节点；添加应力贡献。 |
| Grid solve | 除以质量获得速度，应用重力和边界碰撞。 |
| G2P | 插值回网格速度，更新仿射矩阵和位置。 |
| Polar-SVD | 分解变形梯度；材料定律返回新的变形梯度。 |

### 2.2 本构模型

Genesis 提供了几个解析应力函数：

* **Neo-Hookean 弹性**（粉笔/雪）
* **Von Mises  capped 塑性**（雪-塑性）
* **弱可压缩液体**（WC 流体）
* **各向异性肌肉** 添加主动纤维应力

---

## 3. 有限元法求解器 (`FEMSolver`)

**目的。** 具有四面体网格的高质量可变形固体；对刚性材料可选隐式积分。

### 3.1 能量公式

总势能

$$ \Pi(\mathbf x) = \sum_{e} V_{e}\,\psi(\mathbf F_e) - \sum_{i} m_{i}\,\mathbf g\!\cdot\!\mathbf x_i. $$

第一变分产生内力；第二变分给出单元刚度。

### 3.2 隐式后向欧拉

给定当前状态 $(\mathbf x^n, \mathbf v^n)$ 通过 Newton–Raphson 求解 $\mathbf x^{n+1}$：

$$ \mathbf r(\mathbf x) = \frac{m}{\Delta t^{2}}(\mathbf x - \hat{\mathbf x}) + \frac{\partial \Pi}{\partial \mathbf x} = 0,$$
其中 $\hat{\mathbf x} = \mathbf x^{n} + \Delta t\,\mathbf v^{n}$ 是惯性预测。

每个 Newton 步骤用 PCG 求解 $\mathbf H\,\delta \mathbf x = -\mathbf r$；$\mathbf H$ 是一致的刚度 + 质量矩阵。使用逐顶点 3×3 块的块-Jacobi 逆作为预处理器。线搜索（Armijo 回溯）保证能量减少。

---

## 4. 基于位置的动力学求解器 (`PBDSolver`)

**目的。** 实时布料、弹性杆、XPBD 流体和粒子群。

### 4.1 XPBD 积分循环

1. **预测** – 显式 Euler：$\mathbf v^{*}\!=\!\mathbf v + \Delta t\,\mathbf f/m$ 和 $\mathbf x^{*}\!=\!\mathbf x + \Delta t\,\mathbf v^{*}$。
2. **投影约束** – 迭代边、四面体、SPH 密度等。
   对于每个约束 $C(\mathbf x)\!=\!0$ 求解 Lagrange 乘子 λ
   
   $$ \Delta\mathbf x = -\frac{C + \alpha\,\lambda^{old}}{\sum w_i\,|\nabla\!C_i|^{2}+\alpha}\,\nabla\!C, \quad \alpha = \frac{\text{compliance}}{\Delta t^{2}}. $$

3. **更新速度** – $\mathbf v = (\mathbf x^{new}-\mathbf x^{old})/\Delta t$。

### 4.2 支持的约束

* 拉伸/弯曲（布料）
* 体积保持（XPBD 四面体）
* 不可压缩 SPH 密度和粘度约束（流体-PBD）
* 通过位置校正 + 库仑模型的碰撞和摩擦。

---

## 5. 光滑粒子流体动力学求解器 (`SPHSolver`)

**目的。** 具有 WCSPH 或 DFSPH 压力求解器的基于粒子的流体。

### 5.1 核函数

三次样条核 $W(r,h)$ 和梯度 $\nabla W$，支撑半径 $h=$ `_support_radius`。

### 5.2 弱可压缩 SPH (WCSPH)

* 状态方程：$p_i = k\bigl[(\rho_i/\rho_0)^{\gamma}-1\bigr]$。
* 动量方程：
  
  $$ \frac{d\mathbf v_i}{dt} = -\sum_j m_j \left( \frac{p_i}{\rho_i^2} + \frac{p_j}{\rho_j^2} \right) \nabla W_{ij} + \mathbf g + \mathbf f_{visc} + \mathbf f_{surf}. $$

### 5.3 无散度 SPH (DFSPH)

* 将求解分为**散度遍**（强制执行 $\nabla\!\cdot\mathbf v = 0$）和**密度遍**（强制执行 $\rho\!=\!\rho_0$）。
* 两遍都使用 DFSPh 因子场通过 Jacobi 迭代迭代计算每个粒子的压力系数 κ。
* 确保比 WCSPH 更大的时间步长下的不可压缩性。

---

### 参考文献

* Stam, J. "Stable Fluids", SIGGRAPH 1999.
* Zhu, Y.⁠ & Bridson, R. "Animating Sand as a Fluid", SIGGRAPH 2005.
* Gao, T. et al. "Robust Simulation of Deformable Solids with Implicit FEM", SIGGRAPH 2015.
* Macklin, M. et al. "Position Based Fluids", SIGGRAPH 2013.
* Bender, J. et al. "Position Based Dynamics", 2014.
* Bavo et al. "Divergence-Free SPH", Eurographics 2015.
