# Documentation Style Guide

This guide defines how we write documentation for Genesis World. It is prescriptive: it describes the standard we are moving *toward*, not necessarily how every existing page reads today. When you touch a page, bring it closer to this standard.

Our north star is the class of technical documentation that developers actively enjoy using — Stripe, Django, and the Python standard library. What those share is not a house style but a set of habits: they respect the reader's time, they are accurate to a fault, and they read as one voice rather than a collection of authors.

---

## 1. Principles

Every rule below descends from five principles. When a rule doesn't fit a situation, reason from these instead.

1. **The reader is trying to get something done.** Documentation is a tool, not prose to be admired. Optimize for the reader who is stuck, skimming, and slightly frustrated — not the reader with time to read top to bottom.
2. **Accuracy is non-negotiable.** A single wrong argument name or stale output destroys trust in the whole page. Every code block must run. Every claim must be true at the current version.
3. **Show, then tell.** A correct, runnable example answers more questions than three paragraphs. Lead with it.
4. **One voice.** A reader should not be able to tell that fifty people wrote these pages. Consistency in terminology, structure, and tone is worth more than any individual author's preference.
5. **Less, but better.** The best edit is usually a deletion. Every sentence that doesn't help the reader act is a sentence that hides the one that does.

---

## 2. Voice and tone

**Write in a calm, direct, professional voice.** Confident and warm, never chatty, never salesy.

**Use second person ("you") for the reader and first person plural ("we") sparingly** — reserve "we" for the project's deliberate design decisions ("we follow the w-x-y-z quaternion convention"), not as a narrator walking the reader by the hand ("let's go through it together").

- ✅ "Call `scene.build()` before stepping the simulation."
- ✅ "Genesis World uses a right-handed, Z-up coordinate system."
- ❌ "Now, let's dive in a bit and play around together!"
- ❌ "If you are patient enough, let's walk through it step by step."

**No jokes, winks, or filler.** Personality comes from clarity, not from asides. Delete anything you'd cut from a spoken answer to a colleague who's in a hurry.

- ❌ "…or simply use `'dumb'` if you are a black-and-white person."
- ❌ "…up to 10~80x (yes, this is a bit sci-fi) faster…"
- ❌ "With just two lines of code you can now pick and place arbitrary objects! Feel free to integrate this into your pipeline."

**Keep marketing out of the docs.** Superlatives ("world's fastest", "unprecedented", "effortless") belong on the landing page and in the README, not in reference or tutorial material. State capabilities as facts the reader can verify, and let benchmarks live behind a link.

- ✅ "Parallel simulation runs across environments on a single GPU. See [benchmarks](…) for measured throughput."
- ❌ "Genesis World is the world's fastest physics engine, with unprecedented speed."

**Address the reader's mental state, not just the mechanics.** Say what a step is *for* and what will go wrong without it. The reader who knows *why* `build()` is required will remember it; the reader who was only told to call it will forget.

**Be decisive.** Prefer "Use X." over "You might want to consider possibly using X." Hedging wastes words and erodes authority. When there is a recommended path, name it and move the alternatives to a note.

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
# Name

One sentence: what it is and when to use it, with a link to the How-to in the User Guide.

## <autodoc>   -> `.. autoclass::` the options class, the sensor class, and the return type
## See also
```

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

**Keep paragraphs short.** Three or four sentences maximum. Break dense material into lists, tables, or steps. A wall of text is where information goes to hide.

---

## 4. Language and mechanics

**Active voice, present tense.** "Genesis World compiles the kernels on the first build," not "the kernels will be compiled." Describe what the software *does*, as a fact about the present.

**Short sentences.** One idea each. If a sentence has two "and"s or a parenthetical inside a parenthetical, split it.

**Define a term once, then reuse it exactly.** Don't alternate between "degree of freedom", "dof", and "motor" for the same thing. Introduce the term, bold it on first use, then use it consistently. (See §6 for the terms we've standardized.)

**Prefer concrete over abstract.** "Returns a tensor of shape `(n_envs, 3)`" beats "returns the relevant data."

**Numbers, units, and symbols:**
- Always state units. "9.81 m/s²", "0.01 s", "0.5 m". A bare number is a bug report waiting to happen.
- Use the actual symbol or identifier in code font: `dt`, `max_range`, `n_envs`.
- Write "10–80×" with an en dash and a real multiplication sign, not "10~80x". (Better: avoid the range and cite a benchmark.)

**Capitalization:**
- Sentence case for in-page content headings: "Reading sensor data", not "Reading Sensor Data". Navigation and section titles are the one exception (Title Case) — see §7.
- Code identifiers keep their real casing: `Scene`, `add_entity`, `gs.cpu`.

**Oxford comma. American spelling.** ("color", "behavior", "modeling").

**Spell out "and"; don't use the ampersand (`&`).** In headings, section titles, toctree captions, and running prose, write "and". The ampersand reads as shorthand, sorts and searches inconsistently, and clashes with the calm, spelled-out voice. (It is fine inside code, where `&` is an operator.)

- ✅ "Sensors and perception", "Theory and modelling"
- ❌ "Sensors & perception", "Theory & Modelling"

**Minimize em dashes; default to a colon, comma, or full stop.** The em dash (—) is the exception, not the reflex. Before using one, try a colon (to introduce or expand), a comma (for a light pause), or a new sentence — one of those is almost always cleaner and more scannable. At most one em dash per paragraph, and only for a genuine aside; a sentence whose clauses are strung together with them should be rewritten. When a phrase introduces or defines what follows, use a colon, not a dash. (An en dash in a number range like "10–80×" is not an em dash and is fine.)

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

**Comments earn their place.** A comment should explain *why*, or annotate a non-obvious value (units, conventions, shapes). Don't narrate what the code plainly says.

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
- Another doc page: `` {doc}`/api_reference/scene/scene` `` (leading `/` = path from `source/`).
- A Python object: `` {py:class}`genesis.Scene` `` / `` {py:meth}`genesis.Scene.build` `` where autodoc targets exist.
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

Before opening a docs PR, confirm:

- [ ] Every code block runs against the current release, and I've run it.
- [ ] Every fenced block is tagged with a lowercase language (`python`, `bash`, …).
- [ ] No space-aligned keyword arguments; Python is `black`-clean.
- [ ] The page leads with what it's for and a runnable example within one screen.
- [ ] No parameter, type, default, or return fact is re-typed from the API Reference (the source docstring); the guide and reference-page prose link to it instead.
- [ ] In-page headings are sentence case with no emoji; section/navigation titles (top-level section pages, toctree captions) are Title Case.
- [ ] No page or section title begins with an article ("The", "A", "An").
- [ ] Terminology matches §6; the product is "Genesis World" (not keyword-stuffed).
- [ ] No jokes, no marketing superlatives, no "let's".
- [ ] Headings, titles, and captions spell out "and" — no ampersands (`&`).
- [ ] Internal links use `{doc}` / `{py:*}` roles; no hard-coded genesis-doc URLs.
- [ ] Tensor shapes, coordinate frame, quaternion order, and units are stated where relevant.
- [ ] Alt text on every image; assets live under `_static/` and are referenced relatively.
- [ ] I read the page top to bottom and deleted every sentence that didn't help the reader act.
