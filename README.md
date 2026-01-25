# 抖音视频转文字

一个强大的工具，用于解析抖音分享链接、下载视频，并将视频中的音频转换为文字。

## ✨ 功能特性

- 🔗 **智能解析** - 支持多种抖音分享链接格式（App分享链接、PC端链接）
- 📥 **视频下载** - 自动下载无水印视频
- 🎙️ **语音转文字** - 使用 FunASR 将视频音频转换为文字
- 🖼️ **图集支持** - 自动识别并处理图集内容
- 🐍 **虚拟环境** - 自动创建和管理虚拟环境，避免依赖冲突
- 🚀 **开箱即用** - 提供启动脚本，一键运行

## 📋 系统要求

- Python 3.8+
- FFmpeg（必需，用于视频处理）
- macOS / Linux / Windows

## 📥 安装 Skill

### 方式一：从 GitHub 克隆（推荐）

```bash
# 1. 克隆仓库到本地
git clone git@github.com:majin72/skills-douyin-text-to-text.git

# 2. 进入目录
cd skills-douyin-text-to-text

# 3. 复制到 Cursor 的 skills 目录
# macOS/Linux:
cp -r . ~/.cursor/skills/douyin-video-transcribe

# Windows (PowerShell):
Copy-Item -Recurse . $env:USERPROFILE\.cursor\skills\douyin-video-transcribe
```

### 方式二：手动下载安装

1. **下载代码**
   - 访问 [GitHub 仓库](https://github.com/majin72/skills-douyin-text-to-text)
   - 点击 "Code" → "Download ZIP"
   - 解压下载的 ZIP 文件

2. **安装到 Cursor**
   - 打开终端（macOS/Linux）或命令提示符/PowerShell（Windows）
   - 执行以下命令：

   **macOS/Linux:**
   ```bash
   # 进入解压后的目录
   cd skills-douyin-text-to-text-main
   
   # 复制到 Cursor skills 目录
   cp -r . ~/.cursor/skills/douyin-video-transcribe
   ```

   **Windows:**
   ```cmd
   # 进入解压后的目录
   cd skills-douyin-text-to-text-main
   
   # 复制到 Cursor skills 目录
   xcopy /E /I . %USERPROFILE%\.cursor\skills\douyin-video-transcribe
   ```

3. **验证安装**
   - 检查目录是否存在：
   
   **macOS/Linux:**
   ```bash
   ls ~/.cursor/skills/douyin-video-transcribe
   ```
   
   **Windows:**
   ```cmd
   dir %USERPROFILE%\.cursor\skills\douyin-video-transcribe
   ```
   
   - 应该能看到 `SKILL.md`、`README.md` 和 `scripts/` 目录

### 方式三：直接使用（不安装到全局）

如果不想安装到全局，可以直接在项目目录中使用：

```bash
# 克隆或下载代码后，直接进入目录使用
cd skills-douyin-text-to-text
python scripts/run.py "https://v.douyin.com/xxxxx"
```

## 🔧 安装 FFmpeg

**FFmpeg 是必需的系统工具**，用于视频处理和音频提取。必须单独安装，不能通过 pip 安装。

### macOS

**使用 Homebrew（推荐）：**
```bash
# 安装 Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 FFmpeg
brew install ffmpeg
```

**验证安装：**
```bash
ffmpeg -version
```

### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
# 或者（较新版本）
sudo dnf install ffmpeg
```

**验证安装：**
```bash
ffmpeg -version
```

### Windows

1. **下载 FFmpeg**
   - 访问 [FFmpeg 官网](https://ffmpeg.org/download.html)
   - 或直接下载预编译版本：[ffmpeg-builds](https://www.gyan.dev/ffmpeg/builds/)
   - 下载 "ffmpeg-release-essentials.zip"

2. **解压文件**
   - 解压到某个目录，例如：`C:\ffmpeg`
   - 解压后应该看到 `bin`、`doc`、`presets` 等文件夹

3. **添加到系统 PATH**
   - 右键点击"此电脑" → "属性"
   - 点击"高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到 `Path`，点击"编辑"
   - 点击"新建"，输入 FFmpeg 的 `bin` 目录路径（例如：`C:\ffmpeg\bin`）
   - 点击"确定"保存所有更改

4. **验证安装**
   - 打开**新的**命令提示符或 PowerShell 窗口
   - 运行：
   ```cmd
   ffmpeg -version
   ```
   - 如果显示版本信息，说明安装成功

**注意**：修改 PATH 后必须打开新的命令行窗口才能生效。

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

启动脚本会自动创建虚拟环境并安装依赖：

```bash
# macOS/Linux
cd .cursor/skills/douyin-video-transcribe
./scripts/run.sh "https://v.douyin.com/xxxxx"

# Windows
cd .cursor\skills\douyin-video-transcribe
scripts\run.bat "https://v.douyin.com/xxxxx"

# Python 跨平台
cd .cursor/skills/douyin-video-transcribe
python scripts/run.py "https://v.douyin.com/xxxxx"
```

### 方式二：手动设置

```bash
# 1. 进入目录
cd .cursor/skills/douyin-video-transcribe

# 2. 创建虚拟环境
python scripts/setup_venv.py

# 3. 激活虚拟环境
# macOS/Linux:
source scripts/venv/bin/activate
# Windows:
scripts\venv\Scripts\activate

# 4. 运行脚本
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx"
```

## 📖 使用示例

### 基本使用（仅下载视频）

```bash
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx"
```

### 下载并转文字

```bash
python scripts/parse_douyin_video.py "https://v.douyin.com/xxxxx" --transcribe
```

### 完整参数

```bash
python scripts/parse_douyin_video.py <分享链接> \
  --output-dir ./downloads \          # 输出目录
  --transcribe \                       # 是否转文字
  --model paraformer-zh \             # ASR模型
  --vad-model fsmn-vad \              # VAD模型
  --punc-model ct-punc                # 标点恢复模型
```

## 📦 依赖安装

### 1. 安装 FFmpeg（必需）

**FFmpeg 是系统级工具，必须先安装**。请参考上面的"🔧 安装 FFmpeg"部分。

### 2. 安装 Python 依赖

#### 基础依赖（必需）

如果使用虚拟环境（推荐），启动脚本会自动安装。如果手动安装：

```bash
pip install requests urllib3
```

### 转文字功能依赖（可选）

如果使用 `--transcribe` 参数，需要安装 FunASR 及其前置依赖：

```bash
# 安装顺序很重要！
pip install torch>=1.13 torchaudio funasr>=1.0.0
```

**注意**：
- FunASR 需要 Python >= 3.8
- 必须先安装 torch 和 torchaudio，再安装 funasr
- 首次运行会下载模型文件，需要较长时间和稳定的网络连接

## 📁 项目结构

```
douyin-video-transcribe/
├── README.md                    # 项目说明（本文件）
├── SKILL.md                     # Skill 文档（面向 AI agent）
└── scripts/
    ├── parse_douyin_video.py   # 主脚本：解析链接、下载视频
    ├── transcribe_audio_funasr.py  # 语音转文字脚本
    ├── setup_venv.py           # 虚拟环境设置脚本
    ├── run.py                  # Python 启动脚本（跨平台）
    ├── run.sh                  # Shell 启动脚本（macOS/Linux）
    ├── run.bat                 # 批处理启动脚本（Windows）
    └── venv/                   # 虚拟环境目录（自动创建）
```

## 🎯 功能说明

### 支持的链接格式

- `https://v.douyin.com/xxxxx` - App 分享链接
- `https://www.iesdouyin.com/share/video/xxxxx` - PC 端链接
- `https://www.douyin.com/video/xxxxx` - PC 端链接

### 输出文件

- 视频文件：`{video_id}.mp4`（保存在 `--output-dir` 指定的目录）
- 文字文件：`{video_id}.txt`（如果使用 `--transcribe` 参数）

## ⚙️ 配置说明

### 虚拟环境

项目会自动在 `scripts/venv/` 目录下创建虚拟环境。如果已存在虚拟环境，启动脚本会直接使用。

### 模型配置

FunASR 使用的默认模型：
- **ASR 模型**: `paraformer-zh` - 中文语音识别
- **VAD 模型**: `fsmn-vad` - 语音活动检测
- **标点模型**: `ct-punc` - 标点恢复

可以通过命令行参数自定义模型。

## 🔧 故障排查

### 常见问题

1. **FFmpeg 未安装或找不到**
   - **错误信息**：`ffmpeg: command not found` 或 `'ffmpeg' 不是内部或外部命令`
   - **解决**：请参考上面的"🔧 安装 FFmpeg"部分，按照你的操作系统安装 FFmpeg
   - **验证**：运行 `ffmpeg -version` 检查是否安装成功

2. **ImportError: No module named 'requests'**
   - **解决**：使用启动脚本自动安装，或手动运行 `python scripts/setup_venv.py`

3. **FunASR 未安装**
   - **解决**：运行 `python scripts/setup_venv.py`，选择安装 FunASR

4. **无法解析分享链接**
   - 检查链接格式是否正确
   - 检查网络连接
   - 确认链接未被删除或设为私密

5. **转文字失败**
   - 确认已安装 FunASR：`pip list | grep funasr`
   - 检查 Python 版本是否 >= 3.8
   - 确认视频文件已完整下载
   - 确认 FFmpeg 已正确安装（转文字需要从视频中提取音频）

更多问题请查看 [SKILL.md](SKILL.md) 中的故障排查部分。

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 相关文档

- [SKILL.md](SKILL.md) - 详细的技能文档（面向 AI agent）
- [FunASR 官方文档](https://github.com/alibaba-damo-academy/FunASR)

## ⚠️ 免责声明

本工具仅供学习和研究使用。请遵守相关法律法规，不要用于非法用途。使用本工具下载的内容，请尊重原作者的版权。
