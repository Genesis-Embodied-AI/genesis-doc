# 🔗 Rigid Collision Resolution

Genesis follows a **quadratic penalty formulation** very similar to that used by [MuJoCo](https://mujoco.readthedocs.io/) for enforcing rigid–body constraints.  This document summarises the mathematics and physical interpretation of the model.

---

## 1. General formulation

Let

* $q$ – joint configuration (generalised positions)
* **\dot q** – generalised velocities
* $a = \ddot q$ – the unknown **generalised accelerations** to be solved for each sub-step
* $M(q)$ – joint-space mass matrix (positive definite)
* $\tau_{ext}$ – all external joint forces **already known** (actuation, gravity, hydrodynamics …)
* $J $ – a *stack* of kinematic constraints linearised in acceleration space
* $D$ – diagonal matrix of *softness* / *impedance* parameters per constraint
* $a_{ref}$ – reference accelerations that try to restore penetrations or satisfy motors

We seek the acceleration that minimises the **quadratic cost**

$$
    \frac12 (M a \,{-}\, \tau_{ext})^{\!T} (a \,{-}\, a^{\text{prev}}) 
    \;{+}\;
    \frac12 (J a \,{-}\, a_{ref})^{\!T} D (J a \,{-}\, a_{ref})
$$


---

## 2. Contact & friction model

For every **contact pair** Genesis creates four constraints, which are the basis of the friction pyramid. Mathematically each direction **tᵢ** is

$$
    \mathbf t\_i = \pm d_1\,\mu - \mathbf n \quad\text{or}\quad \pm d_2\,\mu - \mathbf n ,
$$

so that a positive multiplier on **tᵢ** produces a force that lies *inside* the cone $|\mathbf f_t| \le \mu f_n$.  A diagonal entry **Dᵢ** proportional to the combined inverse mass gives the familiar *soft-constraint* behaviour where larger *imp* (implicitness) values lead to stiffer contacts.

---

## 3. Joint limits (inequality constraints)

Revolute and prismatic joints optionally carry a **lower** and **upper** position limit.  Whenever the signed distance to a limit becomes negative

$$ \phi = q - q_{min} < 0 \quad\text{or}\quad \phi = q_{max} - q < 0 $$

a *single* 1-DOF constraint is spawned with Jacobian

$$ J = \pm 1 $$

and reference acceleration

$$ a_{ref} = k\,\phi + c \,\dot q, $$

obtained from the scalar `sol_params` (spring-damper style softness).  The diagonal entry of **D** once again scales with the inverse joint inertia.

---

## 4. Equality constraints

Genesis supports three kinds of **holonomic equalities**:

| Type | DOF removed | Description |
|------|-------------|-------------|
| **Connect** | 3 | Enforces that two points on different bodies share the *same world position*.  Good for ball-and-socket joints. |
| **Weld**    | 6 | Keeps two frames coincident in both translation **and** rotation (optionally scaled torque). |
| **Polynomial joint** | 1 | Constrains one joint as a polynomial function of another (useful for complex mechanisms). |

Each equality writes rows into **J** so that their *relative* translational / rotational velocity vanishes.  Softness and Baumgarte stabilisation again come from per-constraint `sol_params`.

---

## 5. Solvers

The solver class implements **two interchangeable algorithms**:

### 5.1 Projected Conjugate Gradient (PCG)

* Operates in the **reduced space** of accelerations.
* Uses the *mass matrix* as pre-conditioner.
* After each CG step a **back-tracking line search** (Armijo style) projects the new **J a** onto the feasible set (normal ≥0, friction cone).
* Requires only **matrix-vector products**, making it memory-friendly and fast for scenes with many constraints.

### 5.2 Newton–Cholesky

* Builds the **exact Hessian** \(H = M + J^T D J\).
* A Cholesky factorisation (with incremental rank-1 updates) yields search directions.
* Converges in very few steps (often 2-3) but is more expensive for large DOF counts.

Both variants share **identical line-search logic** implemented in `_func_linesearch` that chooses the step length \(\alpha\) minimising the quadratic model whilst respecting inequality activation/de-activation.  The algorithm stops when either

* the gradient norm \(|\nabla f|\) drops below `tolerance · mean_inertia · n_dofs`, or
* the improvement of the cost function falls below the same threshold.

Warm-starting is supported by initialising from the previous sub-step's smoothed accelerations `acc_smooth`.

---

## 6. Practical implications

* **Stability** – because constraints are *implicit* in acceleration space the model handles larger time-steps, similar to MuJoCo.
* **Friction anisotropy** – replacing the cone by a pyramid introduces slight anisotropy.  Increasing the number of directions would reduce this but cost more.
* **Softness** – tuning `imp` and `timeconst` lets you trade constraint stiffness against numerical conditioning.  Values near 1 are stiff but may slow convergence.
* **Choosing a solver** – use *CG* for scenes with thousands of DOFs or when memory is tight; switch to *Newton* when you need very high accuracy or when the DOF count is moderate (<100).

---
