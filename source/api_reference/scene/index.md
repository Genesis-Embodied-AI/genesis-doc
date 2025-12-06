# Scene
A ``genesis.Scene`` object wraps all components in a simulation environment, including a simulator (containing multiple physics solvers), entities, and a visualizer (controlling both the viewer and all the cameras).
Basically, everything happens inside a scene.

## 主要特点

- 提供统一的场景管理接口，整合所有模拟组件
- 支持多种物理求解器和模拟方法
- 提供可视化和渲染功能
- 支持场景元素（实体、力场、网格等）的创建和管理
- 提供模拟控制和执行功能

```{toctree}
scene
simulator
force_field
mesh
```
