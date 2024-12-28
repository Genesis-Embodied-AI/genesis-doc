# 🧑‍💻 インタラクティブな情報アクセスとデバッグ

私たちは、Genesis で作成されたオブジェクトに関する内部情報やすべての利用可能な属性にアクセスするための非常に情報豊富（そして見た目も良い、願わくば）なインターフェースを設計しました。これは、すべての Genesis クラスにおける `__repr__()` メソッドを通じて実装されています。この機能は、`IPython` や `pdb`、または `ipdb` を使用してデバッグすることに慣れている場合に非常に役立ちます。

以下の例では `IPython` を使用します。インストールされていない場合は、`pip install ipython` を実行してインストールしてください。それでは、簡単な例を見ていきましょう：

```python
import genesis as gs

gs.init()

scene = gs.Scene(show_viewer=False)

plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

cam_0 = scene.add_camera()
scene.build()

# IPython のインタラクティブモードに入る
import IPython; IPython.embed()
```

このスクリプトを直接実行するか（`IPython` がインストールされている場合）、ターミナルで `IPython` のインタラクティブウィンドウを開き、ここでコードを最終行を除いて貼り付けることができます。

この小さなコードブロックでは、平面エンティティと Franka アームを追加しました。初心者であれば、シーンに何が含まれているのか疑問に思うかもしれません。`IPython`（または `ipdb`、`pdb`、あるいはネイティブの Python シェル）で単に `scene` と入力すると、シーン内のすべての内容がフォーマットされ、見やすく色付けされた形で表示されます：

```{figure} ../../_static/images/interactive_scene.png
```

最上部の行にはオブジェクトのタイプ（この場合 `<gs.Scene>`）が表示されます。その後、シーン内の利用可能なすべての属性が表示されます。例えば、このシーンが構築済みであること（`is_built` が `True`）、タイムステップ（`dt`）が `0.01` 秒の値を持つ浮動小数点数であること、一意の ID（`uid`）が `'69be70e-dc9574f508c7a4c4de957ceb5'` であることがわかります。シーンには `solvers` という属性もあり、これは持っている異なる物理ソルバーのリストを意味します。このリストは `gs.List` クラスで実装されており、シェル内で `scene.solvers` と入力すると詳細を確認できます。

```{figure} ../../_static/images/interactive_solvers.png
```

また、Franka エンティティを調べることもできます：

```{figure} ../../_static/images/interactive_franka.png
```
ここでは、このエンティティが持つすべての `geoms`（形状）や `links`（リンク）、および関連情報が表示されます。さらにもう一層掘り下げて、`franka.links[0]` と入力してみましょう：

```{figure} ../../_static/images/interactive_link.png
```

ここでは、このリンクに含まれる衝突形状（`geoms`）、視覚形状（`vgeoms`）、そのほか重要な情報、例えば `inertial_mass`（慣性質量）、シーン内でのリンクのグローバルインデックス（`idx`）、所属するエンティティ（`entity`、ここでは Franka アームエンティティ）、そのジョイント（`joint`）などが表示されます。

この情報豊富なインターフェースが、デバッグプロセスをより簡単にする手助けになることを願っています！