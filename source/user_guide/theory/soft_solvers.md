# Soft solvers

Beyond the {doc}`rigid solver <rigid_solver/index>`, Genesis World ships five solvers for continuum and particle materials. The class of the entity options selects the solver that advances an entity, and its `material` selects the **constitutive model** the entity obeys, the rule that turns deformation into stress. The simulator activates a solver at build time only if it holds at least one entity.

To pick a solver and run one, see {doc}`/user_guide/physics/beyond_rigid_bodies`. For how forces cross material boundaries, see {doc}`/user_guide/physics/coupling/index`.

## Solvers

| Solver | Models | Representation |
|---|---|---|
| **MPM** (Material Point Method) | Elastic solids, plastics, sand, snow, liquids | Particles carry state, a background grid resolves forces |
| **FEM** (Finite Element Method) | Stiff elastic solids, volumetric muscles, thin shells | Tetrahedral mesh |
| **PBD** (Position-Based Dynamics) | Cloth, ropes, topology-preserving deformables | Particles linked by constraints |
| **SPH** (Smoothed-Particle Hydrodynamics) | Free-surface liquids | Particles |
| **SF** (Stable Fluids) | Smoke and gas | Fixed Eulerian grid |

A **kinematic** solver for scripted motion rounds out the set, selected by {py:class}`gs.options.KinematicEntityOptions <genesis.options.entities.KinematicEntityOptions>`. A kinematic entity is rendered only and takes no part in physics.

## Deformation and stress

Every continuum material tracks the **deformation gradient** $\mathbf F$, the local map from an undeformed neighborhood to its deformed shape. Its determinant $J = \det \mathbf F$ is the local volume ratio: $J = 1$ preserves volume, $J < 1$ is compression, $J > 1$ expansion. A constitutive model turns $\mathbf F$ into a stress, usually through an elastic strain-energy density $\psi(\mathbf F)$ whose derivative is the force.

Most solids take three parameters, from which Genesis derives the Lamé coefficients $\mu$ (resistance to shear) and $\lambda$ (resistance to volume change):

- **`youngs_modulus`:** Young's modulus in Pa. A larger value is a stiffer body, and a numerically stiffer system that needs smaller substeps.
- **`poisson_ratio`:** Poisson ratio. Values near `0.5` are nearly incompressible.
- **`density`:** density in kg/m³.

$$\mu = \frac{E}{2(1+\nu)}, \qquad \lambda = \frac{E\,\nu}{(1+\nu)(1-2\nu)}.$$

Several models factor $\mathbf F$ first. The polar decomposition $\mathbf F = \mathbf R \mathbf S$ splits it into a rotation and a symmetric stretch; the singular value decomposition $\mathbf F = \mathbf U \boldsymbol\Sigma \mathbf V^\top$ exposes the principal stretches on the diagonal of $\boldsymbol\Sigma$. Plasticity models operate on those stretches directly.

## Elastic solids

An elastic material returns to its rest shape when unloaded. The elastic classes are also the base that the plastic and muscle models extend.

{py:class}`gs.materials.Elastic <genesis.options.materials.Elastic>` is simulated by MPM, FEM, and PBD, and each solver takes its model through the solver options of the entity. Under MPM, {py:class}`gs.options.MPMEntitySolverOptions <genesis.options.entities.MPMEntitySolverOptions>` selects the stress model through `model`:

- **`"corotation"`** (default): fixed-corotated, $\psi(\mathbf F) = \mu\,\lVert \mathbf F - \mathbf R\rVert_F^2 + \tfrac{\lambda}{2}(J-1)^2$. The energy penalizes deviation from the nearest rotation, so large rotations stay well behaved.
- **`"neohooken"`**: $\psi(\mathbf F) = \tfrac{\mu}{2}(\operatorname{tr}(\mathbf F^\top\mathbf F) - 3) - \mu\ln J + \tfrac{\lambda}{2}(\ln J)^2$. Reads $\mathbf F$ and $J$ directly and skips the SVD, so it costs less per particle.

Under FEM, which solves elasticity on a tetrahedral mesh, {py:class}`gs.options.FEMEntitySolverOptions <genesis.options.entities.FEMEntitySolverOptions>` selects the model, defaulting to `"linear"`:

```python
soft = scene.add_entity(
    options=gs.options.FEMEntityOptions(
        morph=gs.morphs.Sphere(
            radius=0.1,
        ),
        material=gs.materials.Elastic(
            youngs_modulus=3e5,
            poisson_ratio=0.45,
        ),
        solver_options=gs.options.FEMEntitySolverOptions(
            model="stable_neohookean",
        ),
    ),
)
```

- **`"linear"`:** linear elasticity, the only model with a constant precomputed Hessian. Valid for small strains; large rotations produce artifacts.
- **`"stable_neohookean"`:** rest-stable Neo-Hookean. Its energy stays defined for inverted or degenerate elements, which suits large deformation and contact-rich scenes.
- **`"linear_corotated"`:** linear elasticity in a per-element rotated frame, correct under large rotation with a linear response to stretch.

Under PBD, through {py:class}`gs.options.PBDElasticEntityOptions <genesis.options.entities.PBDElasticEntityOptions>`, an elastic solid integrates no stress. Position-Based Dynamics enforces geometric constraints on particle positions, and expresses stiffness as **compliance**, the inverse: `stretch_compliance`, `bending_compliance`, and `volume_compliance` of {py:class}`gs.options.PBDElasticEntitySolverOptions <genesis.options.entities.PBDElasticEntitySolverOptions>` govern edge, bending, and volume constraints. Under XPBD a constraint's effective compliance is $\alpha = \text{compliance}/\Delta t^2$, so `0.0` is perfectly rigid. It trades physical accuracy for speed and stability.

## Plastic solids

A plastic material keeps part of its deformation after unloading. Genesis splits $\mathbf F$ into an elastic part that stores energy and a plastic part that does not: each step computes a trial elastic state, then a **return mapping** projects it onto a yield surface and moves the excess into the plastic part.

{py:class}`gs.materials.ElastoPlastic <genesis.options.materials.ElastoPlastic>`, simulated by MPM, selects between two yield criteria through `yield_criterion`:

- **von Mises** (`"von_mises"`, default): yielding follows the deviatoric part of the Hencky strain $\boldsymbol\varepsilon = \ln\boldsymbol\Sigma$. The material flows once $\lVert \operatorname{dev}\boldsymbol\varepsilon\rVert$ exceeds $\tau_Y / (2\mu)$, with `yield_stress` setting $\tau_Y$, so the body dents and holds the dent.
- **Singular-value clamping** (`"stretch_clamp"`): the principal stretches are clamped into $[\,1-\texttt{critical\_compression},\ 1+\texttt{critical\_stretch}\,]$, capping elastic stretch and compression before the rest becomes permanent.

{py:class}`gs.materials.Sand <genesis.options.materials.Sand>` is a Drucker-Prager model for cohesionless granular media. Its yield surface is a cone in stress space set by `friction_angle` in degrees: particles resist shear only under confining pressure, so sand holds an angle of repose and otherwise flows.

{py:class}`gs.materials.Snow <genesis.options.materials.Snow>` applies the singular-value clamping of `ElastoPlastic` alone, and hardens as it compacts, so it packs into a shape-holding solid.

## Liquids

Liquids sustain no shear stress at rest and resist only volume change. MPM, SPH, and PBD all simulate {py:class}`gs.materials.Liquid <genesis.options.materials.Liquid>`, and they differ in how incompressibility is enforced.

Under MPM, a liquid is weakly compressible: each step discards the shape of $\mathbf F$ and keeps its volumetric part $J^{1/3}\mathbf I$, so no shear stress accumulates and pressure comes from volume change alone. A non-zero `viscosity` adds a deviatoric viscous term for a thicker fluid.

Under SPH, a liquid derives pressure from a Tait equation of state,

$$p_i = k\left[\left(\frac{\rho_i}{\rho_0}\right)^{n} - 1\right],$$

with $k$ the `bulk_modulus` of the material divided by $n$, $n$ the `exponent` of {py:class}`gs.options.SPHEntitySolverOptions <genesis.options.entities.SPHEntitySolverOptions>`, and rest density $\rho_0$ from `density`. Viscosity and surface tension are set directly, by `viscosity` and `surface_tension`.

Under PBD, a liquid enforces a per-particle density constraint positionally rather than through pressure, tuned by `density_relaxation` and `viscosity_relaxation` of {py:class}`gs.options.PBDLiquidEntitySolverOptions <genesis.options.entities.PBDLiquidEntitySolverOptions>`.

## Cloth

Cloth stretches and bends with negligible thickness. PBD and FEM both simulate {py:class}`gs.materials.Cloth <genesis.options.materials.Cloth>`.

- **PBD ({py:class}`gs.options.PBDClothEntityOptions <genesis.options.entities.PBDClothEntityOptions>`):** a constraint-based sheet with separate `stretch_compliance` and `bending_compliance` in its solver options. Its mass per unit area is `density` times `thickness`, so entity mass is that times surface area.
- **FEM ({py:class}`gs.options.FEMEntityOptions <genesis.options.entities.FEMEntityOptions>`):** a thin shell for the IPC contact backend, parameterized by `thickness` in meters and an optional `bending_stiffness`. Use it when cloth must resolve penetration-free contact against other bodies.

## Muscles

A muscle adds a controllable **active stress** along an embedded fiber direction $\mathbf m$ on top of a passive elastic response, proportional to a per-step actuation signal. Contracting the fiber pulls the body into a new shape; releasing it lets the elastic part restore the rest configuration.

{py:class}`gs.materials.Muscle <genesis.options.materials.Muscle>` is simulated by two solvers:

- **MPM:** actuated per particle, with the `"neohooken"` passive model by default.
- **FEM:** actuated per tetrahedral element, with the `"linear"` passive model by default.

Both take `n_groups` in their solver options to define independently actuated fiber groups. The control loop is covered in {doc}`/user_guide/physics/soft_robots`.

## Choosing a model

| Behavior | Material | Solvers | Key parameter |
|---|---|---|---|
| Recoverable elastic solid | `Elastic` | MPM, FEM, PBD | `model`, or compliance for PBD |
| Dents and holds its shape | `ElastoPlastic` | MPM | `yield_criterion`, `yield_stress` |
| Granular media | `Sand` | MPM | `friction_angle` |
| Compacting snow | `Snow` | MPM | `critical_compression`, `critical_stretch` |
| Flowing liquid | `Liquid` | MPM, SPH, PBD | `viscosity`; `bulk_modulus`, `surface_tension` for SPH |
| Actuated soft body | `Muscle` | MPM, FEM | `n_groups` |
| Cloth and shells | `Cloth` | PBD, FEM | compliances for PBD; `thickness` for FEM |

## References

- Stomakhin, A. et al. "A Material Point Method for Snow Simulation." SIGGRAPH 2013.
- Klár, G. et al. "Drucker-Prager Elastoplasticity for Sand Animation." SIGGRAPH 2016.
- Smith, B., Goldade, T., Kim, T. "Stable Neo-Hookean Flesh Simulation." ACM TOG 2018.
- Macklin, M., Müller, M., Chentanez, N. "XPBD: Position-Based Simulation of Compliant Constrained Dynamics." MIG 2016.
- Bender, J., Koschier, D. "Divergence-Free Smoothed Particle Hydrodynamics." SCA 2015.
