# LittleOrange 开发文档

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                        User                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                      Agent                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Conversation Manager                     │  │
│  │  - 管理对话历史                                   │  │
│  │  - 处理消息流                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Tool Executor                            │  │
│  │  - 执行工具调用                                   │  │
│  │  - 处理工具结果                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────┬───────────────┘
         │                                │
         ▼                                ▼
┌─────────────────────┐        ┌──────────────────────────┐
│   LLM Provider      │        │   Skill Registry         │
│  - Claude           │        │  - 管理技能              │
│  - OpenAI           │        │  - 动态加载              │
│  - Mock             │        └──────────┬───────────────┘
└─────────────────────┘                   │
                                          ▼
                              ┌──────────────────────────┐
                              │   Tool Registry          │
                              │  - 管理工具              │
                              │  - 提供 Schema           │
                              └──────────┬───────────────┘
                                         │
                                         ▼
                              ┌──────────────────────────┐
                              │   Skills                 │
                              │  - Calculator            │
                              │  - FileOperation         │
                              │  - DateTime              │
                              │  - DataProcessing        │
                              │  - WebSearch             │
                              │  - Custom...             │
                              └──────────────────────────┘
```

### 核心组件

#### 1. Agent (agent.py)

Agent 是系统的核心控制器，负责：

- **对话管理**: 维护对话历史，格式化消息
- **LLM 交互**: 调用 LLM 生成响应
- **工具执行**: 解析和执行工具调用
- **迭代控制**: 管理多轮工具调用

**关键方法**:
- `chat(user_message)`: 处理用户输入，返回响应
- `add_skill(skill)`: 添加技能到 agent
- `reset()`: 重置对话历史
- `_execute_tool(tool_call)`: 执行单个工具调用

#### 2. Skill (skills.py)

Skill 是高级能力模块，定义了 agent 可以执行的复杂任务。

**接口**:
```python
class Skill(ABC):
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """返回此技能提供的工具"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        pass
```

**设计原则**:
- 一个技能可以提供多个工具
- 技能应该是独立的、可复用的
- 技能之间不应该有依赖关系

#### 3. Tool (tools.py)

Tool 是原子操作，是 LLM 可以直接调用的功能。

**接口**:
```python
class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """返回 OpenAI/Claude function calling schema"""
        pass
```

**工具类型**:
- `Tool`: 基础工具类
- `FunctionTool`: 函数包装工具（便捷类）

#### 4. LLM Provider (llm.py)

LLM Provider 抽象了不同大模型 API 的差异。

**支持的提供者**:
- `ClaudeProvider`: Anthropic Claude API
- `OpenAIProvider`: OpenAI GPT API
- `MockProvider`: 测试用模拟提供者

**接口**:
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """生成响应"""
        pass
```

## 数据流

### 1. 用户消息处理流程

```
用户输入
  │
  ▼
Agent.chat()
  │
  ├─> 添加到对话历史
  │
  ▼
LLM Provider.generate()
  │
  ├─> 发送到 LLM API
  │
  ▼
解析响应
  │
  ├─> 有工具调用？
  │   │
  │   ├─> 是: 执行工具
  │   │    │
  │   │    ├─> Tool Registry.get_tool()
  │   │    │
  │   │    ├─> Tool.execute()
  │   │    │
  │   │    ├─> 添加工具结果到历史
  │   │    │
  │   │    └─> 继续迭代
  │   │
  │   └─> 否: 返回最终响应
  │
  ▼
返回给用户
```

### 2. 技能注册流程

```
创建 Skill 实例
  │
  ▼
Agent.add_skill(skill)
  │
  ├─> Skill Registry.register(skill)
  │
  ├─> skill.get_tools()
  │    │
  │    └─> 返回 Tool 列表
  │
  ▼
遍历每个 Tool
  │
  └─> Tool Registry.register(tool)
```

### 3. 工具调用流程

```
LLM 返回 tool_calls
  │
  ▼
遍历每个 tool_call
  │
  ├─> 解析 tool_name 和 arguments
  │
  ├─> Tool Registry.get_tool(tool_name)
  │
  ├─> Tool.execute(**arguments)
  │
  ├─> 捕获异常
  │
  └─> 返回结果 {"success": bool, "result": any}
```

## 扩展指南

### 创建自定义技能

#### 步骤 1: 定义技能类

```python
from little_orange.skills import Skill
from little_orange.tools import FunctionTool, ToolParameter

class MyCustomSkill(Skill):
    def __init__(self):
        super().__init__(
            name="my_skill",
            description="我的自定义技能"
        )
```

#### 步骤 2: 实现 get_tools()

```python
def get_tools(self):
    return [
        FunctionTool(
            name="my_tool",
            description="我的工具",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="参数1"
                )
            ],
            function=self.my_function
        )
    ]
```

#### 步骤 3: 实现工具函数

```python
def my_function(self, param1: str) -> str:
    # 实现你的逻辑
    return f"处理结果: {param1}"
```

#### 步骤 4: 实现 execute()

```python
def execute(self, **kwargs):
    return self.my_function(**kwargs)
```

### 创建自定义 LLM Provider

```python
from little_orange.llm import LLMProvider

class MyLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 初始化你的 API 客户端
    
    def generate(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        # 调用你的 LLM API
        # 返回格式:
        # {
        #     "content": "响应内容",
        #     "tool_calls": [...]  # 可选
        # }
        pass
```

## 最佳实践

### 1. 技能设计

- **单一职责**: 每个技能应该专注于一个领域
- **独立性**: 技能之间不应该有依赖
- **可测试**: 技能应该易于单元测试
- **错误处理**: 优雅地处理异常情况

### 2. 工具设计

- **原子性**: 工具应该执行单一、明确的操作
- **幂等性**: 相同输入应该产生相同输出
- **参数验证**: 验证输入参数的有效性
- **清晰的描述**: 提供清晰的工具和参数描述

### 3. 提示词工程

- **明确角色**: 在 system_prompt 中明确 agent 的角色
- **列出能力**: 告诉 LLM 它可以使用哪些工具
- **示例引导**: 提供使用工具的示例
- **约束说明**: 说明使用工具的限制和注意事项

### 4. 错误处理

```python
try:
    result = tool.execute(**args)
    return {"success": True, "result": result}
except ValueError as e:
    return {"success": False, "error": f"参数错误: {str(e)}"}
except Exception as e:
    return {"success": False, "error": f"执行失败: {str(e)}"}
```

### 5. 性能优化

- **缓存**: 对重复的工具调用结果进行缓存
- **并行执行**: 对独立的工具调用可以并行执行
- **流式输出**: 对长时间运行的任务使用流式输出
- **超时控制**: 为工具执行设置超时

## 测试

### 单元测试示例

```python
import unittest
from little_orange.builtin_skills import CalculatorSkill

class TestCalculatorSkill(unittest.TestCase):
    def setUp(self):
        self.skill = CalculatorSkill()
    
    def test_basic_calculation(self):
        result = self.skill.calculate("2 + 2")
        self.assertEqual(result, 4.0)
    
    def test_advanced_calculation(self):
        result = self.skill.calculate("sqrt(16)")
        self.assertEqual(result, 4.0)
    
    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            self.skill.calculate("invalid")
```

### 集成测试

```python
from little_orange.agent import Agent, AgentConfig
from little_orange.llm import MockProvider

def test_agent_with_calculator():
    llm = MockProvider(mock_responses=["使用计算器"])
    config = AgentConfig()
    agent = Agent(config=config, llm_provider=llm)
    agent.add_skill(CalculatorSkill())
    
    response = agent.chat("计算 2 + 2")
    assert response is not None
```

## 调试技巧

### 1. 启用详细日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("little_orange")
```

### 2. 查看对话历史

```python
history = agent.get_history()
for msg in history:
    print(f"[{msg.role}] {msg.content}")
```

### 3. 使用 Mock Provider

```python
# 模拟特定的响应序列
mock = MockProvider(mock_responses=[
    "我需要使用工具",
    "工具执行完成"
])
```

## 常见问题

### Q: 如何处理长对话？
A: 实现对话历史的截断或摘要机制：

```python
def truncate_history(self, max_messages: int = 20):
    if len(self.conversation_history) > max_messages:
        # 保留 system 消息和最近的消息
        system_msgs = [m for m in self.conversation_history if m.role == "system"]
        recent_msgs = self.conversation_history[-max_messages:]
        self.conversation_history = system_msgs + recent_msgs
```

### Q: 如何实现工具调用的权限控制？
A: 在 Tool 类中添加权限检查：

```python
class SecureTool(Tool):
    def __init__(self, *args, required_permission: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_permission = required_permission
    
    def execute(self, **kwargs):
        if self.required_permission and not self.check_permission():
            raise PermissionError("权限不足")
        return self._execute(**kwargs)
```

### Q: 如何实现异步工具调用？
A: 使用 asyncio：

```python
import asyncio

class AsyncTool(Tool):
    async def execute_async(self, **kwargs):
        # 异步执行逻辑
        pass
    
    def execute(self, **kwargs):
        return asyncio.run(self.execute_async(**kwargs))
```

## 路线图

### 短期目标
- [ ] 添加更多内置技能
- [ ] 支持流式输出
- [ ] 添加工具调用缓存
- [ ] 完善错误处理

### 中期目标
- [ ] 支持多 agent 协作
- [ ] 添加记忆系统
- [ ] 实现工具组合
- [ ] Web UI 界面

### 长期目标
- [ ] 支持自定义 LLM 微调
- [ ] 实现 agent 自我学习
- [ ] 构建技能市场
- [ ] 企业级部署方案

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件
