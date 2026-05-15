# 🤝 Couplers

Couplers are the bridge between Genesis solvers, handling forces and interactions between entities simulated by different physical models. Genesis ships two contact-handling backends with complementary trade-offs:

- [**IPC Coupler**](ipc_coupler) - smooth barrier-based contact for cloth and highly deformable bodies (elastic and plastic). Used for rich soft-body interactions like cooking or cycling without requiring reduced-order abstractions; initial vertex positions are enough. Pairs with rigid-body dynamics as a bonus.
- [**SAP Coupler**](sap_coupler) - semi-analytic primal solver for elastic moderate-deformation volumetric soft bodies. Half-way between rigid-body and IPC, well-suited to FEM-style continuum dynamics.

```{toctree}
:hidden:
:maxdepth: 1

ipc_coupler
sap_coupler
```
