# 🗂 設定システム

## 概要

Genesis のシミュレーションフレームワークは、モジュール化され拡張可能な設定システムを中心に構成されています。
このシステムにより、低レベルの物理ソルバーから高レベルのレンダリング設定まで、シミュレーションのさまざまな要素を構造化された設定オブジェクトで柔軟に組み合わせ、制御できます。

これらのコンポーネントがどのように連携するかを理解するために、まず Genesis シーン初期化の典型的なテンプレートを示します。
このテンプレートでは、シミュレーション設定、ソルバー設定、エンティティ単位の設定がどのように編成されるかを確認できます。

```python
# Genesis を初期化
gs.init(...)

# シーンを初期化
scene = gs.Scene(
    # シミュレーションとカップリング
    sim_options=SimOptions(...),
    coupler_options=CouplerOptions(...),

    # ソルバー
    tool_options=ToolOptions(...),
    rigid_options=RigidOptions(...),
    mpm_options=MPMOptions(...),
    sph_options=SPHOptions(...),
    fem_options=FEMOptions(...),
    sf_options=SFOptions(...),
    pbd_options=PBDOptions(...),

    # 可視化とレンダリング
    vis_options=VisOptions(...),
    viewer_options=ViewerOptions(...),
    renderer=Rasterizer(...),
)

# エンティティを追加
scene.add_entity(
    morph=gs.morphs...,
    material=gs.materials...,
    surface=gs.surfaces....,
)
```

上記のように、Genesis のシーンは次の組み合わせで定義されます。

- [シミュレーションとカップリング](#シミュレーションとカップリング): グローバルなシミュレーションパラメータと、異なるソルバー間の相互作用を定義します。
- [ソルバー](#ソルバー): さまざまなシミュレーション手法（例: 剛体、流体、クロス）に対する物理挙動を設定します。
- [可視化とレンダリング](#可視化とレンダリング): 実行時の可視化と最終レンダリングの設定を調整します。
- シーンに追加する各エンティティごとに:
    - [モーフ](#モーフ): エンティティの幾何形状や構造を定義します。
    - [マテリアル](#マテリアル): 対応する物理ソルバーに関連する材質パラメータを定義します。
    - [サーフェス](#サーフェス): 見た目や表面レンダリングを制御します。

## シミュレーションとカップリング

この設定は、シミュレーション全体の構造と異なる物理ソルバーの結合方法を定義します。
時間積分、安定性、ソルバー間の相互運用といった、シミュレーションループの骨格に関わる要素を制御します。

- `SimOptions`: タイムステップ、重力、減衰、数値積分器などのグローバル設定を定義します。
- `CouplerOptions`: マルチフィジクス相互作用を設定します。例えば、剛体ツールと軟体の相互作用、あるいは多孔質材料内の流体挙動などです。

定義: [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py)

## ソルバー

ソルバーは個別の物理モデルを担う中核です。
各ソルバーは、剛体、流体、変形体など、特定の材料や系に対応するシミュレーションアルゴリズムを実装しています。
シナリオに応じて有効化・無効化できます。

- `RigidOptions`: 接触、衝突、拘束を含む剛体ダイナミクス。
- `MPMOptions`: 弾性体、塑性体、粒状体、流体を扱う Material Point Method ソルバー。
- `SPHOptions`: 流体や粒状流れを扱う Smoothed Particle Hydrodynamics ソルバー。
- `FEMOptions`: 弾性体を扱う Finite Element Method ソルバー。
- `SFOptions`: オイラー型の気体シミュレーション向け Stable Fluid ソルバー。
- `PBDOptions`: クロス、体積変形体、液体、粒子を扱う Position-Based Dynamics ソルバー。
- `ToolOptions`: 一時的な設定。将来的に廃止予定です。

定義: [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py)

## 可視化とレンダリング

この設定は、デバッグや開発時のライブ可視化と、デモ・解析・メディア用途の最終レンダリングを制御します。
ユーザーがシミュレーションをどのように視覚的に確認・操作するかを決める部分です。

- `ViewerOptions`: インタラクティブビューアの設定。
- `VisOptions`: ビューアやカメラに依存しない可視化設定。
- `Renderer`（Rasterizer または Raytracer）: ライティング、シェーディング、ポストプロセスを含むレンダリングバックエンドを定義します。

定義: [genesis/options/vis.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/vis.py) および [genesis/options/renderers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/renderers.py)

## モーフ

Morph はエンティティの形状とトポロジーを定義します。
球や箱のようなプリミティブ形状から、アーティキュレートされた構造アセットまでを含みます。
Morph は、材質や物理挙動が作用する幾何学的基盤です。

- `Primitive`: すべての形状プリミティブ系 Morph。
    - `Box`: 箱形状。
    - `Cylinder`: 円柱形状。
    - `Sphere`: 球形状。
    - `Plane`: 平面形状。
- `FileMorph`:
    - `Mesh`: メッシュファイルから読み込む Morph。
        - `MeshSet`: メッシュ集合。
    - `MJCF`: MJCF ファイルから読み込む Morph（剛体エンティティのみ対応）。
    - `URDF`: URDF ファイルから読み込む Morph（剛体エンティティのみ対応）。
    - `Drone`: ドローンエンティティ作成用の URDF Morph。
- `Terrain`: 剛体地形用 Morph。
- `NoWhere`: Emitter 用の予約 Morph（内部利用）。

定義: [genesis/options/morphs.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/morphs.py)

## マテリアル

Material は、物体が物理力にどう応答するかを定義します。
剛性、摩擦、弾性、減衰、ソルバー固有のパラメータを含みます。
また、エンティティが他のオブジェクトやソルバーとどう相互作用するかも決まります。

- `Rigid`: 剛体およびアーティキュレート系。
- `MPM`: マテリアルポイント法（Material Point Method）。
    - `Elastic`
    - `ElastoPlastic`
    - `Liquid`
    - `Muscle`
    - `Sand`
    - `Snow`
- `FEM`: 有限要素法（Finite Element Method）。
    - `Elastic`
    - `Muscle`
- `PBD`: 位置ベース力学（Position Based Dynamics）。
    - `Cloth`
    - `Elastic`
    - `Liquid`
    - `Particle`
- `SF`: 安定流体法（Stable Fluid）。
    - `Smoke`
- `Hybrid`: 剛体スケルトンで軟体スキンを駆動するモデル。
- `Tool`: 一時的な設定で、将来的に廃止予定。

定義: [genesis/engine/materials](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/materials)

## サーフェス

Surface はエンティティの見た目を定義します。
色、テクスチャ、反射、透明度などのレンダリング属性を含みます。
Surface は、エンティティ内部構造とレンダラの間をつなぐ層です。

- `Default`: 基本的には `Plastic`。
- `Plastic`: 最も基本的なサーフェス。
    - `Rough`: 適切なパラメータを設定した粗い表面のショートカット。
    - `Smooth`: 適切なパラメータを設定した滑らかな表面のショートカット。
    - `Reflective`: 既定で灰色の衝突ジオメトリ向けサーフェス。
    - `Collision`: 適切なパラメータを設定した rough plastic のショートカット。
- `Metal`
    - `Iron`: `metal_type = 'iron'` の金属サーフェスショートカット。
    - `Aluminium`: `metal_type = 'aluminium'` の金属サーフェスショートカット。
    - `Copper`: `metal_type = 'copper'` の金属サーフェスショートカット。
    - `Gold`: `metal_type = 'gold'` の金属サーフェスショートカット。
- `Glass`
    - `Water`: 水面用ショートカット（適切な値を持つ Glass サーフェス）。
- `Emission`: 発光サーフェス。

定義: [genesis/options/surfaces.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/surfaces.py)
