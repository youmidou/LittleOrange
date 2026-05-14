"""
工具系统 - 定义工具接口和注册表
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None


class Tool(ABC):
    """
    工具基类 - 所有工具必须继承此类

    工具是 agent 可以调用的原子操作
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            执行结果
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的 JSON Schema（用于 LLM function calling）

        Returns:
            符合 OpenAI/Claude function calling 格式的 schema
        """
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                param_schema["enum"] = param.enum

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def __repr__(self):
        return f"Tool(name='{self.name}')"


class FunctionTool(Tool):
    """
    函数工具 - 将 Python 函数包装为工具

    这是一个便捷类，可以快速将现有函数转换为工具
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter],
        function: Callable
    ):
        super().__init__(name, description, parameters)
        self.function = function

    def execute(self, **kwargs) -> Any:
        return self.function(**kwargs)


class ToolRegistry:
    """
    工具注册表 - 管理所有可用的工具
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册一个工具"""
        if tool.name in self._tools:
            raise ValueError(f"工具 '{tool.name}' 已经注册")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """注销一个工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """获取指定工具"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Tool]:
        """列出所有已注册的工具"""
        return list(self._tools.values())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具的 schema（用于 LLM API）"""
        return [tool.get_schema() for tool in self._tools.values()]

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"ToolRegistry(tools={len(self._tools)})"
