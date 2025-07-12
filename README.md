# MoviePy Tools - 自动化视频剪辑工具组

这是一个基于 MoviePy 的自动化视频剪辑工具集，帮助你快速处理视频、音频和字幕等多媒体内容。项目的核心功能是通过 JSON 配置文件自动生成包含音频、图像、字幕和动画效果的视频。

## 🎯 项目特点

- **JSON 配置驱动**：通过 JSON 文件定义视频内容和时间轴
- **自动资源下载**：自动下载远程音频和图像资源
- **智能字幕生成**：根据时间轴自动添加字幕
- **动画效果支持**：支持图像动画效果（如轻微放大）
- **多音轨合成**：支持背景音乐、开场音效和主音频的混合
- **批量处理**：支持大量文件的批处理
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
├── scripts/                 # 脚本工具
│   ├── video_generator.py   # 视频生成器 (核心工具)
│   ├── test.json           # 示例配置文件
│   └── test_formatted.json # 格式化的示例配置
├── examples/                # 示例脚本
│   ├── basic_video_editing.py
│   └── batch_processing.py
├── input/                   # 输入文件目录
│   ├── videos/             # 原始视频文件
│   ├── audios/             # 原始音频文件
│   └── subtitles/          # 字幕文件
├── output/                  # 输出文件目录
│   └── video/              # 生成的视频文件
└── templates/               # 模板和预设
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `moviepy` - 视频处理核心库
- `requests` - 用于下载远程资源

### 2. 安装 FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows - 从官网下载：https://ffmpeg.org/download.html
```

### 3. 使用视频生成器

```bash
# 使用默认的 test.json 配置文件
python scripts/video_generator.py

# 指定自定义的 JSON 配置文件
python scripts/video_generator.py my_config.json

# 指定输出目录
python scripts/video_generator.py test.json -o /path/to/output

# 使用绝对路径的配置文件
python scripts/video_generator.py /path/to/config.json
```

## 🎬 视频生成器 (video_generator.py)

### 功能特点

- **多媒体资源整合**：自动下载和整合音频、图像资源
- **精确时间控制**：基于微秒级时间轴进行精确剪辑
- **字幕渲染**：自动添加带样式的字幕
- **动画效果**：支持图像动画效果
- **音频混合**：支持多音轨混合（主音频、背景音乐、音效）

### 使用方法

```bash
# 基本用法
python scripts/video_generator.py [JSON文件路径] [选项]

# 参数说明
# JSON文件路径: 配置文件路径（可选，默认为 test.json）
# -o, --output: 输出目录（可选，默认为 output/video）
```

### 示例

```bash
# 使用项目中的示例配置
python scripts/video_generator.py test.json

# 使用自定义配置文件
python scripts/video_generator.py my_video_config.json

# 指定输出目录
python scripts/video_generator.py test.json -o ./my_videos
```

## 📝 JSON 配置文件格式

JSON 配置文件定义了视频的所有内容和时间轴。以下是完整的格式说明：

### 基本结构

```json
{
  "audioData": "[音频数据数组的JSON字符串]",
  "imageData": "[图像数据数组的JSON字符串]", 
  "text_timielines": [字幕时间轴数组],
  "text_captions": [字幕文本数组],
  "bgAudioData": "[背景音乐数据的JSON字符串]",
  "kcAudioData": "[开场音效数据的JSON字符串]",
  "title_list": [标题列表],
  "title_timelimes": [标题时间轴],
  "roleImgData": "[角色图像数据的JSON字符串]"
}
```

### 详细字段说明

#### 1. audioData - 主音频数据
```json
"audioData": "[{\"audio_url\": \"https://example.com/audio.mp3\", \"duration\": 4008000, \"start\": 0, \"end\": 4008000}]"
```

**字段说明：**
- `audio_url`: 音频文件的 URL
- `duration`: 音频持续时间（微秒）
- `start`: 在视频中的开始时间（微秒）
- `end`: 在视频中的结束时间（微秒）

#### 2. imageData - 图像数据
```json
"imageData": "[{\"image_url\": \"https://example.com/image.jpg\", \"start\": 0, \"end\": 4008000, \"width\": 1440, \"height\": 1080, \"in_animation\": \"轻微放大\", \"in_animation_duration\": 100000}]"
```

**字段说明：**
- `image_url`: 图像文件的 URL
- `start`: 图像显示开始时间（微秒）
- `end`: 图像显示结束时间（微秒）
- `width`: 图像宽度
- `height`: 图像高度
- `in_animation`: 入场动画效果（可选）
- `in_animation_duration`: 动画持续时间（微秒，可选）

#### 3. text_timielines - 字幕时间轴
```json
"text_timielines": [
  {"start": 0, "end": 4008000},
  {"start": 4008000, "end": 7725818}
]
```

#### 4. text_captions - 字幕文本
```json
"text_captions": [
  "第一句字幕",
  "第二句字幕"
]
```

#### 5. bgAudioData - 背景音乐
```json
"bgAudioData": "[{\"audio_url\": \"https://example.com/bg_music.mp3\", \"duration\": 52392000, \"start\": 0, \"end\": 52392000}]"
```

#### 6. kcAudioData - 开场音效
```json
"kcAudioData": "[{\"audio_url\": \"https://example.com/intro_sound.mp3\", \"duration\": 4884897, \"start\": 0, \"end\": 4884897}]"
```

### 时间格式说明

- **所有时间都以微秒为单位**
- 1秒 = 1,000,000 微秒
- 例如：4.008秒 = 4,008,000 微秒

### 示例配置文件

项目中包含了一个完整的示例配置文件 `scripts/test.json`，展示了如何配置一个关于"失信"主题的历史故事视频，包含：

- 8个音频片段（总时长约52秒）
- 8个图像片段（带动画效果）
- 15个字幕片段
- 背景音乐
- 开场音效

## 🛠️ 高级功能

### 动画效果
目前支持的动画效果：
- `轻微放大`: 图像在显示期间缓慢放大

### 音频混合
- 主音频：语音内容
- 背景音乐：自动降低音量（30%）
- 开场音效：适中音量（50%）

### 字幕样式
- 字体大小：48px
- 颜色：白色
- 描边：黑色，3px
- 位置：视频底部，距离底边90px

## 📋 输出格式

- **视频格式**: MP4
- **视频编码**: H.264 (libx264)
- **音频编码**: AAC
- **帧率**: 24 FPS
- **分辨率**: 1440x1080 (可配置)
- **文件名格式**: `JSON文件前缀_YYYYMMDD_HHMM.mp4`
  - 例如：`test_formatted_20250711_2329.mp4`

## 🔧 故障排除

### 常见问题

1. **导入错误**: 确保已安装 moviepy
   ```bash
   pip install moviepy
   ```

2. **FFmpeg 错误**: 确保系统已安装 FFmpeg
   ```bash
   # 检查 FFmpeg 是否安装
   ffmpeg -version
   ```

3. **网络下载失败**: 检查网络连接和 URL 有效性

4. **内存不足**: 对于大型视频，确保有足够的内存和磁盘空间

### 调试建议

- 检查 JSON 文件格式是否正确
- 确认所有 URL 可访问
- 查看控制台输出的详细错误信息

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个项目。

## �� 许可证

MIT License 