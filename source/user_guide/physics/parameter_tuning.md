# Tuning physics parameters

The rigid solver ships with defaults that work for most scenes, but a scene that looks wrong -
objects that jitter at rest, a grasp that slips, a fast body that tunnels through a wall - usually
needs its physics parameters tuned to the task. This page explains the one knob that frames every
tradeoff, the order in which to attack a problem, and what each parameter buys you. The example
script at `examples/tuning/autotune_stability.py` automates the search described here.

## The knob: realtime factor versus realism

Every tuning decision trades physical realism against speed. Genesis frames that trade with a
single target: the **realtime factor**, how many seconds of simulated time you get per second of
wall-clock time (`fps * dt`). It is independent of the timestep and the scene size, so it is
comparable across setups.

```python
tune(scene, realtime_factor=None)   # no speed floor: tune purely for realism
tune(scene, realtime_factor=1.0)    # keep the scene running at least real time
```

With no floor, the search picks the most physically faithful settings it can find. With a floor,
it finds the most faithful settings that still sustain the target speed. Speed is judged headless
on the slow-tail (p95) step time, so an occasional slow step - the kind that breaks a realtime
guarantee - counts against the setting.

## Two phases

Attack a misbehaving scene in this order; skipping the first phase makes the second one chase
symptoms.

1. **Asset preprocessing first.** Condition the collision geometry (convex decomposition, a
   watertight collision mesh, sensible decimation) and fix the scene layout. Most jitter and
   tunneling trace back to a bad collision mesh or an over-broad contact set, not to the solver,
   and no amount of solver tuning fixes a broken mesh. See {doc}`/user_guide/assets/loading_assets`.
2. **Physics parameter search.** Only once the geometry is sound, tune the solver knobs below.
   Seed each one from its analytical starting point (for example, keep the constraint time
   constant at or above twice the integration substep), probe briefly, then search.

## Auto-tuning stability

`examples/tuning/autotune_stability.py` runs the second phase for you on a chosen scenario. It
seeds from the defaults, walks one knob at a time, and keeps a change only when it lowers the
realism score without dropping below the speed floor.

```bash
# Tune a settling box pyramid to run at least real time
python examples/tuning/autotune_stability.py --scenario box_pyramid --realtime_factor 1.0

# Tune a held Franka arm purely for realism (no speed floor)
python examples/tuning/autotune_stability.py --scenario franka
```

It scores each candidate on five signals, all measured over the resting window of a short
rollout: the state stays finite (no NaN), total energy holds steady, contact penetration stays
shallow, residual velocity settles toward zero (the jitter signal), and resting contacts pump no
net energy. The script reports the best parameters, those metrics, the achieved realtime factor,
and whether every tolerance was met.

## The knobs

For each parameter, move it in the direction the symptom calls for and stop at the loosest setting
that fixes it - every tightening costs speed.

- **Timestep (`dt`) and substeps.** The integration step is `dt / substeps`. A shorter step is
  more accurate and more stable but proportionally slower. Prefer raising `substeps` over
  shrinking `dt`: it refines the physics while leaving your control and sensor rate at `dt`.
  Reaching for a 1 ms `dt` to paper over instability is the classic anti-pattern - it slows every
  downstream consumer and usually hides a geometry problem.
- **Constraint time constant (`constraint_timeconst`).** How quickly a contact or joint limit is
  resolved. Smaller is stiffer, so bodies penetrate less, but below roughly twice the integration
  step it injects energy and the scene buzzes. Larger is softer and calmer at rest but allows more
  penetration. Keep it at or above `2 * dt / substeps`.
- **Solver iterations (`iterations`) and tolerance (`tolerance`).** The budget and target for
  resolving contacts each step. More iterations or a tighter tolerance hold stacks and grasps more
  firmly at the cost of a slower step; the solve exits early on easy steps, so the budget only
  bites on hard ones.
- **Friction cone (`friction_cone`).** `pyramidal` (default) is robust and cheap to solve.
  `elliptic` is the exact friction model and holds resting stacks against slow sideways creep, but
  it is harder to solve; use it when a pile drifts under sustained shear and the pyramidal cone
  cannot hold it.
- **No-slip iterations (`noslip_iterations`).** Off by default. Turning it on (start around 5)
  suppresses residual slip and drift, which helps manipulation, but it is experimental and slows
  the step - enable it only when slip is the actual problem, not as a first resort.

## Common-bug playbook

- **Jitter at rest.** A settled object that keeps twitching. First confirm the collision mesh is
  clean and convex-decomposed. Then raise `substeps`, and make sure `constraint_timeconst` is not
  below the `2 * dt / substeps` floor. Watch the residual-velocity metric fall as you tighten.
- **Grasp slip.** A held object slides out of the gripper. Increase friction on the contacting
  materials, switch to the `elliptic` friction cone, and if slip persists enable a few
  `noslip_iterations`.
- **Tunneling.** A fast body passes through a thin wall in one step. This is a timestep problem:
  shorten the integration step (raise `substeps`) so the body cannot travel through the wall
  between contact checks, and verify the wall's collision geometry has real thickness.

## See also

- {doc}`rigid_bodies`: the rigid entity and its material properties.
- {doc}`/user_guide/assets/loading_assets`: preparing collision geometry, the first tuning phase.
- {doc}`/user_guide/theory/rigid_solver/index`: the contact and constraint model behind these knobs.
