# Conventions

This page outlines the coordinate system and mathematical conventions used throughout Genesis.

## Coordinate System

Genesis uses a right-handed coordinate system with the following conventions:

- **+X axis**: Points out of the screen (towards the viewer)
- **+Y axis**: Points to the left
- **+Z axis**: Points upward (vertical)

## Quaternion Representation

Quaternions in Genesis follow the **(w, x, y, z)** convention, where:
- **w**: Scalar component (real part)
- **x, y, z**: Vector components (imaginary parts)

This is also known as the "scalar-first" or "Hamilton" convention. When specifying rotations using quaternions, always provide them in this order.

### Example
```python
# Quaternion representing a 90-degree rotation around the Z-axis
rotation = [0.707, 0, 0, 0.707]  # [w, x, y, z]
```

## Gravity

The gravitational force vector is defined as:
- **Gravity direction**: **-Z** (pointing downward)
- **Default magnitude**: 9.81 m/s²

This means objects will naturally fall in the negative Z direction when no other forces are applied.
