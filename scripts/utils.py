import os
import shutil
import sys

def get_path(str):
    main = sys.modules.get('__main__')
    if main is not None and hasattr(main, "__file__"):
        root = os.path.dirname(os.path.abspath(main.__file__))
    else:
        root = os.getcwd()
    return str.replace("$rootDir", root).replace("$pwd", os.getcwd())

def copy_into(src, dest):
    src_path = get_path(src)
    dest_path = get_path(dest)
    shutil.copy(src_path, dest_path)