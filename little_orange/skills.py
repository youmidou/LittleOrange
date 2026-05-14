"""
Skills 管理系统 - 定义技能接口和注册表
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Skill(ABC):
    """
    技能基类 - 所有技能必须继承此类

    技能是 agent 可以执行的高级能力，每个技能可以提供一个或多个工具
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_tools(self) -> List['Tool']:
        """
        返回此技能提供的工具列表

        Returns:
            工具列表
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行技能的主要功能

        Args:
            **kwargs: 技能参数

        Returns:
            执行结果
        """
        pass

    def __repr__(self):
        return f"Skill(name='{self.name}', description='{self.description}')"


class SkillRegistry:
    """
    技能注册表 - 管理所有可用的技能
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill):
        """注册一个技能"""
        if skill.name in self._skills:
            raise ValueError(f"技能 '{skill.name}' 已经注册")
        self._skills[skill.name] = skill

    def unregister(self, skill_name: str):
        """注销一个技能"""
        if skill_name in self._skills:
            del self._skills[skill_name]

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取指定技能"""
        return self._skills.get(skill_name)

    def list_skills(self) -> List[Skill]:
        """列出所有已注册的技能"""
        return list(self._skills.values())

    def get_skill_descriptions(self) -> Dict[str, str]:
        """获取所有技能的描述"""
        return {
            name: skill.description
            for name, skill in self._skills.items()
        }

    def __len__(self):
        return len(self._skills)

    def __repr__(self):
        return f"SkillRegistry(skills={len(self._skills)})"
