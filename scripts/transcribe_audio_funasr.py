#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用 FunASR 进行语音识别
将音频文件转换为文字
"""

import argparse
import json
import sys
import os
from pathlib import Path

def transcribe_audio(audio_path, model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc", output_dir=None):
    """
    使用 FunASR 进行语音识别
    
    Args:
        audio_path: 音频文件路径
        model: ASR 模型，默认为 paraformer-zh
        vad_model: VAD 模型，默认为 fsmn-vad
        punc_model: 标点恢复模型，默认为 ct-punc
    
    Returns:
        dict: 包含识别结果的字典
    """
    try:
        # 检查音频文件是否存在
        if not os.path.exists(audio_path):
            return {
                "code": "ERROR",
                "message": f"音频文件不存在: {audio_path}"
            }
        
        # 检查文件大小
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            return {
                "code": "ERROR",
                "message": "音频文件为空"
            }
        
        # 方法1：使用 FunASR Python API（推荐，符合官方文档）
        try:
            from funasr import AutoModel
            
            # 初始化模型（参考官方文档）
            # 注意：首次运行会下载模型，可能需要较长时间
            # 使用 disable_update=True 可以禁用更新检查，加快启动速度
            asr_model = AutoModel(
                model=model,
                vad_model=vad_model,
                punc_model=punc_model,
                disable_update=True  # 禁用更新检查，加快启动
            )
            
            # 执行识别（参考官方文档的标准用法）
            # 如果指定了输出目录，可以保存中间结果
            generate_kwargs = {"input": audio_path}
            if output_dir:
                generate_kwargs["output_dir"] = output_dir
            
            result = asr_model.generate(**generate_kwargs)
            
            # 解析结果（根据官方文档，返回格式是列表，每个元素是字典）
            # 格式: [{'key': 'filename', 'text': '识别的文本', 'timestamp': [...]}, ...]
            text = ""
            timestamp_info = []
            
            if isinstance(result, list) and len(result) > 0:
                # 提取所有文本片段并合并
                texts = []
                for item in result:
                    if isinstance(item, dict):
                        item_text = item.get('text', '')
                        if item_text:
                            texts.append(item_text)
                        # 保存时间戳信息（如果有）
                        if 'timestamp' in item:
                            timestamp_info = item.get('timestamp', [])
                    elif isinstance(item, str):
                        texts.append(item)
                # 合并文本，使用空格连接
                text = ' '.join(texts) if texts else ''
            elif isinstance(result, dict):
                # 如果是字典格式，直接提取
                text = result.get('text', '')
                timestamp_info = result.get('timestamp', [])
            elif isinstance(result, str):
                # 如果是字符串，直接使用
                text = result
            else:
                # 其他情况，转换为字符串
                text = str(result)
            
            if text and text.strip():
                return {
                    "code": "SUCCESS",
                    "data": {
                        "text": text.strip(),
                        "audio_path": audio_path,
                        "model": model,
                        "timestamp": timestamp_info if timestamp_info else None
                    }
                }
            else:
                return {
                    "code": "ERROR",
                    "message": "FunASR 返回空文本"
                }
        except ImportError:
            # 如果无法导入 FunASR，提示用户安装
            return {
                "code": "ERROR",
                "message": "FunASR 未安装。请先安装依赖：\n"
                          "1. 推荐：使用虚拟环境 - 运行 'python scripts/setup_venv.py' 或使用启动脚本 'python scripts/run.py'\n"
                          "2. 手动安装：pip install torch>=1.13 torchaudio funasr>=1.0.0"
            }
        except Exception as e:
            # API 调用失败，记录错误并回退到命令行方式
            import warnings
            error_msg = str(e)
            warnings.warn(f"FunASR API 调用失败: {error_msg}，尝试使用命令行方式")
            # 继续执行下面的命令行方式代码
        
        # 方法2：使用命令行方式（备用）
        import subprocess
        
        # 查找 funasr 命令（优先使用虚拟环境中的）
        venv_funasr = Path(__file__).parent / "venv" / "bin" / "funasr"
        if venv_funasr.exists():
            funasr_cmd = str(venv_funasr)
        else:
            funasr_cmd = "funasr"
        
        # 构建命令参数
        cmd = [
            funasr_cmd,
            f"++model={model}",
            f'++vad_model="{vad_model}"',
            f'++punc_model="{punc_model}"',
            f"++input={audio_path}"
        ]
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode != 0:
            error_msg = result.stderr
            if "No such file or directory: 'funasr'" in error_msg or "command not found" in error_msg:
                return {
                    "code": "ERROR",
                    "message": "FunASR 未安装。请先安装依赖：\n"
                              "1. 推荐：使用虚拟环境 - 运行 'python scripts/setup_venv.py' 或使用启动脚本 'python scripts/run.py'\n"
                              "2. 手动安装：pip install torch>=1.13 torchaudio funasr>=1.0.0"
                }
            return {
                "code": "ERROR",
                "message": f"FunASR 执行失败: {error_msg}"
            }
        
        # 解析输出
        output = result.stdout.strip()
        
        # FunASR 的输出格式可能是多行，需要解析
        lines = output.split('\n')
        
        # 提取识别文本（过滤掉日志行）
        transcription_text = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('INFO'):
                # 跳过日志行
                if any(keyword in line.lower() for keyword in ['error', 'warning', 'info', 'debug', 'loading', 'building', 'download']):
                    continue
                if line and not line.startswith('{') and not line.startswith('['):
                    transcription_text = line
                    break
        
        # 如果没找到文本，尝试使用整个输出（去除日志行）
        if not transcription_text:
            text_lines = [
                line.strip() 
                for line in lines 
                if line.strip() 
                and not line.startswith('[')
                and not any(keyword in line.lower() for keyword in ['info', 'warning', 'error', 'debug', 'loading', 'building', 'download'])
            ]
            transcription_text = ' '.join(text_lines) if text_lines else output
        
        if not transcription_text or len(transcription_text.strip()) == 0:
            return {
                "code": "ERROR",
                "message": "未能从 FunASR 输出中提取识别文本",
                "raw_output": output
            }
        
        return {
            "code": "SUCCESS",
            "data": {
                "text": transcription_text.strip(),
                "audio_path": audio_path,
                "model": model
            }
        }
        
    except subprocess.TimeoutExpired:
        return {
            "code": "ERROR",
            "message": "语音识别超时（超过5分钟）"
        }
    except Exception as e:
        return {
            "code": "ERROR",
            "message": f"语音识别异常: {str(e)}"
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='使用 FunASR 进行语音识别')
    parser.add_argument('--audio', type=str, required=True, help='音频文件路径')
    parser.add_argument('--model', type=str, default='paraformer-zh', help='ASR 模型，默认为 paraformer-zh')
    parser.add_argument('--vad_model', type=str, default='fsmn-vad', help='VAD 模型，默认为 fsmn-vad')
    parser.add_argument('--punc_model', type=str, default='ct-punc', help='标点恢复模型，默认为 ct-punc')
    parser.add_argument('--output_dir', type=str, default=None, help='输出目录（可选）')
    
    args = parser.parse_args()
    
    result = transcribe_audio(
        args.audio,
        model=args.model,
        vad_model=args.vad_model,
        punc_model=args.punc_model,
        output_dir=args.output_dir
    )
    
    # 输出 JSON 格式结果
    print(json.dumps(result, ensure_ascii=False))

