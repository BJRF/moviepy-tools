# MoviePy Tools - 自动化视频剪辑工具组

这是一个基于MoviePy的自动化视频剪辑工具集，帮助你快速处理视频、音频和字幕等多媒体内容。

## 🎯 项目特点

- **自动化剪辑**：批量处理视频文件
- **智能拼接**：自动拼接多个视频片段
- **音频处理**：提取、混合、调整音频
- **字幕管理**：自动添加和处理字幕
- **批量操作**：支持大量文件的批处理
- **配置灵活**：通过配置文件自定义处理参数

## 📁 项目结构

```
moviepy-tools/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包列表
├── config.py                # 全局配置
├── main.py                  # 主程序入口
├── core/                    # 核心功能模块
│   ├── __init__.py
│   ├── video_processor.py   # 视频处理核心
│   ├── audio_processor.py   # 音频处理核心
│   ├── subtitle_processor.py # 字幕处理核心
│   └── batch_processor.py   # 批量处理核心
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── file_utils.py        # 文件操作工具
│   ├── time_utils.py        # 时间处理工具
│   └── format_utils.py      # 格式转换工具
├── templates/               # 模板和预设
│   ├── video_templates.py   # 视频模板
│   ├── audio_templates.py   # 音频模板
│   └── subtitle_templates.py # 字幕模板
├── examples/                # 示例脚本
│   ├── basic_editing.py     # 基础剪辑示例
│   ├── batch_processing.py  # 批量处理示例
│   ├── audio_mixing.py      # 音频混合示例
│   └── subtitle_adding.py   # 字幕添加示例
├── input/                   # 输入文件目录
│   ├── videos/             # 原始视频文件
│   ├── audios/             # 原始音频文件
│   └── subtitles/          # 字幕文件
├── output/                  # 输出文件目录
│   ├── processed/          # 处理后的文件
│   ├── temp/               # 临时文件
│   └── logs/               # 日志文件
└── tests/                   # 测试文件
    ├── __init__.py
    ├── test_video.py        # 视频处理测试
    ├── test_audio.py        # 音频处理测试
    └── test_batch.py        # 批量处理测试
```

## 🚀 快速开始

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **安装FFmpeg**
```bash
# macOS
brew install ffmpeg

# 或者从官网下载：https://ffmpeg.org/download.html
```

3. **运行示例**
```bash
python examples/basic_editing.py
```

## 📋 主要功能

### 视频处理
- 视频剪切和拼接
- 分辨率调整
- 帧率转换
- 视频压缩
- 添加水印

### 音频处理
- 音频提取
- 音频混合
- 音量调整
- 音频格式转换
- 背景音乐添加

### 字幕处理
- 字幕添加
- 字幕样式设置
- 多语言字幕
- 字幕时间轴调整

### 批量处理
- 批量格式转换
- 批量剪辑
- 批量添加特效
- 进度监控

## 🛠️ 使用方法

详细的使用说明请查看 `examples/` 目录中的示例脚本。

## 📝 配置说明

在 `config.py` 中可以配置：
- 默认输出格式
- 视频质量设置
- 处理线程数
- 临时文件路径

## 🤝 贡献

欢迎提交Issues和Pull Requests来改进这个项目。

## �� 许可证

MIT License 