---
name: douyin-video-transcribe
description: 解析抖音分享链接，下载视频，并使用FunASR将视频音频转成文字。当用户提供抖音分享链接（v.douyin.com、www.iesdouyin.com、www.douyin.com）时，自动解析链接获取视频信息，下载视频文件，并可选择性地将视频中的音频转换为文字。支持视频和图集两种内容类型。
---

# 抖音视频转文字

## 概述

此skill提供完整的抖音视频处理流程：从分享链接解析、视频下载到音频转文字。当用户提供抖音分享链接时，自动完成整个处理流程。

## ⚠️ 重要提示

**首次使用前，必须先设置虚拟环境！**

- **推荐方式**：使用启动脚本（`run.py`/`run.sh`/`run.bat`），会自动创建虚拟环境
- **手动方式**：运行 `python scripts/setup_venv.py` 创建虚拟环境

**不要直接运行脚本**，否则会提示缺少依赖。请使用启动脚本或先设置虚拟环境。

## 前提条件

### 系统要求

- **Python 版本**: Python 3.6 或更高版本（推荐 3.8+）
- **操作系统**: 支持 macOS、Linux、Windows

### 虚拟环境（推荐）

**强烈推荐使用虚拟环境**，以避免依赖冲突。skill 提供了自动化的虚拟环境管理：

#### 方式一：使用启动脚本（推荐）

启动脚本会自动检测并创建虚拟环境：

**macOS/Linux:**
```bash
./scripts/run.sh "https://v.douyin.com/xxxxx"
```

**Windows:**
```cmd
scripts\run.bat "https://v.douyin.com/xxxxx"
```

**Python 跨平台:**
```bash
python scripts/run.py "https://v.douyin.com/xxxxx"
```

#### 方式二：手动设置虚拟环境

如果需要手动管理虚拟环境：

```bash
# 1. 创建虚拟环境
python scripts/setup_venv.py

# 2. 激活虚拟环境
# macOS/Linux:
source scripts/venv/bin/activate
# Windows:
scripts\venv\Scripts\activate

# 3. 运行脚本
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx"
```

### 必需依赖

以下依赖是运行脚本的基础要求：

**如果使用虚拟环境**（推荐）：
- 虚拟环境会自动安装 `requests` 和 `urllib3`
- 运行 `setup_venv.py` 时会自动安装

**如果直接使用系统Python**：
```bash
pip install requests urllib3
```

### 转文字功能依赖（可选）

如果使用 `--transcribe` 参数进行音频转文字，需要安装 FunASR 及其前置依赖：

**FunASR 前置依赖要求**：
- **Python >= 3.8**（必需）
- **torch >= 1.13**（必需）
- **torchaudio**（必需）
- **funasr >= 1.0.0**

**如果使用虚拟环境**（推荐）：
- 运行 `setup_venv.py` 时选择安装 FunASR
- 脚本会自动安装所有前置依赖（torch、torchaudio）和 FunASR
- 或手动激活虚拟环境后运行：
  ```bash
  pip install torch>=1.13 torchaudio funasr>=1.0.0
  ```

**如果直接使用系统Python**：
```bash
pip install torch>=1.13 torchaudio funasr>=1.0.0
```

**注意**: 
- **Python版本要求**: FunASR 需要 Python 3.8 或更高版本
- **安装顺序**: 必须先安装 torch 和 torchaudio，再安装 funasr
- **安装时间**: torch 和 funasr 的安装可能需要较长时间（取决于网络速度）
- **模型下载**: FunASR 首次运行时会自动下载模型文件，可能需要较长时间
- **磁盘空间**: 确保有足够的磁盘空间（模型文件较大，通常需要几GB）
- **网络要求**: 需要稳定的网络连接以下载依赖和模型

### 网络要求

- 需要能够访问抖音网站（`www.iesdouyin.com`、`v.douyin.com` 等）
- 需要能够访问视频CDN地址以下载视频
- 如果使用转文字功能，首次运行需要能够访问模型下载源

## 工作流程

1. **解析分享链接** - 支持多种抖音分享链接格式（App分享链接、PC端链接）
2. **提取视频信息** - 获取视频标题、作者、封面等信息
3. **下载视频** - 下载无水印视频到本地
4. **音频转文字**（可选）- 使用FunASR将视频中的音频转换为文字

## 使用方法

### ⭐ 快速开始（推荐 - 自动创建虚拟环境）

**必须使用启动脚本**，它会自动检测并创建虚拟环境，无需手动操作：

**macOS/Linux:**
```bash
cd .cursor/skills/douyin-video-transcribe
./scripts/run.sh "https://v.douyin.com/xxxxx"
```

**Windows:**
```cmd
cd .cursor\skills\douyin-video-transcribe
scripts\run.bat "https://v.douyin.com/xxxxx"
```

**Python 跨平台（推荐）:**
```bash
cd .cursor/skills/douyin-video-transcribe
python scripts/run.py "https://v.douyin.com/xxxxx"
```

**启动脚本会自动：**
1. ✅ 检测虚拟环境是否存在
2. ✅ 如果不存在，自动创建虚拟环境
3. ✅ 自动安装基础依赖（requests、urllib3）
4. ✅ 在虚拟环境中运行脚本

### 手动设置虚拟环境（可选）

如果不想使用启动脚本，可以手动设置：

```bash
# 1. 进入skill目录
cd .cursor/skills/douyin-video-transcribe

# 2. 创建虚拟环境（会提示是否安装FunASR）
python scripts/setup_venv.py

# 3. 激活虚拟环境
# macOS/Linux:
source scripts/venv/bin/activate
# Windows:
scripts\venv\Scripts\activate

# 4. 运行脚本
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx"
```

### ⚠️ 不推荐：直接运行脚本

**不建议直接运行脚本**，除非你已确认系统已安装所有依赖：

```bash
# 不推荐 - 可能缺少依赖
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx"
```

### 下载并转文字

添加 `--transcribe` 参数可自动转文字：

**⭐ 推荐：使用启动脚本（会自动创建虚拟环境）:**
```bash
cd .cursor/skills/douyin-video-transcribe
python scripts/run.py "https://v.douyin.com/xxxxx" --transcribe
```

**注意**：首次使用转文字功能时，需要在虚拟环境中安装 FunASR：
```bash
# 激活虚拟环境后
source scripts/venv/bin/activate  # macOS/Linux
# 或
scripts\venv\Scripts\activate  # Windows

# 安装FunASR及其前置依赖
pip install torch>=1.13 torchaudio funasr>=1.0.0
```

**或者运行 setup_venv.py 时选择安装 FunASR：**
```bash
python scripts/setup_venv.py
# 当提示"是否安装FunASR"时，输入 y
```

### 完整参数

```bash
python scripts/parse_douyin_video.py <分享链接> \
  --output-dir ./downloads \          # 输出目录，默认 ./downloads
  --transcribe \                       # 是否转文字
  --model paraformer-zh \             # ASR模型，默认为 paraformer-zh
  --vad-model fsmn-vad \              # VAD模型，默认为 fsmn-vad
  --punc-model ct-punc                # 标点恢复模型，默认为 ct-punc
```

## 脚本说明

### run.py / run.sh / run.bat

启动脚本，自动检测并创建虚拟环境：
- `run.py` - Python 跨平台启动脚本
- `run.sh` - macOS/Linux Shell 启动脚本
- `run.bat` - Windows 批处理启动脚本

**功能**:
- 自动检测虚拟环境是否存在
- 如果不存在，自动创建虚拟环境并安装基础依赖
- 在虚拟环境中运行主脚本

### setup_venv.py

虚拟环境设置脚本，用于手动创建和配置虚拟环境：

```bash
python scripts/setup_venv.py
```

**功能**:
- 创建虚拟环境（如果不存在）
- 安装基础依赖（requests、urllib3）
- 可选安装 FunASR（转文字功能需要）

### parse_douyin_video.py

主要脚本，包含以下功能：

- **parse_share_url()** - 解析分享链接，自动识别App分享链接和PC端链接
- **parse_video_id()** - 根据视频ID获取视频详细信息
- **download_video()** - 下载视频文件
- **转文字集成** - 自动调用同目录下的 `transcribe_audio_funasr.py` 进行语音识别

脚本会输出：
- 视频信息（标题、作者、封面等）
- 下载的视频文件路径
- 转文字结果（如果启用）
- JSON格式的完整信息

### transcribe_audio_funasr.py

语音识别脚本，提供 `transcribe_audio()` 函数用于音频转文字。

**功能特性**:
- 支持 FunASR Python API（推荐方式）
- 支持命令行方式（备用方案）
- 自动处理多种返回格式
- 支持时间戳信息提取

**使用方式**:
- 作为模块导入：`from transcribe_audio_funasr import transcribe_audio`
- 命令行直接运行：`python transcribe_audio_funasr.py --audio <音频文件>`

## 依赖详情

### Python 标准库

脚本使用以下 Python 标准库（无需额外安装）：
- `argparse` - 命令行参数解析
- `json` - JSON数据处理
- `os` - 操作系统接口
- `re` - 正则表达式
- `random` - 随机数生成
- `string` - 字符串操作
- `sys` - 系统相关参数和函数
- `pathlib` - 路径操作
- `urllib.parse` - URL解析
- `importlib.util` - 动态模块导入
- `subprocess` - 子进程管理

### 第三方库

#### requests

用于HTTP请求，处理抖音页面访问和视频下载。

```bash
pip install requests
```

**版本要求**: requests >= 2.20.0

#### urllib3

用于HTTP连接池和重试机制。

```bash
pip install urllib3
```

**版本要求**: urllib3 >= 1.24.0

**注意**: requests 通常会自带 urllib3，但建议单独安装以确保版本兼容性。

#### torch（FunASR前置依赖）

PyTorch 深度学习框架，FunASR 的必需依赖。

```bash
pip install torch>=1.13
```

**版本要求**: torch >= 1.13

**安装说明**:
- torch 是 FunASR 的前置依赖，必须先安装
- 安装包较大（通常几百MB到几GB），需要较长时间
- 建议使用虚拟环境安装
- 根据系统自动选择 CPU 或 GPU 版本

#### torchaudio（FunASR前置依赖）

PyTorch 音频处理库，FunASR 的必需依赖。

```bash
pip install torchaudio
```

**安装说明**:
- torchaudio 是 FunASR 的前置依赖，必须先安装
- 通常与 torch 一起安装
- 建议使用虚拟环境安装

#### funasr（可选）

FunASR 语音识别库，用于音频转文字功能。

```bash
pip install funasr>=1.0.0
```

**版本要求**: funasr >= 1.0.0

**前置依赖**（必须按顺序安装）:
1. Python >= 3.8
2. torch >= 1.13
3. torchaudio
4. funasr >= 1.0.0

**安装说明**:
- **必须先安装前置依赖**: 确保已安装 torch >= 1.13 和 torchaudio
- **Python版本要求**: 需要 Python 3.8 或更高版本
- **安装顺序**: 先安装 torch 和 torchaudio，再安装 funasr
- 首次安装可能需要较长时间（依赖和模型文件较大）
- 建议使用虚拟环境安装
- 如果安装失败，可以尝试：
  - 升级 pip: `pip install --upgrade pip`
  - 使用国内镜像源加速下载
  - 检查网络连接是否稳定

## 注意事项

1. **图集处理** - 如果链接指向图集而非视频，脚本会识别并提示，不会尝试下载视频
2. **无水印视频** - 脚本会自动将 `playwm` 替换为 `play` 获取无水印视频
3. **重定向处理** - 自动处理302重定向，获取真实的CDN视频地址
4. **转文字功能** - `transcribe_audio_funasr.py` 已包含在 skill 的 scripts 目录中，无需额外配置
5. **FunASR前置依赖** - 使用转文字功能前，必须确保已安装：
   - Python >= 3.8
   - torch >= 1.13
   - torchaudio
   - funasr >= 1.0.0
   - 安装顺序：先安装 torch 和 torchaudio，再安装 funasr
6. **模型下载** - FunASR 首次运行时会下载模型，请确保网络连接稳定
7. **视频格式** - 下载的视频格式为 MP4，可直接播放
8. **输出文件** - 视频文件保存为 `{video_id}.mp4`，转文字结果保存为 `{video_id}.txt`
9. **磁盘空间** - torch 和 FunASR 模型文件较大，确保有足够的磁盘空间（建议至少5GB）

## 错误处理

脚本会处理以下常见错误：
- 无效的分享链接
- 视频不存在或已删除
- 网络请求失败
- 视频下载失败
- 转文字失败
- FunASR 模型加载失败

所有错误都会输出清晰的错误信息，方便排查问题。

## 故障排查

### 常见问题

1. **ImportError: No module named 'requests'**
   - **推荐解决**：使用启动脚本 `run.py`/`run.sh`/`run.bat`，会自动创建虚拟环境并安装依赖
   - **手动解决**：运行 `python scripts/setup_venv.py` 创建虚拟环境
   - **直接解决**：运行 `pip install requests urllib3`（不推荐，可能污染系统环境）

2. **ImportError: No module named 'funasr'**
   - **推荐解决**：运行 `python scripts/setup_venv.py`，选择安装 FunASR
   - **手动解决**：激活虚拟环境后运行 `pip install funasr`
   - **直接解决**：运行 `pip install funasr`（仅在使用转文字功能时需要）

3. **虚拟环境创建失败**
   - 检查 Python 版本（需要 3.6+）
   - 确认系统已安装 `venv` 模块（Python 3.3+ 自带）
   - 检查磁盘空间和写入权限

4. **无法解析分享链接**
   - 检查链接格式是否正确
   - 检查网络连接是否正常
   - 确认链接未被删除或设为私密

5. **视频下载失败**
   - 检查网络连接
   - 确认输出目录有写入权限
   - 检查磁盘空间是否充足

6. **转文字失败**
   - 确认已安装 FunASR 及其前置依赖：
     ```bash
     pip list | grep -E "(torch|torchaudio|funasr)"
     ```
   - 检查 Python 版本是否 >= 3.8: `python --version`
   - 确认安装顺序正确：先安装 torch 和 torchaudio，再安装 funasr
   - 检查视频文件是否完整下载
   - 查看错误信息中的具体错误原因
   - 首次运行 FunASR 需要下载模型，请确保网络连接稳定

7. **torch 安装失败或很慢**
   - 使用国内镜像源加速：
     ```bash
     pip install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
     ```
   - 检查网络连接是否稳定
   - 确保有足够的磁盘空间（torch 安装包较大）

8. **FunASR 安装失败**
   - 确认已正确安装前置依赖（torch >= 1.13, torchaudio）
   - 确认 Python 版本 >= 3.8
   - 尝试单独安装：`pip install funasr --no-deps` 然后手动安装依赖
   - 查看详细错误信息，根据错误提示解决问题
