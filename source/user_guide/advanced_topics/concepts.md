# 🧩 概念

## システムアーキテクチャ概要

```{figure} ../../_static/images/overview.png
```

<!-- ユーザー視点では、Genesis で環境を構築するとは `Scene` に `Entity` を追加することです。`Entity` は次で定義されます。
- `Morph`: エンティティの形状（例: プリミティブ形状や URDF）。
- `Material`: エンティティの材質（例: 弾性体、液体、砂など）。Material は対応するソルバーに関連づけられ、MPM 液体と SPH 液体のように異なる挙動を示します。
- `Surface`: テクスチャやレンダリング表面パラメータなど。

内部的には、シーンは次を内包するシミュレータで構成されます。
- `Solver`: 剛体、MPM、FEM などの手法で物理計算を担う中核ソルバー。
- `Coupler`: ソルバー間の力や相互作用を橋渡しするモジュール。 -->

ユーザー視点では、Genesis で環境を構築するとは `Scene` に `Entity` を追加することです。
各 `Entity` は次で定義されます。
- `Morph`: エンティティの幾何形状（例: キューブ・球などのプリミティブ、URDF/MJCF などのモデル）
- `Material`: 物理特性（弾性体、液体、粒状体など）。マテリアル種別によって使用ソルバーが決まり、例えば液体でも MPM と SPH で挙動が異なります。
- `Surface`: テクスチャ、粗さ、反射率など見た目と相互作用に関わる表面特性

内部的には `Scene` は `Simulator` で駆動され、次を含みます。
- `Solver`: 剛体、MPM、FEM、PBD、SPH など各物理モデルを計算するコアソルバー
- `Coupler`: ソルバー間相互作用を処理し、力の結合やエンティティ間ダイナミクスの整合を取るモジュール


## データインデクシング

「剛体エンティティの一部属性だけを制御/取得するにはどうするか」という質問が多いため、
データへのインデックスアクセスを詳しく説明します。

**構造化データフィールド**。
多くの場合、[Quadrants の struct field](https://docs.taichi-lang.org/docs/type#struct-types-and-dataclass) を使っています。
例として MPM を見ると（[ここ](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L103C1-L107C10) と [ここ](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L123)）、
```
struct_particle_state_render = qd.types.struct(
    pos=gs.qd_vec3,
    vel=gs.qd_vec3,
    active=gs.qd_int,
)
...
self.particles_render = struct_particle_state_render.field(
    shape=self._n_particles, needs_grad=False, layout=qd.Layout.SOA
)
```
これは、各要素が `pos`, `vel`, `active` を持つ構造体である巨大な配列（Quadrants では field）を作っていることを意味します。
このフィールド長は `n_particles` で、シーン内の粒子 **すべて** を含みます。
ではシーンに複数エンティティがある場合、どう区別するか。
各要素へ entity ID タグを持たせる方法もありますが、メモリ配置・計算・I/O の観点で最適とは限りません。
Genesis では代わりに **インデックスオフセット** を使います。

**ローカル/グローバルインデクシング**。
インデックスオフセットにより、直感的なユーザー API（ローカル）と最適化済み内部実装（グローバル）を両立します。
ローカルインデクシングは特定エンティティ内の参照（例: 1 番目の関節、30 番目の粒子）です。
グローバルインデクシングは、シーン内全エンティティを含むソルバーのデータフィールドへの直接ポインタです。

```{figure} ../../_static/images/local_global_indexing.png
```

具体例:
- MPM の場合、`vel=torch.zeros((mpm_entity.n_particles, 3))`（このエンティティの粒子のみ）として [`mpm_entity.set_velocity(vel)`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L296) を呼ぶと、グローバルオフセットは自動抽象化されます。
  内部的には概念的に `mpm_solver.particles[start:end].vel = vel` を行っており、`start` はオフセット（[`mpm_entity.particle_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L453)）、`end` はオフセット + 粒子数（[`mpm_entity.particle_end`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L457)）です。
- 剛体の場合、`*_idx_local` はすべてローカルインデックスです。これらは `entity.*_start + *_idx_local` でグローバルへ変換されます。
  例えば [`rigid_entity.get_dofs_position(dofs_idx_local=[2])`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2201) で 3 番目の dof 位置を取ると、実際には `rigid_solver.dofs_state[2+offset].pos` へアクセスしています。ここで `offset` は [`rigid_entity.dofs_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2717) です。

（関連デザインパターンとして [entity component system (ECS)](https://en.wikipedia.org/wiki/Entity_component_system) も参考になります。）

## データフィールドへの直接アクセス

通常、（Quadrants の）データフィールドへ直接アクセスすることは推奨していません。
基本的には `RigidEntity.get_dofs_position` のようなエンティティ API を使ってください。
ただし API 未対応データが必要で、新 API を待てない場合は、
応急処置として直接アクセスする方法があります（ただし多くの場合は非効率です）。
前節のインデクシングに従うと、例えば
```
entity: RigidEntity = ...
tgt = entity.get_dofs_position(...)
```
は次と等価です。
```
all_dofs_pos = entity.solver.dofs_state.pos.to_torch()
tgt = all_dofs_pos[:, entity.dof_start:entity.dof_end]  # 先頭次元はバッチ次元
```

全エンティティは（hybrid entity を除き）特定ソルバーに紐付きます。
欲しい物理属性はソルバー内部のどこかに保存されます
（例: dof 位置は rigid solver の `dofs_state.pos`）。
対応関係の詳細は {doc}`Naming and Variables <naming_and_variables>` を参照してください。
また、ソルバー内のデータフィールドはすべてグローバルインデクシング（全エンティティ対象）なので、
特定エンティティ分だけ抽出するには `entity.*_start` と `entity.*_end` を使います。
