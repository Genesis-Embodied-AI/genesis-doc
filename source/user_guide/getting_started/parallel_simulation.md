# 🚀 并行仿真

```{figure} ../../_static/images/parallel_sim.png
```

GPU加速仿真的最大优势是能实现场景级别的并行性，让我们可以同时在成千上万个环境中训练机器人。

Genesis中创建并行仿真很简单:构建场景时只需添加参数`n_envs`来指定想要多少个环境就行了。为了跟随模仿学习文献的命名习惯,我们也用术语`batching`来表示并行操作。

下面是示例代码:

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

这个代码和[Hello, Genesis](hello_genesis.md)中的示例基本一样,只是`scene.build()`多了两个参数:

- `n_envs`: 指定要创建的并行环境数量
- `env_spacing`: 由于所有并行环境共享同样的状态,这个参数用来指定可视化时把环境放在网格中的间距(x和y方向的距离,单位:米)。这只影响显示效果,不会改变环境中实体的实际位置。

## 控制批量环境中的机器人

之前教程中用过的API比如`franka.control_dofs_position()`仍然可以用来控制批量机器人,只需输入变量增加一个批量维度就行:

```python
franka.control_dofs_position(torch.zeros(B, 9, device=gs.device))
```

因为我们在GPU上运行仿真,为了减少CPU和GPU间的数据传输,建议用`gs.device`指定的torch张量而不是numpy数组(不过numpy数组也能用)。当经常要传输大批量的张量时,这样能明显提升性能。

上面的调用会控制所有环境中的机器人。如果只想控制部分环境,可以额外传入`envs_idx`,但要确保`position`张量的批量维度和`envs_idx`长度一致:

```python
# 只控制3个环境:1、5和7
franka.control_dofs_position(
    position = torch.zeros(3, 9, device=gs.device),
    envs_idx = torch.tensor([1, 5, 7], device=gs.device),
)
```

这样只会向这3个选定的环境发送零位置命令。

## 享受超快的仿真速度

Genesis支持同时运行数万个环境,带来惊人的仿真速度。下面关闭可视化,把批量改成30000(如果GPU显存不够就用小一点的数):

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

在RTX 4090和14900K的台式机上运行这个程序能达到每秒**4300万**帧,比实时快430,000倍,真是太快了!

```{figure} ../../_static/images/parallel_speed.png
```

:::{tip}
**FPS显示:** Genesis默认会在终端显示实时仿真速度。创建场景时设置`show_FPS=False`可以关闭这个功能。
:::
