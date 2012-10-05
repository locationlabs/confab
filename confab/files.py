"""
File options.
"""

import os
import shutil

def _clear_dir(dir_name):
    """
    Remove an entire directory tree.
    """
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)

def _clear_file(file_name):
    """
    Remove an entire directory tree.
    """
    if os.path.exists(file_name):
        os.remove(file_name)

def _ensure_dir(dir_name):
    """
    Ensure that a directory exists.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
