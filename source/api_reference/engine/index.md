# Engine

The engine is the core of Genesis World: a `Scene` wraps a `Simulator` that owns the physics **solvers**, a **coupler** that resolves interactions between them, the **entities** you add, their **materials**, and the **sensors** that read the scene. This section mirrors the `genesis.engine` package and documents each of those components, ordered from the top-level container down to the pieces it holds.

You rarely construct engine objects directly. You describe a scene through options and entities, and the scene builds the solvers, coupler, and states from them when you call `scene.build()`. For how the pieces fit together and the step loop, see {doc}`/user_guide/theory/solvers_and_coupling`.

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

- {doc}`/user_guide/theory/solvers_and_coupling`: how the simulator, solvers, and coupler advance a scene.
- {doc}`/user_guide/getting_started/hello_genesis`: building and stepping a scene.
