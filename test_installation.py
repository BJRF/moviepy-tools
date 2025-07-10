#!/usr/bin/env python3
"""
MoviePy Tools 安装测试脚本
检查依赖是否正确安装，系统是否可以正常运行
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """测试Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ❌ 需要Python 3.7或更高版本")
        return False
    else:
        print("   ✅ Python版本满足要求")
        return True

def test_dependencies():
    """测试依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'moviepy',
        'numpy', 
        'PIL',  # Pillow包导入时使用PIL
        'pydub',
        'pysrt',
        'tqdm',
        'colorama',
        'yaml'  # PyYAML包导入时使用yaml
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("   ✅ 所有依赖包都已安装")
        return True

def test_ffmpeg():
    """测试FFmpeg"""
    print("\n🎬 检查FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            return True
        else:
            print("   ❌ FFmpeg命令执行失败")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg命令超时")
        return False
    except FileNotFoundError:
        print("   ❌ FFmpeg未安装或未添加到PATH")
        print("   安装方法:")
        print("     macOS: brew install ffmpeg")
        print("     Ubuntu: sudo apt install ffmpeg")
        print("     Windows: 下载FFmpeg并添加到PATH")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = [
        'core',
        'utils', 
        'examples',
        'input',
        'output',
        'output/temp',
        'output/logs'
    ]
    
    required_files = [
        'config.py',
        'main.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'core/__init__.py',
        'core/video_processor.py',
        'core/audio_processor.py',
        'core/subtitle_processor.py',
        'core/batch_processor.py',
        'utils/__init__.py',
        'utils/file_utils.py',
        'utils/time_utils.py',
        'utils/format_utils.py'
    ]
    
    missing_items = []
    
    # 检查目录
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"   ✅ {directory}/")
        else:
            print(f"   ❌ {directory}/ (缺失)")
            missing_items.append(directory)
    
    # 检查文件
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (缺失)")
            missing_items.append(file_path)
    
    if missing_items:
        print(f"\n⚠️  缺少项目文件: {len(missing_items)} 个")
        return False
    else:
        print("   ✅ 项目结构完整")
        return True

def test_imports():
    """测试模块导入"""
    print("\n🔧 测试模块导入...")
    
    test_modules = [
        ('config', 'PROJECT_ROOT, VIDEO_CONFIG'),
        ('core.video_processor', 'VideoProcessor'),
        ('core.audio_processor', 'AudioProcessor'), 
        ('core.subtitle_processor', 'SubtitleProcessor'),
        ('core.batch_processor', 'BatchProcessor'),
        ('utils.file_utils', 'ensure_output_dir'),
        ('utils.time_utils', 'parse_time_string'),
        ('utils.format_utils', 'get_video_info')
    ]
    
    import_errors = []
    
    for module_name, items in test_modules:
        try:
            exec(f"from {module_name} import {items}")
            print(f"   ✅ {module_name}")
        except Exception as e:
            print(f"   ❌ {module_name} - {str(e)}")
            import_errors.append(module_name)
    
    if import_errors:
        print(f"\n⚠️  模块导入失败: {len(import_errors)} 个")
        return False
    else:
        print("   ✅ 所有模块导入成功")
        return True

def test_basic_functionality():
    """测试基础功能"""
    print("\n⚙️ 测试基础功能...")
    
    try:
        # 测试时间解析
        from utils.time_utils import parse_time_string
        time_result = parse_time_string("00:01:30")
        assert time_result == 90.0
        print("   ✅ 时间解析功能")
        
        # 测试文件工具
        from utils.file_utils import ensure_output_dir
        test_dir = Path("output/test")
        ensure_output_dir(test_dir / "test.txt")
        assert test_dir.exists()
        print("   ✅ 文件操作功能")
        
        # 测试配置加载
        from config import VIDEO_CONFIG, get_quality_preset
        preset = get_quality_preset("medium")
        assert isinstance(preset, dict)
        print("   ✅ 配置管理功能")
        
        print("   ✅ 基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"   ❌ 基础功能测试失败: {e}")
        return False

def generate_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 测试报告")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"总测试项: {total_tests}")
    print(f"通过: {passed_tests} ✅")
    print(f"失败: {failed_tests} ❌")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 恭喜！所有测试都通过了！")
        print("MoviePy Tools 已准备就绪，可以开始使用了！")
        print("\n📖 下一步:")
        print("1. 查看 QUICKSTART.md 了解使用方法")
        print("2. 运行示例脚本: python3 examples/basic_video_editing.py")
        print("3. 将视频文件放在 input/ 目录中开始处理")
    else:
        print("\n⚠️ 部分测试失败，请解决上述问题后重新运行测试")
        print("如需帮助，请查看 QUICKSTART.md 中的常见问题部分")
    
    return failed_tests == 0

def main():
    """主函数"""
    print("🔍 MoviePy Tools 安装测试")
    print("="*60)
    
    # 运行所有测试
    tests = {
        "Python版本": test_python_version(),
        "依赖包": test_dependencies(),
        "FFmpeg": test_ffmpeg(),
        "项目结构": test_project_structure(),
        "模块导入": test_imports(),
        "基础功能": test_basic_functionality()
    }
    
    # 生成报告
    success = generate_report(tests)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 