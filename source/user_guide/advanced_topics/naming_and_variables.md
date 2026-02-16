# 📃 Naming and Variables

Different solvers represent physical entities using various formats, such as particles, elements, grids, and surfaces. Each data field is prefixed according to its corresponding representation. For computational efficiency and structures, data fields associated with different physical attributes are organized into the following categories (based on types of computations):
- `*_state_*`: Dynamic states updated at every solver step. These fields are typically instantiated with `requires_grad` enabled by default. Its field size is, if differentiable, (number of substeps, number of units) and, if not, (number of units), where units depend on the representation like particles, vertices, etc. There may be different suffix for further specification such as,
    - `*_state_ng`: Set `requires_gradient` to False.
- `*_info`: Static attributes that remain constant throughout the simulation, typically encompassing physical properties such as mass, stiffness, viscosity, etc. Its field size is (number of units,)
- `*_render`: Fields used exclusively for visualization, not directly involved in the physics computations. Its field size is (number of units,).
<!-- Note that there may be both static and dynamic attributes for rendering, resulting in `*_state_render` and `*_info_render`. -->
<!-- There may be different suffix for further specification such as,
    - `*_state_ng`: Set `requires_gradient` to False.
    - `*_state_reordered`: Cached data with reordering. -->

Overall, the naming following `<representation>_<computation-type>`. (We always follow plural form with an s in representation, e.g., `dofs`, `particles`, `elements`, etc.)

Also, some useful generic data types (defined in [genesis/\_\_init\_\_.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/__init__.py)):
```python
qd_vec2 = qd.types.vector(2, qd_float)
qd_vec3 = qd.types.vector(3, qd_float)
qd_vec4 = qd.types.vector(4, qd_float)
qd_vec6 = qd.types.vector(6, qd_float)
qd_vec7 = qd.types.vector(7, qd_float)
qd_vec11 = qd.types.vector(11, qd_float)

qd_mat3 = qd.types.matrix(3, 3, qd_float)
qd_mat4 = qd.types.matrix(4, 4, qd_float)

qd_ivec2 = qd.types.vector(2, qd_int)
qd_ivec3 = qd.types.vector(3, qd_int)
qd_ivec4 = qd.types.vector(4, qd_int)
```

In the following sections, we briefly describe the variables used by each solver.

## Rigid Solver

The rigid solver involves links, joints, geometry, and vertex representations. The rigid solver models articulated bodies composed of links and joints, with each link potentially consisting of multiple geometric components. Each geometry, in turn, may contain numerous vertices.

For links,
* Dynamic link state (`links_state`)
    ```python
    qd.types.struct(
        parent_idx=gs.qd_int,         # index of the parent link in the kinematic tree (-1 if root)
        root_idx=gs.qd_int,           # index of the root link in the articulation
        q_start=gs.qd_int,            # start index in the global configuration vector (q)
        dof_start=gs.qd_int,          # start index in the global DoF vector
        joint_start=gs.qd_int,        # start index for joints affecting this link
        q_end=gs.qd_int,              # end index in the global configuration vector
        dof_end=gs.qd_int,            # end index in the global DoF vector
        joint_end=gs.qd_int,          # end index for joints affecting this link
        n_dofs=gs.qd_int,             # number of degrees of freedom for this link
        pos=gs.qd_vec3,               # current world-space position of the link
        quat=gs.qd_vec4,              # current world-space orientation (quaternion)
        invweight=gs.qd_vec2,         # inverse mass
        is_fixed=gs.qd_int,           # boolean flag: 1 if link is fixed/static, 0 if dynamic
        inertial_pos=gs.qd_vec3,      # position of the inertial frame (CoM) in link-local coordinates
        inertial_quat=gs.qd_vec4,     # orientation of the inertial frame relative to the link frame
        inertial_i=gs.qd_mat3,        # inertia tensor in the inertial frame
        inertial_mass=gs.qd_float,    # mass of the link
        entity_idx=gs.qd_int,         # index of the entity this link belongs to
    )
    ```
* Static link information (`links_info`)
    ```python
    qd.types.struct(
        cinr_inertial=gs.qd_mat3,     # com-based body inertia
        cinr_pos=gs.qd_vec3,          # com-based body position
        cinr_quat=gs.qd_vec4,         # com-based body orientation
        cinr_mass=gs.qd_float,        # com-based body mass
        crb_inertial=gs.qd_mat3,      # com-based composite inertia
        crb_pos=gs.qd_vec3,           # com-based composite position
        crb_quat=gs.qd_vec4,          # com-based composite orientation
        crb_mass=gs.qd_float,         # com-based composite mass
        cdd_vel=gs.qd_vec3,           # com-based acceleration (linear)
        cdd_ang=gs.qd_vec3,           # com-based acceleration (angular)
        pos=gs.qd_vec3,               # current world position
        quat=gs.qd_vec4,              # current orientation
        ang=gs.qd_vec3,               # angular velocity
        vel=gs.qd_vec3,               # linear velocity
        i_pos=gs.qd_vec3,             # inertia position
        i_quat=gs.qd_vec4,            # inertia orientation
        j_pos=gs.qd_vec3,             # joint frame position
        j_quat=gs.qd_vec4,            # joint frame orientation
        j_vel=gs.qd_vec3,             # joint linear velocity
        j_ang=gs.qd_vec3,             # joint angular velocity
        cd_ang=gs.qd_vec3,            # com-based velocity (angular)
        cd_vel=gs.qd_vec3,            # com-based velocity (linear)
        root_COM=gs.qd_vec3,          # center of mass of the root link's subtree
        mass_sum=gs.qd_float,         # total mass of the subtree rooted at this link
        mass_shift=gs.qd_float,       # mass shift
        i_pos_shift=gs.qd_vec3,       # inertia position shift
        cfrc_flat_ang=gs.qd_vec3,     # com-based interaction force (angular)
        cfrc_flat_vel=gs.qd_vec3,     # com-based interaction force (linear)
        cfrc_ext_ang=gs.qd_vec3,      # com-based external force (angular)
        cfrc_ext_vel=gs.qd_vec3,      # com-based external force (linear)
        contact_force=gs.qd_vec3,     # net contact force from environment
        hibernated=gs.qd_int,         # 1 if the link is in a hibernated/static state
    )
    ```

For joints,
* Dynamic DoF state (`dofs_state`)
    ```python
    qd.types.struct(
        force=gs.qd_float,            # total net force applied on this DoF after accumulation
        qf_bias=gs.qd_float,          #
        qf_passive=gs.qd_float,       # total passive forces
        qf_actuator=gs.qd_float,      # actuator force
        qf_applied=gs.qd_float,       #
        act_length=gs.qd_float,       #
        pos=gs.qd_float,              # position
        vel=gs.qd_float,              # velocity
        acc=gs.qd_float,              # acceleration
        acc_smooth=gs.qd_float,       #
        qf_smooth=gs.qd_float,        #
        qf_constraint=gs.qd_float,    # constraint force
        cdof_ang=gs.qd_vec3,          # com-based motion axis (angular)
        cdof_vel=gs.qd_vec3,          # com-based motion axis (linear)
        cdofvel_ang=gs.qd_vec3,       #
        cdofvel_vel=gs.qd_vec3,       #
        cdofd_ang=gs.qd_vec3,         # time-derivative of cdof (angular)
        cdofd_vel=gs.qd_vec3,         # time-derivative of cdof (linear)
        f_vel=gs.qd_vec3,             #
        f_ang=gs.qd_vec3,             #
        ctrl_force=gs.qd_float,       # target force from the controller
        ctrl_pos=gs.qd_float,         # target position from the controller
        ctrl_vel=gs.qd_float,         # target velocity from the controller
        ctrl_mode=gs.qd_int,          # control mode (e.g., position, velocity, torque)
        hibernated=gs.qd_int,         # indicate hibernation
    )
    ```
* Static DoF information (`dofs_info`)
    ```python
    qd.types.struct(
        stiffness=gs.qd_float,        # stiffness of the DoF
        sol_params=gs.qd_vec7,        # constraint solver
        invweight=gs.qd_float,        # inverse mass
        armature=gs.qd_float,         # dof armature inertia/mass
        damping=gs.qd_float,          # damping coefficient
        motion_ang=gs.qd_vec3,        # prescribed angular motion target
        motion_vel=gs.qd_vec3,        # prescribed linear motion target
        limit=gs.qd_vec2,             # lower and upper positional limits of the DoF
        dof_start=gs.qd_int,          # starting index of the DoF in the global system
        kp=gs.qd_float,               # proportional gain for PD control
        kv=gs.qd_float,               # derivative gain for PD control
        force_range=gs.qd_vec2,       # minimum and maximum allowed control force
    )
    ```
* Static joint information (`joints_info`)
    ```python
    qd.types.struct(
        type=gs.qd_int,               # joint type ID (e.g., revolute, prismatic, fixed)
        sol_params=gs.qd_vec7,        # constraint solver (reference; impedance)
        q_start=gs.qd_int,            # start index in global configuration vector (q)
        dof_start=gs.qd_int,          # start index in global DoF vector
        q_end=gs.qd_int,              # end index in global configuration vector
        dof_end=gs.qd_int,            # end index in global DoF vector
        n_dofs=gs.qd_int,             # number of DOFs for this joint
        pos=gs.qd_vec3,               # joint position in world space
    )
    ```

For geometries,
* Dynamic geometry state (`geom_state`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,               # current world position of the geometry
        quat=gs.qd_vec4,              # current world orientation (quaternion)
        vel=gs.qd_vec3,               # linear velocity of the geometry
        ang=gs.qd_vec3,               # angular velocity of the geometry
        aabb_min=gs.qd_vec3,          # minimum bound of the geometry's AABB (axis-aligned bounding box)
        aabb_max=gs.qd_vec3,          # maximum bound of the geometry's AABB
    )
    ```
* Static geometry information (`geom_info`)
    ```python
    qd.types.struct(
        link_idx=gs.qd_int,           # index of the link this geometry belongs to
        type=gs.qd_int,               # geometry type (e.g., box, sphere, mesh)
        local_pos=gs.qd_vec3,         # position in the link's local frame
        local_quat=gs.qd_vec4,        # orientation in the link's local frame
        size=gs.qd_vec3,              # dimensions or bounding volume
    )
    ```

<!-- TODO: verts -->
<!-- TODO: rendering stuffs -->

## MPM Solver

Material Point Method (MPM) uses particle- and grid-based representations.

For particles,
* Dynamic particle state (`particles_state`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,    # position
        vel=gs.qd_vec3,    # velocity
        C=gs.qd_mat3,      # affine velocity field
        F=gs.qd_mat3,      # deformation gradient
        F_tmp=gs.qd_mat3,  # temporary deformation gradient
        U=gs.qd_mat3,      # left orthonormal matrix in SVD (Singular Value Decomposition)
        V=gs.qd_mat3,      # right orthonormal matrix in SVD
        S=gs.qd_mat3,      # diagonal matrix in SVD
        actu=gs.qd_float,  # actuation
        Jp=gs.qd_float,    # volume ratio
    )
    ```
* Dynamic particle state without gradient (`particles_stage_ng`)
    ```python
    qd.types.struct(
        active=gs.qd_int,  # whether the particle is active or not
    )
    ```
* Static particle information (`particles_info`)
    ```python
    qd.types.struct(
        material_idx=gs.qd_int,       # material id
        mass=gs.qd_float,             # mass
        default_Jp=gs.qd_float,       # default volume ratio
        free=gs.qd_int,               # whether the particle is free; non-free particles behave as boundary conditions
        muscle_group=gs.qd_int,       # muscle/actuation group
        muscle_direction=gs.qd_vec3,  # muscle/actuation direction
    )
    ```

For grid,
* Dynamic grid state (`grid_state`)
    ```python
    qd.types.struct(
        vel_in=gs.qd_vec3,   # input momentum
        mass=gs.qd_float,    # mass
        vel_out=gs.qd_vec3,  # output velocity
    )
    ```

For rendering,
* Particle attributes for particle-based rendering (`particles_render`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```
* Static virtual vertex information for visual-based rendering (`vverts_info`)
    ```python
    qd.types.struct(
        support_idxs=qd.types.vector(n_vvert_supports, gs.qd_int),      # the indices of the supporting particles
        support_weights=qd.types.vector(n_vvert_supports, gs.qd_float), # the interpolation weights
    )
    ```
* Dynamic virtual vertex state for visual-based rendering (`vverts_render`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # the position of the virtual vertices
        active=gs.qd_int, # whether the virtual vertex is active
    )
    ```

Check [`genesis/solvers/mpm_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/mpm_solver.py) for more details.

## FEM Solver

Finite Element Method (FEM) uses element and surface representation, where some attributes in elements are stored in the associated vertices.

For elements,
* Dynamic element state in element (`elements_el_state`)
    ```python
    qd.types.struct(
        actu=gs.qd_float,  # actuation
    )
    ```
* Dynamic element state in vertex (`elements_v_state`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,  # position
        vel=gs.qd_vec3,  # velocity
    )
    ```
* Dynamic element state without gradient (`elements_el_state_ng`)
    ```python
    qd.types.struct(
        active=gs.qd_int,  # whether the element is actice
    )
    ```
* Static element information (`elements_el_info`)
    ```python
    qd.types.struct(
        el2v=gs.qd_ivec4,            # vertex index of an element
        mu=gs.qd_float,              # lame parameters (1)
        lam=gs.qd_float,             # lame parameters (2)
        mass_scaled=gs.qd_float,     # scaled element mass. The real mass is mass_scaled / self._vol_scale
        material_idx=gs.qd_int,      # material model index
        B=gs.qd_mat3,                # the inverse of the undeformed shape matrix
        muscle_group=gs.qd_int,      # muscle/actuator group
        muscle_direction=gs.qd_vec3, # muscle/actuator direction
    )
    ```

For surfaces,
* Static surface information (`surfaces_info`)
    ```python
    qd.types.struct(
        tri2v=gs.qd_ivec3,  # vertex index of a triangle
        tri2el=gs.qd_int,   # element index of a triangle
        active=gs.qd_int,   # whether this surface unit is active
    )
    ```

For rendering,
* Dynamic surface attribute in vertex (`surfaces_v_render`)
    ```python
    qd.types.struct(
        vertices=gs.qd_vec3, # position
    )
    ```
* Dynamic surface attribute in face (`surfaces_f_render`)
    ```python
    qd.types.struct(
        indices=gs.qd_int, # vertex indices corresponding to this surface unit (TODO: this is ugly as we flatten out (n_surfaces_max, 3))
    )
    ```

Check [`genesis/solvers/fem_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/fem_solver.py) for more details.


## PBD Solver

Position Based Dynamics (PBD) uses a particle-based representation.

For particles,
* Dynamic particle state (`particles_state`, `particles_state_reordered`)
    ```python
    qd.types.struct(
        free=gs.qd_int,  # whether the particle is free to move. If 0, it is kinematically controlled (e.g., fixed or externally manipulated)
        pos=gs.qd_vec3,  # position
        ipos=gs.qd_vec3, # initial position
        dpos=gs.qd_vec3, # delta position
        vel=gs.qd_vec3,  # velocity
        lam=gs.qd_float, # lagrange multiplier or constraint force scalar
        rho=gs.qd_float, # estimated fluid density
    )
    ```
* Dynamic particle state without gradient (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    qd.types.struct(
        reordered_idx=gs.qd_int, # reordering index
        active=gs.qd_int,        # whether the particle is active
    )
    ```
* Static particle information (`particles_info`, `particles_info_reordered`)
    ```python
    qd.types.struct(
        mass=gs.qd_float,                 # mass
        pos_rest=gs.qd_vec3,              # rest position
        rho_rest=gs.qd_float,             # rest density
        material_type=gs.qd_int,          # material type
        mu_s=gs.qd_float,                 # static friction coefficient
        mu_k=gs.qd_float,                 # dynamic friction coefficient
        air_resistance=gs.qd_float,       # coefficient of drag / damping due to air
        density_relaxation=gs.qd_float,   # parameter for density constraint solver
        viscosity_relaxation=gs.qd_float, # parameter for viscosity behavior
    )
    ```

For rendering,
* Particle attribute (`particles_render`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```

Check [`genesis/solvers/pbd_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/pbd_solver.py) for more details.

## SPH Solver

Smoothed Particle Hydrodynamics (SPH) uses a particle-based representation.

For particles,
* Dynamic particle state (`particles_state`, `particles_state_reordered`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,           # position
        vel=gs.qd_vec3,           # velocity
        acc=gs.qd_vec3,           # acceleration
        rho=gs.qd_float,          # density
        p=gs.qd_float,            # pressure
        dfsph_factor=gs.qd_float, # factor used in DFSPH pressure solve
        drho=gs.qd_float,         # density derivative (rate of change)
    )
    ```
* Dynamic particle state without gradient (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    qd.types.struct(
        reordered_idx=gs.qd_int, # reordering index
        active=gs.qd_int,        # whether the particle is active
    )
    ```
* Static particle information (`particles_info`, `particles_info_reordered`)
    ```python
    qd.types.struct(
        rho=gs.qd_float,       # rest density
        mass=gs.qd_float,      # particle mass
        stiffness=gs.qd_float, # equation-of-state stiffness
        exponent=gs.qd_float,  # equation-of-state exponent
        mu=gs.qd_float,        # viscosity coefficient
        gamma=gs.qd_float,     # surface tension coefficient
    )
    ```

For rendering,
* Particle attributes (`particles_render`)
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```

Check [`genesis/solvers/sph_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/sph_solver.py) for more details.

<!-- ## SF Solver -->
