# `gs.options.Options`

`Options` 是 Genesis 引擎中所有选项类的基类，用于设置场景中特定组件的参数。

## 功能说明

- 提供参数验证和类型检查功能
- 支持参数的序列化和反序列化
- 提供参数复制和属性复制功能
- 作为所有选项类的统一接口

## 主要方法

| 方法名 | 描述 |
| ------ | ---- |
| `copy_attributes_from(source)` | 从源对象复制属性 |
| `copy()` | 创建对象的副本 |
| `dict()` | 将对象转换为字典 |
| `json()` | 将对象转换为 JSON 字符串 |
| `model_dump()` | 将对象转换为字典（Pydantic v2 API） |
| `model_dump_json()` | 将对象转换为 JSON 字符串（Pydantic v2 API） |

```{eval-rst}  
.. autoclass:: genesis.options.options.Options
    :members:
    :show-inheritance:
    :undoc-members:
```
