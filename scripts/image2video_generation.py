#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片转视频生成器
基于xiajiqushi.json数据格式，按顺序生成图片镜头并配上声音
"""

import json
import os
import requests
import tempfile
from moviepy import *
import urllib.parse
from typing import Dict, List, Any, Optional
import time
import sys
import argparse

class Image2VideoGenerator:
    def __init__(self, output_dir: str = "output/video"):
        self.output_dir = output_dir
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
        
        # 视频参数
        self.video_size = (1440, 1080)
        self.fps = 24
        
    def download_file(self, url: str, filename: str) -> Optional[str]:
        """下载文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ 已下载: {filename}")
            return file_path
        except Exception as e:
            print(f"❌ 下载失败 {filename}: {e}")
            return None
    
    def create_image_clip_with_animation(self, image_path: str, start_time: float, 
                                       duration: float, animation_type: str = "轻微放大"):
        """创建带动画效果的图片片段"""
        try:
            # 创建图片片段
            img_clip = ImageClip(image_path)
            img_clip = img_clip.with_duration(duration).with_start(start_time)
            
            # 调整大小以适应视频尺寸
            img_clip = img_clip.resized(self.video_size)
            
            # 添加动画效果
            if animation_type == "轻微放大":
                # 使用resize创建缩放动画
                def resize_func(t):
                    return 1.0 + (t / duration) * 0.08  # 轻微放大8%
                img_clip = img_clip.resized(resize_func)
            elif animation_type == "淡入淡出":
                # 添加透明度变化效果（简化版本）
                img_clip = img_clip.with_opacity(0.8)
            elif animation_type == "左右移动":
                # 保持居中位置
                img_clip = img_clip.with_position('center')
            
            return img_clip
            
        except Exception as e:
            print(f"❌ 创建图片片段失败: {e}")
            return None
    
    def extract_voice_url(self, voice_data: Dict[str, Any]) -> Optional[str]:
        """从voice数据中提取音频URL"""
        try:
            if voice_data.get('code') == 0 and 'data' in voice_data:
                return voice_data['data'].get('link')
            return None
        except Exception as e:
            print(f"❌ 提取音频URL失败: {e}")
            return None
    
    def generate_video(self, json_data: Dict[str, Any], output_filename: str = "image2video.mp4"):
        """生成视频"""
        try:
            print("🎬 开始生成图片转视频...")
            
            # 解析JSON数据
            images = json_data.get('image', [])
            voices = json_data.get('voice', [])
            voice_durations = json_data.get('voiceDurationList', [])
            
            print(f"📊 视频信息:")
            print(f"   🖼️  图片数量: {len(images)}")
            print(f"   🎵 音频数量: {len(voices)}")
            print(f"   ⏱️  音频时长数据: {len(voice_durations)}")
            
            # 确保数据一致性
            min_count = min(len(images), len(voices), len(voice_durations))
            if min_count == 0:
                print("❌ 没有足够的数据来生成视频")
                return None
                
            print(f"   📝 将生成 {min_count} 个镜头")
            
            # 计算总时长
            total_duration = sum(duration_info.get('duration', 0) for duration_info in voice_durations[:min_count])
            print(f"   ⏱️  总时长: {total_duration:.1f} 秒 ({total_duration / 60:.1f} 分钟)")
            
            # 创建视频片段列表
            video_clips = []
            audio_clips = []
            
            current_time = 0.0
            
            # 按顺序处理每个镜头
            for i in range(min_count):
                print(f"\n🎬 处理第 {i+1} 个镜头...")
                
                # 获取当前镜头的数据
                image_url = images[i]
                voice_data = voices[i]
                duration_info = voice_durations[i]
                
                # 获取音频时长
                clip_duration = duration_info.get('duration', 7.0)
                
                print(f"   📸 图片: {image_url}")
                print(f"   🎵 音频时长: {clip_duration:.1f}s")
                print(f"   ⏰ 开始时间: {current_time:.1f}s")
                
                # 1. 下载并处理图片
                image_filename = f"image_{i+1}.jpg"
                image_path = self.download_file(image_url, image_filename)
                
                if image_path:
                    # 创建图片片段
                    animation_types = ["轻微放大", "淡入淡出", "左右移动"]
                    animation_type = animation_types[i % len(animation_types)]
                    
                    img_clip = self.create_image_clip_with_animation(
                        image_path, current_time, clip_duration, animation_type
                    )
                    
                    if img_clip:
                        video_clips.append(img_clip)
                        print(f"   ✅ 图片片段创建成功 (动画: {animation_type})")
                    else:
                        print(f"   ❌ 图片片段创建失败")
                
                # 2. 下载并处理音频
                voice_url = self.extract_voice_url(voice_data)
                if voice_url:
                    audio_filename = f"voice_{i+1}.mp3"
                    audio_path = self.download_file(voice_url, audio_filename)
                    
                    if audio_path:
                        try:
                            audio_clip = AudioFileClip(audio_path)
                            # 设置音频开始时间
                            audio_clip = audio_clip.with_start(current_time)
                            # 确保音频时长不超过预期
                            if audio_clip.duration > clip_duration:
                                audio_clip = audio_clip.subclipped(0, clip_duration)
                            audio_clips.append(audio_clip)
                            print(f"   ✅ 音频片段创建成功")
                        except Exception as e:
                            print(f"   ❌ 音频处理失败: {e}")
                else:
                    print(f"   ❌ 无法提取音频URL")
                
                # 更新时间
                current_time += clip_duration
            
            # 合成视频
            print(f"\n🎬 开始合成视频...")
            print(f"   📹 视频片段数: {len(video_clips)}")
            print(f"   🎵 音频片段数: {len(audio_clips)}")
            
            if video_clips:
                # 合并所有视频片段
                final_video = CompositeVideoClip(video_clips, size=self.video_size)
                final_video = final_video.with_duration(total_duration)
                
                # 合并音频
                if audio_clips:
                    final_audio = CompositeAudioClip(audio_clips)
                    final_audio = final_audio.with_duration(total_duration)
                    final_video = final_video.with_audio(final_audio)
                    print("   ✅ 音频合成完成")
                else:
                    print("   ⚠️  没有音频，生成静音视频")
                
                # 输出视频
                output_path = os.path.join(self.output_dir, output_filename)
                
                print(f"💾 正在保存视频: {output_path}")
                
                final_video.write_videofile(
                    output_path,
                    fps=self.fps,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                print(f"✅ 视频生成完成: {output_path}")
                
                # 显示文件信息
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"📦 文件大小: {file_size / 1024 / 1024:.1f} MB")
                
                # 清理资源
                final_video.close()
                for clip in video_clips + audio_clips:
                    if hasattr(clip, 'close'):
                        clip.close()
                
                return output_path
            else:
                print("❌ 没有有效的视频片段")
                return None
                
        except Exception as e:
            print(f"❌ 生成视频时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print("🧹 临时文件已清理")
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {e}")

def load_json_data(file_path: str) -> Optional[Dict[str, Any]]:
    """加载JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功加载JSON数据: {file_path}")
        return data
        
    except Exception as e:
        print(f"❌ 加载JSON数据失败: {e}")
        return None

def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='根据图片和音频JSON配置生成视频')
    parser.add_argument('json_file', nargs='?', default='xiajiqushi.json', 
                       help='JSON配置文件路径 (默认: xiajiqushi.json)')
    parser.add_argument('-o', '--output', default=None,
                       help='输出目录 (默认: output/video)')
    
    args = parser.parse_args()
    
    # 获取JSON文件路径
    json_file_path = args.json_file
    
    # 如果路径不是绝对路径，则相对于当前脚本目录
    if not os.path.isabs(json_file_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, json_file_path)
    
    # 设置输出目录
    if args.output:
        output_dir = args.output
    else:
        # 项目根目录的输出路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, "output", "video")
    
    print("🎬 图片转视频生成器")
    print("=" * 50)
    print(f"📁 数据文件: {json_file_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 找不到JSON文件: {json_file_path}")
        print("💡 使用方法:")
        print("   python image2video_generation.py")
        print("   python image2video_generation.py xiajiqushi.json")
        print("   python image2video_generation.py /path/to/your/config.json")
        return
    
    # 加载JSON数据
    json_data = load_json_data(json_file_path)
    if not json_data:
        return
    
    # 创建视频生成器
    generator = Image2VideoGenerator(output_dir)
    
    try:
        # 生成输出文件名
        timestamp = time.strftime("%Y%m%d_%H%M")
        json_filename = os.path.splitext(os.path.basename(json_file_path))[0]
        output_filename = f"{json_filename}_{timestamp}.mp4"
        
        print(f"\n🚀 开始生成视频...")
        result = generator.generate_video(json_data, output_filename)
        
        if result:
            print(f"\n🎉 视频生成成功！")
            print(f"📁 输出文件: {result}")
        else:
            print("❌ 视频生成失败")
            
    except Exception as e:
        print(f"❌ 生成过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()
        