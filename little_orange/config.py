"""
配置管理系统
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class LittleOrangeConfig:
    """LittleOrange 配置"""

    # LLM 配置
    llm_provider: str = "claude"  # claude, openai, mock
    model: str = "claude-sonnet-4-6"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

    # Agent 配置
    max_iterations: int = 10
    system_prompt: Optional[str] = None

    # 技能配置
    enabled_skills: list = None

    def __post_init__(self):
        if self.enabled_skills is None:
            self.enabled_skills = [
                "calculator",
                "file_operations",
                "datetime",
                "data_processing"
            ]

    @classmethod
    def from_file(cls, config_path: str) -> 'LittleOrangeConfig':
        """从配置文件加载"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        return cls(**config_dict)

    @classmethod
    def from_env(cls) -> 'LittleOrangeConfig':
        """从环境变量加载"""
        return cls(
            llm_provider=os.getenv("LITTLE_ORANGE_PROVIDER", "claude"),
            model=os.getenv("LITTLE_ORANGE_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LITTLE_ORANGE_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LITTLE_ORANGE_MAX_TOKENS", "4096")),
            max_iterations=int(os.getenv("LITTLE_ORANGE_MAX_ITERATIONS", "10"))
        )

    def to_file(self, config_path: str):
        """保存到配置文件"""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
