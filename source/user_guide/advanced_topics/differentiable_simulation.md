# 🪐 可微分仿真

（内容建设中，更多信息即将推出）

## genesis.Tensor

我们引入了自己的张量数据类型 `genesis.Tensor()`，这样做有以下几个原因：

- 提供一致的用户体验 :)
- 实现从损失到动作输入的端到端梯度传播
- 简化张量创建过程（无需手动指定数据类型，系统会使用 `gs.init()` 中的默认设置）
- 增强安全性检查（包括内存连续性检查，防止不同场景的张量意外混合）
- 为未来的定制需求预留扩展空间

genesis.Tensor 是 PyTorch 张量的扩展，您可以像使用普通的 torch 张量一样使用它，支持所有标准的 torch 运算。

创建 genesis 张量非常简单，只需要将 PyTorch 中的 `torch` 替换为 `genesis` 即可：

```python
x = gs.tensor([0.5, 0.73, 0.5])
y = gs.rand(size=(horizon, 3), requires_grad=True)
```

这样创建的张量都是叶子节点，可以通过 `tensor.grad` 属性访问其梯度。当混合使用 torch 和 genesis 张量时，运算结果会自动转换为 genesis 张量。

需要注意以下几点区别：

- 数据类型处理：系统会自动推断数据类型，并转换为 `gs.init()` 中指定的精度
- 类型覆盖：支持通过 `dtype=int` 或 `dtype=float` 手动指定数据类型
- CUDA 优先：所有 genesis 张量默认在 CUDA 设备上运行
- PyTorch 互操作：通过 `genesis.from_torch(detach=True)` 可以实现与 PyTorch 的无缝集成
- 场景追踪：每个 genesis 张量都有场景属性（scene），用于追踪梯度来源：

    ```python
    state = scene.get_state()
    # state.pos 是 genesis 张量
    print(state.pos.scene) # 显示场景ID
    random_tensor = gs.rand(size=(), requires_grad=True)
    print(random_tensor.scene) # 显示 None
    pos_ = state.pos + random_tensor
    print(pos_.scene) # 显示与 state.pos 相同的场景ID
    ```

- 梯度管理：支持 `tensor.zero_grad()` 操作，功能与 PyTorch 中的相同
