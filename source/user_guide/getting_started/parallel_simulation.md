# 🚀 并行仿真

```{figure} ../../_static/images/parallel_sim.png
```

使用 GPU 加速仿真的最大优势是能够实现场景级并行，从而可以在数千个环境中同时训练机器人。

在 Genesis 中，创建并行仿真就像你想象的那么简单：构建场景时，你只需添加一个额外的参数 `n_envs` 来告诉仿真器你想要多少个环境。就是这样。

注意，为了模仿学习文献中的命名约定，我们也将使用术语 `batching` 来表示并行化操作。

示例脚本：
```python
import genesis as gs
import torch

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
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

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## build ##########################

# 创建 20 个并行环境
B = 20
scene.build(n_envs=B, env_spacing=(1.0, 1.0))

# 控制所有机器人
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 1.0, 0, 0.02, 0.02], device=gs.device), (B, 1)
    ),
)

for i in range(1000):
    scene.step()
```

上述脚本与你在[你好，Genesis](hello_genesis.md)中看到的示例几乎相同，只是 `scene.build()` 现在附加了两个额外的参数：
- `n_envs`：这指定了你想要创建的批量环境的数量
- `env_spacing`：生成的并行环境共享相同的状态。为了可视化目的，你可以指定此参数要求可视化器以网格形式分布所有环境，每个环境之间的距离为 (x, y) 米。注意这只影响可视化行为，不会改变每个环境中实体的实际位置。

### 控制批量环境中的机器人
回想一下，我们在前面的教程中使用了 `franka.control_dofs_position()` 等 API。现在你可以使用完全相同的 API 来控制批量机器人，只是输入变量需要一个额外的批处理维度：
```python
franka.control_dofs_position(torch.zeros(B, 9, device=gs.device))
```
由于我们在 GPU 上运行仿真，为了减少 CPU 和 GPU 之间的数据传输开销，我们可以使用通过 `gs.device` 选择的 torch 张量而不是 numpy 数组（但 numpy 数组也可以）。当你需要频繁发送具有巨大批量大小的张量时，这可以带来明显的性能提升。

上述调用将控制批量环境中的所有机器人。如果你只想控制一部分环境，你可以额外传入 `envs_idx`，但要确保 `position` 张量的批处理维度大小与 `envs_idx` 的长度匹配：
```python
# 仅控制 3 个环境：1、5 和 7
franka.control_dofs_position(
    position = torch.zeros(3, 9, device=gs.device),
    envs_idx = torch.tensor([1, 5, 7], device=gs.device),
)
```
此调用只会向 3 个选定的环境发送零位置命令。

### 享受未来的速度！
Genesis 支持多达数万个并行环境，并以此来解锁前所未有的仿真速度。现在，让我们关闭查看器，将批量大小更改为 30000（如果你的 GPU 显存相对较小，请考虑使用较小的值）：

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
        torch.tensor([0, 0, 0, -1.0, 0, 1.0, 0, 0.02, 0.02], device=gs.device), (30000, 1)
    ),
)

for i in range(1000):
    scene.step()
```

在配备 RTX 4090 和 14900K 的台式机上运行上述脚本，你会获得未来感的仿真速度——超过**4300 万**帧每秒，这比实时快 430,000 倍。尽情享受吧！
```{figure} ../../_static/images/parallel_speed.png
```

:::{tip}
**FPS 日志记录：** 默认情况下，Genesis 日志记录器会在终端中显示实时仿真速度。你可以在创建场景时通过设置 `scene.profiling_options.show_FPS=False` 来禁用此行为。
:::
