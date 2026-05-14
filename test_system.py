"""
LittleOrange 功能测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from little_orange.agent import Agent, AgentConfig
from little_orange.llm import MockProvider
from little_orange.builtin_skills import (
    CalculatorSkill,
    FileOperationSkill,
    DateTimeSkill,
    DataProcessingSkill
)


def test_calculator_skill():
    """测试计算器技能"""
    print("测试 1: 计算器技能")
    print("-" * 50)

    skill = CalculatorSkill()

    # 测试基本运算
    result = skill.calculate("2 + 2")
    assert result == 4.0, f"期望 4.0，得到 {result}"
    print(f"✓ 2 + 2 = {result}")

    # 测试高级函数
    result = skill.calculate("sqrt(16)")
    assert result == 4.0, f"期望 4.0，得到 {result}"
    print(f"✓ sqrt(16) = {result}")

    # 测试复杂表达式
    result = skill.calculate("(10 + 5) * 2")
    assert result == 30.0, f"期望 30.0，得到 {result}"
    print(f"✓ (10 + 5) * 2 = {result}")

    print("✅ 计算器技能测试通过\n")


def test_file_operations():
    """测试文件操作技能"""
    print("测试 2: 文件操作技能")
    print("-" * 50)

    skill = FileOperationSkill(base_dir="./test_data")

    # 创建测试目录
    os.makedirs("./test_data", exist_ok=True)

    # 测试写入
    result = skill.write_file("test.txt", "Hello, LittleOrange!")
    print(f"✓ 写入文件: {result}")

    # 测试读取
    content = skill.read_file("test.txt")
    assert content == "Hello, LittleOrange!", f"期望 'Hello, LittleOrange!'，得到 '{content}'"
    print(f"✓ 读取文件: {content}")

    # 测试列出文件
    files = skill.list_files(".")
    assert "test.txt" in files, "test.txt 应该在文件列表中"
    print(f"✓ 列出文件: {len(files)} 个文件")

    # 清理
    os.remove("./test_data/test.txt")
    os.rmdir("./test_data")

    print("✅ 文件操作技能测试通过\n")


def test_datetime_skill():
    """测试日期时间技能"""
    print("测试 3: 日期时间技能")
    print("-" * 50)

    skill = DateTimeSkill()

    # 测试获取当前时间
    time_str = skill.get_current_time()
    print(f"✓ 当前时间: {time_str}")

    # 测试自定义格式
    time_str = skill.get_current_time("%Y-%m-%d")
    print(f"✓ 日期格式: {time_str}")

    print("✅ 日期时间技能测试通过\n")


def test_data_processing():
    """测试数据处理技能"""
    print("测试 4: 数据处理技能")
    print("-" * 50)

    skill = DataProcessingSkill()

    # 测试 JSON 解析
    json_str = '{"name": "LittleOrange", "version": "0.1.0"}'
    data = skill.parse_json(json_str)
    assert data["name"] == "LittleOrange", "JSON 解析失败"
    print(f"✓ JSON 解析: {data}")

    # 测试 JSON 格式化
    formatted = skill.format_json(json_str, indent=2)
    print(f"✓ JSON 格式化:\n{formatted}")

    print("✅ 数据处理技能测试通过\n")


def test_agent_with_mock():
    """测试 Agent 与 Mock Provider"""
    print("测试 5: Agent 集成测试")
    print("-" * 50)

    # 创建 mock provider
    llm = MockProvider(mock_responses=[
        "这是第一个响应",
        "这是第二个响应"
    ])

    # 创建 agent
    config = AgentConfig(
        system_prompt="你是 LittleOrange 测试助手"
    )
    agent = Agent(config=config, llm_provider=llm)

    # 添加技能
    agent.add_skill(CalculatorSkill())

    # 测试对话
    response1 = agent.chat("你好")
    print(f"✓ 响应 1: {response1}")

    response2 = agent.chat("再见")
    print(f"✓ 响应 2: {response2}")

    # 测试历史
    history = agent.get_history()
    assert len(history) >= 4, "对话历史应该包含至少 4 条消息"
    print(f"✓ 对话历史: {len(history)} 条消息")

    # 测试重置
    agent.reset()
    history = agent.get_history()
    assert len(history) == 1, "重置后应该只有 system 消息"
    print(f"✓ 重置后历史: {len(history)} 条消息")

    print("✅ Agent 集成测试通过\n")


def test_skill_registry():
    """测试技能注册表"""
    print("测试 6: 技能注册表")
    print("-" * 50)

    from little_orange.skills import SkillRegistry

    registry = SkillRegistry()

    # 注册技能
    calc_skill = CalculatorSkill()
    registry.register(calc_skill)
    print(f"✓ 注册技能: {calc_skill.name}")

    # 获取技能
    skill = registry.get_skill("calculator")
    assert skill is not None, "应该能获取到计算器技能"
    print(f"✓ 获取技能: {skill.name}")

    # 列出技能
    skills = registry.list_skills()
    assert len(skills) == 1, "应该有 1 个技能"
    print(f"✓ 技能列表: {len(skills)} 个技能")

    print("✅ 技能注册表测试通过\n")


def test_tool_registry():
    """测试工具注册表"""
    print("测试 7: 工具注册表")
    print("-" * 50)

    from little_orange.tools import ToolRegistry, FunctionTool, ToolParameter

    registry = ToolRegistry()

    # 创建工具
    def test_func(text: str) -> str:
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
        function=test_func
    )

    # 注册工具
    registry.register(tool)
    print(f"✓ 注册工具: {tool.name}")

    # 获取工具
    retrieved_tool = registry.get_tool("to_upper")
    assert retrieved_tool is not None, "应该能获取到工具"
    print(f"✓ 获取工具: {retrieved_tool.name}")

    # 执行工具
    result = retrieved_tool.execute(text="hello")
    assert result == "HELLO", f"期望 'HELLO'，得到 '{result}'"
    print(f"✓ 执行工具: hello -> {result}")

    # 获取 schema
    schemas = registry.get_tool_schemas()
    assert len(schemas) == 1, "应该有 1 个工具 schema"
    print(f"✓ 工具 schemas: {len(schemas)} 个")

    print("✅ 工具注册表测试通过\n")


def main():
    """运行所有测试"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              LittleOrange 功能测试                         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    try:
        test_calculator_skill()
        test_file_operations()
        test_datetime_skill()
        test_data_processing()
        test_agent_with_mock()
        test_skill_registry()
        test_tool_registry()

        print("=" * 60)
        print("🎉 所有测试通过！LittleOrange 系统运行正常！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
