# 🪐 微分可能シミュレーション

（作成中です。詳細は近日公開予定）

## genesis.Tensor
私たち独自のテンソルデータ型である `genesis.Tensor()` を導入しました。以下の理由からです：
- 一貫したユーザー体験を提供するため
- 損失からアクション入力に至るまでのエンドツーエンドの勾配フローを可能にするため
- テンソル作成時にデータ型を指定する必要がなくなるため（もちろん指定することも可能です）。`gs.init()` を呼び出す際に指定されたデータ型が genesis テンソル作成時に使用されます。
- 連続性チェックや異なる Scene からのテンソルが誤って同じ計算グラフにマージされることを防ぐチェックなど、追加の安全チェックを提供します。
- 必要に応じて、他のカスタマイズをサポートするため。

このテンソルは本質的には PyTorch テンソルのサブクラスであるため、ユーザーはこれを単なる torch テンソルとして扱い、さまざまな torch 演算を適用できます。

PyTorch では、テンソルを作成する推奨方法は `torch.tensor` や `torch.rand`、`torch.zeros`、`torch.from_numpy` などのテンソル作成オペレーションを呼び出すことです。genesis ではこれと同じ体験を再現することを目指しており、genesis テンソルは `torch` を `genesis` に置き換えるだけで作成できます。例：

```python
x = gs.tensor([0.5, 0.73, 0.5])
y = gs.rand(size=(horizon, 3), requires_grad=True)
```

この方法で作成されたテンソルは葉テンソルであり、逆伝播後に `tensor.grad` を使ってその勾配にアクセスできます。torch と genesis テンソルを混合して使用する場合、PyTorch の演算は自動的に genesis テンソルを返します。

いくつかの小さな違いも存在します：
- torch と同様に、genesis テンソル作成はパラメータ（整数または浮動小数点数）に基づいてデータ型を自動推定しますが、gs.init() で指定された精度を持つ浮動小数点数または整数型に変換されます。
- データ型を上書きすることも可能で、現在のところテンソル作成オペレーションでは `dtype=int` または `dtype=float` をサポートしています。
- すべての genesis テンソルは CUDA 上にあるため、デバイス選択は許可されていません。このため、`torch.from_numpy` とは異なり、`genesis.from_numpy` は CUDA 上のテンソルを直接返します。
- `genesis.from_torch(detach=True)`：torch テンソルを指定して genesis テンソルを作成します。このとき、detach が True の場合、返される genesis テンソルは PyTorch の計算グラフから切り離された新しい葉ノードになります。detach が False の場合、返される genesis テンソルは上流の torch 計算グラフに接続され、逆伝播時には勾配が接続された PyTorch テンソルにまで流れます。通常は純粋に genesis テンソルを使用することを推奨しますが、これにより、PyTorch 上に構築された上流アプリケーション（例：ニューラルポリシーのトレーニング）との統合が可能になります。
- 各 genesis テンソルオブジェクトには `scene` 属性があります。これから派生した子テンソルは同じ scene を継承します。これにより、勾配フローの出所を追跡することができます。
    ```python
    state = scene.get_state()
    # state.pos は genesis テンソルです
    print(state.pos.scene) # 出力: <class 'genesis.engine.scene.Scene'> id: 'e1a95be2-0947-4dcb-ad02-47b8541df0a0'
    random_tensor = gs.rand(size=(), requires_grad=True)
    print(random_tensor.scene) # 出力: None
    pos_ = state.pos + random_tensor
    print(pos_.scene) # 出力: <class 'genesis.engine.scene.Scene'> id: 'e1a95be2-0947-4dcb-ad02-47b8541df0a0'
    ```
    `tensor.scene` が `None` の場合、`tensor.backward()` は torch テンソルの `backward()` と同じように動作します。それ以外の場合、`tensor.scene` に対して勾配フローが許可され、上流の勾配フローがトリガーされます。
- torch の `nn.Module.zero_grad()` や `optimizer.zero_grad()` のような動作を再現するため、genesis テンソルでは `tensor.zero_grad()` を使用することも可能です。