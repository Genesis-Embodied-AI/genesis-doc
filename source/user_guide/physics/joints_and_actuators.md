# Joints and Actuators

A movable joint of a rigid entity adds one or more **degrees of freedom** (**dofs**); a fixed joint adds none. Each dof carries its own physical and actuator parameters. Genesis World reads them from the URDF or MJCF file when the model provides them. After `scene.build()`, a `set_dofs_*` method overrides a parameter, and the matching `get_dofs_*` method reads it back:

```python
franka.set_dofs_damping(np.full(7, 2.0), dofs_idx_local=np.arange(7))
print(franka.get_dofs_damping())  # shape ([n_envs,] n_dofs) when batch_dofs_info=True, (n_dofs,) otherwise
```

All of these methods take values paired with `dofs_idx_local`, the same pattern as the {doc}`control tutorial </user_guide/getting_started/control_your_robot>`. They require a built scene and raise if called before `build()`.

## Choose the parameter that matches the model

**Passive damping** opposes joint velocity even when the actuator is not commanding the joint. The controller's **velocity gain** `kv` instead sets the response to a velocity error in the active control mode. They can both reduce oscillation, but tune damping to represent the joint's physical resistance and `kv` to set the controller response.

**Armature** adds inertia in joint coordinates, for example to represent motor inertia reflected through a gearbox. Changing a link's mass also changes its weight and the forces it exerts on other bodies. Use armature for the joint-side inertia you intend to model, rather than changing link mass to obtain the same control response.

The tables below connect these physical choices to the setters and model-file fields. See {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>` for method signatures and argument details.

## Passive joint parameters

These parameters act on the dof whether or not you command it.

| Parameter | Setter | Effect | URDF / MJCF source |
|---|---|---|---|
| Stiffness | `set_dofs_stiffness` | A spring pulling the dof back toward position zero, in N·m/rad or N/m. | MJCF joint `stiffness`; zero for URDF. |
| Damping | `set_dofs_damping` | A force opposing the dof velocity, in N·m·s/rad or N·s/m. | URDF `<dynamics damping>`, MJCF joint `damping`. |
| Armature | `set_dofs_armature` | Inertia added to the dof itself, as the reflected inertia of a geared motor rotor. | MJCF joint `armature`; zero for URDF. |
| Friction loss | `set_dofs_frictionloss` | Dry friction in the joint: the dof does not move until the applied force exceeds this value. | URDF `<dynamics friction>`, MJCF joint `frictionloss`. |
| Limits | `set_dofs_limit` | The position range of the dof, enforced as a constraint when `RigidOptions.enable_joint_limit` is on. | URDF `<limit>`, MJCF joint `range`. |

Armature matters most for small, fast links such as fingers and the distal joints of an arm. A real actuator adds inertia to these joints through its gearbox. Omitting that inertia can make the simulated response faster than the hardware response and can make high-gain control harder to integrate at a large `dt`.

## Actuator parameters

`control_dofs_position` and `control_dofs_velocity` drive a dof through a PD controller. Its gains and the force it may apply are dof parameters too:

| Parameter | Setter | Effect |
|---|---|---|
| Position gain | `set_dofs_kp` | Force per unit of position error. |
| Velocity gain | `set_dofs_kv` | Force per unit of velocity error. |
| Force range | `set_dofs_force_range` | Lower and upper bound on the actuator force, in N·m or N. The controller output is clipped to it. |

`control_dofs_force` skips the PD controller and applies the force directly, still clipped to the force range. {doc}`Control your robot </user_guide/getting_started/control_your_robot>` shows the three control modes together.

For actuators that a PD controller does not describe, `set_dofs_act_gain` and `set_dofs_act_bias` set a general affine actuator: the force is the gain times the command, plus a bias made of a constant term, a position term, and a velocity term. `set_dofs_kp` and `set_dofs_kv` write into these same values, so a call to `set_dofs_kp` after `set_dofs_act_gain` resets the actuator to a PD controller.

## Different values per environment

By default, a dof parameter is shared by every environment in the batch, so a setter takes one value per dof and raises on a per-environment array. To give each environment its own value, for example to randomize damping or gains across training environments, set `batch_dofs_info=True` before the build:

```python
scene = gs.Scene(rigid_options=gs.options.RigidOptions(batch_dofs_info=True))
...
scene.build(n_envs=1024)
damping = torch.rand(1024, 7, device=gs.device) * 5.0
franka.set_dofs_damping(damping, dofs_idx_local=np.arange(7))
```

Batched parameters cost one copy per environment, in memory and in the bandwidth to read them, so enable this only when you need it. Heterogeneous scenes enable it automatically. {doc}`Domain randomization </user_guide/policy_training/domain_randomization>` covers the full workflow.

## See also

- {doc}`Control your robot </user_guide/getting_started/control_your_robot>`: position, velocity, and force control in one tutorial.
- {doc}`Rigid bodies </user_guide/physics/rigid_bodies>`: link mass, density, and contact friction.
- {doc}`Tuning simulation parameters </user_guide/configuration/simulation_tuning>`: when to tune joints before contacts.
- {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>`: the full list of `set_dofs_*` and `get_dofs_*` methods.
