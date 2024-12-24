# 🧑‍💻 交互式信息访问和调试

Genesis为所有类都实现了`__repr__()`方法,提供了一个信息丰富且美观的界面,让你能方便地访问Genesis中创建的对象的内部信息和所有属性。如果你使用`IPython`、`pdb`或`ipdb`进行调试,这个功能会很有帮助。

这个例子使用`IPython`演示。如果没安装,可以用`pip install ipython`安装。看下面的示例:

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

# 进入IPython交互模式
import IPython; IPython.embed()
```

你可以直接运行这个脚本(如果已安装`IPython`),或者在终端打开`IPython`交互窗口,粘贴代码(不包括最后一行)。

这段代码添加了一个平面和一个Franka机器人。如果你想看场景里有什么,在`IPython`(或`ipdb`、`pdb`甚至Python原生shell)里输入`scene`,就能看到场景中所有内容,格式化显示并带有颜色:

```{figure} ../../_static/images/interactive_scene.png
```

顶部显示对象类型(`<gs.Scene>`)。下面是所有可用属性。比如,场景已构建(`is_built`为`True`),时间步长(`dt`)是`0.01`秒,唯一ID(`uid`)是`'69be70e-dc9574f508c7a4c4de957ceb5'`。场景还有个`solvers`属性,是个包含不同物理求解器的列表。在shell中输入`scene.solvers`可以查看这个列表,它用`gs.List`类实现,方便查看:

```{figure} ../../_static/images/interactive_solvers.png
```

也可以查看Franka实体:

```{figure} ../../_static/images/interactive_franka.png
```

这里能看到所有的`geoms`和`links`及相关信息。输入`franka.links[0]`可以看更多细节:

```{figure} ../../_static/images/interactive_link.png
```

这里显示了所有碰撞几何体(`geoms`)、视觉几何体(`vgeoms`)和其他重要信息,比如惯性质量(`intertial_mass`)、场景中的全局索引(`idx`)、所属实体(`entity`即Franka机器人)、关节(`joint`)等。

这个信息丰富的界面能让你更容易地调试!
