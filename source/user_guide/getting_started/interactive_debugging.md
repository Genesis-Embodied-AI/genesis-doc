# 🧑‍💻 交互式信息访问与调试

我们设计了一个信息丰富（希望也很美观）的界面，用于访问内部信息和 Genesis 中创建的所有对象的可用属性，通过所有 Genesis 类的 `__repr__()` 方法实现。如果您习惯使用 `IPython`、`pdb` 或 `ipdb` 进行调试，这个功能将非常有用。

在本例中使用 `IPython`。如果没有安装，请通过 `pip install ipython` 安装。这里让我们通过一个简单的例子来说明：
```python
import genesis as gs

gs.init()

scene = gs.Scene(show_viewer=False)

plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

cam_0 = scene.add_camera()
scene.build()

# 进入 IPython 交互模式
import IPython; IPython.embed()
```

您可以直接运行此脚本（如果已安装 `IPython`），或者在终端中进入 `IPython` 交互窗口并粘贴这里的代码（不包括最后一行）。

在这个小块代码中，我们添加了一个平面实体和一个 Franka 机械臂。现在，如果您是新手，可能会想知道场景实际包含什么。如果您在 `IPython` 中（或 `ipdb` 或 `pdb` 甚至原生 python shell）简单地输入 `scene`，您将看到场景中的所有内容，格式化并着色得很好：

```{figure} ../../_static/images/interactive_scene.png
```

在顶行，您将看到对象的类型（此处为 `<gs.Scene>`）。然后您将看到其中所有可用的属性。例如，它告诉您场景已构建（`is_built` 为 `True`），其时间步长（`dt`）为值 `0.01` 秒的浮点数，其唯一 id（`uid`）为 `'69be70e-dc9574f508c7a4c4de957ceb5'`。场景还有一个名为 `solvers` 的属性，本质上是它所拥有的不同物理求解器的列表。您可以在 shell 中进一步输入 `scene.solvers` 并检查此列表，它使用 `gs.List` 类实现以获得更好的可视化效果：

```{figure} ../../_static/images/interactive_solvers.png
```

您还可以检查 Franka 实体：

```{figure} ../../_static/images/interactive_franka.png
```
这里您将看到它所有的 `geoms` 和 `links` 以及相关信息。我们可以再深入一层，输入 `franka.links[0]`：


```{figure} ../../_static/images/interactive_link.png
```
在这里，您将看到 link 中包含的所有碰撞几何体（`geoms`）和视觉几何体（`vgeoms`），以及其他重要信息，例如其 `intertial_mass`、link 在场景中的全局索引（`idx`）、它属于哪个实体（`entity`，即 franka 机械臂实体）、其关节（`joint`）等。

我们希望这个信息丰富的界面能让您的调试过程更轻松！
