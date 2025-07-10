"""
文件操作工具函数
"""

import os
import shutil
from pathlib import Path
from typing import List, Union, Optional
import logging

logger = logging.getLogger(__name__)


def ensure_output_dir(file_path: Union[str, Path]) -> None:
    """确保输出文件的目录存在
    
    Args:
        file_path: 文件路径
    """
    path = Path(file_path)
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)


def get_unique_filename(file_path: Union[str, Path]) -> Path:
    """获取唯一的文件名（如果文件已存在，则添加数字后缀）
    
    Args:
        file_path: 原始文件路径
        
    Returns:
        Path: 唯一的文件路径
    """
    path = Path(file_path)
    
    if not path.exists():
        return path
    
    # 分离文件名和扩展名
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    
    # 寻找可用的文件名
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def get_files_by_extension(directory: Union[str, Path], 
                          extensions: List[str],
                          recursive: bool = True) -> List[Path]:
    """根据扩展名获取目录中的文件
    
    Args:
        directory: 目录路径
        extensions: 扩展名列表（如 ['.mp4', '.avi']）
        recursive: 是否递归搜索子目录
        
    Returns:
        List[Path]: 匹配的文件路径列表
    """
    directory = Path(directory)
    
    if not directory.exists():
        logger.warning(f"目录不存在: {directory}")
        return []
    
    files = []
    
    # 标准化扩展名（确保以点开头且小写）
    normalized_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                           for ext in extensions]
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in normalized_extensions:
            files.append(file_path)
    
    # 按文件名排序
    files.sort(key=lambda x: x.name.lower())
    
    logger.info(f"在目录 {directory} 中找到 {len(files)} 个匹配的文件")
    return files


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节）
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        logger.error(f"无法获取文件大小: {file_path}")
        return 0


def copy_file_metadata(source_path: Union[str, Path], 
                      target_path: Union[str, Path]) -> bool:
    """复制文件的元数据（时间戳等）
    
    Args:
        source_path: 源文件路径
        target_path: 目标文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        shutil.copystat(str(source_path), str(target_path))
        logger.debug(f"元数据复制完成: {source_path} -> {target_path}")
        return True
    except Exception as e:
        logger.error(f"复制元数据失败: {e}")
        return False


def move_file(source_path: Union[str, Path], 
              target_path: Union[str, Path],
              overwrite: bool = False) -> bool:
    """移动文件
    
    Args:
        source_path: 源文件路径
        target_path: 目标文件路径
        overwrite: 是否覆盖已存在的文件
        
    Returns:
        bool: 是否成功
    """
    try:
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            logger.error(f"源文件不存在: {source}")
            return False
        
        if target.exists() and not overwrite:
            logger.error(f"目标文件已存在: {target}")
            return False
        
        # 确保目标目录存在
        ensure_output_dir(target)
        
        # 移动文件
        shutil.move(str(source), str(target))
        logger.info(f"文件移动完成: {source} -> {target}")
        return True
        
    except Exception as e:
        logger.error(f"移动文件失败: {e}")
        return False


def copy_file(source_path: Union[str, Path], 
              target_path: Union[str, Path],
              overwrite: bool = False) -> bool:
    """复制文件
    
    Args:
        source_path: 源文件路径
        target_path: 目标文件路径
        overwrite: 是否覆盖已存在的文件
        
    Returns:
        bool: 是否成功
    """
    try:
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            logger.error(f"源文件不存在: {source}")
            return False
        
        if target.exists() and not overwrite:
            logger.error(f"目标文件已存在: {target}")
            return False
        
        # 确保目标目录存在
        ensure_output_dir(target)
        
        # 复制文件
        shutil.copy2(str(source), str(target))
        logger.info(f"文件复制完成: {source} -> {target}")
        return True
        
    except Exception as e:
        logger.error(f"复制文件失败: {e}")
        return False


def delete_file(file_path: Union[str, Path]) -> bool:
    """删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"文件不存在: {path}")
            return True
        
        path.unlink()
        logger.info(f"文件删除完成: {path}")
        return True
        
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        return False


def create_directory_structure(base_dir: Union[str, Path], 
                             structure: dict) -> bool:
    """创建目录结构
    
    Args:
        base_dir: 基础目录
        structure: 目录结构字典
        
    Returns:
        bool: 是否成功
        
    Example:
        structure = {
            "videos": {},
            "audio": {
                "music": {},
                "voice": {}
            },
            "output": {
                "processed": {},
                "temp": {}
            }
        }
    """
    try:
        base_path = Path(base_dir)
        
        def create_dirs(current_path: Path, struct: dict):
            for name, subdirs in struct.items():
                dir_path = current_path / name
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建目录: {dir_path}")
                
                if isinstance(subdirs, dict):
                    create_dirs(dir_path, subdirs)
        
        create_dirs(base_path, structure)
        logger.info(f"目录结构创建完成: {base_path}")
        return True
        
    except Exception as e:
        logger.error(f"创建目录结构失败: {e}")
        return False


def clean_filename(filename: str) -> str:
    """清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 定义非法字符
    illegal_chars = '<>:"/\\|?*'
    
    # 替换非法字符
    clean_name = filename
    for char in illegal_chars:
        clean_name = clean_name.replace(char, '_')
    
    # 移除多余的空格和点
    clean_name = clean_name.strip(' .')
    
    # 确保文件名不为空
    if not clean_name:
        clean_name = "unnamed_file"
    
    return clean_name


def get_directory_size(directory: Union[str, Path]) -> int:
    """获取目录大小（字节）
    
    Args:
        directory: 目录路径
        
    Returns:
        int: 目录大小（字节）
    """
    try:
        total_size = 0
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    except Exception as e:
        logger.error(f"获取目录大小失败: {e}")
        return 0 