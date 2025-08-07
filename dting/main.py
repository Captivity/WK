"""
DTing 主程序入口
"""

import argparse
import sys
import signal
import threading
from typing import Optional
from .core.apm import AppPerformanceMonitor, performance_service
from .core.config import config
from .web.server import create_app


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 接收到退出信号，正在停止所有监控...")
    performance_service.stop_all()
    sys.exit(0)


def run_cli_monitor(args):
    """运行命令行监控"""
    try:
        print("🚀 DTing 命令行模式启动")
        print(f"📱 应用包名: {args.package}")
        print(f"🔧 平台: {args.platform}")
        
        # 创建监控实例
        apm = AppPerformanceMonitor(
            package_name=args.package,
            platform=args.platform,
            device_id=args.device,
            surfaceview=args.surfaceview,
            no_log=args.no_log,
            collect_all=True,
            duration=args.duration
        )
        
        # 开始监控
        report_path = args.report if args.report else f"./logs/{args.package}_report.html"
        apm.collect_all(report_path=report_path)
        
    except KeyboardInterrupt:
        print("\n⏹️  监控被用户中断")
    except Exception as e:
        print(f"❌ 监控失败: {e}")
        sys.exit(1)


def run_web_server(args):
    """运行Web服务器"""
    try:
        print("🌐 DTing Web 服务器启动")
        print(f"🔗 访问地址: http://{args.host}:{args.port}")
        
        # 创建Flask应用
        app = create_app()
        
        # 启动服务器
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Web服务器启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="DTing - Real-time collection tool for Android/iOS performance data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动Web界面
  python -m dting --web
  
  # 监控Android应用
  python -m dting --package com.example.app --platform Android --duration 60
  
  # 监控iOS应用并生成报告
  python -m dting --package com.example.app --platform iOS --report ./report.html
  
  # 自定义Web服务器
  python -m dting --web --host 0.0.0.0 --port 8080
        """
    )
    
    # 通用参数
    parser.add_argument('--version', action='version', version='DTing 1.0.0')
    parser.add_argument('--config', type=str, help='配置文件路径')
    
    # 运行模式
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--web', action='store_true', help='启动Web服务器模式')
    mode_group.add_argument('--package', type=str, help='要监控的应用包名')
    
    # Web服务器参数
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Web服务器主机地址')
    parser.add_argument('--port', type=int, default=8080, help='Web服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # 监控参数
    parser.add_argument('--platform', type=str, choices=['Android', 'iOS'], default='Android', help='目标平台')
    parser.add_argument('--device', type=str, help='设备ID')
    parser.add_argument('--duration', type=int, default=0, help='监控持续时间（秒），0表示无限制')
    parser.add_argument('--report', type=str, help='报告输出路径')
    parser.add_argument('--surfaceview', action='store_true', default=True, help='使用surfaceview模式')
    parser.add_argument('--no-log', action='store_true', help='禁用日志记录')
    
    args = parser.parse_args()
    
    # 加载配置文件
    if args.config:
        config.config_file = args.config
        config.load_config()
    
    # 更新配置
    if args.host != '0.0.0.0':
        config.set('server.host', args.host, save=False)
    if args.port != 8080:
        config.set('server.port', args.port, save=False)
    if args.debug:
        config.set('server.debug', True, save=False)
    
    # 确定运行模式
    if args.web or (not args.package):
        # Web服务器模式
        run_web_server(args)
    else:
        # 命令行监控模式
        if not args.package:
            parser.error("监控模式需要指定 --package 参数")
        run_cli_monitor(args)


if __name__ == '__main__':
    main()