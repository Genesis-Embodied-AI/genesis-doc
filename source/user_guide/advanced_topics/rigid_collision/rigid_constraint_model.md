# Rigid constraint model

Once collision detection has produced contacts, the rigid solver still has to decide what forces those contacts, along with joint limits and any equality constraints, exert on the bodies. Genesis World does this the way MuJoCo does: it gathers every constraint into one system and solves it once per step for the generalized accelerations that satisfy them all together, using a *soft* formulation that tolerates small, controlled violations in exchange for stability at large timesteps.

This page explains that formulation and the solvers that carry it out. It is conceptual. For where contacts come from, see {doc}`collision_contacts_forces`; for the user-facing API that declares and toggles constraints, see {doc}`/user_guide/getting_started/constraints`. The implementation lives in `genesis/engine/solvers/rigid/constraint/`.

## The system being solved

Write $a = \ddot q$ for the generalized accelerations of all degrees of freedom (dofs), $M(q)$ for the joint-space mass matrix, and $a^{\text{unc}} = M^{-1}\tau$ for the *unconstrained* acceleration the bodies would take under applied and passive forces $\tau$ (actuation, gravity, Coriolis) with no constraints active. Each constraint contributes one row to a Jacobian $J$ that maps accelerations into the constraint's local coordinate, and a target $a_{\text{ref}}$ it would like that coordinate to reach.

The solver finds the acceleration that stays as close as possible to $a^{\text{unc}}$ in the mass metric while also driving $Ja$ toward $a_{\text{ref}}$:

$$
\min_{a}\;
\tfrac12\,(a - a^{\text{unc}})^\top M\,(a - a^{\text{unc}})
\;+\;
\tfrac12\,(Ja - a_{\text{ref}})^\top D\,(Ja - a_{\text{ref}}).
$$

The diagonal matrix $D$ sets each constraint's stiffness. A large $D_{ii}$ pulls $Ja$ almost exactly onto $a_{\text{ref}}$ (a hard constraint); a small one lets it drift (a soft one). Because the penalty is finite, constraints are never enforced exactly. This is what "soft" means, and it is deliberate: it keeps the system well-conditioned and stable at timesteps that would make a hard-constraint solver explode.

The objective is quadratic, so its gradient and Hessian are cheap and constant in $a$:

$$
g = M\,(a - a^{\text{unc}}) + J^\top D\,(Ja - a_{\text{ref}}),
\qquad
H = M + J^\top D\,J.
$$

Equality constraints act in both directions and are always present. Contacts and joint limits are *inequalities*: a contact may only push, never pull, and a joint limit resists only once the joint reaches it. Such a row is active only while it is violated, and friction rows are additionally capped by the friction pyramid. The solver decides which inequality rows are active as part of the solve, through the line search described below.

## Constraint types

Every constraint reduces to the same three ingredients: a Jacobian row $J$, a reference acceleration $a_{\text{ref}}$, and a diagonal stiffness $D_{ii}$. They differ only in how those are built.

### Contacts and friction

Each contact point in the buffer becomes **four** constraints, so the contact-constraint buffer is sized at four rows per point (this is what `max_contacts` bounds). Together the four rows approximate the Coulomb friction cone by a pyramid. Rather than one row for the normal and separate rows for friction, each pyramid edge mixes the two. With contact normal $\mathbf n$, tangent directions $\mathbf d_1, \mathbf d_2$, and friction coefficient $\mu$, the four edge directions are

$$
\pm\,\mu\,\mathbf d_1 - \mathbf n
\qquad\text{and}\qquad
\pm\,\mu\,\mathbf d_2 - \mathbf n .
$$

A non-negative multiplier on any edge produces a force whose tangential part is bounded by $\mu$ times its normal part, so the total contact force stays inside the pyramid $|\mathbf f_t| \le \mu f_n$. The reference acceleration is driven by the penetration depth, so a deeper contact pushes back harder. Replacing the true cone by a pyramid introduces mild direction dependence in friction; adding more edges would reduce it at a proportional cost.

### Joint limits

A revolute or prismatic joint may carry a lower and an upper position limit. While the joint is inside its range, no constraint exists. When the signed distance to a limit goes negative,

$$
\phi = q - q_{\min} < 0
\qquad\text{or}\qquad
\phi = q_{\max} - q < 0,
$$

a single one-dof inequality is spawned with Jacobian $J = \pm 1$ and a reference acceleration that pushes the joint back inside its range. Enable or disable this globally with `enable_joint_limit`.

A related row models dry friction in a joint: dofs with a nonzero friction-loss coefficient get a constraint that resists motion up to a bounded force, independent of any limit.

### Equality constraints

Equality constraints are holonomic: they tie bodies together for the whole simulation (or, for a weld, for as long as you keep it). Genesis World supports three kinds.

- **Connect:** pins two points on different bodies to the same world position, removing 3 translational dofs. This is a ball-and-socket joint.
- **Weld:** holds two frames at a fixed relative pose, removing all 6 dofs. This is the constraint the {doc}`suction-gripper example </user_guide/getting_started/constraints>` toggles at runtime.
- **Joint:** couples two scalar joints so one follows the other through a quartic polynomial, removing 1 dof. This models geared or linked mechanisms.

Each writes its rows into $J$ so that the constrained relative velocity is driven to zero. Set `disable_constraint=True` to turn off all constraints, contacts included.

## Reference acceleration and softness

The reference acceleration is what makes the constraint act like a critically damped spring rather than a rigid wall. For a constraint whose current violation is $\phi$ with rate $\dot\phi$,

$$
a_{\text{ref}} = -b\,\dot\phi - k\,\phi .
$$

The gains $b$ and $k$ come from a time constant and a damping ratio: intuitively, $\phi$ is asked to decay to zero over roughly `constraint_timeconst` seconds without overshoot. A shorter time constant makes the constraint stiffer and its correction faster, at the cost of conditioning. The stiffness entry $D_{ii}$ is scaled by the constraint's inverse inertia so that light and heavy bodies respond consistently. Both are computed per constraint from its `sol_params`, following MuJoCo's `solref`/`solimp` convention.

## Solving the system

The problem is solved iteratively for the generalized accelerations. Set the algorithm with `constraint_solver`; both variants minimize the same objective and share the same line search.

- **`gs.constraint_solver.Newton`** (the default): forms the Hessian $H = M + J^\top D J$ and takes Newton steps by solving $H\,\Delta a = -g$ with a Cholesky factorization. On the CPU it can exploit the band structure of $H$ for a sparse factorization (`sparse_solve`); on the GPU it uses a dense tiled factorization. It converges in a handful of iterations and is the better choice up to moderate dof counts.
- **`gs.constraint_solver.CG`**: preconditioned conjugate gradient in acceleration space, using the mass matrix as the preconditioner and a Polak–Ribière update. It needs only matrix-vector products, never the explicit Hessian, which keeps its memory footprint low on scenes with very many dofs or constraints.

Each iteration proposes a search direction, then a **line search** picks the step length $\alpha$ that minimizes the objective along it. Because the objective's restriction to a line is a quadratic, the exact minimizer is available in closed form, and the search also handles inequality rows switching between active and inactive as $\alpha$ varies. Line-search effort is capped by `ls_iterations` and `ls_tolerance`.

The solve stops when both the gradient norm and the per-iteration cost improvement fall below a scaled tolerance,

$$
\varepsilon = \texttt{tolerance} \cdot \overline{m} \cdot n_{\text{dof}},
$$

where $\overline{m}$ is the mean inertia, or after `iterations` iterations, whichever comes first. Each step warm-starts from the previous step's solution when one is available, falling back to the unconstrained acceleration $a^{\text{unc}}$ otherwise, so a scene near equilibrium converges almost immediately.

:::{note}
`noslip_iterations` enables an optional post-processing pass that suppresses residual tangential drift after the main solve. It is off by default and experimental; reach for it only when slip is a visible problem, for example in contact-rich manipulation, since it adds cost to every step.
:::

## Key options

These `RigidOptions` fields control the model and the solve. Pass them through `gs.options.RigidOptions` when building the scene.

| Option | Default | Effect |
|---|---|---|
| `constraint_solver` | `Newton` | Newton–Cholesky or conjugate gradient. |
| `iterations` | `50` | Maximum solver iterations. |
| `tolerance` | precision-dependent | Convergence threshold (scaled by inertia and dof count). |
| `ls_iterations` | `50` | Maximum line-search iterations per solver iteration. |
| `constraint_timeconst` | `0.01` s | Lower bound on constraint resolution time; smaller is stiffer. |
| `enable_joint_limit` | `True` | Whether joint position limits are enforced. |
| `disable_constraint` | `False` | Disable all constraints, contacts included. |
| `sparse_solve` | auto | Exploit Hessian sparsity in the Newton factorization (CPU). |
| `noslip_iterations` | `0` | Extra anti-slip passes after the main solve. |

## See also

- {doc}`collision_contacts_forces`: how contacts are detected and what each carries into the solve.
- {doc}`/user_guide/getting_started/constraints`: declaring equality constraints and toggling welds at runtime.
- [MuJoCo constraint model](https://mujoco.readthedocs.io/en/latest/computation/index.html#constraint-model): the formulation Genesis World follows, in more mathematical depth.
