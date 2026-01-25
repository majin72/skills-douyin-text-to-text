#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置虚拟环境并安装依赖
"""

import os
import sys
import subprocess
from pathlib import Path


def get_venv_path():
    """获取虚拟环境路径"""
    script_dir = Path(__file__).parent
    return script_dir / "venv"


def create_venv(venv_path):
    """创建虚拟环境"""
    print(f"正在创建虚拟环境: {venv_path}")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建虚拟环境失败: {e}")
        return False


def get_pip_command(venv_path):
    """获取虚拟环境中的pip命令路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip"
    else:
        return venv_path / "bin" / "pip"


def get_python_command(venv_path):
    """获取虚拟环境中的python命令路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python"
    else:
        return venv_path / "bin" / "python"


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}")
        print("   FunASR 需要 Python >= 3.8")
        return False
    return True


def install_requirements(venv_path, install_funasr=False):
    """安装依赖"""
    pip_cmd = get_pip_command(venv_path)
    
    # 基础依赖
    requirements = ["requests>=2.20.0", "urllib3>=1.24.0"]
    
    if install_funasr:
        # 检查Python版本
        python_cmd = get_python_command(venv_path)
        if python_cmd and python_cmd.exists():
            try:
                result = subprocess.run(
                    [str(python_cmd), "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version_str = result.stdout.strip()
                print(f"当前Python版本: {version_str}")
            except:
                pass
        
        if not check_python_version():
            print("⚠️  警告: Python版本可能不满足FunASR要求，但将继续尝试安装")
        
        # FunASR的前置依赖
        print("正在安装FunASR前置依赖...")
        funasr_deps = ["torch>=1.13", "torchaudio"]
        requirements.extend(funasr_deps)
        requirements.append("funasr>=1.0.0")
    
    print(f"正在安装依赖: {', '.join(requirements)}")
    
    try:
        # 升级pip
        print("升级pip...")
        subprocess.run(
            [str(pip_cmd), "install", "--upgrade", "pip"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 安装依赖
        for req in requirements:
            print(f"  安装 {req}...")
            subprocess.run(
                [str(pip_cmd), "install", req],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖失败: {e}")
        if install_funasr:
            print("\n💡 提示: FunASR安装可能需要较长时间，请确保:")
            print("   1. Python版本 >= 3.8")
            print("   2. 网络连接稳定")
            print("   3. 有足够的磁盘空间（模型文件较大）")
        return False


def main():
    """主函数"""
    venv_path = get_venv_path()
    
    # 检查虚拟环境是否已存在
    if venv_path.exists():
        print(f"虚拟环境已存在: {venv_path}")
        response = input("是否重新创建虚拟环境？(y/N): ").strip().lower()
        if response == 'y':
            import shutil
            print("正在删除旧虚拟环境...")
            shutil.rmtree(venv_path)
        else:
            print("使用现有虚拟环境")
            # 检查是否需要安装FunASR
            pip_cmd = get_pip_command(venv_path)
            try:
                result = subprocess.run(
                    [str(pip_cmd), "show", "funasr"],
                    capture_output=True,
                    text=True
                )
                has_funasr = result.returncode == 0
            except:
                has_funasr = False
            
            if not has_funasr:
                response = input("是否安装FunASR（转文字功能需要）？(y/N): ").strip().lower()
                if response == 'y':
                    print("\n⚠️  注意: FunASR需要以下前置依赖:")
                    print("   - Python >= 3.8")
                    print("   - torch >= 1.13")
                    print("   - torchaudio")
                    print("这些依赖将自动安装...\n")
                    install_requirements(venv_path, install_funasr=True)
            return 0
    
    # 创建虚拟环境
    if not create_venv(venv_path):
        return 1
    
    # 询问是否安装FunASR
    install_funasr = False
    response = input("是否安装FunASR（转文字功能需要）？(y/N): ").strip().lower()
    if response == 'y':
        print("\n⚠️  注意: FunASR需要以下前置依赖:")
        print("   - Python >= 3.8")
        print("   - torch >= 1.13")
        print("   - torchaudio")
        print("这些依赖将自动安装...\n")
        install_funasr = True
    
    # 安装依赖
    if not install_requirements(venv_path, install_funasr=install_funasr):
        return 1
    
    print("\n✅ 虚拟环境设置完成！")
    print(f"虚拟环境位置: {venv_path}")
    print("\n使用方法:")
    print(f"  {get_python_command(venv_path)} parse_douyin_video.py <抖音链接>")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
