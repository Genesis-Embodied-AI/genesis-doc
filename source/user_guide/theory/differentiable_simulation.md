# Differentiable simulation

Genesis World can run the physics engine in differentiable mode, so you can backpropagate a loss defined on simulation outputs all the way back to the inputs that produced them. Use it to optimize control signals, fit physical parameters, or train policies through the dynamics rather than around them.

## Minimal example

Enable differentiable mode with `requires_grad=True` on {py:class}`gs.options.SimOptions <genesis.options.solvers.SimOptions>`, run the simulation forward, then call `backward()` on a loss:

```python
import genesis as gs
import torch

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,  # seconds
        requires_grad=True,  # enable differentiable mode
    ),
)
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# A control signal we want gradients for
force = torch.zeros(robot.n_dofs, dtype=gs.tc_float, device=gs.device, requires_grad=True)

for _ in range(100):
    robot.control_dofs_force(force)
    scene.step()

target = torch.tensor([1.0, 0.0, 0.5], dtype=gs.tc_float, device=gs.device)
loss = ((robot.get_state().pos - target) ** 2).sum()

loss.backward()  # propagates through every step back to `force`
print(force.grad)
```

## How autodiff works

- **Enable it once, on the scene:** set `requires_grad=True` in `gs.options.SimOptions`. Genesis World then records the intermediate substep state each step needs for the backward pass. The flag defaults to `False`, so a simulation is non-differentiable unless you opt in; see [Limitations](#limitations) for what differentiable mode costs.
- **Queried states are differentiable:** `get_state()` on an entity (`robot.get_state().pos`) or on a solver (`scene.rigid_solver.get_state().qpos`) returns states whose tensors carry gradients. They are plain `torch.Tensor`s. The other getters (`get_pos()`, `get_qpos()`, ...) return values without gradient.
- **Inputs are any torch tensors:** control forces, initial positions, and target values passed to the setters can be leaf tensors created with `requires_grad=True`, or the output of a torch computation, such as a neural network policy.
- **The simulation is part of the PyTorch graph:** each `scene.step()` is a node of the autograd graph, so `loss.backward()` and `torch.autograd.grad(loss, params)` both differentiate through the physics, down to whatever produced each input, in a single pass.

A single forward run supports one backward pass. Reset the scene with `scene.reset()` before the next forward pass, for example once per optimization step, and call backward before that reset: differentiating a run after `scene.reset()` raises an error. `scene.backward(loss)` runs the backward pass and then restores the physics state the scene was in, so the rollout can continue from there. The tensors of a queried state always lead with the environment dimension, of size 1 when the scene has no parallel environments (`[max(1, n_envs), ...]`).

## Training a policy through the dynamics

An input may depend on states queried earlier in the same rollout, which closes the loop between a policy and the simulation. The gradient reaches the policy parameters through every step, and an action penalty can share the loss with the states without passing `retain_graph=True`. Here the scene is built with parallel environments (`scene.build(n_envs=16)`), so the actions have one row per environment:

```python
n_qs, n_dofs = scene.rigid_solver.n_qs, scene.rigid_solver.n_dofs
policy = torch.nn.Linear(n_qs + n_dofs, n_dofs).to(device=gs.device, dtype=gs.tc_float)
optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)
target_qpos = scene.rigid_solver.get_state().qpos.detach() + 0.1

for _ in range(100):  # optimization iterations
    scene.reset()
    loss = 0.0
    for _ in range(50):  # horizon
        state = scene.rigid_solver.get_state()
        force = policy(torch.cat((state.qpos, state.dofs_vel), dim=-1))
        robot.control_dofs_force(force)
        scene.step()
        loss = loss + 1e-4 * (force**2).sum()
    loss = loss + ((scene.rigid_solver.get_state().qpos - target_qpos) ** 2).sum()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

An input given after the last state the loss reads cannot affect the loss, so its gradient stays `None`, as for any tensor that does not contribute to a PyTorch loss. To stop gradients from flowing back through a state, use `detach()` as for any PyTorch tensor.

## Limitations

- **Memory scales with horizon:** differentiable mode stores intermediate substep state for every step, so long trajectories consume proportionally more GPU memory. Set `substeps_local` in `gs.options.SimOptions` to control how much substep state is retained; in differentiable mode it must be divisible by `substeps`.
- **Some contact and collision paths have no gradients:** gradients through them may be zero or undefined. The rigid solver uses the GJK collision path when gradients are required (see {doc}`rigid_solver/collision_detection`), and the elliptic friction cone is unsupported (see {doc}`rigid_solver/constraints`).
- **Coupler support:** the default legacy coupler carries gradients; the SAP coupler does not. See {doc}`coupling/index`.
- **Hibernation:** unavailable when `requires_grad=True`; see {doc}`rigid_solver/collision_detection`.
- **Numerical stability over long horizons:** gradients backpropagated through many steps can vanish or explode, as with any long recurrent computation.

## See also

- {doc}`/user_guide/configuration/checkpoints`: resetting the scene between optimization passes.
- {doc}`coupling/index`: which coupler to use for gradients.
