# IMU 传感器

`IMUSensor`（惯性测量单元）提供用于机器人状态估计的加速度计和陀螺仪读数。

## 概述

IMU 传感器测量：

- **线加速度**：包含重力在内的 3D 加速度
- **角速度**：3D 旋转速度
- **方向**：当前方向（可选）

## 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="quadruped.urdf"))
scene.build()

# 添加 IMU 到机器人基座
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=robot.get_link("base_link"),
    )
)

# 仿真循环
for i in range(1000):
    scene.step()

    # 获取 IMU 读数
    data = imu.get_data()
    accel = data.linear_acceleration  # (3,) 加速度，单位 m/s^2
    gyro = data.angular_velocity      # (3,) 角速度，单位 rad/s
```

## 配置

```python
gs.sensors.IMU(
    link=link,                    # 附加传感器的 RigidLink
    frame="local",                # 参考坐标系："world" 或 "local"

    # 加速度计参数
    accel_noise_density=0.0,      # 噪声密度 (m/s^2/sqrt(Hz))
    accel_random_walk=0.0,        # 随机游走 (m/s^3/sqrt(Hz))
    accel_bias_correlation_time=0.0,  # 偏置相关时间 (s)

    # 陀螺仪参数
    gyro_noise_density=0.0,       # 噪声密度 (rad/s/sqrt(Hz))
    gyro_random_walk=0.0,         # 随机游走 (rad/s^2/sqrt(Hz))
    gyro_bias_correlation_time=0.0,   # 偏置相关时间 (s)
)
```

## 噪声建模

IMU 支持基于 Allan 方差参数的真实噪声建模：

### 加速度计噪声

| 参数 | 描述 | 典型值 |
|-----------|-------------|---------------|
| `accel_noise_density` | 白噪声 | 0.001-0.01 m/s^2/sqrt(Hz) |
| `accel_random_walk` | 偏置不稳定性 | 0.0001-0.001 m/s^3/sqrt(Hz) |

### 陀螺仪噪声

| 参数 | 描述 | 典型值 |
|-----------|-------------|---------------|
| `gyro_noise_density` | 白噪声 | 0.0001-0.001 rad/s/sqrt(Hz) |
| `gyro_random_walk` | 偏置不稳定性 | 0.00001-0.0001 rad/s^2/sqrt(Hz) |

## 示例：四足机器人状态估计

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
quadruped = scene.add_entity(gs.morphs.URDF(file="go2.urdf"))
scene.build()

# 添加带有真实噪声的 IMU
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=quadruped.get_link("base"),
    )
)

# 状态估计循环
velocity_estimate = np.zeros(3)
dt = scene.dt

for i in range(1000):
    scene.step()

    data = imu.get_data()

    # 简单积分（实际系统使用卡尔曼滤波）
    velocity_estimate += data.linear_acceleration * dt
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.engine.sensors.IMUSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`contact` - 接触力传感
