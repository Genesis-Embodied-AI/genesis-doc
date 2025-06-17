# 🧩 Non-rigid Dynamics

This page gives a compact overview of the physical models implemented by Genesis' continuum and discrete solvers.  The emphasis is on *which equations are being solved and how*, rather than on the Python API. For coupling theory see the dedicated *Solvers & Coupling* chapter.

---

## 1. Eulerian Stable-Fluid Solver (`SFSolver`)

**Purpose.** Fast smoke / gas simulation on a fixed grid.

**Governing equations** – incompressible Navier–Stokes.

**Algorithm** – Jos Stam's *Stable Fluids*:

1. **Advection** – velocities are back-traced with third-order RK and interpolated (`backtrace` + `trilerp`).  Numerically unconditionally stable.
2. **External impulses** – jet sources inject momentum after advection.
3. **Viscosity / decay** – optional exponential damping term.
4. **Pressure projection** – solve Poisson by Jacobi iteration (`pressure_jacobi`).

5. **Boundary conditions** – zero-normal velocity enforced by mirroring components at solid faces.

Because all steps are explicit or diagonally implicit the method is extremely robust at large time-steps and suitable for real-time effects.

---

## 2. Material Point Method Solver (`MPMSolver`)

**Purpose.** Unified simulation of solids, liquids and granular media using particles + background grid.

**Core idea.**  The continuum momentum equation is evaluated on an Eulerian grid while material history (deformation gradient, plastic strain, etc.) is stored on Lagrangian particles.

### 2.1 Update sequence (APIC / CPIC variant)

| Phase | Description |
|-------|-------------|
| P2G | Transfer mass and momentum to neighbour grid nodes with B-spline weights; add stress contribution. |
| Grid solve | Divide by mass to obtain velocities, apply gravity & boundary collisions. |
| G2P | Interpolate grid velocity back, update affine matrix and position. |
| Polar-SVD | Decompose deformation graident; material law returns new deformation gradient. |

### 2.2 Constitutive models

Genesis ships several analytic stress functions:

* **Neo-Hookean elastic** (chalk/snow)
* **Von Mises capped plasticity** (snow-plastic)
* **Weakly compressible liquid** (WC fluid)
* **Anisotropic muscle** adding active fibre stress

---

## 3. Finite Element Method Solver (`FEMSolver`)

**Purpose.** High-quality deformable solids with tetrahedral meshes; optional implicit integration for stiff materials.

### 3.1 Energy formulation

Total potential energy

$$ \Pi(\mathbf x) = \sum_{e} V_{e}\,\psi(\mathbf F_e) - \sum_{i} m_{i}\,\mathbf g\!\cdot\!\mathbf x_i. $$

The first variation yields the internal force; the second variation gives the element stiffness.

### 3.2 Implicit backward Euler

Given current state $(\mathbf x^n, \mathbf v^n)$ solve for $\mathbf x^{n+1}$ by Newton–Raphson:

$$ \mathbf r(\mathbf x) = \frac{m}{\Delta t^{2}}(\mathbf x - \hat{\mathbf x}) + \frac{\partial \Pi}{\partial \mathbf x} = 0,$$
where $\hat{\mathbf x} = \mathbf x^{n} + \Delta t\,\mathbf v^{n}$ is the inertial prediction.

Each Newton step solves $\mathbf H\,\delta \mathbf x = -\mathbf r$ with PCG; $\mathbf H$ is the consistent stiffness + mass matrix.  A block-Jacobi inverse of per-vertex 3×3 blocks is used as preconditioner.  Line-search (Armijo back-tracking) guarantees energy decrease.

---

## 4. Position-Based Dynamics Solver (`PBDSolver`)

**Purpose.** Real-time cloth, elastic rods, XPBD fluids and particle crowds.

### 4.1 XPBD integration cycle

1. **Predict** – explicit Euler: $\mathbf v^{*}\!=\!\mathbf v + \Delta t\,\mathbf f/m$ and $\mathbf x^{*}\!=\!\mathbf x + \Delta t\,\mathbf v^{*}$.
2. **Project constraints** – iterate over edges, tetrahedra, SPH density etc.
   For each constraint $C(\mathbf x)\!=\!0$ solve for Lagrange multiplier λ
   
   $$ \Delta\mathbf x = -\frac{C + \alpha\,\lambda^{old}}{\sum w_i\,|\nabla\!C_i|^{2}+\alpha}\,\nabla\!C, \quad \alpha = \frac{\text{compliance}}{\Delta t^{2}}. $$

3. **Update velocities** – $\mathbf v = (\mathbf x^{new}-\mathbf x^{old})/\Delta t$.

### 4.2 Supported constraints

* Stretch / bending (cloth)
* Volume preservation (XPBD tetrahedra)
* Incompressible SPH density & viscosity constraints (fluid-PBD)
* Collision & friction via positional correction + Coulomb model.

---

## 5. Smoothed Particle Hydrodynamics Solver (`SPHSolver`)

**Purpose.** Particle-based fluids with either WCSPH or DFSPH pressure solvers.

### 5.1 Kernels

Cubic spline kernel $W(r,h)$ and gradient $\nabla W$ with support radius $h=$ `_support_radius`.

### 5.2 Weakly Compressible SPH (WCSPH)

* Equation of state: $p_i = k\bigl[(\rho_i/\rho_0)^{\gamma}-1\bigr]$.
* Momentum equation:
  
  $$ \frac{d\mathbf v_i}{dt} = -\sum_j m_j \left( \frac{p_i}{\rho_i^2} + \frac{p_j}{\rho_j^2} \right) \nabla W_{ij} + \mathbf g + \mathbf f_{visc} + \mathbf f_{surf}. $$

### 5.3 Divergence-free SPH (DFSPH)

* Splits solve into **divergence pass** (enforce $\nabla\!\cdot\mathbf v = 0$) and **density pass** (enforce $\rho\!=\!\rho_0$).
* Both passes iteratively compute per-particle pressure coefficient κ with Jacobi iterations using the *DFSPh factor* field.
* Ensures incompressibility with bigger time-steps than WCSPH.

---

### References

* Stam, J. "Stable Fluids", SIGGRAPH 1999.
* Zhu, Y.⁠ & Bridson, R. "Animating Sand as a Fluid", SIGGRAPH 2005.
* Gao, T. et al. "Robust Simulation of Deformable Solids with Implicit FEM", SIGGRAPH 2015.
* Macklin, M. et al. "Position Based Fluids", SIGGRAPH 2013.
* Bender, J. et al. "Position Based Dynamics", 2014.
* Bavo et al. "Divergence-Free SPH", Eurographics 2015.
