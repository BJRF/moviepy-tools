"""
字幕处理核心模块
提供字幕添加、编辑、转换等功能
"""

import logging
from pathlib import Path
from typing import List, Union, Optional, Tuple
import pysrt
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from config import SUBTITLE_CONFIG
from utils.file_utils import ensure_output_dir
from utils.time_utils import parse_time_string, seconds_to_srt_time

logger = logging.getLogger(__name__)


class SubtitleProcessor:
    """字幕处理器"""
    
    def __init__(self, config=None):
        """初始化字幕处理器
        
        Args:
            config: 自定义配置，如果为None则使用默认配置
        """
        self.config = config or SUBTITLE_CONFIG
        
    def load_subtitle(self, file_path: Union[str, Path]) -> pysrt.SubRipFile:
        """加载字幕文件
        
        Args:
            file_path: 字幕文件路径
            
        Returns:
            pysrt.SubRipFile: 字幕对象
        """
        try:
            subs = pysrt.open(str(file_path), encoding=self.config["default_encoding"])
            logger.info(f"成功加载字幕: {file_path}")
            logger.info(f"字幕条数: {len(subs)}")
            return subs
        except Exception as e:
            logger.error(f"加载字幕失败: {file_path}, 错误: {e}")
            raise
    
    def create_subtitle_clip(self,
                           text: str,
                           start_time: float,
                           end_time: float,
                           font_size: int = None,
                           font_color: str = None,
                           position: Tuple[str, str] = None) -> TextClip:
        """创建字幕剪辑
        
        Args:
            text: 字幕文本
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            font_size: 字体大小
            font_color: 字体颜色
            position: 位置 (horizontal, vertical)
            
        Returns:
            TextClip: 字幕剪辑对象
        """
        try:
            font_size = font_size or self.config["default_font_size"]
            font_color = font_color or self.config["default_color"]
            position = position or self.config["default_position"]
            
            # 创建文本剪辑
            txt_clip = TextClip(
                text,
                fontsize=font_size,
                color=font_color,
                font=self.config["default_font"]
            ).set_position(position).set_duration(end_time - start_time).set_start(start_time)
            
            return txt_clip
            
        except Exception as e:
            logger.error(f"创建字幕剪辑失败: {e}")
            raise
    
    def add_subtitles_to_video(self,
                              video_path: Union[str, Path],
                              subtitle_path: Union[str, Path],
                              output_path: Union[str, Path],
                              font_size: int = None,
                              font_color: str = None,
                              position: Tuple[str, str] = None) -> bool:
        """为视频添加字幕
        
        Args:
            video_path: 视频文件路径
            subtitle_path: 字幕文件路径
            output_path: 输出视频路径
            font_size: 字体大小
            font_color: 字体颜色
            position: 字幕位置
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加载视频
            video = VideoFileClip(str(video_path))
            
            # 加载字幕
            subs = self.load_subtitle(subtitle_path)
            
            # 创建字幕剪辑列表
            subtitle_clips = []
            
            for sub in subs:
                start_time = sub.start.ordinal / 1000.0  # 转换为秒
                end_time = sub.end.ordinal / 1000.0
                
                # 创建字幕剪辑
                txt_clip = self.create_subtitle_clip(
                    sub.text,
                    start_time,
                    end_time,
                    font_size,
                    font_color,
                    position
                )
                
                subtitle_clips.append(txt_clip)
            
            # 合成视频和字幕
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存视频
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac'
            )
            
            # 清理资源
            for clip in subtitle_clips:
                clip.close()
            final_video.close()
            video.close()
            
            logger.info(f"字幕添加完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字幕添加失败: {e}")
            return False
    
    def create_subtitle_file(self,
                           subtitles: List[dict],
                           output_path: Union[str, Path]) -> bool:
        """创建字幕文件
        
        Args:
            subtitles: 字幕列表，每个元素包含 {"text": str, "start": float, "end": float}
            output_path: 输出字幕文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            subs = pysrt.SubRipFile()
            
            for i, sub_data in enumerate(subtitles):
                # 创建字幕项
                sub = pysrt.SubRipItem(
                    index=i + 1,
                    start=pysrt.SubRipTime.from_ordinal(int(sub_data["start"] * 1000)),
                    end=pysrt.SubRipTime.from_ordinal(int(sub_data["end"] * 1000)),
                    text=sub_data["text"]
                )
                subs.append(sub)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存字幕文件
            subs.save(str(output_path), encoding=self.config["default_encoding"])
            
            logger.info(f"字幕文件创建完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字幕文件创建失败: {e}")
            return False
    
    def adjust_subtitle_timing(self,
                             input_path: Union[str, Path],
                             output_path: Union[str, Path],
                             time_offset: float) -> bool:
        """调整字幕时间轴
        
        Args:
            input_path: 输入字幕文件路径
            output_path: 输出字幕文件路径
            time_offset: 时间偏移量（秒，正数表示延后，负数表示提前）
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加载字幕
            subs = self.load_subtitle(input_path)
            
            # 调整时间
            offset_ms = int(time_offset * 1000)
            subs.shift(milliseconds=offset_ms)
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存调整后的字幕
            subs.save(str(output_path), encoding=self.config["default_encoding"])
            
            logger.info(f"字幕时间轴调整完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字幕时间轴调整失败: {e}")
            return False
    
    def extract_text_from_subtitle(self,
                                 input_path: Union[str, Path],
                                 output_path: Union[str, Path] = None) -> Union[List[str], bool]:
        """从字幕文件提取文本
        
        Args:
            input_path: 输入字幕文件路径
            output_path: 输出文本文件路径（可选）
            
        Returns:
            List[str] 或 bool: 如果没有指定输出路径，返回文本列表；否则返回是否成功
        """
        try:
            # 加载字幕
            subs = self.load_subtitle(input_path)
            
            # 提取文本
            texts = [sub.text for sub in subs]
            
            if output_path is None:
                return texts
            
            # 保存到文件
            ensure_output_dir(output_path)
            
            with open(output_path, 'w', encoding=self.config["default_encoding"]) as f:
                for text in texts:
                    f.write(text + '\n')
            
            logger.info(f"字幕文本提取完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字幕文本提取失败: {e}")
            return False if output_path else []
    
    def merge_subtitles(self,
                       input_paths: List[Union[str, Path]],
                       output_path: Union[str, Path]) -> bool:
        """合并多个字幕文件
        
        Args:
            input_paths: 输入字幕文件路径列表
            output_path: 输出字幕文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            merged_subs = pysrt.SubRipFile()
            current_index = 1
            
            for input_path in input_paths:
                subs = self.load_subtitle(input_path)
                
                for sub in subs:
                    # 更新索引
                    sub.index = current_index
                    merged_subs.append(sub)
                    current_index += 1
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存合并后的字幕
            merged_subs.save(str(output_path), encoding=self.config["default_encoding"])
            
            logger.info(f"字幕合并完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"字幕合并失败: {e}")
            return False
    
    def split_subtitle_by_time(self,
                              input_path: Union[str, Path],
                              output_dir: Union[str, Path],
                              split_duration: float) -> bool:
        """按时间分割字幕文件
        
        Args:
            input_path: 输入字幕文件路径
            output_dir: 输出目录
            split_duration: 分割时长（秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加载字幕
            subs = self.load_subtitle(input_path)
            
            if not subs:
                logger.warning("字幕文件为空")
                return False
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            # 计算分割点
            split_duration_ms = int(split_duration * 1000)
            current_time = 0
            part_number = 1
            current_part = pysrt.SubRipFile()
            current_index = 1
            
            for sub in subs:
                sub_start_ms = sub.start.ordinal
                sub_end_ms = sub.end.ordinal
                
                # 如果当前字幕超过分割时间，开始新的部分
                if sub_start_ms >= current_time + split_duration_ms:
                    if current_part:
                        # 保存当前部分
                        output_path = Path(output_dir) / f"part_{part_number:02d}.srt"
                        current_part.save(str(output_path), encoding=self.config["default_encoding"])
                        logger.info(f"字幕分割部分 {part_number} 保存完成: {output_path}")
                    
                    # 开始新的部分
                    current_part = pysrt.SubRipFile()
                    current_time = sub_start_ms
                    part_number += 1
                    current_index = 1
                
                # 添加到当前部分
                sub.index = current_index
                current_part.append(sub)
                current_index += 1
            
            # 保存最后一部分
            if current_part:
                output_path = Path(output_dir) / f"part_{part_number:02d}.srt"
                current_part.save(str(output_path), encoding=self.config["default_encoding"])
                logger.info(f"字幕分割部分 {part_number} 保存完成: {output_path}")
            
            logger.info(f"字幕分割完成，共 {part_number} 个部分")
            return True
            
        except Exception as e:
            logger.error(f"字幕分割失败: {e}")
            return False 