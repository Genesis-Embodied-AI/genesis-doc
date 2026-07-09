# Contact sensors

Genesis World provides sensors for detecting and measuring contact forces. These are essential for manipulation tasks, grasping, and understanding physical interactions.

## ContactForceSensor

The `ContactForceSensor` measures the total contact force being applied to the associated rigid link in its local frame.

### Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))
finger = robot.get_link("finger_link")

# Add contact force sensor to gripper finger
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=finger.idx_local,
    )
)

scene.build()

# Simulation loop
for i in range(1000):
    scene.step()

    # Get contact force (plain tensor, not NamedTuple)
    force = contact_sensor.read()  # ([n_envs,] 3) force in Newtons
    print(f"Contact force: {force}")
```

### Output format

`read()` returns a plain `torch.Tensor` (float32):

| Shape | Description |
|-------|-------------|
| `([n_envs,] 3)` | Total contact force in local link frame (Newtons) |

The options passed to `gs.sensors.ContactForce` (offsets, force clamping, noise) are documented in the reference below.

## ContactSensor

The `ContactSensor` detects whether the associated rigid link is in contact (boolean).

### Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("base").idx_local,
    )
)

scene.build()
scene.step()
in_contact = contact.read()  # ([n_envs,] 1) boolean tensor
```

### Output format

`read()` returns a plain `torch.Tensor` (bool):

| Shape | Description |
|-------|-------------|
| `([n_envs,] 1)` | True if link is in contact |

## API reference

### `gs.sensors.ContactForce`

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.ContactForce
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.contact_force.ContactForceSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

### `gs.sensors.Contact`

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.Contact
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.contact_force.ContactSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: Sensor overview
- {doc}`/api_reference/entity/rigid_entity/index`: RigidEntity and links
