# Tuning Simulation Parameters

Use this page to choose which Genesis World settings to investigate when rigid contact or robot control behaves unexpectedly. Start with the symptom, check the model and commands, and change one parameter at a time. For error messages and capturing a failing run, see {doc}`Troubleshooting </user_guide/overview/troubleshooting>`.

## Find your symptom

| Symptom | Where to start |
|---|---|
| NaNs or objects exploding apart | Check the initial state and collision geometry [before changing settings](#before-changing-solver-settings), then reduce the [integration interval](#time-step-and-substeps). |
| Thin or fast objects passing through each other | Check collision thickness and motion per substep in [Time step and substeps](#time-step-and-substeps). |
| Resting objects jittering or creeping | Check the [contact geometry and friction model](#contact-behavior), then [solver convergence](#solver-convergence-and-precision). |
| A grasped object slipping or twisting | Check [friction and contact geometry](#contact-behavior) and the gripper's [force range](#joint-and-controller-behavior). |
| A robot tracking slowly or oscillating | Check [joint properties, gains, and commands](#joint-and-controller-behavior). |
| Contact-buffer capacity errors | Follow the buffer-specific instructions in {doc}`Troubleshooting </user_guide/overview/troubleshooting>`. |
| Excessive time per step | Measure the cause with {doc}`Profiling </user_guide/performance/profiling>` before reducing substeps or iterations. |

## Before changing solver settings

1. Reduce the scene to the smallest script that still shows the problem.
2. Check units, masses, inertias, joint axes, and limits against the intended model.
3. Show collision geometry with `vis_mode="collision"` in `scene.add_entity(...)`; check initial overlaps and unwanted self-collision.
4. Check controller targets and force limits, including abrupt target changes and joints commanded beyond their limits.

Choose a measure of success before changing a parameter: penetration, drift, tracking error, task completion, or runtime. Rerun the script from the same initial conditions and command sequence after each change. A `.gstraj` recording helps inspect the original failure, but replaying its frames does not evaluate new settings; seeking a frame restores the recorded model parameters too.

Set scene and material options before `scene.build()`, and rebuild the scene to compare changes to them. For joint parameters that can change after the build, use the entity's `set_dofs_*` methods described in {doc}`Joints and actuators </user_guide/physics/joints_and_actuators>`.

## Time step and substeps

`SimOptions.dt` sets how much simulated time one `scene.step()` advances. `SimOptions.substeps` divides that step into smaller integration intervals. Increasing substeps keeps the rate of commands issued once per scene step fixed while giving the solvers a smaller interval; reducing `dt` also changes that command rate unless your loop compensates.

A smaller interval can improve stability and accuracy, at the cost of more solver work per simulated second. For a thin or fast-moving object, compare its motion in one substep with the thickness of the collision geometry. Reduce the interval or use a thicker collision shape if the object can cross it between collision checks.

The bolt-and-nut example uses contact to engage a screw thread, with a 0.02-second scene step divided into 20 substeps:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.02,
        substeps=20,
    ),
    rigid_options=gs.options.RigidOptions(
        constraint_timeconst=4e-3,
    ),
)
```

See [`examples/rigid/bolt_nut_self_screw.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/bolt_nut_self_screw.py) for the complete scene. Its contact stiffness and integration interval are chosen together; treat them as settings for that example, not a general preset.

Soft-body and particle solvers can require a smaller interval than a rigid-only scene. All active time-based solvers share the substep interval in Genesis World. An explicitly set solver `dt` determines that shared rate: it must divide the scene step into an integer number of substeps and agree with other explicitly requested rates, including `SimOptions.substeps`. See {doc}`Options and configuration <config_system>` for the rules.

For coupled scenes, start from an example using the intended material and coupler, such as [`examples/coupling/grasp_soft_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/grasp_soft_cube.py), then check stability at your stiffness and resolution.

## Contact behavior

First check the collision meshes: the visual surface is not necessarily the surface that makes contact. `convexify` and `decimate` on the morph control mesh simplification. A missing contact caused by an inaccurate collision shape needs a geometry change before friction or solver settings can help.

Material properties and solver options affect different parts of contact:

- Set sliding friction through `friction` on `gs.materials.Rigid`. For a slipping grasp, check the contact points and gripper force range as well as the coefficient.
- Compare `RigidOptions.friction_cone` when a resting stack or grasp creeps. The elliptic cone avoids the pyramidal approximation and can reduce drift; measure both the drift and solve time in your scene. `impratio` controls friction impedance relative to the normal response.
- Enable `enable_torsional_friction` in `RigidOptions` for resistance to twisting. For rolling resistance, enable both `enable_torsional_friction` and `enable_rolling_friction`; rolling friction requires torsional friction. Their strengths come from `friction_torsional` and `friction_rolling` on the material. [`examples/rigid/torsional_grasp.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/torsional_grasp.py) combines these with the elliptic cone.

`RigidOptions.constraint_timeconst` controls how quickly constraints correct errors. A smaller value makes the response stiffer, but can introduce jitter; it is clamped to at least twice the integration interval. Check penetration and oscillation together when changing it.

`use_gjk_collision` changes collision detection from MPR to GJK. Compare it when the detector produces poor contacts for your geometry, and measure the runtime change. It does not adjust how the constraint solver responds to the contacts it receives.

For persistent slip after the main solve, `noslip_iterations` enables an additional correction. It is experimental and adds work per step, so compare it only after checking the contact model and commands. See {doc}`Rigid bodies </user_guide/physics/rigid_bodies>` and {py:class}`RigidOptions <genesis.options.solvers.RigidOptions>` for the contact settings.

## Joint and controller behavior

For poor tracking or oscillation, inspect the commands and joint properties before changing contact parameters. Keep targets within joint limits and limit abrupt changes in the commanded position or velocity.

Passive damping and controller velocity gain `kv` can both reduce oscillation, but they represent different effects. Damping models resistance to motion in the joint; `kv` sets the controller's response to velocity error. Tune the physical joint model and controller response separately.

Armature models inertia in joint coordinates, such as motor inertia reflected through a gearbox. Use it for that missing inertia, rather than changing a link's mass to obtain a similar response. Check `kp` and the integration interval together when a light link oscillates under position control, and use `set_dofs_force_range` to represent the actuator's force limits.

{doc}`Joints and actuators </user_guide/physics/joints_and_actuators>` maps these choices to the model-file fields and runtime setters. [`examples/locomotion/go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py) shows the gains and commands in a policy-driven environment.

## Solver convergence and precision

Increase `RigidOptions.iterations` when the constraint solve has not converged, and stop when another increase no longer improves the result. `tolerance` controls convergence checks; more iterations add work per step and cannot correct a wrong model. See {doc}`Constraint solver </user_guide/theory/rigid_solver/constraints>` for how the solve works.

`constraint_solver` selects Newton's method or conjugate gradient. `integrator` separately selects the rigid solver's integration scheme. Check the integration interval first when diagnosing instability, then compare these choices while keeping the scene and commands fixed. See {py:class}`RigidOptions <genesis.options.solvers.RigidOptions>` for the supported values and defaults.

Use `gs.init(precision="64")` to compare double precision when rounding error is a concern. This is an initialization setting, so run the comparison in a fresh process. Measure runtime and memory as well as the behavior you are trying to improve.
