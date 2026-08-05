# Forward dynamics

The first layer of a step places the bodies, builds the mass matrix, and solves $M(q)\,\ddot q = \tau$ for the acceleration they would take with no contact acting. {doc}`Detection <collision_detection>` and the {doc}`constraint solve <constraints>` then correct that acceleration.

## Kinematics

The state is `qpos` and `qvel`, not per-link poses. Forward kinematics walks each kinematic tree root-outward, composing the parent pose with the joint transform to place every link, geom, and attached frame in world space. A second pass propagates velocities. Detection reads the geom poses, and the constraint solver reads the Jacobians built from them. Sensors and rendering read the link frames. Both passes rerun at the end of every substep, so a getter called between steps observes the state that step produced.

## Mass matrix

$M$ is assembled from composite-rigid-body inertias, folded leaf-to-root so that each link carries the spatial inertia of its subtree, then factorized once per substep. The later stages that map forces to accelerations reuse that factorization, including each constraint-solver iteration.

## Forces before contact

$\tau$ collects the forces independent of contact: actuation, according to the control mode of each degree of freedom (dof), and the passive joint forces, damping and stiffness. To those it adds gravity, the Coriolis and centrifugal terms, and any external force applied through the API since the last step. Per-entity `gravity_compensation` scales the gravity contribution. Solving that against the factorized $M$ gives the unconstrained acceleration.

## Integration

Velocity first, then position from the new velocity, which makes the ordering semi-implicit rather than explicit:

$$
\dot q_{k+1} = \dot q_k + \ddot q_k\,\Delta t
\qquad\text{then}\qquad
q_{k+1} = q_k + \dot q_{k+1}\,\Delta t .
$$

A damping force evaluated against the old velocity can overshoot, so every scheme folds joint damping into the effective mass. They differ in what else they cover, selected by `integrator` on `RigidOptions`:

| `integrator` | Beyond implicit damping | Cost |
|---|---|---|
| `Euler` | Nothing. Free bodies take the update above. | One factorization per substep. |
| `implicitfast` | Velocity-actuator bias joins the effective mass, and standalone free bodies advance by the implicit midpoint rule. | Two factorizations per substep. |
| `approximate_implicitfast` (default) | The same, carried into the constraint and external-force accelerations. | One factorization per substep; the correction is approximate. |

The default's extra approximation is wrong in theory and holds up well in practice, so we accept it for the factorization it saves; choose `implicitfast` where it does not hold up. On an undamped dof under `Euler`, the velocity update is exactly `qvel += dt * qacc`, which is what an analytical check wants.

## Timestep and substeps

`dt` is the interval one `scene.step()` advances, and it sets the rate of the control loop. `substeps` divides it into `dt / substeps` passes through all three layers, exposing state at `dt` boundaries only, so the physics can run at a finer interval than the controller. Both scale cost linearly, and `substeps` defaults to 1. A step too large for the scene drives the state out of range; a NaN in the forces or accelerations raises rather than propagating.

## See also

- {doc}`collision_detection`: finding contacts once this layer has moved the bodies.
- {doc}`constraints`: the solve that corrects this acceleration.
- {doc}`/api_reference/engine/solvers/rigid_solver`: `RigidOptions` and the `integrator` values.
- {doc}`/api_reference/engine/simulator`: `SimOptions`, where `dt` and `substeps` live.
