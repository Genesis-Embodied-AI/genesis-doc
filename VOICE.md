# Voice

This guide is about how the sentences read. The [style guide](STYLE_GUIDE.md) covers what goes on a page and
how it is marked up: structure, code examples, terminology, MyST directives. Read this one before you write
prose, and that one before you decide where the prose goes.

Write the way a senior engineer explains something to a capable colleague who is in a hurry. That person wants
the reason along with the instruction, and they will forgive you a longer sentence if it saves them a
question. Being short comes from knowing what you want to say, never from cutting sentences in half.

The failure mode these pages fall into is compression. A page that has had every connective word squeezed out
of it reads as choppy and authorless, and the reader ends up reassembling the logic the writer threw away.
Readers tell us so. Length is not the enemy: a paragraph that explains why a step exists earns its lines, and
a page of clipped declaratives does not become clearer by being shorter.

## Who speaks

Three subjects carry almost every sentence in these docs, and choosing among them deliberately is most of
what makes the pages sound like one person.

- **You** for what the reader does: "Call `scene.build()` before you step the simulation."
- **Genesis World** for what the software does: "Genesis World compiles the kernels on the first build."
- **We** for decisions and conventions the project made: "We follow SciPy's extrinsic x-y-z convention for
  Euler angles", "We call one copy of the scene an environment."

"We" is how the reader hears that a person chose this, so use it for our conventions, our defaults, our
recommendations, and the things we support. What it never does is escort the reader: "let's walk through it
together", "now we will look at the viewer", "if you are patient enough, let's continue". The reader is
reading, not accompanying you.

Keep the verbs active. "Parallelism is turned on when the scene is built" has nobody in it, while "you turn
parallelism on at build time" has both an actor and an action. When you catch yourself writing "is handled",
"is performed", or "can be configured", find the actor and put them in front. This holds for headings too:
prefer "Composing a scene from options" over "A scene is assembled from options".

## Explain, then instruct

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

## Ornament is not warmth

Warming up cold prose tempts you into decoration, which reads as written-by-machine just as badly as the
clipped version did. Both of the following say the same thing; the second one wastes the reader's attention on
a flourish and then editorializes about stiff gains.

- ✅ "`set_dofs_force_range` caps the controller's output."
- ❌ "`set_dofs_force_range` then caps what the controller is allowed to ask for, which is the limit that
  keeps a stiff gain from launching the arm."

If a shorter structure carries the same fact, use the shorter structure. Warmth comes from an audible author
and a reason attached to an instruction, never from ornament. Specifically:

- **Personification.** "The dynamics never get a say", "ask for a GPU backend", "this tutorial gives the arm
  something to hold onto". Software and options do not want, allow, or offer. ✅ "`set_*` writes the state
  directly, without consulting the dynamics."
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
  in what units? Name the cost: ✅ "IPC costs more per step than the other couplers."
- **Stating what the reader already knows.** "Shape primitives need no file at all" tells someone who just
  read the word "primitive" nothing. ✅ "The shape primitives are `Plane`, `Box`, …". The same goes for a
  sentence explaining that a default is the value used when you pass nothing, or that a getter returns the
  thing it is named after. If a reader could infer it from the name or the previous sentence, cut it.

## Rhythm

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

## Anti-patterns

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
  wonder whether you meant three things. Pick the term from §6 of the style guide and repeat it.

## State what is

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

## Words and phrases to avoid

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

## Register

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

## Worked example

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
> stays intersection-free however hard you press two bodies together. IPC costs more per step than the other
> couplers, which is why we leave it off by default.
>
> Use it for cloth with self-collision, for FEM solids pressed hard against each other, and for a gripper
> closing on a deformable object. For coarse rigid contact or mixed continuum scenes (MPM, SPH, PBD), the
> legacy coupler is cheaper and adequate; see the couplers overview for the full comparison.

The mechanism is stated once and made to carry its own consequence ("which is why contact under IPC stays…")
instead of being circled a second time. Defining IPC by what the other two couplers do is gone, and with it
the need to hold three models in your head to learn one. "Robustness" gives way to the property it stood in
for, the cost sits next to the benefit where a reader deciding between couplers needs it, and "we leave it off
by default" tells them that was our call rather than an accident.

## Rewrite rather than patch

Fixing a flagged phrase in place works when a page is basically sound. When a paragraph trips several of the
patterns above at once, and especially when its sentences all run to the same length, patching it produces
prose that reads as edited by machine, because that is what it is. Rewrite the paragraph from the fact it is
trying to convey. The same applies to your own edits: if a change does not alter what a sentence says or how it
reads, it is churn, so leave the original alone.

For a fuller catalog of the machine-writing patterns this guide draws on, see
[avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing).

## Checklist

Before merging prose:

- [ ] Every sentence has a subject that acts: you, Genesis World, or we. No orphaned passives.
- [ ] "We" appears where the page states one of our conventions, defaults, or recommendations.
- [ ] Each non-obvious instruction carries its reason, and no fact appears twice.
- [ ] No paragraph is a stack of five-word sentences; clauses connect with "because", "so", "while".
- [ ] Every bulleted section earned its bullets, and the page is not three lists in a row.
- [ ] No banned word or phrase from the list above, and every adjective is a verifiable property.
- [ ] Claims state what is, and each negation is load-bearing.
- [ ] No slogan headings, rhetorical setup, or trailing pitch clause.
- [ ] At most one em dash per paragraph, used for a genuine aside.
- [ ] No in-jokes or emoji in prose, and any exclamation mark is one you meant.
