# 🪐 可微分仿真

（建设中。更多细节即将推出）

## genesis.Tensor

我们现在有了自己的张量数据类型：`genesis.Tensor()`，原因如下：

- 确保一致的用户体验 :)
- 它使得从损失到动作输入的端到端梯度流成为可能
- 创建张量时无需指定数据类型（尽管你仍然可以），调用 `gs.init()` 时指定的数据类型将在创建 genesis 张量时使用
- 提供额外的安全检查，例如连续性检查和检查不同场景的张量是否意外地合并到同一个计算图中
- 支持其他潜在的自定义需求

这本质上是 PyTorch 张量的子类，因此用户可以简单地将其视为 torch 张量，并应用各种 torch 操作。

在 PyTorch 中，推荐的创建张量的方法是调用 `torch.tensor` 和其他张量创建操作，如 `torch.rand`、`torch.zeros`、`torch.from_numpy` 等。我们旨在在 genesis 中重现相同的体验，genesis 张量可以通过简单地将 `torch` 替换为 `genesis` 来创建，例如：

```
x = gs.tensor([0.5, 0.73, 0.5])
y = gs.rand(size=(horizon, 3), requires_grad=True)
```

以这种方式创建的张量是叶子张量，在反向传播后可以通过 `tensor.grad` 访问它们的梯度。混合使用 torch 和 genesis 张量的 PyTorch 操作将自动生成 genesis 张量。

不过，存在一些细微的差异：

- 类似于 torch，genesis 张量创建会根据参数（无论是 int 还是 float）自动推断张量的数据类型，但随后会转换为在 `gs.init()` 中指定的精度的 float 或 int 类型。
- 用户也可以覆盖数据类型，现在我们支持在调用张量创建操作时使用 `dtype=int` 或 `dtype=float`。
- 所有 genesis 张量都在 cuda 上，因此不允许选择设备。这意味着与 `torch.from_numpy` 不同，`genesis.from_numpy` 直接为你提供 cuda 上的张量。
- `genesis.from_torch(detach=True)`：这会根据 torch 张量创建 genesis 张量。当调用此方法时，如果 `detach` 为 True，返回的 genesis 张量将是一个新的叶子节点，从 PyTorch 的计算图中分离出来。如果 `detach` 为 False，返回的 genesis 张量将连接到上游的 torch 计算图中，在调用反向传播时，梯度将一直流回连接的 PyTorch 张量。默认情况下，我们应该纯粹使用 genesis 张量，但这允许与基于 PyTorch 构建的上游应用程序进行潜在集成，例如训练神经策略。
- 每个 genesis 张量对象都有一个 `scene` 属性。任何从它派生的子张量都会继承相同的场景。这让我们能够跟踪梯度流的来源。

    ```python
    state = scene.get_state()
    # state.pos 是一个 genesis 张量
    print(state.pos.scene) # 输出: <class 'genesis.engine.scene.Scene'> id: 'e1a95be2-0947-4dcb-ad02-47b8541df0a0'
    random_tensor = gs.rand(size=(), requires_grad=True)
    print(random_tensor.scene) # 输出: None
    pos_ = state.pos + random_tensor
    print(pos_.scene) # 输出: <class 'genesis.engine.scene.Scene'> id: 'e1a95be2-0947-4dcb-ad02-47b8541df0a0'
    ```

    如果 `tensor.scene` 为 `None`，`tensor.backward()` 的行为与 torch 张量的 `backward()` 完全相同。否则，它将允许梯度流回 `tensor.scene` 并触发上游梯度流。
- 为了模仿 torch 的行为，如 `nn.Module.zero_grad()` 或 `optimizer.zero_grad()`，你也可以对 genesis 张量执行 `tensor.zero_grad()`。

