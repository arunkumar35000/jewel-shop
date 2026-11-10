#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewellery_shop.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # Auto-detect local virtualenv or system Python37 with Django installed
        base_dir = Path(__file__).resolve().parent
        venv_py = base_dir / "venv" / "Scripts" / "python.exe"
        py37_py = Path(r"C:\Users\ASUS\AppData\Local\Programs\Python\Python37\python.exe")

        candidate = None
        if venv_py.exists():
            candidate = venv_py
        elif py37_py.exists():
            candidate = py37_py

        if candidate and Path(sys.executable).resolve() != candidate.resolve():
            import subprocess
            cmd = [str(candidate)] + sys.argv
            result = subprocess.run(cmd)
            sys.exit(result.returncode)

        # Fallback: add site-packages paths directly
        site_paths = [
            base_dir / "venv" / "Lib" / "site-packages",
            Path(r"C:\Users\ASUS\AppData\Local\Programs\Python\Python37\Lib\site-packages"),
            Path(r"D:\python tutorial\django\jewellery\env\Lib\site-packages"),
        ]
        for sp in site_paths:
            if sp.exists() and str(sp) not in sys.path:
                sys.path.insert(0, str(sp))

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
