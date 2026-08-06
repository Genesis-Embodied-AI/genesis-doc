# Engine

The engine is the core of Genesis World: a `Scene` wraps a `Simulator` that owns the physics **solvers**, a **coupler** that resolves interactions between them, the **entities**, their **materials**, and the **sensors** that read the scene. This section mirrors the `genesis.engine` package and documents each of those components, ordered from the top-level container down to the pieces it holds.

The scene constructs the engine objects. Describe it through options and entities, and `scene.build()` builds the solvers, coupler, and states from them. For how the pieces fit together and the step loop, see {doc}`/user_guide/theory/coupling/index`.

```{toctree}
:titlesonly:

scene
simulator
solvers/index
couplers/index
entity/index
material/index
states/index
sensors/index
mesh
force_field
```

## See also

- {doc}`/user_guide/theory/coupling/index`: how the simulator, solvers, and coupler advance a scene.
- {doc}`/user_guide/getting_started/hello_genesis`: building and stepping a scene.
