# 👋🏻 Hello, Genesis

```{figure} ../../_static/images/hello_genesis.png
```

在本教程中，我们将通过一个基本示例来演示如何加载一个Franka机械臂并让其自由落到地面上，并利用这个示例来说明在Genesis中创建模拟实验的核心步骤和一些基本概念：

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

这就是**完整的代码脚本**！这样的示例只需不到10行代码，已经包含了使用Genesis创建模拟实验所需的所有步骤。

你可以在这里停止并开始探索Genesis，但如果你有足够的耐心，让我们一起逐步了解它：

#### 初始化

第一步是导入Genesis并初始化它：

```
import genesis as gs
gs.init(backend=gs.cpu)
```

- **后端设备**：Genesis设计为跨平台，支持各种后端设备。这里我们使用`gs.cpu`。如果需要GPU加速的[并行模拟](parallel_simulation.md)，可以切换到其他后端，如`gs.cuda`、`gs.vulkan`或`gs.metal`。你也可以使用`gs.gpu`作为快捷方式，Genesis会根据你的系统选择一个后端（例如，如果CUDA可用，则选择`gs.cuda`，对于Apple Silicon设备则选择`gs.metal`）。
- **精度级别**：默认情况下，Genesis使用f32精度。如果需要更高的精度，可以通过设置`precision='64'`来更改为f64。
- **日志级别**：一旦Genesis初始化，你将在终端上看到详细的系统信息和Genesis相关信息，如当前版本。你可以通过将`logging_level`设置为`'warning'`来抑制日志输出。
- **配色方案**：Genesis日志的默认配色方案优化为深色背景终端，即`theme='dark'`。如果你使用浅色背景的终端，可以更改为`'light'`，或者如果你喜欢黑白配色，可以使用`'dumb'`。

一个更详细的`gs.init()`调用示例如下：

```python
gs.init(
    seed                = None,
    precision           = '32',
    debug               = False,
    eps                 = 1e-12,
    logging_level       = None,
    backend             = gs_backend.gpu,
    theme               = 'dark',
    logger_verbose_time = False
)
```

#### 创建场景

Genesis中的所有对象、机器人、摄像机等都放置在一个Genesis `Scene`中：

```python
scene = gs.Scene()
```

一个场景包含一个`simulator`对象，处理所有底层物理求解器，以及一个`visualizer`对象，管理与可视化相关的概念。有关更多详细信息和API，请参见[`Scene`](../../api_reference/scene/scene.md)。

创建场景时，可以配置各种物理求解器参数。一个稍微复杂的示例如下：

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

此示例将模拟的`dt`设置为每步0.01秒，配置重力，并设置交互式查看器的初始摄像机姿态。

#### 将对象加载到场景中

在此示例中，我们将一个平面和一个Franka机械臂加载到场景中：

```python
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
```

在Genesis中，所有对象和机器人都表示为[`Entity`](../../api_reference/entity/index.md)。Genesis设计为完全面向对象，因此你可以直接通过这些实体对象的方法与它们交互，而不是使用句柄或分配给它们的全局ID。
`add_entity`的第一个参数是[`morph`](../../api_reference/options/morph/index.md)。Genesis中的morph是一个混合概念，封装了实体的几何和姿态信息。通过使用不同的morph，你可以从形状原语、网格、URDF、MJCF、地形或软体机器人描述文件中实例化Genesis实体。

创建morph时，还可以指定其位置、方向、大小等。对于方向，morph接受`euler`（scipy外旋x-y-z惯例）或`quat`（w-x-y-z惯例）。一个示例如下：

```python
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml'
        pos   = (0, 0, 0),
        euler = (0, 0, 90), # 我们遵循scipy的外旋x-y-z旋转惯例，以度为单位,
        # quat  = (1.0, 0.0, 0.0, 0.0), # 我们使用w-x-y-z惯例表示四元数,
        scale = 1.0,
    ),
)
```

我们目前支持不同类型的形状原语，包括：

- `gs.morphs.Plane`
- `gs.morphs.Box`
- `gs.morphs.Cylinder`
- `gs.morphs.Sphere`

此外，对于训练运动任务，我们支持各种类型的内置地形以及通过`gs.morphs.Terrain`从用户提供的高度图初始化的地形，我们将在后续教程中介绍。

我们支持从不同格式的外部文件加载：

- `gs.morphs.MJCF`：mujoco `.xml`机器人配置文件
- `gs.morphs.URDF`：以`.urdf`（统一机器人描述格式）结尾的机器人描述文件
- `gs.morphs.Mesh`：非关节网格资产，支持的扩展名包括：`*.obj`、`*.ply`、`*.stl`、`*.glb`、`*.gltf`

从外部文件加载时，需要使用`file`参数指定文件位置。解析时，我们支持*绝对*和*相对*文件路径。请注意，由于Genesis还带有一个内部资产目录（`genesis/assets`），因此如果使用相对路径，我们不仅会相对于当前工作目录搜索相对路径，还会在`genesis/assets`下搜索。因此，在此示例中，我们将从`genesis/assets/xml/franka_emika_panda/panda.xml`检索Franka模型。

:::{note}
在Genesis开发过程中，我们尽可能支持多种文件扩展名，包括支持加载其关联的纹理以进行渲染。如果你希望我们支持上述未列出的其他文件类型，或者发现纹理未正确加载或渲染，请随时提交功能请求！
:::

如果你想使用外部**URDF**文件加载Franka机械臂，只需将morph更改为`gs.morphs.URDF(file='urdf/panda_bullet/panda.urdf', fixed=True)`。请注意，与MJCF文件已经指定了连接机器人基座链接和`world`的关节类型不同，URDF文件不包含此信息。因此，默认情况下，URDF机器人树的基座链接与`world`断开连接（更准确地说，通过一个`free` 6自由度关节连接到`world`）。因此，如果希望基座链接固定，需要额外指定`fixed=True`。

#### 构建场景并开始模拟

```Python
scene.build()
for i in range(1000):
    scene.step()
```

现在一切都已添加，我们可以开始模拟。请注意，我们现在需要先***构建***场景，调用`scene.build()`。这是因为Genesis使用即时（JIT）技术为每次运行动态编译GPU内核，因此我们需要一个显式步骤来启动此过程，将所有内容放置到位，分配设备内存，并创建用于模拟的底层数据字段。

一旦场景构建完成，将弹出一个交互式查看器以可视化场景。查看器带有各种键盘快捷键，用于视频录制、截图、切换不同的可视化模式等。我们将在本教程后面讨论更多关于可视化的细节。

:::{note}
**内核编译和缓存**

由于JIT的特性，每次创建具有新配置的场景（即不同的机器人类型，不同数量的对象等涉及内部数据结构大小变化），Genesis需要动态重新编译GPU内核。Genesis支持已编译内核的自动缓存：在第一次运行后（只要正常退出或通过`ctrl + c`终止，**不是**`ctrl + \`），如果场景配置保持不变，我们将从以前运行的缓存内核加载，以加快场景创建过程。

我们正在积极优化此编译步骤，通过添加并行编译和更快的内核序列化等技术，因此我们预计在未来版本中大大加快此步骤的速度。
:::

现在我们已经走过了整个示例。接下来，让我们深入了解Genesis的可视化系统，玩转查看器并添加一些摄像机。
