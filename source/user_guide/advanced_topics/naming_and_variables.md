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
ti_vec2 = ti.types.vector(2, ti_float)
ti_vec3 = ti.types.vector(3, ti_float)
ti_vec4 = ti.types.vector(4, ti_float)
ti_vec6 = ti.types.vector(6, ti_float)
ti_vec7 = ti.types.vector(7, ti_float)
ti_vec11 = ti.types.vector(11, ti_float)

ti_mat3 = ti.types.matrix(3, 3, ti_float)
ti_mat4 = ti.types.matrix(4, 4, ti_float)

ti_ivec2 = ti.types.vector(2, ti_int)
ti_ivec3 = ti.types.vector(3, ti_int)
ti_ivec4 = ti.types.vector(4, ti_int)
```

In the following sections, we briefly describe the variables used by each solver.

## Rigid Solver

The rigid solver involves links, joints, geometry, and vertex representations. The rigid solver models articulated bodies composed of links and joints, with each link potentially consisting of multiple geometric components. Each geometry, in turn, may contain numerous vertices.

For links,
* Dynamic link state (`links_state`)
    ```python
    ti.types.struct(
        parent_idx=gs.ti_int,         # index of the parent link in the kinematic tree (-1 if root)
        root_idx=gs.ti_int,           # index of the root link in the articulation
        q_start=gs.ti_int,            # start index in the global configuration vector (q)
        dof_start=gs.ti_int,          # start index in the global DoF vector
        joint_start=gs.ti_int,        # start index for joints affecting this link
        q_end=gs.ti_int,              # end index in the global configuration vector
        dof_end=gs.ti_int,            # end index in the global DoF vector
        joint_end=gs.ti_int,          # end index for joints affecting this link
        n_dofs=gs.ti_int,             # number of degrees of freedom for this link
        pos=gs.ti_vec3,               # current world-space position of the link
        quat=gs.ti_vec4,              # current world-space orientation (quaternion)
        invweight=gs.ti_vec2,         # inverse mass
        is_fixed=gs.ti_int,           # boolean flag: 1 if link is fixed/static, 0 if dynamic
        inertial_pos=gs.ti_vec3,      # position of the inertial frame (CoM) in link-local coordinates
        inertial_quat=gs.ti_vec4,     # orientation of the inertial frame relative to the link frame
        inertial_i=gs.ti_mat3,        # inertia tensor in the inertial frame
        inertial_mass=gs.ti_float,    # mass of the link
        entity_idx=gs.ti_int,         # index of the entity this link belongs to
    )
    ```
* Static link information (`links_info`)
    ```python
    ti.types.struct(
        cinr_inertial=gs.ti_mat3,     # com-based body inertia
        cinr_pos=gs.ti_vec3,          # com-based body position
        cinr_quat=gs.ti_vec4,         # com-based body orientation
        cinr_mass=gs.ti_float,        # com-based body mass
        crb_inertial=gs.ti_mat3,      # com-based composite inertia
        crb_pos=gs.ti_vec3,           # com-based composite position
        crb_quat=gs.ti_vec4,          # com-based composite orientation
        crb_mass=gs.ti_float,         # com-based composite mass
        cdd_vel=gs.ti_vec3,           # com-based acceleration (linear)
        cdd_ang=gs.ti_vec3,           # com-based acceleration (angular)
        pos=gs.ti_vec3,               # current world position
        quat=gs.ti_vec4,              # current orientation
        ang=gs.ti_vec3,               # angular velocity
        vel=gs.ti_vec3,               # linear velocity
        i_pos=gs.ti_vec3,             # inertia position
        i_quat=gs.ti_vec4,            # inertia orientation
        j_pos=gs.ti_vec3,             # joint frame position
        j_quat=gs.ti_vec4,            # joint frame orientation
        j_vel=gs.ti_vec3,             # joint linear velocity
        j_ang=gs.ti_vec3,             # joint angular velocity
        cd_ang=gs.ti_vec3,            # com-based velocity (angular)
        cd_vel=gs.ti_vec3,            # com-based velocity (linear)
        root_COM=gs.ti_vec3,          # center of mass of the root link's subtree
        mass_sum=gs.ti_float,         # total mass of the subtree rooted at this link
        mass_shift=gs.ti_float,       # mass shift
        i_pos_shift=gs.ti_vec3,       # inertia position shift
        cfrc_flat_ang=gs.ti_vec3,     # com-based interaction force (angular)
        cfrc_flat_vel=gs.ti_vec3,     # com-based interaction force (linear)
        cfrc_ext_ang=gs.ti_vec3,      # com-based external force (angular)
        cfrc_ext_vel=gs.ti_vec3,      # com-based external force (linear)
        contact_force=gs.ti_vec3,     # net contact force from environment
        hibernated=gs.ti_int,         # 1 if the link is in a hibernated/static state
    )
    ```

For joints,
* Dynamic DoF state (`dofs_state`)
    ```python
    ti.types.struct(
        force=gs.ti_float,            # total net force applied on this DoF after accumulation
        qf_bias=gs.ti_float,          # 
        qf_passive=gs.ti_float,       # total passive forces
        qf_actuator=gs.ti_float,      # actuator force
        qf_applied=gs.ti_float,       # 
        act_length=gs.ti_float,       # 
        pos=gs.ti_float,              # position
        vel=gs.ti_float,              # velocity
        acc=gs.ti_float,              # acceleration
        acc_smooth=gs.ti_float,       # 
        qf_smooth=gs.ti_float,        # 
        qf_constraint=gs.ti_float,    # constraint force
        cdof_ang=gs.ti_vec3,          # com-based motion axis (angular)
        cdof_vel=gs.ti_vec3,          # com-based motion axis (linear)
        cdofvel_ang=gs.ti_vec3,       # 
        cdofvel_vel=gs.ti_vec3,       # 
        cdofd_ang=gs.ti_vec3,         # time-derivative of cdof (angular)
        cdofd_vel=gs.ti_vec3,         # time-derivative of cdof (linear)
        f_vel=gs.ti_vec3,             # 
        f_ang=gs.ti_vec3,             # 
        ctrl_force=gs.ti_float,       # target force from the controller
        ctrl_pos=gs.ti_float,         # target position from the controller
        ctrl_vel=gs.ti_float,         # target velocity from the controller
        ctrl_mode=gs.ti_int,          # control mode (e.g., position, velocity, torque)
        hibernated=gs.ti_int,         # indicate hibernation
    )
    ```
* Static DoF information (`dofs_info`)
    ```python
    ti.types.struct(
        stiffness=gs.ti_float,        # stiffness of the DoF
        sol_params=gs.ti_vec7,        # constraint solver ()
        invweight=gs.ti_float,        # inverse mass
        armature=gs.ti_float,         # dof armature inertia/mass 
        damping=gs.ti_float,          # damping coefficient
        motion_ang=gs.ti_vec3,        # prescribed angular motion target
        motion_vel=gs.ti_vec3,        # prescribed linear motion target
        limit=gs.ti_vec2,             # lower and upper positional limits of the DoF
        dof_start=gs.ti_int,          # starting index of the DoF in the global system
        kp=gs.ti_float,               # proportional gain for PD control
        kv=gs.ti_float,               # derivative gain for PD control
        force_range=gs.ti_vec2,       # minimum and maximum allowed control force
    )
    ```
* Static joint information (`joints_info`)
    ```python
    ti.types.struct(
        type=gs.ti_int,               # joint type ID (e.g., revolute, prismatic, fixed)
        sol_params=gs.ti_vec7,        # constraint solver (reference; impedance)
        q_start=gs.ti_int,            # start index in global configuration vector (q)
        dof_start=gs.ti_int,          # start index in global DoF vector
        q_end=gs.ti_int,              # end index in global configuration vector
        dof_end=gs.ti_int,            # end index in global DoF vector
        n_dofs=gs.ti_int,             # number of DOFs for this joint
        pos=gs.ti_vec3,               # joint position in world space
    )
    ```

For geometries,
* Dynamic geometry state (`geom_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,               # current world position of the geometry
        quat=gs.ti_vec4,              # current world orientation (quaternion)
        vel=gs.ti_vec3,               # linear velocity of the geometry
        ang=gs.ti_vec3,               # angular velocity of the geometry
        aabb_min=gs.ti_vec3,          # minimum bound of the geometry's AABB (axis-aligned bounding box)
        aabb_max=gs.ti_vec3,          # maximum bound of the geometry's AABB
    )
    ```
* Static geometry information (`geom_info`)
    ```python
    ti.types.struct(
        link_idx=gs.ti_int,           # index of the link this geometry belongs to
        type=gs.ti_int,               # geometry type (e.g., box, sphere, mesh)
        local_pos=gs.ti_vec3,         # position in the link's local frame
        local_quat=gs.ti_vec4,        # orientation in the link's local frame
        size=gs.ti_vec3,              # dimensions or bounding volume
    )
    ```

<!-- TODO: verts -->
<!-- TODO: rendering stuffs -->

## MPM Solver

Material Point Method (MPM) uses particle- and grid-based representations. 

For particles,
* Dynamic particle state (`particles_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,    # position
        vel=gs.ti_vec3,    # velocity
        C=gs.ti_mat3,      # affine velocity field
        F=gs.ti_mat3,      # deformation gradient
        F_tmp=gs.ti_mat3,  # temporary deformation gradient
        U=gs.ti_mat3,      # left orthonormal matrix in SVD (Singular Value Decomposition)
        V=gs.ti_mat3,      # right orthonormal matrix in SVD
        S=gs.ti_mat3,      # diagonal matrix in SVD
        actu=gs.ti_float,  # actuation
        Jp=gs.ti_float,    # volume ratio
    )
    ```
* Dynamic particle state without gradient (`particles_stage_ng`)
    ```python
    ti.types.struct(
        active=gs.ti_int,  # whether the particle is active or not
    )
    ```
* Static particle information (`particles_info`)
    ```python
    ti.types.struct(
        material_idx=gs.ti_int,       # material id
        mass=gs.ti_float,             # mass
        default_Jp=gs.ti_float,       # default volume ratio
        free=gs.ti_int,               # whether the particle is free; non-free particles behave as boundary conditions
        muscle_group=gs.ti_int,       # muscle/actuation group
        muscle_direction=gs.ti_vec3,  # muscle/actuation direction
    )
    ```

For grid,
* Dynamic grid state (`grid_state`)
    ```python
    ti.types.struct(
        vel_in=gs.ti_vec3,   # input momentum
        mass=gs.ti_float,    # mass
        vel_out=gs.ti_vec3,  # output velocity
    )
    ```

For rendering,
* Particle attributes for particle-based rendering (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # position
        vel=gs.ti_vec3,   # velocity
        active=gs.ti_int, # whether the particle is active
    )
    ```
* Static virtual vertex information for visual-based rendering (`vverts_info`)
    ```python
    ti.types.struct(
        support_idxs=ti.types.vector(n_vvert_supports, gs.ti_int),      # the indices of the supporting particles
        support_weights=ti.types.vector(n_vvert_supports, gs.ti_float), # the interpolation weights
    )
    ```
* Dynamic virtual vertex state for visual-based rendering (`vverts_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # the position of the virtual vertices
        active=gs.ti_int, # whether the virtual vertex is active
    )
    ```

Check [`genesis/solvers/mpm_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/mpm_solver.py) for more details.

## FEM Solver

Finite Element Method (FEM) uses element and surface representation, where some attributes in elements are stored in the associated vertices.

For elements,
* Dynamic element state in element (`elements_el_state`)
    ```python
    ti.types.struct(
        actu=gs.ti_float,  # actuation
    )
    ```
* Dynamic element state in vertex (`elements_v_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,  # position
        vel=gs.ti_vec3,  # velocity
    )
    ```
* Dynamic element state without gradient (`elements_el_state_ng`)
    ```python
    ti.types.struct(
        active=gs.ti_int,  # whether the element is actice
    )
    ```
* Static element information (`elements_el_info`)
    ```python
    ti.types.struct(
        el2v=gs.ti_ivec4,            # vertex index of an element
        mu=gs.ti_float,              # lame parameters (1)
        lam=gs.ti_float,             # lame parameters (2)
        mass_scaled=gs.ti_float,     # scaled element mass. The real mass is mass_scaled / self._vol_scale
        material_idx=gs.ti_int,      # material model index
        B=gs.ti_mat3,                # the inverse of the undeformed shape matrix
        muscle_group=gs.ti_int,      # muscle/actuator group
        muscle_direction=gs.ti_vec3, # muscle/actuator direction
    )
    ```

For surfaces,
* Static surface information (`surfaces_info`)
    ```python
    ti.types.struct(
        tri2v=gs.ti_ivec3,  # vertex index of a triangle
        tri2el=gs.ti_int,   # element index of a triangle
        active=gs.ti_int,   # whether this surface unit is active
    )
    ```

For rendering,
* Dynamic surface attribute in vertex (`surfaces_v_render`)
    ```python
    ti.types.struct(
        vertices=gs.ti_vec3, # position
    )
    ```
* Dynamic surface attribute in face (`surfaces_f_render`)
    ```python
    ti.types.struct(
        indices=gs.ti_int, # vertex indices corresponding to this surface unit (TODO: this is ugly as we flatten out (n_surfaces_max, 3))
    )
    ```

Check [`genesis/solvers/fem_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/fem_solver.py) for more details.


## PBD Solver

Position Based Dynamics (PBD) uses a particle-based representation.

For particles,
* Dynamic particle state (`particles_state`, `particles_state_reordered`)
    ```python
    ti.types.struct(
        free=gs.ti_int,  # whether the particle is free to move. If 0, it is kinematically controlled (e.g., fixed or externally manipulated)
        pos=gs.ti_vec3,  # position
        ipos=gs.ti_vec3, # initial position
        dpos=gs.ti_vec3, # delta position
        vel=gs.ti_vec3,  # velocity
        lam=gs.ti_float, # lagrange multiplier or constraint force scalar
        rho=gs.ti_float, # estimated fluid density
    )
    ```
* Dynamic particle state without gradient (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    ti.types.struct(
        reordered_idx=gs.ti_int, # reordering index
        active=gs.ti_int,        # whether the particle is active
    )
    ```
* Static particle information (`particles_info`, `particles_info_reordered`)
    ```python
    ti.types.struct(
        mass=gs.ti_float,                 # mass
        pos_rest=gs.ti_vec3,              # rest position
        rho_rest=gs.ti_float,             # rest density
        material_type=gs.ti_int,          # material type
        mu_s=gs.ti_float,                 # static friction coefficient
        mu_k=gs.ti_float,                 # dynamic friction coefficient
        air_resistance=gs.ti_float,       # coefficient of drag / damping due to air
        density_relaxation=gs.ti_float,   # parameter for density constraint solver
        viscosity_relaxation=gs.ti_float, # parameter for viscosity behavior
    )
    ```

For rendering,
* Particle attribute (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # position
        vel=gs.ti_vec3,   # velocity
        active=gs.ti_int, # whether the particle is active
    )
    ```

Check [`genesis/solvers/pbd_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/pbd_solver.py) for more details.

## SPH Solver

Smoothed Particle Hydrodynamics (SPH) uses a particle-based representation.

For particles,
* Dynamic particle state (`particles_state`, `particles_state_reordered`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,           # position
        vel=gs.ti_vec3,           # velocity
        acc=gs.ti_vec3,           # acceleration
        rho=gs.ti_float,          # density
        p=gs.ti_float,            # pressure
        dfsph_factor=gs.ti_float, # factor used in DFSPH pressure solve
        drho=gs.ti_float,         # density derivative (rate of change)
    )
    ```
* Dynamic particle state without gradient (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    ti.types.struct(
        reordered_idx=gs.ti_int, # reordering index 
        active=gs.ti_int,        # whether the particle is active
    )
    ```
* Static particle information (`particles_info`, `particles_info_reordered`)
    ```python
    ti.types.struct(
        rho=gs.ti_float,       # rest density
        mass=gs.ti_float,      # particle mass
        stiffness=gs.ti_float, # equation-of-state stiffness
        exponent=gs.ti_float,  # equation-of-state exponent
        mu=gs.ti_float,        # viscosity coefficient
        gamma=gs.ti_float,     # surface tension coefficient
    )
    ```

For rendering,
* Particle attributes (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # position
        vel=gs.ti_vec3,   # velocity
        active=gs.ti_int, # whether the particle is active
    )
    ```

Check [`genesis/solvers/sph_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/sph_solver.py) for more details.

<!-- ## SF Solver -->
