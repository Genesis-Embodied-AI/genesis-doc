# Constraint model

Once {doc}`collision_detection` has produced contacts, the rigid solver decides what forces those contacts, joint limits, and equality constraints exert on the bodies. It is the third of the rigid solver's {doc}`three layers <index>`. The solver gathers every constraint into one system and solves it once per step for the generalized accelerations that satisfy them together, under a *soft* formulation that tolerates small violations.

For where contacts come from, see {doc}`collision_detection`; for the API that declares and toggles constraints, see {doc}`/user_guide/robot_control/constraints`.

## Constraint system

Write $a = \ddot q$ for the generalized accelerations of all degrees of freedom (dofs), $M(q)$ for the joint-space mass matrix, and $a^{\text{unc}} = M^{-1}\tau$ for the *unconstrained* acceleration the bodies would take under the applied and passive forces $\tau$ with no constraints active. Each constraint contributes one row to a Jacobian $J$ that maps accelerations into the constraint's local coordinate, and a target $a_{\text{ref}}$ for that coordinate.

The solver finds the acceleration that stays closest to $a^{\text{unc}}$ in the mass metric while driving $Ja$ toward $a_{\text{ref}}$:

$$
\min_{a}\;
\tfrac12\,(a - a^{\text{unc}})^\top M\,(a - a^{\text{unc}})
\;+\;
\tfrac12\,(Ja - a_{\text{ref}})^\top D\,(Ja - a_{\text{ref}}).
$$

The diagonal matrix $D$ sets each constraint's stiffness: a large $D_{ii}$ pulls $Ja$ nearly onto $a_{\text{ref}}$, a small one lets it drift. The penalty is finite, so constraints are never enforced exactly. That is what *soft* means here.

The objective is quadratic, so its gradient and Hessian are constant in $a$:

$$
g = M\,(a - a^{\text{unc}}) + J^\top D\,(Ja - a_{\text{ref}}),
\qquad
H = M + J^\top D\,J.
$$

Equality constraints act in both directions and are always present. Contacts and joint limits are *inequalities*: a contact may only push, and a joint limit resists only once the joint reaches it. Such a row is active only while it is violated, and friction rows are capped by the friction cone. The line search below decides which inequality rows are active as the solve proceeds.

## Constraint types

Every constraint reduces to the same three ingredients: a Jacobian row $J$, a reference acceleration $a_{\text{ref}}$, and a diagonal stiffness $D_{ii}$. They differ in how those are built.

### Contacts and friction

Each contact point expands into a block of three to ten constraint rows, depending on the cone selected by `friction_cone` and on which extra friction axes are enabled. `max_contacts` bounds the number of points. The reference acceleration is driven by penetration depth under either cone, so a deeper contact pushes back harder.

**Pyramidal cone (default).** With `friction_cone=gs.friction_cone.pyramidal` a point becomes **four** rows approximating the Coulomb friction cone by a pyramid. Each pyramid edge mixes the normal and tangential directions rather than separating them. With contact normal $\mathbf n$, tangent directions $\mathbf d_1, \mathbf d_2$, and friction coefficient $\mu$, the four edge directions are

$$
\pm\,\mu\,\mathbf d_1 - \mathbf n
\qquad\text{and}\qquad
\pm\,\mu\,\mathbf d_2 - \mathbf n .
$$

A non-negative multiplier on any edge produces a force whose tangential part is bounded by $\mu$ times its normal part, keeping the total inside the pyramid $|\mathbf f_t| \le \mu f_n$. The pyramid makes the friction limit direction-dependent.

**Elliptic cone.** With `friction_cone=gs.friction_cone.elliptic` the normal and tangential rows stay separate and friction is bounded by its Euclidean limit $\sqrt{f_{t_1}^2 + f_{t_2}^2} \le \mu f_n$ in every direction, so the limit is isotropic. `impratio`, the tangential-to-normal impedance ratio, defaults to 100 under this cone. The elliptic cone is unsupported with differentiable simulation.

**Contact resolution.** `contact_resolution` sets how a contact's normal force and friction force are resolved against each other.

- **`gs.contact_resolution.convex`:** MuJoCo's formulation. The contact is a single convex cost in which the friction limit $|\mathbf f_t| \le \mu f_n$ bounds the normal and tangential parts jointly, so tangential demand can be met by raising $f_n$.
- **`gs.contact_resolution.signorini`:** friction is bounded by the normal force the contact has developed, so that force follows the contact's normal state rather than tangential demand. The solver resolves contacts by successive approximation, which costs extra iterations.

`signorini` requires the elliptic cone, whose rows separate into a normal row and a friction disc, and the Newton solver, which reaches the fixed point of the successive approximation. Left unset, `contact_resolution` resolves to `signorini` under those two and to `convex` otherwise; `enable_mujoco_compatibility` keeps `convex`. Requesting `signorini` where it is unavailable raises at build time.

**Torsional and rolling friction.** A point contact transmits no torque, so by default nothing resists a body spinning in place or a ball rolling to rest. `enable_torsional_friction` adds one row per point resisting spin about the normal; `enable_rolling_friction`, which requires torsional friction, adds two more resisting rolling about the tangent axes. Strength is set per geometry by the {py:class}`gs.materials.Rigid <genesis.engine.materials.rigid.Rigid>` coefficients `friction_torsional` and `friction_rolling`, each an effective contact-patch radius in meters; a contacting pair takes the larger of the two values. These rows add solve cost on every contact.

### Joint limits

A revolute or prismatic joint may carry a lower and an upper position limit. While the joint is inside its range, no constraint exists. When the signed distance to a limit goes negative,

$$
\phi = q - q_{\min} < 0
\qquad\text{or}\qquad
\phi = q_{\max} - q < 0,
$$

the solver spawns a single one-dof inequality with Jacobian $J = \pm 1$ and a reference acceleration that pushes the joint back inside its range. `enable_joint_limit` turns this on and off globally.

A related row models dry friction in a joint: dofs with a nonzero friction-loss coefficient get a constraint that resists motion up to a bounded force, independent of any limit.

### Equality constraints

Equality constraints are holonomic, tying bodies together for as long as they exist. Genesis World supports three kinds.

- **Connect:** pins two points on different bodies to the same world position, removing 3 translational dofs, as a ball-and-socket joint does.
- **Weld:** holds two frames at a fixed relative pose, removing all 6 dofs. This is the constraint the {doc}`suction-gripper example </user_guide/robot_control/constraints>` toggles at runtime.
- **Joint:** couples two scalar joints so one follows the other through a quartic polynomial, removing 1 dof, as a geared mechanism does.

Each writes its rows into $J$ so that the solve drives the constrained relative velocity to zero. `disable_constraint=True` turns off all constraints, contacts included.

## Reference acceleration and softness

The reference acceleration makes a constraint act as a critically damped spring rather than a rigid wall. For a constraint whose current violation is $\phi$ with rate $\dot\phi$,

$$
a_{\text{ref}} = -b\,\dot\phi - k\,\phi .
$$

The gains $b$ and $k$ come from a time constant and a damping ratio: $\phi$ decays to zero over roughly `constraint_timeconst` seconds without overshoot. A shorter time constant makes the constraint stiffer and its correction faster, at the cost of conditioning. The stiffness entry $D_{ii}$ is scaled by the constraint's inverse inertia, so light and heavy bodies respond consistently. Both are computed per constraint from its `sol_params`, which carries the `solref` and `solimp` values an MJCF model supplies.

## Solving the system

The solver computes the generalized accelerations iteratively. `constraint_solver` sets the algorithm; both variants minimize the same objective and share the same line search.

- **`gs.constraint_solver.Newton`** (the default): forms the Hessian $H = M + J^\top D J$ and takes Newton steps by solving $H\,\Delta a = -g$ with a Cholesky factorization. On the CPU it can exploit the band structure of $H$ for a sparse factorization (`sparse_solve`); on the GPU it uses a dense tiled factorization. It converges in a handful of iterations, each carrying the cost of the factorization.
- **`gs.constraint_solver.CG`**: preconditioned conjugate gradient in acceleration space, using the mass matrix as the preconditioner and a Polak–Ribière update. It needs only matrix-vector products, never the explicit Hessian, so its memory footprint stays low on scenes with many dofs or constraints.

Each iteration proposes a search direction, then a **line search** picks the step length $\alpha$ minimizing the objective along it. The objective restricted to a line is a quadratic, so the exact minimizer is available in closed form, and the search handles inequality rows switching between active and inactive as $\alpha$ varies. `ls_iterations` and `ls_tolerance` cap the line-search effort.

The solve stops when both the gradient norm and the per-iteration cost improvement fall below a scaled tolerance,

$$
\varepsilon = \texttt{tolerance} \cdot \overline{m} \cdot n_{\text{dof}},
$$

where $\overline{m}$ is the mean inertia, or after `iterations` iterations. Each step warm-starts from the previous step's solution when one is available, and from the unconstrained acceleration $a^{\text{unc}}$ otherwise.

## See also

- {doc}`collision_detection`: how contacts are detected and what each carries into the solve.
- {doc}`/user_guide/robot_control/constraints`: declaring equality constraints and toggling welds at runtime.
- [MuJoCo constraint model](https://mujoco.readthedocs.io/en/latest/computation/index.html#constraint-model): the soft-constraint formulation in more mathematical depth.
