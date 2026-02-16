# 接触传感器

Genesis 提供用于检测和测量接触力的传感器。这些对于操作任务、抓取和理解物理交互至关重要。

## ContactForceSensor

`ContactForceSensor` 测量指定连杆上接触点的力和力矩。

### 用法

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))
scene.build()

# 添加接触力传感器到夹爪手指
finger = robot.get_link("finger_link")
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        link=finger,
    )
)

# 仿真循环
for i in range(1000):
    scene.step()

    # 获取接触力数据
    force_data = contact_sensor.get_data()
    print(f"Contact force: {force_data}")
```

### 配置

```python
gs.sensors.ContactForce(
    link=link,              # 附加传感器的 RigidLink
    frame="world",          # 参考坐标系："world" 或 "local"
    noise_pos=0.0,          # 位置噪声标准差
    noise_quat=0.0,         # 方向噪声标准差
)
```

## ContactSensor

`ContactSensor` 检测接触事件（碰撞开始/结束）而不测量力。

### 用法

```python
contact = scene.add_sensor(
    gs.sensors.Contact(
        link=robot.get_link("base"),
    )
)

scene.step()
contacts = contact.get_data()
```

## API 参考

### ContactForceSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactForceSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

### ContactSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 传感器概述
- {doc}`/api_reference/entity/rigid_entity/index` - RigidEntity 和连杆
