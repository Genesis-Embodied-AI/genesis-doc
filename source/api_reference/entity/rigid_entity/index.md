# RigidEntity

`RigidEntity` 是 Genesis 引擎中用于模拟刚体系统的核心实体类。刚体是指在模拟过程中不会发生变形的物体，是物理模拟中的基础构建块之一。

## RigidEntity 概述

`RigidEntity` 类提供了创建和管理刚体系统的功能，支持多个刚体链接（RigidLink）的组合，通过关节（RigidJoint）连接，实现复杂的机械结构和运动模拟。

## 刚体系统组成

Genesis 引擎的刚体系统由以下核心组件构成：

- **RigidEntity**: 刚体实体的主容器，管理整个刚体系统
- **RigidLink**: 单个刚体链接，是刚体系统的基本单元，具有质量、惯性等物理属性
- **RigidGeom**: 刚体的碰撞几何形状，用于碰撞检测
- **RigidVisGeom**: 刚体的可视化几何形状，用于渲染
- **RigidJoint**: 刚体链接之间的关节约束，控制链接之间的运动方式

```{toctree}
rigid_entity
rigid_link
rigid_joint
rigid_geom
rigid_visgeom
```