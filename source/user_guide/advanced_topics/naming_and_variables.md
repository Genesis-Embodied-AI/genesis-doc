# 📃 命名規則と変数

各ソルバーは、粒子・要素・グリッド・サーフェスなど異なる表現で物理エンティティを扱います。各データフィールドには対応する表現に応じた接頭辞が付きます。計算効率と構造化のため、物理属性に対応するデータフィールドは（計算種別に応じて）次のカテゴリに整理されています。
- `*_state_*`: 各ソルバーステップで更新される動的状態。通常は `requires_grad=True` で生成されます。フィールドサイズは、微分可能時は（サブステップ数, 単位数）、非微分時は（単位数）です。単位は粒子・頂点など表現依存です。さらに次のような接尾辞を持つ場合があります。
    - `*_state_ng`: `requires_gradient` を False に設定。
- `*_info`: シミュレーション中に不変な静的属性。質量、剛性、粘性などの物理パラメータを含みます。フィールドサイズは（単位数）。
- `*_render`: 可視化専用で、物理計算には直接関与しないフィールド。フィールドサイズは（単位数）。
<!-- Note that there may be both static and dynamic attributes for rendering, resulting in `*_state_render` and `*_info_render`. -->
<!-- より詳細な指定として、次のような接尾辞を使う場合があります。
- `*_state_ng`: `requires_gradient` を False に設定。
- `*_state_reordered`: 並べ替え済みキャッシュデータ。 -->

命名は基本的に `<representation>_<computation-type>` に従います。（`dofs`, `particles`, `elements` など、representation は常に複数形 `s` 付きです。）

また、便利な汎用データ型（定義: [genesis/\_\_init\_\_.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/__init__.py)）を示します。
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

以下では、各ソルバーで使われる変数を簡潔に説明します。

## Rigid ソルバー

Rigid ソルバーでは、リンク・関節・ジオメトリ・頂点の表現を扱います。リンクと関節で構成されるアーティキュレート剛体をモデル化し、各リンクは複数ジオメトリを持つことがあり、各ジオメトリは多数の頂点を持ち得ます。

リンクについて:
* 動的リンク状態（`links_state`）
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
* 静的リンク情報（`links_info`）
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

関節について:
* 動的 DoF 状態（`dofs_state`）
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
* 静的 DoF 情報（`dofs_info`）
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
* 静的関節情報（`joints_info`）
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

ジオメトリについて:
* 動的ジオメトリ状態（`geom_state`）
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
* 静的ジオメトリ情報（`geom_info`）
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

## MPM ソルバー

Material Point Method（MPM）は、粒子表現とグリッド表現を使用します。

粒子について:
* 動的粒子状態（`particles_state`）
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
* 勾配なし動的粒子状態（`particles_stage_ng`）
    ```python
    qd.types.struct(
        active=gs.qd_int,  # whether the particle is active or not
    )
    ```
* 静的粒子情報（`particles_info`）
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

グリッドについて:
* 動的グリッド状態（`grid_state`）
    ```python
    qd.types.struct(
        vel_in=gs.qd_vec3,   # input momentum
        mass=gs.qd_float,    # mass
        vel_out=gs.qd_vec3,  # output velocity
    )
    ```

レンダリングについて:
* 粒子ベース描画用の粒子属性（`particles_render`）
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```
* 可視化用仮想頂点の静的情報（`vverts_info`）
    ```python
    qd.types.struct(
        support_idxs=qd.types.vector(n_vvert_supports, gs.qd_int),      # the indices of the supporting particles
        support_weights=qd.types.vector(n_vvert_supports, gs.qd_float), # the interpolation weights
    )
    ```
* 可視化用仮想頂点の動的状態（`vverts_render`）
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # the position of the virtual vertices
        active=gs.qd_int, # whether the virtual vertex is active
    )
    ```

詳細は [`genesis/solvers/mpm_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/mpm_solver.py) を参照してください。

## FEM ソルバー

Finite Element Method（FEM）は、要素表現とサーフェス表現を使用します。要素に属する属性の一部は対応頂点側に保存されます。

要素について:
* 要素側の動的要素状態（`elements_el_state`）
    ```python
    qd.types.struct(
        actu=gs.qd_float,  # actuation
    )
    ```
* 頂点側の動的要素状態（`elements_v_state`）
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,  # position
        vel=gs.qd_vec3,  # velocity
    )
    ```
* 勾配なし動的要素状態（`elements_el_state_ng`）
    ```python
    qd.types.struct(
        active=gs.qd_int,  # whether the element is actice
    )
    ```
* 静的要素情報（`elements_el_info`）
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

サーフェスについて:
* 静的サーフェス情報（`surfaces_info`）
    ```python
    qd.types.struct(
        tri2v=gs.qd_ivec3,  # vertex index of a triangle
        tri2el=gs.qd_int,   # element index of a triangle
        active=gs.qd_int,   # whether this surface unit is active
    )
    ```

レンダリングについて:
* 頂点側の動的サーフェス属性（`surfaces_v_render`）
    ```python
    qd.types.struct(
        vertices=gs.qd_vec3, # position
    )
    ```
* 面側の動的サーフェス属性（`surfaces_f_render`）
    ```python
    qd.types.struct(
        indices=gs.qd_int, # vertex indices corresponding to this surface unit (TODO: this is ugly as we flatten out (n_surfaces_max, 3))
    )
    ```

詳細は [`genesis/solvers/fem_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/fem_solver.py) を参照してください。


## PBD ソルバー

Position Based Dynamics（PBD）は粒子ベース表現を使用します。

粒子について:
* 動的粒子状態（`particles_state`, `particles_state_reordered`）
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
* 勾配なし動的粒子状態（`particles_state_ng`, `particles_state_ng_reordered`）
    ```python
    qd.types.struct(
        reordered_idx=gs.qd_int, # reordering index
        active=gs.qd_int,        # whether the particle is active
    )
    ```
* 静的粒子情報（`particles_info`, `particles_info_reordered`）
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

レンダリングについて:
* 粒子属性（`particles_render`）
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```

詳細は [`genesis/solvers/pbd_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/pbd_solver.py) を参照してください。

## SPH ソルバー

Smoothed Particle Hydrodynamics（SPH）は粒子ベース表現を使用します。

粒子について:
* 動的粒子状態（`particles_state`, `particles_state_reordered`）
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
* 勾配なし動的粒子状態（`particles_state_ng`, `particles_state_ng_reordered`）
    ```python
    qd.types.struct(
        reordered_idx=gs.qd_int, # reordering index
        active=gs.qd_int,        # whether the particle is active
    )
    ```
* 静的粒子情報（`particles_info`, `particles_info_reordered`）
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

レンダリングについて:
* 粒子属性（`particles_render`）
    ```python
    qd.types.struct(
        pos=gs.qd_vec3,   # position
        vel=gs.qd_vec3,   # velocity
        active=gs.qd_int, # whether the particle is active
    )
    ```

詳細は [`genesis/solvers/sph_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/sph_solver.py) を参照してください。

<!-- ## SF Solver -->
