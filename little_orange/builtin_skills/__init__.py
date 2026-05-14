"""
示例技能集合 - 提供常用的技能实现
"""

import os
import json
import math
from typing import List, Any
from datetime import datetime

from ..skills import Skill
from ..tools import Tool, ToolParameter, FunctionTool


class CalculatorSkill(Skill):
    """计算器技能 - 执行数学计算"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持基本运算和高级数学函数"
        )

    def get_tools(self) -> List[Tool]:
        return [
            FunctionTool(
                name="calculate",
                description="计算数学表达式，支持 +, -, *, /, **, sqrt, sin, cos 等",
                parameters=[
                    ToolParameter(
                        name="expression",
                        type="string",
                        description="要计算的数学表达式，例如: '2 + 2', 'sqrt(16)', 'sin(3.14/2)'"
                    )
                ],
                function=self.calculate
            )
        ]

    def execute(self, expression: str) -> Any:
        return self.calculate(expression)

    def calculate(self, expression: str) -> float:
        """安全地计算数学表达式"""
        # 允许的函数和常量
        safe_dict = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
            'abs': abs,
            'pow': pow,
        }

        try:
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            raise ValueError(f"计算错误: {str(e)}")


class FileOperationSkill(Skill):
    """文件操作技能 - 读写文件"""

    def __init__(self, base_dir: str = "."):
        super().__init__(
            name="file_operations",
            description="读取和写入文件内容"
        )
        self.base_dir = base_dir

    def get_tools(self) -> List[Tool]:
        return [
            FunctionTool(
                name="read_file",
                description="读取文件内容",
                parameters=[
                    ToolParameter(
                        name="file_path",
                        type="string",
                        description="要读取的文件路径"
                    )
                ],
                function=self.read_file
            ),
            FunctionTool(
                name="write_file",
                description="写入内容到文件",
                parameters=[
                    ToolParameter(
                        name="file_path",
                        type="string",
                        description="要写入的文件路径"
                    ),
                    ToolParameter(
                        name="content",
                        type="string",
                        description="要写入的内容"
                    )
                ],
                function=self.write_file
            ),
            FunctionTool(
                name="list_files",
                description="列出目录中的文件",
                parameters=[
                    ToolParameter(
                        name="directory",
                        type="string",
                        description="要列出的目录路径",
                        required=False
                    )
                ],
                function=self.list_files
            )
        ]

    def execute(self, operation: str, **kwargs) -> Any:
        if operation == "read":
            return self.read_file(kwargs["file_path"])
        elif operation == "write":
            return self.write_file(kwargs["file_path"], kwargs["content"])
        elif operation == "list":
            return self.list_files(kwargs.get("directory", "."))

    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        full_path = os.path.join(self.base_dir, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"读取文件失败: {str(e)}")

    def write_file(self, file_path: str, content: str) -> str:
        """写入文件内容"""
        full_path = os.path.join(self.base_dir, file_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"成功写入文件: {file_path}"
        except Exception as e:
            raise IOError(f"写入文件失败: {str(e)}")

    def list_files(self, directory: str = ".") -> List[str]:
        """列出目录中的文件"""
        full_path = os.path.join(self.base_dir, directory)
        try:
            return os.listdir(full_path)
        except Exception as e:
            raise IOError(f"列出文件失败: {str(e)}")


class WebSearchSkill(Skill):
    """网络搜索技能 - 模拟搜索功能"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="在网络上搜索信息"
        )

    def get_tools(self) -> List[Tool]:
        return [
            FunctionTool(
                name="search",
                description="搜索网络信息",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="搜索查询"
                    ),
                    ToolParameter(
                        name="num_results",
                        type="number",
                        description="返回结果数量",
                        required=False
                    )
                ],
                function=self.search
            )
        ]

    def execute(self, query: str, num_results: int = 5) -> Any:
        return self.search(query, num_results)

    def search(self, query: str, num_results: int = 5) -> str:
        """
        模拟搜索功能
        实际应用中可以集成真实的搜索 API（如 Google, Bing, DuckDuckGo）
        """
        return f"搜索 '{query}' 的模拟结果（实际应用中需要集成真实搜索 API）"


class DateTimeSkill(Skill):
    """日期时间技能 - 获取和格式化日期时间"""

    def __init__(self):
        super().__init__(
            name="datetime",
            description="获取当前日期时间和进行时间计算"
        )

    def get_tools(self) -> List[Tool]:
        return [
            FunctionTool(
                name="get_current_time",
                description="获取当前日期和时间",
                parameters=[
                    ToolParameter(
                        name="format",
                        type="string",
                        description="时间格式，例如: '%Y-%m-%d %H:%M:%S'",
                        required=False
                    )
                ],
                function=self.get_current_time
            )
        ]

    def execute(self, **kwargs) -> Any:
        return self.get_current_time(kwargs.get("format"))

    def get_current_time(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前时间"""
        return datetime.now().strftime(format)


class DataProcessingSkill(Skill):
    """数据处理技能 - JSON 和数据转换"""

    def __init__(self):
        super().__init__(
            name="data_processing",
            description="处理和转换数据，支持 JSON 解析和格式化"
        )

    def get_tools(self) -> List[Tool]:
        return [
            FunctionTool(
                name="parse_json",
                description="解析 JSON 字符串",
                parameters=[
                    ToolParameter(
                        name="json_string",
                        type="string",
                        description="要解析的 JSON 字符串"
                    )
                ],
                function=self.parse_json
            ),
            FunctionTool(
                name="format_json",
                description="格式化 JSON 数据",
                parameters=[
                    ToolParameter(
                        name="data",
                        type="string",
                        description="要格式化的数据（JSON 字符串）"
                    ),
                    ToolParameter(
                        name="indent",
                        type="number",
                        description="缩进空格数",
                        required=False
                    )
                ],
                function=self.format_json
            )
        ]

    def execute(self, operation: str, **kwargs) -> Any:
        if operation == "parse":
            return self.parse_json(kwargs["json_string"])
        elif operation == "format":
            return self.format_json(kwargs["data"], kwargs.get("indent", 2))

    def parse_json(self, json_string: str) -> Any:
        """解析 JSON 字符串"""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析错误: {str(e)}")

    def format_json(self, data: str, indent: int = 2) -> str:
        """格式化 JSON"""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式化错误: {str(e)}")
