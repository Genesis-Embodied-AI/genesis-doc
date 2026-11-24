# Entity spec and part selection

An entity spec describes an entity before it is built. Pass it as {py:meth}`scene.add_entity(spec=...) <genesis.engine.scene.Scene.add_entity>`, in place of the `morph`, `material` and `surface` arguments. Its class, such as `gs.entities.Rigid` or `gs.entities.FEM`, decides the kind of entity and the solver simulating it.

The `select` method of a spec picks parts of the entity with a `gs.indices` selector: links, collision geoms, visual geoms or vertices. The selection then sets options on those parts, such as density, friction, surface or fixed vertices:

```python
franka_spec = gs.entities.Rigid(
    morph=gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
fingers = franka_spec.select(gs.indices.Link.named("left_finger", "right_finger"))
fingers.select(gs.indices.Geom.at(slice(1, 6))).set_friction(1.5)
franka = scene.add_entity(spec=franka_spec)
```

A value set on a finer level overrides one set on a coarser level: the material or the surface of the entity, then a link selection, then a geom or visual geom selection. For usage, see {doc}`/user_guide/physics/rigid_bodies` and {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Entity specs

```{eval-rst}
.. autoclass:: genesis.options.entities.Spec
    :members: morphs

.. autoclass:: genesis.options.entities.Rigid
    :members: select
    :show-inheritance:

.. autoclass:: genesis.options.entities.Kinematic
    :members: select
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

## Selectors

```{eval-rst}
.. autoclass:: genesis.options.indices.Link
    :members: named, subtree

.. autoclass:: genesis.options.indices.Geom
    :members: at, named

.. autoclass:: genesis.options.indices.VGeom
    :members: at, named

.. autoclass:: genesis.options.indices.Vertex
    :members: at, in_box, closest_to
```

## Selections

```{eval-rst}
.. autoclass:: genesis.options.entities.LinkSelection
    :members: select, set, set_rho, set_friction, set_friction_torsional, set_friction_rolling, set_visualize_contact, set_surface, end

.. autoclass:: genesis.options.entities.GeomSelection
    :members: select, set, set_rho, set_friction, set_friction_torsional, set_friction_rolling, set_visualize_contact, end

.. autoclass:: genesis.options.entities.VGeomSelection
    :members: select, set, set_surface, end

.. autoclass:: genesis.options.entities.VertexSelection
    :members: select, set, set_is_fixed, end
```

## Options set on parts

```{eval-rst}
.. autoclass:: genesis.options.patches.Geom

.. autoclass:: genesis.options.patches.VGeom

.. autoclass:: genesis.options.patches.Vertex
```
