"""
DTing API 路由模块
提供所有 RESTful API 端点
"""

import time
from flask import Blueprint, request, jsonify
from ..core.devices import DeviceManager
from ..core.apm import AppPerformanceMonitor, performance_service
from ..core.collector import DataCollector
from ..core.config import config


# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局设备管理器
device_manager = DeviceManager()

# 服务启动时间
start_time = time.time()


@api_bp.route('/status')
def get_status():
    """获取服务状态"""
    try:
        # 发现设备
        devices = device_manager.discover_devices()
        connected_devices = device_manager.get_connected_devices()
        
        # 计算运行时间
        uptime_seconds = int(time.time() - start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if hours > 0:
            uptime = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            uptime = f"{minutes}m {seconds}s"
        else:
            uptime = f"{seconds}s"
        
        return jsonify({
            'success': True,
            'data': {
                'device_count': len(connected_devices),
                'monitor_count': len(performance_service.list_monitors()),
                'uptime': uptime,
                'version': '1.0.0'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/devices')
def get_devices():
    """获取设备列表"""
    try:
        devices = device_manager.discover_devices()
        devices_data = [device.to_dict() for device in devices]
        
        return jsonify({
            'success': True,
            'devices': devices_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/devices/refresh', methods=['POST'])
def refresh_devices():
    """刷新设备列表"""
    try:
        devices = device_manager.refresh_devices()
        devices_data = [device.to_dict() for device in devices]
        
        return jsonify({
            'success': True,
            'devices': devices_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/devices/<device_id>')
def get_device_info(device_id):
    """获取设备详细信息"""
    try:
        device_info = device_manager.get_device_info(device_id)
        
        if not device_info:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': device_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/devices/<device_id>/connect', methods=['POST'])
def connect_device(device_id):
    """连接设备"""
    try:
        success = device_manager.connect_device(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device connected successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to connect device'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/devices/<device_id>/disconnect', methods=['POST'])
def disconnect_device(device_id):
    """断开设备连接"""
    try:
        success = device_manager.disconnect_device(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device disconnected successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to disconnect device'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/collect')
def collect_performance_data():
    """收集性能数据"""
    try:
        # 获取参数
        platform = request.args.get('platform', 'Android')
        device_id = request.args.get('device_id')
        package_name = request.args.get('package', '')
        target = request.args.get('target', 'cpu')
        
        # 验证参数
        if not device_id:
            return jsonify({
                'success': False,
                'error': 'device_id is required'
            }), 400
        
        if not package_name:
            return jsonify({
                'success': False,
                'error': 'package is required'
            }), 400
        
        # 获取设备
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # 创建数据收集器
        collector = DataCollector(device, package_name)
        
        # 收集数据
        data = collector.collect_single(target)
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitor/start', methods=['POST'])
def start_monitor():
    """启动监控"""
    try:
        data = request.get_json()
        
        # 验证参数
        required_fields = ['monitor_id', 'package_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        monitor_id = data['monitor_id']
        package_name = data['package_name']
        platform = data.get('platform', 'Android')
        device_id = data.get('device_id')
        duration = data.get('duration', 0)
        
        # 启动监控
        success = performance_service.start_monitor(
            monitor_id=monitor_id,
            package_name=package_name,
            platform=platform,
            device_id=device_id,
            duration=duration
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Monitor started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start monitor'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitor/stop', methods=['POST'])
def stop_monitor():
    """停止监控"""
    try:
        data = request.get_json()
        
        if 'monitor_id' not in data:
            return jsonify({
                'success': False,
                'error': 'monitor_id is required'
            }), 400
        
        monitor_id = data['monitor_id']
        
        # 停止监控
        success = performance_service.stop_monitor(monitor_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Monitor stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Monitor not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitor/list')
def list_monitors():
    """获取监控列表"""
    try:
        monitors = performance_service.list_monitors()
        
        return jsonify({
            'success': True,
            'monitors': monitors
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitor/<monitor_id>/status')
def get_monitor_status(monitor_id):
    """获取监控状态"""
    try:
        monitor = performance_service.get_monitor(monitor_id)
        
        if not monitor:
            return jsonify({
                'success': False,
                'error': 'Monitor not found'
            }), 404
        
        summary = monitor.get_summary()
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitor/<monitor_id>/data')
def get_monitor_data(monitor_id):
    """获取监控数据"""
    try:
        monitor = performance_service.get_monitor(monitor_id)
        
        if not monitor:
            return jsonify({
                'success': False,
                'error': 'Monitor not found'
            }), 404
        
        # 获取最近的数据
        count = request.args.get('count', 10, type=int)
        recent_data = monitor.collector.get_recent_data(count)
        
        # 转换为字典格式
        data_list = [data.to_dict() for data in recent_data]
        
        return jsonify({
            'success': True,
            'data': data_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/pid')
def get_pid():
    """获取应用进程ID"""
    try:
        device_id = request.args.get('device_id')
        package_name = request.args.get('package')
        
        if not device_id or not package_name:
            return jsonify({
                'success': False,
                'error': 'device_id and package are required'
            }), 400
        
        # 获取进程ID
        pids = device_manager.get_pid(device_id, package_name)
        
        return jsonify({
            'success': True,
            'data': pids
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/config')
def get_config():
    """获取配置信息"""
    try:
        return jsonify({
            'success': True,
            'data': config.config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 更新配置
        config.update(data)
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/docs')
def api_docs():
    """API 文档"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTing API 文档</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .content {
            padding: 30px;
        }
        
        h1, h2, h3 {
            color: #333;
        }
        
        .endpoint {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8em;
            margin-right: 10px;
        }
        
        .get { background: #28a745; color: white; }
        .post { background: #007bff; color: white; }
        .put { background: #ffc107; color: black; }
        .delete { background: #dc3545; color: white; }
        
        .code {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        
        .params {
            margin: 15px 0;
        }
        
        .param {
            margin: 5px 0;
            padding: 5px 10px;
            background: #e9ecef;
            border-radius: 4px;
            font-family: monospace;
        }
        
        .toc {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .toc ul {
            list-style: none;
            padding-left: 20px;
        }
        
        .toc a {
            color: #007bff;
            text-decoration: none;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 DTing API 文档</h1>
            <p>移动应用性能监控 RESTful API 接口文档</p>
        </div>
        
        <div class="content">
            <div class="toc">
                <h3>目录</h3>
                <ul>
                    <li><a href="#status">服务状态</a></li>
                    <li><a href="#devices">设备管理</a></li>
                    <li><a href="#collect">数据收集</a></li>
                    <li><a href="#monitor">监控管理</a></li>
                    <li><a href="#config">配置管理</a></li>
                    <li><a href="#examples">使用示例</a></li>
                </ul>
            </div>
            
            <h2 id="status">🔍 服务状态</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/status</h3>
                <p>获取服务运行状态和统计信息</p>
                <div class="code">
{
  "success": true,
  "data": {
    "device_count": 2,
    "monitor_count": 1,
    "uptime": "2h 30m 15s",
    "version": "1.0.0"
  }
}
                </div>
            </div>
            
            <h2 id="devices">📱 设备管理</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/devices</h3>
                <p>获取所有连接的设备列表</p>
                <div class="code">
{
  "success": true,
  "devices": [
    {
      "device_id": "emulator-5554",
      "platform": "Android",
      "name": "Android Emulator",
      "connected": true,
      "properties": {
        "brand": "Google",
        "model": "sdk_gphone64_x86_64",
        "version": "13"
      }
    }
  ]
}
                </div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span>/api/devices/refresh</h3>
                <p>刷新设备列表，重新扫描连接的设备</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/devices/{device_id}</h3>
                <p>获取指定设备的详细信息</p>
                <div class="params">
                    <div class="param">device_id: 设备ID</div>
                </div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span>/api/devices/{device_id}/connect</h3>
                <p>连接指定设备</p>
            </div>
            
            <h2 id="collect">📊 数据收集</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/collect</h3>
                <p>收集指定应用的性能数据</p>
                <div class="params">
                    <strong>查询参数:</strong>
                    <div class="param">platform: 平台类型 (Android/iOS)</div>
                    <div class="param">device_id: 设备ID</div>
                    <div class="param">package: 应用包名</div>
                    <div class="param">target: 数据类型 (cpu/memory/fps/battery/network/gpu)</div>
                </div>
                <div class="code">
GET /api/collect?platform=Android&device_id=emulator-5554&package=com.example.app&target=cpu

{
  "success": true,
  "data": 25.6,
  "timestamp": 1640995200.123
}
                </div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/pid</h3>
                <p>获取应用进程ID</p>
                <div class="params">
                    <strong>查询参数:</strong>
                    <div class="param">device_id: 设备ID</div>
                    <div class="param">package: 应用包名</div>
                </div>
            </div>
            
            <h2 id="monitor">🎯 监控管理</h2>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span>/api/monitor/start</h3>
                <p>启动性能监控</p>
                <div class="code">
{
  "monitor_id": "test_monitor_1",
  "package_name": "com.example.app",
  "platform": "Android",
  "device_id": "emulator-5554",
  "duration": 60
}
                </div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span>/api/monitor/stop</h3>
                <p>停止指定监控</p>
                <div class="code">
{
  "monitor_id": "test_monitor_1"
}
                </div>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/monitor/list</h3>
                <p>获取所有活跃监控列表</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/monitor/{monitor_id}/status</h3>
                <p>获取监控状态和摘要信息</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/monitor/{monitor_id}/data</h3>
                <p>获取监控收集的性能数据</p>
                <div class="params">
                    <strong>查询参数:</strong>
                    <div class="param">count: 返回的数据点数量 (默认10)</div>
                </div>
            </div>
            
            <h2 id="config">⚙️ 配置管理</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span>/api/config</h3>
                <p>获取当前配置</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span>/api/config</h3>
                <p>更新配置</p>
                <div class="code">
{
  "monitoring.interval": 2.0,
  "alert.cpu_threshold": 85.0
}
                </div>
            </div>
            
            <h2 id="examples">💡 使用示例</h2>
            
            <h3>Python 示例</h3>
            <div class="code">
import requests

# 获取设备列表
response = requests.get('http://localhost:8080/api/devices')
devices = response.json()['devices']

# 收集CPU数据
params = {
    'platform': 'Android',
    'device_id': 'emulator-5554',
    'package': 'com.example.app',
    'target': 'cpu'
}
response = requests.get('http://localhost:8080/api/collect', params=params)
cpu_usage = response.json()['data']

print(f"CPU使用率: {cpu_usage}%")
            </div>
            
            <h3>curl 示例</h3>
            <div class="code">
# 获取服务状态
curl http://localhost:8080/api/status

# 刷新设备列表
curl -X POST http://localhost:8080/api/devices/refresh

# 收集内存数据
curl "http://localhost:8080/api/collect?platform=Android&device_id=emulator-5554&package=com.example.app&target=memory"

# 启动监控
curl -X POST http://localhost:8080/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{
    "monitor_id": "test_1",
    "package_name": "com.example.app",
    "platform": "Android",
    "device_id": "emulator-5554"
  }'
            </div>
            
            <h3>响应格式</h3>
            <p>所有 API 响应都遵循统一格式：</p>
            <div class="code">
{
  "success": true|false,
  "data": {...},           // 成功时的数据
  "error": "error message", // 失败时的错误信息
  "timestamp": 1640995200.123  // 某些接口包含时间戳
}
            </div>
            
            <h3>错误码</h3>
            <ul>
                <li><strong>200</strong> - 成功</li>
                <li><strong>400</strong> - 请求参数错误</li>
                <li><strong>404</strong> - 资源不存在</li>
                <li><strong>500</strong> - 服务器内部错误</li>
            </ul>
        </div>
    </div>
</body>
</html>
    """


# 错误处理
@api_bp.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """405 错误处理"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500