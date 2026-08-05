# Documentation Style Guide

This guide defines how we write documentation for Genesis World: what belongs on a page, how it is structured, and how it is marked up. Its companion, the [voice guide](VOICE.md), covers how the sentences themselves read. Both are prescriptive, describing the standard we are moving *toward* rather than how every existing page reads today, so bring any page you touch closer to them.

Our model is the class of technical documentation that developers actively enjoy using: Stripe, Django, and the Python standard library. What those share is a set of habits rather than a house style. They respect the reader's time, they are accurate to a fault, and they read as one voice across many authors.

---

## 1. Principles

Every rule below descends from five principles. When a rule doesn't fit a situation, reason from these instead.

1. **The reader is trying to get something done.** Documentation is a tool. Optimize for the reader who is stuck, skimming, and slightly frustrated, rather than for the one with time to read top to bottom.
2. **Accuracy is non-negotiable.** A single wrong argument name or stale output destroys trust in the whole page, so every code block must run and every claim must hold at the current version.
3. **Show, then tell.** A correct, runnable example answers more questions than three paragraphs, so lead with it.
4. **One voice.** A reader should not be able to tell that fifty people wrote these pages. Consistency in terminology, structure, and tone is worth more than any individual author's preference.
5. **Delete before you add.** Every sentence that does not help the reader act hides one that does.

---

## 2. Voice and tone

Sentence-level voice lives in the [voice guide](VOICE.md): who the subject of a sentence is, how much explanation a step gets, rhythm, the patterns we avoid, and the register. Read it before writing prose. This section covers only what is specific to documentation.

**An audible author, not a specification.** These pages are written by people who made choices, and the reader should be able to hear that. Say "we" for our conventions and defaults, keep the verbs active, and give a step its reason rather than only its name. Terseness is the failure mode to watch for: prose with every connective word squeezed out of it reads as choppy and hard to follow, and shortening it further makes it worse.

**Warmth and sloppiness are different things.** Enthusiasm about a real capability is welcome, and so is telling the reader plainly that something is easy when it is. What we cut is looser writing that costs the reader time:

- ❌ "…or simply use `'dumb'` if you are a black-and-white person." (a joke that leaves the option undocumented)
- ❌ "You can stop here if you want, but if you are patient enough, let's walk through it step by step together." (narrator escorting the reader)
- ❌ "…up to 10~80x (yes, this is a bit sci-fi) faster…" (an aside standing in for the methodology)
- ✅ "Simulation is parallelized across environments on the GPU, measured at 10–80× the throughput of prior GPU-accelerated simulators without trading away accuracy. See the [blog post](…) for methodology."

**Keep marketing out of the docs.** Superlatives ("world's fastest", "unprecedented", "effortless") belong on the landing page and in the README, not in reference or tutorial material. State capabilities as facts the reader can verify, and let benchmarks live behind a link.

- ✅ "Parallel simulation runs across environments on a single GPU. See [benchmarks](…) for measured throughput."
- ❌ "Genesis World is the world's fastest physics engine, with unprecedented speed."

**Be decisive about the recommended path.** Where we have a recommendation, name it and move the alternatives to a note: "Use X" beats "you might want to consider using X". Where there is genuinely no recommendation, say so and give the reader the criterion to decide by.

---

## 3. Page structure

Structure every page so a reader can find their answer without reading the whole thing. Assume they arrived from a search engine, landing in the middle.

**Lead with the answer, not the preamble.** The first paragraph states what the page covers and who it's for. The first code block should appear within a screen of the top. Do not open with history, motivation, or a tour of the section.

**Follow the inverted pyramid.** Most common case first, edge cases and configuration later, deep internals last. A reader should be able to stop reading as soon as their need is met.

**A task-oriented page (tutorial / how-to) follows this skeleton:**

```
# Title

One or two sentences: what you'll accomplish and the end result.

## Minimal working example      -> complete, runnable, copy-pasteable
## Walkthrough                  -> explain the example in the order it executes
## Variations / configuration   -> the next things a reader will want
## Notes and gotchas            -> admonitions for pitfalls
## See also                     -> links to related pages
```

**A reference page (a class or a sensor) follows this skeleton. Genesis's API Reference is generated from the source docstrings via autodoc, so the page stays thin and the docstring carries the parameters, returns, and behavior:**

```
# Name                    -> plain text, never wrapped in backticks (see below)

One sentence: what it is and when to use it, with a link to the How-to in the User Guide.

## Options                -> `.. autoclass::` the options class(es)
## <ObjectName>           -> `.. autoclass::` the built object, under its own heading
## See also
```

**Page titles are plain text, never backticked.** The H1 becomes the sidebar and cross-reference label, so
`# Scene` and `# gs.morphs.Box`, not `` # `Scene` ``. Backticked titles make the navigation read unevenly; drop
the code formatting even when the title names a class or a `gs.*` symbol. (Inline code inside the body keeps its
backticks as normal.)

**The API Reference mirrors the code.** Its top-level sections correspond to `genesis` subpackages, so the reference tree and import paths line up: the `engine` section mirrors `genesis.engine` (scene, simulator, entities, materials, solvers, couplers, sensors, states), and `visualization`, `recording`, `differentiation`, and `utilities` mirror `genesis.vis`, `genesis.recorders`, `genesis.grad`, and `genesis.utils`. When you add a component, place its page where the code lives, not by theme. Utilities autodoc individual symbols with explicit `.. autofunction::` / `.. autoclass::` rather than `.. automodule:: :members:`, because the global `undoc-members` setting would otherwise surface internal helpers.

**Options come first, the built object below, each under its own heading.** Most components pair an options class the user configures (`RigidOptions`, `IMU`, `Rasterizer`) with the built object the engine constructs from it (`RigidSolver`, `IMUSensor`, the rasterizer backend). On a page that documents both, keep the options class co-located with its object (do not split options into a separate section), and give each its own `##` heading so the reader sees a clear boundary between what to set and what to call:

- **`## Options`** holds the options autoclass(es). Name the heading for the specific class instead when the component takes several option bundles or the options are a minor part of it (e.g. `## Profiling options` on the Scene page, because a Scene is built from a large options bundle).
- **The built object gets its own heading** below Options, never an autoclass rendered flush under `## Options`. Use the object's class name (`## Simulator`, `## Viewer`) when the object is user-facing; use `## Implementation` when the runtime class is an internal backend fronted by the options as the public API (the renderers).
- **Catalog pages** that document several objects (the sensor pages) use one `##` heading per item, with the options autoclass then the object autoclass inside it; the autoclass signature boxes provide the separation, so no `## Options` sub-heading is needed there.

A configuration class that is itself the public API with no separate built object (morph, material, surface, texture) stands alone on its own page. An options class that configures a component with no page of its own (the base `Options`, and `ProfilingOptions`, since a scene has no separate profiler object) lives on the top-level `Options` page, which also indexes every co-located options class. Give an options class a page next to its component whenever one exists rather than leaving it on the hub (e.g. `KinematicOptions` sits with the KinematicSolver, `BaseCouplerOptions` on the Couplers page). This convention is explained for readers on the API Reference landing page.

**One page, one job.** If a page is teaching a concept, don't bury an API dump in it. If it's a reference, don't turn it into a tutorial. Link between them instead.

**Teach concepts; link the code.** A tutorial's job is to explain what a commented example file cannot: *why* each step exists, the mental model behind it, the conventions in play, and what goes wrong without it. Its job is *not* to narrate code line by line — the reader can read code. Concretely:

- **The runnable example file is the single source of truth for the complete code.** Link it prominently (for example, `examples/tutorials/hello_genesis.py`). Never paste a long script in full, and never paste it *twice* (a walkthrough followed by the whole script at the bottom is the pattern to kill).
- **Pull short excerpts into the page — one per teaching point.** An excerpt anchors an explanation; it does not reproduce the file. If an excerpt has nothing to teach, cut it.
- **Comments say _what_; prose says _why_.** Don't write prose that restates the next line of code ("`scene.build()` builds the scene"). Explain the reason, the trade-off, or the gotcha instead.
- A short, self-contained script (under ~15 lines) may be shown once in full as the minimal working example. Anything longer is excerpted, with the full file linked.

**User Guide vs API Reference: one home per fact.** The two top-level sections have different jobs, and no fact should live in both.

- **The API Reference is information-oriented and generated from the source docstrings** (`{eval-rst}` + `.. autoclass::`); its structure mirrors the code. A reference page carries a one-line "what and when," the autodoc directives, and a link to the How-to in the User Guide. It hosts no usage examples; those live in the guide, never duplicated here. The docstring *is* the reference.
- **The User Guide is task- and understanding-oriented:** the mental model, when to reach for a feature, how APIs combine, sensible values for a use case, and the gotchas, anchored by curated runnable examples.
- **One home per fact.** Every parameter's type, default, and meaning lives once, in the source docstring the reference autodocs. Neither the guide nor a reference page's hand-written prose restates the full parameter or return list; they link to it with `{py:class}` or `{doc}`. Naming the few parameters a task needs, in a teaching example, is fine; reproducing the reference table is not. A compact table that helps a reader *choose between* sensors is navigation, not a restatement, and is welcome.
- **Fix facts at the docstring.** Then the reference updates itself, and the guide keeps no version-fragile specifics that rot silently. If you find either side reproducing the reference, delete it and link.

**Keep paragraphs to three or four sentences.** A paragraph makes one point; when it starts making a second, start a new one. Material that is really a set of parallel items belongs in a list, a table, or numbered steps instead, though see the [voice guide](VOICE.md) on not turning a whole page into bullets.

---

## 4. Language and mechanics

**Active voice, present tense.** "Genesis World compiles the kernels on the first build," not "the kernels will be compiled." Describe what the software *does*, as a fact about the present.

**One idea per sentence, and no nesting.** A parenthetical inside a parenthetical, or a third subordinate clause, is a sentence that wants to be two. Splitting is not the same as chopping: join the halves with the word that names their relationship ("because", "so", "while") rather than leaving two stubs side by side. See the [voice guide](VOICE.md) on rhythm.

**Define a term once, then reuse it exactly.** Don't alternate between "degree of freedom", "dof", and "motor" for the same thing. Introduce the term, bold it on first use, then use it consistently. (See §6 for the terms we've standardized.)

**Prefer concrete over abstract.** "Returns a tensor of shape `(n_envs, 3)`" beats "returns the relevant data."

**Numbers, units, and symbols:**
- Always state units. "9.81 m/s²", "0.01 s", "0.5 m". A bare number is a bug report waiting to happen.
- Use the actual symbol or identifier in code font: `dt`, `max_range`, `n_envs`.
- Write "10–80×" with an en dash and a real multiplication sign, not "10~80x". (Better: avoid the range and cite a benchmark.)
- Arrows follow the context: `→` in prose and in a mapping like `(X, Y, Z) → (X, -Z, Y)`, and ASCII `->` inside code and code comments.

**Capitalization:**
- Sentence case for in-page content headings: "Reading sensor data", not "Reading Sensor Data". Navigation and section titles are the one exception (Title Case) — see §7.
- Code identifiers keep their real casing: `Scene`, `add_entity`, `gs.cpu`.

**Oxford comma. American spelling.** ("color", "behavior", "modeling").

**Spell out "and"; don't use the ampersand (`&`).** In headings, section titles, toctree captions, and running prose, write "and". The ampersand reads as shorthand, sorts and searches inconsistently, and clashes with the calm, spelled-out voice. (It is fine inside code, where `&` is an operator.)

- ✅ "Sensors and perception", "Theory and modeling"
- ❌ "Sensors & perception", "Theory & Modeling"

**Minimize em dashes; default to a colon, comma, or full stop.** Try a colon (to introduce or expand), a comma (for a light pause), or a new sentence first: one of those is almost always cleaner and more scannable. At most one em dash per paragraph, and only for a genuine aside. When a phrase introduces or defines what follows, the punctuation you want is a colon. (An en dash in a number range like "10–80×" is a different character and is fine.)

**Removing an em dash means restructuring the sentence, not swapping in a comma.** A dashed list dropped into commas turns into soup the reader has to parse twice: "Almost everything you put in a scene, a robot, a rigid object, a static mesh, comes from an asset file." Lead with the examples and follow with a colon, or move the list after the claim. ✅ "A robot, a rigid object, a static piece of scenery: almost everything you put in a scene comes from an asset file."

**Definition-style list items lead with a bold term and a colon.** Write `- **Simulation interface:** the user-facing API for …`, with the description as a normal clause after the colon. Do not separate the term from its description with an em dash, and do not use the "bold term, full stop, sentence" form for definition lists.

---

## 5. Code examples

Code is the most-read, most-copied, most-trusted part of any page. Hold it to the highest standard.

**Every example must be runnable and correct.** No pseudo-code passed off as real. If an example is a fragment, mark clearly what's omitted:

```python
# ... scene and robot setup as above ...
force = contact_sensor.read()
```

**Minimal first, complete later.** The opening example should contain the fewest lines that demonstrate the point — nothing decorative. Introduce configuration and options only once the core idea has landed.

**Prefer excerpts from the real example file over hand-typed snippets.** Code copied from a tested example in `examples/` stays correct; hand-typed code drifts out of sync with the API and rots silently. When you show an excerpt, copy it from the file you link as the source of truth (see §3).

**Follow the same conventions as the codebase itself:**
- Tag every fenced block with a language: ` ```python `, ` ```bash `. Never leave a block untagged, and never write ` ```Python ` with a capital P — the label is lowercase.
- Format Python as `black` would. **Do not space-align keyword arguments.** Align-by-column drifts out of alignment on the next edit and violates PEP 8.

  ✅
  ```python
  franka = scene.add_entity(
      gs.morphs.MJCF(
          file="xml/franka_emika_panda/panda.xml",
          pos=(0, 0, 0),
          euler=(0, 0, 90),
      ),
  )
  ```
  ❌
  ```python
  franka = scene.add_entity(
      gs.morphs.MJCF(
          file  = 'xml/franka_emika_panda/panda.xml',
          pos   = (0, 0, 0),
          euler = (0, 0, 90),
      ),
  )
  ```
- Use double quotes for strings, matching the codebase.

**Comment only what the code cannot say.** A comment explains *why*, or annotates a non-obvious value: units, conventions, tensor shapes. Never narrate what the line plainly says.

- ✅ `euler=(0, 0, 90),  # extrinsic x-y-z, degrees`
- ✅ `distances = sensor.read()  # shape ([n_envs,] n_probes)`
- ❌ `scene.build()  # build the scene`

**Show representative output when it aids understanding**, as a comment or a separate block — but only if it's real. Never invent output.

**Prefer `gs.gpu` / `gs.cpu` choices that match the tutorial's intent** and explain the choice once, rather than silently switching backends between examples.

---

## 6. Terminology and naming

Consistency here is what makes the docs read as one voice. These are settled; use them exactly.

**The product is "Genesis World."** Use the full name on first mention in a page and in any heading or introduction. After first mention, "Genesis World" may be shortened to "Genesis" within running prose where there's no ambiguity — but never invent other short forms. Do not write "Genesis World" in every sentence of a paragraph; it reads as keyword stuffing. Rewrite to use "it" or restructure.

- ✅ "Genesis World uses just-in-time compilation. The first build is therefore slower than subsequent runs, because it compiles GPU kernels on the fly."
- ❌ "Genesis World uses JIT. Genesis World compiles kernels on the fly, so Genesis World's first build is slow."

**Standardized terms** (define on first use, then reuse verbatim):

| Use this | Not this | Notes |
|---|---|---|
| degree of freedom / **dof** | motor, axis | Bold `dof` on first use; lowercase in prose, `dof` in code. |
| entity | object, body (when meaning a `gs.Entity`) | Reserve "rigid body" for the physics sense. |
| morph | shape, geometry (when meaning a `gs.morphs.*`) | |
| environment / **env** | world, instance (in the parallel-sim sense) | `n_envs` in code. |
| build (the scene) | compile, initialize | `scene.build()`. |
| step (the simulation) | tick, advance, update | `scene.step()`. |
| viewer | GUI, window | The interactive window. |
| renderer / camera sensor | — | Rendering happens through camera sensors. |

**Product and component names** are proper nouns: **Nyx** (renderer), **Quadrants** (compiler). Capitalize and link on first mention per page.

---

## 7. Formatting and MyST conventions

We build with Sphinx + MyST Markdown (`pydata_sphinx_theme`). Use the following, and only the following, so pages render consistently.

**Headings**
- One `#` H1 per page, matching the page's job. **No emoji in headings.** They break scannability, sorting, and search, and read as decoration. (Existing emoji headings should be removed as pages are touched.)
- **Content headings use sentence case; navigation titles use Title Case.** Every heading inside a page is sentence case. The exception is navigation: the two top-level section landing titles (`User Guide`, `API Reference`) and the sidebar `:caption:` labels in a `{toctree}` (`Getting Started`, `Robot Control`, …) are Title Case, because they read as proper section names rather than page content.
- **Don't start a page or section title with an article.** Name the subject directly: `Sensor pipeline`, not "The sensor pipeline"; `Support field`, not "The support field". A leading "The"/"A"/"An" adds nothing to a title, sorts and scans worse, and pushes the real word right. (An article mid-title, or in a content heading where it reads naturally, is fine.)
- **Spell out "and" in headings and toctree captions — never `&`** (see §4).
- Don't skip levels (no H2 → H4). `myst_heading_anchors` generates anchors down to H4; keep meaningful headings within that depth.

**Cross-references** — prefer Sphinx roles over bare Markdown links for anything inside the docs, so links survive file moves and are checked at build time:
- Another doc page: `` {doc}`/api_reference/engine/scene` `` (leading `/` = path from `source/`).
- A Python object: `` {py:class}`genesis.engine.scene.Scene` `` / `` {py:meth}`genesis.engine.scene.Scene.build` `` where autodoc targets exist.
- **Link the first mention of each API symbol per guide page.** When prose names a public class (`gs.materials.MPM.Muscle`, `gs.options.SimOptions`, `gs.morphs.Box`), link it the first time it appears on the page and leave later repeats as plain inline code. Use the full public name as the display text over the real autodoc target: `` {py:class}`gs.materials.MPM.Muscle <genesis.engine.materials.MPM.muscle.Muscle>` `` (the `gs.*` alias is not itself a resolvable target, so the FQN goes in the angle brackets). Do not link inside code blocks, and do not link backend constants or enum values (`gs.gpu`, `gs.tc_float`, `gs.constraint_solver.Newton`) that are documented as prose rather than autodoc classes.
- Use a plain Markdown link `[text](https://…)` only for **external** URLs.
- Never hard-code `https://…/genesis-doc/...` links to our own pages or assets — they break across versions and forks.

**Admonitions** — use `colon_fence` syntax and reserve each type for its meaning:
```markdown
:::{note}
Supplementary context the reader can skip without breaking anything.
:::

:::{warning}
Something that will cause data loss, crashes, or wrong results if ignored.
:::

:::{tip}
A shortcut or best practice.
:::
```
Don't overuse them — if half the page is boxed, nothing stands out. One idea per admonition; give it a purpose, not a decoration.

**Media (images and video)**
- Store assets under `source/_static/` and reference them with **relative** paths. Do not link to raw GitHub URLs or personal forks.
- Every image needs alt text describing what it shows.
- Use the `{figure}` directive for captioned images and `sphinxcontrib.video` (or a bare `<video>` with `controls`, `width="100%"`) for video. Keep video usage consistent across pages.

**Tables** are the right tool for comparing options, listing return types/shapes, or mapping names to meanings (see the sensor overview table). Prefer a table over a bulleted list when every item shares the same handful of attributes.

---

## 8. Conventions the docs must always honor

These are project-wide facts. State them the same way everywhere, and never contradict them.

**Tensor shapes.** Document every returned tensor's shape, using the batched-optional notation the codebase already uses: the leading batch dim is shown in brackets.
```
distances  # shape ([n_envs,] n_probes)
points     # shape ([n_envs,] n_probes, 3)
```
The `[n_envs,]` bracket means "present when the scene is built with multiple environments, absent otherwise." Use this notation consistently; don't reinvent it per page.

**Coordinate system.** Right-handed, **Z-up**. Gravity is `-Z`, default magnitude 9.81 m/s². State this rather than assuming it.

**Quaternions.** `(w, x, y, z)` — scalar-first (Hamilton). Say so wherever a quaternion appears in an example.

**Rotations / Euler angles.** Extrinsic x-y-z, in degrees, following SciPy's convention. Annotate in code comments where used.

**Units.** SI throughout: meters, seconds, radians (except Euler inputs noted above), kilograms. Always label them.

---

## 9. Pre-merge checklist

Before opening a docs PR, confirm the following, then run the [voice guide](VOICE.md) checklist over the prose:

- [ ] Every code block runs against the current release, and I've run it.
- [ ] Every fenced block is tagged with a lowercase language (`python`, `bash`, …).
- [ ] No space-aligned keyword arguments; Python is `black`-clean.
- [ ] The page leads with what it's for and a runnable example within one screen.
- [ ] No parameter, type, default, or return fact is re-typed from the API Reference (the source docstring); the guide and reference-page prose link to it instead.
- [ ] In-page headings are sentence case with no emoji; section/navigation titles (top-level section pages, toctree captions) are Title Case.
- [ ] No page or section title begins with an article ("The", "A", "An").
- [ ] Terminology matches §6, and the product is "Genesis World" without keyword stuffing.
- [ ] No marketing superlatives; every capability claim is one the reader can verify.
- [ ] Headings, titles, and captions spell out "and", with no ampersands (`&`).
- [ ] Internal links use `{doc}` / `{py:*}` roles; no hard-coded genesis-doc URLs.
- [ ] Tensor shapes, coordinate frame, quaternion order, and units are stated where relevant.
- [ ] Alt text on every image; assets live under `_static/` and are referenced relatively.
- [ ] I read the page top to bottom and deleted every sentence that didn't help the reader act.
