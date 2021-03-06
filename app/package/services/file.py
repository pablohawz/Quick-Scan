"""Set of utils for the creation and management of files.
"""

import os
import numpy as np
from . import file as fileutils


def save_np_to_txt(data: np.ndarray, path: str, file_name="data.txt"):
    """Save a NumPy ndarray to disk.

    It creates the folder if it does not exists and then writes it using
    NumPy's functions.

    Args:
        data (np.ndarray): the data to save
        path (str): the path to the file
        file_name (str, optional): The name of the file.
            Defaults to "data.txt".
    """

    fileutils.mkdir(path)
    file_path = os.path.join(path, file_name)
    np.savetxt(file_path, data)


def check_for_existance(path) -> tuple:
    """Checks for existance of a file or a dir

    If it is a dir => True. If not => check for file and return that.

    Args:
        path (str): Path to the desired file or dir

    Returns:
        bool: Whether it exist or not
        bool: if it is a file or not (it is a dir)
    """

    isdir = os.path.isdir(path)
    if isdir:
        return True, False

    isfile = os.path.isfile(path)
    if isfile:
        return True, True

    return False, None


def check_for_empty(path: str) -> bool:
    """Check if a Directory is empty and also check exceptional situations.
    """

    if os.path.exists(path) and os.path.isdir(path):
        if os.listdir(path):
            return False
    return True


def mkdir(path):
    exists, _ = check_for_existance(path)

    try:
        if not exists:
            os.makedirs(path)
            return True, ''
        else:
            return True, ''
    except Exception as e:
        return False, str(e)
