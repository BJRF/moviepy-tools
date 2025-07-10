"""
视频处理核心模块
提供视频剪辑、拼接、转换等功能
"""

import logging
from pathlib import Path
from typing import List, Tuple, Optional, Union
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import Resize, MultiplySpeed, FadeIn, FadeOut
from config import VIDEO_CONFIG, get_quality_preset
from utils.file_utils import ensure_output_dir, get_unique_filename
from utils.time_utils import parse_time_string

logger = logging.getLogger(__name__)


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, config=None):
        """初始化视频处理器
        
        Args:
            config: 自定义配置，如果为None则使用默认配置
        """
        self.config = config or VIDEO_CONFIG
        
    def load_video(self, file_path: Union[str, Path]) -> VideoFileClip:
        """加载视频文件
        
        Args:
            file_path: 视频文件路径
            
        Returns:
            VideoFileClip: 加载的视频对象
        """
        try:
            clip = VideoFileClip(str(file_path))
            logger.info(f"成功加载视频: {file_path}")
            logger.info(f"视频信息: {clip.duration:.2f}秒, {clip.size}, {clip.fps}fps")
            return clip
        except Exception as e:
            logger.error(f"加载视频失败: {file_path}, 错误: {e}")
            raise
    
    def cut_video(self, 
                  input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  start_time: Union[str, float],
                  end_time: Union[str, float] = None,
                  duration: Union[str, float] = None) -> bool:
        """剪切视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start_time: 开始时间（秒或时间字符串如"00:01:30"）
            end_time: 结束时间（秒或时间字符串）
            duration: 持续时间（秒或时间字符串）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_video(input_path)
            
            # 转换时间格式
            start = parse_time_string(start_time) if isinstance(start_time, str) else start_time
            
            if end_time is not None:
                end = parse_time_string(end_time) if isinstance(end_time, str) else end_time
                cut_clip = clip.subclip(start, end)
            elif duration is not None:
                dur = parse_time_string(duration) if isinstance(duration, str) else duration
                cut_clip = clip.subclip(start, start + dur)
            else:
                cut_clip = clip.subclip(start)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            cut_clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"]
            )
            
            # 清理资源
            cut_clip.close()
            clip.close()
            
            logger.info(f"视频剪切完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频剪切失败: {e}")
            return False
    
    def concatenate_videos(self, 
                          input_paths: List[Union[str, Path]],
                          output_path: Union[str, Path],
                          method: str = "compose") -> bool:
        """拼接多个视频
        
        Args:
            input_paths: 输入视频路径列表
            output_path: 输出视频路径
            method: 拼接方法 ("compose" 或 "chain")
            
        Returns:
            bool: 是否成功
        """
        try:
            clips = []
            for path in input_paths:
                clip = self.load_video(path)
                clips.append(clip)
            
            # 拼接视频
            if method == "compose":
                final_clip = concatenate_videoclips(clips, method="compose")
            else:
                final_clip = concatenate_videoclips(clips, method="chain")
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            final_clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"]
            )
            
            # 清理资源
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f"视频拼接完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频拼接失败: {e}")
            return False
    
    def resize_video(self,
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    target_resolution: Tuple[int, int] = None,
                    scale_factor: float = None) -> bool:
        """调整视频分辨率
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            target_resolution: 目标分辨率 (width, height)
            scale_factor: 缩放因子（如0.5表示缩小一半）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_video(input_path)
            
            if target_resolution:
                resized_clip = clip.resized(newsize=target_resolution)
            elif scale_factor:
                resized_clip = clip.resized(scale_factor)
            else:
                # 使用默认分辨率
                resized_clip = clip.resized(newsize=self.config["default_resolution"])
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            resized_clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"]
            )
            
            # 清理资源
            resized_clip.close()
            clip.close()
            
            logger.info(f"视频分辨率调整完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频分辨率调整失败: {e}")
            return False
    
    def change_speed(self,
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    speed_factor: float) -> bool:
        """改变视频播放速度
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            speed_factor: 速度因子（>1加速，<1减速）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_video(input_path)
            
            # 改变速度
            speed_clip = clip.with_multiply_speed(speed_factor)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            speed_clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"]
            )
            
            # 清理资源
            speed_clip.close()
            clip.close()
            
            logger.info(f"视频速度调整完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频速度调整失败: {e}")
            return False
    
    def add_fade_effect(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       fade_in_duration: float = 1.0,
                       fade_out_duration: float = 1.0) -> bool:
        """添加淡入淡出效果
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            fade_in_duration: 淡入时长（秒）
            fade_out_duration: 淡出时长（秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_video(input_path)
            
            # 添加淡入淡出效果
            fade_clip = clip.with_effects([FadeIn(fade_in_duration), FadeOut(fade_out_duration)])
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            fade_clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"]
            )
            
            # 清理资源
            fade_clip.close()
            clip.close()
            
            logger.info(f"视频淡入淡出效果添加完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频淡入淡出效果添加失败: {e}")
            return False
    
    def compress_video(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      quality: str = "medium") -> bool:
        """压缩视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            quality: 质量等级 ("low", "medium", "high", "ultra")
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_video(input_path)
            
            # 获取质量预设
            preset = get_quality_preset(quality)
            
            # 调整分辨率
            if clip.size != preset["resolution"]:
                clip = clip.resized(newsize=preset["resolution"])
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存压缩后的视频
            clip.write_videofile(
                str(output_path),
                codec=self.config["default_codec"],
                audio_codec=self.config["default_audio_codec"],
                bitrate=preset["audio_bitrate"],
                fps=preset["fps"]
            )
            
            # 清理资源
            clip.close()
            
            logger.info(f"视频压缩完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"视频压缩失败: {e}")
            return False 