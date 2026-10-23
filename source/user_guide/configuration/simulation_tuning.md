# Tuning Simulation Parameters

Tuning removes one failure at a time. Start with the smallest scene that shows the problem, check the model, and only then change solver options. The defaults of Genesis World suit most scenes, so this page explains what each option trades and in which order to change them, and points to examples whose settings you can start from.

## Diagnose before you tune

Most problems that look like contact problems are not. Before you change a parameter, decide which kind of problem you have:

- **Initial state or geometry.** Bodies overlap at the start, the collision mesh differs from the visual mesh, or a joint starts outside its limits.
- **Control.** The gains are too high for the link, or the target jumps between steps.
- **Model.** A mass or inertia is wrong, or the joint has no damping or armature where the real robot has some.
- **Capacity.** The scene has more contacts than the solver has room for. Genesis World raises an error that names the buffer, see {doc}`Troubleshooting </user_guide/overview/troubleshooting>`.
- **Contact or solver.** Only after the four above are ruled out.

Three rules follow from this list. Do not hide a model or control problem behind stiffer contacts or more solver iterations, because a bad mass ratio or an overlapping collision shape stays unstable with any solver setting. Tune physical parameters before solver options. And stiffer is not always more stable: a stiffer contact penetrates less, but it can also jitter or add energy to the scene.

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

Change one parameter at a time, and keep a change only if the task metric improves and nothing else regresses. Pick what you watch before the first change: the task metric, NaN errors, penetration, and run time. {doc}`Troubleshooting </user_guide/overview/troubleshooting>` explains how to record a run to a `.gstraj` file, so you can replay the same failure after each change.

## Time step and substeps

Two `SimOptions` fields set the integration interval. Each `scene.step()` advances the simulation by `dt`, and each solver integrates `substeps` times within that step, so the interval is `dt / substeps`. A smaller interval is more stable and more accurate, and the cost grows with the number of substeps.

Choose `dt` to match how often your program reads or commands the scene, for example the control rate of a policy. Then increase `substeps` until the simulation is stable. This keeps the control rate fixed while the solvers take smaller intervals. Reducing the interval is the most reliable fix for instability, and also the most expensive one.

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

Soft bodies, fluids, and granular materials need a much smaller interval than rigid bodies, because their solvers are numerically stiff. When rigid and soft entities share a scene, use the settings of the soft solver.

## Contacts

These options change how rigid contacts behave. Friction is set per geometry by the material, and the rest are `RigidOptions` fields.

- **`friction`** in `gs.materials.Rigid` sets the sliding friction coefficient of a geometry. Check it, and the force limit of the gripper, before anything else when a grasped object slips.
- **`friction_cone`** selects the friction model. The pyramidal cone is the default and is easy to solve. The elliptic cone is the exact cone, and holds resting stacks and grasps without slow creep, at the cost of a slower solve. `impratio` stiffens friction relative to the normal response, and matters mainly with the elliptic cone.
- **`enable_torsional_friction`** and **`enable_rolling_friction`** make contacts resist spin and rolling, with the strength set by `friction_torsional` and `friction_rolling` in the material. Without them, a grasped object can pivot forever. [`examples/rigid/torsional_grasp.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/torsional_grasp.py) combines both with the elliptic cone.
- **`noslip_iterations`** adds a step after the main solve that suppresses slip and drift. It is experimental and slows the simulation, so enable it only when slip is the problem.
- **`constraint_timeconst`** sets how fast a constraint corrects an error, in seconds. A smaller value makes contacts stiffer, down to a floor of twice the integration interval. Genesis World raises a smaller value to that floor and logs a warning.
- **`use_gjk_collision`** uses GJK instead of MPR for collision detection. It is more stable but much slower.
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
| Resting objects jitter or creep | Use the elliptic friction cone. | Increase `iterations`, or enable `noslip_iterations`. | Run time |
| Grasped object slips or pivots | Check `friction`, the contact points, and the gripper force range. | Enable torsional friction, and use the elliptic cone. | Run time |
| Robot tracks its target slowly or oscillates | Tune `kp` and `kv`, and avoid steps in the target. | Add armature, and reduce the integration interval. | Response speed |
| Simulation is too slow | Reduce `substeps` and `iterations`. | Simplify the collision meshes, and enable `use_hibernation` for scenes where bodies come to rest. | Accuracy |
