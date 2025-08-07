"""
DTing 日志记录模块
"""

import os
import time
import logging
from typing import Optional
from ..core.config import config


class Logger:
    """DTing 日志记录器"""
    
    def __init__(self, name: str, log_dir: Optional[str] = None):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录，None则使用配置中的路径
        """
        self.name = name
        self.log_dir = log_dir or config.get("monitoring.save_path", "./logs")
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件路径
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"{name}_{timestamp}.log")
        
        # 配置日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """设置日志处理器"""
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录错误"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """记录严重错误"""
        self.logger.critical(message)