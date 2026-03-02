# 💧 パーティクルエミッター

Emitter は、流体・材料シミュレーション（SPH、MPM、PBD）向けに粒子を生成します。

## エミッターの作成

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

## サポートされるマテリアル

- `gs.materials.SPH.Liquid()` - SPH 流体
- `gs.materials.MPM.Liquid()` - MPM 液体
- `gs.materials.MPM.Sand()` - 粒状体
- `gs.materials.PBD.Liquid()` - Position-based 流体

## 指向性放出

```python
for step in range(500):
    emitter.emit(
        pos=np.array([0.5, 0.5, 2.0]),      # ノズル位置
        direction=np.array([0.0, 0.0, -1.0]), # 放出方向
        speed=5.0,                            # 粒子速度
        droplet_shape="circle",               # 形状: circle, sphere, square, rectangle
        droplet_size=0.1,                     # 半径または辺長
    )
    scene.step()
```

### 液滴形状

| 形状 | `droplet_size` | 説明 |
|-------|---------------|-------------|
| `"circle"` | `float` | 円柱状ストリーム |
| `"sphere"` | `float` | 球状液滴 |
| `"square"` | `float` | 立方体状液滴 |
| `"rectangle"` | `(w, h)` | 長方形ストリーム |

## 全方向放出

球形ソースから放射状に粒子を放出します。

```python
emitter.emit_omni(
    pos=(0.5, 0.5, 1.0),
    source_radius=0.1,
    speed=2.0,
)
```

## 動的放出

```python
for i in range(1000):
    # 振動する方向
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

## 複数エミッター

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

## 注意点

- Emitter は `scene.build()` 前に追加する必要があります
- `max_particles` に達すると粒子は再利用されます
- 微分可能シミュレーション（`requires_grad=True`）とは互換性がありません
