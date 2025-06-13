#!/usr/bin/env python
"""
CardVerification 1Panel环境配置检查脚本
专为1Panel + OpenResty环境设计
"""

import os
import sys
import requests
import subprocess
from pathlib import Path

class Panel1ConfigChecker:
    """1Panel环境配置检查器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def log_error(self, message):
        self.errors.append(f"❌ {message}")
    
    def log_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
    
    def log_success(self, message):
        self.success.append(f"✅ {message}")
    
    def check_environment_file(self):
        """检查环境配置文件"""
        print("🔍 检查环境配置文件...")
        
        if not Path('.env').exists():
            if Path('.env.1panel.example').exists():
                self.log_warning("环境配置文件 .env 不存在，请复制 .env.1panel.example")
            else:
                self.log_error("环境配置文件不存在")
            return
        
        # 读取环境变量
        env_vars = {}
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        # 检查关键配置
        required_vars = [
            'SECRET_KEY',
            'POSTGRES_DB',
            'POSTGRES_USER', 
            'POSTGRES_PASSWORD'
        ]
        
        for var in required_vars:
            if var not in env_vars or not env_vars[var]:
                self.log_error(f"环境变量 {var} 未配置")
            else:
                self.log_success(f"环境变量 {var} 已配置")
        
        # 检查域名配置
        allowed_hosts = env_vars.get('ALLOWED_HOSTS', '')
        if 'kami.killua.tech' in allowed_hosts:
            self.log_success("域名 kami.killua.tech 已配置")
        else:
            self.log_warning("建议在 ALLOWED_HOSTS 中添加 kami.killua.tech")
    
    def check_docker_environment(self):
        """检查Docker环境"""
        print("🔍 检查Docker环境...")
        
        try:
            # 检查Docker
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success("Docker 已安装")
            else:
                self.log_error("Docker 未安装或无法访问")
        except FileNotFoundError:
            self.log_error("Docker 未安装")
        
        try:
            # 检查Docker Compose
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success("Docker Compose 已安装")
            else:
                self.log_error("Docker Compose 未安装或无法访问")
        except FileNotFoundError:
            self.log_error("Docker Compose 未安装")
    
    def check_1panel_files(self):
        """检查1Panel相关文件"""
        print("🔍 检查1Panel部署文件...")
        
        required_files = [
            'docker-compose.1panel.yml',
            'Dockerfile.1panel',
            'deploy_1panel.sh',
            'manage_1panel.sh'
        ]
        
        for file in required_files:
            if Path(file).exists():
                self.log_success(f"文件 {file} 存在")
            else:
                self.log_error(f"文件 {file} 不存在")
    
    def check_container_status(self):
        """检查容器状态"""
        print("🔍 检查容器状态...")
        
        try:
            # 检查容器是否运行
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.1panel.yml', 'ps'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                if 'Up' in result.stdout:
                    self.log_success("容器正在运行")
                else:
                    self.log_warning("容器未运行，请执行部署脚本")
            else:
                self.log_warning("无法检查容器状态")
        except Exception as e:
            self.log_warning(f"检查容器状态失败: {e}")
    
    def check_application_health(self):
        """检查应用健康状态"""
        print("🔍 检查应用健康状态...")
        
        try:
            # 检查本地应用响应
            response = requests.get('http://127.0.0.1:8000/api/v1/health/', timeout=10)
            if response.status_code == 200:
                self.log_success("应用本地访问正常")
            else:
                self.log_warning(f"应用响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("应用未启动或端口未开放")
        except Exception as e:
            self.log_warning(f"应用健康检查失败: {e}")
    
    def check_domain_access(self):
        """检查域名访问"""
        print("🔍 检查域名访问...")
        
        try:
            # 检查域名访问
            response = requests.get('https://kami.killua.tech/api/v1/health/', 
                                  timeout=10, verify=False)
            if response.status_code == 200:
                self.log_success("域名访问正常")
            else:
                self.log_warning(f"域名访问异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("域名无法访问，请检查1Panel反向代理配置")
        except Exception as e:
            self.log_warning(f"域名访问检查失败: {e}")
    
    def check_static_files(self):
        """检查静态文件"""
        print("🔍 检查静态文件...")
        
        static_dir = Path('staticfiles')
        if static_dir.exists():
            self.log_success("静态文件目录存在")
            
            # 检查关键静态文件
            css_files = list(static_dir.glob('**/*.css'))
            js_files = list(static_dir.glob('**/*.js'))
            
            if css_files:
                self.log_success(f"CSS文件已收集 ({len(css_files)} 个)")
            else:
                self.log_warning("未找到CSS文件，请运行 collectstatic")
            
            if js_files:
                self.log_success(f"JS文件已收集 ({len(js_files)} 个)")
            else:
                self.log_warning("未找到JS文件，请运行 collectstatic")
        else:
            self.log_warning("静态文件目录不存在，请运行 collectstatic")
    
    def check_logs_directory(self):
        """检查日志目录"""
        print("🔍 检查日志配置...")
        
        logs_dir = Path('logs')
        if logs_dir.exists():
            self.log_success("日志目录存在")
            
            # 检查日志文件
            log_files = ['django.log', 'gunicorn_access.log', 'gunicorn_error.log']
            for log_file in log_files:
                log_path = logs_dir / log_file
                if log_path.exists():
                    self.log_success(f"日志文件 {log_file} 存在")
                else:
                    self.log_warning(f"日志文件 {log_file} 不存在")
        else:
            self.log_warning("日志目录不存在")
    
    def generate_1panel_config(self):
        """生成1Panel配置建议"""
        print("\n📋 1Panel配置建议:")
        print("=" * 60)
        
        config_suggestions = [
            "网站管理 → 创建网站",
            "域名: kami.killua.tech",
            "类型: 反向代理",
            "代理地址: http://127.0.0.1:8000",
            "",
            "SSL配置:",
            "- 申请Let's Encrypt证书",
            "- 启用强制HTTPS",
            "",
            "反向代理规则:",
            "- /static/ → http://127.0.0.1:8000/static/",
            "- /media/ → http://127.0.0.1:8000/media/",
            "- / → http://127.0.0.1:8000",
        ]
        
        for suggestion in config_suggestions:
            print(f"  {suggestion}")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始1Panel环境配置检查...\n")
        
        self.check_environment_file()
        print()
        
        self.check_docker_environment()
        print()
        
        self.check_1panel_files()
        print()
        
        self.check_container_status()
        print()
        
        self.check_application_health()
        print()
        
        self.check_domain_access()
        print()
        
        self.check_static_files()
        print()
        
        self.check_logs_directory()
        print()
        
        self.print_summary()
        self.generate_1panel_config()
    
    def print_summary(self):
        """打印检查结果摘要"""
        print("=" * 60)
        print("📊 1Panel环境配置检查结果")
        print("=" * 60)
        
        if self.success:
            print("\n✅ 成功项目:")
            for item in self.success:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️  警告项目:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n❌ 错误项目:")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ 配置检查发现错误，请修复后重新部署")
            return False
        elif self.warnings:
            print("⚠️  配置检查发现警告，建议优化配置")
            return True
        else:
            print("✅ 配置检查通过，1Panel环境配置正常")
            return True


def main():
    """主函数"""
    checker = Panel1ConfigChecker()
    success = checker.run_all_checks()
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
