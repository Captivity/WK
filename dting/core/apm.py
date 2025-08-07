"""
DTing 应用性能监控模块 (APM)
类似 SoloX 的核心功能，提供移动应用性能监控
"""

import time
import os
import json
import threading
from typing import Dict, Any, Optional, List, Union
from .devices import DeviceManager, Device, AndroidDevice, IOSDevice
from .collector import DataCollector, PerformanceData
from .config import config
from ..utils.logger import Logger
from ..utils.report import ReportGenerator


class AppPerformanceMonitor:
    """应用性能监控器 - DTing 的核心类"""
    
    def __init__(
        self,
        package_name: str,
        platform: str = "Android",
        device_id: Optional[str] = None,
        surfaceview: bool = True,
        no_log: bool = False,
        pid: Optional[str] = None,
        record: bool = False,
        collect_all: bool = False,
        duration: int = 0
    ):
        """
        初始化应用性能监控器
        
        Args:
            package_name: 应用包名
            platform: 平台类型 (Android/iOS)
            device_id: 设备ID，None则自动选择第一个设备
            surfaceview: 是否使用surfaceview模式
            no_log: 是否禁用日志记录
            pid: 进程ID
            record: 是否录制屏幕
            collect_all: 是否收集所有性能指标
            duration: 监控持续时间（秒），0表示无限制
        """
        self.package_name = package_name
        self.platform = platform.lower()
        self.device_id = device_id
        self.surfaceview = surfaceview
        self.no_log = no_log
        self.pid = pid
        self.record = record
        self.collect_all = collect_all
        self.duration = duration
        
        # 初始化组件
        self.device_manager = DeviceManager()
        self.device: Optional[Device] = None
        self.collector: Optional[DataCollector] = None
        self.logger: Optional[Logger] = None
        self.is_monitoring = False
        self.start_time = 0
        
        # 性能数据
        self.performance_data: List[PerformanceData] = []
        self.alerts: List[Dict[str, Any]] = []
        
        # 初始化
        self._initialize()
    
    def _initialize(self) -> None:
        """初始化监控器"""
        try:
            # 发现设备
            devices = self.device_manager.discover_devices()
            if not devices:
                raise RuntimeError("No devices found")
            
            # 选择设备
            if self.device_id:
                self.device = self.device_manager.get_device(self.device_id)
                if not self.device:
                    raise RuntimeError(f"Device {self.device_id} not found")
            else:
                # 根据平台选择第一个设备
                platform_devices = self.device_manager.get_devices_by_platform(self.platform)
                if not platform_devices:
                    raise RuntimeError(f"No {self.platform} devices found")
                self.device = platform_devices[0]
                self.device_id = self.device.device_id
            
            # 连接设备
            if not self.device_manager.connect_device(self.device_id):
                raise RuntimeError(f"Failed to connect to device {self.device_id}")
            
            # 创建数据收集器
            self.collector = DataCollector(self.device, self.package_name)
            
            # 设置日志记录
            if not self.no_log:
                self.logger = Logger(f"dting_{self.device_id}_{self.package_name}")
                self.logger.info(f"Initialized APM for {self.package_name} on {self.device}")
            
            print(f"✅ DTing initialized for {self.package_name} on {self.device}")
            
        except Exception as e:
            print(f"❌ Failed to initialize DTing: {e}")
            raise
    
    def collect_cpu(self) -> float:
        """
        收集CPU使用率
        
        Returns:
            CPU使用率百分比
        """
        if not self.collector:
            return 0.0
        
        cpu_usage = self.collector.collect_single('cpu')
        if cpu_usage is None:
            cpu_usage = 0.0
        
        # 检查告警
        self._check_alert('cpu', cpu_usage)
        
        if self.logger:
            self.logger.debug(f"CPU Usage: {cpu_usage}%")
        
        return cpu_usage
    
    def collect_memory(self) -> float:
        """
        收集内存使用量
        
        Returns:
            内存使用量 (MB)
        """
        if not self.collector:
            return 0.0
        
        memory_usage = self.collector.collect_single('memory')
        if memory_usage is None:
            memory_usage = 0.0
        
        # 检查告警
        self._check_alert('memory', memory_usage)
        
        if self.logger:
            self.logger.debug(f"Memory Usage: {memory_usage} MB")
        
        return memory_usage
    
    def collect_memory_detail(self) -> Dict[str, Any]:
        """
        收集详细内存信息
        
        Returns:
            详细内存信息字典
        """
        if not self.collector:
            return {}
        
        memory_detail = self.collector.collect_single('memory_detail')
        if memory_detail is None:
            memory_detail = {}
        
        if self.logger:
            self.logger.debug(f"Memory Detail: {memory_detail}")
        
        return memory_detail
    
    def collect_network(self, wifi: bool = True) -> Dict[str, Any]:
        """
        收集网络使用数据
        
        Args:
            wifi: 是否监控WiFi网络
            
        Returns:
            网络使用数据字典
        """
        if not self.collector:
            return {}
        
        network_data = self.collector.collect_single('network')
        if network_data is None:
            network_data = {}
        
        if self.logger:
            self.logger.debug(f"Network Usage: {network_data}")
        
        return network_data
    
    def collect_fps(self) -> float:
        """
        收集FPS数据
        
        Returns:
            FPS值
        """
        if not self.collector:
            return 0.0
        
        fps = self.collector.collect_single('fps')
        if fps is None:
            fps = 0.0
        
        # 检查告警
        self._check_alert('fps', fps)
        
        if self.logger:
            self.logger.debug(f"FPS: {fps}")
        
        return fps
    
    def collect_battery(self) -> Dict[str, Any]:
        """
        收集电池信息
        
        Returns:
            电池信息字典
        """
        if not self.collector:
            return {}
        
        battery_info = self.collector.collect_single('battery')
        if battery_info is None:
            battery_info = {}
        
        # 检查电池温度告警
        if 'temperature' in battery_info:
            self._check_alert('battery_temp', battery_info['temperature'])
        
        if self.logger:
            self.logger.debug(f"Battery Info: {battery_info}")
        
        return battery_info
    
    def collect_gpu(self) -> float:
        """
        收集GPU使用率
        
        Returns:
            GPU使用率百分比
        """
        if not self.collector:
            return 0.0
        
        gpu_usage = self.collector.collect_single('gpu')
        if gpu_usage is None:
            gpu_usage = 0.0
        
        if self.logger:
            self.logger.debug(f"GPU Usage: {gpu_usage}%")
        
        return gpu_usage
    
    def collect_thermal(self) -> Dict[str, Any]:
        """
        收集热量信息
        
        Returns:
            热量信息字典
        """
        if not self.collector:
            return {}
        
        thermal_info = self.collector.collect_single('thermal')
        if thermal_info is None:
            thermal_info = {}
        
        if self.logger:
            self.logger.debug(f"Thermal Info: {thermal_info}")
        
        return thermal_info
    
    def collect_all(self, report_path: Optional[str] = None) -> None:
        """
        收集所有性能指标
        
        Args:
            report_path: 报告保存路径
        """
        if not self.collector:
            print("❌ Collector not initialized")
            return
        
        print(f"🚀 Starting performance monitoring for {self.package_name}")
        print(f"📱 Device: {self.device}")
        print(f"⏱️  Duration: {self.duration}s" if self.duration > 0 else "⏱️  Duration: Unlimited")
        
        # 添加数据回调
        self.collector.add_callback(self._on_data_collected)
        
        # 开始收集
        self.is_monitoring = True
        self.start_time = time.time()
        
        try:
            interval = config.get("monitoring.interval", 1.0)
            duration = self.duration if self.duration > 0 else None
            
            self.collector.start_continuous_collection(interval, duration)
            
            if self.logger:
                self.logger.info("Started continuous performance monitoring")
            
            # 等待收集完成
            if duration:
                # 有限时长监控
                time.sleep(duration)
                self.stop_monitoring()
            else:
                # 无限时长监控，等待手动停止
                try:
                    while self.is_monitoring:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n⏹️  Monitoring stopped by user")
                    self.stop_monitoring()
        
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            if self.logger:
                self.logger.error(f"Monitoring error: {e}")
        
        finally:
            # 生成报告
            if report_path:
                self.generate_report(report_path)
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.collector:
            self.collector.stop_continuous_collection()
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        print(f"⏹️  Monitoring stopped after {duration:.1f}s")
        print(f"📊 Collected {len(self.performance_data)} data points")
        
        if self.logger:
            self.logger.info(f"Monitoring stopped after {duration:.1f}s")
    
    def _on_data_collected(self, data: PerformanceData) -> None:
        """数据收集回调"""
        self.performance_data.append(data)
        
        # 实时输出关键指标
        if len(self.performance_data) % 10 == 0:  # 每10次输出一次
            self._print_realtime_stats(data)
    
    def _print_realtime_stats(self, data: PerformanceData) -> None:
        """打印实时统计信息"""
        elapsed = time.time() - self.start_time
        print(f"\r⏱️  {elapsed:6.1f}s | "
              f"CPU: {data.cpu_usage:5.1f}% | "
              f"MEM: {data.memory_usage:6.1f}MB | "
              f"FPS: {data.fps:4.1f} | "
              f"BAT: {data.battery_info.get('level', 0):3d}%", end="")
    
    def _check_alert(self, metric: str, value: Union[int, float]) -> None:
        """检查告警条件"""
        thresholds = {
            'cpu': config.get("alert.cpu_threshold", 80.0),
            'memory': config.get("alert.memory_threshold", 80.0),
            'fps': config.get("alert.fps_threshold", 30.0),
            'battery_temp': config.get("alert.battery_temp_threshold", 45.0)
        }
        
        if metric in thresholds:
            threshold = thresholds[metric]
            
            # FPS是低于阈值告警，其他是高于阈值告警
            is_alert = value < threshold if metric == 'fps' else value > threshold
            
            if is_alert:
                alert = {
                    'timestamp': time.time(),
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'message': f'{metric.upper()} {"below" if metric == "fps" else "above"} threshold: {value} {"<" if metric == "fps" else ">"} {threshold}'
                }
                self.alerts.append(alert)
                
                print(f"\n⚠️  ALERT: {alert['message']}")
                
                if self.logger:
                    self.logger.warning(alert['message'])
    
    def generate_report(self, report_path: str) -> bool:
        """
        生成性能报告
        
        Args:
            report_path: 报告保存路径
            
        Returns:
            是否成功生成报告
        """
        try:
            if not self.performance_data:
                print("❌ No performance data to generate report")
                return False
            
            print(f"📊 Generating performance report...")
            
            # 创建报告生成器
            report_generator = ReportGenerator(
                device_info=self.device.to_dict(),
                package_name=self.package_name,
                performance_data=self.performance_data,
                alerts=self.alerts,
                start_time=self.start_time,
                end_time=time.time()
            )
            
            # 生成HTML报告
            success = report_generator.generate_html_report(report_path)
            
            if success:
                print(f"✅ Report generated: {report_path}")
                if self.logger:
                    self.logger.info(f"Report generated: {report_path}")
            else:
                print(f"❌ Failed to generate report")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to generate report: {e}")
            if self.logger:
                self.logger.error(f"Failed to generate report: {e}")
            return False
    
    def export_data(self, file_path: str, format: str = "json") -> bool:
        """
        导出性能数据
        
        Args:
            file_path: 导出文件路径
            format: 导出格式 (json/csv)
            
        Returns:
            是否成功导出
        """
        if not self.collector:
            return False
        
        return self.collector.export_data(file_path, format)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要字典
        """
        if not self.performance_data:
            return {}
        
        # 计算统计信息
        cpu_values = [d.cpu_usage for d in self.performance_data if d.cpu_usage > 0]
        memory_values = [d.memory_usage for d in self.performance_data if d.memory_usage > 0]
        fps_values = [d.fps for d in self.performance_data if d.fps > 0]
        
        summary = {
            'device': self.device.to_dict() if self.device else {},
            'package_name': self.package_name,
            'duration': time.time() - self.start_time if self.start_time else 0,
            'data_points': len(self.performance_data),
            'alerts_count': len(self.alerts),
            'stats': {
                'cpu': self._calculate_stats(cpu_values),
                'memory': self._calculate_stats(memory_values),
                'fps': self._calculate_stats(fps_values)
            }
        }
        
        return summary
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """计算统计信息"""
        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.is_monitoring:
            self.stop_monitoring()
        
        if self.device_manager and self.device_id:
            self.device_manager.disconnect_device(self.device_id)


# 全局监控服务实例
class PerformanceService:
    """性能监控服务"""
    
    def __init__(self):
        self.monitors: Dict[str, AppPerformanceMonitor] = {}
        self.is_running = False
    
    def start_monitor(
        self,
        monitor_id: str,
        package_name: str,
        platform: str = "Android",
        device_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """启动监控"""
        try:
            if monitor_id in self.monitors:
                print(f"Monitor {monitor_id} already exists")
                return False
            
            monitor = AppPerformanceMonitor(
                package_name=package_name,
                platform=platform,
                device_id=device_id,
                **kwargs
            )
            
            self.monitors[monitor_id] = monitor
            self.is_running = True
            
            print(f"✅ Started monitor: {monitor_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start monitor {monitor_id}: {e}")
            return False
    
    def stop_monitor(self, monitor_id: str) -> bool:
        """停止监控"""
        if monitor_id not in self.monitors:
            print(f"Monitor {monitor_id} not found")
            return False
        
        try:
            monitor = self.monitors[monitor_id]
            monitor.stop_monitoring()
            del self.monitors[monitor_id]
            
            if not self.monitors:
                self.is_running = False
            
            print(f"✅ Stopped monitor: {monitor_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop monitor {monitor_id}: {e}")
            return False
    
    def stop_all(self) -> None:
        """停止所有监控"""
        for monitor_id in list(self.monitors.keys()):
            self.stop_monitor(monitor_id)
        self.is_running = False
        print("✅ All monitors stopped")
    
    def get_monitor(self, monitor_id: str) -> Optional[AppPerformanceMonitor]:
        """获取监控实例"""
        return self.monitors.get(monitor_id)
    
    def list_monitors(self) -> List[str]:
        """获取监控列表"""
        return list(self.monitors.keys())


# 全局服务实例
performance_service = PerformanceService()