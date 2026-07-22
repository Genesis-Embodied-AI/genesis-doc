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
- **State getters return differentiable tensors:** methods such as `get_pos()`, `get_vel()`, and `get_qpos()` return a {py:class}`gs.Tensor <genesis.grad.tensor.Tensor>` (a subclass of `torch.Tensor` that also carries a reference to the scene it came from). See the {doc}`Tensor reference </api_reference/differentiation/tensor>`.
- **`backward()` flows through the physics:** calling `backward()` on any tensor derived from scene state runs the standard PyTorch backward pass, then continues the gradient backward through time across the recorded steps, down to the inputs you marked with `requires_grad=True`.
- **Inputs are ordinary leaf tensors:** control forces, initial positions, and target values are plain PyTorch tensors created with `requires_grad=True`. Any operation that mixes them with scene-derived tensors yields a scene-tracked tensor, which keeps the graph connected.

A single forward run supports one backward pass. Reset the scene with `scene.reset()` before the next forward pass, for example once per optimization step. State tensors follow the batched-optional shape convention (`([n_envs,] ...)`); see {doc}`/user_guide/configuration/conventions`.

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
- **Not every operation is differentiable:** some contact and collision paths do not provide gradients. Gradients through those paths may be zero or undefined. The rigid solver uses the GJK collision path when gradients are required (see {doc}`rigid_collision/collision_contacts_forces`), and the elliptic friction cone is unsupported (see {doc}`rigid_collision/rigid_constraint_model`).
- **Coupler support:** differentiable simulation is supported by the default legacy coupler; the SAP coupler does not support it. See {doc}`couplers/index`.
- **Hibernation is unavailable** when `requires_grad=True`; see {doc}`hibernation`.
- **Numerical stability over long horizons:** gradients backpropagated through many steps can vanish or explode, as with any long recurrent computation.

## See also

- {doc}`/api_reference/differentiation/index`: the differentiable tensor and creation-op reference.
- {doc}`/user_guide/configuration/checkpoints`: resetting the scene between optimization passes.
- {doc}`solvers_and_coupling`: which coupler to use for gradients.
