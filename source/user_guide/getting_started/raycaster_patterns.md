# 📡 レイキャスターパターン

Genesis は、LiDAR と深度センサーのシミュレーション向けに複数のレイパターンを提供します。

## パターンの種類

| パターン | 用途 |
|---------|----------|
| `SphericalPattern` | 3D LiDAR（Velodyne、Ouster など） |
| `DepthCameraPattern` | 深度カメラ（RealSense、Kinect） |
| `GridPattern` | 平面センシング、高さマップ |

## SphericalPattern（LiDAR パターン）

```python
import genesis as gs

# 水平 360°、垂直 60° の FOV
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

### SphericalPattern のパラメータ

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),              # (水平, 垂直) 角度
    n_points=(128, 64),             # (水平, 垂直) レイ本数
    angular_resolution=(0.25, 0.5), # 代替指定: 1 レイあたりの角度
    angles=(h_angles, v_angles),    # カスタム角度配列
)
```

### 実機 LiDAR の設定例

```python
# Velodyne VLP-16
velodyne = gs.sensors.SphericalPattern(fov=(360.0, 30.0), n_points=(1800, 16))

# 前方 120° FOV
front_lidar = gs.sensors.SphericalPattern(fov=((-60, 60), 30.0), n_points=(128, 32))
```

## DepthCameraPattern（深度カメラ）

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

### DepthCameraPattern のパラメータ

```python
gs.sensors.DepthCameraPattern(
    res=(640, 480),           # 解像度 (width, height)
    fov_horizontal=90.0,      # 水平 FOV（度）
    fov_vertical=None,        # アスペクト比から自動計算
    fx=None, fy=None,         # 焦点距離（FOV を上書き）
    cx=None, cy=None,         # 主点
)
```

## GridPattern（グリッド）

平行レイの平面グリッドです。

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,            # 10cm 間隔
    size=(2.0, 2.0),           # 2m x 2m グリッド
    direction=(0.0, 0.0, -1.0), # 下向き
)
```

## センサーデータの読み取り

```python
scene.build()
scene.step()

# LiDAR データ
data = lidar.read()
points = data.points         # 形状: (n_h, n_v, 3)
distances = data.distances   # 形状: (n_h, n_v)

# 深度カメラ画像
depth_image = depth_cam.read_image()  # 形状: (H, W)
```

## 共通オプション

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

## マルチ環境

```python
scene.build(n_envs=4)
data = lidar.read()
print(data.points.shape)  # バッチ環境では (4, n_h, n_v, 3)
```
