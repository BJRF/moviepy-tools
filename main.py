#!/usr/bin/env python3
"""
MoviePy Tools 主程序入口
自动化视频剪辑工具
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import setup_logging, PROJECT_ROOT
from core import VideoProcessor, AudioProcessor, SubtitleProcessor, BatchProcessor
from utils import get_video_info, get_audio_info, format_duration


def setup_argument_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="MoviePy Tools - 自动化视频剪辑工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s video cut input.mp4 output.mp4 --start 00:01:00 --end 00:02:00
  %(prog)s video concat video1.mp4 video2.mp4 --output merged.mp4
  %(prog)s audio extract input.mp4 --output audio.mp3
  %(prog)s batch convert input_dir output_dir --format mp4
  %(prog)s info input.mp4
        """
    )
    
    # 全局参数
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='启用详细日志输出')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='静默模式，只输出错误信息')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 视频处理命令
    video_parser = subparsers.add_parser('video', help='视频处理')
    video_subparsers = video_parser.add_subparsers(dest='video_action', help='视频操作')
    
    # 视频剪切
    cut_parser = video_subparsers.add_parser('cut', help='剪切视频')
    cut_parser.add_argument('input', help='输入视频文件')
    cut_parser.add_argument('output', help='输出视频文件')
    cut_parser.add_argument('--start', '-s', required=True, help='开始时间 (HH:MM:SS)')
    cut_parser.add_argument('--end', '-e', help='结束时间 (HH:MM:SS)')
    cut_parser.add_argument('--duration', '-d', help='持续时间 (HH:MM:SS)')
    
    # 视频拼接
    concat_parser = video_subparsers.add_parser('concat', help='拼接视频')
    concat_parser.add_argument('inputs', nargs='+', help='输入视频文件列表')
    concat_parser.add_argument('--output', '-o', required=True, help='输出视频文件')
    
    # 视频压缩
    compress_parser = video_subparsers.add_parser('compress', help='压缩视频')
    compress_parser.add_argument('input', help='输入视频文件')
    compress_parser.add_argument('output', help='输出视频文件')
    compress_parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], 
                                default='medium', help='压缩质量')
    
    # 视频调整大小
    resize_parser = video_subparsers.add_parser('resize', help='调整视频大小')
    resize_parser.add_argument('input', help='输入视频文件')
    resize_parser.add_argument('output', help='输出视频文件')
    resize_parser.add_argument('--width', '-w', type=int, help='目标宽度')
    resize_parser.add_argument('--height', type=int, help='目标高度')
    resize_parser.add_argument('--resolution', '-r', help='目标分辨率 (如 1920x1080)')
    
    # 音频处理命令
    audio_parser = subparsers.add_parser('audio', help='音频处理')
    audio_subparsers = audio_parser.add_subparsers(dest='audio_action', help='音频操作')
    
    # 音频提取
    extract_parser = audio_subparsers.add_parser('extract', help='从视频提取音频')
    extract_parser.add_argument('input', help='输入视频文件')
    extract_parser.add_argument('--output', '-o', help='输出音频文件')
    extract_parser.add_argument('--format', '-f', choices=['mp3', 'wav', 'aac'], 
                               default='mp3', help='音频格式')
    
    # 音频剪切
    audio_cut_parser = audio_subparsers.add_parser('cut', help='剪切音频')
    audio_cut_parser.add_argument('input', help='输入音频文件')
    audio_cut_parser.add_argument('output', help='输出音频文件')
    audio_cut_parser.add_argument('--start', '-s', required=True, help='开始时间')
    audio_cut_parser.add_argument('--end', '-e', help='结束时间')
    audio_cut_parser.add_argument('--duration', '-d', help='持续时间')
    
    # 音频混合
    mix_parser = audio_subparsers.add_parser('mix', help='混合音频')
    mix_parser.add_argument('background', help='背景音频文件')
    mix_parser.add_argument('foreground', help='前景音频文件')
    mix_parser.add_argument('--output', '-o', required=True, help='输出音频文件')
    mix_parser.add_argument('--bg-volume', type=float, default=0.3, help='背景音量 (0-1)')
    mix_parser.add_argument('--fg-volume', type=float, default=1.0, help='前景音量 (0-1)')
    
    # 字幕处理命令
    subtitle_parser = subparsers.add_parser('subtitle', help='字幕处理')
    subtitle_subparsers = subtitle_parser.add_subparsers(dest='subtitle_action', help='字幕操作')
    
    # 添加字幕
    add_sub_parser = subtitle_subparsers.add_parser('add', help='为视频添加字幕')
    add_sub_parser.add_argument('video', help='输入视频文件')
    add_sub_parser.add_argument('subtitle', help='字幕文件')
    add_sub_parser.add_argument('--output', '-o', required=True, help='输出视频文件')
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='批量处理')
    batch_subparsers = batch_parser.add_subparsers(dest='batch_action', help='批量操作')
    
    # 批量转换
    batch_convert_parser = batch_subparsers.add_parser('convert', help='批量转换格式')
    batch_convert_parser.add_argument('input_dir', help='输入目录')
    batch_convert_parser.add_argument('output_dir', help='输出目录')
    batch_convert_parser.add_argument('--format', '-f', default='mp4', help='目标格式')
    batch_convert_parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], 
                                     default='medium', help='压缩质量')
    
    # 批量剪切
    batch_cut_parser = batch_subparsers.add_parser('cut', help='批量剪切视频')
    batch_cut_parser.add_argument('input_dir', help='输入目录')
    batch_cut_parser.add_argument('output_dir', help='输出目录')
    batch_cut_parser.add_argument('--start', '-s', required=True, help='开始时间')
    batch_cut_parser.add_argument('--end', '-e', help='结束时间')
    batch_cut_parser.add_argument('--duration', '-d', help='持续时间')
    
    # 信息查看命令
    info_parser = subparsers.add_parser('info', help='查看文件信息')
    info_parser.add_argument('input', help='输入文件')
    
    return parser


def handle_video_commands(args, video_processor: VideoProcessor) -> bool:
    """处理视频相关命令"""
    if args.video_action == 'cut':
        return video_processor.cut_video(
            args.input, args.output, args.start, args.end, args.duration
        )
    
    elif args.video_action == 'concat':
        return video_processor.concatenate_videos(args.inputs, args.output)
    
    elif args.video_action == 'compress':
        return video_processor.compress_video(args.input, args.output, args.quality)
    
    elif args.video_action == 'resize':
        if args.resolution:
            try:
                width, height = map(int, args.resolution.split('x'))
                target_resolution = (width, height)
            except ValueError:
                print(f"错误: 无效的分辨率格式: {args.resolution}")
                return False
        elif args.width and args.height:
            target_resolution = (args.width, args.height)
        else:
            print("错误: 请指定 --resolution 或 --width 和 --height")
            return False
        
        return video_processor.resize_video(args.input, args.output, target_resolution)
    
    return False


def handle_audio_commands(args, audio_processor: AudioProcessor) -> bool:
    """处理音频相关命令"""
    if args.audio_action == 'extract':
        output_path = args.output
        if not output_path:
            input_path = Path(args.input)
            output_path = input_path.with_suffix(f'.{args.format}')
        
        return audio_processor.extract_audio_from_video(args.input, output_path)
    
    elif args.audio_action == 'cut':
        return audio_processor.cut_audio(
            args.input, args.output, args.start, args.end, args.duration
        )
    
    elif args.audio_action == 'mix':
        return audio_processor.mix_audios(
            args.background, args.foreground, args.output,
            args.bg_volume, args.fg_volume
        )
    
    return False


def handle_subtitle_commands(args, subtitle_processor: SubtitleProcessor) -> bool:
    """处理字幕相关命令"""
    if args.subtitle_action == 'add':
        return subtitle_processor.add_subtitles_to_video(
            args.video, args.subtitle, args.output
        )
    
    return False


def handle_batch_commands(args, batch_processor: BatchProcessor) -> bool:
    """处理批量处理命令"""
    if args.batch_action == 'convert':
        results = batch_processor.batch_convert_video_format(
            args.input_dir, args.output_dir, args.format, args.quality
        )
        
        # 保存处理报告
        report_path = Path(args.output_dir) / "batch_convert_report.json"
        batch_processor.save_batch_report(results, report_path)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"批量转换完成: {success_count}/{len(results)} 个文件成功")
        return success_count > 0
    
    elif args.batch_action == 'cut':
        results = batch_processor.batch_cut_videos(
            args.input_dir, args.output_dir, args.start, args.end, args.duration
        )
        
        # 保存处理报告
        report_path = Path(args.output_dir) / "batch_cut_report.json"
        batch_processor.save_batch_report(results, report_path)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"批量剪切完成: {success_count}/{len(results)} 个文件成功")
        return success_count > 0
    
    return False


def handle_info_command(args) -> bool:
    """处理信息查看命令"""
    file_path = Path(args.input)
    
    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return False
    
    file_ext = file_path.suffix.lower()
    
    # 判断文件类型
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv']
    audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    
    if file_ext in video_extensions:
        info = get_video_info(file_path)
        print(f"\n📹 视频文件信息: {info['file_name']}")
        print(f"   文件大小: {info.get('file_size', '未知')}")
        print(f"   持续时间: {info.get('duration_formatted', '未知')}")
        print(f"   分辨率: {info.get('width', '?')}x{info.get('height', '?')}")
        print(f"   帧率: {info.get('fps', '未知')} fps")
        print(f"   包含音频: {'是' if info.get('has_audio') else '否'}")
        
        if info.get('has_audio'):
            print(f"   音频采样率: {info.get('audio_fps', '未知')} Hz")
            print(f"   音频声道: {info.get('audio_channels', '未知')}")
    
    elif file_ext in audio_extensions:
        info = get_audio_info(file_path)
        print(f"\n🎵 音频文件信息: {info['file_name']}")
        print(f"   文件大小: {info.get('file_size', '未知')}")
        print(f"   持续时间: {info.get('duration_formatted', '未知')}")
        print(f"   采样率: {info.get('fps', '未知')} Hz")
        print(f"   声道数: {info.get('channels', '未知')}")
    
    else:
        print(f"错误: 不支持的文件格式: {file_ext}")
        return False
    
    return True


def main():
    """主函数"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # 设置日志
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # 创建处理器实例
        video_processor = VideoProcessor()
        audio_processor = AudioProcessor()
        subtitle_processor = SubtitleProcessor()
        batch_processor = BatchProcessor()
        
        success = False
        
        # 根据命令执行相应操作
        if args.command == 'video':
            success = handle_video_commands(args, video_processor)
        
        elif args.command == 'audio':
            success = handle_audio_commands(args, audio_processor)
        
        elif args.command == 'subtitle':
            success = handle_subtitle_commands(args, subtitle_processor)
        
        elif args.command == 'batch':
            success = handle_batch_commands(args, batch_processor)
        
        elif args.command == 'info':
            success = handle_info_command(args)
        
        else:
            print(f"错误: 未知命令: {args.command}")
            parser.print_help()
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        return 1
    except Exception as e:
        logger.error(f"执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 