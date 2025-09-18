# 💡 Tips

## Running Performance Benchmarks

* One may need to temporarily disable caching when doing profiling and/or benchmarking. The most straightforward solution would be to completely wip out the persistent local cache folder. This is not recommended because its effect will persist beyond the scope of your experiment, slowing down start up of all your future simulations until your cache is finally recovered. One should rather redirect Genesis (and Taichi) to some alternative temporary cache folder. This can be done editing any Python code, by setting a few environment variables:
```bash
XDG_CACHE_HOME="$(mktemp -d)" GS_CACHE_FILE_PATH="$XDG_CACHE_HOME/genesis" TI_OFFLINE_CACHE_FILE_PATH="$XDG_CACHE_HOME/taichi" python [...]
```
Note that specifying `XDG_CACHE_HOME` is sufficient on Linux, but not on Windows OS and Mac OS.

# 🖥️ Command Line Tools

We provided some command line tools that you can execute in terminal once Genesis is installed. These include:

- `gs view *.*`: Visualize a given asset (mesh/URDF/MJCF) (can be useful if you want to quickly check if your asset can be loaded and visualized correctly)
- `gs animate 'path/*.png'`: Combine all images that matches the given pattern into a video.
