# -*- coding: utf-8 -*-
# godot配置輸出

from gamefang.Gfile import gFile

def output_in_one(dic_converted_data : dict, output_fp, header='', tail=''):
    '''
    輸出配置文件至一個文件中
    '''
    result = ''
    result += header.encode().decode('unicode_escape')  # _note 可轉義\n，但中文會亂碼
    for conf_name, converted_data in dic_converted_data.items():
        result += f'static var {conf_name} := {converted_data}\n'
    result += tail.encode().decode('unicode_escape')
    result = result.replace(': True', ': true')
    result = result.replace(': False', ': false')
    result = result.replace(': None', ': null')
    result = result.replace(': [None]', ': []')
    gFile.write_to_file(result, output_fp)
    print(f'Godot File Done! <{output_fp}>')