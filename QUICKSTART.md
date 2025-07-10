# MoviePy Tools 快速开始指南

欢迎使用 MoviePy Tools！这是一个基于 MoviePy 的自动化视频剪辑工具组，让视频处理变得简单高效。

## 🚀 快速安装

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 在macOS上安装FFmpeg（推荐使用Homebrew）
brew install ffmpeg

# 在Ubuntu/Debian上安装FFmpeg
sudo apt update
sudo apt install ffmpeg

# 在Windows上安装FFmpeg
# 下载FFmpeg并添加到PATH环境变量
```

### 2. 初始化项目

```bash
# 创建项目目录结构
python config.py

# 或者运行初始化脚本
python -c "from config import create_directories; create_directories()"
```

## 📁 项目结构

```
moviepy-tools/
├── README.md              # 项目说明
├── QUICKSTART.md          # 快速开始指南
├── requirements.txt       # 依赖包列表
├── config.py             # 全局配置
├── main.py               # 主程序入口
├── core/                 # 核心功能模块
│   ├── video_processor.py    # 视频处理
│   ├── audio_processor.py    # 音频处理
│   ├── subtitle_processor.py # 字幕处理
│   └── batch_processor.py    # 批量处理
├── utils/                # 工具函数
│   ├── file_utils.py         # 文件操作
│   ├── time_utils.py         # 时间处理
│   └── format_utils.py       # 格式处理
├── examples/             # 示例脚本
│   ├── basic_video_editing.py # 基础视频编辑
│   └── batch_processing.py    # 批量处理示例
├── input/                # 输入文件目录
└── output/               # 输出文件目录
    ├── temp/             # 临时文件
    └── logs/             # 日志文件
```

## 🎬 基础使用

### 命令行界面

MoviePy Tools 提供了强大的命令行界面，支持各种视频处理操作：

#### 查看文件信息
```bash
python main.py info input/video.mp4
```

#### 视频剪切
```bash
# 剪切视频（从1分钟到2分钟）
python main.py video cut input/video.mp4 output/cut_video.mp4 --start 00:01:00 --end 00:02:00

# 剪切指定时长（从开始剪切30秒）
python main.py video cut input/video.mp4 output/cut_video.mp4 --start 00:00:00 --duration 00:00:30
```

#### 视频拼接
```bash
python main.py video concat video1.mp4 video2.mp4 video3.mp4 --output merged_video.mp4
```

#### 视频压缩
```bash
python main.py video compress input/video.mp4 output/compressed.mp4 --quality medium
```

#### 调整视频大小
```bash
python main.py video resize input/video.mp4 output/resized.mp4 --resolution 1280x720
```

#### 音频提取
```bash
python main.py audio extract input/video.mp4 --output output/audio.mp3 --format mp3
```

#### 音频处理
```bash
# 剪切音频
python main.py audio cut input/audio.mp3 output/cut_audio.mp3 --start 00:00:10 --duration 00:00:30

# 混合音频
python main.py audio mix background.mp3 voice.mp3 --output mixed.mp3 --bg-volume 0.3
```

#### 字幕处理
```bash
python main.py subtitle add input/video.mp4 input/subtitles.srt --output output/video_with_subs.mp4
```

#### 批量处理
```bash
# 批量转换格式
python main.py batch convert input_dir/ output_dir/ --format mp4 --quality medium

# 批量剪切
python main.py batch cut input_dir/ output_dir/ --start 00:00:00 --end 00:01:00
```

### Python API 使用

#### 基础视频处理

```python
from core import VideoProcessor

# 创建视频处理器
video_processor = VideoProcessor()

# 剪切视频
video_processor.cut_video(
    "input/video.mp4", 
    "output/cut_video.mp4", 
    start_time="00:01:00", 
    end_time="00:02:00"
)

# 拼接视频
video_processor.concatenate_videos(
    ["video1.mp4", "video2.mp4"], 
    "output/merged.mp4"
)

# 压缩视频
video_processor.compress_video(
    "input/video.mp4", 
    "output/compressed.mp4", 
    quality="medium"
)
```

#### 音频处理

```python
from core import AudioProcessor

# 创建音频处理器
audio_processor = AudioProcessor()

# 从视频提取音频
audio_processor.extract_audio_from_video(
    "input/video.mp4", 
    "output/audio.mp3"
)

# 混合音频
audio_processor.mix_audios(
    "background.mp3", 
    "voice.mp3", 
    "output/mixed.mp3",
    background_volume=0.3,
    foreground_volume=1.0
)
```

#### 字幕处理

```python
from core import SubtitleProcessor

# 创建字幕处理器
subtitle_processor = SubtitleProcessor()

# 创建字幕文件
subtitles = [
    {"text": "Hello World", "start": 0, "end": 3},
    {"text": "Welcome to MoviePy Tools", "start": 3, "end": 6}
]
subtitle_processor.create_subtitle_file(subtitles, "output/subtitles.srt")

# 为视频添加字幕
subtitle_processor.add_subtitles_to_video(
    "input/video.mp4", 
    "input/subtitles.srt", 
    "output/video_with_subs.mp4"
)
```

#### 批量处理

```python
from core import BatchProcessor

# 创建批量处理器
batch_processor = BatchProcessor()

# 批量转换格式
results = batch_processor.batch_convert_video_format(
    input_dir="input/videos/",
    output_dir="output/converted/",
    target_format="mp4",
    quality="medium"
)

# 查看处理结果
for result in results:
    if result["success"]:
        print(f"✅ {result['file']} 处理成功")
    else:
        print(f"❌ {result['file']} 处理失败: {result['error']}")
```

## 🔧 配置说明

### 视频质量设置

在 `config.py` 中定义了四种质量预设：

- **low**: 适合快速处理，文件较小
- **medium**: 平衡质量和文件大小（推荐）
- **high**: 高质量输出
- **ultra**: 最高质量，文件较大

### 自定义配置

```python
# 修改默认配置
from config import VIDEO_CONFIG, AUDIO_CONFIG

# 自定义视频配置
VIDEO_CONFIG["default_quality"] = "high"
VIDEO_CONFIG["default_resolution"] = (1920, 1080)

# 自定义音频配置
AUDIO_CONFIG["default_bitrate"] = "320k"
AUDIO_CONFIG["default_sample_rate"] = 48000
```

## 📖 示例脚本

### 运行基础示例

```bash
# 运行基础视频编辑示例
python examples/basic_video_editing.py

# 运行批量处理示例
python examples/batch_processing.py
```

### 准备示例文件

1. 将测试视频文件放在 `input/` 目录中
2. 重命名主要测试文件为 `sample_video.mp4`
3. 运行示例脚本查看效果

## 🐛 常见问题

### 1. FFmpeg 未找到

**错误**: `FFmpeg not found`

**解决方案**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: 下载FFmpeg并添加到PATH
```

### 2. 内存不足

**错误**: `MemoryError` 或处理大文件时崩溃

**解决方案**:
- 降低视频质量设置
- 分批处理大文件
- 增加系统虚拟内存

### 3. 编码错误

**错误**: 字幕或文件名包含特殊字符时出错

**解决方案**:
- 确保文件名使用英文字符
- 检查字幕文件编码为UTF-8

### 4. 权限错误

**错误**: `PermissionError` 无法写入文件

**解决方案**:
- 检查输出目录的写入权限
- 确保文件未被其他程序占用

## 🔗 更多资源

- [MoviePy 官方文档](https://moviepy.readthedocs.io/)
- [FFmpeg 官方网站](https://ffmpeg.org/)
- [项目 GitHub 仓库](https://github.com/your-username/moviepy-tools)

## 💡 技巧和建议

1. **处理大文件**: 建议先剪切成小片段再处理
2. **批量操作**: 使用批量处理功能提高效率
3. **质量选择**: 根据用途选择合适的质量设置
4. **备份文件**: 处理重要文件前先备份
5. **查看日志**: 出现问题时查看 `output/logs/` 中的日志文件

开始你的视频编辑之旅吧！🎬✨ 