# Robot Control

Getting a robot to do something useful means turning a goal in task space, "put the gripper here", into motion in joint space that respects the robot's kinematics and its surroundings. This section covers the tools Genesis World provides for that: inverse kinematics to find configurations that reach a pose, motion and path planning to connect configurations without collisions, and constraints to tie links together into mechanisms.

It builds directly on {doc}`Control your robot </user_guide/getting_started/control_your_robot>`, which introduced the position and force control modes; here the question is not how to command a joint but what to command it to. Start with the combined IK-and-planning tutorial for the end-to-end workflow, then reach for the individual pages when a specific need arises.

- {doc}`inverse_kinematics_motion_planning` is the complete pick-and-place walkthrough: solve IK for a target end-effector pose, plan a collision-free path to it, then close the gripper and lift. It also covers the pose conventions IK expects.
- {doc}`advanced_ik` extends the solver in the two directions that matter for real manipulation and for training: multi-target and multi-link IK, and solving across parallel environments at once.
- {doc}`constraints` covers rigid-body constraints that keep a geometric relationship between two links, coincident points, a fixed relative pose, or coupled joints.
- {doc}`path_planning` details `plan_path`, the kinematic planner that finds a collision-free trajectory through joint space from a start to a goal configuration.

```{toctree}
:hidden:
:maxdepth: 1

inverse_kinematics_motion_planning
advanced_ik
constraints
path_planning
```
