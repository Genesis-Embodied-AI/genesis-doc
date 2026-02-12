# 📦 加载 USD 场景

Genesis 支持从 Universal Scene Description (USD) 文件加载复杂场景，使你能够导入具有正确物理属性和关节配置的铰接机器人、刚体对象和完整环境。USD 是由 Pixar 开发的开源框架，用于在 3D 世界中进行描述、合成、模拟和协作。

本教程将指导你在 Genesis 中加载 USD 文件、配置解析选项以及使用基于 USD 的场景。该解析器设计为与从 NVIDIA Isaac Sim 等流行工具导出的资源无缝协作，同时支持标准 USD 物理模式。

## 安装

要将 USD 资源加载到 Genesis 场景中，请安装所需的依赖项：

```bash
pip install -e .[usd]
```

### 可选：USD 材质烘焙

对于超越 `UsdPreviewSurface` 的高级材质解析，你可以选择性安装 Omniverse Kit 进行 USD 材质烘焙。此功能仅适用于 Python 3.10 和 3.11 以及 GPU 后端。（对于 Python 3.12，场景中大部分材质可能成功烘焙，但有些会保持未烘焙状态。）

```bash
pip install --extra-index-url https://pypi.nvidia.com/ omniverse-kit
export OMNI_KIT_ACCEPT_EULA=yes
```

**注意：** 必须设置 `OMNI_KIT_ACCEPT_EULA` 环境变量以接受 EULA。这是一次性操作。一旦设置，将不会再次提示。如果禁用 USD 烘焙，Genesis 将仅解析 `UsdPreviewSurface` 类型的材质。

如果你遇到 Genesis 警告 "Baking process failed: ..."，以下是一些故障排除提示：

- **EULA 接受**：首次启动可能需要接受 Omniverse EULA。在运行时接受或设置 `OMNI_KIT_ACCEPT_EULA=yes` 自动接受。

- **IOMMU 警告**：首次启动时可能会弹出显示 "IOMMU Enabled" 警告的窗口。及时点击 "OK" 以避免超时。

- **初始安装**：首次启动可能会安装额外的依赖项，这可能导致超时。安装完成后再次运行你的程序；后续运行将不需要安装。

- **多个 Python 环境**：如果你有多个 Python 环境（特别是不同 Python 版本），Omniverse Kit 扩展可能会跨环境冲突。删除共享的 Omniverse 扩展文件夹（例如 Linux 上的 `~/.local/share/ov/data/ext`）然后重试。

## 概述

Genesis 的 USD 解析器支持以下功能：

### 关节类型

- **旋转关节** (`UsdPhysics.RevoluteJoint`)：具有角度限制的旋转关节
- **滑动关节** (`UsdPhysics.PrismaticJoint`)：具有距离限制的线性/滑动关节
- **球形关节** (`UsdPhysics.SphericalJoint`)：具有 3 个旋转自由度的球关节
- **固定关节** (`UsdPhysics.FixedJoint`)：连杆之间的刚性连接
- **自由关节** (`UsdPhysics.Joint`，类型为 "PhysicsJoint")：具有完整平移和旋转自由度的 6-DOF 关节

### 物理属性

- **关节限制**（下限/上限）：支持旋转和滑动关节
- **关节摩擦** (`dofs_frictionloss`)：支持旋转、滑动和球形关节
- **关节惯量** (`dofs_armature`)：支持旋转、滑动和球形关节
- **关节刚度** (`dofs_stiffness`)：支持旋转和滑动关节的被动属性
- **关节阻尼** (`dofs_damping`)：支持旋转和滑动关节的被动属性
- **驱动 API** (`dofs_kp`, `dofs_kv`, `dofs_force_range`)：支持旋转、滑动和球形关节的 PD 控制参数

### 几何体

- **视觉几何体**：从匹配视觉模式的 USD 几何体 prim 解析
- **碰撞几何体**：从匹配碰撞模式的 USD 几何体 prim 解析

### 材质与渲染

- **UsdPreviewSurface**：完全支持漫反射颜色、不透明度、金属度、粗糙度、自发光、法线贴图和 IOR
- **材质烘焙**：通过 Omniverse Kit 可选支持超越 **UsdPreviewSurface** 的复杂材质
- **显示颜色**：当材质不可用时回退到 `displayColor`

## 基本示例

让我们从一个简单的示例开始，加载包含铰接对象的 USD 文件：

```python
import genesis as gs
from huggingface_hub import snapshot_download

# 初始化 Genesis
gs.init(backend=gs.cpu)

# 创建场景
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    show_viewer=True,
)

# 下载 USD 资源（Genesis 资源的示例）
asset_path = snapshot_download(
    repo_type="dataset",
    repo_id="Genesis-Intelligence/assets",
    revision="c50bfe3e354e105b221ef4eb9a79504650709dd2",
    allow_patterns="usd/Refrigerator055/*",
    max_workers=1,
)

# 加载 USD stage
entities = scene.add_stage(
    morph=gs.morphs.USD(
        file=f"{asset_path}/usd/Refrigerator055/Refrigerator055.usd",
    ),
)

# 构建并模拟
scene.build()
```

USD 文件可以在单个文件中包含多个刚体实体（关节体和刚体）。Genesis 提供两种加载 USD 的方法：

- **`scene.add_stage()`**：自动发现并加载 USD 文件中的**所有**刚体实体。这是加载具有多个实体的完整 USD 场景的推荐方法。

- **`scene.add_entity()`**：从 USD 文件加载**单个**实体。如果未指定 `prim_path`，则使用 USD stage 的默认 prim。设置 `prim_path` 以定位 stage 中的特定 prim。

## USD Morph 配置

`gs.morphs.USD` 类提供了广泛的配置选项来控制 USD 文件的解析方式：

### 关节动力学配置

Genesis 可以从 USD 属性解析关节属性。

由于某些关节物理属性不是 USD 标准的一部分，Genesis 提供了默认的属性名称候选，以适应成熟的导出器，特别是 Isaac Sim，它使用自定义属性如 `physxJoint:jointFriction` 和 `physxLimit:angular:stiffness`。

例如，以下代码配置关节摩擦的属性名称候选。解析器将按顺序尝试这些候选，并使用找到的第一个。

```python
gs.morphs.USD(
    file="robot.usd",
    # 关节摩擦属性（按顺序尝试）
    joint_friction_attr_candidates=[
        "physxJoint:jointFriction",  # Isaac Sim 兼容性
        "physics:jointFriction",
        "jointFriction",
        "friction",
    ],
)
```

支持的属性列在下表中：

| Genesis 属性名称 | 来源 / 默认属性名称候选 | 描述 |
|----------------|-------------|-------------|
| `dofs_frictionloss` | `["physxJoint:jointFriction", "physics:jointFriction", "jointFriction", "friction"]` | 关节摩擦（被动属性） |
| `dofs_armature` | `["physxJoint:armature", "physics:armature", "armature"]` | 关节惯量（被动属性） |
| `dofs_kp` | `"physics:stiffness"` | PD 控制比例增益 (kp) - 来自 DriveAPI |
| `dofs_kv` | `"physics:angular:damping"` | PD 控制微分增益 (kv) - 来自 DriveAPI |
| `dofs_stiffness` | **旋转关节：** `["physxLimit:angular:stiffness", "physics:stiffness", "stiffness"]`<br>**滑动关节：** `["physxLimit:linear:stiffness", "physxLimit:X:stiffness", "physxLimit:Y:stiffness", "physxLimit:Z:stiffness", "physics:linear:stiffness", "linear:stiffness"]` | 被动关节刚度（取决于关节类型） |
| `dofs_damping` | **旋转关节：** `["physxLimit:angular:damping", "physics:angular:damping", "angular:damping"]`<br>**滑动关节：** `["physxLimit:linear:damping", "physxLimit:X:damping", "physxLimit:Y:damping", "physxLimit:Z:damping", "physics:linear:damping", "linear:damping"]` | 被动关节阻尼（取决于关节类型） |

注意，方括号 (`[...]`) 内的属性名称是非官方的 USD 属性，用户可以设置自己的属性名称候选来自定义解析行为，而没有方括号 (`...`) 的属性名称是官方 USD 属性，直接从 USD 文件解析。

### 几何体解析选项

Genesis 可以从 USD 文件解析碰撞和视觉几何体。你可以配置正则表达式模式来识别哪些 prim 应被视为仅碰撞或仅视觉几何体。解析器使用 `re.match()` 检查 prim 的名称是否从字符串开头匹配每个模式。

**识别规则：**

1. **模式匹配**：解析器递归遍历 prim 层次结构。对于每个 prim，它按顺序检查 prim 的名称是否匹配模式。一旦 prim 匹配模式，它就被标记为视觉匹配或碰撞匹配，该分类由其所有子 prim 递归继承。

2. **几何体分类**：
   - 匹配视觉模式的 prim 被视为仅视觉几何体（不用于碰撞检测）。
   - 匹配碰撞模式的 prim 被视为仅碰撞几何体（不用于可视化）。
   - 同时匹配两种模式的 prim 被视为视觉和碰撞几何体。
   - 不匹配任何模式的 prim 也被视为视觉和碰撞几何体（这是仅网格 USD 资源的默认行为）。

3. **可见性和用途**：仅解析可见的 prim（未标记为 "invisible"）。用途为 "guide" 的 prim 从视觉几何体中排除，但仍可以是碰撞几何体。

**配置示例：**

```python
gs.morphs.USD(
    file="robot.usd",
    # 识别碰撞网格的正则表达式模式（按顺序尝试）
    collision_mesh_prim_patterns=[
        r"^([cC]ollision).*",  # 匹配以 "Collision" 或 "collision" 开头的 prim
    ],
    # 识别视觉网格的正则表达式模式
    visual_mesh_prim_patterns=[
        r"^([vV]isual).*",     # 匹配以 "Visual" 或 "visual" 开头的 prim
    ],
)
```

**Stage 结构示例：**

- **刚体上的直接几何体**：几何体 prim 本身不匹配任何模式，因此被视为视觉和碰撞几何体。

    ```usd
    def Cube "Cube" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
    }
    ```
- **单独的视觉和碰撞子项**：匹配模式的直接子项被相应处理，匹配传播到其子树。

    ```usd
    def Xform "ObjectA" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Cube "Visual"      # 匹配视觉模式 → 仅视觉
            {
            }

            def Cube "Collision"   # 匹配碰撞模式 → 仅碰撞
            {
            }
        }
    ```
- **嵌套层次结构**：一旦父项匹配模式，所有后代继承该分类。

    ```usd
    def Xform "ObjectB" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Xform "Visual"     # 匹配视觉模式
            {
                def Mesh "Cube"    # 继承仅视觉（整个子树）
                {
                }
                def Mesh "Sphere"  # 继承仅视觉
                {
                }
            }

            def Xform "Collision" # 匹配碰撞模式
            {
                def Cube "Cube"   # 继承仅碰撞（整个子树）
                {
                }
            }
        }
    ```
- **无模式匹配**：不匹配任何模式的 prim 被视为视觉和碰撞几何体。
    ```usd
    def Xform "ObjectC" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
        def Mesh "Whatever"  # 无模式匹配 → 视觉和碰撞
        {
        }
    }
    ```


## 下一步

- 了解如何在 Genesis 中[控制机器人](control_your_robot.md)
- 探索 USD 加载机器人的[逆运动学](inverse_kinematics_motion_planning.md)
- 查看[并行模拟](parallel_simulation.md)了解如何使用 USD 资源进行训练
- 参阅 [API 参考](../../api_reference/options/morph/file_morph/file_morph.md)了解详细的 USD morph 选项
- 参阅[约定](conventions.md)了解 Genesis 使用的坐标系和数学约定的更多详细信息。
