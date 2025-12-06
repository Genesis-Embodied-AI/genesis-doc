# `DroneEntity`

`DroneEntity` 是 Genesis 引擎中用于模拟无人机的实体类，提供了无人机的物理模拟和控制功能。

## 功能说明

- 模拟无人机的物理运动，包括位置、姿态、速度等
- 支持无人机的控制输入，如油门、俯仰、滚转、偏航
- 提供无人机状态获取和设置接口
- 支持与其他实体的交互

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `idx` | int | 实体在场景中的索引 |
| `uid` | int | 实体的唯一标识符 |
| `is_built` | bool | 实体是否已构建完成 |
| `scene` | Scene | 所属的场景对象 |
| `sim` | Simulator | 所属的模拟器对象 |
| `solver` | Solver | 处理该实体的求解器 |
| `material` | Material | 实体的材料属性 |
| `morph` | Morph | 实体的形态配置 |
| `surface` | Surface | 实体的表面约束或几何 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.drone_entity.DroneEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
