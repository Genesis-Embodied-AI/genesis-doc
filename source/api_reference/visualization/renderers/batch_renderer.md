# BatchRenderer

`BatchRenderer` 提供高吞吐量的并行渲染，针对大规模强化学习训练中的许多并行环境进行优化。

## 概述

BatchRenderer 专为以下场景设计：

- **最大吞吐量**：针对渲染数千个环境进行优化
- **并行执行**：原生支持批处理仿真
- **RL 训练**：高效的策略学习观测生成
- **GPU 加速**：完整的 GPU 流水线，最小化 CPU 开销

## 快速开始

```python
import genesis as gs

gs.init()

# 创建具有多个环境的场景
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# 使用并行环境构建
scene.build(n_envs=1024)

# 添加 batch renderer 相机
cam = scene.add_camera(
    res=(84, 84),
    pos=(2, 0, 1),
    lookat=(0, 0, 0.5),
)

# 训练循环
for step in range(10000):
    # 获取批处理观测
    obs = cam.render(rgb=True)  # 形状：(n_envs, H, W, 3)

    # 策略推理...
    actions = policy(obs)

    # 执行所有环境步骤
    scene.step()
```

## 配置

通过 `BatchRendererOptions` 配置 BatchRenderer：

```python
batch_options = gs.options.BatchRendererOptions(
    # 配置选项
)
```

## 输出格式

当 `n_envs > 1` 时，相机输出是批处理的：

| 输出 | 形状 | 描述 |
|--------|-------|-------------|
| `rgb` | `(n_envs, H, W, 3)` | 批处理 RGB 图像 |
| `depth` | `(n_envs, H, W)` | 批处理深度图 |
| `segmentation` | `(n_envs, H, W)` | 批处理分割 |

## 性能提示

1. **分辨率**：对于 RL 使用较小的分辨率（64x64 或 84x84）
2. **渲染频率**：仅在需要时渲染，而不是每步都渲染
3. **GPU 内存**：监控使用大量环境时的显存使用

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.batch_renderer.BatchRenderer
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`rasterizer` - 标准光栅化渲染器
- {doc}`/api_reference/options/renderer/batchrenderer` - BatchRenderer 选项
