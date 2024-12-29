# 👋🏻 Genesisの使い方

```{figure} ../../_static/images/hello_genesis.png
```

このチュートリアルでは、1つのFrankaアームを読み込んで床に自由落下させる基本的な例を通じて、Genesisでシミュレーション実験を作成するための核となるステップと基本的な概念を説明します：

```python
import genesis as gs
gs.init(backend=gs.cpu)

scene = gs.Scene(show_viewer=True)
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

scene.build()

for i in range(1000):
    scene.step()
```
これが**完全なスクリプト**です！このような例は10行未満のコードですが、Genesisを使用してシミュレーション実験を作成するために必要なすべてのステップが含まれています。

一緒にステップ毎に見ていきましょう：

#### 初期化
最初のステップはgenesisをインポートして初期化することです：
```python
import genesis as gs
gs.init(backend=gs.cpu)
```
- **バックエンドデバイス**: Genesisはクロスプラットフォームとして設計されており、様々なバックエンドデバイスをサポートしています。ここでは`gs.cpu`を使用しています。[並列シミュレーション](parallel_simulation.md)のためにGPUアクセラレーションが必要な場合は、`gs.cuda`、`gs.vulkan`、`gs.metal`などの他のバックエンドに切り替えることができます。また、`gs.gpu`をショートカットとして使用することもでき、Genesisはシステムに基づいてバックエンドを選択します（例：CUDAが利用可能な場合は`gs.cuda`、Apple Siliconデバイスの場合は`gs.metal`）。
- **精度レベル**: デフォルトでは、Genesisはf32精度を使用します。より高い精度レベルが必要な場合は、`precision='64'`を設定してf64に変更できます。
- **ロギングレベル**: Genesis初期化後、ターミナルにシステム情報やGenesisの現在のバージョンなどのGenesis関連情報を示すロガー出力が表示されます。`logging_level`を`'warning'`に設定することで、ロガー出力を抑制できます。
- **カラースキーム**: Genesisロガーで使用されるデフォルトのカラーテーマは、暗い背景のターミナル用に最適化されています（`theme='dark'`）。明るい背景のターミナルを使用している場合は`'light'`に変更するか、白黒派の場合は単純に`'dumb'`を使用できます。

より詳細な`gs.init()`の呼び出し例は以下のようになります：
```python
gs.init(
    seed                = None,
    precision           = '32',
    debug               = False,
    eps                 = 1e-12,
    logging_level       = None,
    backend             = gs_backend.gpu,
    theme               = 'dark',
    logger_verbose_time = False
)
```

#### シーンの作成
Genesis内のすべてのオブジェクト、ロボット、カメラなどはGenesis `Scene`に配置されます：
```python
scene = gs.Scene()
```
シーンは、すべての基礎となる物理ソルバーを処理する`simulator`オブジェクトと、可視化関連の概念を管理する`visualizer`オブジェクトをラップします。詳細とAPIについては[`Scene`](../../api_reference/scene/scene.md)を参照してください。

シーンを作成する際には、様々な物理ソルバーのパラメータを設定できます。より複雑な例は以下のようになります：
```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        gravity=(0, 0, -10.0),
    ),
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
)
```
この例では、各ステップのシミュレーション`dt`を0.01秒に設定し、重力を設定し、インタラクティブビューアーの初期カメラポーズを設定しています。

#### シーンへのオブジェクトの読み込み
この例では、1つの平面と1つのFrankaアームをシーンに読み込みます：
```python
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
```
Genesisでは、すべてのオブジェクトとロボットは[`Entity`](../../api_reference/entity/index.md)として表現されます。Genesisは完全にオブジェクト指向で設計されているため、ハンドルやグローバルIDを使用する代わりに、これらのエンティティオブジェクトのメソッドを直接使用して操作することができます。

`add_entity`の最初のパラメータは[`morph`](../../api_reference/options/morph/index.md)です。Genesis内のmorphはハイブリッドな概念で、エンティティのジオメトリと姿勢情報の両方をカプセル化しています。異なるmorphを使用することで、形状プリミティブ、メッシュ、URDF、MJCF、地形、またはソフトロボット記述ファイルからGenesisエンティティをインスタンス化できます。

morphを作成する際には、位置、方向、サイズなどを追加で指定できます。方向については、morphは`euler`（scipyの外因性x-y-z規約）または`quat`（w-x-y-z規約）のいずれかを受け入れます。例は以下のようになります：
```python
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (0, 0, 0),
        euler = (0, 0, 90), # scipyの外因性x-y-z回転規約に従います（度単位）
        # quat  = (1.0, 0.0, 0.0, 0.0), # 四元数にはw-x-y-z規約を使用します
        scale = 1.0,
    ),
)
```

現在、以下のような異なる種類の形状プリミティブをサポートしています：
- `gs.morphs.Plane`
- `gs.morphs.Box`
- `gs.morphs.Cylinder`
- `gs.morphs.Sphere`

また、移動タスクのトレーニングのために、`gs.morphs.Terrain`を介して様々な種類の組み込み地形やユーザーが与えた高度マップから初期化された地形もサポートしています。これについては後のチュートリアルで説明します。

以下を含む異なる形式の外部ファイルからの読み込みをサポートしています：
- `gs.morphs.MJCF`: mujoco `.xml`ロボット設定ファイル
- `gs.morphs.URDF`: `.urdf`で終わるロボット記述ファイル（Unified Robotics Description Format）
- `gs.morphs.Mesh`: 非関節メッシュアセット、サポートされる拡張子には以下が含まれます：`*.obj`、`*.ply`、`*.stl`、`*.glb`、`*.gltf`

外部ファイルから読み込む場合は、`file`パラメータでファイルの場所を指定する必要があります。これを解析する際、*絶対*パスと*相対*パスの両方をサポートしています。Genesisには内部アセットディレクトリ（`genesis/assets`）も付属しているため、相対パスが使用されている場合、現在の作業ディレクトリに対する相対パスだけでなく、`genesis/assets`の下も検索します。したがって、この例では、Frankaモデルを`genesis/assets/xml/franka_emika_panda/panda.xml`から取得します。

:::{note}
Genesisの開発中、できるだけ多くのファイル拡張子をサポートするよう努めてきました。これにはレンダリングのための関連テクスチャの読み込みのサポートも含まれます。上記以外のファイルタイプのサポートが必要な場合や、テクスチャが正しく読み込まれないまたはレンダリングされない場合は、機能リクエストをお寄せください！
:::

外部**URDF**ファイルを使用してFrankaアームを読み込む場合は、単にmorphを`gs.morphs.URDF(file='urdf/panda_bullet/panda.urdf', fixed=True)`に変更するだけです。MJCFファイルはロボットのベースリンクと`world`を接続するジョイントタイプを既に指定しているのに対し、URDFファイルにはこの情報が含まれていないことに注意してください。したがって、デフォルトでは、URDFロボットツリーのベースリンクは`world`から切り離されています（より正確には、6自由度の`free`ジョイントを介して`world`に接続されています）。そのため、ベースリンクを固定したい場合は、`morphs.URDF`と`morphs.Mesh`に対して追加で`fixed=True`を指定する必要があります。

#### シーンのビルドとシミュレーションの開始
```python
scene.build()
for i in range(1000):
    scene.step()
```
すべてが追加されたので、シミュレーションを開始できます。`scene.build()`を呼び出してシーンを***ビルド***する必要があることに注意してください。これは、Genesisが実行時にGPUカーネルをその場でコンパイルするためのジャストインタイム（JIT）技術を使用しているためです。そのため、すべてを適切に配置し、デバイスメモリを割り当て、シミュレーション用の基礎となるデータフィールドを作成するための明示的なステップが必要です。

シーンがビルドされると、シーンを可視化するためのインタラクティブビューアーがポップアップします。ビューアーには、ビデオ録画、スクリーンショット、異なる可視化モード間の切り替えなど、様々なキーボードショートカットが用意されています。可視化に関する詳細は、このチュートリアルの後半で説明します。

:::{note}
**カーネルのコンパイルとキャッシング**

JITの性質上、新しい設定（異なるロボットタイプ、異なるオブジェクト数など、内部データ構造のサイズ変更を伴うもの）でシーンを作成するたびに、Genesisはその場でGPUカーネルを再コンパイルする必要があります。Genesisはコンパイル済みカーネルの自動キャッシングをサポートしています：最初の実行後（正常に終了するか`ctrl + c`で終了した場合。`ctrl + \`では**ない**）、シーン設定が同じままであれば、シーン作成プロセスを高速化するために以前の実行からキャッシュされたカーネルを読み込みます。

私たちは並列コンパイルやより高速なカーネルシリアライゼーションなどの技術を追加することで、このコンパイルステップの最適化に積極的に取り組んでいます。そのため、将来のリリースでこのステップの速度が大幅に向上することが期待されます。
:::

これで例全体を説明しました。次に、Genesisの可視化システムについて詳しく見て、ビューアーを操作してカメラを追加してみましょう。