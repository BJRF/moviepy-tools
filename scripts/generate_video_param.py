# 在这里，您可以通过 'args'  获取节点中的输入变量，并通过 'ret' 输出结果
# 'args' 已经被正确地注入到环境中
# 下面是一个示例，首先获取节点的全部输入参数params，其次获取其中参数名为'input'的值：
# params = args.params; 
# input = params['input'];
# 下面是一个示例，输出一个包含多种数据类型的 'ret' 对象：
# ret: Dict[str, Any] =  { "name": '小明', "hobbies": ["看书", "旅游"] };

import json
import re
import math
from typing import List, Dict, Any, Tuple

async def main(args: Any) -> Dict[str, Any]:
    params = args.params
    
    image_list = params.get('image_list', [])
    audio_list = params.get('audio_list', [])
    duration_list = params.get('duration_list', [])
    scenes = params.get('scenes', [])
    
    # 处理音频数据
    audio_data = []
    audio_start_time = 0
    aideoTimelines = []
    max_duration = 0
    
    image_data = []
    
    # 处理音频和图片数据
    for i in range(min(len(audio_list), len(duration_list))):
        duration = duration_list[i]
        audio_data.append({
            'audio_url': audio_list[i],
            'duration': duration,
            'start': audio_start_time,
            'end': audio_start_time + duration
        })
        aideoTimelines.append({
            'start': audio_start_time,
            'end': audio_start_time + duration
        })
        
        # 处理图片数据，根据索引决定是否添加动画
        if (i - 1) % 2 == 0:
            image_data.append({
                'image_url': image_list[i],
                'start': audio_start_time,
                'end': audio_start_time + duration,
                'width': 1440,
                'height': 1080,
                'in_animation': "轻微放大",
                'in_animation_duration': 100000
            })
        else:
            image_data.append({
                'image_url': image_list[i],
                'start': audio_start_time,
                'end': audio_start_time + duration,
                'width': 1440,
                'height': 1080
            })
        
        audio_start_time += duration
        max_duration = audio_start_time
    
    # 处理角色图片数据
    role_img_data = []
    if params.get('role_img_url') and duration_list:
        role_img_data.append({
            'image_url': params.get('role_img_url'),
            'start': 0,
            'end': duration_list[0],
            'width': 1440,
            'height': 1080
        })
    
    # 处理字幕
    captions = [item.get('cap', '') for item in scenes]
    subtitle_durations = duration_list
    
    text_timelines, processed_subtitles = process_subtitles(
        captions,
        subtitle_durations
    )
    
    # 处理标题
    title = params.get('title', '')
    title_list = [title]
    title_timelines = [
        {
            'start': 0,
            'end': duration_list[0] if duration_list else 0
        }
    ]
    
    # 开场音效和背景音乐URL
    kc_audio_url = "https://p9-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/c04e7b48586a48f1863e421be4b10cf1.MP3~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1777550323&x-signature=T%2BNjvPHPyHnGICvWRFDeFaj17UM%3D&x-wf-file_name=%E6%95%85%E4%BA%8B%E5%BC%80%E5%9C%BA%E9%9F%B3%E6%95%88.MP3"
    bg_audio_url = "https://p3-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/5603dc783a6c4b75a4bf4e1b44086ad5.MP3~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1777550332&x-signature=E1123RzPTMD%2BipseRN4itYxhZyc%3D&x-wf-file_name=%E6%95%85%E4%BA%8B%E8%83%8C%E6%99%AF%E9%9F%B3%E4%B9%90.MP3"
    
    # 背景音乐数据
    bg_audio_data = []
    bg_audio_data.append({
        'audio_url': bg_audio_url,
        'duration': max_duration,  # 注意：原代码中是 'duraion'，这里修正为 'duration'
        'start': 0,
        'end': max_duration
    })
    
    # 开场音效数据
    kc_audio_data = []
    kc_audio_data.append({
        'audio_url': kc_audio_url,
        'duration': 4884897,
        'start': 0,
        'end': 4884897
    })
    
    # 构建输出对象
    ret_data = {
        'audioData': json.dumps(audio_data, ensure_ascii=False),
        'bgAudioData': json.dumps(bg_audio_data, ensure_ascii=False),
        'kcAudioData': json.dumps(kc_audio_data, ensure_ascii=False),
        'imageData': json.dumps(image_data, ensure_ascii=False),
        'text_timielines': text_timelines,
        'text_captions': processed_subtitles,
        'title_list': title_list,
        'title_timelimes': title_timelines,
        'roleImgData': json.dumps(role_img_data, ensure_ascii=False)
    }
    
    # 先生成包含所有内容的字符串
    all_content_str = json.dumps(ret_data, ensure_ascii=False, indent=2)
    
    # 最终构建输出对象
    ret: Dict[str, Any] = {
        **ret_data,
        'all_content': all_content_str
    }
    
    return ret


# 字幕配置
SUB_CONFIG = {
    'MAX_LINE_LENGTH': 25,
    'SPLIT_PRIORITY': ['。', '！', '？', '，', ',', '：', ':', '、', '；', ';', ' '],
    'TIME_PRECISION': 3
}


def split_long_phrase(text: str, max_len: int) -> List[str]:
    """
    分割长文本为多个短语
    """
    if len(text) <= max_len:
        return [text]
    
    # 严格在max_len范围内查找分隔符
    for delimiter in SUB_CONFIG['SPLIT_PRIORITY']:
        pos = text.rfind(delimiter, 0, max_len)  # 限制查找范围
        if pos > 0:
            split_pos = pos + 1
            return [
                text[:split_pos].strip(),
                *split_long_phrase(text[split_pos:].strip(), max_len)
            ]
    
    # 汉字边界检查防止越界
    start_pos = min(max_len, len(text)) - 1
    for i in range(start_pos, 0, -1):
        if re.match(r'[\u4e00-\u9fff]', text[i]):  # 汉字Unicode范围
            return [
                text[:i + 1].strip(),
                *split_long_phrase(text[i + 1:].strip(), max_len)
            ]
    
    # 强制分割时保证不超过max_len
    split_pos = min(max_len, len(text))
    return [
        text[:split_pos].strip(),
        *split_long_phrase(text[split_pos:].strip(), max_len)
    ]


def process_subtitles(
    captions: List[str],
    subtitle_durations: List[int],
    start_time_us: int = 0
) -> Tuple[List[Dict[str, int]], List[str]]:
    """
    处理字幕数据
    
    Args:
        captions: 字幕文本列表
        subtitle_durations: 字幕持续时间列表（微秒）
        start_time_us: 起始时间（微秒，默认0）
    
    Returns:
        tuple: (时间轴列表, 处理后的字幕列表)
    """
    # 清理正则表达式
    clean_regex = re.compile(r'[\u3000\u3002-\u303F\uff00-\uffef\u2000-\u206F!"#$%&\'()*+\-./<=>?@\\^_`{|}~]')
    
    processed_subtitles = []
    processed_subtitle_durations = []
    
    for index, text in enumerate(captions):
        if index >= len(subtitle_durations):
            break
            
        total_duration = subtitle_durations[index]
        phrases = split_long_phrase(text, SUB_CONFIG['MAX_LINE_LENGTH'])
        
        # 清理标点符号
        phrases = [clean_regex.sub('', p).strip() for p in phrases]
        phrases = [p for p in phrases if len(p) > 0]
        
        if not phrases:
            processed_subtitles.append('[无内容]')
            processed_subtitle_durations.append(total_duration)
            continue
        
        # 时间分配逻辑
        total_chars = sum(len(p) for p in phrases)
        accumulated_us = 0
        
        for i, phrase in enumerate(phrases):
            ratio = len(phrase) / total_chars
            if i == len(phrases) - 1:
                # 最后一段用剩余时间
                duration_us = total_duration - accumulated_us
            else:
                duration_us = round(total_duration * ratio)
            
            processed_subtitles.append(phrase)
            processed_subtitle_durations.append(duration_us)
            accumulated_us += duration_us
    
    # 时间轴生成（从指定起始时间开始）
    text_timelines = []
    current_time = start_time_us
    
    for duration_us in processed_subtitle_durations:
        start = current_time
        end = start + duration_us
        
        text_timelines.append({
            'start': start,
            'end': end
        })
        
        current_time = end
    
    return text_timelines, processed_subtitles


 