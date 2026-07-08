# Differentiable simulation

Genesis World can run the physics engine in differentiable mode, so you can backpropagate a loss defined on simulation outputs all the way back to the inputs that produced them. Use it to optimize control signals, fit physical parameters, or train policies through the dynamics rather than around them.

This page covers how autodiff works in Genesis World and how the differentiable tensor type fits together. The child pages document the tensor class and the tensor-creation operations:

```{toctree}
:titlesonly:

tensor
creation_ops
```

## Minimal example

Enable differentiable mode with `requires_grad=True` on `gs.options.SimOptions`, run the simulation forward, then call `backward()` on a loss:

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
force = torch.zeros(robot.n_dofs, device=gs.device, requires_grad=True)

for _ in range(100):
    robot.control_dofs_force(force)
    scene.step()

target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)
loss = torch.nn.functional.mse_loss(robot.get_pos(), target)

loss.backward()  # propagates through every step back to `force`
print(force.grad)
```

## How autodiff works

- **Enable it once, on the scene:** set `requires_grad=True` in `gs.options.SimOptions`. Genesis World then records the intermediate substep state each step needs for the backward pass. The flag defaults to `False`, so simulations are non-differentiable unless you opt in.
- **State getters return differentiable tensors:** methods such as `get_pos()`, `get_vel()`, and `get_qpos()` return a `gs.Tensor` (documented on the {doc}`tensor` page), a subclass of `torch.Tensor` that also carries a reference to the scene it came from.
- **`backward()` flows through the physics:** calling `backward()` on any tensor derived from scene state runs the standard PyTorch backward pass, then continues the gradient backward through time across the recorded steps, down to the inputs you marked with `requires_grad=True`.
- **Inputs are ordinary leaf tensors:** control forces, initial positions, and target values are plain PyTorch tensors created with `requires_grad=True`. Any operation that mixes them with scene-derived tensors yields a scene-tracked tensor, which keeps the graph connected.

A single forward run supports one backward pass. Reset the scene with `scene.reset()` before the next forward pass, for example once per optimization step.

## Shapes and conventions

State getters follow the codebase's batched-optional shape notation. With a scene built for a single environment the batch dimension is absent; with multiple environments it leads:

```python
pos = robot.get_pos()  # shape ([n_envs,] 3)
vel = robot.get_vel()  # shape ([n_envs,] 3)
```

Positions are in meters, velocities in m/s. The coordinate system is right-handed and Z-up, with gravity along `-Z` at 9.81 m/s² by default.

## Example: trajectory optimization

Optimize a full control sequence to drive the robot's base to a target. The scene is reset each step so every backward pass runs against a fresh forward trajectory:

```python
import genesis as gs
import torch

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,  # seconds
        requires_grad=True,
    ),
)
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

n_steps = 100
controls = torch.zeros(n_steps, robot.n_dofs, device=gs.device, requires_grad=True)
optimizer = torch.optim.Adam([controls], lr=0.01)
target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)

for step in range(100):
    scene.reset()
    for t in range(n_steps):
        robot.control_dofs_force(controls[t])
        scene.step()

    loss = torch.nn.functional.mse_loss(robot.get_pos(), target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"step {step}: loss = {loss.item():.4f}")
```

## Detaching from the scene

To stop gradients from flowing back into the simulation, drop the tensor's scene association:

```python
pos = robot.get_pos()
pos_detached = pos.detach()      # detaches from autograd and from the scene
pos_sceneless = pos.sceneless()  # keeps autograd, drops only the scene link
```

`detach()` removes the scene link by default (`sceneless=True`); pass `sceneless=False` to keep it. Use `sceneless()` when you want a tensor to stay in the PyTorch graph but not feed gradients back through the physics. Reading `tensor.scene` tells you which scene, if any, a tensor is bound to.

:::{note}
Mixing two tensors that belong to different scenes raises an error, since gradients cannot flow into more than one scene. Call `sceneless()` on one of them first if you do not need the gradient to reach its scene.
:::

## Limitations

- **Memory scales with horizon:** differentiable mode stores intermediate substep state for every step, so long trajectories consume proportionally more GPU memory. Set `substeps_local` in `gs.options.SimOptions` to control how much substep state is retained; in differentiable mode it must be divisible by `substeps`.
- **Not every operation is differentiable:** some contact and collision paths do not provide gradients. Gradients through those paths may be zero or undefined.
- **Numerical stability over long horizons:** gradients backpropagated through many steps can vanish or explode, as with any long recurrent computation.

## See also

- {doc}`tensor`: the differentiable tensor class
- {doc}`creation_ops`: creating tensors for differentiable simulation
- {doc}`/api_reference/engine/states/index`: reading and writing simulation state
