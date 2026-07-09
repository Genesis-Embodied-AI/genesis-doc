# Developers

This section is for building on Genesis World rather than only using it: extending the engine with your own resources, following the conventions the codebase holds itself to, and measuring where a simulation spends its time. Read it when you are writing a package on top of Genesis World, contributing upstream, or chasing a performance problem that the task-oriented guides do not address.

The extension points are deliberately narrow and documented; the conventions exist so that contributed code reads like the code around it. If you are adding a new **sensor** type specifically, that guide has moved next to the sensors it complements, see {doc}`Custom sensors </user_guide/sensing/custom_sensors/index>`.

- {doc}`extending_genesis` shows how to tie an external package's setup and teardown to `gs.init()` and `gs.destroy()`, so your extension's lifecycle tracks the engine's.
- {doc}`naming_and_variables` is the reference for the naming and indexing conventions used across the API and the source: how entities are identified, and how local and global indices relate.
- {doc}`profiling` covers measuring simulation performance, from coarse frame timing down to per-kernel detail.

```{toctree}
:hidden:
:maxdepth: 1

extending_genesis
naming_and_variables
profiling
```
