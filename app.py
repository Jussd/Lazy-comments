#!/usr/bin/env python3
"""Entry point that works around PyInstaller name-collision."""

import os
import sys

# Force the script's directory onto sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now run the original entry script
import runpy
runpy.run_path(os.path.join(os.path.dirname(__file__), "lazy_comments.py"), run_name="__main__")

