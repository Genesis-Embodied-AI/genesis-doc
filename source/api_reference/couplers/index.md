# Couplers

Coupler 是 Genesis 引擎中用于连接不同物理系统或求解器的组件，负责处理不同系统之间的相互作用和数据交换。耦合器实现了多物理场模拟和混合求解器系统。

## 耦合器类型

Genesis 引擎支持多种耦合器，用于不同类型的物理系统之间的交互：

- **SAP 耦合器**：用于刚体与其他系统的耦合
- **MPM-PBD 耦合器**：用于 MPM 与 PBD 系统的耦合
- **MPM-SPH 耦合器**：用于 MPM 与 SPH 系统的耦合
- **FEM-Rigid 耦合器**：用于 FEM 与刚体系统的耦合
- **通用耦合器**：用于自定义系统间的耦合

## 耦合器架构

所有耦合器都继承自统一的 `Coupler` 基类，提供一致的接口和生命周期管理。耦合器与求解器之间通过明确的接口进行通信，实现了不同物理系统之间的解耦和集成。

```{toctree}
:maxdepth: 2

base_coupler
sap_coupler
mpm_pbd_coupler
mpm_sph_coupler
fem_rigid_coupler
```
