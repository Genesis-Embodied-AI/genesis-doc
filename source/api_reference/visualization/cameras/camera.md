# Camera

`Camera` 类是 Genesis 中视觉感知的主要接口。它为使用不同后端渲染图像提供了统一的 API。

## 概述

相机可以捕获：

- **RGB 图像**：场景的彩色渲染
- **深度图**：从相机到表面的距离
- **分割**：逐像素的实体/连杆识别
- **法线**：表面法向量

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.camera.Camera
   :members:
   :undoc-members:
   :show-inheritance:
```

## 示例

### 基本渲染

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

scene.step()
rgb = cam.render(rgb=True)
print(rgb.shape)  # (480, 640, 3)
```

### 保存图像

```python
import cv2

rgb = cam.render(rgb=True)
cv2.imwrite("output.png", rgb[..., ::-1])  # RGB 转 BGR 以用于 OpenCV
```

### 深度可视化

```python
import numpy as np

depth = cam.render(depth=True)

# 归一化以进行可视化
depth_vis = (depth - depth.min()) / (depth.max() - depth.min())
depth_vis = (depth_vis * 255).astype(np.uint8)
```

### 使用 GUI 显示

```python
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    GUI=True,  # 在单独窗口中显示
)
```

## 另请参阅

- {doc}`index` - 相机概述和参数
- {doc}`/api_reference/visualization/renderers/index` - 渲染器后端
