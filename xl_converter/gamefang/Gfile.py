# -*- coding: utf-8 -*-
# 文件處理模塊

#region import
# std
import os
import inspect
from typing import Container, Iterable
#endregion

class gFile:
    '''文件處理模塊'''
    @staticmethod
    def get_file_list(
            folder: str,
            list_exts: Container[str] | Iterable[str] = (),
            is_recur: bool = False
        ) -> list[str]:
        '''
        按後綴獲取文件列表，可選擇是否遞歸

        :param folder: 要搜索的文件夾路徑
        :param list_exts: 後綴白名單容器，留空則不篩選。示例：('jpg','png')
        :param is_recur: 是否使用遞歸
        :return: 匹配的文件路徑列表
        '''
        list_files = []
        if is_recur:
            for root, _, files in os.walk(folder):
                for f in files:
                    if not list_exts or __class__.get_file_ext(f) in list_exts:
                        list_files.append(__class__.path_join(root, f))
        else:
            for f in os.listdir(folder):
                if not list_exts or __class__.get_file_ext(f) in list_exts:
                    list_files.append(__class__.path_join(folder, f))
        return list_files

    @staticmethod
    def get_abspath(relative_path: str, cur_path: str = '') -> str:
        '''獲取絶對路徑''' 
        if (os.path.isabs(relative_path)): return relative_path
        if cur_path == '':
            frame = inspect.stack()[1]
            caller_file = frame.filename
            cur_path = __class__.get_folder(os.path.abspath(caller_file))
        else:
            cur_path = os.path.abspath(cur_path)
        full_path = __class__.path_join(cur_path, relative_path)
        return os.path.abspath(full_path)

    @staticmethod
    def path_join(*paths) -> str:
        '''路徑拼接'''
        paths = [item for item in paths if item]
        return os.path.join(*paths)

    @staticmethod
    def get_folder(path: str) -> str:
        '''獲取文件夾'''
        return os.path.dirname(path)

    @staticmethod
    def get_file_name(path: str) -> str:
        '''獲取文件名'''
        return os.path.basename(path)

    @staticmethod
    def get_file_ext(path: str) -> str:
        '''獲取後綴名（不包括.）'''
        _, ext = os.path.splitext(path)
        return ext[1:] if ext else ''

    @staticmethod
    def is_file_exists(path: str) -> bool:
        '''路徑是否存在'''
        return os.path.exists(path)
    
    @staticmethod
    def ensure_fp(path: str) -> bool:
        '''檢查文件路徑，如文件夾不存在則自動創建'''
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
            return True
        return False

    @staticmethod
    def write_to_file(content, output_fp: str, auto_md: bool = True) -> None:
        '''
        寫入字符串至文件，文件夾不存在則自動創建
        
        :param content: 寫入的內容字符串
        :param output_fp: 輸出文件路徑
        :param auto_md: 是否自動創建相應路徑
        '''
        output_fullpath = __class__.get_abspath(output_fp)
        if auto_md:
            __class__.ensure_fp(output_fullpath)
        else:
            raise Exception(f'{output_fp} not exist!')
        with open(output_fullpath, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def load_file_str(path: str) -> str:
        '''讀取文件內容為字符串'''
        with open(__class__.get_abspath(path), 'r', encoding='utf-8') as f:
            return f.read()

if __name__ == '__main__':
    # 獲取文件列表
    filelist = gFile.get_file_list(gFile.get_folder(__file__), ['py'], True)
    print(filelist)
    # 獲取絶對路徑
    fullpath = gFile.get_abspath('filex.py')
    print(fullpath)
    # 路徑拼接
    print(gFile.path_join('gamefang', 'filex.py'))
    # 寫入字符串至文件
    gFile.write_to_file(fullpath, gFile.get_abspath('test.txt'))