# -*- coding: utf-8 -*-
# 主要處理流程

# 本地模塊
from gamefang.setting import SettingData
from gamefang.file import *
import gamefang.misc as misc
import excel

# region 數據加載
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
# endregion

# region 數據清洗
# 各數據類型的清洗方法，數據名需要和setting中對應
DIC_TYPE_PARSE_METHOD = {
    'int' : misc.to_int,
    'float' : misc.to_float,
    'bool' : misc.to_bool,
    'str' : misc.to_str,
    'intlist' : misc.to_list_int,
    'floatlist' : misc.to_list_float,
    'boollist' : misc.to_list_bool,
    'strlist' : misc.to_list_str,
    'dict' : misc.to_dict,
}

def _data_clean(raw_data, setting_data):
    '''
    清洗數據，返回：
    ```python
    {
        '表名1' : {
            'is_using' : [True, True, False...]},   # 各原始列是否在使用
            'content' : [
                ['int', 'str', 'bool'...],  # 首行數據類型
                ['key', 'name', 'pickable'...], # 二行變量名
                [1, '蘋果', True...],   # 三行起實際數據
                [2, '香蕉', False...],
                ...
            ],
            'raw_data' : {...}, # 未清洗的原始數據
        },
        '表名2' : {...},
        ...
    }
    ```
    '''
    result = {}
    note_signs = tuple(setting_data.get('note_signs'))
    for conf_name, datadic in raw_data.items():
        this_conf_dic = {}
        raw_value_list = datadic['raw_value_list']
        # 確定列是否使用
        row = raw_value_list[1]   # 第二行為字段名稱
        if row[0] != 'key': # 字段名應以key起始
            print(f'warning: {conf_name} is not start with key param!')
        is_using = [not item.startswith(note_signs) for item in row]
        this_conf_dic['is_using'] = is_using    # 是否使用數據（含註釋列），保存至數據
        list_param_name = [item for num,item in enumerate(raw_value_list[1]) if is_using[num]]   # 實際表頭（不含註釋列）
        # 確定各列數據類型
        row = raw_value_list[0]   # 第一行為數據類型
        all_list_type = [__confirm_type(item, setting_data) for item in row]    # 類型列表（含註釋列）
        list_type = [item for num,item in enumerate(all_list_type) if is_using[num]]    # 實際類型（不含註釋列）
        # 確定默認值
        row = raw_value_list[2] # 第三行可以是默認值
        if str(row[0]) == '0':
            default_values = [__parse_type(item, all_list_type[num]) for num,item in enumerate(row)]    # 默認值（含註釋列）
        else:
            default_values = []
        # 遍歷內容
        this_conf_dic['content'] = []
        this_conf_dic['content'].append(list_type)  # 添加類型
        this_conf_dic['content'].append(list_param_name)    # 添加表頭
        start_row = (2,3)[len(default_values) != 0]
        for row_num, row in enumerate(datadic['raw_value_list'][start_row:]):
            if str(row[0]).startswith(note_signs): continue  # 行註釋
            row_content = []
            for col_num,item in enumerate(row):
                if not is_using[col_num]: continue  # 列註釋
                if item is None and default_values:    # 為空且設置了默認值，則賦予默認值
                    result_item = default_values[col_num]
                else:   # 否則轉化類型
                    result_item = __parse_type(item, all_list_type[col_num])
                row_content.append(result_item)
            this_conf_dic['content'].append(row_content)
        result[conf_name] = this_conf_dic
        result[conf_name]['raw_data'] = datadic # 同時存儲未清洗數據
    return result

def __confirm_type(value, setting_data):
    '''
    確定數據類型，返回類型的字符串
    '''
    for type_str in DIC_TYPE_PARSE_METHOD.keys():
        name_list = setting_data.get(f'{type_str}_name')
        if value in name_list:
            return type_str

def __parse_type(value, type_str):
    '''
    根據類型轉化數據
    '''
    if type_str not in DIC_TYPE_PARSE_METHOD.keys():
        return None
    method = DIC_TYPE_PARSE_METHOD[type_str]
    return method(value)
# endregion


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
    all_raw_xl_data = _get_raw_xl_data(setting_data)
    if not all_raw_xl_data: return
    # 數據清洗
    all_xl_data = _data_clean(all_raw_xl_data, setting_data)
    print(all_xl_data)
    return
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