# Contact sensors

Sensors that report contact on a rigid link, for manipulation, grasping, and physical-interaction tasks. For usage and how to scope a reading with `filter_link_idx`, see the {doc}`contact sensing guide </user_guide/sensing/contact>`.

## `gs.sensors.ContactForce`

The total contact force on the associated link, in its local frame.

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
