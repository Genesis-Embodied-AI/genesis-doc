# `gs.materials.Avatar`

`Avatar` 是 Genesis 引擎中用于定义虚拟角色材料属性的类，用于模拟虚拟角色的物理行为，如肌肉、骨骼等。

## 功能说明

- 定义虚拟角色的物理材料属性
- 支持肌肉参数的配置，如刚度、阻尼等
- 提供材料属性的获取和设置接口
- 支持与其他物理系统的交互

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `density` | float | 材料密度 |
| `youngs_modulus` | float | 杨氏模量 |
| `poisson_ratio` | float | 泊松比 |
| `muscle_stiffness` | float | 肌肉刚度 |
| `muscle_damping` | float | 肌肉阻尼 |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.avatar.Avatar
    :members:
    :show-inheritance:
    :undoc-members:
```
