# Entity spec

An entity spec is the typed description that {py:meth}`scene.add_entity(spec=...) <genesis.engine.scene.Scene.add_entity>` constructs an entity from. Its class, such as `gs.entities.Rigid` or `gs.entities.FEM`, decides the kind of entity and the solver simulating it. Its `select` method records density, friction or fixed vertices on parts of the entity, which `gs.indices` selectors name. For usage, see {doc}`/user_guide/physics/rigid_bodies` and {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Entity spec classes

```{eval-rst}
.. autoclass:: genesis.options.entities.Spec
    :members: morphs

.. autoclass:: genesis.options.entities.Rigid
    :members: select
    :show-inheritance:

.. autoclass:: genesis.options.entities.Kinematic
    :show-inheritance:

.. autoclass:: genesis.options.entities.FEM
    :members: select
    :show-inheritance:

.. autoclass:: genesis.options.entities.MPM
    :show-inheritance:

.. autoclass:: genesis.options.entities.SPH
    :show-inheritance:

.. autoclass:: genesis.options.entities.PBD
    :show-inheritance:

.. autoclass:: genesis.options.entities.Hybrid
    :show-inheritance:
```

## Selections

```{eval-rst}
.. autoclass:: genesis.options.entities.LinkSelection
    :members: select, set, set_rho, set_friction, set_friction_torsional, set_friction_rolling, end

.. autoclass:: genesis.options.entities.GeomSelection
    :members: select, set, set_rho, set_friction, set_friction_torsional, set_friction_rolling, end

.. autoclass:: genesis.options.entities.VertexSelection
    :members: select, set, set_is_fixed, end
```

## Selectors

```{eval-rst}
.. autoclass:: genesis.options.indices.Link
    :members: named, subtree

.. autoclass:: genesis.options.indices.Geom
    :members: at

.. autoclass:: genesis.options.indices.Vertex
    :members: at, in_box, closest_to
```

## Quantities set on parts

```{eval-rst}
.. autoclass:: genesis.options.patches.Geom

.. autoclass:: genesis.options.patches.Vertex
```
