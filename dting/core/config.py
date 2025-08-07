"""
DTing 配置管理模块
"""

import os
import json
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or os.path.join(
            os.path.expanduser("~"), ".dting", "config.json"
        )
        self._config = self._load_default_config()
        
        # 如果配置文件存在，加载配置
        if os.path.exists(self.config_file):
            self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False
            },
            "monitoring": {
                "interval": 1.0,  # 监控间隔(秒)
                "max_duration": 3600,  # 最大监控时长(秒)
                "auto_save": True,
                "save_path": "./logs"
            },
            "android": {
                "adb_path": "adb",
                "timeout": 30
            },
            "ios": {
                "timeout": 30,
                "use_tidevice": True
            },
            "data": {
                "buffer_size": 1000,
                "export_format": "json",
                "compress": True
            },
            "alert": {
                "cpu_threshold": 80.0,
                "memory_threshold": 80.0,
                "fps_threshold": 30.0,
                "battery_temp_threshold": 45.0
            },
            "ui": {
                "theme": "light",
                "language": "zh_CN",
                "auto_refresh": True,
                "refresh_interval": 2
            }
        }
    
    def load_config(self) -> None:
        """从文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self._merge_config(self._config, file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_file}: {e}")
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Failed to save config file {self.config_file}: {e}")
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> None:
        """合并用户配置和默认配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分割的层级访问，如 'server.port'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分割的层级访问
            value: 配置值
            save: 是否立即保存到文件
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        if save:
            self.save_config()
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> None:
        """
        批量更新配置
        
        Args:
            updates: 更新的配置字典
            save: 是否立即保存到文件
        """
        for key, value in updates.items():
            self.set(key, value, save=False)
        
        if save:
            self.save_config()
    
    def reset(self, save: bool = True) -> None:
        """
        重置为默认配置
        
        Args:
            save: 是否立即保存到文件
        """
        self._config = self._load_default_config()
        
        if save:
            self.save_config()
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self._config.copy()


# 全局配置实例
config = Config()