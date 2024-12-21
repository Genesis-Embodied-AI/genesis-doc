# 🧑‍💻 交互式信息访问和调试

我们设计了一个非常信息丰富（并且希望看起来也很不错）的界面，用于访问Genesis中创建的对象的内部信息和所有可用属性，这是通过为所有Genesis类实现的`__repr__()`方法实现的。如果您习惯于通过`IPython`、`pdb`或`ipdb`进行调试，这个功能将非常有用。

在这个例子中，我们使用`IPython`。如果您没有安装它，可以通过`pip install ipython`进行安装。让我们通过一个简单的例子来演示：

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

# 进入IPython的交互模式
import IPython; IPython.embed()
```

您可以直接运行这个脚本（如果您已经安装了`IPython`），或者您可以在终端中进入一个`IPython`交互窗口，并粘贴代码（不包括最后一行）。

在这段代码中，我们添加了一个平面实体和一个Franka机械臂。现在，如果您是新手，您可能会想知道场景中实际包含了什么。如果您在`IPython`（或`ipdb`、`pdb`甚至是原生的python shell）中简单地输入`scene`，您将看到场景中的所有内容，格式化并且颜色美观：

```{figure} ../../_static/images/interactive_scene.png
```

在顶部行，您将看到对象的类型（在本例中为`<gs.Scene>`）。然后，您将看到其中所有可用的属性。例如，它告诉您场景已构建（`is_built`为`True`），其时间步长（`dt`）是一个值为`0.01`秒的浮点数，其唯一ID（`uid`）是`'69be70e-dc9574f508c7a4c4de957ceb5'`。场景还有一个名为`solvers`的属性，它本质上是一个包含不同物理求解器的列表。您可以在shell中进一步输入`scene.solvers`并检查这个列表，它是使用`gs.List`类实现的，以便更好地可视化：

```{figure} ../../_static/images/interactive_solvers.png
```

您还可以检查Franka实体：

```{figure} ../../_static/images/interactive_franka.png
```

在这里，您将看到它包含的所有`geoms`和`links`及相关信息。我们可以更深入一层，输入`franka.links[0]`：

```{figure} ../../_static/images/interactive_link.png
```

在这里，您将看到所有的碰撞几何体（`geoms`）和视觉几何体（`vgeoms`）以及其他重要信息，例如其惯性质量（`intertial_mass`）、场景中的全局索引（`idx`）、所属实体（`entity`，即Franka机械臂实体）、其关节（`joint`）等。

我们希望这个信息丰富的界面可以让您的调试过程更加轻松！
