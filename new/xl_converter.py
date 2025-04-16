# -*- coding: utf-8 -*-
# 主要處理流程

# 本地模塊
from gamefang.setting import SettingData
from gamefang.file import *
import excel

def _get_raw_xl_data(setting_data):
    '''
    加載所有excel基本數據
    '''
    # 獲取全部excel文件名列表
    target_folder = path_join(setting_data.folder, setting_data.get('xl_dir'))
    excel_files = __excel_file_list(target_folder, setting_data.get('file_exts'), setting_data.get('recursive_xl_files'))
    if not excel_files:
        print('no excel file found!')
        return
    # 獲取excel內容字典
    result = {}
    for fn in excel_files:
        result.update(__workbook_data_load(fn, setting_data))
    return result

def __workbook_data_load(fn, setting_data):
    '''
    excel工作簿數據加載
    '''
    wb = excel.get_workbook(fn)
    result = {}
    for name in wb.sheetnames:
        if name.startswith(setting_data.get('sheet_name_prefix')):
            real_name = name[len(setting_data.get('sheet_name_prefix')):]
            raw_value_list = excel.get_sheet_range_value_list(wb[name], setting_data.get('bound_tag'))
            result[real_name] = {
                'file_path' : fn,   # 來源excel文件路徑
                'raw_value_list' : raw_value_list,  # 選定區域原始值二維列表
            }
    return result

def __excel_file_list(folder, list_exts, is_recur = False):
    '''
    獲取Excel文件列表
    '''
    list_file = get_file_list(folder, list_exts, is_recur)
    return [file for file in list_file if not get_file_name(file).startswith(('~$','__'))]

def main(setting_fp):
    '''
    主流程
    '''
    # 加載設置
    setting_fp = get_abspath(setting_fp)
    setting_data = SettingData(setting_fp)
    setting_data.fp = setting_fp
    setting_data.folder = get_folder(setting_fp)
    print(f'setting loaded: {setting_fp}')
    # 加載excel基本數據
    all_xl_data = _get_raw_xl_data(setting_data)
    print(all_xl_data)
    if not all_xl_data: return
    return
    # 處理數據 1. 去掉註釋行、列 2. 數據類型轉化 3. 根據配置處理默認值 4. pickle緩存數據，供外部調用
    # 輸出數據，根據配置輸出為json、csv等
    # 基於緩存數據的額外代碼生成，指定相關的處理文件路徑并執行

if __name__ == '__main__':
    main('xl_converter.ini')
    # 實際調用，ini應放置在項目固定目録下，sh腳本應指定固定的python文件位置
    # import argparse
    # parser = argparse.ArgumentParser(description = 'setting')
    # parser.add_argument('--fp', type = str, required = True, help = 'the path of setting file')
    # args = parser.parse_args()
    # main(args.fp)