# 🚀 Support Field 

Genesis 中凸体形状的碰撞检测严重依赖*支持函数*。Minkowski Portal Refinement (MPR) 算法的每次迭代都会询问以下形式的问题：

> _"给定方向 **d**，哪个顶点具有最大的点积 **v·d**？"_

一个朴素实现每次都必须遍历所有顶点——对于包含数千个点的模型来说是浪费的。为了避免这种情况，Genesis 在场景初始化期间为每个凸体几何体预计算一个 **Support Field**。实现位于 `genesis/engine/solvers/rigid/support_field_decomp.py`。

---

## 工作原理

1. **均匀方向网格**  –  使用经度/纬度 (`θ`, `ϕ`) 将球面离散为 `support_res × support_res` 个方向。默认 `support_res = 180`，产生约 32 k 个采样方向。
2. **离线投影**      –  对于每个方向，我们投影*所有*顶点并记住具有最大点积的索引。结果数组为：
   * `support_v ∈ ℝ^{N_dir×3}` – *对象空间*中的实际顶点位置。
   * `support_vid ∈ ℕ^{N_dir}`   – 原始顶点索引（用于热启动 SDF 查询）。
   * `support_cell_start[i_g]`   – 每个几何体扁平数组的前缀和偏移量。
3. **Taichi Fields** – 数组被复制到 GPU 驻留的 Taichi 字段中，以便内核无需主机往返即可访问它们。

```python
v_ws, idx = support_field._func_support_world(dir_ws, i_geom, i_batch)
```

以上以 **O(1)** 给出任何查询方向的世界空间极值点。

---

## 数据布局

| 字段 | 形状 | 描述 |
|-------|-------|-------------|
| `support_v`         | `(N_cells, 3)` | 顶点位置 (float32/64) |
| `support_vid`       | `(N_cells,)`   | 对应的顶点索引 (int32) |
| `support_cell_start`| `(n_geoms,)`   | 扁平数组的偏移量 |

!!! info "内存占用"
    使用默认分辨率，每个凸体形状使用约 32 k × (3 × 4 + 4) = 416 kB。对于小基元的集合，这比为每个形状构建 BVH 便宜得多。

---

## 优点

* **恒定时间查找** 在 MPR 期间 ⇒ GPU 上更少的分支发散。
* **GPU 友好** – Support Field 是一个简单的 SOA 数组，没有复杂的指针追踪。
* **适用于*任何*凸网格** – 无需标准轴或边界框。

## 限制与未来工作

* 方向网格是各向同性但非自适应的 – 小于角单元大小的特征可能映射到错误的顶点。
* 如果场景中几何体数量很大，预处理和内存消耗会很昂贵。

---

## API 摘要

```python
from genesis.engine.solvers.rigid.rigid_solver_decomp import RigidSolver
solver   = RigidSolver(...)
s_field  = solver.collider._mpr._support  # 内部句柄

v_ws, idx = s_field._func_support_world(dir_ws, i_geom, i_env)
```

`v_ws` 是*世界空间*支持点，而 `idx` 是原始网格中的顶点 ID（全局索引）。

---

## 与碰撞管线的关系

Support Field 是一个**加速结构**，专门被*凸体-凸体*精阶段使用。其他碰撞路径 – SDF、地形、平面-盒体 – 绕过它，因为它们要么依赖解析支持函数，要么依赖距离场。

有关 MPR 如何集成此结构的详细信息，请参见 {doc}`碰撞、接触与力 <collision_contacts_forces>`。
