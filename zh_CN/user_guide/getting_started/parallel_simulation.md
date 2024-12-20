# 🚀 并行仿真

```{figure} ../../_static/images/parallel_sim.png
```

使用GPU加速仿真的最大优势是能够实现场景级别的并行性，这样我们可以在成千上万个环境中同时训练机器人。

在Genesis中，创建并行仿真非常简单：在构建场景时，只需添加一个额外的参数`n_envs`来告诉模拟器你想要多少个环境。就是这么简单。

请注意，为了模仿学习文献中的命名约定，我们也会使用术语`batching`来表示并行化操作。

示例脚本：

```python
import genesis as gs
import torch

########################## 初始化 ##########################
gs.init(backend=gs.gpu)

########################## 创建场景 ##########################
scene = gs.Scene(
    show_viewer    = True,
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (3.5, -1.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
    ),
    rigid_options = gs.options.RigidOptions(
        dt                = 0.01,
    ),
)

########################## 实体 ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## 构建 ##########################

# 创建20个并行环境
B = 20
scene.build(n_envs=B, env_spacing=(1.0, 1.0))

# 控制所有机器人
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 0, 0, 0.02, 0.02], device=gs.device), (B, 1)
    ),
)

for i in range(1000):
    scene.step()
```

上述脚本与[Hello, Genesis](hello_genesis.md)中的示例几乎相同，只是`scene.build()`现在附加了两个额外的参数：

- `n_envs`：指定你想要创建的批量环境数量
- `env_spacing`：生成的并行环境共享相同的状态。为了可视化目的，你可以指定此参数，要求可视化工具将所有环境以(x, y)米的距离分布在网格中。请注意，这只影响可视化行为，并不会改变每个环境中实体的实际位置。

### 控制批量环境中的机器人

回想一下我们在之前的教程中使用的API，例如`franka.control_dofs_position()`。现在你可以使用完全相同的API来控制批量机器人，只是输入变量需要一个额外的批量维度：

```python
franka.control_dofs_position(torch.zeros(B, 9, device=gs.device))
```

由于我们在GPU上运行仿真，为了减少CPU和GPU之间的数据传输开销，我们可以使用通过`gs.device`选择的torch张量而不是numpy数组（但numpy数组也可以工作）。当你需要频繁发送一个具有巨大批量大小的张量时，这可以带来显著的性能提升。

上述调用将控制批量环境中的所有机器人。如果你只想控制某些环境，可以另外传入`envs_idx`，但请确保`position`张量的批量维度大小与`envs_idx`的长度匹配：

```python
# 只控制3个环境：1, 5和7。
franka.control_dofs_position(
    position = torch.zeros(3, 9, device=gs.device),
    envs_idx = torch.tensor([1, 5, 7], device=gs.device),
)
```

此调用将仅向3个选定的环境发送零位置命令。

### 享受未来的速度

Genesis支持多达数万个并行环境，并以这种方式解锁前所未有的仿真速度。现在，让我们关闭查看器，并将批量大小更改为30000（如果你的GPU显存较小，请考虑使用较小的批量大小）：

```python
import torch
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(
    show_viewer   = False,
    rigid_options = gs.options.RigidOptions(
        dt                = 0.01,
    ),
)

plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

scene.build(n_envs=30000)

# 控制所有机器人
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 0, 0, 0.02, 0.02], device=gs.device), (30000, 1)
    ),
)

for i in range(1000):
    scene.step()
```

在配备RTX 4090和14900K的桌面上运行上述脚本可以实现未来的仿真速度——每秒超过**4300万**帧，这比实时快430,000倍。享受吧！

```{figure} ../../_static/images/parallel_speed.png
```

:::{tip}
**FPS日志记录：** 默认情况下，Genesis记录器将在终端显示实时仿真速度。你可以在创建场景时设置`show_FPS=False`来禁用此行为。
:::
