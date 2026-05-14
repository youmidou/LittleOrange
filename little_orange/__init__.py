"""
LittleOrange - 一个模块化的大模型 Agent 和 Skills 系统
"""

from .agent import Agent
from .skills import Skill, SkillRegistry
from .tools import Tool, ToolRegistry

__version__ = "0.1.0"
__all__ = ["Agent", "Skill", "SkillRegistry", "Tool", "ToolRegistry"]
