# Soft solvers

Beyond the {doc}`rigid solver <rigid_solver/index>`, Genesis World ships five solvers for continuum and particle materials. You do not instantiate one: assigning a `material` to an entity selects both the solver that advances it and the **constitutive model** it obeys, the rule that turns deformation into stress. A solver is activated at build time only if it holds at least one entity.

To pick a solver and run one, see {doc}`/user_guide/physics/beyond_rigid_bodies`. For how forces cross material boundaries, see {doc}`coupling/index`.

## Solvers

| Solver | Models | Representation |
|---|---|---|
| **MPM** (Material Point Method) | Elastic solids, plastics, sand, snow, liquids | Particles carry state, a background grid resolves forces |
| **FEM** (Finite Element Method) | Stiff elastic solids, volumetric muscles, thin shells | Tetrahedral mesh |
| **PBD** (Position-Based Dynamics) | Cloth, ropes, topology-preserving deformables | Particles linked by constraints |
| **SPH** (Smoothed-Particle Hydrodynamics) | Free-surface liquids | Particles |
| **SF** (Stable Fluids) | Smoke and gas | Fixed Eulerian grid |

A **kinematic** solver for scripted motion and a **tool** solver for driven manipulators round out the set, and a material selects them as it does the five above: `gs.materials.Kinematic` and `gs.materials.Tool`. The tool solver drives the soft solvers through one-way coupling, while a kinematic entity is rendered only and takes no part in physics.

## Deformation and stress

Every continuum material tracks the **deformation gradient** $\mathbf F$, the local map from an undeformed neighborhood to its deformed shape. Its determinant $J = \det \mathbf F$ is the local volume ratio: $J = 1$ preserves volume, $J < 1$ is compression, $J > 1$ expansion. A constitutive model turns $\mathbf F$ into a stress, usually through an elastic strain-energy density $\psi(\mathbf F)$ whose derivative is the force.

Most solids take three parameters, from which Genesis derives the Lamé coefficients $\mu$ (resistance to shear) and $\lambda$ (resistance to volume change):

- **`E`:** Young's modulus in Pa. Larger `E` is a stiffer body, and a numerically stiffer system that needs smaller substeps.
- **`nu`:** Poisson ratio. Values near `0.5` are nearly incompressible.
- **`rho`:** density in kg/m³, or kg/m² for the 2D PBD cloth model.

$$\mu = \frac{E}{2(1+\nu)}, \qquad \lambda = \frac{E\,\nu}{(1+\nu)(1-2\nu)}.$$

Several models factor $\mathbf F$ first. The polar decomposition $\mathbf F = \mathbf R \mathbf S$ splits it into a rotation and a symmetric stretch; the singular value decomposition $\mathbf F = \mathbf U \boldsymbol\Sigma \mathbf V^\top$ exposes the principal stretches on the diagonal of $\boldsymbol\Sigma$. Plasticity models operate on those stretches directly.

## Elastic solids

An elastic material returns to its rest shape when unloaded. The elastic classes are also the base that the plastic and muscle models extend.

{py:class}`gs.materials.MPM.Elastic <genesis.engine.materials.MPM.elastic.Elastic>` selects its stress model through `model`:

- **`"corotation"`** (default): fixed-corotated, $\psi(\mathbf F) = \mu\,\lVert \mathbf F - \mathbf R\rVert_F^2 + \tfrac{\lambda}{2}(J-1)^2$. The energy penalizes deviation from the nearest rotation, so large rotations stay well behaved.
- **`"neohooken"`**: $\psi(\mathbf F) = \tfrac{\mu}{2}(\operatorname{tr}(\mathbf F^\top\mathbf F) - 3) - \mu\ln J + \tfrac{\lambda}{2}(\ln J)^2$. Reads $\mathbf F$ and $J$ directly and skips the SVD, so it costs less per particle.

{py:class}`gs.materials.FEM.Elastic <genesis.engine.materials.FEM.elastic.Elastic>` solves elasticity on a tetrahedral mesh, defaulting to `"linear"`:

```python
soft = scene.add_entity(
    material=gs.materials.FEM.Elastic(E=3e5, nu=0.45, model="stable_neohookean"),
    morph=gs.morphs.Sphere(radius=0.1),
)
```

- **`"linear"`:** linear elasticity, the only model with a constant precomputed Hessian. Valid for small strains; large rotations produce artifacts.
- **`"stable_neohookean"`:** rest-stable Neo-Hookean. Its energy stays defined for inverted or degenerate elements, which suits large deformation and contact-rich scenes.
- **`"linear_corotated"`:** linear elasticity in a per-element rotated frame, correct under large rotation with a linear response to stretch.

{py:class}`gs.materials.PBD.Elastic <genesis.engine.materials.PBD.elastic.Elastic>` integrates no stress. Position-Based Dynamics enforces geometric constraints on particle positions, and expresses stiffness as **compliance**, the inverse: `stretch_compliance`, `bending_compliance`, and `volume_compliance` govern edge, bending, and volume constraints. Under XPBD a constraint's effective compliance is $\alpha = \text{compliance}/\Delta t^2$, so `0.0` is perfectly rigid. It trades physical accuracy for speed and stability.

## Plastic solids

A plastic material keeps part of its deformation after unloading. Genesis splits $\mathbf F$ into an elastic part that stores energy and a plastic part that does not: each step computes a trial elastic state, then a **return mapping** projects it onto a yield surface and moves the excess into the plastic part.

{py:class}`gs.materials.MPM.ElastoPlastic <genesis.engine.materials.MPM.elasto_plastic.ElastoPlastic>` offers two yield criteria through `use_von_mises`:

- **von Mises** (default): yielding follows the deviatoric part of the Hencky strain $\boldsymbol\varepsilon = \ln\boldsymbol\Sigma$. The material flows once $\lVert \operatorname{dev}\boldsymbol\varepsilon\rVert$ exceeds $\tau_Y / (2\mu)$, with `von_mises_yield_stress` setting $\tau_Y$, so the body dents and holds the dent.
- **Singular-value clamping** (`use_von_mises=False`): the principal stretches are clamped into $[\,1-\texttt{yield\_lower},\ 1+\texttt{yield\_higher}\,]$, capping elastic stretch and compression before the rest becomes permanent.

{py:class}`gs.materials.MPM.Sand <genesis.engine.materials.MPM.sand.Sand>` is a Drucker-Prager model for cohesionless granular media. Its yield surface is a cone in stress space set by `friction_angle` in degrees: particles resist shear only under confining pressure, so sand holds an angle of repose and otherwise flows.

{py:class}`gs.materials.MPM.Snow <genesis.engine.materials.MPM.snow.Snow>` specializes `ElastoPlastic` with singular-value clamping only, and hardens as it compacts, so it packs into a shape-holding solid.

## Liquids

Liquids sustain no shear stress at rest and resist only volume change. The three classes differ in how incompressibility is enforced.

{py:class}`gs.materials.MPM.Liquid <genesis.engine.materials.MPM.liquid.Liquid>` is weakly compressible: each step discards the shape of $\mathbf F$ and keeps its volumetric part $J^{1/3}\mathbf I$, so no shear stress accumulates and pressure comes from volume change alone. `viscous=True` retains a deviatoric viscous term for a thicker fluid.

{py:class}`gs.materials.SPH.Liquid <genesis.engine.materials.SPH.liquid.Liquid>` derives pressure from a Tait equation of state,

$$p_i = k\left[\left(\frac{\rho_i}{\rho_0}\right)^{n} - 1\right],$$

with $k$ from `stiffness`, $n$ from `exponent`, and rest density $\rho_0$ from `rho`. Viscosity and surface tension are set directly, by `mu` and `gamma`.

{py:class}`gs.materials.PBD.Liquid <genesis.engine.materials.PBD.liquid.Liquid>` enforces a per-particle density constraint positionally rather than through pressure, tuned by `density_relaxation` and `viscosity_relaxation`.

## Cloth

Cloth stretches and bends with negligible thickness.

- **{py:class}`gs.materials.PBD.Cloth <genesis.engine.materials.PBD.cloth.Cloth>`:** a constraint-based sheet with separate `stretch_compliance` and `bending_compliance`. Its `rho` is a surface density, so entity mass is `rho` times surface area.
- **{py:class}`gs.materials.FEM.Cloth <genesis.engine.materials.FEM.cloth.Cloth>`:** a thin-shell FEM material for the IPC contact backend, parameterized by `thickness` in meters and an optional `bending_stiffness`. Use it when cloth must resolve penetration-free contact against other bodies.

## Muscles

A muscle adds a controllable **active stress** along an embedded fiber direction $\mathbf m$ on top of a passive elastic response, proportional to a per-step actuation signal. Contracting the fiber pulls the body into a new shape; releasing it lets the elastic part restore the rest configuration.

- **{py:class}`gs.materials.MPM.Muscle <genesis.engine.materials.MPM.muscle.Muscle>`:** actuated per particle, extending `MPM.Elastic` with the `"neohooken"` passive model.
- **{py:class}`gs.materials.FEM.Muscle <genesis.engine.materials.FEM.muscle.Muscle>`:** actuated per tetrahedral element, extending `FEM.Elastic` with the `"linear"` passive model.

Both take `n_groups` to define independently actuated fiber groups. The control loop is covered in {doc}`/user_guide/physics/soft_robots`.

## Choosing a model

| Behavior | Material | Key parameter |
|---|---|---|
| Recoverable elastic solid | `MPM.Elastic`, `FEM.Elastic`, `PBD.Elastic` | `model`, or compliance for PBD |
| Dents and holds its shape | `MPM.ElastoPlastic` | `use_von_mises`, `von_mises_yield_stress` |
| Granular media | `MPM.Sand` | `friction_angle` |
| Compacting snow | `MPM.Snow` | `yield_lower`, `yield_higher` |
| Flowing liquid | `MPM.Liquid`, `SPH.Liquid`, `PBD.Liquid` | `viscous`; `stiffness`, `mu`, `gamma` for SPH |
| Actuated soft body | `MPM.Muscle`, `FEM.Muscle` | `n_groups` |
| Cloth and shells | `PBD.Cloth`, `FEM.Cloth` | compliances; `thickness` for FEM |

## References

- Stomakhin, A. et al. "A Material Point Method for Snow Simulation." SIGGRAPH 2013.
- Klár, G. et al. "Drucker-Prager Elastoplasticity for Sand Animation." SIGGRAPH 2016.
- Smith, B., Goldade, T., Kim, T. "Stable Neo-Hookean Flesh Simulation." ACM TOG 2018.
- Macklin, M., Müller, M., Chentanez, N. "XPBD: Position-Based Simulation of Compliant Constrained Dynamics." MIG 2016.
- Bender, J., Koschier, D. "Divergence-Free Smoothed Particle Hydrodynamics." SCA 2015.
