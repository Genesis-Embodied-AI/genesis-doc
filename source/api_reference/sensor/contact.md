# Contact Sensors

Genesis provides sensors for detecting and measuring contact forces. These are essential for manipulation tasks, grasping, and understanding physical interactions.

## ContactForceSensor

The `ContactForceSensor` measures forces and torques at contact points on a specified link.

### Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))
scene.build()

# Add contact force sensor to gripper finger
finger = robot.get_link("finger_link")
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        link=finger,
    )
)

# Simulation loop
for i in range(1000):
    scene.step()

    # Get contact force data
    force_data = contact_sensor.get_data()
    print(f"Contact force: {force_data}")
```

### Configuration

```python
gs.sensors.ContactForce(
    link=link,              # RigidLink to attach sensor to
    frame="world",          # Reference frame: "world" or "local"
    noise_pos=0.0,          # Position noise standard deviation
    noise_quat=0.0,         # Orientation noise standard deviation
)
```

## ContactSensor

The `ContactSensor` detects contact events (collision start/end) without force measurement.

### Usage

```python
contact = scene.add_sensor(
    gs.sensors.Contact(
        link=robot.get_link("base"),
    )
)

scene.step()
contacts = contact.get_data()
```

## API Reference

### ContactForceSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactForceSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

### ContactSensor

```{eval-rst}
.. autoclass:: genesis.engine.sensors.ContactSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Sensor overview
- {doc}`/api_reference/entity/rigid_entity/index` - RigidEntity and links
