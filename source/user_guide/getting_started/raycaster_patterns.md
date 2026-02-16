# 📡 Raycaster 模式

Genesis 为 LiDAR 和深度传感器仿真提供了多种射线模式。

## 模式类型

| 模式 | 使用场景 |
|---------|----------|
| `SphericalPattern` | 3D LiDAR (Velodyne, Ouster) |
| `DepthCameraPattern` | 深度相机 (RealSense, Kinect) |
| `GridPattern` | 平面感知、高度图 |

## SphericalPattern (LiDAR)

```python
import genesis as gs

# 360° 水平视场角，60° 垂直视场角
pattern = gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),
    n_points=(128, 32),
)

lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.15),
        max_range=100.0,
        min_range=0.1,
        draw_debug=True,
    )
)
```

### SphericalPattern 参数

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),              # (水平, 垂直) 度
    n_points=(128, 64),             # (水平, 垂直) 射线数
    angular_resolution=(0.25, 0.5), # 替代方案：每条射线的度数
    angles=(h_angles, v_angles),    # 自定义角度数组
)
```

### 真实 LiDAR 配置

```python
# Velodyne VLP-16
velodyne = gs.sensors.SphericalPattern(fov=(360.0, 30.0), n_points=(1800, 16))

# 前向 120° 视场角
front_lidar = gs.sensors.SphericalPattern(fov=((-60, 60), 30.0), n_points=(128, 32))
```

## DepthCameraPattern

```python
pattern = gs.sensors.DepthCameraPattern(
    res=(640, 480),
    fov_horizontal=87.0,
)

depth_cam = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.05),
        max_range=5.0,
    )
)
```

### DepthCameraPattern 参数

```python
gs.sensors.DepthCameraPattern(
    res=(640, 480),           # 分辨率 (宽, 高)
    fov_horizontal=90.0,      # 水平视场角度数
    fov_vertical=None,        # 从长宽比自动计算
    fx=None, fy=None,         # 焦距 (覆盖 FOV)
    cx=None, cy=None,         # 主点
)
```

## GridPattern

平面平行射线网格：

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,            # 10cm 间距
    size=(2.0, 2.0),           # 2m x 2m 网格
    direction=(0.0, 0.0, -1.0), # 指向下方
)
```

## 读取传感器数据

```python
scene.build()
scene.step()

# LiDAR 数据
data = lidar.read()
points = data.points         # 形状: (n_h, n_v, 3)
distances = data.distances   # 形状: (n_h, n_v)

# 深度相机图像
depth_image = depth_cam.read_image()  # 形状: (H, W)
```

## 通用选项

```python
gs.sensors.Lidar(
    pattern=pattern,
    entity_idx=robot.idx,
    pos_offset=(0.0, 0.0, 0.15),
    euler_offset=(0.0, 0.0, 0.0),
    max_range=100.0,
    min_range=0.1,
    return_world_frame=True,
    draw_debug=True,
)
```

## 多环境

```python
scene.build(n_envs=4)
data = lidar.read()
print(data.points.shape)  # (4, n_h, n_v, 3) 用于批处理环境
```
