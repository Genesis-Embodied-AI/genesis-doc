# 🎥 レコーダーを使ったデータ保存と可視化
Genesis には、シミュレーションを遅くせずにデータを自動処理できる記録ユーティリティも用意されています。
これにより、整形済みデータをファイルへストリーム出力したり、ライブ可視化したりできます。

```python
# 1. シーンを build する前に記録開始
sensor.start_recording(
    rec_options=gs.recorders.NPZFile(
        filename="sensor_data.npz"
    ),
)
```
... 以上です。記録はシーンが非アクティブになると自動で停止・クリーンアップされます。
また、`scene.stop_recording()` でも停止できます。

センサーデータは `sensor.start_recording(recorder_options)` で記録できます。
また、カスタムのデータ取得関数を使って `scene.start_recording(data_func, recorder_options)` により任意データを記録することもできます。例：

```
def imu_data_func():
    data = imu.read()
    true_data = imu.read_ground_truth()
    return {
        "lin_acc": data.lin_acc,
        "true_lin_acc": true_data.lin_acc,
        "ang_vel": data.ang_vel,
        "true_ang_vel": true_data.ang_vel,
    }

scene.start_recording(
    imu_data_func,
    gs.recorders.MPLLinePlot(
        title="IMU Data",
        labels={
            "lin_acc": ("x", "y", "z"),
            "true_lin_acc": ("x", "y", "z"),
            "ang_vel": ("x", "y", "z"),
            "true_ang_vel": ("x", "y", "z"),
        },
    ),
)
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>

現在利用可能なレコーダーについては、API リファレンスの `RecorderOptions` を参照してください。
レコーダーの利用例は `examples/sensors/` にもあります。 
