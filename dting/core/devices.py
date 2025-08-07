"""
DTing 设备管理模块
负责 Android 和 iOS 设备的发现、连接和管理
"""

import subprocess
import json
import time
import re
from typing import List, Dict, Any, Optional, Union
from .config import config


class Device:
    """设备基类"""
    
    def __init__(self, device_id: str, platform: str, name: str = ""):
        """
        初始化设备
        
        Args:
            device_id: 设备ID
            platform: 平台类型 (Android/iOS)
            name: 设备名称
        """
        self.device_id = device_id
        self.platform = platform
        self.name = name or device_id
        self.connected = False
        self.properties = {}
    
    def __str__(self) -> str:
        return f"{self.platform} Device: {self.name} ({self.device_id})"
    
    def __repr__(self) -> str:
        return f"Device(id='{self.device_id}', platform='{self.platform}', name='{self.name}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "device_id": self.device_id,
            "platform": self.platform,
            "name": self.name,
            "connected": self.connected,
            "properties": self.properties
        }


class AndroidDevice(Device):
    """Android 设备类"""
    
    def __init__(self, device_id: str, name: str = ""):
        super().__init__(device_id, "Android", name)
        self.adb_path = config.get("android.adb_path", "adb")
    
    def execute_adb(self, command: str, timeout: int = 30) -> str:
        """
        执行 ADB 命令
        
        Args:
            command: ADB 命令
            timeout: 超时时间
            
        Returns:
            命令输出
        """
        full_command = f"{self.adb_path} -s {self.device_id} {command}"
        try:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise RuntimeError(f"ADB command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"ADB command timeout: {command}")
        except Exception as e:
            raise RuntimeError(f"ADB command error: {e}")
    
    def get_properties(self) -> Dict[str, Any]:
        """获取设备属性"""
        try:
            # 获取设备基本信息
            brand = self.execute_adb("shell getprop ro.product.brand")
            model = self.execute_adb("shell getprop ro.product.model") 
            version = self.execute_adb("shell getprop ro.build.version.release")
            sdk = self.execute_adb("shell getprop ro.build.version.sdk")
            cpu_abi = self.execute_adb("shell getprop ro.product.cpu.abi")
            
            self.properties = {
                "brand": brand,
                "model": model,
                "version": version,
                "sdk": sdk,
                "cpu_abi": cpu_abi,
                "screen_size": self._get_screen_size(),
                "battery_info": self._get_battery_info()
            }
            return self.properties
        except Exception as e:
            print(f"Failed to get Android device properties: {e}")
            return {}
    
    def _get_screen_size(self) -> str:
        """获取屏幕尺寸"""
        try:
            output = self.execute_adb("shell wm size")
            match = re.search(r'(\d+)x(\d+)', output)
            if match:
                return f"{match.group(1)}x{match.group(2)}"
        except:
            pass
        return "Unknown"
    
    def _get_battery_info(self) -> Dict[str, Any]:
        """获取电池信息"""
        try:
            output = self.execute_adb("shell dumpsys battery")
            battery_info = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if 'level:' in line:
                    battery_info['level'] = int(line.split(':')[1].strip())
                elif 'temperature:' in line:
                    battery_info['temperature'] = int(line.split(':')[1].strip()) / 10
                elif 'voltage:' in line:
                    battery_info['voltage'] = int(line.split(':')[1].strip())
            
            return battery_info
        except:
            return {}
    
    def get_running_apps(self) -> List[str]:
        """获取运行中的应用包名"""
        try:
            output = self.execute_adb("shell pm list packages -3")
            packages = []
            for line in output.split('\n'):
                if line.startswith('package:'):
                    packages.append(line.replace('package:', '').strip())
            return packages
        except:
            return []
    
    def get_pid(self, package_name: str) -> List[str]:
        """获取应用进程ID"""
        try:
            output = self.execute_adb(f"shell ps | grep {package_name}")
            pids = []
            for line in output.split('\n'):
                if package_name in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pids.append(f"{parts[1]}:{package_name}")
            return pids
        except:
            return []


class IOSDevice(Device):
    """iOS 设备类"""
    
    def __init__(self, device_id: str, name: str = ""):
        super().__init__(device_id, "iOS", name)
        self.use_tidevice = config.get("ios.use_tidevice", True)
    
    def execute_ios_command(self, command: str, timeout: int = 30) -> str:
        """
        执行 iOS 命令
        
        Args:
            command: iOS 命令
            timeout: 超时时间
            
        Returns:
            命令输出
        """
        if self.use_tidevice:
            full_command = f"tidevice -u {self.device_id} {command}"
        else:
            # 使用其他 iOS 工具
            full_command = f"ios-deploy -i {self.device_id} {command}"
        
        try:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise RuntimeError(f"iOS command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"iOS command timeout: {command}")
        except Exception as e:
            raise RuntimeError(f"iOS command error: {e}")
    
    def get_properties(self) -> Dict[str, Any]:
        """获取设备属性"""
        try:
            if self.use_tidevice:
                output = self.execute_ios_command("info")
                info = json.loads(output)
                
                self.properties = {
                    "name": info.get("DeviceName", ""),
                    "model": info.get("ProductType", ""),
                    "version": info.get("ProductVersion", ""),
                    "identifier": info.get("UniqueDeviceID", ""),
                    "architecture": info.get("CPUArchitecture", ""),
                    "battery_level": self._get_battery_level()
                }
            return self.properties
        except Exception as e:
            print(f"Failed to get iOS device properties: {e}")
            return {}
    
    def _get_battery_level(self) -> int:
        """获取电池电量"""
        try:
            if self.use_tidevice:
                output = self.execute_ios_command("battery")
                # 解析电池信息
                for line in output.split('\n'):
                    if 'BatteryLevel' in line:
                        return int(float(line.split(':')[1].strip()) * 100)
        except:
            pass
        return -1
    
    def get_running_apps(self) -> List[str]:
        """获取运行中的应用"""
        try:
            if self.use_tidevice:
                output = self.execute_ios_command("ps")
                apps = []
                lines = output.split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            apps.append(parts[2])  # 应用包名
                return apps
        except:
            pass
        return []


class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.devices: List[Device] = []
        self.connected_devices: Dict[str, Device] = {}
    
    def discover_devices(self) -> List[Device]:
        """发现所有连接的设备"""
        devices = []
        
        # 发现 Android 设备
        devices.extend(self._discover_android_devices())
        
        # 发现 iOS 设备
        devices.extend(self._discover_ios_devices())
        
        self.devices = devices
        return devices
    
    def _discover_android_devices(self) -> List[AndroidDevice]:
        """发现 Android 设备"""
        devices = []
        adb_path = config.get("android.adb_path", "adb")
        
        try:
            # 执行 adb devices 命令
            result = subprocess.run(
                [adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                for line in lines:
                    if line.strip() and '\t' in line:
                        device_id, status = line.split('\t')
                        if status == 'device':
                            device = AndroidDevice(device_id)
                            device.connected = True
                            # 获取设备名称
                            try:
                                model = device.execute_adb("shell getprop ro.product.model")
                                device.name = f"{model} ({device_id})"
                            except:
                                device.name = device_id
                            devices.append(device)
        except Exception as e:
            print(f"Failed to discover Android devices: {e}")
        
        return devices
    
    def _discover_ios_devices(self) -> List[IOSDevice]:
        """发现 iOS 设备"""
        devices = []
        
        try:
            # 使用 tidevice 或其他工具发现 iOS 设备
            result = subprocess.run(
                ["tidevice", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    try:
                        device_list = json.loads(output)
                        for device_info in device_list:
                            device_id = device_info.get("udid", "")
                            device_name = device_info.get("name", device_id)
                            
                            if device_id:
                                device = IOSDevice(device_id, device_name)
                                device.connected = True
                                devices.append(device)
                    except json.JSONDecodeError:
                        # 如果输出不是 JSON，尝试解析文本格式
                        lines = output.split('\n')
                        for line in lines:
                            if line.strip():
                                device_id = line.strip()
                                device = IOSDevice(device_id)
                                device.connected = True
                                devices.append(device)
        except FileNotFoundError:
            # tidevice 未安装
            print("Warning: tidevice not found, iOS device discovery disabled")
        except Exception as e:
            print(f"Failed to discover iOS devices: {e}")
        
        return devices
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """根据设备ID获取设备"""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_devices_by_platform(self, platform: str) -> List[Device]:
        """根据平台获取设备列表"""
        return [device for device in self.devices if device.platform.lower() == platform.lower()]
    
    def connect_device(self, device_id: str) -> bool:
        """连接设备"""
        device = self.get_device(device_id)
        if device:
            # 更新设备属性
            device.get_properties()
            self.connected_devices[device_id] = device
            return True
        return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """断开设备连接"""
        if device_id in self.connected_devices:
            device = self.connected_devices[device_id]
            device.connected = False
            del self.connected_devices[device_id]
            return True
        return False
    
    def get_connected_devices(self) -> List[Device]:
        """获取已连接的设备列表"""
        return list(self.connected_devices.values())
    
    def refresh_devices(self) -> List[Device]:
        """刷新设备列表"""
        return self.discover_devices()
    
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取设备详细信息"""
        device = self.get_device(device_id)
        if device:
            device.get_properties()
            return device.to_dict()
        return {}
    
    def get_pid(self, device_id: str, package_name: str) -> List[str]:
        """获取应用进程ID"""
        device = self.get_device(device_id)
        if device and hasattr(device, 'get_pid'):
            return device.get_pid(package_name)
        return []