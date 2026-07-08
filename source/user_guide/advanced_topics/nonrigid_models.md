# Non-rigid material models

A **constitutive model** is the equation that relates how much a material deforms to the stress it develops in response. In Genesis World you do not call these equations directly. You assign a `material` to an entity, and that choice selects both the solver that advances it and the constitutive model it obeys. This page explains the models behind the material classes in `gs.materials`: what each one computes, the parameters that shape it, and when to reach for it.

For the complementary question of which *solver* to use and how to configure a scene around it, see {doc}`/user_guide/getting_started/beyond_rigid_bodies`. For actuated muscles specifically, see {doc}`/user_guide/getting_started/soft_robots`. For how forces cross material boundaries, see {doc}`/user_guide/advanced_topics/solvers_and_coupling`.

## The shared foundation

Every continuum material tracks the **deformation gradient** $\mathbf F$, the local map from an undeformed neighborhood to its deformed shape. Its determinant $J = \det \mathbf F$ is the local volume ratio: $J = 1$ is volume-preserving, $J < 1$ is compression, and $J > 1$ is expansion. A constitutive model is a rule that turns $\mathbf F$ into a stress, usually by way of an elastic strain-energy density $\psi(\mathbf F)$ whose derivative is the force.

Most solids share three physical parameters, from which Genesis derives the Lamé coefficients $\mu$ (resistance to shear) and $\lambda$ (resistance to volume change):

- **`E`:** Young's modulus in Pa, the overall stiffness. Larger `E` means a stiffer body and a numerically stiffer system that needs smaller substeps.
- **`nu`:** Poisson ratio, the tendency to preserve volume under stretch. Values near `0.5` are nearly incompressible.
- **`rho`:** density in kg/m³ (kg/m² for the 2D PBD cloth model).

$$\mu = \frac{E}{2(1+\nu)}, \qquad \lambda = \frac{E\,\nu}{(1+\nu)(1-2\nu)}.$$

Several models factor $\mathbf F$ before building a stress. The polar decomposition $\mathbf F = \mathbf R \mathbf S$ splits it into a rotation $\mathbf R$ and a symmetric stretch $\mathbf S$; the singular value decomposition $\mathbf F = \mathbf U \boldsymbol\Sigma \mathbf V^\top$ exposes the principal stretches on the diagonal of $\boldsymbol\Sigma$. Plasticity models operate directly on those stretches.

## Elastic models

An elastic material returns to its rest shape when unloaded: all deformation is stored as recoverable energy. Genesis provides elastic models across three solvers, and the elastic classes are the base that plasticity and muscle models extend.

**`gs.materials.MPM.Elastic`** offers two stress models through its `model` argument:

- **`"corotation"`** (the default): the fixed-corotated model, whose energy penalizes deviation from the nearest rotation, $\psi(\mathbf F) = \mu\,\lVert \mathbf F - \mathbf R\rVert_F^2 + \tfrac{\lambda}{2}(J-1)^2$. It handles large rotations cleanly and is a good default for stiff, chalk-like solids.
- **`"neohooken"`**: a Neo-Hookean model, $\psi(\mathbf F) = \tfrac{\mu}{2}(\operatorname{tr}(\mathbf F^\top\mathbf F) - 3) - \mu\ln J + \tfrac{\lambda}{2}(\ln J)^2$. It reads $\mathbf F$ and $J$ directly and skips the SVD, so it is cheaper per particle. The accepted literal is spelled `"neohooken"`.

**`gs.materials.FEM.Elastic`** solves elasticity on a tetrahedral mesh and exposes three models, defaulting to `"linear"`:

```python
soft = scene.add_entity(
    material=gs.materials.FEM.Elastic(E=3e5, nu=0.45, model="stable_neohookean"),
    morph=gs.morphs.Sphere(radius=0.1),
)
```

- **`"linear"`:** linear elasticity. Fastest and the only model with a constant (precomputed) Hessian, but valid only for small strains; large rotations produce visible artifacts.
- **`"stable_neohookean"`:** the rest-stable Neo-Hookean formulation. Its energy stays well-defined for inverted or degenerate elements, which makes it the robust choice for large deformation and contact-rich scenes.
- **`"linear_corotated"`:** linear elasticity evaluated in a per-element rotated frame, recovering correct behavior under large rotation while keeping a linear stress response to stretch.

**`gs.materials.PBD.Elastic`** takes a different route. Position-Based Dynamics does not integrate a stress; it enforces geometric constraints on particle positions. Stiffness is expressed as **compliance** (inverse stiffness) rather than a modulus, with `stretch_compliance`, `bending_compliance`, and `volume_compliance` controlling edge, bending, and volume constraints. In the XPBD formulation a constraint's effective compliance is $\alpha = \text{compliance}/\Delta t^2$, so a compliance of `0.0` is perfectly rigid. Reach for it when speed and stability matter more than physical accuracy.

## Elastoplasticity: permanent deformation

A plastic material keeps part of its deformation after unloading. Genesis models this by splitting $\mathbf F$ into an elastic part that stores energy and a plastic part that does not. Each step first computes a trial elastic state, then a **return mapping** projects it back onto a yield surface, moving any excess into the permanent plastic part.

**`gs.materials.MPM.ElastoPlastic`** supports two yield criteria through `use_von_mises`:

- **von Mises (`use_von_mises=True`, the default):** yielding is governed by the deviatoric (shape-changing) part of the Hencky strain $\boldsymbol\varepsilon = \ln\boldsymbol\Sigma$. The material flows once $\lVert \operatorname{dev}\boldsymbol\varepsilon\rVert$ exceeds $\tau_Y / (2\mu)$, where the threshold `von_mises_yield_stress` is $\tau_Y$. This models a metal- or clay-like solid that dents and holds the dent.
- **Singular-value clamping (`use_von_mises=False`):** the principal stretches are clamped into $[\,1-\texttt{yield\_lower},\ 1+\texttt{yield\_higher}\,]$, capping how far the material may stretch or compress elastically before the rest is made permanent.

**`gs.materials.MPM.Sand`** implements a Drucker-Prager model for cohesionless granular media. Its yield surface is a cone in stress space set by `friction_angle` (degrees): particles resist shear only under confining pressure, so sand piles up to an angle of repose and otherwise flows.

```python
sand = scene.add_entity(
    material=gs.materials.MPM.Sand(friction_angle=45.0),  # degrees
    morph=gs.morphs.Box(size=(0.2, 0.2, 0.2)),
)
```

**`gs.materials.MPM.Snow`** is a specialization of `ElastoPlastic` that uses singular-value clamping (it does not support von Mises) and additionally *hardens* as it compacts: the more it is compressed, the stiffer it becomes. This reproduces the way snow packs into a firm, shape-holding solid.

## Liquids

Liquids sustain no shear stress at rest; they resist only changes in volume. Three material classes model them, differing in how strictly incompressibility is enforced.

**`gs.materials.MPM.Liquid`** is weakly compressible. Each step it discards the shape of $\mathbf F$, keeping only its volumetric part $J^{1/3}\mathbf I$, so no shear stress accumulates and the material flows freely; pressure comes from the volume change alone. Set `viscous=True` to retain a deviatoric viscous term for a thicker fluid.

**`gs.materials.SPH.Liquid`** is a purely particle-based fluid whose pressure follows a Tait equation of state,

$$p_i = k\left[\left(\frac{\rho_i}{\rho_0}\right)^{n} - 1\right],$$

where $k$ is `stiffness`, $n$ is `exponent`, and $\rho_0$ is the rest density `rho`. It exposes fluid parameters directly: `mu` sets viscosity and `gamma` sets surface tension. Choose SPH when you want a free-surface liquid tuned by physical fluid properties.

**`gs.materials.PBD.Liquid`** enforces a per-particle density constraint positionally rather than through pressure, tuned by `density_relaxation` and `viscosity_relaxation`. It is the fastest liquid model and the least physically precise.

## Muscles: active materials

A muscle is an elastic material with an extra, controllable stress. On top of the passive elastic response, it adds an **active stress** along an embedded fiber direction $\mathbf m$, proportional to a per-step actuation signal. Contracting the fiber pulls the body into a new shape; releasing it lets the elastic part restore the rest configuration.

- **`gs.materials.MPM.Muscle`:** actuated per particle; extends `MPM.Elastic` and defaults to the `"neohooken"` passive model.
- **`gs.materials.FEM.Muscle`:** actuated per tetrahedral element; extends `FEM.Elastic` and defaults to the `"linear"` passive model.

Both accept `n_groups` to define independently actuated fiber groups. The end-to-end control loop is covered in {doc}`/user_guide/getting_started/soft_robots`.

## Cloth and thin shells

Cloth is a two-dimensional material: it stretches and bends but has negligible thickness. Two classes model it.

- **`gs.materials.PBD.Cloth`:** a constraint-based sheet with separate `stretch_compliance` and `bending_compliance`. Its `rho` is a surface density in kg/m², and entity mass is `rho` times surface area. This is the fast, interactive option for garments and flags.
- **`gs.materials.FEM.Cloth`:** a thin-shell FEM material for the IPC contact backend, parameterized by `thickness` (m) and optional `bending_stiffness`. Use it when cloth must resolve accurate, penetration-free contact against other bodies.

## Choosing a model

| Behavior you want | Material | Key parameter or option |
|---|---|---|
| Recoverable elastic solid | `MPM.Elastic`, `FEM.Elastic`, `PBD.Elastic` | `model`, or compliance for PBD |
| Dents and holds its shape | `MPM.ElastoPlastic` | `use_von_mises`, `von_mises_yield_stress` |
| Granular media / sand | `MPM.Sand` | `friction_angle` |
| Compacting snow | `MPM.Snow` | `yield_lower`, `yield_higher` |
| Flowing liquid | `MPM.Liquid`, `SPH.Liquid`, `PBD.Liquid` | `viscous`; `stiffness`/`mu`/`gamma` for SPH |
| Actuated soft body | `MPM.Muscle`, `FEM.Muscle` | `n_groups`, actuation signal |
| Cloth and shells | `PBD.Cloth`, `FEM.Cloth` | compliances; `thickness` for FEM |

## References

- Stomakhin, A. et al. "A Material Point Method for Snow Simulation." SIGGRAPH 2013.
- Klár, G. et al. "Drucker-Prager Elastoplasticity for Sand Animation." SIGGRAPH 2016.
- Smith, B., Goldade, T., Kim, T. "Stable Neo-Hookean Flesh Simulation." ACM TOG 2018.
- Macklin, M., Müller, M., Chentanez, N. "XPBD: Position-Based Simulation of Compliant Constrained Dynamics." MIG 2016.
- Bender, J., Koschier, D. "Divergence-Free Smoothed Particle Hydrodynamics." SCA 2015.
