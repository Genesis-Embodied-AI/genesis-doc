# 💥 刚体碰撞检测

Genesis 为刚体提供了高效、功能丰富的碰撞检测和接触生成管线。Python 实现位于 `genesis/engine/solvers/rigid/collider_decomp.py`。本页提供对算法构建块的*概念性*概述，以便您理解、扩展或调试代码。

> **范围。** 重点在于刚体-刚体交互。软体/粒子碰撞依赖于其他求解器，位于 `genesis/engine/coupler.py` 等文件中。

---

## 管线概述

整个过程可以分为三个连续阶段：

1. **AABB 更新** – 为每个几何体更新世界空间的轴对齐边界框。
2. **粗阶段 (Sweep-and-Prune)** – 基于 AABB 快速排除明显不相交的几何体对，输出*可能的*碰撞对。
3. **精阶段** – 使用特定原语算法、SDF、MPR 或 GJK 为每个保留的对稳健地计算实际接触流形（法线、穿透深度、位置等）。

`Collider` 通过公共的 `detection()` 方法协调所有三个阶段：

```python
collider.detection()  # 更新 AABB → SAP 粗阶段 → 精阶段
```

每个阶段在以下各节中描述。

---

## 1 · AABB 更新

辅助内核 `_func_update_aabbs()` 将工作委托给 `RigidSolver._func_update_geom_aabbs()`。它为每个几何体计算一个*紧密的*世界空间 AABB，并将结果存储在 `geoms_state[..].aabb_min / aabb_max` 中。

为什么每帧都要做这件事？

* 刚体移动 ⇒ 它们的边界框发生变化。
* AABB 重叠检查是粗阶段的基石。

---

## 2 · 粗阶段 – Sweep & Prune

粗阶段在 `_func_broad_phase()` 中实现。它是经典 Sweep-and-Prune（又称 Sort-and-Sweep）的 *N·log N* 插入排序变体：

1.  将每个 AABB 投影到单个轴（当前为 X 轴），并将其 *min* 和 *max* 端点插入可排序缓冲区。
2.  **热启动** – 端点已经几乎从上一帧排序好 ⇒ 插入排序几乎呈线性。
3.  遍历排序后的缓冲区，维护一个与当前端点重叠的区间*活动集*。
4.  当 `min_a` 穿过 `max_b` 内部时，我们就有一个*潜在的*对 `(geom_a, geom_b)`。

额外的过滤步骤移除物理上不可能或明确禁用的对：

* 相同连杆 / 相邻连杆过滤。
* `contype`/`conaffinity` 位掩码。
* 相对于世界都固定的连杆对。
* *休眠*支持 – 除非与激活体碰撞，否则忽略休眠体。

保留的对存储在 `broad_collision_pairs` 和 `n_broad_pairs` 中。

---

## 3 · 精阶段 – 接触流形生成

精阶段分为四个专门的内核：

| 内核 | 何时运行 | 目的 |
|------|---------|------|
| `_func_narrow_phase_convex_vs_convex` | 一般凸-凸 & 平面-凸 | 使用 **MPR**（Minkowski Portal Refinement）的默认路径，带有符号距离场查询回退。当 `RigidOptions` 中的 `use_gjk_collision` 选项设置为 `True` 时使用 **GJK** 算法。 |
| `_func_narrow_phase_convex_specializations` | 平面-盒体 & 盒体-盒体 | 具有一对凸几何体解析解的专门处理程序。 |
| `_func_narrow_phase_any_vs_terrain` | 至少一个几何体是*高度场地形* | 每个支撑单元生成多个接触点。 |
| `_func_narrow_phase_nonconvex_vs_nonterrain` | 至少一个几何体是**非凸**的 | 通过 SDF 顶点/边缘采样处理网格 ↔ 凸体或网格 ↔ 网格碰撞。 |

### 3.1 凸体-凸体

#### 3.1.1. GJK

GJK 配合 EPA 是许多物理引擎中广泛使用的接触检测算法，因为它具有以下优点：

* 完全在 GPU 上运行，得益于无分支的支持映射原语。
* 每个形状只需要一个*支持函数* – 无需面邻接或特征缓存。
* 当几何体不接触时给出分离距离。
* 在许多实现中经过验证的数值鲁棒性。

在 Genesis 中，当 `RigidOptions` 中的 `use_gjk_collision` 选项设置为 `True` 时启用。此外，Genesis 通过以下措施增强 GJK 的鲁棒性。

* 对运行时的单纯形和多面体进行彻底的退化检查。
* 鲁棒的面法线估计。
* 鲁棒的穿透深度上下界估计。

Genesis 使用**预计算的 Support Field** 加速支持查询（参见 {doc}`Support Field <support_field>`）。

通过在第一个接触法线周围进行*小姿态扰动*启用多接触生成。每对最多存储五个接触点 (`_n_contacts_per_pair = 5`)。

#### 3.1.2. MPR

MPR 是另一个被物理引擎广泛采用的接触检测算法。尽管它与 GJK 共享大部分优点，但当几何体不碰撞时它不给出分离距离，并且由于在许多实现中没有得到充分验证，可能容易受到数值错误和退化的影响。

在 Genesis 中，MPR 在深度穿透时通过符号距离场回退进行了改进。

与 GJK 一样，Genesis 使用预计算的 Support Field 加速 MPR 的支持查询，并通过在第一个接触法线周围进行小姿态扰动来检测多个接触点。因此，每对最多存储五个接触点 (`_n_contacts_per_pair = 5`)。

### 3.2 非凸对象

对于三角形网格或分解的凸簇，管线使用离线预烘焙的**符号距离场**（SDF）。算法采样

* 顶点（顶点-面接触），然后
* 边缘（边缘-边缘接触）

并保留最深的穿透。如果已经找到顶点接触，则跳过成本高昂的边缘遍历。

### 3.3 平面 ↔ 盒体 特殊情况

移植了 Mujoco 的解析平面-盒体和盒体-盒体例程，以获得额外的稳定性，并避免当盒体平放在平面上时的退化情况。

---

## 接触数据布局

成功的接触被推送到*数组结构体*字段 `contact_data`：

| 字段 | 含义 |
|------|------|
| `geom_a`, `geom_b` | 几何体索引 |
| `penetration` | 正深度（≤ 0 表示分离） |
| `normal` | 世界空间单位向量，从 **B 指向 A** |
| `pos` | 相互穿透的中点 |
| `friction` | 有效库仑系数（取两者最大值） |
| `sol_params` | 求解器调整常数 |

`n_contacts` 以原子方式递增，以便 GPU 内核可以并行追加。

---

## 热启动与缓存

为了提高时间相干性，我们为每对几何体缓存先前最深顶点的 ID 和最后已知的分离法线。缓存被咨询以*播种* MPR 搜索方向，并在对在粗阶段分离时清除。

---

## 休眠

启用此功能后，仅属于休眠体的接触被保留但不再每帧重新评估 (`n_contacts_hibernated`)。这大大减少了具有大型静态背景场景中的 GPU 工作量。

---

## 调整参数

| 选项 | 默认值 | 效果 |
|------|--------|------|
| `RigidSolver._max_collision_pairs` | 4096 | 粗阶段对的上限（每环境） |
| `Collider._mc_perturbation` | `1e-2` rad | 多接触搜索的扰动角度 |
| `Collider._mc_tolerance`    | `1e-2` 的 AABB 大小  | 重复接触拒绝半径 |
| `Collider._mpr_to_gjk_overlap_ratio` | `0.5` | 当一个形状包围另一个时从 MPR 切换到 SDF 的阈值 |

---

## 进一步阅读

* {doc}`Support Field <support_field>` – 支持映射形状的离线加速结构。
