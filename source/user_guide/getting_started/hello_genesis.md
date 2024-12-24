# 👋🏻 Hello, Genesis

```{figure} ../../_static/images/hello_genesis.png
```

本教程通过演示一个简单例子 - 加载Franka机械臂并让其自由落下,介绍如何在Genesis中创建模拟实验的核心步骤和基本概念:

```python
import genesis as gs
gs.init(backend=gs.cpu)

scene = gs.Scene(show_viewer=True)
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

scene.build()

for i in range(1000):
    scene.step()
```

上面就是完整代码了！不到10行代码就完成了所有Genesis模拟实验的必需步骤。

你现在可以开始探索Genesis,或者继续阅读下文详细了解每个步骤:

## 初始化

首先导入Genesis并初始化:

```python
import genesis as gs
gs.init(backend=gs.cpu)
```

- **后端**: Genesis支持多平台,这里用`gs.cpu`。想用GPU做[并行模拟](parallel_simulation.md)可以换成`gs.cuda`、`gs.vulkan`或`gs.metal`。也可以用`gs.gpu`,让Genesis根据系统自动选择后端(有CUDA用CUDA,苹果芯片用Metal)。
- **精度**: 默认f32精度,通过`precision='64'`可改为f64。
- **日志**: 初始化时会显示系统信息和版本,`logging_level='warning'`可减少日志输出。
- **主题**: 日志默认深色主题`theme='dark'`,可改为`'light'`或黑白的`'dumb'`。

完整初始化参数示例:

```python
gs.init(
    seed = None,
    precision = '32',
    debug = False,
    eps = 1e-12,
    logging_level = None,
    backend = gs_backend.gpu,
    theme = 'dark',
    logger_verbose_time = False
)
```

## 创建场景

所有对象、机器人和摄像机都放在Genesis `Scene`中:

```python
scene = gs.Scene()
```

场景包含`simulator`物理引擎和`visualizer`可视化组件。详见[`Scene`](../../api_reference/scene/scene.md)。

创建场景时可以配置物理参数,示例:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        gravity=(0, 0, -10.0),
    ),
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
)
```

这设置了模拟步长、重力和初始相机位置等。

## 添加对象

加载一个平面和Franka机械臂:

```python
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
```

Genesis中所有对象都是[`Entity`](../../api_reference/entity/index.md),可直接调用其方法操作,不需要ID。
`add_entity`的第一个参数是[`morph`](../../api_reference/options/morph/index.md),定义了实体的几何和姿态。morph支持从原始形状、网格、URDF、MJCF等创建实体。

创建morph时可指定位置、方向、大小等。方向可用`euler`(scipy外旋x-y-z)或`quat`(w-x-y-z),示例:

```python
franka = scene.add_entity(
    gs.morphs.MJCF(
        file = 'xml/franka_emika_panda/panda.xml'
        pos = (0, 0, 0),
        euler = (0, 0, 90), # scipy外旋x-y-z,单位度
        # quat = (1.0, 0.0, 0.0, 0.0), # w-x-y-z四元数
        scale = 1.0,
    ),
)
```

支持的形状包括:

- `gs.morphs.Plane`
- `gs.morphs.Box`
- `gs.morphs.Cylinder`
- `gs.morphs.Sphere`

还可从文件加载:

- `gs.morphs.MJCF`: mujoco .xml文件
- `gs.morphs.URDF`: .urdf文件
- `gs.morphs.Mesh`: 支持.obj、.ply、.stl、.glb、.gltf等网格

文件路径可以是绝对或相对路径,也会在`genesis/assets`目录下查找。本例中Franka模型从`genesis/assets/xml/franka_emika_panda/panda.xml`加载。

:::{note}
如果需要支持其他文件格式或发现纹理问题,欢迎提需求!
:::

用URDF加载Franka只需改为`gs.morphs.URDF(file='urdf/panda_bullet/panda.urdf', fixed=True)`。URDF默认基座通过6自由度关节连world,`fixed=True`可固定基座。

## 构建并模拟

```python
scene.build()
for i in range(1000):
    scene.step()
```

添加完对象后,需要先调用`scene.build()`。这是因为Genesis用JIT为每次运行编译GPU内核,需要这步来分配内存并创建数据。

构建完成后会打开查看器显示场景。查看器有快捷键可录像、截图、切换显示模式等。

:::{note}
**内核编译和缓存**

每次用新配置创建场景都需重新编译GPU内核。Genesis会自动缓存编译结果:第一次运行后(正常退出或ctrl+c,不是ctrl+\\),如果配置不变就直接用缓存。

我们正在优化编译速度,将来版本会快很多。
:::

至此完成了整个示例,接下来看看Genesis的可视化系统。
