# 📃 命名与变量

不同的求解器使用各种格式表示物理实体，例如粒子、单元、网格和表面。每个数据字段都根据其对应的表示方式进行前缀标记。为了计算效率和结构，与不同物理属性相关的数据字段被组织成以下类别（基于计算类型）：
- `*_state_*`：在每个求解器步骤中更新的动态状态。这些字段默认启用 `requires_grad` 实例化。其字段大小为：如果可微分，则是（子步数，单元数）；如果不可微分，则是（单元数），其中单元取决于表示方式，如粒子、顶点等。可能有不同的后缀用于进一步指定，例如：
    - `*_state_ng`：将 `requires_gradient` 设置为 False。
- `*_info`：在整个模拟过程中保持不变的静态属性，通常涵盖物理属性，如质量、刚度、粘度等。其字段大小为（单元数，）
- `*_render`：仅用于可视化的字段，不直接参与物理计算。其字段大小为（单元数，）。
<!-- 注意，渲染可能有静态和动态属性，从而产生 `*_state_render` 和 `*_info_render`。 -->
<!-- 可能有不同的后缀用于进一步指定，例如：
    - `*_state_ng`：将 `requires_gradient` 设置为 False。
    - `*_state_reordered`：带有重新排序的缓存数据。 -->

总体而言，命名遵循 `<representation>_<computation-type>`。（我们始终使用复数形式，例如 `dofs`、`particles`、`elements` 等。）

此外，一些有用的通用数据类型（定义在 [genesis/\_\_init\_\_.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/__init__.py)）：
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

在以下章节中，我们简要描述每个求解器使用的变量。

## 刚体求解器 (Rigid Solver)

刚体求解器涉及连杆、关节、几何体和顶点表示。刚体求解器模拟由连杆和关节组成的关节体，每个连杆可能由多个几何组件组成。每个几何体又可能包含多个顶点。

对于连杆 (links)：
* 动态连杆状态 (`links_state`)
    ```python
    ti.types.struct(
        parent_idx=gs.ti_int,         # 运动树中父连杆的索引（如果是根则为 -1）
        root_idx=gs.ti_int,           # 关节中根连杆的索引
        q_start=gs.ti_int,            # 全局配置向量 (q) 中的起始索引
        dof_start=gs.ti_int,          # 全局自由度向量中的起始索引
        joint_start=gs.ti_int,        # 影响此连杆的关节的起始索引
        q_end=gs.ti_int,              # 全局配置向量中的结束索引
        dof_end=gs.ti_int,            # 全局自由度向量中的结束索引
        joint_end=gs.ti_int,          # 影响此连杆的关节的结束索引
        n_dofs=gs.ti_int,             # 此连杆的自由度数量
        pos=gs.ti_vec3,               # 连杆当前的世界空间位置
        quat=gs.ti_vec4,              # 连杆当前的世界空间方向（四元数）
        invweight=gs.ti_vec2,         # 逆质量
        is_fixed=gs.ti_int,           # 布尔标志：如果连杆固定/静态则为 1，动态则为 0
        inertial_pos=gs.ti_vec3,      # 惯性坐标系（质心）在连杆局部坐标中的位置
        inertial_quat=gs.ti_vec4,     # 惯性坐标系相对于连杆坐标系的方向
        inertial_i=gs.ti_mat3,        # 惯性坐标系中的惯性张量
        inertial_mass=gs.ti_float,    # 连杆的质量
        entity_idx=gs.ti_int,         # 此连杆所属实体的索引
    )
    ```
* 静态连杆信息 (`links_info`)
    ```python
    ti.types.struct(
        cinr_inertial=gs.ti_mat3,     # 基于质心的体惯性
        cinr_pos=gs.ti_vec3,          # 基于质心的体位置
        cinr_quat=gs.ti_vec4,         # 基于质心的体方向
        cinr_mass=gs.ti_float,        # 基于质心的体质量
        crb_inertial=gs.ti_mat3,      # 基于质心的复合惯性
        crb_pos=gs.ti_vec3,           # 基于质心的复合位置
        crb_quat=gs.ti_vec4,          # 基于质心的复合方向
        crb_mass=gs.ti_float,         # 基于质心的复合质量
        cdd_vel=gs.ti_vec3,           # 基于质心的加速度（线性）
        cdd_ang=gs.ti_vec3,           # 基于质心的加速度（角）
        pos=gs.ti_vec3,               # 当前世界位置
        quat=gs.ti_vec4,              # 当前方向
        ang=gs.ti_vec3,               # 角速度
        vel=gs.ti_vec3,               # 线速度
        i_pos=gs.ti_vec3,             # 惯性位置
        i_quat=gs.ti_vec4,            # 惯性方向
        j_pos=gs.ti_vec3,             # 关节坐标系位置
        j_quat=gs.ti_vec4,            # 关节坐标系方向
        j_vel=gs.ti_vec3,             # 关节线速度
        j_ang=gs.ti_vec3,             # 关节角速度
        cd_ang=gs.ti_vec3,            # 基于质心的速度（角）
        cd_vel=gs.ti_vec3,            # 基于质心的速度（线性）
        root_COM=gs.ti_vec3,          # 根连杆子树的质心
        mass_sum=gs.ti_float,         # 以此连杆为根的子树的总质量
        mass_shift=gs.ti_float,       # 质量偏移
        i_pos_shift=gs.ti_vec3,       # 惯性位置偏移
        cfrc_flat_ang=gs.ti_vec3,     # 基于质心的相互作用力（角）
        cfrc_flat_vel=gs.ti_vec3,     # 基于质心的相互作用力（线性）
        cfrc_ext_ang=gs.ti_vec3,      # 基于质心的外力（角）
        cfrc_ext_vel=gs.ti_vec3,      # 基于质心的外力（线性）
        contact_force=gs.ti_vec3,     # 来自环境的净接触力
        hibernated=gs.ti_int,         # 如果连杆处于休眠/静态状态则为 1
    )
    ```

对于关节 (joints)：
* 动态自由度状态 (`dofs_state`)
    ```python
    ti.types.struct(
        force=gs.ti_float,            # 累积后应用于此自由度的总净力
        qf_bias=gs.ti_float,          # 
        qf_passive=gs.ti_float,       # 总被动力
        qf_actuator=gs.ti_float,      # 执行器力
        qf_applied=gs.ti_float,       # 
        act_length=gs.ti_float,       # 
        pos=gs.ti_float,              # 位置
        vel=gs.ti_float,              # 速度
        acc=gs.ti_float,              # 加速度
        acc_smooth=gs.ti_float,       # 
        qf_smooth=gs.ti_float,        # 
        qf_constraint=gs.ti_float,    # 约束力
        cdof_ang=gs.ti_vec3,          # 基于质心的运动轴（角）
        cdof_vel=gs.ti_vec3,          # 基于质心的运动轴（线性）
        cdofvel_ang=gs.ti_vec3,       # 
        cdofvel_vel=gs.ti_vec3,       # 
        cdofd_ang=gs.ti_vec3,         # cdof 的时间导数（角）
        cdofd_vel=gs.ti_vec3,         # cdof 的时间导数（线性）
        f_vel=gs.ti_vec3,             # 
        f_ang=gs.ti_vec3,             # 
        ctrl_force=gs.ti_float,       # 控制器的目标力
        ctrl_pos=gs.ti_float,         # 控制器的目标位置
        ctrl_vel=gs.ti_float,         # 控制器的目标速度
        ctrl_mode=gs.ti_int,          # 控制模式（例如位置、速度、扭矩）
        hibernated=gs.ti_int,         # 指示休眠状态
    )
    ```
* 静态自由度信息 (`dofs_info`)
    ```python
    ti.types.struct(
        stiffness=gs.ti_float,        # 自由度的刚度
        sol_params=gs.ti_vec7,        # 约束求解器
        invweight=gs.ti_float,        # 逆质量
        armature=gs.ti_float,         # 自由度电枢惯性/质量 
        damping=gs.ti_float,          # 阻尼系数
        motion_ang=gs.ti_vec3,        # 规定的角运动目标
        motion_vel=gs.ti_vec3,        # 规定的线运动目标
        limit=gs.ti_vec2,             # 自由度的位置下限和上限
        dof_start=gs.ti_int,          # 自由度在全局系统中的起始索引
        kp=gs.ti_float,               # PD 控制的比例增益
        kv=gs.ti_float,               # PD 控制的微分增益
        force_range=gs.ti_vec2,       # 允许的最小和最大控制力
    )
    ```
* 静态关节信息 (`joints_info`)
    ```python
    ti.types.struct(
        type=gs.ti_int,               # 关节类型 ID（例如旋转、平移、固定）
        sol_params=gs.ti_vec7,        # 约束求解器（参考；阻抗）
        q_start=gs.ti_int,            # 全局配置向量 (q) 中的起始索引
        dof_start=gs.ti_int,          # 全局自由度向量中的起始索引
        q_end=gs.ti_int,              # 全局配置向量中的结束索引
        dof_end=gs.ti_int,            # 全局自由度向量中的结束索引
        n_dofs=gs.ti_int,             # 此关节的自由度数量
        pos=gs.ti_vec3,               # 关节在世界空间中的位置
    )
    ```

对于几何体 (geometries)：
* 动态几何体状态 (`geom_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,               # 几何体的当前世界位置
        quat=gs.ti_vec4,              # 几何体的当前世界方向（四元数）
        vel=gs.ti_vec3,               # 几何体的线速度
        ang=gs.ti_vec3,               # 几何体的角速度
        aabb_min=gs.ti_vec3,          # 几何体 AABB（轴对齐边界框）的最小边界
        aabb_max=gs.ti_vec3,          # 几何体 AABB 的最大边界
    )
    ```
* 静态几何体信息 (`geom_info`)
    ```python
    ti.types.struct(
        link_idx=gs.ti_int,           # 此几何体所属连杆的索引
        type=gs.ti_int,               # 几何体类型（例如盒体、球体、网格）
        local_pos=gs.ti_vec3,         # 连杆局部坐标系中的位置
        local_quat=gs.ti_vec4,        # 连杆局部坐标系中的方向
        size=gs.ti_vec3,              # 尺寸或包围体
    )
    ```

<!-- TODO: verts -->
<!-- TODO: rendering stuffs -->

## MPM 求解器 (MPM Solver)

物质点法 (MPM) 使用粒子和网格表示。

对于粒子 (particles)：
* 动态粒子状态 (`particles_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,    # 位置
        vel=gs.ti_vec3,    # 速度
        C=gs.ti_mat3,      # 仿射速度场
        F=gs.ti_mat3,      # 变形梯度
        F_tmp=gs.ti_mat3,  # 临时变形梯度
        U=gs.ti_mat3,      # SVD（奇异值分解）中的左正交矩阵
        V=gs.ti_mat3,      # SVD 中的右正交矩阵
        S=gs.ti_mat3,      # SVD 中的对角矩阵
        actu=gs.ti_float,  # 驱动
        Jp=gs.ti_float,    # 体积比
    )
    ```
* 无梯度的动态粒子状态 (`particles_stage_ng`)
    ```python
    ti.types.struct(
        active=gs.ti_int,  # 粒子是否激活
    )
    ```
* 静态粒子信息 (`particles_info`)
    ```python
    ti.types.struct(
        material_idx=gs.ti_int,       # 材料 id
        mass=gs.ti_float,             # 质量
        default_Jp=gs.ti_float,       # 默认体积比
        free=gs.ti_int,               # 粒子是否自由；非自由粒子表现为边界条件
        muscle_group=gs.ti_int,       # 肌肉/驱动组
        muscle_direction=gs.ti_vec3,  # 肌肉/驱动方向
    )
    ```

对于网格 (grid)：
* 动态网格状态 (`grid_state`)
    ```python
    ti.types.struct(
        vel_in=gs.ti_vec3,   # 输入动量
        mass=gs.ti_float,    # 质量
        vel_out=gs.ti_vec3,  # 输出速度
    )
    ```

对于渲染 (rendering)：
* 基于粒子的渲染的粒子属性 (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # 位置
        vel=gs.ti_vec3,   # 速度
        active=gs.ti_int, # 粒子是否激活
    )
    ```
* 基于视觉渲染的静态虚拟顶点信息 (`vverts_info`)
    ```python
    ti.types.struct(
        support_idxs=ti.types.vector(n_vvert_supports, gs.ti_int),      # 支撑粒子的索引
        support_weights=ti.types.vector(n_vvert_supports, gs.ti_float), # 插值权重
    )
    ```
* 基于视觉渲染的动态虚拟顶点状态 (`vverts_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # 虚拟顶点的位置
        active=gs.ti_int, # 虚拟顶点是否激活
    )
    ```

查看 [`genesis/solvers/mpm_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/mpm_solver.py) 获取更多详情。

## FEM 求解器 (FEM Solver)

有限元法 (FEM) 使用单元和表面表示，其中单元中的一些属性存储在相关顶点中。

对于单元 (elements)：
* 单元中的动态单元状态 (`elements_el_state`)
    ```python
    ti.types.struct(
        actu=gs.ti_float,  # 驱动
    )
    ```
* 顶点中的动态单元状态 (`elements_v_state`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,  # 位置
        vel=gs.ti_vec3,  # 速度
    )
    ```
* 无梯度的动态单元状态 (`elements_el_state_ng`)
    ```python
    ti.types.struct(
        active=gs.ti_int,  # 单元是否激活
    )
    ```
* 静态单元信息 (`elements_el_info`)
    ```python
    ti.types.struct(
        el2v=gs.ti_ivec4,            # 单元的顶点索引
        mu=gs.ti_float,              # Lame 参数 (1)
        lam=gs.ti_float,             # Lame 参数 (2)
        mass_scaled=gs.ti_float,     # 缩放后的单元质量。实际质量为 mass_scaled / self._vol_scale
        material_idx=gs.ti_int,      # 材料模型索引
        B=gs.ti_mat3,                # 未变形形状矩阵的逆
        muscle_group=gs.ti_int,      # 肌肉/执行器组
        muscle_direction=gs.ti_vec3, # 肌肉/执行器方向
    )
    ```

对于表面 (surfaces)：
* 静态表面信息 (`surfaces_info`)
    ```python
    ti.types.struct(
        tri2v=gs.ti_ivec3,  # 三角形的顶点索引
        tri2el=gs.ti_int,   # 三角形的单元索引
        active=gs.ti_int,   # 此表面单元是否激活
    )
    ```

对于渲染 (rendering)：
* 顶点中的动态表面属性 (`surfaces_v_render`)
    ```python
    ti.types.struct(
        vertices=gs.ti_vec3, # 位置
    )
    ```
* 面中的动态表面属性 (`surfaces_f_render`)
    ```python
    ti.types.struct(
        indices=gs.ti_int, # 与此表面单元对应的顶点索引（TODO：这很丑陋，因为我们扁平化了 (n_surfaces_max, 3)）
    )
    ```

查看 [`genesis/solvers/fem_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/fem_solver.py) 获取更多详情。


## PBD 求解器 (PBD Solver)

基于位置的动力学 (PBD) 使用基于粒子的表示。

对于粒子 (particles)：
* 动态粒子状态 (`particles_state`, `particles_state_reordered`)
    ```python
    ti.types.struct(
        free=gs.ti_int,  # 粒子是否可以自由移动。如果为 0，则它是运动学控制的（例如固定或外部操纵）
        pos=gs.ti_vec3,  # 位置
        ipos=gs.ti_vec3, # 初始位置
        dpos=gs.ti_vec3, # 位置增量
        vel=gs.ti_vec3,  # 速度
        lam=gs.ti_float, # Lagrange 乘子或约束力标量
        rho=gs.ti_float, # 估计的流体密度
    )
    ```
* 无梯度的动态粒子状态 (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    ti.types.struct(
        reordered_idx=gs.ti_int, # 重新排序索引
        active=gs.ti_int,        # 粒子是否激活
    )
    ```
* 静态粒子信息 (`particles_info`, `particles_info_reordered`)
    ```python
    ti.types.struct(
        mass=gs.ti_float,                 # 质量
        pos_rest=gs.ti_vec3,              # 静止位置
        rho_rest=gs.ti_float,             # 静止密度
        material_type=gs.ti_int,          # 材料类型
        mu_s=gs.ti_float,                 # 静摩擦系数
        mu_k=gs.ti_float,                 # 动摩擦系数
        air_resistance=gs.ti_float,       # 空气阻力/阻尼系数
        density_relaxation=gs.ti_float,   # 密度约束求解器的参数
        viscosity_relaxation=gs.ti_float, # 粘度行为的参数
    )
    ```

对于渲染 (rendering)：
* 粒子属性 (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # 位置
        vel=gs.ti_vec3,   # 速度
        active=gs.ti_int, # 粒子是否激活
    )
    ```

查看 [`genesis/solvers/pbd_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/pbd_solver.py) 获取更多详情。

## SPH 求解器 (SPH Solver)

光滑粒子流体动力学 (SPH) 使用基于粒子的表示。

对于粒子 (particles)：
* 动态粒子状态 (`particles_state`, `particles_state_reordered`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,           # 位置
        vel=gs.ti_vec3,           # 速度
        acc=gs.ti_vec3,           # 加速度
        rho=gs.ti_float,          # 密度
        p=gs.ti_float,            # 压力
        dfsph_factor=gs.ti_float, # DFSPH 压力求解中使用的因子
        drho=gs.ti_float,         # 密度导数（变化率）
    )
    ```
* 无梯度的动态粒子状态 (`particles_state_ng`, `particles_state_ng_reordered`)
    ```python
    ti.types.struct(
        reordered_idx=gs.ti_int, # 重新排序索引 
        active=gs.ti_int,        # 粒子是否激活
    )
    ```
* 静态粒子信息 (`particles_info`, `particles_info_reordered`)
    ```python
    ti.types.struct(
        rho=gs.ti_float,       # 静止密度
        mass=gs.ti_float,      # 粒子质量
        stiffness=gs.ti_float, # 状态方程刚度
        exponent=gs.ti_float,  # 状态方程指数
        mu=gs.ti_float,        # 粘度系数
        gamma=gs.ti_float,     # 表面张力系数
    )
    ```

对于渲染 (rendering)：
* 粒子属性 (`particles_render`)
    ```python
    ti.types.struct(
        pos=gs.ti_vec3,   # 位置
        vel=gs.ti_vec3,   # 速度
        active=gs.ti_int, # 粒子是否激活
    )
    ```

查看 [`genesis/solvers/sph_solver.py`](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/solvers/sph_solver.py) 获取更多详情。

<!-- ## SF Solver -->
