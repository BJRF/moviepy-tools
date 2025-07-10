#!/usr/bin/env python3
"""
批量处理示例
演示如何使用MoviePy Tools进行批量视频处理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import BatchProcessor
from utils import get_files_by_extension


def batch_convert_example():
    """批量格式转换示例"""
    print("🔄 批量格式转换示例")
    print("=" * 50)
    
    batch_processor = BatchProcessor()
    
    # 输入和输出目录
    input_dir = "input/batch_videos"
    output_dir = "output/converted_videos"
    
    # 创建目录
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查输入目录中的视频文件
    video_files = get_files_by_extension(input_dir, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        print(f"⚠️  在 {input_dir} 中没有找到视频文件")
        print("请将要转换的视频文件放在该目录中")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 批量转换为MP4格式
    print("\n开始批量转换...")
    results = batch_processor.batch_convert_video_format(
        input_dir=input_dir,
        output_dir=output_dir,
        target_format="mp4",
        quality="medium"
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n📊 转换结果:")
    print(f"   ✅ 成功: {success_count} 个文件")
    print(f"   ❌ 失败: {failed_count} 个文件")
    
    # 保存详细报告
    report_path = Path(output_dir) / "conversion_report.json"
    batch_processor.save_batch_report(results, report_path)
    print(f"📄 详细报告已保存: {report_path}")


def batch_cut_example():
    """批量剪切示例"""
    print("\n✂️ 批量剪切示例")
    print("=" * 50)
    
    batch_processor = BatchProcessor()
    
    # 输入和输出目录
    input_dir = "input/batch_videos"
    output_dir = "output/cut_videos"
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查输入目录中的视频文件
    video_files = get_files_by_extension(input_dir, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        print(f"⚠️  在 {input_dir} 中没有找到视频文件")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 批量剪切（提取前60秒）
    print("\n开始批量剪切（前60秒）...")
    results = batch_processor.batch_cut_videos(
        input_dir=input_dir,
        output_dir=output_dir,
        start_time=0,
        end_time=60
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n📊 剪切结果:")
    print(f"   ✅ 成功: {success_count} 个文件")
    print(f"   ❌ 失败: {failed_count} 个文件")
    
    # 保存详细报告
    report_path = Path(output_dir) / "cut_report.json"
    batch_processor.save_batch_report(results, report_path)
    print(f"📄 详细报告已保存: {report_path}")


def batch_extract_audio_example():
    """批量提取音频示例"""
    print("\n🎵 批量提取音频示例")
    print("=" * 50)
    
    batch_processor = BatchProcessor()
    
    # 输入和输出目录
    input_dir = "input/batch_videos"
    output_dir = "output/extracted_audio"
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查输入目录中的视频文件
    video_files = get_files_by_extension(input_dir, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        print(f"⚠️  在 {input_dir} 中没有找到视频文件")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 批量提取音频
    print("\n开始批量提取音频...")
    results = batch_processor.batch_extract_audio(
        input_dir=input_dir,
        output_dir=output_dir,
        audio_format="mp3"
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n📊 提取结果:")
    print(f"   ✅ 成功: {success_count} 个文件")
    print(f"   ❌ 失败: {failed_count} 个文件")
    
    # 保存详细报告
    report_path = Path(output_dir) / "extract_report.json"
    batch_processor.save_batch_report(results, report_path)
    print(f"📄 详细报告已保存: {report_path}")


def batch_resize_example():
    """批量调整大小示例"""
    print("\n📐 批量调整大小示例")
    print("=" * 50)
    
    batch_processor = BatchProcessor()
    
    # 输入和输出目录
    input_dir = "input/batch_videos"
    output_dir = "output/resized_videos"
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查输入目录中的视频文件
    video_files = get_files_by_extension(input_dir, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        print(f"⚠️  在 {input_dir} 中没有找到视频文件")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 批量调整为720p
    print("\n开始批量调整大小（720p）...")
    results = batch_processor.batch_resize_videos(
        input_dir=input_dir,
        output_dir=output_dir,
        target_resolution=(1280, 720)
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n📊 调整结果:")
    print(f"   ✅ 成功: {success_count} 个文件")
    print(f"   ❌ 失败: {failed_count} 个文件")
    
    # 保存详细报告
    report_path = Path(output_dir) / "resize_report.json"
    batch_processor.save_batch_report(results, report_path)
    print(f"📄 详细报告已保存: {report_path}")


def batch_add_subtitles_example():
    """批量添加字幕示例"""
    print("\n📝 批量添加字幕示例")
    print("=" * 50)
    
    batch_processor = BatchProcessor()
    
    # 输入目录
    video_dir = "input/batch_videos"
    subtitle_dir = "input/batch_subtitles"
    output_dir = "output/videos_with_subtitles"
    
    # 创建目录
    Path(subtitle_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查视频文件
    video_files = get_files_by_extension(video_dir, ['.mp4', '.avi', '.mov', '.mkv'])
    subtitle_files = get_files_by_extension(subtitle_dir, ['.srt', '.ass', '.vtt'])
    
    if not video_files:
        print(f"⚠️  在 {video_dir} 中没有找到视频文件")
        return
    
    if not subtitle_files:
        print(f"⚠️  在 {subtitle_dir} 中没有找到字幕文件")
        print("请确保字幕文件与视频文件同名（扩展名不同）")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    print(f"📁 找到 {len(subtitle_files)} 个字幕文件")
    
    # 批量添加字幕
    print("\n开始批量添加字幕...")
    results = batch_processor.batch_add_subtitles(
        video_dir=video_dir,
        subtitle_dir=subtitle_dir,
        output_dir=output_dir
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count
    
    print(f"\n📊 添加结果:")
    print(f"   ✅ 成功: {success_count} 个文件")
    print(f"   ❌ 失败: {failed_count} 个文件")
    
    # 保存详细报告
    report_path = Path(output_dir) / "subtitle_report.json"
    batch_processor.save_batch_report(results, report_path)
    print(f"📄 详细报告已保存: {report_path}")


def create_sample_structure():
    """创建示例目录结构"""
    print("\n📁 创建示例目录结构")
    print("=" * 50)
    
    # 创建必要的目录
    directories = [
        "input/batch_videos",
        "input/batch_subtitles",
        "output/converted_videos",
        "output/cut_videos",
        "output/extracted_audio",
        "output/resized_videos",
        "output/videos_with_subtitles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   📂 创建目录: {directory}")
    
    # 创建示例说明文件
    readme_content = """# 批量处理示例说明

## 目录结构

### 输入目录
- `input/batch_videos/` - 放置要处理的视频文件
- `input/batch_subtitles/` - 放置字幕文件（与视频文件同名）

### 输出目录
- `output/converted_videos/` - 格式转换后的视频
- `output/cut_videos/` - 剪切后的视频
- `output/extracted_audio/` - 提取的音频文件
- `output/resized_videos/` - 调整大小后的视频
- `output/videos_with_subtitles/` - 添加字幕后的视频

## 使用方法

1. 将视频文件放在 `input/batch_videos/` 目录中
2. 如需添加字幕，将字幕文件放在 `input/batch_subtitles/` 目录中
3. 运行批量处理脚本：`python examples/batch_processing.py`

## 支持的格式

### 视频格式
- MP4, AVI, MOV, MKV, WebM, FLV

### 音频格式
- MP3, WAV, AAC, FLAC, OGG

### 字幕格式
- SRT, ASS, VTT
"""
    
    readme_path = Path("input/README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   📄 创建说明文件: {readme_path}")
    print("\n✅ 示例目录结构创建完成！")


def main():
    """主函数"""
    print("🔄 MoviePy Tools 批量处理示例")
    print("=" * 60)
    
    try:
        # 创建示例目录结构
        create_sample_structure()
        
        # 运行批量处理示例
        batch_convert_example()
        batch_cut_example()
        batch_extract_audio_example()
        batch_resize_example()
        batch_add_subtitles_example()
        
        print("\n" + "=" * 60)
        print("🎉 批量处理示例演示完成！")
        print("\n📋 使用建议:")
        print("1. 将视频文件放在 input/batch_videos/ 目录中")
        print("2. 运行相应的批量处理功能")
        print("3. 查看 output/ 目录中的处理结果")
        print("4. 查看生成的JSON报告了解详细信息")
        
    except Exception as e:
        print(f"\n❌ 批量处理示例出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 