# `gs.materials.Rigid`

`Rigid` 是 Genesis 引擎中用于定义刚体材料属性的类，用于模拟刚体的物理行为，如碰撞、摩擦等。

## 功能说明

- 定义刚体的物理材料属性
- 支持摩擦、恢复系数等参数的配置
- 提供材料属性的获取和设置接口
- 支持与其他物理系统的交互

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `density` | float | 材料密度 |
| `friction` | float | 摩擦系数 |
| `restitution` | float | 恢复系数 |
| `youngs_modulus` | float | 杨氏模量 |
| `poisson_ratio` | float | 泊松比 |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.rigid.Rigid
    :members:
    :show-inheritance:
    :undoc-members:
```
