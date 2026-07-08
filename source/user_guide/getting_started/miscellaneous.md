# Tips and tools

A few things that don't belong to any one tutorial: how to run clean benchmarks despite Genesis World's caching, and the command-line tools installed alongside the package.

## Benchmarking with a disposable cache

Genesis World compiles GPU kernels just-in-time and caches the results to a persistent local folder, so repeated runs of the same scene start quickly. Quadrants, the compiler, keeps its own cache in the same way. This is what you want for day-to-day work, but it distorts profiling and benchmarking: the first run pays the compilation cost and later runs read from the warm cache.

Do not wipe the persistent cache to get around this. Its effect outlives your experiment, and every future simulation is slow until the cache rebuilds. Instead, redirect both caches to a throwaway directory for the duration of a single run, by setting a few environment variables:

```bash
XDG_CACHE_HOME="$(mktemp -d)" \
GS_CACHE_FILE_PATH="$XDG_CACHE_HOME/genesis" \
QD_OFFLINE_CACHE_FILE_PATH="$XDG_CACHE_HOME/quadrants" \
python your_script.py
```

- `GS_CACHE_FILE_PATH` — Genesis World's cache directory.
- `QD_OFFLINE_CACHE_FILE_PATH` — the Quadrants compiler cache directory.
- `XDG_CACHE_HOME` — the base cache directory, honored on Linux only.

On Linux, `XDG_CACHE_HOME` alone is enough to relocate the Genesis World cache. On Windows and macOS it is ignored, so set `GS_CACHE_FILE_PATH` and `QD_OFFLINE_CACHE_FILE_PATH` explicitly as shown above.

## Command-line tools

Installing Genesis World adds a `gs` command with a few subcommands. Run `gs` with no arguments to list them.

**`gs launch [asset]`** opens an asset in the interactive {doc}`viewer <visualization>`. It accepts a Mesh, URDF, MJCF, or USD file; for a USD stage, every rigid entity in the stage is loaded. The viewer's overlay exposes per-joint sliders and play, pause, step, and reset controls, and it starts paused so you can inspect and pose the asset first. With no file, it opens an empty scene to which you can add entities live. Useful flags: `-c` visualize collision geometry, `-r` slowly rotate the asset, `-s SCALE` scale it, and `-l` show link frames.

```bash
gs launch xml/franka_emika_panda/panda.xml
```

**`gs play [asset]`** opens the same interactive viewer but runs the physics simulation, so joints and bodies respond under gravity and contact. With no file, it loads a demo scene (a Franka arm on a ground plane). It accepts `-c` and `-s SCALE`.

```bash
gs play xml/franka_emika_panda/panda.xml
```

**`gs animate 'pattern'`** combines every image matching a glob pattern into a video written to `video.mp4`. Pass `--fps` to set the frame rate (default 30).

```bash
gs animate 'frames/*.png' --fps 60
```

:::{note}
`gs view` still works as a deprecated alias of `gs launch` and prints a deprecation warning. Use `gs launch` instead.
:::
