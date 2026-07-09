# Debugging and Interaction

Simulations are easier to build when you can see and poke at them. This section covers the tools for watching a Genesis World scene as it runs and for inspecting what it is doing while you develop: the interactive viewer window, the debug drawing and inspection facilities, and the plugin hooks that let you drive the viewer with your own code.

These are development-time tools, meant for a machine with a display. To capture images off-screen or produce photorealistic frames, whether headless or not, see {doc}`Rendering </user_guide/rendering/index>` instead; the two share the scene's `visualizer` but serve different purposes.

- {doc}`visualization` is the starting point: the interactive **viewer** window and the `gs` command-line tools that open a scene without writing a script.
- {doc}`interactive_debugging` covers the three complementary ways to understand a running scene, rich interactive inspection from a Python shell, debug drawing overlaid on the view, and the built-in state readouts.
- {doc}`viewer_plugin` shows how to extend the viewer itself: register keybindings, mouse interactions, and plugins that hook into the running simulation.

```{toctree}
:hidden:
:maxdepth: 1

visualization
interactive_debugging
viewer_plugin
```
