"""
LLM 提供者接口和实现 - 支持多种大模型 API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os


class LLMProvider(ABC):
    """LLM 提供者基类"""

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        生成响应

        Args:
            messages: 对话消息列表
            tools: 可用工具列表
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            包含响应内容和可能的工具调用的字典
        """
        pass


class ClaudeProvider(LLMProvider):
    """
    Claude API 提供者（使用 Anthropic SDK）
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-6"):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "需要安装 anthropic 包: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        # 分离 system 消息
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)

        # 构建请求参数
        request_params = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        if system_message:
            request_params["system"] = system_message

        if tools:
            # 转换为 Claude 工具格式
            claude_tools = []
            for tool in tools:
                claude_tools.append({
                    "name": tool["function"]["name"],
                    "description": tool["function"]["description"],
                    "input_schema": tool["function"]["parameters"]
                })
            request_params["tools"] = claude_tools

        # 调用 API
        response = self.client.messages.create(**request_params)

        # 解析响应
        result = {"content": ""}

        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                if "tool_calls" not in result:
                    result["tool_calls"] = []
                result["tool_calls"].append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": str(block.input)
                    }
                })

        return result


class OpenAIProvider(LLMProvider):
    """
    OpenAI API 提供者（支持 GPT-4 等模型）
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "需要安装 openai 包: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 OPENAI_API_KEY")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        request_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**request_params)

        result = {
            "content": response.choices[0].message.content or ""
        }

        if response.choices[0].message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response.choices[0].message.tool_calls
            ]

        return result


class MockProvider(LLMProvider):
    """
    模拟提供者 - 用于测试，不调用真实 API
    """

    def __init__(self, mock_responses: Optional[List[str]] = None):
        self.mock_responses = mock_responses or ["这是一个模拟响应"]
        self.call_count = 0

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        response_index = self.call_count % len(self.mock_responses)
        self.call_count += 1

        return {
            "content": self.mock_responses[response_index]
        }
