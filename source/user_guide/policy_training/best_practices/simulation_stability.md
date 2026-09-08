# Recovering from rigid solver failures

In batched Genesis World simulations, use {py:meth}`RigidSolver.get_error_envs_mask() <genesis.engine.solvers.rigid.rigid_solver.RigidSolver.get_error_envs_mask>` to identify environments with rigid solver errors. For NaN constraint-force and acceleration errors, read the mask after each {py:meth}`Scene.step() <genesis.engine.scene.Scene.step>` and reset the selected environments before stepping again.

## Reset affected environments

This example uses `gs.cpu` so it runs on a machine without a GPU. Use `gs.gpu` for GPU training.

```python
import genesis as gs

gs.init(backend=gs.cpu)
scene = gs.Scene(show_viewer=False)
scene.add_entity(gs.morphs.Sphere(radius=0.1, pos=(0.0, 0.0, 0.5)))
scene.build(n_envs=4)

for _ in range(20):
    scene.step()
    scene.reset(envs_idx=scene.rigid_solver.get_error_envs_mask())
```

The sphere has a radius of 0.1 m, starts 0.5 m above the origin, and falls under gravity. This scene normally has an empty error mask. The loop shows where to handle failures when adding controls, contacts, or randomized initial states.

{py:meth}`Scene.reset() <genesis.engine.scene.Scene.reset>` restores the selected environments to their initial state and clears their error flags. Healthy environments retain their physics state. The mask also flags {ref}`capacity and internal solver errors <rigid-solver-capacity-errors>`.

In a training environment, combine the error mask with the task's termination conditions and reset the task buffers for the same selection. The [Go2 environment](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py) does this in `step()` and `_reset_idx()`, including the action history and episode counters. If reset samples a new pose or velocity, ensure that sample is valid before applying it.

Keep the selection as a boolean mask when passing `envs_idx`, because calling `.nonzero()` on a GPU mask adds a GPU-to-CPU synchronization. See {doc}`efficient_environment` for the boolean-mask fast path and buffer handling.

## Diagnose repeated numerical failures

Resetting an occasional invalid episode lets training continue, while repeated failures call for changes to the scene or its randomization. Numerical instability can produce NaNs in constraint forces or accelerations. Genesis World flags these failures, and its integration checks reject updates containing NaN positions or velocities so they do not replace the environment's current state.

Check the following parts of the scene:

- **Initial state:** sample poses and velocities that respect the model's constraints. Deep intersections, violated joint limits, or incompatible equality constraints demand large corrections at the start of an episode.
- **Integration interval:** reduce `dt` or increase `substeps` in {py:class}`gs.options.SimOptions <genesis.options.solvers.SimOptions>` when fast motion or stiff contacts change substantially within one integration interval. If the scene sets a separate `dt` in {py:class}`gs.options.RigidOptions <genesis.options.solvers.RigidOptions>`, reduce that override instead. More integration steps increase computation for the same simulated duration.
- **Constraint response:** increase `constraint_timeconst` to soften constraints, allowing more time for a correction. Keep the response time comfortably larger than the rigid integration interval. Check time constants authored in the model as well, because those take precedence over the default option. See the {doc}`constraint model </user_guide/theory/rigid_solver/constraints>` for the stiffness and conditioning tradeoff.
- **Mass and inertia:** use physically plausible values. Extreme mass ratios along a chain or nearly singular inertias make the dynamics harder to solve accurately. Joint armature can improve conditioning, but also changes the joint's response to applied forces.
- **Constraint consistency:** inspect redundant equality constraints and unintended self-collisions, especially between adjacent links. Closed kinematic loops can make initialization and constraint solving more sensitive, so check that their constraints can be satisfied together.

(rigid-solver-capacity-errors)=
## Handle capacity and internal errors

An error about the maximum number of contacts or contact pairs means the scene exceeded a configured capacity. Follow the option named in the exception to increase the budget, or reduce the contacts the scene generates. A reset clears the flag, but the same scene can exceed that budget again. Investigate other solver errors using the exception's instructions before continuing the run.

## Read the exception report

Genesis World checks error flags at the start of periodic steps, so a flag left set can cause a later `scene.step()` to raise.

In a batched scene, the exception lists the environments reporting the displayed error. If other environments have errors without reporting that displayed error, a separate list names them. Use these lists to identify which initial states, randomization samples, or contacts to inspect.

## See also

- {doc}`efficient_environment`: pass boolean masks and reset task buffers efficiently.
- {doc}`domain_randomization`: vary physical properties and initial states across environments.
- {doc}`/api_reference/engine/solvers/rigid_solver`: rigid solver options and public methods.
