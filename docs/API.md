# LittleOrange API 参考

## 核心类

### Agent

智能代理核心类。

```python
from little_orange.agent import Agent, AgentConfig
```

#### AgentConfig

```python
@dataclass
class AgentConfig:
    model: str = "claude-sonnet-4-6"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None
    max_iterations: int = 10
```

**参数**:
- `model`: 模型名称
- `temperature`: 温度参数 (0.0-1.0)，控制输出的随机性
- `max_tokens`: 最大生成 token 数
- `system_prompt`: 系统提示词
- `max_iterations`: 最大迭代次数，防止无限循环

#### Agent

```python
class Agent:
    def __init__(
        self,
        config: AgentConfig,
        llm_provider: LLMProvider,
        skill_registry: Optional[SkillRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None
    )
```

**方法**:

##### `chat(user_message: str) -> str`
与 agent 对话。

**参数**:
- `user_message`: 用户输入

**返回**: agent 的响应

**示例**:
```python
response = agent.chat("你好")
```

##### `add_skill(skill: Skill)`
添加技能到 agent。

**参数**:
- `skill`: 技能实例

**示例**:
```python
agent.add_skill(CalculatorSkill())
```

##### `reset()`
重置对话历史。

##### `get_history() -> List[Message]`
获取对话历史。

**返回**: 消息列表

---

## Skills

### Skill

技能基类。

```python
from little_orange.skills import Skill
```

```python
class Skill(ABC):
    def __init__(self, name: str, description: str)
    
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """返回此技能提供的工具列表"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行技能的主要功能"""
        pass
```

**属性**:
- `name`: 技能名称
- `description`: 技能描述

### SkillRegistry

技能注册表。

```python
from little_orange.skills import SkillRegistry
```

**方法**:

##### `register(skill: Skill)`
注册一个技能。

##### `unregister(skill_name: str)`
注销一个技能。

##### `get_skill(skill_name: str) -> Optional[Skill]`
获取指定技能。

##### `list_skills() -> List[Skill]`
列出所有已注册的技能。

---

## Tools

### Tool

工具基类。

```python
from little_orange.tools import Tool, ToolParameter
```

```python
class Tool(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter]
    )
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema"""
        pass
```

### ToolParameter

工具参数定义。

```python
@dataclass
class ToolParameter:
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
```

### FunctionTool

函数工具 - 将 Python 函数包装为工具。

```python
from little_orange.tools import FunctionTool
```

```python
class FunctionTool(Tool):
    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter],
        function: Callable
    )
```

**示例**:
```python
def my_func(text: str) -> str:
    return text.upper()

tool = FunctionTool(
    name="to_upper",
    description="转换为大写",
    parameters=[
        ToolParameter(
            name="text",
            type="string",
            description="要转换的文本"
        )
    ],
    function=my_func
)
```

### ToolRegistry

工具注册表。

```python
from little_orange.tools import ToolRegistry
```

**方法**:

##### `register(tool: Tool)`
注册一个工具。

##### `get_tool(tool_name: str) -> Optional[Tool]`
获取指定工具。

##### `list_tools() -> List[Tool]`
列出所有已注册的工具。

##### `get_tool_schemas() -> List[Dict[str, Any]]`
获取所有工具的 schema（用于 LLM API）。

---

## LLM Providers

### LLMProvider

LLM 提供者基类。

```python
from little_orange.llm import LLMProvider
```

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """生成响应"""
        pass
```

### ClaudeProvider

Claude API 提供者。

```python
from little_orange.llm import ClaudeProvider
```

```python
class ClaudeProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-6"
    )
```

**参数**:
- `api_key`: Anthropic API 密钥（可选，默认从环境变量读取）
- `model`: 模型名称

**支持的模型**:
- `claude-opus-4-7`
- `claude-sonnet-4-6`
- `claude-haiku-4-5-20251001`

### OpenAIProvider

OpenAI API 提供者。

```python
from little_orange.llm import OpenAIProvider
```

```python
class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo"
    )
```

**参数**:
- `api_key`: OpenAI API 密钥（可选，默认从环境变量读取）
- `model`: 模型名称

**支持的模型**:
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

### MockProvider

模拟提供者（用于测试）。

```python
from little_orange.llm import MockProvider
```

```python
class MockProvider(LLMProvider):
    def __init__(
        self,
        mock_responses: Optional[List[str]] = None
    )
```

**参数**:
- `mock_responses`: 模拟响应列表

---

## 内置技能

### CalculatorSkill

计算器技能。

```python
from little_orange.builtin_skills import CalculatorSkill
```

**工具**:
- `calculate(expression: str) -> float`: 计算数学表达式

**支持的函数**:
- 基本运算: `+`, `-`, `*`, `/`, `**`
- 数学函数: `sqrt`, `sin`, `cos`, `tan`, `log`, `log10`, `exp`
- 常量: `pi`, `e`

**示例**:
```python
skill = CalculatorSkill()
result = skill.calculate("sqrt(16) + 2 * 3")  # 10.0
```

### FileOperationSkill

文件操作技能。

```python
from little_orange.builtin_skills import FileOperationSkill
```

```python
class FileOperationSkill(Skill):
    def __init__(self, base_dir: str = ".")
```

**工具**:
- `read_file(file_path: str) -> str`: 读取文件
- `write_file(file_path: str, content: str) -> str`: 写入文件
- `list_files(directory: str = ".") -> List[str]`: 列出文件

### DateTimeSkill

日期时间技能。

```python
from little_orange.builtin_skills import DateTimeSkill
```

**工具**:
- `get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str`: 获取当前时间

### DataProcessingSkill

数据处理技能。

```python
from little_orange.builtin_skills import DataProcessingSkill
```

**工具**:
- `parse_json(json_string: str) -> Any`: 解析 JSON
- `format_json(data: str, indent: int = 2) -> str`: 格式化 JSON

### WebSearchSkill

网络搜索技能。

```python
from little_orange.builtin_skills import WebSearchSkill
```

**工具**:
- `search(query: str, num_results: int = 5) -> str`: 搜索网络

---

## 配置

### LittleOrangeConfig

配置类。

```python
from little_orange.config import LittleOrangeConfig
```

```python
@dataclass
class LittleOrangeConfig:
    llm_provider: str = "claude"
    model: str = "claude-sonnet-4-6"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    max_iterations: int = 10
    system_prompt: Optional[str] = None
    enabled_skills: list = None
```

**方法**:

##### `from_file(config_path: str) -> LittleOrangeConfig`
从配置文件加载。

##### `from_env() -> LittleOrangeConfig`
从环境变量加载。

##### `to_file(config_path: str)`
保存到配置文件。

##### `to_dict() -> Dict[str, Any]`
转换为字典。

**示例**:
```python
# 从文件加载
config = LittleOrangeConfig.from_file("config.json")

# 从环境变量加载
config = LittleOrangeConfig.from_env()

# 保存到文件
config.to_file("config.json")
```

---

## 数据类型

### Message

对话消息。

```python
@dataclass
class Message:
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
```

---

## 异常

### ValueError
参数错误或验证失败。

### IOError
文件操作失败。

### PermissionError
权限不足。

---

## 环境变量

- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `OPENAI_API_KEY`: OpenAI API 密钥
- `LITTLE_ORANGE_PROVIDER`: LLM 提供者 (claude, openai, mock)
- `LITTLE_ORANGE_MODEL`: 模型名称
- `LITTLE_ORANGE_TEMPERATURE`: 温度参数
- `LITTLE_ORANGE_MAX_TOKENS`: 最大 token 数
- `LITTLE_ORANGE_MAX_ITERATIONS`: 最大迭代次数
