# 🖐️ Sensors

Robots need sensors to observe the world around them.
In Genesis, sensors extract information from the scene, computing values using the state of the scene but not affecting the scene itself.
All sensors have a `read()` function that returns the sensor data.

Currently only Camera and rigid tactile sensors are supported, but soft tactile and distance (LiDAR) sensors are coming soon!

## Tactile Hand Example

In this tutorial, we'll walk through how to set up tactile sensors on an Allegro robotic hand. We'll add `RigidContactForceGridSensor` to each fingertip to detect contact forces when the hand interacts with objects.

The full example script is available at `examples/sensors/tactile/tactile_fingertips.py`.

### Scene Setup

First, let's create our simulation scene and load the robotic hand:

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu, logging_level=None)

########################## scene setup ##########################
scene = gs.Scene()

scene.add_entity(gs.morphs.Plane())

# define which fingertips we want to add sensors to
sensorized_link_names = [
    "index_3_tip",
    "middle_3_tip",
    "ring_3_tip",
    "thumb_3_tip",
]

# load the hand .urdf
hand = scene.add_entity(
    morph=gs.morphs.URDF(
        file="allegro_hand/allegro_hand_right_glb.urdf",
        pos=(0.0, 0.0, 0.1),
        euler=(0.0, -90.0, 180.0),
        fixed=True,  # Fix the base so the whole hand doesn't flop on the ground
        links_to_keep=sensorized_link_names,  # Make sure the links we want to sensorize aren't merged
    ),
    material=gs.materials.Rigid(),
)

# Some arbitrary objects to interact with the hand: spheres arranged in a circle
pos_radius = 0.06
for i in range(10):
    scene.add_entity(
        gs.morphs.Sphere(
            pos=(pos_radius * np.cos(i * np.pi / 5) + 0.02, pos_radius * np.sin(i * np.pi / 5), 0.3 + 0.04 * i),
            radius=0.02,
        ),
        surface=gs.surfaces.Default(
            color=(0.0, 1.0, 1.0, 0.5),
        ),
    )
```

Here we load a robotic hand and specify which fingertip links we want to attach sensors to.
The `links_to_keep` parameter ensures that the links will not be merged when the URDF is parsed. (Links that are attached with fixed joints are merged to optimize the simulator.)

The small spheres positioned in a circle above the hand will fall down and create contact forces when they hit the fingertips.


### Adding the Sensors

```python
########################## add sensors ##########################
sensors = []
for link in hand.links:
    if link.name in sensorized_link_names:
        sensor = RigidContactForceGridSensor(entity=hand, link_idx=link.idx, grid_size=(2, 2, 2))
        sensors.append(sensor)

cam = scene.add_camera(
    res=(1280, 960),
    pos=(0.5, 0.7, 0.7),
    lookat=(0.0, 0.0, 0.1),
    fov=20,
    GUI=args.vis,
)
```

The `RigidContactForceGridSensor` takes three parameters:
- A rigid entity (our hand)
- The specific link index (fingertip link)
- The grid dimensions `(2, 2, 2)` specifies the resolution (grid size) of the sensor.

Now let's position the hand and run the simulation:

```python
########################## build ##########################
scene.build(n_envs=args.n_envs)

dofs_position = [0.1, 0, -0.1, 0.7, 0.6, 0.6, 0.6, 1.0, 0.65, 0.65, 0.65, 1.0, 0.6, 0.6, 0.6, 0.7]
if args.n_envs > 0:
    dofs_position = [dofs_position] * args.n_envs
hand.set_dofs_position(np.array(dofs_position))

max_observed_force_magnitude = 0.0
for _ in tqdm(range(steps), total=steps):
    scene.step()

    for sensor in sensors:
        grid_forces = sensor.read()  # data shape: [n_envs, grid_x, grid_y, grid_z, 3] where 3 is for force xyz
        grid_force_magnitudes = np.linalg.norm(grid_forces, axis=-1)
        max_observed_force_magnitude = max(max_observed_force_magnitude, np.max(grid_force_magnitudes))
```

Each sensor returns force data with shape `(n_envs, grid_x, grid_y, grid_z, 3)`, where the last dimension contains the 3D force vector `[fx, fy, fz]` at each grid cell.

### Visualization

Curious how it looks?
Using the force data read by the sensor at each step and applying some transformations, we can visualize the forces the fingertips are feeling!

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/tactile_fingertips.mp4" type="video/mp4">
</video>

The function `visualize_grid_sensor()` is provided in the full example script, but we don't recommend its usage outside of this demo because it is very inefficient.

Instead, the sensor data can be collected for post-processing outside of the simulation!

## Data Recording

Genesis provides tools to automatically record sensor data.

`SensorDataRecorder` can record multiple sensors at varying rates and save the collected data at once.

```python
from genesis.sensors import SensorDataRecorder, RecordingOptions, NPZFileWriter, VideoFileWriter
...

data_recorder = SensorDataRecorder(step_dt=dt)  # step_dt should match simulation dt
data_recorder.add_sensor(cam, VideoFileWriter(filename="video.mp4", fps=1/dt))  # fps=1/dt for real-time video speed
data_recorder.add_sensor(sensor, NPZFileWriter(filename="sensor_data.npz"))

# Run simulation and automatically record all sensor data
data_recorder.start_recording()
for i in range(1000):
    scene.step()
    data_recorder.step()  # calls read() on each sensor depending on its associated RecordingOptions

data_recorder.stop_recording()
```

By default, sensor data is read every step.
You can specify `RecordingOptions` to adjust the sampling rate.

```python
data_recorder.add_sensor(
    sensor,
    RecordingOptions(
        handler=NPZFileWriter(filename="sensor_data.npz"),
        hz=60
    )
)
```

You may also define custom data handlers.
```python
from genesis.sensors import DataHandler

class CustomDataHandler(DataHandler):
    def initialize(self):
        ...

    def process(self, data):
        ...

    def cleanup(self):
        ...
```