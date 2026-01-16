"""
Some utils functions
"""
import os
import shutil
import sys
import pandas as pd

def get_path(path:str):
    """
    Get the path from template for given string.
        - Replace `$root` by the execution path (directory of __main__)
        - Replace `$pwd` by current execution directory

    :param path: Template path to be updated
    """
    main = sys.modules.get('__main__')
    if main is not None and hasattr(main, "__file__"):
        root = os.path.dirname(os.path.abspath(main.__file__))
    else:
        root = os.getcwd()
    return path.replace("$rootDir", root).replace("$pwd", os.getcwd())

def copy_into(src, dest):
    """
    Copy file into directory

    :param src: Template path of file to be copied
    :param dest: Path to its destination
    """
    src_path = get_path(src)
    dest_path = get_path(dest)
    shutil.copy(src_path, dest_path)

def create_unexisting_dir(path:str):
    """
    Create a directory on disk, if it does not exist

    :param path: Path to the directory to be created
    :type path: str
    """
    if not os.path.exists(path):
        os.makedirs(path)

def export_df(df:pd.DataFrame, output_dir:str, name:str):
    """
    Save a dataframe as a CSV file.

    :param df: Dataframe to be saved
    :type df: pd.DataFrame
    :param output_dir: Path to directory
    :type output_dir: str
    :param name: Name of the CSV file
    :type name: str
    """
    dest_path = os.path.join(output_dir, name)
    df.to_csv(dest_path, index=False)
