"""
LittleOrange - 大模型 Agent 和 Skills 系统示例

这个示例展示了如何使用 LittleOrange 创建一个智能 agent，
并为其添加各种技能（skills）来扩展功能。
"""

import os
from little_orange.agent import Agent, AgentConfig
from little_orange.llm import ClaudeProvider, OpenAIProvider, MockProvider
from little_orange.builtin_skills import (
    CalculatorSkill,
    FileOperationSkill,
    DateTimeSkill,
    DataProcessingSkill,
    WebSearchSkill
)


def create_agent(provider_type: str = "mock") -> Agent:
    """
    创建一个配置好的 LittleOrange agent

    Args:
        provider_type: LLM 提供者类型 (claude, openai, mock)

    Returns:
        配置好的 Agent 实例
    """
    # 选择 LLM 提供者
    if provider_type == "claude":
        llm_provider = ClaudeProvider(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-sonnet-4-6"
        )
    elif provider_type == "openai":
        llm_provider = OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4-turbo"
        )
    else:
        # 使用模拟提供者进行测试
        llm_provider = MockProvider(
            mock_responses=[
                "我需要使用计算器来计算这个表达式。",
                "计算完成！结果是 4。"
            ]
        )

    # 创建 agent 配置
    config = AgentConfig(
        model="claude-sonnet-4-6",
        temperature=0.7,
        max_tokens=4096,
        system_prompt="""你是 LittleOrange，一个智能助手。
你可以使用各种工具来帮助用户完成任务。

可用的技能包括：
- 计算器：执行数学计算
- 文件操作：读写文件
- 日期时间：获取当前时间
- 数据处理：处理 JSON 数据
- 网络搜索：搜索信息

当用户提出请求时，分析需要使用哪些工具，然后调用相应的工具来完成任务。""",
        max_iterations=10
    )

    # 创建 agent
    agent = Agent(config=config, llm_provider=llm_provider)

    # 添加技能
    agent.add_skill(CalculatorSkill())
    agent.add_skill(FileOperationSkill(base_dir="./data"))
    agent.add_skill(DateTimeSkill())
    agent.add_skill(DataProcessingSkill())
    agent.add_skill(WebSearchSkill())

    return agent


def example_calculator():
    """示例 1: 使用计算器技能"""
    print("=" * 60)
    print("示例 1: 计算器技能")
    print("=" * 60)

    agent = create_agent("mock")
    response = agent.chat("请帮我计算 2 + 2")
    print(f"用户: 请帮我计算 2 + 2")
    print(f"Agent: {response}")
    print()


def example_file_operations():
    """示例 2: 文件操作技能"""
    print("=" * 60)
    print("示例 2: 文件操作技能")
    print("=" * 60)

    agent = create_agent("mock")

    # 创建测试目录
    os.makedirs("./data", exist_ok=True)

    # 写入文件
    response = agent.chat("请在 data/test.txt 中写入 'Hello, LittleOrange!'")
    print(f"用户: 请在 data/test.txt 中写入 'Hello, LittleOrange!'")
    print(f"Agent: {response}")
    print()


def example_datetime():
    """示例 3: 日期时间技能"""
    print("=" * 60)
    print("示例 3: 日期时间技能")
    print("=" * 60)

    agent = create_agent("mock")
    response = agent.chat("现在几点了？")
    print(f"用户: 现在几点了？")
    print(f"Agent: {response}")
    print()


def example_custom_skill():
    """示例 4: 创建自定义技能"""
    print("=" * 60)
    print("示例 4: 创建自定义技能")
    print("=" * 60)

    from little_orange.skills import Skill
    from little_orange.tools import FunctionTool, ToolParameter

    class GreetingSkill(Skill):
        """自定义问候技能"""

        def __init__(self):
            super().__init__(
                name="greeting",
                description="生成个性化问候语"
            )

        def get_tools(self):
            return [
                FunctionTool(
                    name="greet",
                    description="生成问候语",
                    parameters=[
                        ToolParameter(
                            name="name",
                            type="string",
                            description="要问候的人的名字"
                        ),
                        ToolParameter(
                            name="language",
                            type="string",
                            description="语言 (zh, en)",
                            required=False
                        )
                    ],
                    function=self.greet
                )
            ]

        def execute(self, name: str, language: str = "zh"):
            return self.greet(name, language)

        def greet(self, name: str, language: str = "zh") -> str:
            if language == "zh":
                return f"你好，{name}！欢迎使用 LittleOrange！"
            else:
                return f"Hello, {name}! Welcome to LittleOrange!"

    agent = create_agent("mock")
    agent.add_skill(GreetingSkill())

    response = agent.chat("请用中文问候 Alice")
    print(f"用户: 请用中文问候 Alice")
    print(f"Agent: {response}")
    print()


def interactive_mode():
    """交互模式 - 与 agent 持续对话"""
    print("=" * 60)
    print("LittleOrange 交互模式")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'reset' 重置对话")
    print("输入 'history' 查看对话历史")
    print()

    # 检查是否有 API 密钥
    provider_type = "mock"
    if os.getenv("ANTHROPIC_API_KEY"):
        provider_type = "claude"
        print("检测到 ANTHROPIC_API_KEY，使用 Claude")
    elif os.getenv("OPENAI_API_KEY"):
        provider_type = "openai"
        print("检测到 OPENAI_API_KEY，使用 OpenAI")
    else:
        print("未检测到 API 密钥，使用模拟模式")
    print()

    agent = create_agent(provider_type)

    while True:
        try:
            user_input = input("你: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                print("再见！")
                break

            if user_input.lower() == 'reset':
                agent.reset()
                print("对话已重置")
                continue

            if user_input.lower() == 'history':
                print("\n对话历史:")
                for i, msg in enumerate(agent.get_history(), 1):
                    print(f"{i}. [{msg.role}] {msg.content[:100]}...")
                print()
                continue

            response = agent.chat(user_input)
            print(f"Agent: {response}\n")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {str(e)}\n")


def main():
    """主函数 - 运行所有示例"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    LittleOrange                            ║")
    print("║            大模型 Agent 和 Skills 系统                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # 运行示例
    example_calculator()
    example_file_operations()
    example_datetime()
    example_custom_skill()

    # 进入交互模式
    print("\n是否进入交互模式？(y/n): ", end="")
    choice = input().strip().lower()
    if choice == 'y':
        interactive_mode()


if __name__ == '__main__':
    main()
