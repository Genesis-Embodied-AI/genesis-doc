# Genesis 文档 (中文版)

本仓库包含 Genesis 的中文文档。Genesis 是一个用于机器人仿真的 Python 库。

## 快速开始

### 1. 克隆仓库

首先克隆文档仓库到本地：

```bash
git clone https://github.com/Genesis-Embodied-AI/genesis-doc.git
cd genesis-doc
# 切换到中文文档分支
git checkout zh_version
```

### 2. 环境配置

创建并配置 Python 环境：

```bash
# 创建新的conda环境
conda create -n genesis python=3.10
conda activate genesis

# 安装文档构建依赖
pip install -r requirements.txt
```

### 3. 构建文档

文档使用 Sphinx 构建。以下命令会构建文档并启动实时预览服务器:

```bash
# 清理构建目录并构建文档
rm -rf build/
make html

# 启动实时预览服务器
sphinx-autobuild -b html -E -a -q ./source ./build/html
```

构建完成后,可以在浏览器中访问 <http://localhost:8000> 查看文档。

### 常见问题

1. 如果遇到构建错误,可以尝试:
   - 清理构建目录: `rm -rf build/`
   - 重新安装依赖: `pip install -e ".[docs]"`

2. 实时预览不更新:
   - 检查 sphinx-autobuild 是否正在运行
   - 尝试手动刷新浏览器缓存

### 贡献指南

欢迎提交 PR 帮助改进文档:

1. Fork 本仓库
2. 创建新分支
3. 提交修改
4. 发起 Pull Request

如有任何问题,请提交 Issue 讨论。
