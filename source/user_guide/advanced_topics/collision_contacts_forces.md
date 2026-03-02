# 💥 剛体衝突検出

Genesis は、剛体向けに高効率かつ高機能な衝突検出/接触生成パイプラインを提供します。
Python 実装は `genesis/engine/solvers/rigid/collider_decomp.py` にあります。
このページでは、コードの理解・拡張・デバッグに必要なアルゴリズム要素を **概念的に** 整理します。

> **対象範囲**: 主に剛体-剛体相互作用です。軟体/粒子衝突は `genesis/engine/coupler.py` など別ソルバー側で処理されます。

---

## パイプライン概要

処理は次の 3 段階で構成されます。

1. **AABB 更新** – 各ジオメトリのワールド座標系 AABB（軸平行境界ボックス）を更新
2. **ブロードフェーズ（Sweep-and-Prune）** – AABB に基づき、非交差ペアを高速除外して *候補* ペアのみ出力
3. **ナローフェーズ** – 生き残った各ペアについて、接触法線・貫入深さ・接触位置などの接触マニフォールドを精密計算

`Collider` は公開メソッド `detection()` で 3 段階を統括します。

```python
collider.detection()  # updates AABBs → SAP broad phase → narrow phase(s)
```

以降で各段階を説明します。

---

## 1 · AABB 更新

ヘルパーカーネル `_func_update_aabbs()` は `RigidSolver._func_update_geom_aabbs()` へ処理を委譲します。
各ジオメトリの *タイトな* ワールド空間 AABB を計算し、`geoms_state[..].aabb_min / aabb_max` に保存します。

毎フレームこれを行う理由:

* 剛体は動くため、境界ボックスも毎フレーム変化する
* AABB 重なり判定は broad phase の土台である

---

## 2 · ブロードフェーズ（Sweep & Prune）

broad phase は `_func_broad_phase()` で実装されます。
古典的 Sweep-and-Prune（Sort-and-Sweep）の *N·log N* 挿入ソート変種です。

1. 各 AABB を単一軸（現在は X）へ射影し、*min*/*max* 端点をソート用バッファへ挿入
2. **Warm-start** – 前フレームからほぼ整列済みなので挿入ソートがほぼ線形化
3. ソート済みバッファを走査し、現在端点と重なる区間の *active set* を維持
4. `min_a` が `max_b` の内側へ入ったら候補ペア `(geom_a, geom_b)` を生成

その後、物理的に不可能または無効化されたペアを追加フィルタします。

* 同一リンク/隣接リンクの除外
* `contype` / `conaffinity` ビットマスク
* どちらもワールド固定リンクのペア除外
* *Hibernation* 対応 – 起床中剛体との衝突以外では休止剛体を無視

生き残ったペアは `broad_collision_pairs` と `n_broad_pairs` に保存されます。

---

## 3 · ナローフェーズ（接触マニフォールド生成）

narrow phase は 4 種の専用カーネルに分かれます。

| カーネル | 実行条件 | 目的 |
|--------|--------------|---------|
| `_func_narrow_phase_convex_vs_convex` | 一般の凸-凸 & 平面-凸 | 既定経路。**MPR**（Minkowski Portal Refinement）を使用し、必要に応じて SDF 問い合わせへフォールバック。`RigidOptions.use_gjk_collision=True` の場合は **GJK** を使用。 |
| `_func_narrow_phase_convex_specializations` | 平面-箱 & 箱-箱 | 解析解を持つ凸形状ペア向け専用ハンドラ |
| `_func_narrow_phase_any_vs_terrain` | 少なくとも一方が *height-field terrain* | 支持セルごとに複数接触点を生成 |
| `_func_narrow_phase_nonconvex_vs_nonterrain` | 少なくとも一方が **非凸** | SDF の頂点/辺サンプリングで mesh↔convex / mesh↔mesh を処理 |

### 3.1 凸-凸

#### 3.1.1 GJK（ギルバート・ジョンソン・キアーシ）

GJK（+EPA）は多くの物理エンジンで使われる接触検出法で、主な利点は次です。

* 分岐の少ない support-mapping により GPU 上で完結しやすい
* 形状ごとに *support function* だけあればよく、面隣接情報や特徴キャッシュが不要
* 非接触時に分離距離を得られる
* 多くの実装で数値的頑健性が検証されている

Genesis では `RigidOptions.use_gjk_collision=True` で有効化されます。
さらに次の工夫で頑健性を強化しています。

* 実行時の simplex/polytope 退化を徹底チェック
* 頑健な面法線推定
* 貫入深さの下限/上限推定を頑健化

support 問い合わせは **事前計算 Support Field** で高速化します（{doc}`Support Field <support_field>` 参照）。

複数接触点生成は、最初の接触法線まわりに小さな姿勢摂動を加えて行います。
各ペアあたり最大 5 接触（`_n_contacts_per_pair = 5`）を保持します。

#### 3.1.2 MPR（Minkowski Portal Refinement）

MPR も広く使われる接触検出法です。
GJK の利点の多くを共有しますが、非衝突時の分離距離は得られず、
実装検証の蓄積が GJK より少ないため、数値誤差や退化に弱くなり得ます。

Genesis では、深い貫入時に SDF フォールバックを入れることで MPR を強化しています。

GJK 同様、MPR も事前計算 Support Field で高速化し、
最初の法線周りの小摂動で複数接触を検出します。
したがって 1 ペアあたり最大 5 接触（`_n_contacts_per_pair = 5`）です。

### 3.2 非凸オブジェクト

三角形メッシュや凸クラスタ分解済み形状には、オフライン焼き込み済み **SDF（符号付き距離場）** を使います。
アルゴリズムは

* 頂点（vertex-face 接触）
* 辺（edge-edge 接触）

をサンプリングし、最深貫入を採用します。
頂点接触が既に見つかれば高コストな辺パスは省略されます。

### 3.3 平面↔箱の特殊処理

箱が平面へ面接触するような退化ケースを避けるため、
MuJoCo の解析的な plane-box / box-box ルーチンを移植しています。

---

## 接触データレイアウト

有効接触は `contact_data`（構造体配列）へ格納されます。

| Field | 意味 |
|-------|---------|
| `geom_a`, `geom_b` | ジオメトリインデックス |
| `penetration` | 正の貫入深さ（≤0 は分離） |
| `normal` | **B から A** へ向くワールド空間単位法線 |
| `pos` | 相互貫入領域の中点 |
| `friction` | 有効クーロン係数（2 形状の最大値） |
| `sol_params` | ソルバー調整定数 |

`n_contacts` は atomic 加算されるため、GPU カーネルが並列に追記できます。

---

## ウォームスタートとキャッシュ

時間的コヒーレンス向上のため、各ジオメトリペアごとに
「前回の最深頂点 ID」と「既知の分離法線」をキャッシュします。
このキャッシュは MPR の初期探索方向に使われ、
broad phase で分離したペアはクリアされます。

---

## ハイバネーション

この機能を有効にすると、休止剛体同士の接触は保持されますが毎フレーム再評価されません（`n_contacts_hibernated`）。
大規模静的背景を含むシーンで GPU 負荷を大きく削減できます。

---

## チューニングパラメータ

| オプション | 既定値 | 効果 |
|--------|---------|--------|
| `RigidSolver._max_collision_pairs` | 4096 | broad-phase ペア数上限（環境ごと） |
| `Collider._mc_perturbation` | `1e-2` rad | 多接触探索時の摂動角 |
| `Collider._mc_tolerance`    | `1e-2` of AABB size  | 重複接触を除外する半径 |
| `Collider._mpr_to_gjk_overlap_ratio` | `0.5` | 一方が他方を包含する際に MPR から SDF へ切り替える閾値 |

---

## 関連ドキュメント

* {doc}`Support Field <support_field>` – support-mapping 形状のオフライン加速構造
