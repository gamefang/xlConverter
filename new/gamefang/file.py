# -*- coding: utf-8 -*-
# 文件處理模塊

import os
import inspect

def get_file_list(folder, list_exts, is_recur = False):
    '''
    按後綴獲取文件列表，可選擇是否遞歸
    '''
    list_files = []
    if is_recur:
        for root, _, files in os.walk(folder):
            for f in files:
                if os.path.splitext(f)[1][1:] in list_exts:
                    list_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            if os.path.splitext(f)[1][1:] in list_exts:
                list_files.append(os.path.join(folder, f))
    return list_files

def get_abspath(relative_path, cur_path = None):
    '''
    獲取絶對路徑
    ''' 
    if (os.path.isabs(relative_path)): return relative_path
    if cur_path is None:
        frame = inspect.stack()[1]
        caller_file = frame.filename
        cur_path = os.path.dirname(os.path.abspath(caller_file))
    else:
        cur_path = os.path.abspath(cur_path)
    full_path = os.path.join(cur_path, relative_path)
    return os.path.abspath(full_path)

def get_folder(path):
    '''
    獲取文件夾
    '''
    return os.path.dirname(path)

def path_join(*paths):
    '''
    路徑拼接
    '''
    paths = [item for item in paths if item]
    return os.path.join(*paths)

def get_file_name(path):
    '''
    獲取文件名
    '''
    return os.path.basename(path)