#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复版视频生成器
解决时长和字幕问题
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

class VideoGeneratorFixed:
    def __init__(self, output_dir: str = "output/video"):
        self.output_dir = output_dir
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(output_dir, exist_ok=True)
    
    def download_file(self, url: str, filename: str) -> Optional[str]:
        """下载文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"已下载: {filename}")
            return file_path
        except Exception as e:
            print(f"下载失败 {filename}: {e}")
            return None
    
    def microseconds_to_seconds(self, microseconds: int) -> float:
        """将微秒转换为秒"""
        return microseconds / 1000000.0
    
    def create_subtitle_clip(self, text: str, start_time: float, end_time: float, 
                           video_size: tuple = (1440, 1080)):
        """创建字幕片段"""
        duration = end_time - start_time
        
        # 创建文本片段 - 使用正确的API
        txt_clip = TextClip(
            text=text, 
            font_size=48, 
            color='white', 
            stroke_color='black',
            stroke_width=3,
            font='Arial Unicode'
        )
        
        # 设置时间和位置 - 调整位置确保字幕完全显示
        txt_clip = txt_clip.with_duration(duration).with_start(start_time)
        
        # 计算字幕的合适位置，确保字幕底部距离视频底部90像素
        # 字幕大小约为字体大小 + 描边宽度的1.5倍
        estimated_text_height = int(txt_clip.size[1]) if txt_clip.size[1] else 60
        bottom_margin = 90  # 距离底部90像素
        subtitle_y_position = video_size[1] - bottom_margin - estimated_text_height
        
        # 确保字幕不会超出视频顶部
        subtitle_y_position = max(subtitle_y_position, 20)
        
        txt_clip = txt_clip.with_position(('center', subtitle_y_position))
        
        return txt_clip
    
    def create_image_clip_with_animation(self, image_path: str, start_time: float, 
                                       end_time: float, animation_type: Optional[str] = None,
                                       video_size: tuple = (1440, 1080)):
        """创建带动画效果的图片片段"""
        duration = end_time - start_time
        
        # 创建图片片段
        img_clip = ImageClip(image_path)
        img_clip = img_clip.with_duration(duration).with_start(start_time)
        
        # 调整大小以适应视频尺寸
        img_clip = img_clip.resized(video_size)
        
        # 添加动画效果
        if animation_type == "轻微放大":
            # 使用resize创建缩放动画
            img_clip = img_clip.resized(lambda t: 1.0 + (t / duration) * 0.05)
        
        return img_clip
    
    def generate_video(self, video_data: Dict[str, Any], output_filename: str = "generated_video.mp4"):
        """生成视频"""
        try:
            # 解析JSON数据
            audio_data = json.loads(video_data['audioData'])
            image_data = json.loads(video_data['imageData'])
            text_timelines = video_data['text_timielines']
            text_captions = video_data['text_captions']
            bg_audio_data = json.loads(video_data['bgAudioData'])
            kc_audio_data = json.loads(video_data['kcAudioData'])
            
            # 计算正确的总时长 - 从最后一个音频片段的结束时间获取
            last_audio = audio_data[-1] if audio_data else None
            total_duration = self.microseconds_to_seconds(last_audio['end']) if last_audio else 60.0
            
            print("开始生成视频...")
            print(f"预期总时长: {total_duration:.2f}秒")
            
            # 下载音频文件
            audio_clips = []
            for i, audio_info in enumerate(audio_data):
                audio_url = audio_info['audio_url']
                start_time = self.microseconds_to_seconds(audio_info['start'])
                
                # 下载音频文件
                audio_filename = f"audio_{i}.mp3"
                audio_path = self.download_file(audio_url, audio_filename)
                
                if audio_path:
                    audio_clip = AudioFileClip(audio_path)
                    audio_clip = audio_clip.with_start(start_time)
                    audio_clips.append(audio_clip)
            
            # 下载图片文件并创建视频片段
            video_clips = []
            for i, img_info in enumerate(image_data):
                img_url = img_info['image_url']
                start_time = self.microseconds_to_seconds(img_info['start'])
                end_time = self.microseconds_to_seconds(img_info['end'])
                animation_type = img_info.get('in_animation')
                
                # 下载图片文件
                img_filename = f"image_{i}.jpg"
                img_path = self.download_file(img_url, img_filename)
                
                if img_path:
                    img_clip = self.create_image_clip_with_animation(
                        img_path, start_time, end_time, animation_type
                    )
                    video_clips.append(img_clip)
            
            # 创建字幕片段
            subtitle_clips = []
            print(f"创建 {len(text_captions)} 个字幕片段...")
            for i, (timeline, caption) in enumerate(zip(text_timelines, text_captions)):
                start_time = self.microseconds_to_seconds(timeline['start'])
                end_time = self.microseconds_to_seconds(timeline['end'])
                
                if start_time < total_duration:  # 只创建在总时长内的字幕
                    end_time = min(end_time, total_duration)  # 确保不超过总时长
                    subtitle_clip = self.create_subtitle_clip(caption, start_time, end_time)
                    subtitle_clips.append(subtitle_clip)
            
            # 下载背景音乐
            bg_audio_clips = []
            for bg_audio_info in bg_audio_data:
                bg_url = bg_audio_info['audio_url']
                bg_filename = "bg_music.mp3"
                bg_path = self.download_file(bg_url, bg_filename)
                
                if bg_path:
                    bg_clip = AudioFileClip(bg_path)
                    bg_clip = bg_clip.with_volume_scaled(0.3)  # 降低背景音乐音量
                    # 确保背景音乐不超过总时长
                    bg_clip = bg_clip.with_duration(total_duration)
                    bg_audio_clips.append(bg_clip)
            
            # 下载开场音效
            kc_audio_clips = []
            for kc_audio_info in kc_audio_data:
                kc_url = kc_audio_info['audio_url']
                kc_filename = "opening_sound.mp3"
                kc_path = self.download_file(kc_url, kc_filename)
                
                if kc_path:
                    kc_clip = AudioFileClip(kc_path)
                    kc_clip = kc_clip.with_volume_scaled(0.5)  # 适中音量
                    kc_audio_clips.append(kc_clip)
            
            print("开始合成视频...")
            
            # 合成视频
            if video_clips:
                # 合并所有视频片段和字幕
                all_clips = video_clips + subtitle_clips
                final_video = CompositeVideoClip(all_clips, size=(1440, 1080))
                
                # 强制设置正确的时长
                final_video = final_video.subclipped(0, total_duration)
                
                # 合并音频
                all_audio_clips = audio_clips + bg_audio_clips + kc_audio_clips
                if all_audio_clips:
                    final_audio = CompositeAudioClip(all_audio_clips)
                    # 确保音频时长不超过视频时长
                    final_audio = final_audio.subclipped(0, total_duration)
                    final_video = final_video.with_audio(final_audio)
                
                # 输出视频
                output_path = os.path.join(self.output_dir, output_filename)
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                print(f"视频生成完成: {output_path}")
                
                # 清理临时文件
                final_video.close()
                for clip in audio_clips + video_clips + subtitle_clips + bg_audio_clips + kc_audio_clips:
                    clip.close()
                
                return output_path
            else:
                print("没有有效的视频片段")
                return None
                
        except Exception as e:
            print(f"生成视频时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print("临时文件已清理")
        except:
            pass

def load_video_data_from_file(file_path: str) -> Optional[Dict[str, Any]]:
    """从文件加载视频数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理转义字符
        # 如果文件包含转义的换行符，先处理它们
        if '\\n' in content:
            content = content.replace('\\n', '\n')
        
        # 如果文件包含转义的引号，处理它们
        if '\\"' in content:
            # 这是一个更复杂的情况，需要先解析外层JSON，再处理内层的转义字符串
            try:
                # 尝试直接解析
                video_data = json.loads(content)
            except json.JSONDecodeError:
                # 如果失败，尝试使用ast.literal_eval处理一些转义字符
                import ast
                try:
                    # 先尝试将转义字符串转换为正常字符串
                    content = ast.literal_eval(f'"{content}"')
                    video_data = json.loads(content)
                except:
                    raise ValueError("无法解析JSON格式")
        else:
            # 正常解析JSON
            video_data = json.loads(content)
        
        # 确保必要的字段存在
        required_fields = ['audioData', 'imageData', 'text_timielines', 'text_captions', 'bgAudioData', 'kcAudioData']
        for field in required_fields:
            if field not in video_data:
                print(f"警告: 缺少必要字段 {field}")
                video_data[field] = "[]" if field.endswith('Data') else []
        
        # 添加默认字段
        if 'title_list' not in video_data:
            video_data['title_list'] = ["默认标题"]
        if 'title_timelimes' not in video_data:
            video_data['title_timelimes'] = [{"start": 0, "end": 4000000}]
        if 'roleImgData' not in video_data:
            video_data['roleImgData'] = "[]"
        if 'all_content' not in video_data:
            video_data['all_content'] = None
        
        return video_data
        
    except Exception as e:
        print(f"❌ 加载视频数据失败: {e}")
        return None

def main():
    """主函数，从命令行参数指定的JSON文件读取数据并生成视频"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='根据JSON配置文件生成视频')
    parser.add_argument('json_file', nargs='?', default='test.json', 
                       help='JSON配置文件路径 (默认: test.json)')
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
    
    print("🎬 开始从JSON文件生成视频...")
    print(f"📁 数据文件: {json_file_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 找不到JSON文件: {json_file_path}")
        print("💡 使用方法:")
        print("   python video_generator.py [JSON文件路径]")
        print("   python video_generator.py test.json")
        print("   python video_generator.py /path/to/your/config.json")
        return
    
    # 加载视频数据
    video_data = load_video_data_from_file(json_file_path)
    if not video_data:
        print("❌ 加载视频数据失败")
        return
    
    # 解析音频数据获取视频信息
    try:
        audio_data = json.loads(video_data['audioData'])
        image_data = json.loads(video_data['imageData'])
        
        # 计算总时长
        total_duration_microseconds = audio_data[-1]['end'] if audio_data else 60000000
        total_duration_seconds = total_duration_microseconds / 1000000.0
        
        print(f"📊 视频信息:")
        print(f"   ⏱️  总时长: {total_duration_seconds:.1f} 秒 ({total_duration_seconds / 60:.1f} 分钟)")
        print(f"   🎵 音频片段数: {len(audio_data)}")
        print(f"   🖼️  图片片段数: {len(image_data)}")
        print(f"   💬 字幕片段数: {len(video_data['text_captions'])}")
        
        # 获取视频主题
        title = video_data.get('title_list', ['未知主题'])[0]
        print(f"   📝 视频主题: {title}")
        
    except Exception as e:
        print(f"⚠️  解析视频信息时出错: {e}")
    
    # 创建视频生成器
    generator = VideoGeneratorFixed(output_dir)
    
    try:
        # 生成可读性强的分钟级日期时间格式
        timestamp = time.strftime("%Y%m%d_%H%M")
        
        # 从JSON文件名生成输出文件名
        json_filename = os.path.splitext(os.path.basename(json_file_path))[0]
        output_filename = f"{json_filename}_{timestamp}.mp4"
        
        print(f"\n🚀 开始生成视频...")
        result = generator.generate_video(video_data, output_filename)
        
        if result:
            print(f"\n✅ 视频生成成功！")
            print(f"📁 输出文件: {result}")
            
            # 显示文件信息
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"📦 文件大小: {file_size / 1024 / 1024:.1f} MB")
            
            print(f"\n🎉 视频已保存")
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