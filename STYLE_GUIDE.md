# Documentation Style Guide

This guide defines how we write documentation for Genesis World: how the prose should read, what belongs on a page, how to structure it, and how to mark it up. It is prescriptive, describing the standard we are moving *toward* rather than how every existing page reads today, so bring any page you touch closer to it.

Our model is the class of technical documentation that developers actively enjoy using: Stripe, Django, and the Python standard library. What those share is a set of habits rather than a house style. They respect the reader's time, they are accurate to a fault, and they read as one voice across many authors.

---

## 1. Principles

Every rule below descends from five principles. When a rule doesn't fit a situation, reason from these instead.

1. **The reader is trying to get something done.** Documentation is a tool. Optimize for the reader who is stuck, skimming, and slightly frustrated, rather than for the one with time to read top to bottom.
2. **Run every code block and check every claim against the current version.** A single wrong argument name or stale output destroys trust in the whole page.
3. **Lead with a correct, runnable example.** It answers more questions than three paragraphs of description.
4. **One voice.** A reader should not be able to tell that fifty people wrote these pages. Consistency in terminology, structure, and tone is worth more than any individual author's preference.
5. **Delete sentences that fail to help the reader.** Keep the explanations that earn their lines: see §2 on explaining generously.

---

## 2. Voice and tone

Write the way a senior engineer explains something to a capable colleague who is in a hurry. That person wants the reason along with the instruction, and they will forgive you a longer sentence if it saves them a question. Being short comes from knowing what you want to say, never from cutting sentences in half.

The failure mode these pages fall into is compression. A page that has had every connective word squeezed out of it reads as choppy and authorless, and the reader ends up reassembling the logic the writer threw away. Readers tell us so. Length is not the enemy: a paragraph that explains why a step exists earns its lines, and a page of clipped declaratives does not become clearer by being shorter.

**Warmth and sloppiness are different things.** Enthusiasm about a real capability is welcome, and so is telling the reader plainly that something is easy when it is. What we cut is looser writing that costs the reader time:

- ❌ "…or simply use `'dumb'` if you are a black-and-white person." (a joke that leaves the option undocumented)
- ❌ "You can stop here if you want, but if you are patient enough, let's walk through it step by step together." (narrator escorting the reader)
- ❌ "…up to 10~80x (yes, this is a bit sci-fi) faster…" (an aside standing in for the methodology)
- ✅ "Genesis World parallelizes simulation across environments on the GPU, measured at 10–80× the throughput of prior GPU-accelerated simulators without trading away accuracy. See the [blog post](…) for methodology."

**Keep marketing out of the docs.** Superlatives ("world's fastest", "unprecedented", "effortless") belong on the landing page and in the README, not in reference or tutorial material. State capabilities as facts the reader can verify, and let benchmarks live behind a link.

- ✅ "Parallel simulation runs across environments on a single GPU. See [benchmarks](…) for measured throughput."
- ❌ "Genesis World is the world's fastest physics engine, with unprecedented speed."

**Be decisive about the recommended path.** Where we have a recommendation, name it and move the alternatives to a note: "Use X" beats "you might want to consider using X". Where there is genuinely no recommendation, say so and give the reader the criterion to decide by.

### Who speaks

Choosing the subject of a sentence deliberately is most of what makes these pages sound like one person.
Three forms carry almost all of them.

- **The bare imperative** for anything the reader does. This is the default, and it is shorter and more direct
  than naming the reader: ✅ "Configure the solver through `RigidOptions`." ❌ "You configure the solver
  through `RigidOptions`."
- **Genesis World** for what the software does: "Genesis World compiles the kernels on the first build."
- **We** for decisions and conventions the project made: "We follow SciPy's extrinsic x-y-z convention for
  Euler angles", "We call one copy of the scene an environment."

Lead with the verb. A sentence that opens "You configure", "You create", "You can pin", or "You must
reconstruct" is an instruction wearing a subject it does not need, and dropping the pronoun leaves it clearer:
"Configure", "Create", "Pin", "Reconstruct". The same goes for "you can" and "you must", which add permission
or obligation to a plain instruction. Reserve "you" for the cases where the reader genuinely has to be the
subject: a possessive ("your scene", "the GPU your machine has"), a contrast between what you do and what the
engine does in response, or a subordinate clause where an imperative cannot go ("anything you omit uses its
defaults").

Where a sentence states a fact rather than giving an instruction, an imperative would misrepresent it, so give
the fact a real actor instead of the reader. ✅ "Genesis World constructs the solvers for you." ❌ "You rarely
construct a solver directly."

"We" is how the reader hears that a person chose this, so use it for our conventions, our defaults, our
recommendations, and the things we support. What it never does is escort the reader: "let's walk through it
together", "now we will look at the viewer", "if you are patient enough, let's continue". The reader is
reading, not accompanying you.

Keep the verbs active. "Parallelism is turned on when the scene is built" has nobody in it, while "turn
parallelism on at build time" is both shorter and an instruction. When you catch yourself writing "is handled",
"is performed", or "can be configured", find the actor and put them in front, or recast the sentence as an
imperative. This holds for headings too: prefer "Composing a scene from options" over "A scene is assembled
from options".

### Explain, then instruct

Every non-obvious step gets its reason in the same breath as the instruction, and the reason goes first when
it is what makes the instruction make sense.

- ✅ "Genesis World compiles GPU kernels just-in-time, so `scene.build()` is an explicit step: it allocates
  device memory, creates the simulation data fields, and triggers that compilation."
- ❌ "Call `scene.build()`. It allocates memory and compiles kernels."

Say what goes wrong without the step, when something does. Say what the value means in the reader's terms,
not the solver's. When a default exists, say why it is the default. A reader who understands why `build()` is
required will remember it forever; a reader who was told to call it will forget by the next page.

Cut repetition rather than length. Explaining the same fact twice on one page is what to remove; the
explanation itself stays.

### Ornament is not warmth

Warming up cold prose tempts you into decoration, which reads as written-by-machine just as badly as the
clipped version did. Both of the following say the same thing; the second one wastes the reader's attention on
a flourish and then editorializes about stiff gains.

- ✅ "`set_dofs_force_range` caps the controller's output."
- ❌ "`set_dofs_force_range` then caps what the controller is allowed to ask for, which is the limit that
  keeps a stiff gain from launching the arm."

If a shorter structure carries the same fact, use the shorter structure. Warmth comes from an audible author
and a reason attached to an instruction, never from ornament. Specifically:

- **Personification.** "The dynamics never get a say", "ask for a GPU backend", "this tutorial gives the arm
  something to hold onto". Software and options do not want, allow, or offer. ✅ "`set_*` writes the robot
  state directly, without consulting the dynamics."
- **Abstract restatement.** "Parallelism belongs to the scene rather than to the entities in it" says less
  than the concrete instruction it replaced. ✅ "You choose the number of copies when you build the scene."
- **Aphoristic contrast.** "Two families of methods read alike and behave nothing alike." ✅ "`set_*` and
  `control_*` look similar and do different things."
- **Rhetorical framing before the fact.** "Training a policy takes millions of steps, and stepping one robot
  at a time is no way to collect them." ✅ "Training a policy takes millions of interaction steps, so you
  want many environments running at once."
- **Editing by synonym.** Changing "skipping the PD controller" to "bypassing the PD controller" alters
  nothing a reader experiences. If an edit does not change what a sentence says or how it reads, drop it.
- **Inventing a claim to sound helpful.** "Confusing them is the most common way a first control loop goes
  wrong", "a model tuned for another simulator rarely feels right in this one". Neither is something we
  measured. Write the fact you can defend: "gains from another model rarely transfer unchanged."
- **Wrapping an instruction in a metaphor.** "A sentence that fails to help the reader act hides one that
  does, so delete it" makes the reader decode an image to find the instruction. Lead with the imperative and
  stop: ✅ "Delete sentences that fail to help the reader."
- **Vague cost metaphors.** "You pay for that", "it does not come for free", "this is not cheap". Pay what,
  in what units, and compared to what? Name the cost: ✅ "IPC costs more per step than the legacy coupler."
- **Stating what the reader already knows.** "Shape primitives need no file at all" tells someone who just
  read the word "primitive" nothing. ✅ "The shape primitives are `Plane`, `Box`, …". The same goes for a
  sentence explaining that a default is the value used when you pass nothing, or that a getter returns the
  thing it is named after. If a reader could infer it from the name or the previous sentence, cut it.

### Rhythm

Telegraph style is the most common way these pages go wrong: every sentence five words long, starting with a
verb, sitting on its own line. Write a paragraph that makes one point and then stops.

Vary the sentence length and let the clauses connect. A "because" or a "so" in the middle of a sentence is
usually clearer than the same content split across a full stop, because it names the relationship instead of
leaving the reader to infer it. Fragments belong in a list, a table, or a code comment, and read as curt in
prose.

- ✅ "The first build is slow because Genesis World compiles GPU kernels on the fly. Later runs load them
  from cache and start immediately."
- ❌ "The first build is slow. Kernels compile on the fly. Later runs reuse the cache. Only the first one
  is slow."

Bold-lead bullets are a real format, and a page made entirely of them is a slide deck. Use them where the lead
phrase is the index the reader scans for, as in the lists on this page, and write paragraphs everywhere else.
When a page runs three bulleted sections back to back, at least one of them wanted to be prose.

### Anti-patterns

The habit, then the replacement.

- **Preamble.** A page that opens with a tour of itself, or a section that restates its own heading. Open on
  the fact the reader came for.
- **Fragments as statements.** "Fully differentiable." becomes "Gradients flow through the physics."
- **Restating the reason.** Give it once, in the same breath as the claim: "Prefer `expand` over `repeat`,
  because it returns a view."
- **Oblique verdicts.** "Comments earn their place", "X belongs here", "X is the right tool". Use the
  imperative: "Comment only what the code cannot say."
- **Trailing purpose clauses that pitch.** "…which is what makes it the tool for modeling a suction gripper."
  State the capability and stop: "…so a suction gripper can pick an object up and release it."
- **Headings and bullet leads that say nothing.** A short punchy label is good ("One scene, one state",
  "Differentiable by design"); a label that only sets a mood is not ("Built for the future", or "Unified, not
  bolted together", which defines by negation before it defines anything).
- **Rhetorical setup.** "Here's the thing", "The catch?", "But wait", "It turns out that". Start at the
  content.
- **Definition by contrast.** "A hybrid entity is not a single solver's object" makes the reader hold a wrong
  model in their head before you correct it. Say what the thing is: "A hybrid entity pairs two entities that
  share one scene and one timestep."
- **Uniform hedging.** "You might want to consider possibly using X" is three hedges around one
  recommendation. Be decisive where we have a recommendation, and say so plainly where we do not: "Use the
  Newton solver", or "either value works, so pick by which failure you would rather debug".
- **Emphatic capitals and bold slogans.** Replace the emphasis with a better fact, and reserve bold for the
  term being defined rather than for a whole clause. An exclamation mark is fine where you mean it; what does
  not work is one standing in for the evidence.
- **Narrating history.** "This option was previously called `n_worlds`", "we have now added USD support". A
  page describes what is true at the current version, and version history lives in the changelog.
- **Em dashes.** Default to a colon, a comma, or a full stop, and keep at most one per paragraph for a
  genuine aside. When a phrase introduces or defines what follows, a colon is the punctuation you want.
- **False concession.** "While the rasterizer has limitations, it remains a solid choice." State the actual
  tradeoff: "The rasterizer cannot do refraction, and it renders a frame in milliseconds instead of seconds."
- **Rhetorical question openers.** "What if you could simulate thousands of robots at once?" Make the claim.
- **Copula dressing.** "serves as", "features", "boasts", "offers", "provides" where "is" or "has" would do.
  ✅ "`Scene` has a `simulator` and a `visualizer`." ❌ "`Scene` serves as a container that features both a
  simulator and a visualizer."
- **Vague attribution.** "Experts recommend", "it is generally considered". Either we recommend it, and say
  so, or a source does, and you cite it.
- **Superficial -ing clauses.** "…, highlighting the flexibility of the solver", "…, reflecting the unified
  design". These read as analysis and carry no fact. Delete, or replace with the fact.
- **Hyphenated adjective pileups.** "a high-quality, well-tested, production-ready renderer". Keep one
  modifier, and pick the one you can defend.
- **Bullet lists of bare noun phrases.** A list whose items have no verbs wants to be prose. Parameter
  tables and format lists are the exception.
- **Synonym cycling.** Rotating "environment", "world", and "instance" for one concept makes the reader
  wonder whether you meant three things. Pick the term from §6 and repeat it.

### State what is

Drop "not X", "unlike Y", and "does not …" unless the negation is the literal specification, or the reader
genuinely arrives believing the opposite. If a property is not mentioned, it does not exist, and defending
against an objection nobody raised only plants it.

- ✅ "`scene.add_camera()` returns a camera you drive yourself: call `render()` for pixels and
  `start_recording()` for video."
- ❌ "`scene.add_camera()` does not return a sensor. Unlike a camera sensor, you do not read it with
  `read()`; instead you drive it yourself."

The exception is a real choice between two things we ship, where the contrast *is* the information a reader
came for. A comparison table earns its negations, and so does one clause separating the camera sensor from the
visualization camera. Three paragraphs of it does not.

### Words and phrases to avoid

Nobody says these out loud.

- "reach for", "dive into", "delve", "unpack" (except a tuple), "leverage" as a verb, "surface" as a verb,
  "spin up", "seamlessly", "effortlessly", "simply", and "just" as a minimizer.
- "it's worth noting", "it's important to understand", "keep in mind", "note that" as a sentence opener,
  "that said", "at the end of the day", "the key insight here". Conjugating around one of these does not
  count. If the fact matters, state it; if it does not, delete it.
- "robust", "seamless", "crucial", "comprehensive", "powerful", "elegant" as unearned adjectives. Name the
  property instead: "stable under large deformation", "intersection-free", "covers every solver".
- "massive", "blazingly fast", "game-changer", and "10x" as a figure of speech. A measured number with a link
  to the benchmark is welcome, and a superlative is not.
- Filler that a shorter word replaces exactly: "in order to" is "to", "due to the fact that" is "because",
  "a variety of" is usually a number, and "Moreover" / "Furthermore" / "Additionally" at the head of a
  sentence is either "and" or a sign the paragraph needs reordering.
- Stacked hedges: "could potentially", "may sometimes", "can often help to". Each one cancels the last, so
  keep at most one.

"Robust" deserves its own note, because numerical robustness is a real and useful property, so say it
precisely. "The elliptic friction cone is more robust" is marketing; "the elliptic friction cone keeps resting
objects from creeping" is the fact a reader can act on.

### Register

Somebody reads these pages in five years with no idea who wrote them or what the thread was, so they carry no
in-jokes, no winks at the reader, and no emoji in prose or headings.

That is not a vow of blandness, and flat prose is the more common problem here. Being enthusiastic about
something we built is welcome as long as the enthusiasm is attached to a fact: differentiable tactile sensors,
gradients that flow through contact, thousands of environments on one GPU. Write those the way you would say
them to a colleague who would find them interesting, because they are interesting. Saying that something is
easy is fine when it is easy, and "that is all it takes" is a real sentence. What we avoid is hype with
nothing under it: a superlative the reader cannot verify ("world's fastest"), an adjective standing in for a
property ("robust", "powerful"), or a claim whose only evidence is an exclamation mark.

Passages that speak to the community rather than to a task keep their warmth in full. The mission statement,
the invitation to contribute, and the request to report a page that disagrees with the code are the project
talking to a person, so "we would love to hear from you" belongs there. Leave that register alone when you
edit those passages; everything above is about the pages that explain how something works.

### Worked example

The opening of the IPC coupler page, before:

> The IPC coupler resolves contact with Incremental Potential Contact, a barrier-based model built on the
> [libuipc](https://github.com/spiriMirror/libuipc) library. Where the legacy coupler applies impulses and
> the SAP coupler solves a semi-analytic contact problem, IPC advances every coupled body through a single
> smooth potential whose barrier term grows without bound as surfaces approach. The result is contact that
> stays intersection-free and stable even under large deformation, which is what makes it the right choice
> for cloth and heavily deforming soft bodies.
>
> Reach for IPC when accuracy and robustness matter more than speed: cloth with self-collision, FEM solids
> pressed hard against each other, or a gripper closing on a deformable object.

After:

> The IPC coupler resolves contact with Incremental Potential Contact, a barrier-based model built on the
> [libuipc](https://github.com/spiriMirror/libuipc) library. It advances every coupled body through a single
> smooth potential whose barrier term grows without bound as two surfaces approach, so contact under IPC
> stays intersection-free however hard you press two bodies together. IPC costs more per step than the legacy
> coupler, so we keep legacy as the default and let you select IPC per scene.
>
> Use it for cloth with self-collision, for FEM solids pressed hard against each other, and for a gripper
> closing on a deformable object. For mixed continuum scenes (MPM, SPH, PBD) or coarse rigid contact, stay on
> the legacy coupler; see the couplers overview for the full comparison.

The mechanism is stated once and made to carry its own consequence ("so contact under IPC stays…")
instead of being circled a second time. Defining IPC by what the other two couplers do is gone, and with it
the need to hold three models in your head to learn one. "Robustness" gives way to the property it stood in
for, the cost sits next to the benefit where a reader deciding between couplers needs it, and "we keep legacy as
the default" tells them that was our call rather than an accident.

### Rewrite rather than patch

Fixing a flagged phrase in place works when a page is basically sound. When a paragraph trips several of the
patterns above at once, and especially when its sentences all run to the same length, patching it produces
prose that reads as edited by machine, because that is what it is. Rewrite the paragraph from the fact it is
trying to convey. The same applies to your own edits: if a change does not alter what a sentence says or how it
reads, it is churn, so leave the original alone.

For a fuller catalog of the machine-writing patterns this guide draws on, see
[avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing).

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

**Teach concepts; link the code.** A tutorial's job is to explain what a commented example file cannot: *why* each step exists, the mental model behind it, the conventions in play, and what goes wrong without it. Its job is *not* to narrate code line by line, because the reader can read code. Concretely:

- **The runnable example file is the single source of truth for the complete code.** Link it prominently (for example, `examples/tutorials/hello_genesis.py`). Never paste a long script in full, and never paste it *twice* (a walkthrough followed by the whole script at the bottom is the pattern to kill).
- **Pull short excerpts into the page, one per teaching point.** An excerpt anchors an explanation; it does not reproduce the file. If an excerpt has nothing to teach, cut it.
- **Comments say _what_; prose says _why_.** Don't write prose that restates the next line of code ("`scene.build()` builds the scene"). Explain the reason, the trade-off, or the gotcha instead.
- A short, self-contained script (under ~15 lines) may be shown once in full as the minimal working example. Anything longer is excerpted, with the full file linked.

**User Guide vs API Reference: one home per fact.** The two top-level sections have different jobs, and no fact should live in both.

- **The API Reference is information-oriented and generated from the source docstrings** (`{eval-rst}` + `.. autoclass::`); its structure mirrors the code. A reference page carries a one-line "what and when," the autodoc directives, and a link to the How-to in the User Guide. It hosts no usage examples; those live in the guide, never duplicated here. The docstring *is* the reference.
- **The User Guide is task- and understanding-oriented:** the mental model, when to reach for a feature, how APIs combine, sensible values for a use case, and the gotchas, anchored by curated runnable examples.
- **One home per fact.** Every parameter's type, default, and meaning lives once, in the source docstring the reference autodocs. Neither the guide nor a reference page's hand-written prose restates the full parameter or return list; they link to it with `{py:class}` or `{doc}`. Naming the few parameters a task needs, in a teaching example, is fine; reproducing the reference table is not. A compact table that helps a reader *choose between* sensors is navigation, not a restatement, and is welcome.
- **Fix facts at the docstring.** Then the reference updates itself, and the guide keeps no version-fragile specifics that rot silently. If you find either side reproducing the reference, delete it and link.

**Keep paragraphs to three or four sentences.** A paragraph makes one point; when it starts making a second, start a new one. Material that is really a set of parallel items belongs in a list, a table, or numbered steps instead, though see §2 on not turning a whole page into bullets.

---

## 4. Language and mechanics

**Active voice, present tense.** "Genesis World compiles the kernels on the first build," not "the kernels will be compiled." Describe what the software *does*, as a fact about the present.

**One idea per sentence, and no nesting.** A parenthetical inside a parenthetical, or a third subordinate clause, is a sentence that wants to be two. Splitting is not the same as chopping: join the halves with the word that names their relationship ("because", "so", "while") rather than leaving two stubs side by side. See §2 on rhythm.

**Define a term once, then reuse it exactly.** Don't alternate between "degree of freedom", "dof", and "motor" for the same thing. Introduce the term, bold it on first use, then use it consistently. (See §6 for the terms we've standardized.)

**Prefer concrete over abstract.** "Returns a tensor of shape `(n_envs, 3)`" beats "returns the relevant data."

**Numbers, units, and symbols:**
- Always state units. "9.81 m/s²", "0.01 s", "0.5 m". A bare number is a bug report waiting to happen.
- Use the actual symbol or identifier in code font: `dt`, `max_range`, `n_envs`.
- Write "10–80×" with an en dash and a real multiplication sign, not "10~80x". (Better: avoid the range and cite a benchmark.)
- Arrows follow the context: `→` in prose and in a mapping like `(X, Y, Z) → (X, -Z, Y)`, and ASCII `->` inside code and code comments.

**Capitalization:**
- Sentence case for in-page content headings: "Reading sensor data", not "Reading Sensor Data". Navigation and section titles are the one exception (Title Case); see §7.
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

**Minimal first, complete later.** The opening example should contain the fewest lines that demonstrate the point, with nothing decorative. Introduce configuration and options only once the core idea has landed.

**Prefer excerpts from the real example file over hand-typed snippets.** Code copied from a tested example in `examples/` stays correct; hand-typed code drifts out of sync with the API and rots silently. When you show an excerpt, copy it from the file you link as the source of truth (see §3).

**Follow the same conventions as the codebase itself:**
- Tag every fenced block with a language: ` ```python `, ` ```bash `. Never leave a block untagged, and never write ` ```Python ` with a capital P: the label is lowercase.
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

**Show representative output when it aids understanding**, as a comment or a separate block, but only if it's real. Never invent output.

**Prefer `gs.gpu` / `gs.cpu` choices that match the tutorial's intent** and explain the choice once, rather than silently switching backends between examples.

---

## 6. Terminology and naming

Consistency here is what makes the docs read as one voice. These are settled; use them exactly.

**The product is "Genesis World."** Use the full name on first mention in a page and in any heading or introduction. After first mention, "Genesis World" may be shortened to "Genesis" within running prose where there's no ambiguity, but never invent other short forms. Do not write "Genesis World" in every sentence of a paragraph; it reads as keyword stuffing. Rewrite to use "it" or restructure.

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
- **Spell out "and" in headings and toctree captions, never `&`** (see §4).
- Don't skip levels (no H2 → H4). `myst_heading_anchors` generates anchors down to H4; keep meaningful headings within that depth.

**Cross-references:** prefer Sphinx roles over bare Markdown links for anything inside the docs, so links survive file moves and Sphinx checks them at build time:
- Another doc page: `` {doc}`/api_reference/engine/scene` `` (leading `/` = path from `source/`).
- A Python object: `` {py:class}`genesis.engine.scene.Scene` `` / `` {py:meth}`genesis.engine.scene.Scene.build` `` where autodoc targets exist.
- **Link the first mention of each API symbol per guide page.** When prose names a public class (`gs.materials.MPM.Muscle`, `gs.options.SimOptions`, `gs.morphs.Box`), link it the first time it appears on the page and leave later repeats as plain inline code. Use the full public name as the display text over the real autodoc target: `` {py:class}`gs.materials.MPM.Muscle <genesis.engine.materials.MPM.muscle.Muscle>` `` (the `gs.*` alias is not itself a resolvable target, so the FQN goes in the angle brackets). Do not link inside code blocks, and do not link backend constants or enum values (`gs.gpu`, `gs.tc_float`, `gs.constraint_solver.Newton`) that are documented as prose rather than autodoc classes.
- Use a plain Markdown link `[text](https://…)` only for **external** URLs.
- Never hard-code `https://…/genesis-doc/...` links to our own pages or assets, because they break across versions and forks.

**Admonitions:** use `colon_fence` syntax and reserve each type for its meaning:
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
Don't overuse them: if half the page is boxed, nothing stands out. One idea per admonition; give it a purpose, not a decoration.

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

**Quaternions.** `(w, x, y, z)`, scalar-first (Hamilton). Say so wherever a quaternion appears in an example.

**Rotations / Euler angles.** Extrinsic x-y-z, in degrees, following SciPy's convention. Annotate in code comments where used.

**Units.** SI throughout: meters, seconds, radians (except Euler inputs noted above), kilograms. Always label them.

---

## 9. Pre-merge checklist

Before opening a docs PR, confirm:

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
- [ ] Instructions lead with the verb; no sentence opens "You configure" / "You can" / "You must".
- [ ] Every sentence has a subject that acts: an imperative, Genesis World, or we. No orphaned passives.
- [ ] "We" appears where the page states one of our conventions, defaults, or recommendations.
- [ ] Each non-obvious instruction carries its reason, and no fact appears twice.
- [ ] No paragraph is a stack of five-word sentences; clauses connect with "because", "so", "while".
- [ ] Every bulleted section earned its bullets, and the page is not three lists in a row.
- [ ] No banned word or phrase from §2, and every adjective is a verifiable property.
- [ ] Claims state what is, and each negation is load-bearing.
- [ ] No slogan headings, rhetorical setup, or trailing pitch clause.
- [ ] No in-jokes or emoji in prose, and any exclamation mark is one you meant.
- [ ] I read the page top to bottom and deleted every sentence that didn't help the reader act.
