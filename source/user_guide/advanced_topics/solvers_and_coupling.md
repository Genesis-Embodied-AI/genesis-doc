# 🧮 Solvers & Coupling

Genesis allows you to combine multiple continuum and rigid-body solvers in the **same scene** – e.g. MPM snow interacting with SPH water, deformable FEM tissue colliding with surgical tools, or rigid props splashing into a granular bed.  All cross-solver interactions are orchestrated by the `gs.engine.Coupler` class.

This page explains:

* the **architecture** of the Coupler and how it decides which solver pairs are active;
* the **impulse-based collision response** that governs momentum exchange;
* the meaning of **friction, restitution, softness** and other coupling parameters;
* a quick **reference table** of currently supported solver pairs; and
* **usage examples** showing how to enable/disable specific interactions.

---

## 1. Architecture overview

Internally the simulator owns **one Coupler instance** which keeps pointers to every solver.  During each sub-step the simulator executes:

1. `solver.preprocess(f)`  &nbsp;&nbsp; – solver-specific internal bookkeeping.
2. `coupler.preprocess(f)`  &nbsp;&nbsp; – e.g. surfacing operations for CPIC.
3. `solver.advance(f)`       – advance each individual solver.
4. `coupler.couple(f)`       – exchange momentum between solvers.

Because all solver fields live on Taichi data-structures the Coupler can call Taichi `@kernel`s that touch the memory of several solvers **without data copies**.

### 1.1 Activating a coupling pair

Whether a pair is active is determined **statically once** when `Coupler.build()` is called:

```python
self._rigid_mpm = rigid.is_active() and mpm.is_active() and options.rigid_mpm
```

so you simply turn a pair on/off from python via `CouplerOptions` (see §4).


## 2. Impulse-based collision response

### 2.1 Signed distance & influence weight

For every candidate contact the Coupler queries the signed distance function `sdf(p)` of the rigid geometry.  The *softness* parameter produces a smooth blending weight

\[
\text{influence} = \min\bigl( \exp\!\left(-\dfrac{\;d\;}{\epsilon}\right) ,\;1 \bigr)
\]

where `d` is the signed distance and `ε = coup_softness`.  Large softness values make the contact zone thicker and produce gentler impulses.

### 2.2 Relative velocity decomposition

For a particle/grid node with world velocity **v** and a rigid body velocity **vᵣ**, the **relative velocity** is

\[ \mathbf r = \mathbf v - \mathbf v_{\text{rigid}}. \]

Split **r** into its normal and tangential components

\[
 r_n = (\mathbf r \cdot \mathbf n)\,\mathbf n, \quad
 r_t = \mathbf r - r_n
\]

with **n** the outward surface normal.

### 2.3 Normal impulse (restitution)

If the normal component is *inward* (\(r_n<0\)) an impulse is applied so that after the collision

\[ r_n' = -e\,r_n, \quad 0 \le e \le 1, \]

where `e = coup_restitution` is the **restitution coefficient**.  `e=0` is perfectly inelastic, `e=1` perfectly elastic.

### 2.4 Tangential impulse (Coulomb friction)

Friction is implemented by **scaling** the tangential component:

\[ r_t' = \max\!\bigl( 0,\;|r_t| + \mu \, r_n\bigr) \; \dfrac{r_t}{|r_t|}\,, \]

with `μ = coup_friction`.  This is an impulse-based variant of Coulomb friction that ensures the post-collision tangential speed never exceeds the sticking limit.

### 2.5 Velocity update and momentum transfer

The new particle/node velocity is then

\[ \mathbf v' = \mathbf v_{\text{rigid}} + (r_t' + r_n') \times \text{influence} + \mathbf r\,(1-\text{influence}). \]

The *change of momentum*

\[ \Delta\mathbf p = m\,(\mathbf v' - \mathbf v) \]

is applied as an **external force** on the rigid body

\[ \mathbf F_{\text{rigid}} = -\dfrac{\Delta\mathbf p}{\Delta t}. \]

Thus Newton's third law is satisfied and the rigid body responds to fluid impacts.

---

## 3. Supported solver pairs

| Pair | Direction | Notes |
|------|-----------|-------|
| **MPM ↔ Rigid** | impulse based on grid nodes (supports CPIC) |
| **MPM ↔ SPH**   | averages SPH particle velocities within an MPM cell |
| **MPM ↔ PBD**   | similar to SPH but skips pinned PBD particles |
| **FEM ↔ Rigid** | collision on surface vertices only |
| **FEM ↔ MPM**   | uses MPM P2G/G2P weights to exchange momentum |
| **FEM ↔ SPH**   | experimental – normal projection only |
| **SPH ↔ Rigid** | robust side-flip handling of normals |
| **PBD ↔ Rigid** | positional correction then velocity projection |
| **Tool ↔ MPM**  | delegated to each Tool entity's `collide()` |

If a combination is not in the table it is currently unsupported.

---

## 4. Configuration (`gs.options.CouplerOptions`)

```python
from genesis import options as gso

opt = gso.CouplerOptions(
    rigid_mpm = True,   # enable MPM–rigid coupling
    rigid_sph = True,   # enable SPH–rigid coupling
    coup_softness = 0.02,      # contact thickness (m)
    coup_friction  = 0.3,      # Coulomb µ
    coup_restitution = 0.1,    # bounciness e
)
```

All boolean flags default to **False** so only the pairs you explicitly activate will be evaluated at run-time.

Parameter summary:

| Name | Meaning | Typical range |
|------|---------|---------------|
| `coup_softness` | exponential fall-off length of influence | 0.01 – 0.05 (m) |
| `coup_friction` | Coulomb friction coefficient μ | 0 – 1 |
| `coup_restitution` | normal restitution coefficient e | 0 – 1 |

---

## 5. Practical tips

* **Performance** – coupling kernels run once per sub-step.  Disable unused pairs to save time.
* **Softness** – start with a larger `coup_softness` (e.g. 0.05 m) for stable simulations, then decrease to sharpen contacts.
* **Friction** – for dry contacts choose μ≈0.5.  For water-rigid interactions set μ close to 0.
* **Restitution** – values >0.3 can introduce oscillations when coupled with compliant materials.

---

## 6. Minimal example

```python
import genesis as gs

sim = gs.Simulator()

# Add a rigid bowl
bowl = sim.add_rigid("bowl.obj", friction=0.4)

# Fill with SPH water
water = sim.add_sph_box(res=(64,64,64), density=1000)

# Enable SPH-rigid coupling
sim.options.coupler.rigid_sph = True
sim.options.coupler.coup_friction = 0.1
sim.options.coupler.coup_softness = 0.02

sim.run(3.0)  # seconds
```

The water will splash against the bowl transferring momentum back to the bowl via the impulse-based method detailed above.

---

*Last updated: {{ date }}*
