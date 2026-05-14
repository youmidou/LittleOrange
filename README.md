# LittleOrange 🍊

一个模块化、可扩展的大模型 Agent 和 Skills 系统。

## 特性

- 🤖 **智能 Agent**: 基于大模型的智能代理，支持多轮对话和工具调用
- 🛠️ **技能系统**: 可插拔的技能模块，轻松扩展 agent 能力
- 🔧 **工具框架**: 灵活的工具定义和执行框架
- 🌐 **多 LLM 支持**: 支持 Claude、OpenAI 等多种大模型 API
- 📦 **内置技能**: 提供计算器、文件操作、日期时间等常用技能
- 🎯 **易于扩展**: 简单的接口设计，方便创建自定义技能

## 架构

```
LittleOrange/
├── little_orange/          # 核心库
│   ├── agent.py           # Agent 核心类
│   ├── skills.py          # 技能管理系统
│   ├── tools.py           # 工具框架
│   ├── llm.py             # LLM 提供者接口
│   ├── config.py          # 配置管理
│   └── builtin_skills/    # 内置技能
│       └── __init__.py    # 计算器、文件操作等
├── main.py                # 使用示例
├── config.example.json    # 配置示例
└── .env.example          # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install anthropic  # 如果使用 Claude
# 或
pip install openai     # 如果使用 OpenAI
```

### 2. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
ANTHROPIC_API_KEY=your_api_key_here
# 或
OPENAI_API_KEY=your_api_key_here
```

### 3. 运行示例

```bash
python main.py
```

## 使用示例

### 基础使用

```python
from little_orange.agent import Agent, AgentConfig
from little_orange.llm import ClaudeProvider
from little_orange.builtin_skills import CalculatorSkill

# 创建 LLM 提供者
llm_provider = ClaudeProvider(api_key="your_api_key")

# 创建 agent 配置
config = AgentConfig(
    model="claude-sonnet-4-6",
    temperature=0.7,
    system_prompt="你是一个智能助手"
)

# 创建 agent
agent = Agent(config=config, llm_provider=llm_provider)

# 添加技能
agent.add_skill(CalculatorSkill())

# 对话
response = agent.chat("请帮我计算 123 * 456")
print(response)
```

### 创建自定义技能

```python
from little_orange.skills import Skill
from little_orange.tools import FunctionTool, ToolParameter

class WeatherSkill(Skill):
    """天气查询技能"""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="查询天气信息"
        )
    
    def get_tools(self):
        return [
            FunctionTool(
                name="get_weather",
                description="获取指定城市的天气",
                parameters=[
                    ToolParameter(
                        name="city",
                        type="string",
                        description="城市名称"
                    )
                ],
                function=self.get_weather
            )
        ]
    
    def execute(self, city: str):
        return self.get_weather(city)
    
    def get_weather(self, city: str) -> str:
        # 实际应用中调用天气 API
        return f"{city}的天气：晴天，25°C"

# 使用自定义技能
agent.add_skill(WeatherSkill())
response = agent.chat("北京今天天气怎么样？")
```

## 内置技能

### CalculatorSkill - 计算器
执行数学计算，支持基本运算和高级数学函数。

```python
from little_orange.builtin_skills import CalculatorSkill
agent.add_skill(CalculatorSkill())
```

### FileOperationSkill - 文件操作
读取、写入和列出文件。

```python
from little_orange.builtin_skills import FileOperationSkill
agent.add_skill(FileOperationSkill(base_dir="./data"))
```

### DateTimeSkill - 日期时间
获取当前日期和时间。

```python
from little_orange.builtin_skills import DateTimeSkill
agent.add_skill(DateTimeSkill())
```

### DataProcessingSkill - 数据处理
处理和转换 JSON 数据。

```python
from little_orange.builtin_skills import DataProcessingSkill
agent.add_skill(DataProcessingSkill())
```

### WebSearchSkill - 网络搜索
搜索网络信息（需要集成搜索 API）。

```python
from little_orange.builtin_skills import WebSearchSkill
agent.add_skill(WebSearchSkill())
```

## 核心概念

### Agent（代理）
Agent 是系统的核心，负责：
- 管理对话历史
- 调用 LLM 生成响应
- 执行工具和技能
- 处理多轮对话

### Skill（技能）
Skill 是高级能力模块，每个技能可以提供一个或多个工具。技能是可插拔的，可以动态添加到 agent。

### Tool（工具）
Tool 是原子操作，是 agent 可以调用的具体功能。工具通过 function calling 机制被 LLM 调用。

### LLM Provider（LLM 提供者）
LLM Provider 是与大模型 API 交互的接口，支持：
- Claude (Anthropic)
- OpenAI (GPT-4)
- Mock (测试用)

## 配置

### 使用配置文件

```python
from little_orange.config import LittleOrangeConfig

# 从文件加载
config = LittleOrangeConfig.from_file("config.json")

# 从环境变量加载
config = LittleOrangeConfig.from_env()

# 保存到文件
config.to_file("config.json")
```

### 配置选项

- `llm_provider`: LLM 提供者 (claude, openai, mock)
- `model`: 模型名称
- `api_key`: API 密钥
- `temperature`: 温度参数 (0.0-1.0)
- `max_tokens`: 最大 token 数
- `max_iterations`: 最大迭代次数
- `system_prompt`: 系统提示词
- `enabled_skills`: 启用的技能列表

## 高级用法

### 对话历史管理

```python
# 获取对话历史
history = agent.get_history()

# 重置对话
agent.reset()
```

### 自定义工具

```python
from little_orange.tools import Tool, ToolParameter

class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="自定义工具",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="参数1"
                )
            ]
        )
    
    def execute(self, param1: str):
        return f"执行结果: {param1}"
```

### 使用函数工具

```python
from little_orange.tools import FunctionTool, ToolParameter

def my_function(text: str) -> str:
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
    function=my_function
)

agent.tool_registry.register(tool)
```

## 开发指南

### 项目结构

- `little_orange/`: 核心库代码
  - `agent.py`: Agent 实现
  - `skills.py`: 技能系统
  - `tools.py`: 工具框架
  - `llm.py`: LLM 提供者
  - `config.py`: 配置管理
  - `builtin_skills/`: 内置技能

### 添加新技能

1. 继承 `Skill` 基类
2. 实现 `get_tools()` 方法
3. 实现 `execute()` 方法
4. 注册到 agent

### 测试

```bash
# 使用 Mock Provider 进行测试
python main.py
```

## 示例项目

查看 `main.py` 获取完整的使用示例，包括：
- 基础对话
- 工具调用
- 自定义技能
- 交互模式

## 常见问题

### Q: 如何切换不同的 LLM？
A: 在创建 agent 时指定不同的 LLM Provider：

```python
# 使用 Claude
llm_provider = ClaudeProvider(api_key="...")

# 使用 OpenAI
llm_provider = OpenAIProvider(api_key="...")
```

### Q: 如何限制 agent 的迭代次数？
A: 在 AgentConfig 中设置 `max_iterations`：

```python
config = AgentConfig(max_iterations=5)
```

### Q: 如何添加自定义的系统提示词？
A: 在 AgentConfig 中设置 `system_prompt`：

```python
config = AgentConfig(
    system_prompt="你是一个专业的编程助手..."
)
```

## 贡献

欢迎贡献代码、报告问题或提出建议！

## 许可证

MIT License

## 联系方式

- GitHub: [LittleOrange](https://github.com/yourusername/LittleOrange)
- Email: your.email@example.com

---

Made with ❤️ by LittleOrange Team
