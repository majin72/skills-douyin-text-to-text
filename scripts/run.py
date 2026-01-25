#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动检测并使用虚拟环境的启动脚本
如果虚拟环境不存在，会自动创建
"""

import os
import sys
import subprocess
from pathlib import Path


def get_venv_path():
    """获取虚拟环境路径"""
    script_dir = Path(__file__).parent
    return script_dir / "venv"


def get_python_command(venv_path):
    """获取虚拟环境中的python命令路径"""
    if sys.platform == "win32":
        python_cmd = venv_path / "Scripts" / "python.exe"
    else:
        python_cmd = venv_path / "bin" / "python"
    
    if not python_cmd.exists():
        return None
    return python_cmd


def check_and_setup_venv():
    """检查并设置虚拟环境"""
    venv_path = get_venv_path()
    
    # 如果虚拟环境不存在，创建它
    if not venv_path.exists():
        print("虚拟环境不存在，正在创建...")
        try:
            # 直接创建虚拟环境
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✅ 虚拟环境创建成功")
            
            # 安装基础依赖
            pip_cmd = get_pip_command(venv_path)
            if pip_cmd and pip_cmd.exists():
                print("正在安装基础依赖...")
                subprocess.run(
                    [str(pip_cmd), "install", "--upgrade", "pip", "--quiet"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                subprocess.run(
                    [str(pip_cmd), "install", "requests>=2.20.0", "urllib3>=1.24.0", "--quiet"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print("✅ 基础依赖安装完成")
                print("💡 提示：如需使用转文字功能，请运行: python scripts/setup_venv.py 安装 FunASR")
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建虚拟环境失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 创建虚拟环境失败: {e}")
            return None
    
    python_cmd = get_python_command(venv_path)
    if not python_cmd or not python_cmd.exists():
        print("❌ 无法找到虚拟环境中的Python")
        return None
    
    return python_cmd


def get_pip_command(venv_path):
    """获取虚拟环境中的pip命令路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def main():
    """主函数"""
    # 检查虚拟环境
    venv_python = check_and_setup_venv()
    if not venv_python:
        print("⚠️  使用系统Python运行（可能缺少依赖）")
        venv_python = sys.executable
    
    # 获取主脚本路径
    script_dir = Path(__file__).parent
    main_script = script_dir / "parse_douyin_video.py"
    
    if not main_script.exists():
        print(f"❌ 找不到主脚本: {main_script}")
        return 1
    
    # 运行主脚本
    os.execv(str(venv_python), [str(venv_python), str(main_script)] + sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
