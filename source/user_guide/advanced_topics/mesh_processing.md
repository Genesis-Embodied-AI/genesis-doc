# 🔺 网格处理

Genesis 提供网格工具用于加载、简化、凸分解和碰撞处理。

## 加载网格

```python
import genesis as gs

# 从文件加载
entity = scene.add_entity(gs.morphs.Mesh(file="model.obj"))

# 带处理选项
entity = scene.add_entity(
    gs.morphs.Mesh(
        file="model.obj",
        scale=0.1,
        convexify=True,
        decimate=True,
        decimate_face_num=500,
    )
)
```

## 简化 (Decimation)

降低网格复杂度以获得更好的碰撞性能：

```python
gs.morphs.Mesh(
    file="high_poly.obj",
    decimate=True,
    decimate_face_num=500,         # 目标面数
    decimate_aggressiveness=2,     # 0-8 等级
)
```

**激进程度等级：**
- 0: 无损
- 2: 保留特征（默认）
- 5: 显著减少
- 8: 最大减少

## 凸分解 (Convex Decomposition)

对于碰撞检测，网格被分解为凸部分：

```python
gs.morphs.Mesh(
    file="concave.obj",
    convexify=True,  # 需要时自动分解
)
```

Genesis 使用 COACD 库，具有可配置选项：

```python
gs.options.COACDOptions(
    threshold=0.05,
    max_convex_hull=16,
    resolution=2000,
    preprocess_mode="auto",
)
```

## 碰撞处理

Genesis 自动处理碰撞网格：

1. **修复**：移除重复面
2. **凸化检查**：测试简单凸包是否足够
3. **分解**：将凹网格分割为凸部分
4. **简化**：减少高面网格（>5000 面警告）

## 四面体化 (Tetrahedralization)

用于 FEM/可变形仿真：

```python
entity = scene.add_entity(
    morph=gs.morphs.Mesh(file="model.obj"),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4),
)
# 网格自动四面体化用于 FEM
```

## 网格属性

```python
mesh = entity.morph.mesh

verts = mesh.verts      # (N, 3) 顶点
faces = mesh.faces      # (M, 3) 面索引
normals = mesh.normals  # (N, 3) 逐顶点法线
uvs = mesh.uvs          # (N, 2) 纹理坐标

is_convex = mesh.is_convex
volume = mesh.volume
area = mesh.area
```

## 粒子采样

从网格体积采样粒子：

```python
mesh.particlize(p_size=0.01, sampler="random")
```

**采样器：**
- `"random"`：随机采样
- `"pbs_poisson"`：泊松盘采样
- `"pbs_grid"`：基于网格的采样

## 基本网格

Genesis 提供内置基本体：

```python
gs.morphs.Sphere(radius=0.5)
gs.morphs.Box(size=(1.0, 1.0, 1.0))
gs.morphs.Cylinder(radius=0.3, height=1.0)
gs.morphs.Plane()
```

## 缓存

Genesis 缓存处理后的网格以加快加载：

| 缓存类型 | 扩展名 | 目的 |
|------------|-----------|---------|
| Convex | `.cvx` | 凸分解 |
| Tetrahedral | `.tet` | FEM 四面体化 |
| SDF | `.gsd` | 符号距离场 |
| Remesh | `.rm` | 重新网格化版本 |
| Particles | `.ptc` | 粒子采样 |

缓存使用输入参数的 SHA256 哈希进行失效处理。

## 依赖项

- **trimesh**：核心网格操作
- **fast_simplification**：简化
- **coacd**：凸分解
- **pyvista + tetgen**：四面体化
