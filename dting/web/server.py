"""
DTing Flask Web 服务器
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from ..api.routes import api_bp
from ..core.config import config


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'dting-secret-key-2024'
    app.config['DEBUG'] = config.get('server.debug', False)
    
    # 初始化 SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 模板目录
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    # 确保目录存在
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # 主页路由
    @app.route('/')
    def index():
        """主页"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTing - 移动应用性能监控工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .feature {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            transition: transform 0.3s ease;
        }
        
        .feature:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .feature h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .feature p {
            color: #666;
            line-height: 1.6;
        }
        
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #333;
            border: 2px solid #dee2e6;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
        }
        
        .api-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin-top: 30px;
        }
        
        .api-section h3 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .api-example {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        
        .status-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .status-card {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .status-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .status-label {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 DTing</h1>
            <p>实时移动应用性能监控工具</p>
        </header>
        
        <main class="main-content">
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">📱</div>
                    <h3>多平台支持</h3>
                    <p>支持 Android 和 iOS 设备，无需 ROOT 或越狱</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <h3>实时监控</h3>
                    <p>实时收集 CPU、内存、FPS、电池等性能指标</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <h3>可视化报告</h3>
                    <p>生成美观的性能报告和实时图表</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🔌</div>
                    <h3>API 接口</h3>
                    <p>提供 RESTful API 和 Python SDK</p>
                </div>
            </div>
            
            <div class="action-buttons">
                <a href="/monitor" class="btn btn-primary">🚀 开始监控</a>
                <a href="/devices" class="btn btn-secondary">📱 设备管理</a>
                <a href="/api/docs" class="btn btn-secondary">📖 API 文档</a>
            </div>
            
            <div class="api-section">
                <h3>🔌 快速开始 - Python API</h3>
                <div class="api-example">
# 安装 DTing
pip install dting

# Python 代码示例
from dting import AppPerformanceMonitor

# 创建监控实例
apm = AppPerformanceMonitor(
    package_name='com.example.app',
    platform='Android',
    duration=60
)

# 收集性能数据
cpu_usage = apm.collect_cpu()
memory_usage = apm.collect_memory()
fps = apm.collect_fps()

# 生成报告
apm.collect_all(report_path='./report.html')
                </div>
            </div>
        </main>
        
        <section class="status-section">
            <h3 style="text-align: center; margin-bottom: 30px;">📊 服务状态</h3>
            <div class="status-grid" id="statusGrid">
                <div class="status-card">
                    <div class="status-value" id="deviceCount">-</div>
                    <div class="status-label">连接设备</div>
                </div>
                
                <div class="status-card">
                    <div class="status-value" id="monitorCount">-</div>
                    <div class="status-label">活跃监控</div>
                </div>
                
                <div class="status-card">
                    <div class="status-value" id="uptime">-</div>
                    <div class="status-label">运行时间</div>
                </div>
                
                <div class="status-card">
                    <div class="status-value" id="version">1.0.0</div>
                    <div class="status-label">版本</div>
                </div>
            </div>
        </section>
    </div>
    
    <script>
        // 更新状态信息
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('deviceCount').textContent = data.device_count || 0;
                    document.getElementById('monitorCount').textContent = data.monitor_count || 0;
                    document.getElementById('uptime').textContent = data.uptime || '0s';
                })
                .catch(error => {
                    console.error('Failed to fetch status:', error);
                });
        }
        
        // 初始加载和定期更新
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
        """
    
    @app.route('/monitor')
    def monitor():
        """监控页面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTing - 性能监控</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .control-panel {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .form-group label {
            font-weight: bold;
            color: #333;
        }
        
        .form-group select,
        .form-group input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056b3;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-title {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        
        .metric-unit {
            font-size: 0.8em;
            color: #666;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            color: #333;
        }
        
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f1b2b8;
        }
        
        .status.warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DTing 性能监控</h1>
            
            <div class="control-panel">
                <div class="form-group">
                    <label>设备:</label>
                    <select id="deviceSelect">
                        <option value="">正在加载设备...</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>应用包名:</label>
                    <input type="text" id="packageInput" placeholder="com.example.app">
                </div>
                
                <div class="form-group">
                    <label>平台:</label>
                    <select id="platformSelect">
                        <option value="Android">Android</option>
                        <option value="iOS">iOS</option>
                    </select>
                </div>
                
                <button class="btn btn-primary" onclick="startMonitoring()">🚀 开始监控</button>
                <button class="btn btn-danger" onclick="stopMonitoring()">⏹️ 停止监控</button>
            </div>
        </div>
        
        <div id="statusMessage" class="status" style="display: none;"></div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">💻 CPU 使用率</div>
                <div class="metric-value" id="cpuValue">0</div>
                <div class="metric-unit">%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🧠 内存使用</div>
                <div class="metric-value" id="memoryValue">0</div>
                <div class="metric-unit">MB</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🎮 FPS</div>
                <div class="metric-value" id="fpsValue">0</div>
                <div class="metric-unit">Hz</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🔋 电池电量</div>
                <div class="metric-value" id="batteryValue">0</div>
                <div class="metric-unit">%</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-title">CPU 使用率趋势</div>
                <canvas id="cpuChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">内存使用趋势</div>
                <canvas id="memoryChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">FPS 趋势</div>
                <canvas id="fpsChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">电池信息</div>
                <canvas id="batteryChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        let isMonitoring = false;
        let monitorInterval = null;
        let charts = {};
        let chartData = {
            timestamps: [],
            cpu: [],
            memory: [],
            fps: [],
            battery: []
        };
        
        // 初始化图表
        function initCharts() {
            const commonOptions = {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '时间'
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            };
            
            // CPU 图表
            charts.cpu = new Chart(document.getElementById('cpuChart'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU (%)',
                        data: [],
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        y: { ...commonOptions.scales.y, max: 100 }
                    }
                }
            });
            
            // 内存图表
            charts.memory = new Chart(document.getElementById('memoryChart'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '内存 (MB)',
                        data: [],
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        fill: true
                    }]
                },
                options: commonOptions
            });
            
            // FPS 图表
            charts.fps = new Chart(document.getElementById('fpsChart'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'FPS',
                        data: [],
                        borderColor: '#45b7d1',
                        backgroundColor: 'rgba(69, 183, 209, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        y: { ...commonOptions.scales.y, max: 60 }
                    }
                }
            });
            
            // 电池图表
            charts.battery = new Chart(document.getElementById('batteryChart'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '电量 (%)',
                        data: [],
                        borderColor: '#96ceb4',
                        backgroundColor: 'rgba(150, 206, 180, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        y: { ...commonOptions.scales.y, max: 100 }
                    }
                }
            });
        }
        
        // 加载设备列表
        function loadDevices() {
            fetch('/api/devices')
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('deviceSelect');
                    select.innerHTML = '<option value="">选择设备</option>';
                    
                    if (data.devices && data.devices.length > 0) {
                        data.devices.forEach(device => {
                            const option = document.createElement('option');
                            option.value = device.device_id;
                            option.textContent = `${device.name} (${device.platform})`;
                            select.appendChild(option);
                        });
                    } else {
                        select.innerHTML = '<option value="">无可用设备</option>';
                    }
                })
                .catch(error => {
                    console.error('Failed to load devices:', error);
                    showStatus('无法加载设备列表', 'error');
                });
        }
        
        // 开始监控
        function startMonitoring() {
            const deviceId = document.getElementById('deviceSelect').value;
            const packageName = document.getElementById('packageInput').value;
            const platform = document.getElementById('platformSelect').value;
            
            if (!deviceId || !packageName) {
                showStatus('请选择设备和输入应用包名', 'error');
                return;
            }
            
            if (isMonitoring) {
                showStatus('监控已在运行中', 'warning');
                return;
            }
            
            isMonitoring = true;
            clearChartData();
            
            // 开始收集数据
            monitorInterval = setInterval(() => {
                collectPerformanceData(deviceId, packageName, platform);
            }, 2000);
            
            showStatus(`正在监控 ${packageName} (${platform})`, 'success');
        }
        
        // 停止监控
        function stopMonitoring() {
            if (!isMonitoring) {
                showStatus('监控未运行', 'warning');
                return;
            }
            
            isMonitoring = false;
            if (monitorInterval) {
                clearInterval(monitorInterval);
                monitorInterval = null;
            }
            
            showStatus('监控已停止', 'success');
        }
        
        // 收集性能数据
        function collectPerformanceData(deviceId, packageName, platform) {
            const targets = ['cpu', 'memory', 'fps', 'battery'];
            
            targets.forEach(target => {
                fetch(`/api/collect?platform=${platform}&device_id=${deviceId}&package=${packageName}&target=${target}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateMetrics(target, data.data);
                            updateChart(target, data.data);
                        }
                    })
                    .catch(error => {
                        console.error(`Failed to collect ${target}:`, error);
                    });
            });
        }
        
        // 更新指标显示
        function updateMetrics(target, value) {
            switch (target) {
                case 'cpu':
                    document.getElementById('cpuValue').textContent = typeof value === 'number' ? value.toFixed(1) : '0';
                    break;
                case 'memory':
                    document.getElementById('memoryValue').textContent = typeof value === 'number' ? value.toFixed(1) : '0';
                    break;
                case 'fps':
                    document.getElementById('fpsValue').textContent = typeof value === 'number' ? value.toFixed(1) : '0';
                    break;
                case 'battery':
                    if (value && typeof value === 'object' && value.level !== undefined) {
                        document.getElementById('batteryValue').textContent = value.level;
                    }
                    break;
            }
        }
        
        // 更新图表
        function updateChart(target, value) {
            const now = new Date();
            const timeLabel = now.toLocaleTimeString();
            
            // 限制数据点数量
            const maxDataPoints = 30;
            
            if (chartData.timestamps.length >= maxDataPoints) {
                chartData.timestamps.shift();
                chartData.cpu.shift();
                chartData.memory.shift();
                chartData.fps.shift();
                chartData.battery.shift();
            }
            
            chartData.timestamps.push(timeLabel);
            
            switch (target) {
                case 'cpu':
                    chartData.cpu.push(typeof value === 'number' ? value : 0);
                    updateChartData(charts.cpu, chartData.timestamps, chartData.cpu);
                    break;
                case 'memory':
                    chartData.memory.push(typeof value === 'number' ? value : 0);
                    updateChartData(charts.memory, chartData.timestamps, chartData.memory);
                    break;
                case 'fps':
                    chartData.fps.push(typeof value === 'number' ? value : 0);
                    updateChartData(charts.fps, chartData.timestamps, chartData.fps);
                    break;
                case 'battery':
                    const batteryLevel = (value && typeof value === 'object' && value.level !== undefined) ? value.level : 0;
                    chartData.battery.push(batteryLevel);
                    updateChartData(charts.battery, chartData.timestamps, chartData.battery);
                    break;
            }
        }
        
        // 更新图表数据
        function updateChartData(chart, labels, data) {
            chart.data.labels = [...labels];
            chart.data.datasets[0].data = [...data];
            chart.update('none');
        }
        
        // 清空图表数据
        function clearChartData() {
            chartData = {
                timestamps: [],
                cpu: [],
                memory: [],
                fps: [],
                battery: []
            };
            
            Object.values(charts).forEach(chart => {
                chart.data.labels = [];
                chart.data.datasets[0].data = [];
                chart.update();
            });
        }
        
        // 显示状态消息
        function showStatus(message, type) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            // 3秒后自动隐藏
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            loadDevices();
        });
    </script>
</body>
</html>
        """
    
    @app.route('/devices')
    def devices():
        """设备管理页面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTing - 设备管理</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056b3;
        }
        
        .devices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .device-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .device-card:hover {
            transform: translateY(-2px);
        }
        
        .device-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .device-icon {
            font-size: 2em;
            margin-right: 15px;
        }
        
        .device-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .device-id {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .device-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-connected {
            background: #d4edda;
            color: #155724;
        }
        
        .status-disconnected {
            background: #f8d7da;
            color: #721c24;
        }
        
        .device-info {
            margin: 15px 0;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        
        .info-label {
            color: #666;
        }
        
        .info-value {
            font-weight: bold;
            color: #333;
        }
        
        .device-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 0.9em;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #1e7e34;
        }
        
        .btn-info {
            background: #17a2b8;
            color: white;
        }
        
        .btn-info:hover {
            background: #117a8b;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .no-devices {
            text-align: center;
            padding: 40px;
            color: #666;
            background: white;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📱 设备管理</h1>
                <p>管理和监控连接的 Android/iOS 设备</p>
            </div>
            <button class="btn btn-primary" onclick="refreshDevices()">🔄 刷新设备</button>
        </div>
        
        <div id="devicesContainer">
            <div class="loading">
                <div style="font-size: 2em; margin-bottom: 10px;">⏳</div>
                <div>正在加载设备列表...</div>
            </div>
        </div>
    </div>
    
    <script>
        // 加载设备列表
        function loadDevices() {
            document.getElementById('devicesContainer').innerHTML = `
                <div class="loading">
                    <div style="font-size: 2em; margin-bottom: 10px;">⏳</div>
                    <div>正在加载设备列表...</div>
                </div>
            `;
            
            fetch('/api/devices')
                .then(response => response.json())
                .then(data => {
                    renderDevices(data.devices || []);
                })
                .catch(error => {
                    console.error('Failed to load devices:', error);
                    document.getElementById('devicesContainer').innerHTML = `
                        <div class="no-devices">
                            <div style="font-size: 2em; margin-bottom: 10px;">❌</div>
                            <div>加载设备列表失败</div>
                        </div>
                    `;
                });
        }
        
        // 渲染设备列表
        function renderDevices(devices) {
            const container = document.getElementById('devicesContainer');
            
            if (devices.length === 0) {
                container.innerHTML = `
                    <div class="no-devices">
                        <div style="font-size: 2em; margin-bottom: 10px;">📱</div>
                        <div>未发现连接的设备</div>
                        <div style="margin-top: 10px; color: #999;">请确保设备已连接并启用调试模式</div>
                    </div>
                `;
                return;
            }
            
            const devicesHTML = devices.map(device => {
                const icon = device.platform === 'Android' ? '🤖' : '🍎';
                const statusClass = device.connected ? 'status-connected' : 'status-disconnected';
                const statusText = device.connected ? '已连接' : '未连接';
                
                const properties = device.properties || {};
                
                return `
                    <div class="device-card">
                        <div class="device-header">
                            <div class="device-icon">${icon}</div>
                            <div>
                                <div class="device-name">${device.name}</div>
                                <div class="device-id">${device.device_id}</div>
                                <span class="device-status ${statusClass}">${statusText}</span>
                            </div>
                        </div>
                        
                        <div class="device-info">
                            <div class="info-item">
                                <span class="info-label">平台:</span>
                                <span class="info-value">${device.platform}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">品牌:</span>
                                <span class="info-value">${properties.brand || properties.name || 'Unknown'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">型号:</span>
                                <span class="info-value">${properties.model || 'Unknown'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">系统版本:</span>
                                <span class="info-value">${properties.version || 'Unknown'}</span>
                            </div>
                            ${properties.screen_size ? `
                            <div class="info-item">
                                <span class="info-label">屏幕尺寸:</span>
                                <span class="info-value">${properties.screen_size}</span>
                            </div>
                            ` : ''}
                            ${properties.battery_info && properties.battery_info.level ? `
                            <div class="info-item">
                                <span class="info-label">电池电量:</span>
                                <span class="info-value">${properties.battery_info.level}%</span>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="device-actions">
                            <button class="btn btn-success btn-sm" onclick="connectDevice('${device.device_id}')">
                                ${device.connected ? '✅ 已连接' : '🔗 连接'}
                            </button>
                            <button class="btn btn-info btn-sm" onclick="viewDeviceInfo('${device.device_id}')">
                                📋 详情
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = `<div class="devices-grid">${devicesHTML}</div>`;
        }
        
        // 刷新设备列表
        function refreshDevices() {
            fetch('/api/devices/refresh', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    loadDevices();
                })
                .catch(error => {
                    console.error('Failed to refresh devices:', error);
                });
        }
        
        // 连接设备
        function connectDevice(deviceId) {
            fetch(`/api/devices/${deviceId}/connect`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadDevices(); // 重新加载设备列表
                    } else {
                        alert('连接设备失败: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Failed to connect device:', error);
                    alert('连接设备失败');
                });
        }
        
        // 查看设备详情
        function viewDeviceInfo(deviceId) {
            fetch(`/api/devices/${deviceId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const info = JSON.stringify(data.data, null, 2);
                        alert('设备详情:\\n' + info);
                    } else {
                        alert('获取设备信息失败: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Failed to get device info:', error);
                    alert('获取设备信息失败');
                });
        }
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadDevices();
        });
    </script>
</body>
</html>
        """
    
    return app