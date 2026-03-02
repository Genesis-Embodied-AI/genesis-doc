# 🧮 非剛体カップリング

Genesis では、複数の連続体ソルバーと剛体ソルバーを **同一シーン** で組み合わせられます。
例えば MPM 雪と SPH 水の相互作用、変形 FEM 組織と手術ツールの衝突、粒状床へ飛び込む剛体などです。
ソルバー間相互作用はすべて `gs.engine.Coupler` クラスで統括されます。

このページでは次を説明します。

* Coupler の **アーキテクチャ** と、どのソルバーペアが有効化されるか
* 運動量交換を決める **インパルスベース衝突応答**
* **摩擦、反発、softness** などカップリングパラメータの意味
* 現在対応しているソルバーペアの **早見表**
* 特定相互作用を有効/無効にする **利用例**

---

## 1. アーキテクチャ概要

内部的にシミュレータは **1 つの Coupler インスタンス** を持ち、全ソルバーへの参照を保持します。
各サブステップで次を実行します。

1. `coupler.preprocess(f)`  – 例: CPIC 用サーフェシング
2. `solver.substep_pre_coupling(f)` – 各ソルバーを個別更新
3. `coupler.couple(f)` – ソルバー間で運動量交換
4. `solver.substep_post_coupling(f)` – 衝突後のソルバー後処理

全ソルバーフィールドは Quadrants データ構造上にあるため、Coupler は複数ソルバーのメモリへ **コピーなし** でアクセスする Quadrants `@kernel` を呼べます。

### 1.1 カップリングペア有効化

ペアが有効かどうかは `Coupler.build()` 時に **静的に一度だけ** 決まります。

```python
self._rigid_mpm = rigid.is_active() and mpm.is_active() and options.rigid_mpm
```


## 2. インパルスベース衝突応答

### 2.1 符号付き距離と影響重み

各接触候補に対して、Coupler は剛体ジオメトリの符号付き距離関数 `sdf(p)` を問い合わせます。
*softness* パラメータにより、滑らかなブレンド重みを作ります。

$$
\text{influence} = \min\bigl( \exp\!\left(-\dfrac{\;d\;}{\epsilon}\right) ,\;1 \bigr)
$$

ここで `d` は符号付き距離、`ε = coup_softness` です。
softness が大きいほど接触領域は厚くなり、インパルスは穏やかになります。

### 2.2 相対速度の分解

世界速度 **v** を持つ粒子/グリッドノードと剛体速度 **vᵣ** の **相対速度** は

$$ \mathbf r = \mathbf v - \mathbf v_{\text{rigid}}. $$

これを法線成分と接線成分に分解します。

$$
 r_n = (\mathbf r \cdot \mathbf n)\,\mathbf n, \quad
 r_t = \mathbf r - r_n
$$

ここで **n** は外向き法線です。

### 2.3 法線インパルス（反発）

法線成分が内向き（$r_n<0$）なら、衝突後に

$$ r_n' = -e\,r_n, \quad 0 \le e \le 1, $$

となるようインパルスを加えます。
`e = coup_restitution` は **反発係数** で、`e=0` は完全非弾性、`e=1` は完全弾性です。

### 2.4 接線インパルス（クーロン摩擦）

摩擦は接線成分の **スケーリング** で実装されます。

$$ r_t' = \max\!\bigl( 0,\;|r_t| + \mu \, r_n\bigr) \; \dfrac{r_t}{|r_t|}\,, $$

ここで `μ = coup_friction` です。
これはクーロン摩擦のインパルス型実装で、衝突後の接線速度が静止限界を超えないようにします。

### 2.5 速度更新と運動量移送

新しい粒子/ノード速度は

$$ \mathbf v' = \mathbf v_{\text{rigid}} + (r_t' + r_n') \times \text{influence} + \mathbf r\,(1-\text{influence}). $$

運動量変化

$$ \Delta\mathbf p = m\,(\mathbf v' - \mathbf v) $$

は剛体への **外力** として適用されます。

$$ \mathbf F_{\text{rigid}} = -\dfrac{\Delta\mathbf p}{\Delta t}. $$

これにより作用反作用を満たし、剛体側も流体衝撃に応答します。

---

## 3. サポートされるソルバーペア

| ペア | 方向 | 備考 |
|------|-----------|-------|
| **MPM ↔ Rigid** | グリッドノードに基づくインパルス（CPIC 対応） |
| **MPM ↔ SPH**   | MPM セル内の SPH 粒子速度を平均化 |
| **MPM ↔ PBD**   | SPH 類似だが固定 PBD 粒子は除外 |
| **FEM ↔ Rigid** | 表面頂点のみで衝突 |
| **FEM ↔ MPM**   | MPM の P2G/G2P 重みで運動量交換 |
| **FEM ↔ SPH**   | 実験的（法線射影のみ） |
| **SPH ↔ Rigid** | 法線の side-flip を考慮した安定処理 |
| **PBD ↔ Rigid** | 位置補正後に速度射影 |
| **Tool ↔ MPM**  | 各 Tool エンティティの `collide()` へ委譲 |

表にない組み合わせは現時点で未対応です。

---
