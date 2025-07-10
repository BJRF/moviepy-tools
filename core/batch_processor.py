"""
批量处理核心模块
提供批量视频处理功能
"""

import logging
import os
from pathlib import Path
from typing import List, Union, Optional, Callable, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json
from config import BATCH_CONFIG, SUPPORTED_FORMATS
from utils.file_utils import get_files_by_extension, ensure_output_dir
from .video_processor import VideoProcessor
from .audio_processor import AudioProcessor
from .subtitle_processor import SubtitleProcessor

logger = logging.getLogger(__name__)


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config=None):
        """初始化批量处理器
        
        Args:
            config: 自定义配置，如果为None则使用默认配置
        """
        self.config = config or BATCH_CONFIG
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.subtitle_processor = SubtitleProcessor()
        
    def process_files_in_parallel(self,
                                 files: List[Path],
                                 process_func: Callable,
                                 max_workers: int = None,
                                 show_progress: bool = True) -> List[Dict[str, Any]]:
        """并行处理文件
        
        Args:
            files: 文件路径列表
            process_func: 处理函数
            max_workers: 最大工作线程数
            show_progress: 是否显示进度条
            
        Returns:
            List[Dict]: 处理结果列表
        """
        max_workers = max_workers or self.config["max_workers"]
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {executor.submit(process_func, file): file for file in files}
            
            # 处理结果
            if show_progress:
                progress_bar = tqdm(total=len(files), desc="处理进度", unit="文件")
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append({
                        "file": str(file_path),
                        "success": True,
                        "result": result,
                        "error": None
                    })
                except Exception as e:
                    logger.error(f"处理文件失败: {file_path}, 错误: {e}")
                    results.append({
                        "file": str(file_path),
                        "success": False,
                        "result": None,
                        "error": str(e)
                    })
                
                if show_progress:
                    progress_bar.update(1)
            
            if show_progress:
                progress_bar.close()
        
        return results
    
    def batch_convert_video_format(self,
                                  input_dir: Union[str, Path],
                                  output_dir: Union[str, Path],
                                  target_format: str = "mp4",
                                  quality: str = "medium") -> List[Dict[str, Any]]:
        """批量转换视频格式
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            target_format: 目标格式
            quality: 视频质量
            
        Returns:
            List[Dict]: 处理结果
        """
        try:
            # 获取视频文件
            video_files = get_files_by_extension(input_dir, SUPPORTED_FORMATS["video"])
            
            if not video_files:
                logger.warning(f"在目录 {input_dir} 中没有找到视频文件")
                return []
            
            logger.info(f"找到 {len(video_files)} 个视频文件")
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            def convert_single_video(input_path: Path) -> bool:
                """转换单个视频文件"""
                output_path = Path(output_dir) / f"{input_path.stem}.{target_format}"
                return self.video_processor.compress_video(input_path, output_path, quality)
            
            # 批量处理
            results = self.process_files_in_parallel(
                video_files,
                convert_single_video,
                show_progress=True
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            logger.info(f"批量转换完成: {success_count}/{len(results)} 个文件成功")
            
            return results
            
        except Exception as e:
            logger.error(f"批量转换视频格式失败: {e}")
            return []
    
    def batch_cut_videos(self,
                        input_dir: Union[str, Path],
                        output_dir: Union[str, Path],
                        start_time: Union[str, float],
                        end_time: Union[str, float] = None,
                        duration: Union[str, float] = None) -> List[Dict[str, Any]]:
        """批量剪切视频
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            start_time: 开始时间
            end_time: 结束时间
            duration: 持续时间
            
        Returns:
            List[Dict]: 处理结果
        """
        try:
            # 获取视频文件
            video_files = get_files_by_extension(input_dir, SUPPORTED_FORMATS["video"])
            
            if not video_files:
                logger.warning(f"在目录 {input_dir} 中没有找到视频文件")
                return []
            
            logger.info(f"找到 {len(video_files)} 个视频文件")
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            def cut_single_video(input_path: Path) -> bool:
                """剪切单个视频文件"""
                output_path = Path(output_dir) / f"{input_path.stem}_cut{input_path.suffix}"
                return self.video_processor.cut_video(
                    input_path, output_path, start_time, end_time, duration
                )
            
            # 批量处理
            results = self.process_files_in_parallel(
                video_files,
                cut_single_video,
                show_progress=True
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            logger.info(f"批量剪切完成: {success_count}/{len(results)} 个文件成功")
            
            return results
            
        except Exception as e:
            logger.error(f"批量剪切视频失败: {e}")
            return []
    
    def batch_extract_audio(self,
                           input_dir: Union[str, Path],
                           output_dir: Union[str, Path],
                           audio_format: str = "mp3") -> List[Dict[str, Any]]:
        """批量提取音频
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            audio_format: 音频格式
            
        Returns:
            List[Dict]: 处理结果
        """
        try:
            # 获取视频文件
            video_files = get_files_by_extension(input_dir, SUPPORTED_FORMATS["video"])
            
            if not video_files:
                logger.warning(f"在目录 {input_dir} 中没有找到视频文件")
                return []
            
            logger.info(f"找到 {len(video_files)} 个视频文件")
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            def extract_single_audio(input_path: Path) -> bool:
                """提取单个视频的音频"""
                output_path = Path(output_dir) / f"{input_path.stem}.{audio_format}"
                return self.audio_processor.extract_audio_from_video(input_path, output_path)
            
            # 批量处理
            results = self.process_files_in_parallel(
                video_files,
                extract_single_audio,
                show_progress=True
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            logger.info(f"批量提取音频完成: {success_count}/{len(results)} 个文件成功")
            
            return results
            
        except Exception as e:
            logger.error(f"批量提取音频失败: {e}")
            return []
    
    def batch_add_subtitles(self,
                           video_dir: Union[str, Path],
                           subtitle_dir: Union[str, Path],
                           output_dir: Union[str, Path]) -> List[Dict[str, Any]]:
        """批量添加字幕
        
        Args:
            video_dir: 视频目录
            subtitle_dir: 字幕目录
            output_dir: 输出目录
            
        Returns:
            List[Dict]: 处理结果
        """
        try:
            # 获取视频文件
            video_files = get_files_by_extension(video_dir, SUPPORTED_FORMATS["video"])
            
            if not video_files:
                logger.warning(f"在目录 {video_dir} 中没有找到视频文件")
                return []
            
            logger.info(f"找到 {len(video_files)} 个视频文件")
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            def add_subtitle_to_video(video_path: Path) -> bool:
                """为单个视频添加字幕"""
                # 查找对应的字幕文件
                subtitle_path = None
                for ext in SUPPORTED_FORMATS["subtitle"]:
                    potential_subtitle = Path(subtitle_dir) / f"{video_path.stem}{ext}"
                    if potential_subtitle.exists():
                        subtitle_path = potential_subtitle
                        break
                
                if not subtitle_path:
                    logger.warning(f"未找到视频 {video_path.name} 对应的字幕文件")
                    return False
                
                output_path = Path(output_dir) / f"{video_path.stem}_with_subtitles{video_path.suffix}"
                return self.subtitle_processor.add_subtitles_to_video(
                    video_path, subtitle_path, output_path
                )
            
            # 批量处理
            results = self.process_files_in_parallel(
                video_files,
                add_subtitle_to_video,
                show_progress=True
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            logger.info(f"批量添加字幕完成: {success_count}/{len(results)} 个文件成功")
            
            return results
            
        except Exception as e:
            logger.error(f"批量添加字幕失败: {e}")
            return []
    
    def batch_resize_videos(self,
                           input_dir: Union[str, Path],
                           output_dir: Union[str, Path],
                           target_resolution: tuple = (1280, 720)) -> List[Dict[str, Any]]:
        """批量调整视频分辨率
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            target_resolution: 目标分辨率
            
        Returns:
            List[Dict]: 处理结果
        """
        try:
            # 获取视频文件
            video_files = get_files_by_extension(input_dir, SUPPORTED_FORMATS["video"])
            
            if not video_files:
                logger.warning(f"在目录 {input_dir} 中没有找到视频文件")
                return []
            
            logger.info(f"找到 {len(video_files)} 个视频文件")
            
            # 确保输出目录存在
            ensure_output_dir(output_dir)
            
            def resize_single_video(input_path: Path) -> bool:
                """调整单个视频分辨率"""
                output_path = Path(output_dir) / f"{input_path.stem}_resized{input_path.suffix}"
                return self.video_processor.resize_video(
                    input_path, output_path, target_resolution
                )
            
            # 批量处理
            results = self.process_files_in_parallel(
                video_files,
                resize_single_video,
                show_progress=True
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            logger.info(f"批量调整分辨率完成: {success_count}/{len(results)} 个文件成功")
            
            return results
            
        except Exception as e:
            logger.error(f"批量调整分辨率失败: {e}")
            return []
    
    def save_batch_report(self,
                         results: List[Dict[str, Any]],
                         output_path: Union[str, Path]) -> bool:
        """保存批量处理报告
        
        Args:
            results: 处理结果列表
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 统计信息
            total_files = len(results)
            success_files = sum(1 for r in results if r["success"])
            failed_files = total_files - success_files
            
            report = {
                "timestamp": str(Path().resolve()),
                "summary": {
                    "total_files": total_files,
                    "success_files": success_files,
                    "failed_files": failed_files,
                    "success_rate": f"{success_files/total_files*100:.1f}%" if total_files > 0 else "0%"
                },
                "details": results
            }
            
            # 确保输出目录存在
            ensure_output_dir(output_path)
            
            # 保存报告
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"批量处理报告保存完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存批量处理报告失败: {e}")
            return False
    
    def cleanup_temp_files(self, temp_dir: Union[str, Path]) -> bool:
        """清理临时文件
        
        Args:
            temp_dir: 临时文件目录
            
        Returns:
            bool: 是否成功
        """
        try:
            temp_path = Path(temp_dir)
            if not temp_path.exists():
                return True
            
            # 删除临时文件
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.debug(f"删除临时文件: {file_path}")
            
            # 删除空目录
            for dir_path in temp_path.rglob("*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.debug(f"删除空目录: {dir_path}")
            
            logger.info(f"临时文件清理完成: {temp_dir}")
            return True
            
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
            return False 