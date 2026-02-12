# 👋🏻 你好，Genesis

```{figure} ../../_static/images/hello_genesis.png
```
在本教程中，我们将通过一个基本示例来演示：加载单个 Franka 机械臂，让它自由落到地板上，并使用这个示例来说明在 Genesis 中创建仿真实验的核心步骤以及一些基本概念：

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
这是**完整的代码脚本**！这样一个示例仅需不到 10 行代码，就已经包含了使用 Genesis 创建仿真实验所需的全部必要步骤。

如果你愿意，现在就可以停止阅读，开始探索 Genesis。但如果你有足够的耐心，让我们一起一步一步地了解它：

#### 初始化
第一步是导入 Genesis 并初始化它：
```
import genesis as gs
gs.init(backend=gs.cpu)
```
- **后端设备（Backend device）**：Genesis 设计为跨平台，支持各种后端设备。这里我们使用 `gs.cpu`。如果你需要 GPU 加速的[并行仿真](parallel_simulation.md)，可以切换到其他后端，如 `gs.cuda`、`gs.vulkan` 或 `gs.metal`。你也可以使用 `gs.gpu` 作为快捷方式，Genesis 会根据你的系统选择合适的后端（例如，如果有 CUDA 可用则选择 `gs.cuda`，对于 Apple Silicon 设备则选择 `gs.metal`）。
- **精度级别（Precision level）**：默认情况下，Genesis 使用 f32 精度。如果需要更高的精度，可以通过设置 `precision='64'` 切换到 f64。
- **日志级别（Logging level）**：Genesis 初始化后，你会在终端看到日志输出，详细说明系统信息和 Genesis 相关信息，如当前版本。你可以通过将 `logging_level` 设置为 `'warning'` 来抑制日志输出。
- **配色方案（Color scheme）**：Genesis 日志使用的默认配色主题针对深色背景终端进行了优化，即 `theme='dark'`。如果你使用的是浅色背景的终端，可以切换到 `'light'`，或者如果你只喜欢黑白配色，可以直接使用 `'dumb'`。

一个更详细的 `gs.init()` 调用示例如下：
```python
gs.init(
    seed                = None,
    precision           = '32',
    debug               = False,
    eps                 = 1e-12,
    logging_level       = None,
    backend             = gs.gpu,
    theme               = 'dark',
    logger_verbose_time = False
)
```

#### 创建场景
Genesis 中的所有对象、机器人、相机等都放置在一个 Genesis `Scene` 中：
```python
scene = gs.Scene()
```
一个场景包装了一个 `simulator` 对象，它处理所有底层的物理求解器，以及一个 `visualizer` 对象，它管理与可视化相关的概念。有关更多详细信息和 API，请参阅 [`Scene`](../../api_reference/scene/scene.md)。

创建场景时，你可以配置各种物理求解器参数。一个稍微复杂一点的例子是：
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
这个示例将仿真 `dt` 设置为每步 0.01 秒，配置了重力，并为交互式查看器设置了初始相机姿态。


#### 将对象加载到场景中
在这个示例中，我们将一个平面和一个 Franka 机械臂加载到场景中：
```python
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
```
在 Genesis 中，所有对象和机器人都表示为 [`Entity`](../../api_reference/entity/index.md)。Genesis 设计为完全面向对象，因此你可以直接通过这些实体对象的方法与它们交互，而不是使用分配给它们的句柄或全局 ID。
`add_entity` 的第一个参数是 [`morph`](../../api_reference/options/morph/index.md)。在 Genesis 中，morph 是一个混合概念，封装了实体的几何和姿态信息。通过使用不同的 morph，你可以从形状基元、网格、URDF、MJCF、地形或软体机器人描述文件实例化 Genesis 实体。

创建 morph 时，你可以额外指定其位置、方向、大小等。对于方向，morph 接受 `euler`（scipy 外旋 x-y-z 约定）或 `quat`（w-x-y-z 约定）。一个示例是：
```python
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (0, 0, 0),
        euler = (0, 0, 90), # 我们遵循 scipy 的外旋 x-y-z 旋转约定，以度为单位
        # quat  = (1.0, 0.0, 0.0, 0.0), # 我们使用 w-x-y-z 约定表示四元数
        scale = 1.0,
    ),
)
```

我们目前支持不同类型的形状基元，包括：
- `gs.morphs.Plane`
- `gs.morphs.Box`
- `gs.morphs.Cylinder`
- `gs.morphs.Sphere`

此外，对于训练运动任务，我们还支持各种内置地形以及通过 `gs.morphs.Terrain` 从用户给定的高度图初始化的地形，这将在后面的教程中介绍。

我们支持从不同格式的外部文件加载，包括：
- `gs.morphs.MJCF`：Mujoco `.xml` 机器人配置文件
- `gs.morphs.URDF`：以 `.urdf` 结尾的机器人描述文件（统一机器人描述格式）
- `gs.morphs.USD`：通用场景描述文件（`.usd`, `.usda`, `.usdc`, `.usdz`），用于加载包含关节机器人和刚体的复杂场景。详细信息请参阅 [USD 导入教程](usd_import.md)。
- `gs.morphs.Mesh`：非关节网格资产，支持的扩展名包括：`*.obj`, `*.ply`, `*.stl`, `*.glb`, `*.gltf`


从外部文件加载时，你需要使用 `file` 参数指定文件位置。在解析时，我们支持*绝对*和*相对*文件路径。注意，由于 Genesis 还带有一个内部资产目录（`genesis/assets`），如果使用相对路径，我们不仅会搜索相对于当前工作目录的路径，还会在 `genesis/assets` 下搜索。因此，在这个示例中，我们将从以下位置获取 Franka 模型：`genesis/assets/xml/franka_emika_panda/panda.xml`。

:::{note}
在 Genesis 的开发过程中，我们尝试支持尽可能多的文件扩展名，包括支持加载它们关联的纹理以进行渲染。如果你希望我们支持上面未列出的任何其他文件类型，或者发现你的纹理未正确加载或渲染，请随时提交功能请求！
:::

如果你想使用外部 **URDF** 文件加载 Franka 机械臂，只需将 morph 更改为 `gs.morphs.URDF(file='urdf/panda_bullet/panda.urdf', fixed=True)`。注意，与 MJCF 文件已经指定了机器人基座连杆与 `world` 之间的关节类型不同，URDF 文件不包含此信息。因此，默认情况下，URDF 机器人树的基座连杆与 `world` 断开连接（或者更准确地说，通过 `free` 6 自由度关节与 `world` 连接）。因此，如果我们希望基座连杆固定，需要额外为 `morphs.URDF` 和 `morphs.Mesh` 指定 `fixed=True`。


#### 构建场景并开始仿真
```Python
scene.build()
for i in range(1000):
    scene.step()
```
现在一切都已添加完毕，我们可以开始仿真了。注意，我们现在需要先调用 `scene.build()` 来***构建***场景。这是因为 Genesis 使用即时（JIT）技术为每次运行动态编译 GPU 内核，因此我们需要一个显式的步骤来启动这个过程，将一切放置到位、分配设备内存并为仿真创建底层数据字段。

场景构建后，一个交互式查看器将弹出以可视化场景。查看器带有各种键盘快捷键，用于视频录制、截图、在不同可视化模式之间切换等。我们将在本教程后面讨论更多关于可视化的细节。


:::{note}
**内核编译和缓存**

由于 JIT 的特性，每次创建具有新配置的场景时（即不同的机器人类型、不同数量的对象等涉及内部数据结构大小变化的情况），Genesis 需要动态重新编译 GPU 内核。Genesis 支持自动缓存编译的内核：在第一次运行后（只要正常退出或通过 `ctrl + c` 终止，**不是** `ctrl + \`），如果场景配置保持不变，我们将从先前运行的缓存内核中加载，以加快场景创建过程。

我们正在积极通过添加并行编译和更快的内核序列化等技术来优化这个编译步骤，因此我们期望在未来版本中大大加快这一步骤的速度。
:::


现在我们已经了解了整个示例。接下来，让我们深入了解 Genesis 的可视化系统，玩玩查看器并添加一些相机。
