# 🎑 ビューア操作

Genesis ビューアは、カメラ操作、録画、可視化切り替えなどのためのマウス・キーボード操作をサポートします。
この機能は、カスタムキーバインドとビューアプラグインで簡単に拡張できます。


## キーバインドの追加

`scene.build()` 前に `scene.viewer.register_keybinds(...)` でキーバインドを登録します。


```python
import genesis.vis.keybindings as kb

...

is_running = True

def stop():
    global is_running
    is_running = False

scene.viewer.register_keybinds(
    kb.Keybind("greetings", kb.Key.G, kb.KeyAction.PRESS, callback=lambda: print("Hello!")),
    kb.Keybind("quit", kb.Key.ESCAPE, kb.KeyAction.PRESS, callback=stop),
    # 必要なだけキーバインドを追加できます
)
scene.build()

while is_running:
    scene.step()
```

```{figure} ../../_static/images/keybindings_instructions.png
:alt: Viewer overlay showing keyboard instructions including plugin keybindings
```
登録したキーバインドは、ビューアの説明オーバーレイに表示されるため、利用者は操作方法をすぐ把握できます。


デフォルトのビューア操作を無効化したり、ヘルプ表示を隠したい場合は、シーン作成時に対応オプションを設定します。

```python
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        enable_help_text=False,         # 操作説明テキストを非表示にする
        enable_default_keybinds=False,  # 既定のキーボードショートカットを無効化する
    ),
)
```


## ビューアプラグイン

ビューアプラグインは、カスタム入力処理や可視化機能でインタラクティブなシーンビューアを拡張します。
マウス/キーボードイベントの受信、毎フレームのデバッグジオメトリ描画、各シミュレーションステップでのロジック実行が可能で、
メッシュ上の点選択やマウスドラッグ操作などのツール実装に適しています。

プラグインは `scene.build()` *前* に `scene.viewer.add_plugin(plugin)` で追加します。
サンプルスクリプトは `examples/viewer_plugin/` にあります。


### マウス操作プラグイン

**`MouseInteractionPlugin`** は、シーン内の剛体をクリック＆ドラッグできます。
既定では位置を直接設定して移動し、オプションでバネ力を使ったより物理的な操作も可能です。

完全なサンプルは `examples/viewer_plugin/mouse_interaction.py` にあります。
位置制御ではなくバネ力を使うには `--use_force` フラグを使ってください。

```python
scene.viewer.add_plugin(
    gs.vis.viewer_plugins.MouseInteractionPlugin(
        use_force=True,  # False = set position, True = spring force
        spring_const=1000.0,
        color=(0.1, 0.6, 0.8, 0.6),
    )
)
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/viewer_plugin_mouse_spring.mp4" type="video/mp4">
</video>


### カスタムプラグイン

`ViewerPlugin`（またはスクリーン座標→ワールドレイ変換が必要なら `RaycasterViewerPlugin`）を継承し、`scene.viewer.add_plugin()` で追加することで独自プラグインを実装できます。

#### ViewerPlugin ベースクラス

カスタムプラグインは `gs.vis.viewer_plugins.ViewerPlugin` を継承します。
シーンビルド後にビューアから `build(viewer, camera, scene)` が呼ばれるので、参照保存や初期化処理をここで行います。

イベントフックは、イベントを消費した場合 `EVENT_HANDLED`（または `True`）を返し、
他プラグインやデフォルトビューアへ処理を渡す場合は `None` を返します。

| メソッド | 説明 |
|--------|-------------|
| `on_mouse_motion(x, y, dx, dy)` | マウス移動時に呼ばれます |
| `on_mouse_drag(x, y, dx, dy, buttons, modifiers)` | ボタン押下中のドラッグ時に呼ばれます |
| `on_mouse_press(x, y, buttons, modifiers)` | マウスボタン押下時に呼ばれます（初回押下で 1 回） |
| `on_mouse_release(x, y, buttons, modifiers)` | マウスボタン解放時に呼ばれます |
| `on_mouse_scroll(x, y, dx, dy)` | スクロールホイール操作時に呼ばれます |
| `on_key_press(key, modifiers)` | キー押下時に呼ばれます |
| `on_key_release(key, modifiers)` | キー解放時に呼ばれます |
| `on_resize(width, height)` | ウィンドウリサイズ時に呼ばれます |
| `update_on_sim_step()` | `scene.step()` ごとに呼ばれます |
| `on_draw()` | 各フレームでカスタム描画のために呼ばれます |
| `on_close()` | ビューア終了時に呼ばれます |

```python
from genesis.vis.viewer_plugins import ViewerPlugin, EVENT_HANDLED, EVENT_HANDLE_STATE

class MyPlugin(ViewerPlugin):
    def build(self, viewer, camera, scene):
        super().build(viewer, camera, scene)
        # self.viewer, self.camera, self.scene が設定される

    def on_key_press(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        if symbol == ord("x"):
            # 何らかの処理
            return EVENT_HANDLED
        return None

    def on_draw(self) -> None:
        # 例: self.scene.draw_debug_*() でデバッグ描画
        pass
```

#### RaycasterViewerPlugin とスクリーン空間レイ

クリック選択や 3D ドラッグ挙動には、マウス座標を通るカメラレイが必要です。
`ViewerPlugin` ではなく `RaycasterViewerPlugin` を継承すると、レイキャスタを内部保持し、
`_screen_position_to_ray(x, y)` で `Ray`（ワールド座標系の始点と方向）を取得できます。

`RaycasterViewerPlugin` は `update_on_sim_step()` もオーバーライドしており、
各ステップでレイキャスタをシーンと同期します。

```python
from genesis.vis.viewer_plugins import RaycasterViewerPlugin, EVENT_HANDLED

class PickerPlugin(RaycasterViewerPlugin):
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button != 1:
            return None
        ray = self._screen_position_to_ray(x, y)
        hit = self._raycaster.cast(*ray)
        if hit is not None and hit.geom:
            link = hit.geom.link
            world_pos = hit.position
            # ...
            return EVENT_HANDLED
        return None
```

`scene.viewer.register_keybinds()` を使ってキー（終了、モード切替など）を登録すると、
そのキーバインドはビューアのキーボード説明オーバーレイにも表示されます。


#### 例: Mesh Point Selector

**`MeshPointSelectorPlugin`** は、マウスレイキャストで剛体メッシュ上の点を選択します。
クリックで点を追加/削除し、選択点は球で表示され、グリッドスナップも可能です。
終了時に、選択点（リンクローカル座標）を CSV へ出力します。
これはエンティティ上にセンサーを配置するためのローカル位置取得などに有用です。

完全なサンプルは `examples/viewer_plugin/mesh_point_selector.py` にあります。

```python
from genesis.vis.viewer_plugins import MeshPointSelectorPlugin

scene.viewer.add_plugin(
    MeshPointSelectorPlugin(
        sphere_radius=0.004,
        sphere_color=(0.1, 0.3, 1.0, 1.0),
        hover_color=(0.3, 0.5, 1.0, 1.0),
        grid_snap=(-1.0, 0.01, 0.01),  # -1 = no snap on that axis
        output_file="selected_points.csv",
    )
)
scene.build()
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/viewer_plugin_mesh_point.mp4" type="video/mp4">
</video>
