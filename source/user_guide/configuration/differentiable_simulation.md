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
loss = ((robot.get_pos() - target) ** 2).sum()

loss.backward()  # propagates through every step back to `force`
print(force.grad)
```

## How autodiff works

- **Enable it once, on the scene:** set `requires_grad=True` in `gs.options.SimOptions`. Each step then saves the state it starts from, and its backward pass replays the step from there. The flag defaults to `False`, so a simulation is non-differentiable unless you opt in; see [Limitations](#limitations) for what differentiable mode costs.
- **Queried states are differentiable:** the entity getters (`get_pos()`, `get_qpos()`, `get_dofs_position()`, `get_dofs_velocity()`, `get_links_pos()`, `get_dofs_control_force()`, `get_dofs_force()`, `get_particles_pos()`, ...) return tensors that carry gradients. They are plain `torch.Tensor`s. A query inside `torch.no_grad()`, for example for logging, returns values without gradient. `scene.get_state()` returns a copy outside of the autograd graph, for restoring the scene rather than computing a loss.
- **Inputs are any torch tensors:** control forces, PD control targets (`control_dofs_position`, `control_dofs_velocity`, `control_dofs_position_velocity`), initial positions, and velocities passed to the setters can be leaf tensors created with `requires_grad=True`, or the output of a torch computation, such as a neural network policy.
- **The simulation is part of the PyTorch graph:** each `scene.step()`, each setter call, and each query is a node of the autograd graph, so `loss.backward()` and `torch.autograd.grad(loss, params)` both differentiate through the physics, down to whatever produced each input, in a single pass.

The rollout behaves like a tensor that the simulator modifies in place. Pass `retain_graph=True` to run backward through the same rollout more than once. Call backward before any of these, each of which makes a later backward pass through the rollout raise an error: `scene.reset()`, a change to the model (such as `set_dofs_kv`), or a setter call inside `torch.no_grad()`. Reset the scene with `scene.reset()` before the next forward pass, for example once per optimization step. `scene.backward(loss)` runs the backward pass and then restores the physics state the scene was in, so the rollout can continue from there. A gradient that is not finite raises an error during the backward pass, which names the step where it appeared.

## Training a policy through the dynamics

An input may depend on states queried earlier in the same rollout, which closes the loop between a policy and the simulation. The gradient reaches the policy parameters through every step, and an action penalty can share the loss with the states without passing `retain_graph=True`. Here the scene is built with parallel environments (`scene.build(n_envs=16)`), so the actions have one row per environment:

```python
n_qs, n_dofs = robot.n_qs, robot.n_dofs
policy = torch.nn.Linear(n_qs + n_dofs, n_dofs).to(device=gs.device, dtype=gs.tc_float)
optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)
target_qpos = robot.get_qpos().detach() + 0.1

for _ in range(100):  # optimization iterations
    scene.reset()
    loss = 0.0
    for _ in range(50):  # horizon
        force = policy(torch.cat((robot.get_qpos(), robot.get_dofs_velocity()), dim=-1))
        robot.control_dofs_force(force)
        scene.step()
        loss = loss + 1e-4 * (force**2).sum()
    loss = loss + ((robot.get_qpos() - target_qpos) ** 2).sum()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

An input given after the last state the loss reads cannot affect the loss, so its gradient stays `None`, as for any tensor that does not contribute to a PyTorch loss. To stop gradients from flowing back through a state, use `detach()` as for any PyTorch tensor.

## Limitations

- **Supported solvers and couplings:** the rigid and kinematic solvers, the MPM solver without CPIC, and the FEM solver with its explicit integrator support gradients. The PBD, SPH and SF solvers, the implicit FEM solver, the coupling of FEM with rigid, MPM or SPH entities, and the SAP and IPC couplers do not. `scene.build()` raises an error that names each unsupported component.
- **Memory scales with horizon:** each step saves the state it starts from, so long trajectories consume proportionally more GPU memory.
- **Some contact and collision paths have no gradients:** gradients through them may be zero or undefined. The rigid solver uses the GJK collision path when gradients are required (see {doc}`/user_guide/theory/rigid_solver/collision_detection`), and the elliptic friction cone and `box_box_detection=True` are unsupported (see {doc}`/user_guide/theory/rigid_solver/constraints`).
- **Coupler support:** the default legacy coupler carries gradients; the SAP coupler does not. See {doc}`/user_guide/physics/coupling/index`.
- **Hibernation:** unavailable when `requires_grad=True`; see {doc}`/user_guide/theory/rigid_solver/collision_detection`.
- **Numerical stability over long horizons:** gradients backpropagated through many steps can vanish or explode, as with any long recurrent computation.

## See also

- {doc}`/user_guide/configuration/checkpoints`: resetting the scene between optimization passes.
- {doc}`/user_guide/physics/coupling/index`: which coupler to use for gradients.
