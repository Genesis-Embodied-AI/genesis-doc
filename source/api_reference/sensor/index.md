# Sensors

Genesis 提供多种传感器用于感知仿真状态。Sensors 附加到 entities 上，提供视觉观测、力测量和惯性读数等数据。

## 概览

可用的传感器类型：

| Sensor | 描述 | 使用场景 |
|--------|-------------|----------|
| **Camera** | 视觉观测（RGB、深度、分割） | 基于视觉的控制 |
| **ContactForceSensor** | 接触点的力/力矩 | 操作、抓取 |
| **IMUSensor** | 加速度计和陀螺仪读数 | 机器人状态估计 |
| **RaycasterSensor** | 基于射线的距离测量 | LIDAR、接近感应 |

## 快速开始

### 添加 Sensors

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# Camera sensor（通过 add_camera）
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

# 首先 build scene
scene.build()

# 在末端执行器上的接触力 sensor
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        link=robot.get_link("end_effector"),
    )
)

# IMU sensor
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=robot.get_link("base_link"),
    )
)
```

### 读取 Sensor 数据

```python
scene.step()

# Camera
rgb = cam.render(rgb=True)
depth = cam.render(depth=True)

# 接触力
force = contact_sensor.get_data()

# IMU
imu_data = imu.get_data()
acceleration = imu_data.linear_acceleration
angular_velocity = imu_data.angular_velocity
```

## Sensor 类型

```{toctree}
:titlesonly:

camera
contact
imu
raycaster
```

## 另请参阅

- {doc}`/api_reference/visualization/index` - 可视化系统
- {doc}`/api_reference/entity/index` - 向 entities 添加 sensors
