# 射线投射传感器

`RaycasterSensor` 提供基于射线的距离测量，可用于 LIDAR 仿真、接近传感和障碍物检测。

## 概述

射线投射传感器：

- 从连杆的坐标系向场景中投射射线
- 返回与几何体相交的距离
- 支持可配置的射线模式（线性、平面、自定义）
- 使用 GPU 加速的 BVH 遍历高效计算

## 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.add_entity(gs.morphs.Box(pos=(2, 0, 0.5)))  # 障碍物
scene.build()

# 添加射线投射传感器（使用 Lidar 选项）
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        link=robot.get_link("sensor_link"),
    )
)

# 仿真循环
for i in range(100):
    scene.step()

    # 获取距离数据
    ranges = lidar.get_data()  # (n_rays,) 距离数组
    print(f"Min range: {ranges.min():.2f} m")
```

## 配置

```python
gs.sensors.Raycaster(
    link=link,              # 附加传感器的 RigidLink
    n_rays=360,             # 投射的射线数量
    min_range=0.1,          # 最小检测范围 (m)
    max_range=10.0,         # 最大检测范围 (m)
    pattern="circular",     # 射线模式类型

    # 角度范围（用于圆形/线性模式）
    fov_horizontal=360.0,   # 水平视场角 (度)
    fov_vertical=0.0,       # 垂直视场角 (度)

    # 相对于连杆坐标系的位置偏移
    offset_pos=(0, 0, 0),
    offset_quat=(0, 0, 0, 1),
)
```

## 射线模式

### 圆形（2D LIDAR）

```python
lidar_2d = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        n_rays=360,
        pattern="circular",
        fov_horizontal=360.0,
    )
)
```

### 平面（3D LIDAR）

```python
lidar_3d = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        n_rays=16 * 360,  # 16 个垂直层
        pattern="planar",
        fov_horizontal=360.0,
        fov_vertical=30.0,
    )
)
```

### 自定义模式

```python
import numpy as np

# 定义自定义射线方向
rays = np.array([
    [1, 0, 0],    # 前方
    [0, 1, 0],    # 左方
    [-1, 0, 0],   # 后方
    [0, -1, 0],   # 右方
])

sensor = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        ray_directions=rays,
    )
)
```

## 输出格式

| 输出 | 形状 | 描述 |
|--------|-------|-------------|
| `ranges` | `(n_rays,)` | 到交点的距离（无碰撞时为 max_range） |
| `hits` | `(n_rays,)` | 有效相交的布尔掩码 |

## 性能

Raycaster 使用 GPU 加速的线性 BVH（LBVH）进行高效的射线-场景相交计算：

- 随场景复杂度扩展良好
- 可高效处理数百至数千条射线
- 在并行环境中批处理

## API 参考

```{eval-rst}
.. autoclass:: genesis.engine.sensors.RaycasterSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`camera` - 视觉传感
