# Tactile sensors

Tactile sensors turn a rigid link's surface into a grid of sensing points, or **taxels**, and report how that surface interacts with nearby geometry. They range from a per-probe contact flag to dense per-taxel force, torque, and elastomer-displacement fields that imitate a tactile skin.

Two families share this interface but estimate contact differently:

- **SDF-query probes** (`ContactProbe`, `ContactDepthProbe`, `KinematicTaxel`) query the signed distance from each probe to nearby collision geometry. They need no list of target links.
- **Point-cloud probes** (`ElastomerTaxel`, `ProximityTaxel`) sample a point cloud from the tracked meshes and measure against those points.

Create a sensor from the matching `gs.sensors.*` options object with `scene.add_sensor()`; the call returns the sensor handle whose `read()` gives the measured value. For the attach-and-read model, probe layout with `probe_local_pos`, and the force models behind each estimate, see {doc}`the contact and tactile sensors guide </user_guide/getting_started/sensors/contact_and_tactile>`.

## ContactProbe

Thresholds each probe's penetration depth into a per-probe boolean contact flag.

```{eval-rst}
.. autoclass:: genesis.options.sensors.tactile.ContactProbe
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.kinematic_tactile.ContactProbeSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## ContactDepthProbe

Reports the penetration depth at each probe, in meters.

```{eval-rst}
.. autoclass:: genesis.options.sensors.tactile.ContactDepthProbe
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.kinematic_tactile.ContactDepthProbeSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## KinematicTaxel

Adds a spring-damper force model on top of the depth query, estimating per-taxel force and torque from penetration and relative motion.

```{eval-rst}
.. autoclass:: genesis.options.sensors.tactile.KinematicTaxel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.kinematic_tactile.KinematicTaxelSensor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.kinematic_tactile.KinematicTaxelReturnType
   :members:
   :undoc-members:
```

## ElastomerTaxel

Models a soft tactile skin, reporting a 3D marker displacement per probe from indentation and shear against the tracked geometry.

```{eval-rst}
.. autoclass:: genesis.options.sensors.tactile.ElastomerTaxel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.point_cloud_tactile.ElastomerTaxelSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## ProximityTaxel

Estimates per-taxel force and torque from a point cloud sampled on the tracked meshes within a spherical sensing volume around each taxel, capturing near-touch as well as touch.

```{eval-rst}
.. autoclass:: genesis.options.sensors.tactile.ProximityTaxel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.point_cloud_tactile.ProximityTaxelSensor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.point_cloud_tactile.ProximityTaxelReturnType
   :members:
   :undoc-members:
```

## See also

- {doc}`index` - Sensor overview
- {doc}`/user_guide/getting_started/sensors/contact_and_tactile` - Usage, probe layout, and force models
- {doc}`contact` - Solver-based contact and contact-force sensing
