"""
DTing Web 模块
包含 Flask Web 服务器和前端界面
"""

from .server import create_app

__all__ = [
    "create_app",
]