"""
DTing - Real-time collection tool for Android/iOS performance data
一个类似 SoloX 的性能测试工具

Author: DTing Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "DTing Team"
__license__ = "MIT"

from .core.apm import AppPerformanceMonitor
from .core.devices import DeviceManager
from .core.config import Config

__all__ = [
    "AppPerformanceMonitor",
    "DeviceManager", 
    "Config",
]