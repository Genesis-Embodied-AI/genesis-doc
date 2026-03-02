# 🚀 サポートフィールド

Genesis における凸形状の衝突判定は、*support function* に強く依存しています。
Minkowski Portal Refinement（MPR）アルゴリズムの各反復では、次のような問い合わせを行います。

> _"方向 **d** が与えられたとき、内積 **v·d** が最大になる頂点はどれか？"_

素朴実装では毎回すべての頂点を走査する必要があり、数千頂点モデルでは非効率です。
これを避けるため、Genesis はシーン初期化時に各凸ジオメトリの **Support Field** を前計算します。
実装は `genesis/engine/solvers/rigid/support_field_decomp.py` にあります。

---

## 仕組み

1. **一様方向グリッド** – 球面を経度/緯度（`θ`, `ϕ`）で `support_res × support_res` 方向へ離散化します。デフォルト `support_res = 180` で、約 32k 方向です。
2. **オフライン投影** – 各方向について *全* 頂点を投影し、内積最大の頂点インデックスを保存します。得られる配列:
   * `support_v ∈ ℝ^{N_dir×3}` – *オブジェクト空間* の頂点座標
   * `support_vid ∈ ℕ^{N_dir}` – 元頂点インデックス（SDF 問い合わせの warm-start に有用）
   * `support_cell_start[i_g]` – ジオメトリごとのフラット配列先頭オフセット
3. **Quadrants Fields** – これら配列を GPU 常駐の Quadrants field へコピーし、ホスト往復なしでカーネルから参照可能にします。

```python
v_ws, idx = support_field._func_support_world(dir_ws, i_geom, i_batch)
```

これで任意方向に対するワールド空間の極点を **O(1)** で取得できます。

---

## データレイアウト

| フィールド | 形状 | 説明 |
|-------|-------|-------------|
| `support_v`         | `(N_cells, 3)` | 頂点座標（float32/64） |
| `support_vid`       | `(N_cells,)`   | 対応頂点インデックス（int32） |
| `support_cell_start`| `(n_geoms,)`   | フラット配列へのオフセット |

!!! info "メモリ使用量"
    デフォルト解像度では各凸形状あたり ≈ 32k × (3 × 4 + 4) = 416 kB を使用します。小さなプリミティブ群では、形状ごとに BVH を構築するより安価です。

---

## 利点

* MPR 中の **定数時間ルックアップ** により GPU 分岐発散を低減
* **GPU フレンドリー** – サポートフィールドは単純な SOA 配列で、複雑なポインタ追跡が不要
* **任意の凸メッシュに適用可能** – 代表軸や境界ボックスに依存しない

## 制限と今後

* 方向グリッドは等方的で非適応のため、角セルより小さな特徴は誤頂点へ割り当てられる可能性があります。
* シーン内ジオメトリ数が多い場合、前処理時間とメモリ消費が大きくなります。

---

## API サマリ

```python
from genesis.engine.solvers.rigid.rigid_solver_decomp import RigidSolver
solver   = RigidSolver(...)
s_field  = solver.collider._mpr._support  # internal handle

v_ws, idx = s_field._func_support_world(dir_ws, i_geom, i_env)
```

`v_ws` は *ワールド空間* のサポート点、`idx` は元メッシュ内の頂点 ID（グローバルインデックス）です。

---

## 衝突パイプラインとの関係

Support Field は *凸-凸* 狭域判定専用の **加速構造** です。
SDF、地形、平面-箱など他の衝突経路は、解析的 support function や距離場を使うためこれを使いません。

MPR への統合詳細は {doc}`Collision, Contacts & Forces <collision_contacts_forces>` を参照してください。
