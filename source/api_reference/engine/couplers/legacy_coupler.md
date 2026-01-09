# LegacyCoupler

The `LegacyCoupler` provides basic impulse-based coupling between different physics solvers.

## Overview

The Legacy coupler:

- Uses impulse-based contact resolution
- Handles rigid-soft interactions
- Simple and fast for basic scenarios

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.LegacyCouplerOptions(
        friction=0.5,
    ),
)
```

## See Also

- {doc}`index` - Coupler overview
- {doc}`sap_coupler` - Spatial acceleration
