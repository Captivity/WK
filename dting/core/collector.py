"""
DTing 数据收集器模块
负责收集CPU、内存、网络、FPS、电池等性能指标
"""

import time
import json
import threading
import psutil
import re
import subprocess
from typing import Dict, Any, List, Optional, Callable
from .devices import Device, AndroidDevice, IOSDevice
from .config import config


class PerformanceData:
    """性能数据类"""
    
    def __init__(self, timestamp: float = None):
        self.timestamp = timestamp or time.time()
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.memory_detail = {}
        self.network_usage = {}
        self.fps = 0.0
        self.battery_info = {}
        self.gpu_usage = 0.0
        self.thermal_info = {}
        self.jank_info = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "memory_detail": self.memory_detail,
            "network_usage": self.network_usage,
            "fps": self.fps,
            "battery_info": self.battery_info,
            "gpu_usage": self.gpu_usage,
            "thermal_info": self.thermal_info,
            "jank_info": self.jank_info
        }


class AndroidCollector:
    """Android 性能数据收集器"""
    
    def __init__(self, device: AndroidDevice, package_name: str = ""):
        self.device = device
        self.package_name = package_name
        self.pid = None
        self.last_network_data = None
        self.last_cpu_data = None
    
    def get_pid(self) -> Optional[str]:
        """获取应用进程ID"""
        if not self.package_name:
            return None
        
        try:
            output = self.device.execute_adb(f"shell pidof {self.package_name}")
            if output:
                self.pid = output.strip().split()[0]
                return self.pid
        except:
            pass
        return None
    
    def collect_cpu(self) -> float:
        """收集CPU使用率"""
        try:
            if self.package_name and not self.pid:
                self.get_pid()
            
            if self.pid:
                # 获取进程CPU使用率
                output = self.device.execute_adb(f"shell top -p {self.pid} -n 1")
                lines = output.split('\n')
                for line in lines:
                    if self.pid in line and '%' in line:
                        # 解析CPU使用率
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if '%' in part and part.replace('%', '').replace('.', '').isdigit():
                                return float(part.replace('%', ''))
            else:
                # 获取全局CPU使用率
                output = self.device.execute_adb("shell cat /proc/stat")
                lines = output.split('\n')
                for line in lines:
                    if line.startswith('cpu '):
                        fields = line.split()
                        total_time = sum(int(x) for x in fields[1:])
                        idle_time = int(fields[4])
                        
                        if self.last_cpu_data:
                            last_total, last_idle = self.last_cpu_data
                            total_diff = total_time - last_total
                            idle_diff = idle_time - last_idle
                            
                            if total_diff > 0:
                                cpu_usage = 100.0 * (total_diff - idle_diff) / total_diff
                                self.last_cpu_data = (total_time, idle_time)
                                return cpu_usage
                        
                        self.last_cpu_data = (total_time, idle_time)
                        return 0.0
        except Exception as e:
            print(f"Failed to collect CPU data: {e}")
        return 0.0
    
    def collect_memory(self) -> float:
        """收集内存使用量 (MB)"""
        try:
            if self.package_name and not self.pid:
                self.get_pid()
            
            if self.pid:
                # 获取进程内存使用
                output = self.device.execute_adb(f"shell dumpsys meminfo {self.pid}")
                lines = output.split('\n')
                for line in lines:
                    if 'TOTAL' in line and 'kB' in line:
                        # 解析内存使用量
                        match = re.search(r'(\d+)', line)
                        if match:
                            return float(match.group(1)) / 1024  # 转换为MB
            else:
                # 获取全局内存使用
                output = self.device.execute_adb("shell cat /proc/meminfo")
                lines = output.split('\n')
                mem_total = mem_available = 0
                
                for line in lines:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])
                
                if mem_total > 0:
                    used_memory = (mem_total - mem_available) / 1024  # 转换为MB
                    return used_memory
        except Exception as e:
            print(f"Failed to collect memory data: {e}")
        return 0.0
    
    def collect_memory_detail(self) -> Dict[str, Any]:
        """收集详细内存信息"""
        try:
            if self.package_name and not self.pid:
                self.get_pid()
            
            if self.pid:
                output = self.device.execute_adb(f"shell dumpsys meminfo {self.pid}")
                lines = output.split('\n')
                
                memory_detail = {}
                for line in lines:
                    line = line.strip()
                    if 'Pss Total' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            memory_detail['pss_total'] = float(match.group(1)) / 1024
                    elif 'Private Dirty' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            memory_detail['private_dirty'] = float(match.group(1)) / 1024
                    elif 'Private Clean' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            memory_detail['private_clean'] = float(match.group(1)) / 1024
                
                return memory_detail
        except Exception as e:
            print(f"Failed to collect memory detail: {e}")
        return {}
    
    def collect_network(self, wifi: bool = True) -> Dict[str, Any]:
        """收集网络使用数据"""
        try:
            if self.package_name and not self.pid:
                self.get_pid()
            
            if self.pid:
                # 获取应用网络使用
                uid_output = self.device.execute_adb(f"shell cat /proc/{self.pid}/status")
                uid = None
                for line in uid_output.split('\n'):
                    if line.startswith('Uid:'):
                        uid = line.split()[1]
                        break
                
                if uid:
                    rx_output = self.device.execute_adb(f"shell cat /proc/net/xt_qtaguid/stats | grep {uid}")
                    
                    rx_bytes = tx_bytes = 0
                    for line in rx_output.split('\n'):
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 8:
                                rx_bytes += int(parts[5])
                                tx_bytes += int(parts[7])
                    
                    current_data = {
                        'rx_bytes': rx_bytes,
                        'tx_bytes': tx_bytes,
                        'timestamp': time.time()
                    }
                    
                    if self.last_network_data:
                        time_diff = current_data['timestamp'] - self.last_network_data['timestamp']
                        if time_diff > 0:
                            rx_speed = (rx_bytes - self.last_network_data['rx_bytes']) / time_diff / 1024  # KB/s
                            tx_speed = (tx_bytes - self.last_network_data['tx_bytes']) / time_diff / 1024  # KB/s
                            
                            self.last_network_data = current_data
                            return {
                                'rx_speed': rx_speed,
                                'tx_speed': tx_speed,
                                'rx_total': rx_bytes / 1024,  # KB
                                'tx_total': tx_bytes / 1024   # KB
                            }
                    
                    self.last_network_data = current_data
        except Exception as e:
            print(f"Failed to collect network data: {e}")
        
        return {'rx_speed': 0, 'tx_speed': 0, 'rx_total': 0, 'tx_total': 0}
    
    def collect_fps(self) -> float:
        """收集FPS数据"""
        try:
            if not self.package_name:
                return 0.0
            
            # 使用 gfxinfo 获取FPS
            output = self.device.execute_adb(f"shell dumpsys gfxinfo {self.package_name}")
            lines = output.split('\n')
            
            # 查找最近的帧渲染时间
            frame_times = []
            in_frame_stats = False
            
            for line in lines:
                if 'Total frames rendered:' in line:
                    in_frame_stats = True
                    continue
                elif in_frame_stats and line.strip():
                    try:
                        time_value = float(line.strip().split()[0])
                        if time_value > 0:
                            frame_times.append(time_value)
                    except (ValueError, IndexError):
                        continue
                
                if len(frame_times) >= 120:  # 获取最近120帧
                    break
            
            if frame_times:
                avg_frame_time = sum(frame_times[-60:]) / len(frame_times[-60:])  # 最近60帧
                if avg_frame_time > 0:
                    fps = 1000.0 / avg_frame_time  # 转换为FPS
                    return min(fps, 60.0)  # 限制最大60FPS
        except Exception as e:
            print(f"Failed to collect FPS data: {e}")
        return 0.0
    
    def collect_battery(self) -> Dict[str, Any]:
        """收集电池信息"""
        try:
            output = self.device.execute_adb("shell dumpsys battery")
            battery_info = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if 'level:' in line:
                    battery_info['level'] = int(line.split(':')[1].strip())
                elif 'temperature:' in line:
                    battery_info['temperature'] = int(line.split(':')[1].strip()) / 10
                elif 'voltage:' in line:
                    battery_info['voltage'] = int(line.split(':')[1].strip())
                elif 'current now:' in line:
                    battery_info['current'] = int(line.split(':')[1].strip())
                elif 'status:' in line:
                    battery_info['status'] = line.split(':')[1].strip()
            
            # 计算功率
            if 'voltage' in battery_info and 'current' in battery_info:
                battery_info['power'] = abs(battery_info['voltage'] * battery_info['current'] / 1000000)
            
            return battery_info
        except Exception as e:
            print(f"Failed to collect battery data: {e}")
        return {}
    
    def collect_gpu(self) -> float:
        """收集GPU使用率"""
        try:
            # 尝试获取GPU信息
            output = self.device.execute_adb("shell cat /sys/class/kgsl/kgsl-3d0/gpubusy")
            if output:
                busy_time, total_time = map(int, output.split())
                if total_time > 0:
                    return (busy_time / total_time) * 100
        except:
            # 尝试其他GPU监控方式
            try:
                output = self.device.execute_adb("shell cat /proc/mali/utilization")
                if output and '%' in output:
                    match = re.search(r'(\d+)%', output)
                    if match:
                        return float(match.group(1))
            except:
                pass
        return 0.0
    
    def collect_thermal(self) -> Dict[str, Any]:
        """收集热量信息"""
        try:
            thermal_info = {}
            
            # 获取CPU温度
            try:
                output = self.device.execute_adb("shell cat /sys/class/thermal/thermal_zone*/temp")
                temperatures = []
                for line in output.split('\n'):
                    if line.strip().isdigit():
                        temp = int(line.strip()) / 1000  # 转换为摄氏度
                        temperatures.append(temp)
                
                if temperatures:
                    thermal_info['cpu_temp'] = max(temperatures)
            except:
                pass
            
            # 获取电池温度 (从battery信息中获取)
            battery_info = self.collect_battery()
            if 'temperature' in battery_info:
                thermal_info['battery_temp'] = battery_info['temperature']
            
            return thermal_info
        except Exception as e:
            print(f"Failed to collect thermal data: {e}")
        return {}


class IOSCollector:
    """iOS 性能数据收集器"""
    
    def __init__(self, device: IOSDevice, package_name: str = ""):
        self.device = device
        self.package_name = package_name
        self.last_network_data = None
    
    def collect_cpu(self) -> float:
        """收集CPU使用率"""
        try:
            if self.package_name:
                output = self.device.execute_ios_command(f"proc_info {self.package_name}")
                # 解析iOS应用CPU使用率
                for line in output.split('\n'):
                    if 'CPU' in line:
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            return float(match.group(1))
            else:
                # 获取系统CPU使用率
                output = self.device.execute_ios_command("sysinfo")
                for line in output.split('\n'):
                    if 'CPU Usage' in line:
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            return float(match.group(1))
        except Exception as e:
            print(f"Failed to collect iOS CPU data: {e}")
        return 0.0
    
    def collect_memory(self) -> float:
        """收集内存使用量 (MB)"""
        try:
            if self.package_name:
                output = self.device.execute_ios_command(f"proc_info {self.package_name}")
                # 解析iOS应用内存使用
                for line in output.split('\n'):
                    if 'Memory' in line:
                        match = re.search(r'(\d+\.?\d*)\s*MB', line)
                        if match:
                            return float(match.group(1))
            else:
                # 获取系统内存使用
                output = self.device.execute_ios_command("sysinfo")
                for line in output.split('\n'):
                    if 'Memory' in line:
                        match = re.search(r'(\d+\.?\d*)\s*MB', line)
                        if match:
                            return float(match.group(1))
        except Exception as e:
            print(f"Failed to collect iOS memory data: {e}")
        return 0.0
    
    def collect_network(self, wifi: bool = True) -> Dict[str, Any]:
        """收集网络使用数据"""
        try:
            output = self.device.execute_ios_command("network_info")
            network_data = {'rx_speed': 0, 'tx_speed': 0, 'rx_total': 0, 'tx_total': 0}
            
            for line in output.split('\n'):
                if 'RX:' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        network_data['rx_total'] = int(match.group(1)) / 1024  # KB
                elif 'TX:' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        network_data['tx_total'] = int(match.group(1)) / 1024  # KB
            
            # 计算速率
            current_time = time.time()
            if self.last_network_data:
                time_diff = current_time - self.last_network_data['timestamp']
                if time_diff > 0:
                    network_data['rx_speed'] = (network_data['rx_total'] - self.last_network_data['rx_total']) / time_diff
                    network_data['tx_speed'] = (network_data['tx_total'] - self.last_network_data['tx_total']) / time_diff
            
            self.last_network_data = {
                'rx_total': network_data['rx_total'],
                'tx_total': network_data['tx_total'],
                'timestamp': current_time
            }
            
            return network_data
        except Exception as e:
            print(f"Failed to collect iOS network data: {e}")
        return {'rx_speed': 0, 'tx_speed': 0, 'rx_total': 0, 'tx_total': 0}
    
    def collect_fps(self) -> float:
        """收集FPS数据"""
        try:
            if self.package_name:
                output = self.device.execute_ios_command(f"fps {self.package_name}")
                match = re.search(r'(\d+\.?\d*)\s*fps', output)
                if match:
                    return float(match.group(1))
        except Exception as e:
            print(f"Failed to collect iOS FPS data: {e}")
        return 0.0
    
    def collect_battery(self) -> Dict[str, Any]:
        """收集电池信息"""
        try:
            output = self.device.execute_ios_command("battery")
            battery_info = {}
            
            for line in output.split('\n'):
                if 'BatteryLevel' in line:
                    match = re.search(r'(\d+\.?\d*)', line)
                    if match:
                        battery_info['level'] = int(float(match.group(1)) * 100)
                elif 'Temperature' in line:
                    match = re.search(r'(\d+\.?\d*)', line)
                    if match:
                        battery_info['temperature'] = float(match.group(1))
                elif 'Voltage' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        battery_info['voltage'] = int(match.group(1))
            
            return battery_info
        except Exception as e:
            print(f"Failed to collect iOS battery data: {e}")
        return {}


class DataCollector:
    """数据收集器主类"""
    
    def __init__(self, device: Device, package_name: str = ""):
        self.device = device
        self.package_name = package_name
        self.is_collecting = False
        self.collection_thread = None
        self.data_buffer: List[PerformanceData] = []
        self.max_buffer_size = config.get("data.buffer_size", 1000)
        self.callbacks: List[Callable[[PerformanceData], None]] = []
        
        # 根据设备类型创建对应的收集器
        if isinstance(device, AndroidDevice):
            self.collector = AndroidCollector(device, package_name)
        elif isinstance(device, IOSDevice):
            self.collector = IOSCollector(device, package_name)
        else:
            raise ValueError(f"Unsupported device type: {type(device)}")
    
    def add_callback(self, callback: Callable[[PerformanceData], None]) -> None:
        """添加数据回调函数"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[PerformanceData], None]) -> None:
        """移除数据回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def collect_single(self, target: str) -> Any:
        """收集单个性能指标"""
        try:
            if target == 'cpu':
                return self.collector.collect_cpu()
            elif target == 'memory':
                return self.collector.collect_memory()
            elif target == 'memory_detail':
                return self.collector.collect_memory_detail()
            elif target == 'network':
                return self.collector.collect_network()
            elif target == 'fps':
                return self.collector.collect_fps()
            elif target == 'battery':
                return self.collector.collect_battery()
            elif target == 'gpu':
                return self.collector.collect_gpu()
            elif target == 'thermal':
                return self.collector.collect_thermal()
            else:
                raise ValueError(f"Unknown target: {target}")
        except Exception as e:
            print(f"Failed to collect {target}: {e}")
            return None
    
    def collect_all(self) -> PerformanceData:
        """收集所有性能指标"""
        data = PerformanceData()
        
        try:
            data.cpu_usage = self.collector.collect_cpu()
            data.memory_usage = self.collector.collect_memory()
            data.memory_detail = self.collector.collect_memory_detail()
            data.network_usage = self.collector.collect_network()
            data.fps = self.collector.collect_fps()
            data.battery_info = self.collector.collect_battery()
            
            if hasattr(self.collector, 'collect_gpu'):
                data.gpu_usage = self.collector.collect_gpu()
            if hasattr(self.collector, 'collect_thermal'):
                data.thermal_info = self.collector.collect_thermal()
                
        except Exception as e:
            print(f"Failed to collect all data: {e}")
        
        return data
    
    def start_continuous_collection(self, interval: float = 1.0, duration: Optional[float] = None) -> None:
        """开始连续收集数据"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval, duration)
        )
        self.collection_thread.start()
    
    def stop_continuous_collection(self) -> None:
        """停止连续收集数据"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join()
    
    def _collection_loop(self, interval: float, duration: Optional[float]) -> None:
        """数据收集循环"""
        start_time = time.time()
        
        while self.is_collecting:
            try:
                # 检查是否超过持续时间
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # 收集数据
                data = self.collect_all()
                
                # 添加到缓冲区
                self.data_buffer.append(data)
                
                # 限制缓冲区大小
                if len(self.data_buffer) > self.max_buffer_size:
                    self.data_buffer.pop(0)
                
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(data)
                    except Exception as e:
                        print(f"Callback error: {e}")
                
                # 等待下次收集
                time.sleep(interval)
                
            except Exception as e:
                print(f"Collection loop error: {e}")
                time.sleep(interval)
        
        self.is_collecting = False
    
    def get_recent_data(self, count: int = 10) -> List[PerformanceData]:
        """获取最近的数据"""
        return self.data_buffer[-count:] if count <= len(self.data_buffer) else self.data_buffer.copy()
    
    def clear_buffer(self) -> None:
        """清空数据缓冲区"""
        self.data_buffer.clear()
    
    def export_data(self, file_path: str, format: str = "json") -> bool:
        """导出数据到文件"""
        try:
            data_list = [data.to_dict() for data in self.data_buffer]
            
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, indent=2, ensure_ascii=False)
            elif format.lower() == "csv":
                import pandas as pd
                df = pd.DataFrame(data_list)
                df.to_csv(file_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
        except Exception as e:
            print(f"Failed to export data: {e}")
            return False