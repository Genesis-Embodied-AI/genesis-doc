# 📷 相机传感器

Genesis 提供三种相机传感器后端，用于在仿真中渲染 RGB 图像。

## 相机传感器类型

| 传感器 | 后端 | 多环境 | 最适用于 |
|--------|---------|-----------|----------|
| `RasterizerCameraSensor` | OpenGL | 顺序 | 快速实时渲染 |
| `RaytracerCameraSensor` | LuisaRender | 仅单环境 | 照片级真实感图像 |
| `BatchRendererCameraSensor` | Madrona GPU | 并行 | 高吞吐量 RL 训练 |

## 基本用法

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(morph=gs.morphs.Plane())

# 添加相机传感器
camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
    )
)

scene.build(n_envs=1)
scene.step()

# 读取渲染图像
data = camera.read()
print(data.rgb.shape)  # 单环境为 (512, 512, 3)
```

## 相机选项

### 通用参数（所有后端）

```python
gs.sensors.RasterizerCameraOptions(
    res=(512, 512),              # （宽，高）
    pos=(3.0, 0.0, 2.0),         # 位置（世界或局部，如果连接）
    lookat=(0.0, 0.0, 0.0),      # 观察点
    up=(0.0, 0.0, 1.0),          # 上向量
    fov=60.0,                    # 垂直视场角度
    entity_idx=-1,               # 连接到的实体（-1 = 静态）
    link_idx_local=0,            # 用于连接的连杆索引
)
```

### 光线追踪器特定参数

```python
gs.sensors.RaytracerCameraOptions(
    model="pinhole",             # "pinhole" 或 "thinlens"
    spp=256,                     # 每像素采样数
    denoise=False,               # 应用降噪
    aperture=2.8,                # 景深（thinlens）
    focus_dist=3.0,              # 焦距（thinlens）
)
```

### 批量渲染器特定参数

```python
gs.sensors.BatchRendererCameraOptions(
    near=0.01,                   # 近裁剪平面
    far=100.0,                   # 远裁剪平面
    use_rasterizer=True,         # GPU 光栅化器模式
)
```

**注意：** 所有 BatchRenderer 相机必须具有相同的分辨率。

## 将相机连接到实体

将相机安装在机器人的末端执行器上：

```python
robot = scene.add_entity(morph=gs.morphs.URDF(file="robot.urdf"))

camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(640, 480),
        pos=(0.1, 0.0, 0.05),    # 相对于连杆坐标系的偏移
        lookat=(0.2, 0.0, 0.0),  # 观察方向
        entity_idx=robot.idx,    # 连接到机器人
        link_idx_local=8,        # 末端执行器连杆
    )
)
```

相机会自动跟随实体的运动。

## 多环境渲染

```python
scene.build(n_envs=4)

# 为每个环境设置不同的状态
sphere.set_pos([[0, 0, 1], [0.2, 0, 1], [0.4, 0, 1], [0.6, 0, 1]])
scene.step()

# 读取所有环境
data = camera.read()
print(data.rgb.shape)  # (4, H, W, 3)

# 读取特定环境
data = camera.read(envs_idx=[0, 2])
print(data.rgb.shape)  # (2, H, W, 3)
```

## 选择后端

- **Rasterizer**：默认选择，快速，适用于所有平台
- **Raytracer**：需要照片级真实感时使用（需要 `renderer=gs.renderers.RayTracer()`）
- **BatchRenderer**：用于多环境 RL 训练（仅 CUDA）

```python
# 对于光线追踪器，配置场景渲染器
scene = gs.Scene(renderer=gs.renderers.RayTracer())

# 对于批量渲染器
scene = gs.Scene(renderer=gs.renderers.BatchRenderer())
```
