# backend/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录路径
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'

# 加载 .env 文件
load_dotenv(dotenv_path=env_path)

class Config:
    """通用配置类"""
    FIGMA_TOKEN = os.getenv("FIGMA_ACCESS_TOKEN")
    API_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = os.getenv("DEBUG", "False") == "True"

    @classmethod
    def validate(cls):
        """检查必要配置是否存在"""
        if not cls.FIGMA_TOKEN:
            raise ValueError("❌ 错误: 未在 .env 文件中找到 FIGMA_ACCESS_TOKEN")
        print("✅ 配置加载成功")

# 导出实例供其他模块使用
config = Config()