# Genesis 文档（中文版）

1. 使用 Python >= 3.9 创建干净的环境，安装 Sphinx 和其他依赖

```bash
pip install genesis-world  # 需要 Python >= 3.9
```

2. 构建文档并实时监视更改

```bash
# 在 genesis-doc/ 目录下
rm -rf build/; make html; sphinx-autobuild ./source ./build/html
```
