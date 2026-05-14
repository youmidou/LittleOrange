# LittleOrange 快速开始指南

## 5 分钟上手

### 1. 安装依赖

```bash
# 激活虚拟环境（如果还没有）
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装 LLM SDK
pip install anthropic  # 使用 Claude
# 或
pip install openai     # 使用 OpenAI
```

### 2. 设置 API 密钥

```bash
# 方式 1: 使用环境变量
export ANTHROPIC_API_KEY="your_api_key_here"

# 方式 2: 创建 .env 文件
cp .env.example .env
# 然后编辑 .env 文件填入你的 API 密钥
```

### 3. 运行示例

```bash
python main.py
```

## 第一个 Agent

创建一个简单的计算器 agent：

```python
from little_orange.agent import Agent, AgentConfig
from little_orange.llm import ClaudeProvider
from little_orange.builtin_skills import CalculatorSkill

# 1. 创建 LLM 提供者
llm = ClaudeProvider(api_key="your_api_key")

# 2. 配置 agent
config = AgentConfig(
    system_prompt="你是一个数学助手，可以帮助用户进行计算。"
)

# 3. 创建 agent
agent = Agent(config=config, llm_provider=llm)

# 4. 添加技能
agent.add_skill(CalculatorSkill())

# 5. 开始对话
response = agent.chat("请帮我计算 (123 + 456) * 2")
print(response)
```

## 添加更多技能

```python
from little_orange.builtin_skills import (
    CalculatorSkill,
    FileOperationSkill,
    DateTimeSkill,
    DataProcessingSkill
)

# 添加多个技能
agent.add_skill(CalculatorSkill())
agent.add_skill(FileOperationSkill(base_dir="./data"))
agent.add_skill(DateTimeSkill())
agent.add_skill(DataProcessingSkill())

# 现在 agent 可以执行更多任务
agent.chat("现在几点了？")
agent.chat("帮我计算 sqrt(144)")
agent.chat("读取 data/test.txt 文件")
```

## 创建自定义技能

```python
from little_orange.skills import Skill
from little_orange.tools import FunctionTool, ToolParameter

class GreetingSkill(Skill):
    def __init__(self):
        super().__init__(
            name="greeting",
            description="生成问候语"
        )
    
    def get_tools(self):
        return [
            FunctionTool(
                name="greet",
                description="向某人问候",
                parameters=[
                    ToolParameter(
                        name="name",
                        type="string",
                        description="要问候的人的名字"
                    )
                ],
                function=self.greet
            )
        ]
    
    def execute(self, name: str):
        return self.greet(name)
    
    def greet(self, name: str) -> str:
        return f"你好，{name}！欢迎使用 LittleOrange！"

# 使用自定义技能
agent.add_skill(GreetingSkill())
agent.chat("请问候 Alice")
```

## 交互模式

运行 `main.py` 并选择进入交互模式，可以持续与 agent 对话：

```bash
python main.py
# 当提示时输入 'y' 进入交互模式
```

交互模式命令：
- 输入任何问题与 agent 对话
- `reset` - 重置对话历史
- `history` - 查看对话历史
- `quit` 或 `exit` - 退出

## 使用不同的 LLM

### Claude (Anthropic)

```python
from little_orange.llm import ClaudeProvider

llm = ClaudeProvider(
    api_key="your_anthropic_key",
    model="claude-sonnet-4-6"  # 或 claude-opus-4-7
)
```

### OpenAI

```python
from little_orange.llm import OpenAIProvider

llm = OpenAIProvider(
    api_key="your_openai_key",
    model="gpt-4-turbo"  # 或 gpt-4, gpt-3.5-turbo
)
```

### 测试模式（无需 API）

```python
from little_orange.llm import MockProvider

llm = MockProvider(
    mock_responses=["这是模拟响应"]
)
```

## 配置文件

使用配置文件管理设置：

```python
from little_orange.config import LittleOrangeConfig

# 从文件加载
config = LittleOrangeConfig.from_file("config.json")

# 从环境变量加载
config = LittleOrangeConfig.from_env()
```

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 阅读 [docs/API.md](docs/API.md) 学习 API 参考
- 参考 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) 进行高级开发
- 运行 `main.py` 查看更多示例

## 常见问题

**Q: 没有 API 密钥怎么办？**  
A: 使用 `MockProvider` 进行测试，不需要真实 API。

**Q: 如何调试？**  
A: 使用 `agent.get_history()` 查看对话历史，了解 agent 的思考过程。

**Q: 技能不工作？**  
A: 确保在 `system_prompt` 中告诉 agent 它可以使用哪些工具。

**Q: 如何限制成本？**  
A: 在 `AgentConfig` 中设置 `max_tokens` 和 `max_iterations`。

## 获取帮助

- GitHub Issues: 报告问题
- 文档: 查看 `docs/` 目录
- 示例: 运行 `main.py`
