# `AvatarGeom`

`AvatarGeom` 是 Avatar 实体中用于碰撞检测的几何组件，类似于 RigidGeom，但仅用于碰撞检查。

## 功能描述

`AvatarGeom` 负责处理 Avatar 实体的碰撞几何形状，包括网格数据、碰撞属性和 SDF（有符号距离场）表示。它主要用于碰撞检测系统，确保 Avatar 实体与其他实体之间的物理交互正确计算。

## 主要属性

- `T_mesh_to_sdf`: 网格到 SDF 的变换矩阵
- `contype`, `conaffinity`: 碰撞类型和亲和力参数，用于控制碰撞检测行为
- `friction`: 摩擦系数
- `coup_restitution`, `coup_softness`: 耦合恢复系数和柔软度
- `init_pos`, `init_quat`: 初始位置和四元数
- `mesh`: 几何网格数据
- `sdf_val`, `sdf_grad`: SDF 值和梯度
- `surface`: 表面属性，用于渲染

## 主要方法

- `get_AABB()`: 获取几何形状的轴对齐包围盒
- `get_pos()`: 获取当前位置
- `get_quat()`: 获取当前四元数
- `get_trimesh()`: 获取三角网格表示
- `get_verts()`: 获取顶点数据
- `set_friction(value)`: 设置摩擦系数
- `set_sol_params(restitution=None, softness=None)`: 设置求解参数
- `visualize_sdf()`: 可视化 SDF 表示

```{eval-rst}  
.. autoclass:: genesis.engine.entities.avatar_entity.avatar_geom.AvatarGeom
    :members:
    :show-inheritance:
    :undoc-members:
```
