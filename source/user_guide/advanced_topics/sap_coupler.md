# 🔧 SAP カップラー

Genesis は、剛体-FEM 接触を高精度に扱う Semi-Analytic Primal（SAP）カップリングを提供します。

## 要件

```python
import genesis as gs

# 64-bit 精度が必須
gs.init(backend=gs.gpu, precision="64")
```

## 基本設定

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),  # 必須
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

## 主要パラメータ

| パラメータ | 既定値 | 説明 |
|-----------|---------|-------------|
| `n_sap_iterations` | 5 | ステップあたり SAP 反復回数 |
| `n_pcg_iterations` | 100 | PCG ソルバー最大反復回数 |
| `sap_convergence_atol` | 1e-6 | 絶対収束許容値 |
| `sap_convergence_rtol` | 1e-5 | 相対収束許容値 |
| `sap_taud` | 0.1 | 散逸の時定数 |
| `hydroelastic_stiffness` | 1e8 | 水弾性接触剛性 |
| `point_contact_stiffness` | 1e8 | 点接触剛性 |
| `enable_rigid_fem_contact` | True | 剛体-FEM カップリング有効化 |

## 接触タイプオプション

| パラメータ | 値 | 説明 |
|-----------|--------|-------------|
| `fem_floor_contact_type` | "tet", "vert", "none" | FEM-床接触方式 |
| `rigid_floor_contact_type` | "tet", "vert", "none" | 剛体-床接触 |
| `rigid_rigid_contact_type` | "tet", "none" | 剛体-剛体接触 |

- **"tet"**: デフォルト。四面体化ベース（最も高精度）
- **"vert"**: 非常に粗いメッシュ向け
- **"none"**: 接触タイプ無効化

## ロボット把持の例

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    rigid_options=gs.options.RigidOptions(enable_self_collision=False),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True, pcg_threshold=1e-10),
    coupler_options=gs.options.SAPCouplerOptions(
        pcg_threshold=1e-10,
        sap_convergence_atol=1e-10,
        sap_convergence_rtol=1e-10,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(radius=0.02, pos=(0.65, 0.0, 0.02)),
    material=gs.materials.FEM.Elastic(model="linear_corotated", E=1e5, nu=0.4),
)
```

## FEM シミュレーション

```python
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.0, 0.0, 0.1), radius=0.1),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4, model="linear_corotated"),
)
```

## SAP を使うべき場面

**SAP が適するケース:**
- 剛体-FEM 相互作用（変形体把持など）
- Hydroelastic 接触モデル
- 高精度要件
- 変形体を含むマニピュレーションタスク

**LegacyCoupler が適するケース:**
- 複数粒子ソルバー（MPM, SPH, PBD）
- 微分可能シミュレーション（SAP は勾配非対応）
- 剛体のみシミュレーション

## パフォーマンス

- **収束が速い**: LegacyCoupler の 150 ステップに対し 40 ステップ
- **精度が高い**: 位置誤差 ~1e-3（LegacyCoupler は ~5e-3）
- **トレードオフ**: 64-bit 精度と FEM 陰解法ソルバーが必要

## 制限事項

- Rigid + FEM ソルバーのみ対応
- 64-bit 精度（`precision="64"`）必須
- FEM は陰解法ソルバー必須
- 微分可能シミュレーションの勾配は未対応
