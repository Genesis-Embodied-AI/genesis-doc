# API Reference

This section documents the Genesis World API. It is generated from the source docstrings and its structure mirrors the code: each top-level section corresponds to a `genesis` subpackage, so the reference tree and the import paths line up. Task-oriented explanations, examples, and tutorials live in the {doc}`User Guide </user_guide/index>`.

## How this reference is organized

- **{doc}`Options <options/index>`** (`genesis.options`): the index to every options class, and the home for those with no built-object page.
- **{doc}`Engine <engine/index>`** (`genesis.engine`): the scene, simulator, solvers, coupler, entities, materials, states, and sensors that make up a simulation.
- **{doc}`Visualization <visualization/index>`** (`genesis.vis`): the viewer, cameras, renderer backends, and lights.
- **{doc}`Recording <recording/index>`** (`genesis.recorders`): recorders that capture simulation data to files or live plots.
- **{doc}`Differentiable simulation <differentiation/index>`** (`genesis.grad`): the gradient-carrying tensor type and its creation ops.
- **{doc}`Utilities <utilities/index>`** (`genesis.utils`): geometry, mesh, tensor, and device helpers.

## Options and built objects

Most components in Genesis World come in two halves: an **options** class you configure, and the **built object** the engine constructs from it. You pass an options instance in (`gs.options.RigidOptions`, `gs.sensors.IMU`, `gs.renderers.Rasterizer`, ...), and Genesis builds the working object it configures (`RigidSolver`, `IMUSensor`, the rasterizer backend, ...) when the scene builds. The options carry the settings; the built object carries the runtime state and methods.

Reference pages follow this flow: the options class is documented **first**, then the built object it produces **below** it. Read the options to see what you can set, and the built object to see what you can call and read back once the scene is running. Configuration classes with no separate built object (morphs, materials, surfaces, textures) appear on their own, and the few options with no built-object page at all are collected on the {doc}`Options <options/index>` page.

```{toctree}
:titlesonly:
:maxdepth: 2
:hidden:

options/index
engine/index
visualization/index
recording/index
differentiation/index
utilities/index
```
