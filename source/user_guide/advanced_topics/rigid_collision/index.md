# 🎱 Rigid Collision

Rigid-body collision in Genesis is handled in two distinct phases - first finding which bodies are in contact, then computing the impulses that resolve those contacts. The two pages below describe each phase's algorithmic content.

- [**Rigid Collision Detection**](collision_contacts_forces) - broad-phase pruning and narrow-phase contact manifold generation (Sweep & Prune, GJK, MPR, special cases).
- [**Rigid Collision Resolution**](rigid_constraint_model) - constraint formulation, contact and friction model, joint limits, equality constraints, and the numerical solvers (PCG, Newton-Cholesky).

```{toctree}
:hidden:
:maxdepth: 1

collision_contacts_forces
rigid_constraint_model
```
