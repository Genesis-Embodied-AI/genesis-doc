# 📦 USD シーンの読み込み

Genesis は Universal Scene Description（USD: 汎用シーン記述）ファイルからの複雑なシーン読み込みをサポートします。
これにより、適切な物理特性と関節設定を備えたアーティキュレートロボット、剛体オブジェクト、環境全体をインポートできます。
USD は Pixar が開発したオープンソースフレームワークで、3D ワールドの記述・構成・シミュレーション・共同作業に使われます。

このチュートリアルでは、Genesis で USD ファイルを読み込み、パースオプションを設定し、USD ベースのシーンを扱う方法を説明します。
パーサは NVIDIA Isaac Sim などの一般的ツールから出力されたアセットとスムーズに連携するよう設計されており、標準 USD physics schema にも対応しています。

## インストール

USD アセットを Genesis シーンへ読み込むには、必要な依存関係をインストールします。

```bash
pip install -e .[usd]
```

### オプション: USD マテリアルベイク

`UsdPreviewSurface` を超える高度なマテリアル解析が必要な場合、オプションで Omniverse Kit をインストールできます。
この機能は Python 3.10 / 3.11 かつ GPU バックエンドでのみ利用可能です。
（Python 3.12 では大半のマテリアルが成功する可能性はありますが、一部未ベイクが残ることがあります。）

```bash
pip install --extra-index-url https://pypi.nvidia.com/ omniverse-kit
export OMNI_KIT_ACCEPT_EULA=yes
```

**注:** EULA 受諾のため `OMNI_KIT_ACCEPT_EULA` 環境変数を設定する必要があります。これは一度だけ必要です。
USD ベイクを無効化した場合、Genesis は `UsdPreviewSurface` 型マテリアルのみ解析します。

Genesis の警告 "Baking process failed: ..." が出る場合のトラブルシュート:

- **EULA 受諾**: 初回起動で Omniverse EULA 受諾が必要な場合があります。実行中に受諾するか、`OMNI_KIT_ACCEPT_EULA=yes` を設定してください。
- **IOMMU 警告**: 初回起動時に "IOMMU Enabled" 警告ウィンドウが出ることがあります。タイムアウト回避のため速やかに "OK" を押してください。
- **初回インストール**: 初回起動で追加依存の導入が走り、タイムアウトすることがあります。導入完了後に再実行すれば、2 回目以降は再導入されません。
- **複数 Python 環境**: 複数環境（特に Python バージョン違い）を使っていると Omniverse 拡張が競合する場合があります。共有拡張フォルダ（Linux では `~/.local/share/ov/data/ext` など）を削除して再試行してください。

## 概要

Genesis の USD パーサは次の機能をサポートします。

### 関節タイプ

- **Revolute Joints** (`UsdPhysics.RevoluteJoint`): 角度制限付き回転関節
- **Prismatic Joints** (`UsdPhysics.PrismaticJoint`): 距離制限付き直動関節
- **Spherical Joints** (`UsdPhysics.SphericalJoint`): 3 回転自由度を持つ球関節
- **Fixed Joints** (`UsdPhysics.FixedJoint`): リンク間の固定接続
- **Free Joints** (`UsdPhysics.Joint` with type "PhysicsJoint"): 並進・回転とも自由な 6-DOF 関節

### 物理プロパティ

- **Joint limits**（下限/上限）: revolute と prismatic に対応
- **Joint friction** (`dofs_frictionloss`): revolute / prismatic / spherical に対応
- **Joint armature** (`dofs_armature`): revolute / prismatic / spherical に対応
- **Joint stiffness** (`dofs_stiffness`): revolute / prismatic の受動特性として対応
- **Joint damping** (`dofs_damping`): revolute / prismatic の受動特性として対応
- **Drive API** (`dofs_kp`, `dofs_kv`, `dofs_force_range`): revolute / prismatic / spherical の PD 制御パラメータに対応

### ジオメトリ

- **Visual geometries**: 視覚パターンに一致する USD geometry prim から解析
- **Collision geometries**: 衝突パターンに一致する USD geometry prim から解析

### マテリアルとレンダリング

- **UsdPreviewSurface**: diffuse color / opacity / metallic / roughness / emissive / normal map / IOR に完全対応
- **Material baking**: **UsdPreviewSurface** 以外の複雑マテリアル向けに Omniverse Kit でオプション対応
- **Display colors**: マテリアルがない場合は `displayColor` へフォールバック

## 基本例

まずはアーティキュレートオブジェクトを含む USD ファイルを読み込むシンプルな例です。

```python
import genesis as gs
from huggingface_hub import snapshot_download

# Genesis を初期化
gs.init(backend=gs.cpu)

# シーンを作成
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    show_viewer=True,
)

# USD アセットをダウンロード（Genesis assets の例）
asset_path = snapshot_download(
    repo_type="dataset",
    repo_id="Genesis-Intelligence/assets",
    revision="c50bfe3e354e105b221ef4eb9a79504650709dd2",
    allow_patterns="usd/Refrigerator055/*",
    max_workers=1,
)

# USD ステージを読み込む
entities = scene.add_stage(
    morph=gs.morphs.USD(
        file=f"{asset_path}/usd/Refrigerator055/Refrigerator055.usd",
    ),
)

# ビルドしてシミュレーション
scene.build()
```

USD ファイルには、単一ファイル内に複数の剛体エンティティ（アーティキュレーションと剛体）を含められます。
Genesis では USD 読み込みに 2 つの方法があります。

- **`scene.add_stage()`**: USD 内の **すべて** の剛体エンティティを自動検出して読み込みます。複数エンティティを含むシーン全体を読み込む推奨方法です。

- **`scene.add_entity()`**: USD から **単一** エンティティを読み込みます。`prim_path` 未指定時は stage の default prim を使用します。特定 prim を対象にする場合は `prim_path` を指定します。

## USD Morph 設定

`gs.morphs.USD` クラスには、USD ファイルのパース方法を制御するための詳細オプションがあります。

### 関節ダイナミクス設定

Genesis は USD 属性から関節プロパティをパースできます。

関節物理プロパティの一部は USD 標準に含まれないため、Genesis は属性名候補のデフォルトセットを提供します。
特に Isaac Sim で使われる `physxJoint:jointFriction`、`physxLimit:angular:stiffness` などのカスタム属性に対応します。

以下は関節摩擦の属性名候補を設定する例です。パーサは候補を順に試し、見つかった最初の属性を使用します。

```python
gs.morphs.USD(
    file="robot.usd",
    # Joint friction attributes (tried in order)
    joint_friction_attr_candidates=[
        "physxJoint:jointFriction",  # Isaac Sim compatibility
        "physics:jointFriction",
        "jointFriction",
        "friction",
    ],
)
```

対応属性は次表のとおりです。

| Genesis 属性名 | 参照元 / 既定の属性名候補 | 説明 |
|----------------|-------------|-------------|
| `dofs_frictionloss` | `["physxJoint:jointFriction", "physics:jointFriction", "jointFriction", "friction"]` | 関節摩擦（受動特性） |
| `dofs_armature` | `["physxJoint:armature", "physics:armature", "armature"]` | 関節アーマチュア（受動特性） |
| `dofs_kp` | `"physics:stiffness"` | PD 制御の比例ゲイン（kp、DriveAPI 由来） |
| `dofs_kv` | `"physics:angular:damping"` | PD 制御の微分ゲイン（kv、DriveAPI 由来） |
| `dofs_stiffness` | **回転関節:** `["physxLimit:angular:stiffness", "physics:stiffness", "stiffness"]`<br>**直動関節:** `["physxLimit:linear:stiffness", "physxLimit:X:stiffness", "physxLimit:Y:stiffness", "physxLimit:Z:stiffness", "physics:linear:stiffness", "linear:stiffness"]` | 関節剛性（受動特性、関節タイプ依存） |
| `dofs_damping` | **回転関節:** `["physxLimit:angular:damping", "physics:angular:damping", "angular:damping"]`<br>**直動関節:** `["physxLimit:linear:damping", "physxLimit:X:damping", "physxLimit:Y:damping", "physxLimit:Z:damping", "physics:linear:damping", "linear:damping"]` | 関節減衰（受動特性、関節タイプ依存） |

`[...]` 内の属性名は非公式 USD 属性で、必要に応じて候補を独自設定できます。
一方、`...`（角括弧なし）の属性名は公式 USD 属性で、USD ファイルから直接パースされます。

### ジオメトリ解析オプション

Genesis は USD から collision / visual ジオメトリを解析できます。
どの prim を collision-only / visual-only とみなすかを、正規表現パターンで指定できます。
パーサは `re.match()` を使い、文字列先頭から各パターン一致を判定します。

**認識ルール:**

1. **パターン一致**: パーサは prim 階層を再帰走査します。各 prim 名を順番にパターン照合し、
   一致した時点で visual-matched / collision-matched としてマークします。
   この分類は子孫 prim へ再帰的に継承されます。

2. **ジオメトリ分類**:
   - visual パターン一致 prim は visual-only（衝突判定には不使用）
   - collision パターン一致 prim は collision-only（可視化には不使用）
   - 両方一致 prim は visual / collision 両方として扱う
   - どちらにも一致しない prim も visual / collision 両方として扱う（メッシュのみ USD の既定動作）

3. **Visibility と Purpose（可視性と用途）**: 可視 prim（`invisible` でないもの）のみ解析します。
   purpose が `guide` の prim は visual から除外されますが、collision にはなれます。

**設定例:**

```python
gs.morphs.USD(
    file="robot.usd",
    # Regex patterns to identify collision meshes (tried in order)
    collision_mesh_prim_patterns=[
        r"^([cC]ollision).*",  # Matches prims starting with "Collision" or "collision"
    ],
    # Regex patterns to identify visual meshes
    visual_mesh_prim_patterns=[
        r"^([vV]isual).*",     # Matches prims starting with "Visual" or "visual"
    ],
)
```

**Stage 構造の例:**

- **剛体上の直接ジオメトリ**: ジオメトリ prim がどのパターンにも一致しないため、visual / collision の両方として扱われます。

    ```usd
    def Cube "Cube" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
    }
    ```
- **visual と collision の子を分離**: 直下の子が一致した場合、その分類がサブツリーに伝播します。

    ```usd
    def Xform "ObjectA" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Cube "Visual"      # Matches visual pattern → visual-only
            {
            }

            def Cube "Collision"   # Matches collision pattern → collision-only
            {
            }
        }
    ```
- **ネスト階層**: 親が一致すると、子孫はすべてその分類を継承します。

    ```usd
    def Xform "ObjectB" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Xform "Visual"     # Matches visual pattern
            {
                def Mesh "Cube"    # Inherits visual-only (entire subtree)
                {
                }
                def Mesh "Sphere"  # Inherits visual-only
                {
                }
            }

            def Xform "Collision" # Matches collision pattern
            {
                def Cube "Cube"   # Inherits collision-only (entire subtree)
                {
                }
            }
        }
    ```
- **パターン不一致**: どのパターンにも一致しない prim は visual / collision 両方として扱われます。
    ```usd
    def Xform "ObjectC" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
        def Mesh "Whatever"  # No pattern match → both visual and collision
        {
        }
    }
    ```


## 次のステップ

- Genesis における [ロボット制御](control_your_robot.md) を学ぶ
- USD ロボット向けの [逆運動学](inverse_kinematics_motion_planning.md) を試す
- USD アセットでの学習向けに [並列シミュレーション](parallel_simulation.md) を確認する
- USD morph オプション詳細は [API リファレンス](../../api_reference/options/morph/file_morph/file_morph.md) を参照する
- 座標系と数理規約の詳細は [規約](conventions.md) を参照する
