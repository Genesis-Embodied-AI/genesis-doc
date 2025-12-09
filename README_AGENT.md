# Genesis API Reference Agent

A powerful Python agent that integrates all API documentation from the `api_reference` directory and provides a convenient interface for users to query and access API information.

## Features

- **Comprehensive Documentation Integration**: Loads and processes all Markdown documentation from the API reference directory
- **Structured Knowledge Base**: Organizes API information into categories (entities, materials, options, scene, sensor)
- **Advanced Search**: Search for APIs by name, description, or parameters
- **Interactive Mode**: User-friendly command-line interface for querying API information
- **Export Functionality**: Export the knowledge base to JSON for external use

## Installation

No external dependencies are required. The agent uses only Python standard libraries.

## Usage

### Basic Usage

Run the agent in interactive mode:

```bash
python genesis_api_agent.py
```

### Interactive Commands

- `help`: Show help information
- `exit`: Exit the agent
- `categories`: List all categories
- `list [category]`: List all APIs (optionally filtered by category)
- `search <query>`: Search for APIs matching query
- `get <api_name>`: Get detailed information about an API
- `<natural language>`: Ask a question about the API (experimental)

### Example Usage

```
=== Genesis API Reference Agent ===
Type 'help' for available commands, 'exit' to quit.
===================================

> categories

Categories:
  - entities: 22 APIs
  - materials: 23 APIs
  - options: 17 APIs
  - scene: 5 APIs
  - sensor: 1 APIs

> list entities

APIs (22 total):
  1. entities.DroneEntity
  2. entities.Emitter
  3. entities.FEMEntity
  4. entities.HybridEntity
  5. entities.MPMEntity
  6. entities.SFEntity
  7. entities.SPHEntity
  8. entities.Tool
  ...

> search force field

Search results for 'force field' (1 total):
  1. scene.ForceField (scene)
     ForceField 是所有力场的基类，用于在模拟中对物体施加各种类型的力（实际上是加速度场）。

> get ForceField

=== ForceField ===
Category: scene

Summary:
  ForceField 是所有力场的基类，用于在模拟中对物体施加各种类型的力（实际上是加速度场）。

Inheritance:
  ForceField
  ├── Constant
  ├── Wind
  ├── Point
  ├── Drag
  ├── Noise
  ├── Vortex
  ├── Turbulence
  └── Custom

Parameters:
  - direction (Vector): 力场的方向向量，必须是归一化的三维向量
  - strength (float): 力场的强度（加速度值，单位：m/s²）
  - active (bool): 力场是否激活，默认为True

Code Examples:
  Example 1:
  ```python
  import genesis as gs

  # 创建场景
  scene = gs.Scene()

  # 添加一个球体
  sphere = gs.primitives.Sphere(position=(0, 0, 1))
  scene.add_entity(sphere)

  # 创建并添加恒定力场（恒定加速度）
  constant_force = gs.force_fields.Constant(direction=(1, 0, 0), strength=5.0)
  scene.add_force_field(constant_force)

  # 构建并运行场景
  scene.build()
  for _ in range(100):
      scene.step()
  ```
```

### Programmatic Usage

You can also use the agent programmatically:

```python
from genesis_api_agent import GenesisAPIAgent

# Initialize the agent
agent = GenesisAPIAgent()

# List all categories
categories = agent.knowledge_base.keys()

# Search for APIs
results = agent.search("force field")

# Get detailed API info
api_info = agent.get_api_info("ForceField")

# Export knowledge base to JSON
agent.export_knowledge_base("genesis_api_knowledge_base.json")
```

## Knowledge Base Structure

The agent builds a structured knowledge base with the following information for each API:

- **Title**: API name and title
- **Summary**: Brief description of the API
- **Inheritance**: Class inheritance hierarchy
- **Parameters**: List of parameters with types and descriptions
- **Code Examples**: Usage examples in Python
- **File Path**: Location of the source documentation

## Extending the Agent

You can extend the agent by adding new features:

1. **NLP Integration**: Add natural language processing for better query handling
2. **Web Interface**: Create a web-based UI for the agent
3. **Additional Formats**: Support for exporting to other formats (HTML, PDF)
4. **Live Updates**: Add functionality to update the knowledge base dynamically

## License

This project is open source and available under the MIT License.
