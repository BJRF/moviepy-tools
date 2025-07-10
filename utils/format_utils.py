"""
格式处理工具函数
"""

import os
from pathlib import Path
from typing import Union, Dict, Any, Optional
import logging
from moviepy import VideoFileClip, AudioFileClip

logger = logging.getLogger(__name__)


def get_video_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """获取视频文件信息
    
    Args:
        file_path: 视频文件路径
        
    Returns:
        Dict: 视频信息字典
    """
    try:
        clip = VideoFileClip(str(file_path))
        
        info = {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "file_size": get_file_size_readable(file_path),
            "file_size_bytes": Path(file_path).stat().st_size,
            "duration": clip.duration,
            "duration_formatted": format_duration(clip.duration),
            "fps": clip.fps,
            "size": clip.size,
            "width": clip.w,
            "height": clip.h,
            "aspect_ratio": f"{clip.w}:{clip.h}",
            "has_audio": clip.audio is not None,
        }
        
        # 如果有音频，获取音频信息
        if clip.audio is not None:
            info.update({
                "audio_fps": clip.audio.fps,
                "audio_duration": clip.audio.duration,
                "audio_channels": clip.audio.nchannels if hasattr(clip.audio, 'nchannels') else None,
            })
        
        clip.close()
        return info
        
    except Exception as e:
        logger.error(f"获取视频信息失败: {file_path}, 错误: {e}")
        return {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "error": str(e)
        }


def get_audio_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """获取音频文件信息
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        Dict: 音频信息字典
    """
    try:
        clip = AudioFileClip(str(file_path))
        
        info = {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "file_size": get_file_size_readable(file_path),
            "file_size_bytes": Path(file_path).stat().st_size,
            "duration": clip.duration,
            "duration_formatted": format_duration(clip.duration),
            "fps": clip.fps,
            "channels": clip.nchannels if hasattr(clip, 'nchannels') else None,
        }
        
        clip.close()
        return info
        
    except Exception as e:
        logger.error(f"获取音频信息失败: {file_path}, 错误: {e}")
        return {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "error": str(e)
        }


def is_valid_video_format(file_path: Union[str, Path]) -> bool:
    """检查是否为有效的视频格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为有效视频格式
    """
    try:
        clip = VideoFileClip(str(file_path))
        is_valid = clip.duration > 0 and clip.size[0] > 0 and clip.size[1] > 0
        clip.close()
        return is_valid
    except Exception:
        return False


def is_valid_audio_format(file_path: Union[str, Path]) -> bool:
    """检查是否为有效的音频格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为有效音频格式
    """
    try:
        clip = AudioFileClip(str(file_path))
        is_valid = clip.duration > 0
        clip.close()
        return is_valid
    except Exception:
        return False


def convert_size_to_readable(size_bytes: int) -> str:
    """将字节大小转换为可读格式
    
    Args:
        size_bytes: 字节大小
        
    Returns:
        str: 可读的大小格式
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"


def get_file_size_readable(file_path: Union[str, Path]) -> str:
    """获取文件的可读大小格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 可读的文件大小
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return convert_size_to_readable(size_bytes)
    except Exception:
        return "未知"


def format_duration(seconds: float) -> str:
    """格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 0:
        return "0秒"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    elif minutes > 0:
        return f"{minutes}:{secs:02d}"
    else:
        return f"{secs}秒"


def get_resolution_category(width: int, height: int) -> str:
    """获取分辨率类别
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        str: 分辨率类别
    """
    total_pixels = width * height
    
    if total_pixels >= 7680 * 4320:  # 8K
        return "8K"
    elif total_pixels >= 3840 * 2160:  # 4K
        return "4K"
    elif total_pixels >= 2560 * 1440:  # 2K
        return "2K"
    elif total_pixels >= 1920 * 1080:  # Full HD
        return "Full HD"
    elif total_pixels >= 1280 * 720:  # HD
        return "HD"
    elif total_pixels >= 854 * 480:  # SD
        return "SD"
    else:
        return "Low"


def calculate_bitrate(file_size_bytes: int, duration_seconds: float) -> str:
    """计算比特率
    
    Args:
        file_size_bytes: 文件大小（字节）
        duration_seconds: 持续时间（秒）
        
    Returns:
        str: 比特率字符串
    """
    if duration_seconds <= 0:
        return "未知"
    
    # 计算比特率 (bits per second)
    bitrate_bps = (file_size_bytes * 8) / duration_seconds
    
    # 转换为合适的单位
    if bitrate_bps >= 1000000:
        return f"{bitrate_bps / 1000000:.2f} Mbps"
    elif bitrate_bps >= 1000:
        return f"{bitrate_bps / 1000:.2f} Kbps"
    else:
        return f"{bitrate_bps:.0f} bps"


def get_aspect_ratio_name(width: int, height: int) -> str:
    """获取宽高比名称
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        str: 宽高比名称
    """
    # 计算最大公约数
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    ratio_gcd = gcd(width, height)
    ratio_w = width // ratio_gcd
    ratio_h = height // ratio_gcd
    
    # 常见宽高比映射
    ratio_names = {
        (16, 9): "16:9 (宽屏)",
        (4, 3): "4:3 (标准)",
        (21, 9): "21:9 (超宽屏)",
        (1, 1): "1:1 (正方形)",
        (3, 2): "3:2",
        (5, 4): "5:4",
        (16, 10): "16:10",
    }
    
    return ratio_names.get((ratio_w, ratio_h), f"{ratio_w}:{ratio_h}")


def estimate_compression_ratio(original_size: int, compressed_size: int) -> str:
    """估算压缩比
    
    Args:
        original_size: 原始文件大小
        compressed_size: 压缩后文件大小
        
    Returns:
        str: 压缩比描述
    """
    if original_size <= 0:
        return "无法计算"
    
    ratio = compressed_size / original_size
    percentage = (1 - ratio) * 100
    
    if percentage > 0:
        return f"压缩了 {percentage:.1f}%"
    else:
        return f"增大了 {abs(percentage):.1f}%"


def get_codec_info(file_path: Union[str, Path]) -> Dict[str, str]:
    """获取编解码器信息（需要ffprobe）
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict: 编解码器信息
    """
    # 这里可以集成ffprobe来获取更详细的编解码器信息
    # 目前返回基本信息
    file_ext = Path(file_path).suffix.lower()
    
    codec_mapping = {
        '.mp4': {'video': 'H.264', 'audio': 'AAC'},
        '.avi': {'video': 'H.264/DivX', 'audio': 'MP3/PCM'},
        '.mkv': {'video': 'H.264/H.265', 'audio': 'AAC/FLAC'},
        '.mov': {'video': 'H.264', 'audio': 'AAC'},
        '.webm': {'video': 'VP8/VP9', 'audio': 'Vorbis/Opus'},
        '.flv': {'video': 'H.264', 'audio': 'AAC/MP3'},
        '.mp3': {'audio': 'MP3'},
        '.wav': {'audio': 'PCM'},
        '.flac': {'audio': 'FLAC'},
        '.aac': {'audio': 'AAC'},
        '.ogg': {'audio': 'Vorbis'},
    }
    
    return codec_mapping.get(file_ext, {'video': '未知', 'audio': '未知'})


def validate_output_format(input_path: Union[str, Path], 
                          output_path: Union[str, Path]) -> bool:
    """验证输出格式是否兼容
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        
    Returns:
        bool: 是否兼容
    """
    input_ext = Path(input_path).suffix.lower()
    output_ext = Path(output_path).suffix.lower()
    
    # 定义兼容的转换
    compatible_conversions = {
        # 视频格式之间的转换
        '.mp4': ['.avi', '.mkv', '.mov', '.webm', '.flv'],
        '.avi': ['.mp4', '.mkv', '.mov', '.webm'],
        '.mkv': ['.mp4', '.avi', '.mov', '.webm'],
        '.mov': ['.mp4', '.avi', '.mkv', '.webm'],
        '.webm': ['.mp4', '.avi', '.mkv', '.mov'],
        '.flv': ['.mp4', '.avi', '.mkv'],
        
        # 音频格式之间的转换
        '.mp3': ['.wav', '.flac', '.aac', '.ogg'],
        '.wav': ['.mp3', '.flac', '.aac', '.ogg'],
        '.flac': ['.mp3', '.wav', '.aac', '.ogg'],
        '.aac': ['.mp3', '.wav', '.flac', '.ogg'],
        '.ogg': ['.mp3', '.wav', '.flac', '.aac'],
    }
    
    # 如果格式相同，总是兼容的
    if input_ext == output_ext:
        return True
    
    # 检查是否在兼容列表中
    return output_ext in compatible_conversions.get(input_ext, []) 