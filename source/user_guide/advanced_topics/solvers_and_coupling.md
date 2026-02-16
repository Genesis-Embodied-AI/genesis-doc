# 🧮 非刚体耦合

Genesis 允许您在**同一场景**中组合多个连续介质和刚体求解器——例如 MPM 雪与 SPH 水交互、可变形 FEM 组织与手术工具碰撞，或刚体道具溅入颗粒床。所有跨求解器交互都由 `gs.engine.Coupler` 类协调。

本页解释：

* Coupler 的**架构**以及它如何决定哪些求解器对处于活动状态；
* 控制动量交换的**基于脉冲的碰撞响应**；
* **摩擦、恢复、柔软度**和其他耦合参数的含义；
* 当前支持的求解器对的**快速参考表**；以及
* 显示如何启用/禁用特定交互的**使用示例**。

---

## 1. 架构概述

内部仿真器拥有**一个 Coupler 实例**，它保存指向每个求解器的指针。在每个子步骤中，仿真器执行：

1. `coupler.preprocess(f)`  &nbsp;&nbsp; – 例如 CPIC 的表面操作。
2. `solver.substep_pre_coupling(f)`       – 推进每个单独的求解器。
3. `coupler.couple(f)`       – 在求解器之间交换动量。
4. `solver.substep_post_coupling(f)`       – 碰撞后的求解器后处理。

因为所有求解器字段都驻留在 Taichi 数据结构中，Coupler 可以调用触及多个求解器内存的 Taichi `@kernel`，**无需数据拷贝**。

### 1.1 激活耦合对

一对是否处于活动状态在调用 `Coupler.build()` 时**静态确定一次**：

```python
self._rigid_mpm = rigid.is_active() and mpm.is_active() and options.rigid_mpm
```


## 2. 基于脉冲的碰撞响应

### 2.1 符号距离与影响权重

对于每个候选接触，Coupler 查询刚体几何体的符号距离函数 `sdf(p)`。*柔软度*参数产生一个平滑的混合权重

$$
\text{influence} = \min\bigl( \exp\!\left(-\dfrac{\;d\;}{\epsilon}\right) ,\;1 \bigr)
$$

其中 `d` 是符号距离，`ε = coup_softness`。较大的柔软度值使接触区更厚，产生更柔和的脉冲。

### 2.2 相对速度分解

对于具有世界速度 **v** 的粒子/网格节点和刚体速度 **vᵣ**，**相对速度**为

$$ \mathbf r = \mathbf v - \mathbf v_{\text{rigid}}. $$

将 **r** 分解为其法向和切向分量

$$
 r_n = (\mathbf r \cdot \mathbf n)\,\mathbf n, \quad
 r_t = \mathbf r - r_n
$$

其中 **n** 是向外的表面法线。

### 2.3 法向脉冲（恢复）

如果法向分量是*向内*的 ($r_n<0$)，则施加一个脉冲，使得碰撞后

$$ r_n' = -e\,r_n, \quad 0 \le e \le 1, $$

其中 `e = coup_restitution` 是**恢复系数**。`e=0` 是完全非弹性的，`e=1` 是完全弹性的。

### 2.4 切向脉冲（库仑摩擦）

摩擦通过**缩放**切向分量来实现：

$$ r_t' = \max\!\bigl( 0,\;|r_t| + \mu \, r_n\bigr) \; \dfrac{r_t}{|r_t|}\,, $$

其中 `μ = coup_friction`。这是库仑摩擦的基于脉冲的变体，确保碰撞后的切向速度不超过粘着极限。

### 2.5 速度更新与动量传递

新的粒子/节点速度为

$$ \mathbf v' = \mathbf v_{\text{rigid}} + (r_t' + r_n') \times \text{influence} + \mathbf r\,(1-\text{influence}). $$

*动量变化*

$$ \Delta\mathbf p = m\,(\mathbf v' - \mathbf v) $$

作为**外力**应用于刚体

$$ \mathbf F_{\text{rigid}} = -\dfrac{\Delta\mathbf p}{\Delta t}. $$

因此满足牛顿第三定律，刚体对流体冲击做出响应。

---

## 3. 支持的求解器对

| 对 | 方向 | 说明 |
|------|-----------|-------|
| **MPM ↔ Rigid** | 基于网格节点的脉冲（支持 CPIC） |
| **MPM ↔ SPH**   | 平均 MPM 单元内的 SPH 粒子速度 |
| **MPM ↔ PBD**   | 类似于 SPH 但跳过固定的 PBD 粒子 |
| **FEM ↔ Rigid** | 仅在表面顶点上的碰撞 |
| **FEM ↔ MPM**   | 使用 MPM P2G/G2P 权重交换动量 |
| **FEM ↔ SPH**   | 实验性 – 仅法向投影 |
| **SPH ↔ Rigid** | 法线的鲁棒侧面翻转处理 |
| **PBD ↔ Rigid** | 位置校正然后速度投影 |
| **Tool ↔ MPM**  | 委托给每个 Tool 实体的 `collide()` |

如果表中未列出某个组合，则当前不支持。

---
