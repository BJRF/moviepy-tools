"""
音频处理核心模块
提供音频提取、混合、调整等功能
"""

import logging
from pathlib import Path
from typing import List, Union, Optional
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx import MultiplyVolume, AudioFadeIn, AudioFadeOut
from config import AUDIO_CONFIG
from utils.file_utils import ensure_output_dir
from utils.time_utils import parse_time_string

logger = logging.getLogger(__name__)


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self, config=None):
        """初始化音频处理器
        
        Args:
            config: 自定义配置，如果为None则使用默认配置
        """
        self.config = config or AUDIO_CONFIG
        
    def load_audio(self, file_path: Union[str, Path]) -> AudioFileClip:
        """加载音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            AudioFileClip: 加载的音频对象
        """
        try:
            clip = AudioFileClip(str(file_path))
            logger.info(f"成功加载音频: {file_path}")
            logger.info(f"音频信息: {clip.duration:.2f}秒")
            return clip
        except Exception as e:
            logger.error(f"加载音频失败: {file_path}, 错误: {e}")
            raise
    
    def extract_audio_from_video(self,
                                input_path: Union[str, Path],
                                output_path: Union[str, Path],
                                start_time: Union[str, float] = None,
                                end_time: Union[str, float] = None) -> bool:
        """从视频中提取音频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出音频路径
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            bool: 是否成功
        """
        try:
            video_clip = VideoFileClip(str(input_path))
            audio_clip = video_clip.audio
            
            # 如果指定了时间范围，则截取
            if start_time is not None or end_time is not None:
                start = parse_time_string(start_time) if isinstance(start_time, str) else start_time
                end = parse_time_string(end_time) if isinstance(end_time, str) else end_time
                
                if start is not None and end is not None:
                    audio_clip = audio_clip.subclip(start, end)
                elif start is not None:
                    audio_clip = audio_clip.subclip(start)
                elif end is not None:
                    audio_clip = audio_clip.subclip(0, end)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            audio_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            audio_clip.close()
            video_clip.close()
            
            logger.info(f"音频提取完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            return False
    
    def cut_audio(self,
                  input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  start_time: Union[str, float],
                  end_time: Union[str, float] = None,
                  duration: Union[str, float] = None) -> bool:
        """剪切音频
        
        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            start_time: 开始时间
            end_time: 结束时间
            duration: 持续时间
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_audio(input_path)
            
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
            
            # 保存音频
            cut_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            cut_clip.close()
            clip.close()
            
            logger.info(f"音频剪切完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频剪切失败: {e}")
            return False
    
    def concatenate_audios(self,
                          input_paths: List[Union[str, Path]],
                          output_path: Union[str, Path]) -> bool:
        """拼接多个音频文件
        
        Args:
            input_paths: 输入音频路径列表
            output_path: 输出音频路径
            
        Returns:
            bool: 是否成功
        """
        try:
            clips = []
            for path in input_paths:
                clip = self.load_audio(path)
                clips.append(clip)
            
            # 拼接音频
            final_clip = CompositeAudioClip(clips)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            final_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f"音频拼接完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频拼接失败: {e}")
            return False
    
    def mix_audios(self,
                   background_path: Union[str, Path],
                   foreground_path: Union[str, Path],
                   output_path: Union[str, Path],
                   background_volume: float = 0.3,
                   foreground_volume: float = 1.0) -> bool:
        """混合两个音频文件
        
        Args:
            background_path: 背景音频路径
            foreground_path: 前景音频路径
            output_path: 输出音频路径
            background_volume: 背景音频音量（0-1）
            foreground_volume: 前景音频音量（0-1）
            
        Returns:
            bool: 是否成功
        """
        try:
            background = self.load_audio(background_path)
            foreground = self.load_audio(foreground_path)
            
            # 调整音量
            if background_volume != 1.0:
                background = background.with_multiply_volume(background_volume)
            if foreground_volume != 1.0:
                foreground = foreground.with_multiply_volume(foreground_volume)
            
            # 确保背景音频长度足够
            if background.duration < foreground.duration:
                # 循环背景音频
                repeat_times = int(foreground.duration / background.duration) + 1
                background = CompositeAudioClip([background] * repeat_times)
                background = background.subclip(0, foreground.duration)
            else:
                # 截取背景音频
                background = background.subclip(0, foreground.duration)
            
            # 混合音频
            mixed_clip = CompositeAudioClip([background, foreground])
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            mixed_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            background.close()
            foreground.close()
            mixed_clip.close()
            
            logger.info(f"音频混合完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频混合失败: {e}")
            return False
    
    def adjust_volume(self,
                     input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     volume_factor: float) -> bool:
        """调整音频音量
        
        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            volume_factor: 音量因子（1.0为原音量）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_audio(input_path)
            
            # 调整音量
            volume_clip = clip.with_multiply_volume(volume_factor)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            volume_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            volume_clip.close()
            clip.close()
            
            logger.info(f"音频音量调整完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频音量调整失败: {e}")
            return False
    
    def add_fade_effect(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       fade_in_duration: float = 1.0,
                       fade_out_duration: float = 1.0) -> bool:
        """添加音频淡入淡出效果
        
        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            fade_in_duration: 淡入时长（秒）
            fade_out_duration: 淡出时长（秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_audio(input_path)
            
            # 添加淡入淡出效果
            fade_clip = clip.with_effects([AudioFadeIn(fade_in_duration), AudioFadeOut(fade_out_duration)])
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            fade_clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            fade_clip.close()
            clip.close()
            
            logger.info(f"音频淡入淡出效果添加完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频淡入淡出效果添加失败: {e}")
            return False
    
    def convert_format(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      target_format: str = None) -> bool:
        """转换音频格式
        
        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            target_format: 目标格式（如果为None则从输出路径推断）
            
        Returns:
            bool: 是否成功
        """
        try:
            clip = self.load_audio(input_path)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存音频
            clip.write_audiofile(
                str(output_path),
                bitrate=self.config["default_bitrate"],
                fps=self.config["default_sample_rate"]
            )
            
            # 清理资源
            clip.close()
            
            logger.info(f"音频格式转换完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频格式转换失败: {e}")
            return False 