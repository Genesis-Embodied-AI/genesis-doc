# Contact sensors

Sensors that report contact on a rigid link, for manipulation, grasping, and physical-interaction tasks. For the attach-and-read model and how to scope a reading with `filter_link_idx`, see the {doc}`contact sensing guide </user_guide/sensing/contact>`.

## `gs.sensors.ContactForce`

The total contact force on the associated link, in its local frame.

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FR_foot").idx_local,
    )
)
scene.build()
scene.step()

force = sensor.read()  # shape ([n_envs,] 3), Newtons, link-local frame
```

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.ContactForce
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.contact_force.ContactForceSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.sensors.Contact`

A boolean: whether the associated link is in contact.

```python
# ... scene and robot set up as above ...
contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FR_foot").idx_local,
    )
)
scene.build()
scene.step()

in_contact = contact.read()  # shape ([n_envs,] 1), bool
```

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

- {doc}`index`: sensor overview.
- {doc}`/user_guide/sensing/contact`: the contact sensing guide.
- {doc}`/api_reference/entity/rigid_entity/index`: RigidEntity and links.
