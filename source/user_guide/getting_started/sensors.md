# 🖲️ センサー

ロボットは周囲の世界を観測するためにセンサーを必要とします。
Genesis におけるセンサーは、シーン状態を使って情報を計算して取得しますが、シーン自体には影響を与えません。

センサーは `scene.add_sensor(sensor_options)` で作成し、`sensor.read()` または `sensor.read_ground_truth()` で読み取ります。
```python
scene = ...

# 1. シーンにセンサーを追加
sensor = scene.add_sensor(
    gs.sensors.Contact(
        ...,
        draw_debug=True, # シーンビューア上でセンサーデータを可視化
    )
)

# 2. シーンをビルド
scene.build()

for _ in range(1000):
    scene.step()

    # 3. センサーからデータを取得
    measured_data = sensor.read()
    ground_truth_data = sensor.read_ground_truth()
```

現在サポートされているセンサー:
- `IMU`（加速度計 + ジャイロ）
- `Contact`（剛体リンクごとの真偽値）
- `ContactForce`（剛体リンクごとの xyz 力）
- `Raycaster`
  - `Lidar`
  - `DepthCamera`
<!-- - `RGBCamera` -->

センサーの利用例は `examples/sensors/` にあります。


## IMU の例

このチュートリアルでは、ロボットアームのエンドエフェクタに IMU センサーを設定する方法を説明します。
ロボットが円軌道をたどる際の線形加速度と角速度を IMU で計測し、現実的なノイズパラメータ付きでリアルタイム可視化します。

完全なサンプルスクリプトは `examples/sensors/imu_franka.py` にあります。

### シーン設定

まずシミュレーションシーンを作成し、ロボットアームを読み込みます。

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    sim_options=gs.options.SimOptions(
        dt=0.01,
    ),
    show_viewer=True,
)

########################## entities ##########################
scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
end_effector = franka.get_link("hand")
motors_dof = (0, 1, 2, 3, 4, 5, 6)
```

ここでは Franka ロボットアームを使った基本シーンを構築しています。
カメラは作業空間を見やすい位置に配置し、IMU を取り付けるエンドエフェクタリンクを取得します。

### IMU センサーの追加

`entity_idx` と `link_idx_local` を指定して、エンドエフェクタ上のエンティティに IMU を「取り付け」ます。

```python
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
        # sensor characteristics
        acc_cross_axis_coupling=(0.0, 0.01, 0.02),
        gyro_cross_axis_coupling=(0.03, 0.04, 0.05),
        acc_noise=(0.01, 0.01, 0.01),
        gyro_noise=(0.01, 0.01, 0.01),
        acc_random_walk=(0.001, 0.001, 0.001),
        gyro_random_walk=(0.001, 0.001, 0.001),
        delay=0.01,
        jitter=0.01,
        interpolate=True,
        draw_debug=True,
    )
)
```

`gs.sensors.IMU` コンストラクタでは次のセンサー特性を設定できます。
- `pos_offset`: リンク座標系に対するセンサー位置
- `acc_cross_axis_coupling` と `gyro_cross_axis_coupling`: センサー軸ずれをシミュレート
- `acc_noise` と `gyro_noise`: 計測値にガウスノイズを付加
- `acc_random_walk` と `gyro_random_walk`: 時間経過によるドリフトをシミュレート
- `delay` と `jitter`: 時間遅延の現実性を導入
- `interpolate`: 遅延計測を平滑化
- `draw_debug`: ビューアにセンサーフレームを可視化

### モーション制御とシミュレーション

次にシーンをビルドし、興味深い IMU 値が得られるよう円運動を作ります。

```python
########################## build and control ##########################
scene.build()

franka.set_dofs_kp(np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]))
franka.set_dofs_kv(np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]))

# Create a circular path for end effector to follow
circle_center = np.array([0.4, 0.0, 0.5])
circle_radius = 0.15
rate = np.deg2rad(2.0)  # Angular velocity in radians per step

def control_franka_circle_path(i):
    pos = circle_center + np.array([np.cos(i * rate), np.sin(i * rate), 0]) * circle_radius
    qpos = franka.inverse_kinematics(
        link=end_effector,
        pos=pos,
        quat=np.array([0, 1, 0, 0]),  # Keep orientation fixed
    )
    franka.control_dofs_position(qpos[:-2], motors_dof)
    scene.draw_debug_sphere(pos, radius=0.01, color=(1.0, 0.0, 0.0, 0.5))  # Visualize target

# Run simulation
for i in range(1000):
    scene.step()
    control_franka_circle_path(i)
```

ロボットは姿勢を固定したまま水平円軌道をたどります。
この円運動により、IMU は向心加速度や、センサー姿勢に基づく重力影響を検出します。

シーンビルド後は、計測値と真値の両方にアクセスできます。

```python
# Access sensor readings
print("Ground truth data:")
print(imu.read_ground_truth())
print("Measured data:")
print(imu.read())
```

IMU は次のフィールドを持つ **named tuple** を返します。
- `lin_acc`: 線形加速度（m/s², 3 次元ベクトル）
- `ang_vel`: 角速度（rad/s, 3 次元ベクトル）

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>

## 接触センサー

接触センサーは、剛体ソルバーから剛体リンクごとの接触情報を取得します。
`Contact` センサーは真偽値を返し、`ContactForce` は対応する剛体リンクのローカル座標系で合力ベクトルを返します。
<!-- NOTE: Untested with other solver couplings -->

完全なサンプルスクリプトは `examples/sensors/contact_force_go2.py` にあります（力センサーを使うには `--force` フラグを追加）。

```{figure} ../../_static/images/contact_force_sensor.png
```

## KinematicContactProbe センサー
`KinematicContactProbe` は、剛体エンティティリンクに関連付けられた「プローブ」点に沿って接触深さを問い合わせる触覚センサーです。
前述の接触センサーのように物理ソルバーから力を取得するのではなく、このセンサーは接触貫入深さから `F = stiffness * penetration * probe_normal` として力を推定します。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/kin_probe_data.mp4" type="video/mp4">
</video>

テレオペ制御付きのサンプルは `examples/sensors/kinematic_contact_probe.py` にあります。

触覚センサーの taxel（触覚画素）を模倣するために、ロボットハンドやエンドエフェクタ上へ触覚プローブのグリッドを簡単に配置できます。

## Raycaster センサー: Lidar と Depth Camera

`Raycaster` センサーは、シーンにレイを投射してジオメトリとの交差を検出し、距離を計測します。
レイ本数とレイ方向は `RaycastPattern` で指定できます。
`SphericalPattern` は視野角と角度分解能の LiDAR 風指定をサポートし、`GridPattern` は平面からレイを投射します。
`DepthCamera` センサーは `read_image()` によりレイキャスト情報を深度画像として整形します。利用可能なオプションの詳細は API リファレンスを参照してください。

```python
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.Spherical(),
        entity_idx=robot.idx, # attach to a rigid entity
        pos_offset=(0.3, 0.0, 0.1) # offset from attached entity
        return_world_frame=True, # whether to return points in world frame or local frame
    )
)

depth_camera = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=gs.sensors.DepthCameraPattern(
            res=(480, 360), # image resolution in width, height
            fov_horizontal=90, # field of view in degrees
            fov_vertical=40,
        ),
    )
)

...

lidar.read() # returns a NamedTuple containing points and distances
depth_camera.read_image() # returns tensor of distances as shape (height, width)

```

ロボットに取り付けた raycaster センサーの例は `examples/sensors/lidar_teleop.py` にあります。
`--pattern` フラグに `spherical` を指定すると LiDAR 風、`grid` で平面グリッド、`depth` で深度カメラパターンになります。

`python examples/sensors/lidar_teleop.py --pattern depth` の実行例:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/depth_camera.mp4" type="video/mp4">
</video>
