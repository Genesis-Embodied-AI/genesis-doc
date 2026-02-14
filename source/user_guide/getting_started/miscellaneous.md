# 💡 提示

## 运行性能基准测试

* 在进行性能分析和/或基准测试时，可能需要临时禁用缓存。最直接的解决方案是完全清除持久性本地缓存文件夹。不推荐这样做，因为它的影响会持续到实验范围之外，减慢所有未来模拟的启动速度，直到缓存最终恢复。你应该将 Genesis（和 Taichi）重定向到某个替代的临时缓存文件夹。这可以通过编辑任何 Python 代码、设置几个环境变量来完成：
```bash
XDG_CACHE_HOME="$(mktemp -d)" GS_CACHE_FILE_PATH="$XDG_CACHE_HOME/genesis" TI_OFFLINE_CACHE_FILE_PATH="$XDG_CACHE_HOME/taichi" python [...]
```
注意，在 Linux 上指定 `XDG_CACHE_HOME` 就足够了，但在 Windows 和 Mac OS 上则不够。

# 🖥️ 命令行工具

我们提供了一些命令行工具，你可以在安装 Genesis 后在终端中执行。这些包括：

- `gs view *.*`：可视化给定资源（网格/URDF/MJCF）（如果你想快速检查资源是否能正确加载和可视化，这可能很有用）
- `gs animate 'path/*.png'`：将所有匹配给定模式的图像组合成视频。
