"""
核心 Agent 类 - 负责对话管理、技能调用和工具执行
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .skills import SkillRegistry
from .tools import ToolRegistry
from .llm import LLMProvider


@dataclass
class Message:
    """对话消息"""
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class AgentConfig:
    """Agent 配置"""
    model: str = "claude-sonnet-4-6"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None
    max_iterations: int = 10


class Agent:
    """
    LittleOrange Agent - 智能代理核心类

    功能：
    - 管理对话历史
    - 调用 LLM 生成响应
    - 执行工具和技能
    - 处理多轮对话
    """

    def __init__(
        self,
        config: AgentConfig,
        llm_provider: LLMProvider,
        skill_registry: Optional[SkillRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        self.config = config
        self.llm_provider = llm_provider
        self.skill_registry = skill_registry or SkillRegistry()
        self.tool_registry = tool_registry or ToolRegistry()
        self.conversation_history: List[Message] = []

        if config.system_prompt:
            self.conversation_history.append(
                Message(role="system", content=config.system_prompt)
            )

    def add_skill(self, skill):
        """添加技能到 agent"""
        self.skill_registry.register(skill)
        for tool in skill.get_tools():
            self.tool_registry.register(tool)

    def chat(self, user_message: str) -> str:
        """
        与 agent 对话

        Args:
            user_message: 用户输入

        Returns:
            agent 的响应
        """
        self.conversation_history.append(
            Message(role="user", content=user_message)
        )

        iteration = 0
        while iteration < self.config.max_iterations:
            iteration += 1

            # 调用 LLM
            response = self.llm_provider.generate(
                messages=self._format_messages(),
                tools=self.tool_registry.get_tool_schemas(),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            # 处理响应
            if response.get("tool_calls"):
                # 执行工具调用
                self.conversation_history.append(
                    Message(
                        role="assistant",
                        content=response.get("content", ""),
                        tool_calls=response["tool_calls"]
                    )
                )

                # 执行每个工具调用
                for tool_call in response["tool_calls"]:
                    tool_result = self._execute_tool(tool_call)
                    self.conversation_history.append(
                        Message(
                            role="tool",
                            content=json.dumps(tool_result),
                            tool_call_id=tool_call["id"],
                            name=tool_call["function"]["name"]
                        )
                    )
            else:
                # 没有工具调用，返回最终响应
                assistant_message = response.get("content", "")
                self.conversation_history.append(
                    Message(role="assistant", content=assistant_message)
                )
                return assistant_message

        return "达到最大迭代次数，对话终止。"

    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])

        try:
            tool = self.tool_registry.get_tool(tool_name)
            result = tool.execute(**tool_args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _format_messages(self) -> List[Dict[str, Any]]:
        """格式化消息为 LLM API 格式"""
        formatted = []
        for msg in self.conversation_history:
            message_dict = {"role": msg.role, "content": msg.content}

            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            if msg.name:
                message_dict["name"] = msg.name

            formatted.append(message_dict)

        return formatted

    def reset(self):
        """重置对话历史"""
        system_messages = [
            msg for msg in self.conversation_history
            if msg.role == "system"
        ]
        self.conversation_history = system_messages

    def get_history(self) -> List[Message]:
        """获取对话历史"""
        return self.conversation_history.copy()
