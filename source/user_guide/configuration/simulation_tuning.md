# Tuning Simulation Parameters

Start with the smallest scene that shows the problem, check the model, and then change one parameter at a time. This page covers tuning for rigid contact and robot control, with guidance for choosing the integration interval in coupled scenes.

## Diagnose before you tune

Contact failures can originate in geometry, control, or the model as well as the solver. Before changing contact parameters, check these possible causes:

- **Initial state or geometry.** Bodies overlap at the start, the collision mesh differs from the visual mesh, or a joint starts outside its limits.
- **Control.** The gains are too high for the link, or the target jumps between steps.
- **Model.** A mass or inertia is wrong, or the joint has no damping or armature where the real robot has some.
- **Capacity.** The scene has more contacts than the solver has room for. Genesis World raises an error that names the buffer, see {doc}`Troubleshooting </user_guide/overview/troubleshooting>`.
- **Contact or solver.** Only after the four above are ruled out.

Three rules follow from this list. Correct model and control errors before increasing contact stiffness or solver iterations, because solver settings cannot correct the underlying geometry or physical parameters. Tune physical parameters before solver options. And stiffer is not always more stable: a stiffer contact penetrates less, but it can also jitter or add energy to the scene.

## Tuning order

For scenes dominated by rigid contact, such as manipulation and locomotion:

1. Reproduce the problem in the smallest scene that shows it.
2. Check the units, masses, inertias, joint axes, and joint limits of the model.
3. Show the collision geometry with `vis_mode="collision"` in `scene.add_entity` and compare it with the visual mesh.
4. Reduce the integration interval with a smaller `dt` or more `substeps`.
5. Tune the contacts: friction, friction cone, and contact stiffness.
6. Tune the joints and drives: gains, damping, armature, and force range.
7. Increase the constraint solver `iterations` while the result still improves.
8. Recover speed last, by reducing substeps or iterations until the behavior degrades.

If the problem is poor tracking or oscillation of a robot, tune the joints and drives before the contacts.

Change one parameter at a time, and keep a change only if the task metric improves and nothing else regresses. Pick what you watch before the first change: the task metric, NaN errors, penetration, and run time. Use a `.gstraj` recording to inspect the original failure, as described in {doc}`Troubleshooting </user_guide/overview/troubleshooting>`. To evaluate a parameter change, rerun the reproducing script from the same initial conditions and command sequence. Replaying recorded frames displays the original run; it does not test the changed settings.

## Example: a slipping grasp

Suppose a gripper closes on an object, but the object slides out during a lift. Measure the object's displacement relative to the gripper, whether the lift completes, and the runtime for the same command sequence.

1. Show the collision geometry and check that both fingers contact the object before the lift starts.
2. Inspect the gripper's force range and commanded motion. Correct a force limit or target that prevents the fingers from closing.
3. If the object slides along the fingers, change only the material friction and rerun the script from its initial state.
4. If the object twists between the fingers, compare torsional friction in a separate run.
5. If the grasp still creeps, compare the elliptic friction cone while keeping the other settings fixed.

Keep a change when it reduces slip without unacceptable penetration, oscillation, or runtime. If higher friction introduces jitter, return to the previous value and check the integration interval and controller gains before increasing it further. The {doc}`joints guide </user_guide/physics/joints_and_actuators>` explains how drive parameters differ from passive joint properties.

## Time step and substeps

Two `SimOptions` fields set the integration interval. Each `scene.step()` advances the simulation by `dt`, and each solver integrates `substeps` times within that step, so the interval is `dt / substeps`. A smaller interval can improve stability and accuracy, at the cost of more solver work per simulated second.

Choose `dt` to match how often your program reads or commands the scene, for example the control rate of a policy. Then increase `substeps` until the simulation is stable. This keeps the control rate fixed while the solvers take smaller intervals. Reducing the interval is a useful diagnostic for integration instability; measure the added run time before keeping the change.

The bolt and nut example drives a screw thread through contact alone, so it uses a long control step split into many substeps, and stiffens the contacts to match:

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

These examples show settings for other kinds of scenes:

| Scene | Example |
|---|---|
| Legged robot trained with RL | [`examples/locomotion/go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py) |
| Gripper grasping a soft body | [`examples/coupling/grasp_soft_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/grasp_soft_cube.py) |
| Thread engaged through contact only | [`examples/rigid/bolt_nut_self_screw.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/bolt_nut_self_screw.py) |
| Fluids, granular materials, cloth | [`examples/tutorials/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/tutorials) (`sph_liquid.py`, `mpm.py`, `pbd_cloth.py`) |

Soft-body and particle solvers can require a smaller integration interval than a rigid-only scene. Start from an example for the material and coupler you use, then check stability at the intended stiffness and resolution. All active time-based solvers share the substep interval: increase `SimOptions.substeps` to reduce it for the whole scene. An explicitly set solver `dt` must divide the scene step into an integer number of substeps and agree with any other explicitly requested rate. See {doc}`Options and configuration <config_system>` for solver timestep settings.

## Contacts

These options change how rigid contacts behave. Friction is set per geometry by the material, and the rest are `RigidOptions` fields.

- **`friction`** in `gs.materials.Rigid` sets the sliding friction coefficient of a geometry. Check it, and the force limit of the gripper, before anything else when a grasped object slips.
- **`friction_cone`** selects the friction model. The pyramidal cone is the default and is easy to solve. The elliptic cone avoids the pyramidal approximation and can reduce creep in resting stacks and grasps. Compare the drift and solve time in your scene before switching. `impratio` stiffens friction relative to the normal response, and matters mainly with the elliptic cone.
- **`enable_torsional_friction`** and **`enable_rolling_friction`** make contacts resist spin and rolling, with the strength set by `friction_torsional` and `friction_rolling` in the material. Consider torsional friction when an object slips by twisting in a grasp, and rolling friction when rolling motion is the problem. [`examples/rigid/torsional_grasp.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/torsional_grasp.py) combines both with the elliptic cone.
- **`noslip_iterations`** adds a step after the main solve that suppresses slip and drift. It is experimental and slows the simulation, so enable it only when slip is the problem.
- **`constraint_timeconst`** sets how fast a constraint corrects an error, in seconds. A smaller value makes contacts stiffer, down to a floor of twice the integration interval. Genesis World raises a smaller value to that floor and logs a warning.
- **`use_gjk_collision`** uses GJK instead of MPR for collision detection. Compare it when collision detection produces poor contacts for your geometry; changing the detector can also change the runtime.
- **`max_collision_pairs`** and **`max_contacts`** size the contact buffers. Increase them when the solver reports that it ran out of contact points.

The collision mesh also matters. By default, Genesis World replaces each mesh of a rigid entity with convex hulls, and splits it into several hulls when one is not accurate enough. `convexify` and `decimate` on the morph control this simplification.

## Joints and drives

Use gains that the real robot could produce. A light link with a high `kp` needs a small integration interval, so a gripper finger is often the first part of a robot to become unstable. Before you reduce the interval for one link, try these:

- Add `armature` to the joint. It adds inertia to the joint without changing the mass of the link.
- Add `damping` to the joint, or increase `kv`.
- Limit the force with `set_dofs_force_range`.
- Limit how fast the target changes in your control code, instead of jumping to a new target in one step.

{doc}`Joints and actuators </user_guide/physics/joints_and_actuators>` explains each parameter and where it comes from in URDF and MJCF files.

## Constraint solver

The constraint solver iterates until the change falls below `tolerance`, or until it reaches `iterations`. Increase `iterations` when resting objects jitter, and stop when another increase no longer changes the result. More iterations cost time but do not fix a wrong model. `constraint_solver` selects Newton's method, the default, or conjugate gradient.

`integrator` selects the integration scheme of the rigid solver. `implicitfast` and `Euler` match their MuJoCo counterparts, and the default `approximate_implicitfast` is a faster approximation of `implicitfast`.

To run in double precision, call `gs.init(precision="64")`. This reduces rounding error, at the cost of speed and memory.

## Symptoms

| Symptom | Try first | Then try | Cost |
|---|---|---|---|
| `Invalid ... causing 'nan'` error | Reduce the integration interval. Check for overlapping geometry at the start. | Lower the gains, and add armature or damping. | Run time |
| Objects explode apart at contact | Check for overlapping collision geometry and unwanted self-collision. | Reduce the integration interval, and lower contact or drive stiffness. | Run time |
| Thin or fast objects pass through each other | Reduce the integration interval, so that an object moves less than its thickness in one substep. | Use a thicker collision shape. | Run time |
| Resting objects jitter or creep | Check the collision geometry and integration interval; compare the elliptic friction cone. | Increase `iterations`, or enable `noslip_iterations`. | Run time |
| Grasped object slips or pivots | Check `friction`, the contact points, and the gripper force range. | Enable torsional friction, and use the elliptic cone. | Run time |
| Robot tracks its target slowly or oscillates | Tune `kp` and `kv`, and avoid steps in the target. | Add armature, and reduce the integration interval. | Response speed |
| Simulation is too slow | Reduce `substeps` and `iterations`. | Simplify the collision meshes, and enable `use_hibernation` for scenes where bodies come to rest. | Accuracy |
