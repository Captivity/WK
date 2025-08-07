# DTing

DTing - Real-time collection tool for Android/iOS performance data (类似 SoloX 的性能测试工具)

![DTing Logo](https://img.shields.io/badge/DTing-v1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS-orange.svg)

## 🔎 预览

DTing 是一个实时的 Android/iOS 性能数据收集工具。

快速定位和分析性能问题，提高应用性能和质量。无需 ROOT/越狱，即插即用。

## 📦 环境要求

* 安装 Python 3.8+
* 安装 adb 并配置环境变量 (Android 测试需要)
* 对于 iOS 测试，需要安装 iTunes (Windows) 或 Xcode Command Line Tools (macOS)

## 📥 安装

### 使用 pip 安装

```bash
pip install -U dting
```

### 从源码安装

```bash
git clone https://github.com/dting-team/DTing.git
cd DTing
pip install -r requirements.txt
python setup.py install
```

## 🚀 快速开始

### 默认启动

```bash
python -m dting
```

### 自定义配置

```bash
python -m dting --host=0.0.0.0 --port=8080
```

### 使用命令行工具

```bash
# 启动服务器
dting-server

# 启动主程序
dting
```

## 🏴󠁣󠁩󠁣󠁭󠁿 Python API

```python
from dting.core.apm import AppPerformanceMonitor
from dting.core.devices import DeviceManager

# 获取设备列表
dm = DeviceManager()
devices = dm.get_devices()
print(devices)

# 创建性能监控实例
apm = AppPerformanceMonitor(
    package_name='com.example.app',
    platform='Android',
    device_id='your_device_id',
    collect_all=True,
    duration=60
)

# 收集单个性能指标
cpu_usage = apm.collect_cpu()  # %
memory_usage = apm.collect_memory()  # MB
fps = apm.collect_fps()  # Hz
battery_info = apm.collect_battery()  # level:%, temperature:°C
network_info = apm.collect_network()  # KB/s

# 收集所有性能指标
if __name__ == '__main__':
    apm.collect_all(report_path='./performance_report.html')
```

## 🏴󠁣󠁩󠁣󠁭󠁿 服务 API

### 启动后台服务

```bash
# macOS/Linux
nohup python3 -m dting &

# Windows
start /min python3 -m dting &
```

### 通过 API 请求性能数据

**Android:**
```
http://localhost:8080/api/collect?platform=Android&device_id=your_device&package=com.example.app&target=cpu
```

**iOS:**
```
http://localhost:8080/api/collect?platform=iOS&device_id=your_device&package=com.example.app&target=memory
```

支持的 target 参数：`cpu`, `memory`, `memory_detail`, `network`, `fps`, `battery`, `gpu`, `thermal`

## 🔥 特性

* **无需 ROOT/越狱：** Android 设备无需 Root，iOS 设备无需越狱。高效解决 Android 和 iOS 性能测试分析难题。
* **数据完整性：** 提供 CPU、GPU、内存、电池、网络、FPS、卡顿等多维度数据。
* **美观报告：** 提供美观详细的报告分析，可视化、编辑、管理和下载所有测试用例。
* **实用监控设置：** 支持设置报警值、收集时长等，支持远程设备监控。
* **对比模式：** 支持两台移动设备的同时对比测试。
  * 🌱2-设备：在两台不同手机上测试同一应用。
  * 🌱2-应用：在配置相同的两台手机上测试不同应用。
* **Python/API 集成：** 支持 Python 和 API 收集性能数据，方便集成到自动化测试流程。

## 📊 支持的性能指标

### CPU
应用进程的 CPU 占用百分比和全局 CPU 占用百分比。

### 内存
应用进程的 PSS 内存、Private Dirty 内存和全局内存占用。

### FPS
应用实际帧率、延迟帧数、单帧最长延迟时间和延迟帧占比。

### 网络
应用上下行速率、累计流量和全局网络数据。

### 电池
设备瞬时电流、电流均值、温度、电压等信息。

### GPU
GPU 使用率和相关性能数据。

### 热量
设备温度监控数据。

## 🌐 Web 界面

DTing 提供现代化的 Web 界面，包括：

* 实时性能监控面板
* 历史数据分析图表
* 设备管理和配置
* 测试报告生成和导出
* 性能对比分析

访问地址：`http://localhost:8080`

## 🛠️ 开发

### 项目结构

```
DTing/
├── dting/
│   ├── core/           # 核心功能模块
│   ├── web/           # Web 界面
│   ├── api/           # API 接口
│   ├── devices/       # 设备处理
│   ├── utils/         # 工具函数
│   └── templates/     # 模板文件
├── tests/             # 测试文件
├── docs/              # 文档
└── setup.py          # 安装配置
```

### 运行开发版本

```bash
git clone https://github.com/dting-team/DTing.git
cd DTing
pip install -r requirements.txt
python -m dting.main
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

* 灵感来源于 [SoloX](https://github.com/smart-test-ti/SoloX) 项目
* 使用了 Flask、Socket.IO 等优秀的开源库
