# `RigidVisGeom`

`RigidVisGeom` 是用于可视化刚体链接的几何形状，与 `RigidGeom` 相对应，但仅用于渲染目的，不参与碰撞检测。每个 RigidLink 可以包含多个 RigidVisGeom，它们共同定义了刚体的可视化外观。

## 功能说明

`RigidVisGeom` 类提供了以下主要功能：

- 定义刚体链接的可视化几何形状
- 设置可视化形状的位置和姿态
- 管理表面材质和纹理
- 提供渲染所需的几何信息
- 支持与碰撞几何形状不同的可视化表示

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 可视化几何形状在引擎中的全局索引 |
| `uid` | `int` | 可视化几何形状的唯一标识符 |
| `link` | `RigidLink` | 所属的刚体链接 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `pos` | `list` | 可视化形状在链接坐标系中的位置 [x, y, z] |
| `quat` | `list` | 可视化形状在链接坐标系中的姿态四元数 [w, x, y, z] |
| `init_pos` | `list` | 初始位置 [x, y, z] |
| `init_quat` | `list` | 初始姿态四元数 [w, x, y, z] |
| `vmesh` | `object` | 可视化网格对象 |
| `n_vverts` | `int` | 可视化顶点数量 |
| `n_vfaces` | `int` | 可视化面数量 |
| `init_vverts` | `list` | 初始可视化顶点坐标 |
| `init_vfaces` | `list` | 初始可视化面索引 |
| `init_vnormals` | `list` | 初始可视化法线向量 |
| `uvs` | `list` | UV 纹理坐标 |
| `surface` | `object` | 表面材质对象 |
| `metadata` | `dict` | 元数据信息 |
| `is_built` | `bool` | 可视化几何形状是否已构建完成 |

## 代码示例

```python
import genesis
from genesis import World, RigidEntity

# 创建一个新的世界
world = World()

# 创建一个带有自定义可视化几何形状的刚体实体
custom_robot = RigidEntity(
    world=world,
    name="custom_robot",
    link_params=[
        {
            "name": "base",
            "geoms": [
                {
                    "type": "box",
                    "size": [0.5, 0.5, 0.2],
                    "pos": [0, 0, 0.1],
                    "material": "default"
                }
            ],
            "vgeoms": [
                {
                    "type": "box",
                    "size": [0.55, 0.55, 0.25],
                    "pos": [0, 0, 0.1],
                    "surface": {
                        "color": [0.8, 0.2, 0.2, 1.0],  # 红色
                        "shininess": 0.8
                    }
                }
            ],
            "is_free": False  # 固定基座
        },
        {
            "name": "arm",
            "geoms": [
                {
                    "type": "cylinder",
                    "size": [0.05, 1.0],
                    "pos": [0, 0, 0.5],
                    "material": "default"
                }
            ],
            "vgeoms": [
                {
                    "type": "cylinder",
                    "size": [0.06, 1.05],
                    "pos": [0, 0, 0.5],
                    "surface": {
                        "color": [0.2, 0.8, 0.2, 1.0],  # 绿色
                        "shininess": 0.6
                    }
                }
            ]
        },
        {
            "name": "end_effector",
            "geoms": [
                {
                    "type": "sphere",
                    "size": [0.1],
                    "pos": [0, 0, 0],
                    "material": "default"
                }
            ],
            "vgeoms": [
                {
                    "type": "sphere",
                    "size": [0.12],
                    "pos": [0, 0, 0],
                    "surface": {
                        "color": [0.2, 0.2, 0.8, 1.0],  # 蓝色
                        "shininess": 1.0
                    }
                },
                {
                    "type": "cylinder",
                    "size": [0.03, 0.2],
                    "pos": [0, 0, -0.1],
                    "surface": {
                        "color": [0.8, 0.8, 0.2, 1.0],  # 黄色
                        "shininess": 0.5
                    }
                }
            ]
        }
    ],
    joint_params=[
        {
            "name": "shoulder",
            "type": "hinge",
            "link_idx1": 0,
            "link_idx2": 1,
            "pos": [0, 0, 0.2],
            "axis": [0, 1, 0]
        },
        {
            "name": "wrist",
            "type": "ball",
            "link_idx1": 1,
            "link_idx2": 2,
            "pos": [0, 0, 1.0],
            "axis": [1, 0, 0]
        }
    ]
)

# 初始化世界
world.init()

# 获取可视化几何形状信息
base_link = custom_robot.links[0]
base_vgeom = base_link.vgeoms[0]

arm_link = custom_robot.links[1]
arm_vgeom = arm_link.vgeoms[0]

end_effector = custom_robot.links[2]
eef_sphere = end_effector.vgeoms[0]
eef_cylinder = end_effector.vgeoms[1]

# 打印可视化几何形状信息
print(f"Base vgeom type: {base_vgeom.type}")
print(f"Base vgeom size: {base_vgeom.size}")
print(f"Arm vgeom position: {arm_vgeom.pos}")
print(f"End effector has {end_effector.n_vgeoms} vgeoms")

# 运行模拟
for _ in range(100):
    world.step()
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_geom.RigidVisGeom
    :members:
    :show-inheritance:
    :undoc-members:
```
