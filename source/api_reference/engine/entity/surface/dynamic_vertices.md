# DynamicVertices

The vertices of a visual geom that switch at runtime between variants, or that you write per environment with `vgeom.set_vverts(...)` after the build. Only the visual geoms of rigid and kinematic entities admit them, through `gs.options.VGeom.dynamic_vertices` or the `dynamic_vertices` of the entity spec.

```{eval-rst}
.. autoclass:: genesis.options.surfaces.DynamicVertices
```
