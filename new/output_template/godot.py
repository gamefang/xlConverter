# -*- coding: utf-8 -*-
# godot配置輸出

import gamefang.filex as filex

def output_in_one(dic_converted_data, output_fp):
    '''
    輸出配置文件至一個文件中
    '''
    result = ''
    result += '''class_name RawData
extends Object

'''
    for conf_name, converted_data in dic_converted_data.items():
        result += f'static var {conf_name} = {converted_data}\n'
    result.replace('True', 'true')
    result.replace('False', 'false')
    filex.write_to_file(result[:-1], output_fp)
    print(f'<{output_fp}> Done!')