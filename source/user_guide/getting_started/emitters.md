# 💧 粒子发射器

发射器用于生成流体和材料模拟的粒子（SPH、MPM、PBD）。

## 创建发射器

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
    sph_options=gs.options.SPHOptions(particle_size=0.02),
)

scene.add_entity(gs.morphs.Plane())

emitter = scene.add_emitter(
    material=gs.materials.SPH.Liquid(),
    max_particles=100000,
    surface=gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7)),
)

scene.build()
```

## 支持的材质

- `gs.materials.SPH.Liquid()` - SPH 流体
- `gs.materials.MPM.Liquid()` - MPM 液体
- `gs.materials.MPM.Sand()` - 颗粒材料
- `gs.materials.PBD.Liquid()` - 基于位置的流体

## 定向发射

```python
for step in range(500):
    emitter.emit(
        pos=np.array([0.5, 0.5, 2.0]),      # 喷嘴位置
        direction=np.array([0.0, 0.0, -1.0]), # 发射方向
        speed=5.0,                            # 粒子速度
        droplet_shape="circle",               # 形状：circle, sphere, square, rectangle
        droplet_size=0.1,                     # 半径或边长
    )
    scene.step()
```

### 液滴形状

| 形状 | `droplet_size` | 描述 |
|-------|---------------|-------------|
| `"circle"` | `float` | 圆柱流 |
| `"sphere"` | `float` | 球形液滴 |
| `"square"` | `float` | 立方体液滴 |
| `"rectangle"` | `(w, h)` | 矩形流 |

## 全向发射

从球形源径向发射粒子：

```python
emitter.emit_omni(
    pos=(0.5, 0.5, 1.0),
    source_radius=0.1,
    speed=2.0,
)
```

## 动态发射

```python
for i in range(1000):
    # 振荡方向
    direction = np.array([0.0, np.sin(i / 10) * 0.3, -1.0])

    emitter.emit(
        pos=np.array([0.5, 0.0, 2.0]),
        direction=direction,
        speed=8.0,
        droplet_shape="rectangle",
        droplet_size=[0.03, 0.05],
    )
    scene.step()
```

## 多发射器

```python
emitter1 = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.9, 0.4, 1.0)),
)
emitter2 = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.4, 0.9, 1.0)),
)

for step in range(500):
    emitter1.emit(pos=np.array([0.3, 0.5, 2.0]), direction=np.array([0, 0, -1]), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    emitter2.emit(pos=np.array([0.7, 0.5, 2.0]), direction=np.array([0, 0, -1]), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    scene.step()
```

## 注意事项

- 发射器必须在 `scene.build()` 之前添加
- 当达到 `max_particles` 时粒子会循环使用
- 与可微模拟不兼容（`requires_grad=True`）
