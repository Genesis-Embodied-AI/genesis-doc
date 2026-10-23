# Stability and Accuracy

A simulation is stable when its state stays finite and bounded, and accurate when it follows the physics closely enough for your task. In Genesis World, both depend mostly on two numbers in `SimOptions`: the step size `dt` and the number of `substeps` per step.

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=1e-2,     # seconds of simulated time per scene.step(), the default
        substeps=1,  # solver integrations per scene.step(), the default
    ),
)
```

Each `scene.step()` advances the simulation by `dt`, and each solver integrates `substeps` times with an interval of `dt / substeps`. A smaller interval is more stable and more accurate. The cost grows with the number of substeps, at most linearly.

## Choose dt and substeps

Choose `dt` to match how often your program reads or commands the scene, for example the control rate of a policy. Then increase `substeps` until the simulation is stable. This keeps the control rate fixed while the solvers take smaller intervals.

| Scene | Typical setting |
|---|---|
| Rigid robots and objects | `dt=1e-2`, `substeps=1`. Reduce the interval for light links with high gains, such as grippers. |
| Soft bodies, fluids, granular materials | `dt=4e-3`, `substeps=10` or more. These solvers are numerically stiff. |
| Coupled rigid and soft entities | Use the settings of the soft solver. |

Light links with high gains are a frequent cause of rigid instability, because a finger with a mass of a few grams and a high `kp` needs a small interval. Instead of a smaller `dt`, you can also add armature to the joint, which adds inertia without changing the mass of the link. See {doc}`Joints and actuators </user_guide/physics/joints_and_actuators>`.

## Signs of instability

- **The solver raises `Invalid constraint forces causing 'nan'` or `Invalid accelerations causing 'nan'`.** The state became infinite or NaN. Reduce the integration interval.
- **Objects explode apart or fly away at contact.** Contact forces are too large for the interval. Reduce the interval, or check that the collision geometry does not overlap at the start.
- **Thin or fast objects pass through each other.** An object moves more than its thickness in one substep. Reduce the interval.
- **Resting objects jitter.** The constraint solver did not converge. Increase `iterations` in `RigidOptions`, or use the elliptic friction cone described in {doc}`Rigid bodies </user_guide/physics/rigid_bodies>`.

{doc}`Troubleshooting </user_guide/overview/troubleshooting>` explains how to record a run that becomes unstable, so you can replay the steps before the failure.

## Rigid solver options

These `RigidOptions` fields trade speed for stability and accuracy. The defaults suit most scenes.

| Option | Default | Effect |
|---|---|---|
| `integrator` | `approximate_implicitfast` | `implicitfast` and `Euler` match their MuJoCo counterparts. `approximate_implicitfast` is a faster approximation of `implicitfast`. |
| `iterations` | 25 | Maximum iterations of the constraint solver per step. The solver stops early when it reaches `tolerance`. |
| `tolerance` | 1e-5 for 32-bit, 1e-8 for 64-bit | Convergence tolerance of the constraint solver. |
| `constraint_timeconst` | 0.01 | Time constant of the constraint response, in seconds. A smaller value makes contacts stiffer, down to twice the integration interval. Genesis World raises a smaller value to that floor and logs a warning. |
| `use_gjk_collision` | `False` | Use GJK instead of MPR for collision detection. It is more stable, but much slower. |

To run in double precision, call `gs.init(precision="64")`. This reduces rounding error, at the cost of speed and memory.
