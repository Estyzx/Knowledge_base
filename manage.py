#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # 尝试加载.env文件中的环境变量
    env_path = Path(__file__).resolve().parent / '.env'
    if (env_path.exists()):
        print("找到.env配置文件，加载环境变量...")
        try:
            # 明确指定使用UTF-8编码打开文件
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        except Exception as e:
            print(f"加载.env文件出错: {str(e)}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowledge_base.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
