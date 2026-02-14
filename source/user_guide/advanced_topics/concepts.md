# 🧩 核心概念

## 系统架构概述

```{figure} ../../_static/images/overview.png
```

<!-- From an user perspective, building an environment using Genesis is to add `Entity` in `Scene`, where `Entity` is specified by
- `Morph`: the geometry of the entity, e.g., primitive shapes or URDF.
- `Material`: the material of the entity, e.g., elastic object, liquid, sand, etc. Material is associated with the underlying solvers, e.g., there is MPM liquid and SPH liquid, those demonstrate different behaviors.
- `Surface`: the texture, rendering surface parameters etc

Under the hood, the scene consists of a simulator that encapsulates,
- `Solver`: the physics solver that handles the core physics engine with different methods like rigid, material point method (MPM), finite element method (FEM), etc.
- `Coupler`: the bridge across solvers that handle forces and any interaction in between. -->

从用户的角度来看，在 Genesis 中构建环境涉及向 `Scene` 添加 `Entity` 对象。每个 `Entity` 由以下部分定义：
- `Morph`：实体的几何形状，例如基本形状（如立方体、球体）或关节模型（如 URDF、MJCF）。
- `Material`：实体的物理属性，例如弹性固体、液体或颗粒材料。材料类型决定了所使用的底层求解器——例如，MPM 和 SPH 都可以模拟液体，但各自表现出不同的行为。
- `Surface`：视觉和交互相关的表面属性，例如纹理、粗糙度或反射率。

在幕后，`Scene` 由 `Simulator` 提供支持，其中包括：
- `Solver`：核心物理求解器，负责模拟不同的物理模型，例如刚体动力学、物质点法（MPM）、有限元法（FEM）、基于位置的动力学（PBD）和光滑粒子流体动力学（SPH）。
- `Coupler`：处理求解器之间交互的模块，确保一致的力耦合和实体间动力学。


## 数据索引

我们收到了很多关于如何部分操作刚体实体的问题，例如仅控制或检索某些属性。因此，我们认为有必要对数据索引访问进行更深入的解释。

**结构化数据字段**。在大多数情况下，我们使用 [struct Taichi field](https://docs.taichi-lang.org/docs/type#struct-types-and-dataclass)。以 MPM 为例进行更好的说明（[此处](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L103C1-L107C10) 和 [此处](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L123)）：
```
struct_particle_state_render = ti.types.struct(
    pos=gs.ti_vec3,
    vel=gs.ti_vec3,
    active=gs.ti_int,
)
...
self.particles_render = struct_particle_state_render.field(
    shape=self._n_particles, needs_grad=False, layout=ti.Layout.SOA
)
```
这意味着我们正在创建一个巨大的"数组"（在 Taichi 中称为 field），其中每个条目都是一个结构化数据类型，包含 `pos`、`vel` 和 `active`。注意，这个数据字段的长度是 `n_particles`，包含场景中的 __所有__ 粒子。那么，假设场景中有多个实体，我们如何区分不同的实体呢？一个直接的想法是用相应的实体 ID "标记" 数据字段的每个条目。然而，从内存布局、计算和 I/O 的角度来看，这可能不是最佳实践。相反，我们使用索引偏移来区分实体。

**局部索引和全局索引**。索引偏移同时提供了简单直观的用户界面（局部索引）和优化的底层实现（全局索引）。局部索引允许在实体 __内部__ 进行交互，例如特定实体的第 1 个关节或第 30 个粒子。全局索引是直接指向求解器内部数据字段的指针，考虑了场景中的所有实体。视觉示意如下：

```{figure} ../../_static/images/local_global_indexing.png
```

我们在下面提供了一些具体示例以便更好地理解：
- 在 MPM 模拟中，假设 `vel=torch.zeros((mpm_entity.n_particles, 3))`（仅考虑 __该__ 实体的所有粒子），[`mpm_entity.set_velocity(vel)`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L296) 自动抽象出全局索引的偏移。在底层，Genesis 实际上在做类似 `mpm_solver.particles[start:end].vel = vel` 的操作，其中 `start` 是偏移量（[`mpm_entity.particle_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L453)），`end` 是偏移量加上粒子数量（[`mpm_entity.particle_end`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L457)）。
- 在刚体模拟中，所有 `*_idx_local` 都表示局部索引，用户通过它们进行交互。它们将通过 `entity.*_start + *_idx_local` 转换为全局索引。假设我们想通过 [`rigid_entity.get_dofs_position(dofs_idx_local=[2])`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2201) 获取第 3 个自由度的位置，这实际上是在访问 `rigid_solver.dofs_state[2+offset].pos`，其中 `offset` 是 [`rigid_entity.dofs_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2717)。

（关于相关设计模式 [实体组件系统 (ECS)](https://en.wikipedia.org/wiki/Entity_component_system) 的有趣阅读）

## 直接访问数据字段

通常，我们不鼓励用户直接访问（Taichi）数据字段。
相反，用户应该主要使用每个实体中的 API，例如 `RigidEntity.get_dofs_position`。
但是，如果有人想访问 API 不支持的数据字段，并且无法等待新的 API 支持，可以尝试直接访问数据字段，这可能是一个快速但（很可能）低效的解决方案。具体来说，按照上一节描述的数据索引机制，假设有人想这样做：
```
entity: RigidEntity = ...
tgt = entity.get_dofs_position(...)
```

这等价于：
```
all_dofs_pos = entity.solver.dofs_state.pos.to_torch()
tgt = all_dofs_pos[:, entity.dof_start:entity.dof_end]  # 第一个维度是批次维度
```

所有实体都与特定的求解器相关联（混合实体除外）。
每个所需的物理属性都存储在求解器中的某个位置（例如，这里的自由度位置存储在刚体求解器的 `dofs_state.pos` 中）。
有关这些映射的更多详细信息，您可以查看 {doc}`命名与变量 <naming_and_variables>`。
此外，求解器中的所有数据字段都遵循全局索引（针对所有实体），您需要 `entity.*_start` 和 `entity.*_end` 来仅提取与特定实体相关的数据。
