# ✍️ 二段階学習によるマニピュレーション

この例では、**強化学習（RL）** と **模倣学習（IL）** を組み合わせた **二段階学習パラダイム** によるロボットマニピュレーションを示します。
中心となる考え方は、まず完全な状態情報を使って **特権的な教師ポリシー** を学習し、その知識を、カメラ観測（および必要に応じてロボットの固有感覚）に依存する **視覚ベースの生徒ポリシー** へ蒸留することです。
このアプローチにより、シミュレーション内で効率よく学習しつつ、特権状態が使えない実機環境へのギャップを埋めることができます。

---

## 環境概要

マニピュレーション環境は次の要素で構成されます。

* **ロボット:** 7-DoF の Franka Panda アーム（平行ジョーグリッパー付き）。
* **物体:** 初期位置・姿勢をランダム化した箱。多様な学習シナリオを確保します。
* **カメラ:** 操作シーンを向いた左右 2 台のステレオ RGB カメラ。ここではバッチレンダリングに [Madrona Engine](https://madrona-engine.github.io/) を使用します。
* **観測:**

  * **特権状態:** エンドエフェクタ姿勢と物体姿勢（教師学習時のみ使用）。
  * **視覚状態:** ステレオ RGB 画像（生徒ポリシーで使用）。
* **行動:** 6-DoF のエンドエフェクタ差分姿勢コマンド（3D 位置 + 姿勢）。
* **報酬:** **キーポイント整列** 報酬を使用します。これはグリッパーと物体の間に参照キーポイントを定義し、把持可能な姿勢に整列するよう促します。

  * この定式化により密な shaping 項を避け、タスク成功を直接符号化できます。
  * ポリシーが目標到達を学習するのに必要なのはこの報酬のみです。

---

## RL 学習（ステージ 1: 教師ポリシー）

第 1 段階では、[RSL-RL library](https://github.com/leggedrobotics/rsl_rl) の **Proximal Policy Optimization（PPO）** を使って教師ポリシーを学習します。

**セットアップ:**

```bash
pip install tensorboard rsl-rl-lib==2.2.4
```

**学習:**

```bash
python examples/manipulation/grasp_train.py --stage=rl
```

**モニタリング:**

```bash
tensorboard --logdir=logs
```

学習が成功した場合、報酬カーブは次のようになります。

```{figure} ../../_static/images/manipulation_curve.png
```

**重要ポイント:**

* **入力:** 特権状態（画像なし）。
* **出力:** エンドエフェクタ行動コマンド。
* **並列化:** 大規模ベクトル化ロールアウト（例: 1024–4096 環境）で高スループット化。
* **報酬設計:** キーポイント整列だけで一貫した把持挙動を獲得可能。
* **結果:** 真値状態情報を前提に安定した把持を学習する軽量 MLP ポリシー。

この教師ポリシーが次段階のデモンストレーション源になります。

---

## 模倣学習（ステージ 2: 生徒ポリシー）

第 2 段階では、RL 教師を模倣する **視覚条件付き生徒ポリシー** を学習します。

**アーキテクチャ:**

* **エンコーダ:** 共有ステレオ CNN エンコーダが視覚特徴を抽出。
* **統合ネットワーク:** 画像特徴と（任意で）ロボット固有感覚を統合。
* **出力ヘッド:**
  * **行動ヘッド:** 6-DoF マニピュレーション行動を予測。
  * **姿勢ヘッド:** 補助タスクとして物体姿勢（xyz + quaternion）を予測。

**学習目的:**

* **損失関数:**
  * 行動 MSE（生徒 vs 教師）。
  * 姿勢損失 = 位置 MSE + クォータニオン距離。
* **データ収集:** 教師によるオンライン監督。必要に応じて **DAgger 方式の補正** を使い、共変量シフトを緩和します。

**結果:** 特権状態にアクセスせず、把持挙動を汎化できる視覚ベースポリシー。

**学習実行:**

```bash
python examples/manipulation/grasp_train.py --stage=bc
```

---

## 評価

教師ポリシー・生徒ポリシーの両方を、可視化あり/なしでシミュレーション評価できます。

* **教師ポリシー（MLP）:**

```bash
python examples/manipulation/grasp_eval.py --stage=rl
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_rl.mp4" type="video/mp4">
</video>

* **生徒ポリシー（CNN+MLP）:**

```bash
python examples/manipulation/grasp_eval.py --stage=bc --record
```

生徒は Mandrona でレンダリングされたステレオカメラ観測を使って環境を認識します。
<video preload="auto" controls="True" width="100%"> <source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_stereo.mp4" type="video/mp4"> </video>


**ログとモニタリング:**

* TensorBoard にメトリクスを記録（`logs/grasp_rl/` または `logs/grasp_bc/`）。
* RL/BC の両段階で定期チェックポイントを保存。

---

## まとめ

この二段階パイプラインは、ロボットマニピュレーションの実践的戦略を示します。

1. **教師ポリシー（RL）:** 完全情報による高効率学習。
2. **生徒ポリシー（IL）:** デモから蒸留された視覚ベース制御。

結果として、学習時のサンプル効率と、現実的な知覚入力への頑健性を両立したポリシーが得られます。
