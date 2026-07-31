# Forward dynamics

The first layer of a step: place the bodies, build the mass matrix, and solve $M(q)\,\ddot q = \tau$ for the acceleration they would have with nothing in the way. The next two layers, {doc}`detection <rigid_collision/index>` and the {doc}`constraint solve <rigid_constraint_model>`, correct that acceleration.

## Kinematics

The state is `qpos` and `qvel`, not per-link poses. Forward kinematics walks each kinematic tree root-outward, composing the parent pose with the joint transform to place every link, geom, and attached frame in world space; a second pass propagates velocities. Detection reads the geom poses, the constraint solver reads the Jacobians built from them, and sensors and rendering read the link frames. Both passes rerun at the end of every substep, so a getter called between steps observes the state that step produced.

## Mass matrix

$M$ is assembled from composite-rigid-body inertias, folded leaf-to-root so each link carries the spatial inertia of its whole subtree, then factorized once per substep. Every later stage that maps forces to accelerations reuses that factorization, each constraint-solver iteration included, which is what keeps the solve cheap relative to its iteration count.

## Forces before contact

$\tau$ collects everything independent of contact:

- **Actuation**, per the dof's control mode: a force directly, or the force a position or velocity target implies.
- **Passive joint forces**: damping against velocity, stiffness toward the neutral position.
- **Bias forces**: gravity, scaled per entity by `gravity_compensation`, plus the Coriolis and centrifugal terms.
- **External forces** applied through the API since the last step, cleared once the step ends.

Solving that against the factorized $M$ gives the unconstrained acceleration.

## Integration

Velocity first, then position from the new velocity, so the ordering is semi-implicit rather than explicit:

$$
\dot q_{k+1} = \dot q_k + \ddot q_k\,\Delta t
\qquad\text{then}\qquad
q_{k+1} = q_k + \dot q_{k+1}\,\Delta t .
$$

Velocity-dependent forces are why there is more than one scheme: evaluated against the old velocity, a stiff damping force overshoots and the oscillation grows every step, while folding it into the effective mass removes that limit. All three schemes do this for joint damping and differ in what else they cover.

| `integrator` | Beyond implicit damping | Cost |
|---|---|---|
| `Euler` | Nothing; free bodies take the plain update above. | Cheapest. |
| `implicitfast` | Velocity-actuator bias joins the effective mass, and standalone free bodies advance by the implicit midpoint rule. | A second factorization per substep. |
| `approximate_implicitfast` (default) | The same, carried into the constraint and external-force accelerations. | One factorization per substep; the approximation is inexact and holds up in practice. |

Move off `Euler` for a velocity-controlled joint whose gain is stiff enough to overshoot, or a free body whose rotation the plain update integrates poorly. Keep it when the force-to-acceleration relation must hold exactly: on an undamped dof the velocity update is precisely `qvel += dt * qacc`.

## Timestep and substeps

`dt` is what one `scene.step()` advances, and it clocks the control loop. `substeps` divides it into `dt / substeps` passes through all three layers, exposing state only at `dt` boundaries. Cost is linear in either. Lower `dt` when the controller needs the rate; raise `substeps` when only the physics does, which is why it defaults to 1 and earns its cost mainly for soft materials and stiff contact.

Too large a step shows up as interpenetration the constraint solver cannot clear, joints gaining energy instead of settling, or state leaving the numerical range. Genesis halts on the last of these.

## See also

- {doc}`rigid_collision/index`: finding contacts once this layer has moved the bodies.
- {doc}`rigid_constraint_model`: the solve that corrects this acceleration.
- {doc}`/api_reference/engine/solvers/rigid_solver`: `RigidOptions` and the `integrator` values.
- {doc}`/api_reference/engine/simulator`: `SimOptions`, where `dt` and `substeps` live.
