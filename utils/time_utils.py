"""
时间处理工具函数
"""

import re
from typing import Union
import logging

logger = logging.getLogger(__name__)


def parse_time_string(time_str: Union[str, float, int]) -> float:
    """解析时间字符串为秒数
    
    Args:
        time_str: 时间字符串，支持格式：
                 - "HH:MM:SS" (如 "01:30:45")
                 - "MM:SS" (如 "30:45")
                 - "SS" (如 "45")
                 - 数字 (直接返回)
                 
    Returns:
        float: 时间（秒）
    """
    if isinstance(time_str, (int, float)):
        return float(time_str)
    
    if not isinstance(time_str, str):
        raise ValueError(f"时间格式不支持: {type(time_str)}")
    
    time_str = time_str.strip()
    
    # 匹配 HH:MM:SS 格式
    pattern_hms = r'^(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d+))?$'
    match = re.match(pattern_hms, time_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        milliseconds = int(match.group(4) or 0)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if milliseconds:
            # 处理毫秒
            total_seconds += milliseconds / (10 ** len(match.group(4)))
        
        return float(total_seconds)
    
    # 匹配 MM:SS 格式
    pattern_ms = r'^(\d{1,2}):(\d{1,2})(?:\.(\d+))?$'
    match = re.match(pattern_ms, time_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        milliseconds = int(match.group(3) or 0)
        
        total_seconds = minutes * 60 + seconds
        if milliseconds:
            total_seconds += milliseconds / (10 ** len(match.group(3)))
        
        return float(total_seconds)
    
    # 匹配纯数字格式（秒）
    pattern_s = r'^(\d+)(?:\.(\d+))?$'
    match = re.match(pattern_s, time_str)
    if match:
        seconds = int(match.group(1))
        milliseconds = int(match.group(2) or 0)
        
        total_seconds = seconds
        if milliseconds:
            total_seconds += milliseconds / (10 ** len(match.group(2)))
        
        return float(total_seconds)
    
    raise ValueError(f"无法解析时间格式: {time_str}")


def seconds_to_time_string(seconds: Union[int, float], 
                          format_type: str = "HH:MM:SS") -> str:
    """将秒数转换为时间字符串
    
    Args:
        seconds: 秒数
        format_type: 格式类型 ("HH:MM:SS", "MM:SS", "SS")
        
    Returns:
        str: 时间字符串
    """
    if seconds < 0:
        raise ValueError("时间不能为负数")
    
    total_seconds = int(seconds)
    milliseconds = int((seconds - total_seconds) * 1000)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if format_type == "HH:MM:SS":
        if milliseconds > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    elif format_type == "MM:SS":
        total_minutes = total_seconds // 60
        secs = total_seconds % 60
        if milliseconds > 0:
            return f"{total_minutes:02d}:{secs:02d}.{milliseconds:03d}"
        else:
            return f"{total_minutes:02d}:{secs:02d}"
    elif format_type == "SS":
        if milliseconds > 0:
            return f"{total_seconds}.{milliseconds:03d}"
        else:
            return str(total_seconds)
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


def seconds_to_srt_time(seconds: Union[int, float]) -> str:
    """将秒数转换为SRT字幕时间格式
    
    Args:
        seconds: 秒数
        
    Returns:
        str: SRT时间格式 (HH:MM:SS,mmm)
    """
    if seconds < 0:
        raise ValueError("时间不能为负数")
    
    total_seconds = int(seconds)
    milliseconds = int((seconds - total_seconds) * 1000)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def srt_time_to_seconds(srt_time: str) -> float:
    """将SRT时间格式转换为秒数
    
    Args:
        srt_time: SRT时间格式 (HH:MM:SS,mmm)
        
    Returns:
        float: 秒数
    """
    # 匹配 HH:MM:SS,mmm 格式
    pattern = r'^(\d{1,2}):(\d{1,2}):(\d{1,2}),(\d{1,3})$'
    match = re.match(pattern, srt_time.strip())
    
    if not match:
        raise ValueError(f"无效的SRT时间格式: {srt_time}")
    
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    milliseconds = int(match.group(4))
    
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return total_seconds


def format_duration(seconds: Union[int, float], 
                   show_milliseconds: bool = False) -> str:
    """格式化持续时间为易读格式
    
    Args:
        seconds: 秒数
        show_milliseconds: 是否显示毫秒
        
    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 0:
        return "0秒"
    
    total_seconds = int(seconds)
    milliseconds = int((seconds - total_seconds) * 1000)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    parts = []
    
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if secs > 0 or (hours == 0 and minutes == 0):
        if show_milliseconds and milliseconds > 0:
            parts.append(f"{secs}.{milliseconds:03d}秒")
        else:
            parts.append(f"{secs}秒")
    
    return "".join(parts)


def calculate_time_offset(start_time: Union[str, float], 
                         target_time: Union[str, float]) -> float:
    """计算时间偏移量
    
    Args:
        start_time: 起始时间
        target_time: 目标时间
        
    Returns:
        float: 偏移量（秒）
    """
    start_seconds = parse_time_string(start_time)
    target_seconds = parse_time_string(target_time)
    
    return target_seconds - start_seconds


def validate_time_range(start_time: Union[str, float], 
                       end_time: Union[str, float],
                       duration: Union[str, float] = None) -> bool:
    """验证时间范围是否有效
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        duration: 总时长（可选，用于验证结束时间不超过总时长）
        
    Returns:
        bool: 是否有效
    """
    try:
        start_seconds = parse_time_string(start_time)
        end_seconds = parse_time_string(end_time)
        
        # 检查开始时间是否小于结束时间
        if start_seconds >= end_seconds:
            logger.error(f"开始时间 ({start_seconds}) 必须小于结束时间 ({end_seconds})")
            return False
        
        # 检查时间是否为负数
        if start_seconds < 0 or end_seconds < 0:
            logger.error("时间不能为负数")
            return False
        
        # 如果提供了总时长，检查结束时间是否超过总时长
        if duration is not None:
            duration_seconds = parse_time_string(duration)
            if end_seconds > duration_seconds:
                logger.error(f"结束时间 ({end_seconds}) 超过了总时长 ({duration_seconds})")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"时间范围验证失败: {e}")
        return False


def split_time_into_chunks(total_duration: Union[str, float], 
                          chunk_duration: Union[str, float]) -> list:
    """将总时长分割为多个时间段
    
    Args:
        total_duration: 总时长
        chunk_duration: 每段时长
        
    Returns:
        list: 时间段列表，每个元素是 (start_time, end_time) 元组
    """
    total_seconds = parse_time_string(total_duration)
    chunk_seconds = parse_time_string(chunk_duration)
    
    if chunk_seconds <= 0:
        raise ValueError("分段时长必须大于0")
    
    chunks = []
    current_start = 0
    
    while current_start < total_seconds:
        current_end = min(current_start + chunk_seconds, total_seconds)
        chunks.append((current_start, current_end))
        current_start = current_end
    
    return chunks


def get_time_progress_percentage(current_time: Union[str, float], 
                               total_time: Union[str, float]) -> float:
    """获取时间进度百分比
    
    Args:
        current_time: 当前时间
        total_time: 总时间
        
    Returns:
        float: 进度百分比 (0-100)
    """
    current_seconds = parse_time_string(current_time)
    total_seconds = parse_time_string(total_time)
    
    if total_seconds <= 0:
        return 0.0
    
    percentage = (current_seconds / total_seconds) * 100
    return min(max(percentage, 0.0), 100.0)  # 确保在0-100范围内 