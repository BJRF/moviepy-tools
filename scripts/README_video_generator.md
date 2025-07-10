# 视频生成器使用说明

## 概述
`video_generator_fixed.py` 是一个修复版的视频生成脚本，能够从JSON数据文件中读取内容并生成完整的视频。

## 主要功能
- 从JSON数据文件读取视频配置
- 下载音频、图片和背景音乐
- 创建字幕片段
- 合成最终视频
- 自动保存到项目根目录的 `output/video/` 文件夹

## 使用方法

### 1. 准备数据文件
脚本会自动寻找以下文件（按优先级排序）：
- `test.json` - 标准JSON文件（推荐）
- `test_formatted.json` - 格式化的JSON文件
- `test` - 原始数据文件

### 2. 运行脚本
```bash
cd scripts
python video_generator_fixed.py
```

### 3. 输出位置
生成的视频将保存在：
```
项目根目录/output/video/generated_video_[时间戳].mp4
```

## 数据格式要求

JSON文件应包含以下字段：
- `audioData`: 音频片段数据（JSON字符串）
- `imageData`: 图片片段数据（JSON字符串）
- `text_timielines`: 字幕时间轴
- `text_captions`: 字幕内容
- `bgAudioData`: 背景音乐数据
- `kcAudioData`: 开场音效数据
- `title_list`: 视频标题列表
- `title_timelimes`: 标题时间轴
- `roleImgData`: 角色图片数据（可选）

## 输出示例
```
🎬 开始从test文件生成视频...
📁 使用JSON数据文件: /path/to/test.json
📁 输出目录: /path/to/output/video
📊 视频信息:
   ⏱️  总时长: 52.4 秒 (0.9 分钟)
   🎵 音频片段数: 8
   🖼️  图片片段数: 8
   💬 字幕片段数: 15
   📝 视频主题: 失信

🚀 开始生成视频...
✅ 视频生成成功！
📁 输出文件: /path/to/output/video/generated_video_1752078890.mp4
📦 文件大小: 6.2 MB
🎉 视频已保存到项目根目录的 output/video/ 文件夹中
```

## 注意事项
- 确保网络连接正常，脚本需要下载音频和图片文件
- 生成的视频分辨率为 1440x1080
- 视频帧率为 24fps
- 使用 H.264 编码，AAC 音频编码
- 临时文件会在生成完成后自动清理

## 故障排除
如果遇到JSON解析错误，请检查：
1. 数据文件格式是否正确
2. 是否包含必要的字段
3. JSON字符串是否正确转义

**推荐使用 `test.json` 文件格式**，这是标准的JSON格式，最容易解析和维护。如果需要处理原始的转义字符串格式，建议先转换为标准JSON格式。

## 文件格式说明
- `test.json`: 标准JSON格式，推荐使用
- `test_formatted.json`: 备用格式化JSON文件
- `test`: 原始数据文件（可能包含转义字符） 