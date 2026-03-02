# 🧩 非剛体ダイナミクス

このページでは、Genesis の連続体/離散ソルバーで実装されている物理モデルを簡潔に整理します。
重点は Python API ではなく、*どの方程式をどのように解いているか* です。
カップリング理論は専用章 *Solvers & Coupling* を参照してください。

---

## 1. オイラー系 Stable-Fluid（安定流体）ソルバー（`SFSolver`）

**目的**: 固定グリッド上での高速な煙/気体シミュレーション。

**支配方程式** – 非圧縮 Navier–Stokes。

**アルゴリズム** – Jos Stam の *Stable Fluids*:

1. **移流（Advection）** – 速度場を 3 次 RK で逆追跡し補間（`backtrace` + `trilerp`）。数値的に無条件安定。
2. **外力インパルス** – 移流後にジェット源から運動量を注入。
3. **粘性/減衰** – 任意の指数減衰項。
4. **圧力投影** – Jacobi 反復（`pressure_jacobi`）で Poisson 方程式を解く。
5. **境界条件** – 固体面で成分ミラーリングにより法線方向速度をゼロ化。

すべてのステップが陽的または対角陰的のため、大きい時間刻みでも頑健で、リアルタイム用途に適します。

---

## 2. Material Point Method（マテリアルポイント法）ソルバー（`MPMSolver`）

**目的**: 粒子 + 背景グリッドにより、固体・液体・粒状体を統一的にシミュレーション。

**基本アイデア**: 連続体の運動量方程式はオイラー格子上で評価し、
変形勾配や塑性ひずみなどの履歴量はラグランジュ粒子に保持します。

### 2.1 更新シーケンス（APIC / CPIC 変種）

| フェーズ | 説明 |
|-------|-------------|
| P2G | B-spline 重みで質量と運動量を近傍グリッドへ転送し、応力寄与を加算 |
| グリッド解法 | 質量で割って速度を求め、重力と境界衝突を適用 |
| G2P | グリッド速度を補間して粒子へ戻し、アフィン行列と位置を更新 |
| 極分解（Polar-SVD） | 変形勾配を分解し、材料則により新しい変形勾配を計算 |

### 2.2 構成則モデル

Genesis は複数の解析的応力関数を提供します。

* **Neo-Hookean elastic**（チョーク/雪）
* **Von Mises capped plasticity**（雪の塑性）
* **Weakly compressible liquid**（WC 流体）
* **Anisotropic muscle**（能動繊維応力付き）

---

## 3. Finite Element Method（有限要素法）ソルバー（`FEMSolver`）

**目的**: 四面体メッシュによる高品質な変形体シミュレーション。
剛性材料向けに陰解法積分を選択可能。

### 3.1 エネルギー定式化

全ポテンシャルエネルギー:

$$ \Pi(\mathbf x) = \sum_{e} V_{e}\,\psi(\mathbf F_e) - \sum_{i} m_{i}\,\mathbf g\!\cdot\!\mathbf x_i. $$

第一変分で内部力、第二変分で要素剛性を得ます。

### 3.2 後退オイラー陰解法

現在状態 $(\mathbf x^n, \mathbf v^n)$ から、Newton–Raphson で $\mathbf x^{n+1}$ を解きます。

$$ \mathbf r(\mathbf x) = \frac{m}{\Delta t^{2}}(\mathbf x - \hat{\mathbf x}) + \frac{\partial \Pi}{\partial \mathbf x} = 0,$$
ここで $\hat{\mathbf x} = \mathbf x^{n} + \Delta t\,\mathbf v^{n}$ は慣性予測です。

各 Newton ステップで $\mathbf H\,\delta \mathbf x = -\mathbf r$ を PCG で解きます。
$\mathbf H$ は整合剛性 + 質量行列です。
前処理には頂点ごとの 3×3 ブロック逆行列を使う block-Jacobi を用います。
ラインサーチ（Armijo バックトラッキング）でエネルギー減少を保証します。

---

## 4. Position-Based Dynamics（位置ベース力学）ソルバー（`PBDSolver`）

**目的**: リアルタイムのクロス、弾性ロッド、XPBD 流体、粒子群。

### 4.1 XPBD 積分サイクル

1. **予測（Predict）** – 陽的オイラー:
   $\mathbf v^{*}\!=\!\mathbf v + \Delta t\,\mathbf f/m$、
   $\mathbf x^{*}\!=\!\mathbf x + \Delta t\,\mathbf v^{*}$。
2. **制約投影（Project constraints）** – 辺、四面体、SPH 密度などを反復処理。
   各制約 $C(\mathbf x)\!=\!0$ に対してラグランジュ乗数 λ を解く:

   $$ \Delta\mathbf x = -\frac{C + \alpha\,\lambda^{old}}{\sum w_i\,|\nabla\!C_i|^{2}+\alpha}\,\nabla\!C, \quad \alpha = \frac{\text{compliance}}{\Delta t^{2}}. $$

3. **速度更新（Update velocities）** –
   $\mathbf v = (\mathbf x^{new}-\mathbf x^{old})/\Delta t$。

### 4.2 対応制約

* 伸長 / 曲げ（クロス）
* 体積保持（XPBD 四面体）
* 非圧縮 SPH 密度制約 + 粘性制約（流体 PBD）
* 位置補正 + クーロンモデルによる衝突・摩擦

---

## 5. Smoothed Particle Hydrodynamics（SPH）ソルバー（`SPHSolver`）

**目的**: WCSPH または DFSPH 圧力ソルバーによる粒子ベース流体。

### 5.1 カーネル

三次スプラインカーネル $W(r,h)$ と勾配 $\nabla W$。
サポート半径は $h=$ `_support_radius`。

### 5.2 弱圧縮性 SPH（WCSPH）

* 状態方程式: $p_i = k\bigl[(\rho_i/\rho_0)^{\gamma}-1\bigr]$。
* 運動方程式:

  $$ \frac{d\mathbf v_i}{dt} = -\sum_j m_j \left( \frac{p_i}{\rho_i^2} + \frac{p_j}{\rho_j^2} \right) \nabla W_{ij} + \mathbf g + \mathbf f_{visc} + \mathbf f_{surf}. $$

### 5.3 発散フリー SPH（DFSPH）

* 解法を **divergence pass**（$\nabla\!\cdot\mathbf v = 0$）と
  **density pass**（$\rho\!=\!\rho_0$）に分離。
* どちらのパスも Jacobi 反復で粒子ごとの圧力係数 κ を求め、*DFSPH factor* フィールドを使用。
* WCSPH より大きい時間刻みで非圧縮性を維持できます。

---

### 参考文献

* Stam, J. "Stable Fluids", SIGGRAPH 1999.
* Zhu, Y.⁠ & Bridson, R. "Animating Sand as a Fluid", SIGGRAPH 2005.
* Gao, T. et al. "Robust Simulation of Deformable Solids with Implicit FEM", SIGGRAPH 2015.
* Macklin, M. et al. "Position Based Fluids", SIGGRAPH 2013.
* Bender, J. et al. "Position Based Dynamics", 2014.
* Bavo et al. "Divergence-Free SPH", Eurographics 2015.
