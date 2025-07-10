#!/usr/bin/env python3
"""
基础视频编辑示例
演示如何使用MoviePy Tools进行基本的视频处理操作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import VideoProcessor, AudioProcessor, SubtitleProcessor
from utils import get_video_info


def basic_video_operations():
    """基础视频操作示例"""
    print("🎬 基础视频编辑示例")
    print("=" * 50)
    
    # 初始化处理器
    video_processor = VideoProcessor()
    audio_processor = AudioProcessor()
    
    # 示例文件路径（请根据实际情况修改）
    input_video = "input/sample_video.mp4"
    
    # 检查输入文件是否存在
    if not Path(input_video).exists():
        print(f"⚠️  示例文件不存在: {input_video}")
        print("请将视频文件放在 input/ 目录中，并重命名为 sample_video.mp4")
        return
    
    print(f"📁 处理文件: {input_video}")
    
    # 1. 获取视频信息
    print("\n1️⃣ 获取视频信息")
    info = get_video_info(input_video)
    print(f"   文件大小: {info.get('file_size', '未知')}")
    print(f"   持续时间: {info.get('duration_formatted', '未知')}")
    print(f"   分辨率: {info.get('width', '?')}x{info.get('height', '?')}")
    print(f"   帧率: {info.get('fps', '未知')} fps")
    
    # 2. 视频剪切
    print("\n2️⃣ 视频剪切 (前30秒)")
    cut_output = "output/cut_video.mp4"
    success = video_processor.cut_video(
        input_video, cut_output, 
        start_time=0, end_time=30
    )
    if success:
        print(f"   ✅ 剪切完成: {cut_output}")
    else:
        print("   ❌ 剪切失败")
    
    # 3. 视频压缩
    print("\n3️⃣ 视频压缩")
    compress_output = "output/compressed_video.mp4"
    success = video_processor.compress_video(
        input_video, compress_output, 
        quality="medium"
    )
    if success:
        print(f"   ✅ 压缩完成: {compress_output}")
    else:
        print("   ❌ 压缩失败")
    
    # 4. 提取音频
    print("\n4️⃣ 提取音频")
    audio_output = "output/extracted_audio.mp3"
    success = audio_processor.extract_audio_from_video(
        input_video, audio_output
    )
    if success:
        print(f"   ✅ 音频提取完成: {audio_output}")
    else:
        print("   ❌ 音频提取失败")
    
    # 5. 调整视频大小
    print("\n5️⃣ 调整视频大小 (720p)")
    resize_output = "output/resized_video.mp4"
    success = video_processor.resize_video(
        input_video, resize_output, 
        target_resolution=(1280, 720)
    )
    if success:
        print(f"   ✅ 大小调整完成: {resize_output}")
    else:
        print("   ❌ 大小调整失败")
    
    print("\n🎉 基础视频编辑示例完成！")
    print("📂 输出文件位于 output/ 目录中")


def video_concatenation_example():
    """视频拼接示例"""
    print("\n🔗 视频拼接示例")
    print("=" * 50)
    
    video_processor = VideoProcessor()
    
    # 示例：将多个视频片段拼接
    video_files = [
        "input/video1.mp4",
        "input/video2.mp4",
        "input/video3.mp4"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in video_files if Path(f).exists()]
    
    if len(existing_files) < 2:
        print("⚠️  需要至少2个视频文件进行拼接")
        print("请将视频文件放在 input/ 目录中")
        return
    
    print(f"📁 拼接文件: {existing_files}")
    
    # 拼接视频
    concat_output = "output/concatenated_video.mp4"
    success = video_processor.concatenate_videos(
        existing_files, concat_output
    )
    
    if success:
        print(f"✅ 拼接完成: {concat_output}")
    else:
        print("❌ 拼接失败")


def audio_processing_example():
    """音频处理示例"""
    print("\n🎵 音频处理示例")
    print("=" * 50)
    
    audio_processor = AudioProcessor()
    
    # 示例音频文件
    background_audio = "input/background_music.mp3"
    voice_audio = "input/voice.mp3"
    
    # 检查文件是否存在
    if not Path(background_audio).exists() or not Path(voice_audio).exists():
        print("⚠️  需要背景音乐和语音文件")
        print("请将音频文件放在 input/ 目录中：")
        print("  - background_music.mp3")
        print("  - voice.mp3")
        return
    
    # 混合音频
    mixed_output = "output/mixed_audio.mp3"
    success = audio_processor.mix_audios(
        background_audio, voice_audio, mixed_output,
        background_volume=0.3, foreground_volume=1.0
    )
    
    if success:
        print(f"✅ 音频混合完成: {mixed_output}")
    else:
        print("❌ 音频混合失败")
    
    # 音频剪切
    if Path(voice_audio).exists():
        cut_audio_output = "output/cut_audio.mp3"
        success = audio_processor.cut_audio(
            voice_audio, cut_audio_output,
            start_time=10, duration=30
        )
        
        if success:
            print(f"✅ 音频剪切完成: {cut_audio_output}")
        else:
            print("❌ 音频剪切失败")


def subtitle_example():
    """字幕处理示例"""
    print("\n📝 字幕处理示例")
    print("=" * 50)
    
    subtitle_processor = SubtitleProcessor()
    
    # 创建示例字幕
    sample_subtitles = [
        {"text": "欢迎使用MoviePy Tools", "start": 0, "end": 3},
        {"text": "这是一个自动化视频剪辑工具", "start": 3, "end": 6},
        {"text": "支持视频、音频和字幕处理", "start": 6, "end": 9},
        {"text": "让视频编辑变得简单高效", "start": 9, "end": 12}
    ]
    
    # 创建字幕文件
    subtitle_file = "output/sample_subtitles.srt"
    success = subtitle_processor.create_subtitle_file(
        sample_subtitles, subtitle_file
    )
    
    if success:
        print(f"✅ 字幕文件创建完成: {subtitle_file}")
    else:
        print("❌ 字幕文件创建失败")
    
    # 如果有视频文件，添加字幕
    input_video = "input/sample_video.mp4"
    if Path(input_video).exists() and success:
        video_with_subtitles = "output/video_with_subtitles.mp4"
        success = subtitle_processor.add_subtitles_to_video(
            input_video, subtitle_file, video_with_subtitles
        )
        
        if success:
            print(f"✅ 字幕添加完成: {video_with_subtitles}")
        else:
            print("❌ 字幕添加失败")


def main():
    """主函数"""
    print("🎬 MoviePy Tools 示例演示")
    print("=" * 60)
    
    # 创建输出目录
    Path("output").mkdir(exist_ok=True)
    
    try:
        # 运行各种示例
        basic_video_operations()
        video_concatenation_example()
        audio_processing_example()
        subtitle_example()
        
        print("\n" + "=" * 60)
        print("🎉 所有示例演示完成！")
        print("📂 查看 output/ 目录中的输出文件")
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 