# -*- coding: utf-8 -*-
# 主要處理流程

# 本地模塊
import gamefang.setx as setx
import gamefang.filex as filex
import gamefang.miscx as miscx
import gamefang.excelx as excelx

# region 數據加載
def _get_raw_xl_data(set_data):
    '''
    加載所有excel基本數據
    '''
    # 獲取全部excel文件名列表
    target_folder = filex.path_join(set_data.folder, set_data.get('xl_dir'))
    excel_files = __excel_file_list(target_folder, set_data.get('file_exts'), set_data.get('recursive_xl_files'))
    if not excel_files:
        print('no excel file found!')
        return
    # 獲取excel內容字典
    result = {}
    for fn in excel_files:
        result.update(__workbook_data_load(fn, set_data))
    return result

def __workbook_data_load(fn, set_data):
    '''
    excel工作簿數據加載
    '''
    wb = excelx.get_workbook(fn)
    result = {}
    for name in wb.sheetnames:
        if name.startswith(set_data.get('sheet_name_prefix')):
            real_name = name[len(set_data.get('sheet_name_prefix')):]
            raw_value_list = excelx.get_sheet_range_value_list(wb[name], set_data.get('bound_tag'))
            result[real_name] = {
                'file_path' : fn,   # 來源excel文件路徑
                'raw_value_list' : raw_value_list,  # 選定區域原始值二維列表
            }
    return result

def __excel_file_list(folder, list_exts, is_recur = False):
    '''
    獲取Excel文件列表
    '''
    list_file = filex.get_file_list(folder, list_exts, is_recur)
    return [file for file in list_file if not filex.get_file_name(file).startswith(('~$','__'))]
# endregion

# region 數據清洗及轉化
# 各數據類型的清洗方法，數據名需要和setting中對應
DIC_TYPE_PARSE_METHOD = {
    'int' : miscx.to_int,
    'float' : miscx.to_float,
    'bool' : miscx.to_bool,
    'str' : miscx.to_str,
    'intlist' : miscx.to_list_int,
    'floatlist' : miscx.to_list_float,
    'boollist' : miscx.to_list_bool,
    'strlist' : miscx.to_list_str,
    'dict' : miscx.to_dict,
    'dictlist' : miscx.to_list_dict,
}

def _data_clean(raw_data, set_data):
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
    note_signs = tuple(set_data.get('note_signs'))
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
        all_list_type = [__confirm_type(item, set_data) for item in row]    # 類型列表（含註釋列）
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

def __confirm_type(value, set_data):
    '''
    確定數據類型，返回類型的字符串
    '''
    for type_str in DIC_TYPE_PARSE_METHOD.keys():
        name_list = set_data.get(f'{type_str}_name')
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

def _data_convert(origin_data, base_data_style):
    '''
    數據格式轉化
    '''
    match base_data_style:
        case 0: # 二維列表 [['key','hp'...],[1,30...],[2,50...]...]
            return origin_data
        case 1: # 條目字典列表 [{'key':1,'hp':30...},{'key':2,'hp':50...}...]
            return __to_row_dict_list(origin_data)
        case 2: # key嵌套字典 {1:{'hp':30...},2:{'hp':50...}...}
            return __to_key_nested_dict(origin_data)
    return origin_data

def __to_row_dict_list(origin_data):
    '''
    from: [['key','hp'...],[1,30...],[2,50...]...]
    to: [{'key':1,'hp':30...},{'key':2,'hp':50...}...]
    '''
    result=[]
    list_param_name = origin_data[0]
    for row_list in origin_data[1:]:
        subdic = {}
        for i in range(0, len(row_list)):
            param_name = list_param_name[i]
            subdic[param_name] = row_list[i]
        result.append(subdic)
    return result

def __to_key_nested_dict(origin_data):
    '''
    from: [['key','hp'...],[1,30...],[2,50...]...]
    to: {1:{'hp':30...},2:{'hp':50...}...}
    '''
    result = {}
    list_param_name = origin_data[0]
    for row_list in origin_data[1:]:
        key = row_list[0]
        subdic = {}
        for i in range(1, len(row_list)):
            param_name = list_param_name[i]
            subdic[param_name] = row_list[i]
        result[key] = subdic
    return result
# endregion

# region 數據輸出
def _data_output(all_xl_data, set_data):
    '''
    數據按要求輸出
    '''
    # pickle存儲
    if set_data.get('cache_data'):
        import pickle
        cache_fp = filex.path_join(set_data.folder, set_data.get('cache_dir'))
        with open(cache_fp, 'wb') as file:
            pickle.dump(all_xl_data, file)
        # with open(cache_fp, 'rb') as file:
        #     unpacked_data = pickle.load(file)
        #     print(unpacked_data)    # 測試查看最終數據
    # 文件輸出
    output_template = set_data.get('output_template')
    dic_converted_data = {key: value['converted_data'] for key, value in all_xl_data.items()}
    match output_template:
        case 'csv': # 支持二維列表、多文件
            if set_data.get('base_data_style') != 0:
                print('[base_data_style] must be [0] when [output_template] is [csv]!')
                return
            import csv
            for conf_name, converted_data in dic_converted_data.items():
                output_fp = filex.path_join(set_data.folder, set_data.get('output_dir'), f'{conf_name}.{set_data.get("output_ext")}')
                with open(output_fp, 'w', encoding='utf-8') as file:
                    writer = csv.writer(file, lineterminator='\n')
                    writer.writerows(converted_data)
                print(f'<{output_fp}> Done!')
        case 'json':    # 支持任意類型
            import json
            if set_data.get('output_in_one'):
                output_fp = filex.path_join(set_data.folder, set_data.get('output_dir'), set_data.get('output_in_one_fn'))
                with open(output_fp, 'w', encoding='utf-8') as file:
                    jsonstr = json.dumps(dic_converted_data)
                    file.write(jsonstr)
                print(f'<{output_fp}> Done!')
            else:
                for conf_name, converted_data in dic_converted_data.items():
                    output_fp = filex.path_join(set_data.folder, set_data.get('output_dir'), f'{conf_name}.{set_data.get("output_ext")}')
                    with open(output_fp, 'w', encoding='utf-8') as file:
                        jsonstr = json.dumps(dic_converted_data[conf_name])
                        file.write(jsonstr)
                    print(f'<{output_fp}> Done!')
        case 'unity':
            pass
        case 'godot':   # 支持嵌套字典、單文件
            output_fp = filex.path_join(set_data.folder, set_data.get('output_dir'), set_data.get('output_in_one_fn'))
            import output_template.godot as godot
            godot.output_in_one(dic_converted_data, output_fp,
                header=set_data.get('output_file_header') or '', tail=set_data.get('output_file_tail') or '')
# endregion

def main(set_fp):
    '''
    主流程
    '''
    # 加載設置
    set_fp = filex.get_abspath(set_fp)
    set_data = setx.SettingData(set_fp)
    set_data.fp = set_fp
    set_data.folder = filex.get_folder(set_fp)
    print(f'setting loaded: {set_fp}')
    # 加載excel基本數據
    all_raw_xl_data = _get_raw_xl_data(set_data)
    if not all_raw_xl_data: return
    # 數據清洗及轉化
    all_xl_data = _data_clean(all_raw_xl_data, set_data)
    for k,v in all_xl_data.items():
        using_origin_data = v['content'][1:]    # 去掉第一行的數據類型再進行轉換
        converted_data = _data_convert(using_origin_data, set_data.get('base_data_style'))
        all_xl_data[k]['converted_data'] = converted_data
    # 選擇模板輸出
    _data_output(all_xl_data, set_data)
    # 執行後續任務
    done_scripts = set_data.get('done_scripts')
    if (done_scripts):
        import os
        import sys
        for script in done_scripts:
            fp = filex.path_join(set_data.folder, script)
            sys.stdout.flush()  # 確保按順序執行
            os.system(f'python {fp}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 and sys.argv[0]:  # 直接運行腳本（測試）
        main('../sample/xl_converter.ini')
    else:   # 外部帶參數調用
        # 實際調用，ini應放置在項目固定目録下，sh腳本應指定固定的python文件位置
        import argparse
        parser = argparse.ArgumentParser(description = 'setting')
        parser.add_argument('--fp', type = str, required = True, help = 'the path of setting file')
        args = parser.parse_args()
        main(args.fp)