"""
MoviePy Tools 全局配置文件
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 输入输出目录配置
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = OUTPUT_DIR / "temp"
LOG_DIR = OUTPUT_DIR / "logs"

# 视频处理配置
VIDEO_CONFIG = {
    "default_format": "mp4",
    "default_codec": "libx264",
    "default_audio_codec": "aac",
    "default_fps": 30,
    "default_quality": "medium",  # low, medium, high, ultra
    "default_resolution": (1920, 1080),
    "compression_crf": 23,  # 0-51, 越小质量越好
}

# 音频处理配置
AUDIO_CONFIG = {
    "default_format": "mp3",
    "default_bitrate": "192k",
    "default_sample_rate": 44100,
    "default_channels": 2,
    "volume_normalize": True,
}

# 字幕配置
SUBTITLE_CONFIG = {
    "default_format": "srt",
    "default_font": "Arial",
    "default_font_size": 24,
    "default_color": "white",
    "default_position": ("center", "bottom"),
    "default_encoding": "utf-8",
}

# 批量处理配置
BATCH_CONFIG = {
    "max_workers": 4,  # 并行处理的最大线程数
    "chunk_size": 10,  # 每批处理的文件数
    "progress_bar": True,
    "auto_cleanup": True,  # 自动清理临时文件
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_enabled": True,
    "console_enabled": True,
}

# 质量预设
QUALITY_PRESETS = {
    "low": {
        "crf": 28,
        "resolution": (854, 480),
        "fps": 24,
        "audio_bitrate": "128k",
    },
    "medium": {
        "crf": 23,
        "resolution": (1280, 720),
        "fps": 30,
        "audio_bitrate": "192k",
    },
    "high": {
        "crf": 18,
        "resolution": (1920, 1080),
        "fps": 30,
        "audio_bitrate": "256k",
    },
    "ultra": {
        "crf": 15,
        "resolution": (3840, 2160),
        "fps": 60,
        "audio_bitrate": "320k",
    },
}

# 文件扩展名映射
SUPPORTED_FORMATS = {
    "video": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "subtitle": [".srt", ".ass", ".vtt", ".sub"],
    "image": [".jpg", ".jpeg", ".png", ".bmp", ".gif"],
}

# 创建必要的目录
def create_directories():
    """创建项目必要的目录结构"""
    directories = [
        INPUT_DIR / "videos",
        INPUT_DIR / "audios", 
        INPUT_DIR / "subtitles",
        OUTPUT_DIR / "processed",
        TEMP_DIR,
        LOG_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
        # 创建 .gitkeep 文件以保持目录结构
        gitkeep_file = directory / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()

# 获取质量预设
def get_quality_preset(quality_name):
    """获取指定质量的预设配置"""
    return QUALITY_PRESETS.get(quality_name, QUALITY_PRESETS["medium"])

# 验证文件格式
def is_supported_format(file_path, format_type):
    """检查文件格式是否受支持"""
    if format_type not in SUPPORTED_FORMATS:
        return False
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in SUPPORTED_FORMATS[format_type]

# 设置日志
def setup_logging(level=None):
    """设置日志配置
    
    Args:
        level: 日志级别
    """
    import logging
    import sys
    from pathlib import Path
    
    # 设置日志级别
    if level is None:
        level = getattr(logging, LOG_CONFIG["level"])
    
    # 创建根日志器
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter(LOG_CONFIG["format"])
    
    # 控制台处理器
    if LOG_CONFIG["console_enabled"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if LOG_CONFIG["file_enabled"]:
        log_file = LOG_DIR / "moviepy_tools.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

# 初始化配置
if __name__ == "__main__":
    create_directories()
    print("✅ 项目目录结构已创建完成！") 