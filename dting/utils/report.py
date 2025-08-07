"""
DTing 报告生成模块
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from ..core.collector import PerformanceData


class ReportGenerator:
    """性能报告生成器"""
    
    def __init__(
        self,
        device_info: Dict[str, Any],
        package_name: str,
        performance_data: List[PerformanceData],
        alerts: List[Dict[str, Any]],
        start_time: float,
        end_time: float
    ):
        """
        初始化报告生成器
        
        Args:
            device_info: 设备信息
            package_name: 应用包名
            performance_data: 性能数据列表
            alerts: 告警列表
            start_time: 开始时间
            end_time: 结束时间
        """
        self.device_info = device_info
        self.package_name = package_name
        self.performance_data = performance_data
        self.alerts = alerts
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
    
    def generate_html_report(self, output_path: str) -> bool:
        """
        生成HTML格式的性能报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否成功生成
        """
        try:
            # 生成报告数据
            report_data = self._generate_report_data()
            
            # 生成HTML内容
            html_content = self._generate_html_content(report_data)
            
            # 写入文件
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to generate HTML report: {e}")
            return False
    
    def _generate_report_data(self) -> Dict[str, Any]:
        """生成报告数据"""
        # 计算统计信息
        cpu_values = [d.cpu_usage for d in self.performance_data if d.cpu_usage > 0]
        memory_values = [d.memory_usage for d in self.performance_data if d.memory_usage > 0]
        fps_values = [d.fps for d in self.performance_data if d.fps > 0]
        
        # 生成时间序列数据
        timestamps = [d.timestamp for d in self.performance_data]
        
        return {
            'basic_info': {
                'package_name': self.package_name,
                'device_info': self.device_info,
                'start_time': datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S'),
                'duration': f"{self.duration:.1f}s",
                'data_points': len(self.performance_data),
                'alerts_count': len(self.alerts)
            },
            'statistics': {
                'cpu': self._calculate_stats(cpu_values),
                'memory': self._calculate_stats(memory_values),
                'fps': self._calculate_stats(fps_values)
            },
            'time_series': {
                'timestamps': [t - self.start_time for t in timestamps],  # 相对时间
                'cpu_usage': [d.cpu_usage for d in self.performance_data],
                'memory_usage': [d.memory_usage for d in self.performance_data],
                'fps': [d.fps for d in self.performance_data],
                'battery_level': [d.battery_info.get('level', 0) for d in self.performance_data],
                'battery_temp': [d.battery_info.get('temperature', 0) for d in self.performance_data]
            },
            'alerts': self.alerts
        }
    
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
    
    def _generate_html_content(self, data: Dict[str, Any]) -> str:
        """生成HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTing 性能报告 - {data['basic_info']['package_name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .info-card h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .info-label {{
            color: #666;
        }}
        .info-value {{
            font-weight: bold;
            color: #333;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-title {{
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        .stat-values {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }}
        .stat-item {{
            padding: 10px;
            background: white;
            border-radius: 4px;
        }}
        .stat-item-label {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-item-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}
        .chart-container {{
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }}
        .alert-section {{
            margin-top: 30px;
        }}
        .alert-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
        }}
        .alert-item {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .alert-time {{
            font-size: 0.9em;
            color: #666;
        }}
        .alert-message {{
            font-weight: bold;
            color: #856404;
        }}
        .no-alerts {{
            text-align: center;
            color: #28a745;
            font-weight: bold;
            padding: 20px;
            background: #d4edda;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DTing 性能报告</h1>
            <p>{data['basic_info']['package_name']} 性能监控报告</p>
        </div>
        
        <div class="content">
            <!-- 基本信息 -->
            <div class="info-grid">
                <div class="info-card">
                    <h3>📱 设备信息</h3>
                    <div class="info-item">
                        <span class="info-label">设备名称:</span>
                        <span class="info-value">{data['basic_info']['device_info'].get('name', 'Unknown')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">平台:</span>
                        <span class="info-value">{data['basic_info']['device_info'].get('platform', 'Unknown')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">设备ID:</span>
                        <span class="info-value">{data['basic_info']['device_info'].get('device_id', 'Unknown')}</span>
                    </div>
                </div>
                
                <div class="info-card">
                    <h3>⏱️ 测试信息</h3>
                    <div class="info-item">
                        <span class="info-label">开始时间:</span>
                        <span class="info-value">{data['basic_info']['start_time']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">结束时间:</span>
                        <span class="info-value">{data['basic_info']['end_time']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">持续时间:</span>
                        <span class="info-value">{data['basic_info']['duration']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">数据点数:</span>
                        <span class="info-value">{data['basic_info']['data_points']}</span>
                    </div>
                </div>
            </div>
            
            <!-- 统计信息 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">💻 CPU 使用率 (%)</div>
                    <div class="stat-values">
                        <div class="stat-item">
                            <div class="stat-item-label">最小值</div>
                            <div class="stat-item-value">{data['statistics']['cpu']['min']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">最大值</div>
                            <div class="stat-item-value">{data['statistics']['cpu']['max']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">平均值</div>
                            <div class="stat-item-value">{data['statistics']['cpu']['avg']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">样本数</div>
                            <div class="stat-item-value">{data['statistics']['cpu']['count']}</div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">🧠 内存使用 (MB)</div>
                    <div class="stat-values">
                        <div class="stat-item">
                            <div class="stat-item-label">最小值</div>
                            <div class="stat-item-value">{data['statistics']['memory']['min']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">最大值</div>
                            <div class="stat-item-value">{data['statistics']['memory']['max']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">平均值</div>
                            <div class="stat-item-value">{data['statistics']['memory']['avg']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">样本数</div>
                            <div class="stat-item-value">{data['statistics']['memory']['count']}</div>
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">🎮 FPS</div>
                    <div class="stat-values">
                        <div class="stat-item">
                            <div class="stat-item-label">最小值</div>
                            <div class="stat-item-value">{data['statistics']['fps']['min']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">最大值</div>
                            <div class="stat-item-value">{data['statistics']['fps']['max']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">平均值</div>
                            <div class="stat-item-value">{data['statistics']['fps']['avg']:.1f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">样本数</div>
                            <div class="stat-item-value">{data['statistics']['fps']['count']}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 性能图表 -->
            <div class="chart-container">
                <div class="chart-title">📈 CPU 使用率趋势</div>
                <canvas id="cpuChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📈 内存使用趋势</div>
                <canvas id="memoryChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📈 FPS 趋势</div>
                <canvas id="fpsChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🔋 电池信息</div>
                <canvas id="batteryChart" width="400" height="200"></canvas>
            </div>
            
            <!-- 告警信息 -->
            <div class="alert-section">
                <div class="alert-title">⚠️ 告警信息 ({len(data['alerts'])} 条)</div>
                {self._generate_alerts_html(data['alerts'])}
            </div>
        </div>
    </div>
    
    <script>
        // 图表数据
        const chartData = {json.dumps(data['time_series'])};
        
        // 通用图表配置
        const commonOptions = {{
            responsive: true,
            scales: {{
                x: {{
                    title: {{
                        display: true,
                        text: '时间 (秒)'
                    }}
                }},
                y: {{
                    beginAtZero: true
                }}
            }},
            plugins: {{
                legend: {{
                    display: false
                }}
            }}
        }};
        
        // CPU 图表
        new Chart(document.getElementById('cpuChart'), {{
            type: 'line',
            data: {{
                labels: chartData.timestamps,
                datasets: [{{
                    label: 'CPU使用率(%)',
                    data: chartData.cpu_usage,
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    fill: true,
                    tension: 0.3
                }}]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        title: {{
                            display: true,
                            text: 'CPU使用率 (%)'
                        }},
                        max: 100
                    }}
                }}
            }}
        }});
        
        // 内存图表
        new Chart(document.getElementById('memoryChart'), {{
            type: 'line',
            data: {{
                labels: chartData.timestamps,
                datasets: [{{
                    label: '内存使用(MB)',
                    data: chartData.memory_usage,
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    fill: true,
                    tension: 0.3
                }}]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        title: {{
                            display: true,
                            text: '内存使用 (MB)'
                        }}
                    }}
                }}
            }}
        }});
        
        // FPS 图表
        new Chart(document.getElementById('fpsChart'), {{
            type: 'line',
            data: {{
                labels: chartData.timestamps,
                datasets: [{{
                    label: 'FPS',
                    data: chartData.fps,
                    borderColor: '#45b7d1',
                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                    fill: true,
                    tension: 0.3
                }}]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        title: {{
                            display: true,
                            text: 'FPS'
                        }},
                        max: 60
                    }}
                }}
            }}
        }});
        
        // 电池图表
        new Chart(document.getElementById('batteryChart'), {{
            type: 'line',
            data: {{
                labels: chartData.timestamps,
                datasets: [{{
                    label: '电量(%)',
                    data: chartData.battery_level,
                    borderColor: '#96ceb4',
                    backgroundColor: 'rgba(150, 206, 180, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y'
                }}, {{
                    label: '温度(°C)',
                    data: chartData.battery_temp,
                    borderColor: '#feca57',
                    backgroundColor: 'rgba(254, 202, 87, 0.1)',
                    fill: false,
                    tension: 0.3,
                    yAxisID: 'y1'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: '时间 (秒)'
                        }}
                    }},
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {{
                            display: true,
                            text: '电量 (%)'
                        }},
                        min: 0,
                        max: 100
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {{
                            display: true,
                            text: '温度 (°C)'
                        }},
                        grid: {{
                            drawOnChartArea: false,
                        }},
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    def _generate_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """生成告警HTML"""
        if not alerts:
            return '<div class="no-alerts">✅ 无告警信息</div>'
        
        html = ""
        for alert in alerts:
            timestamp = datetime.fromtimestamp(alert['timestamp']).strftime('%H:%M:%S')
            html += f"""
            <div class="alert-item">
                <div class="alert-time">{timestamp}</div>
                <div class="alert-message">{alert['message']}</div>
            </div>
            """
        
        return html