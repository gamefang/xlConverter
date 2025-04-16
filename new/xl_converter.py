# -*- coding: utf-8 -*-
# 主要處理流程

import argparse
# 本地模塊
from setting import SettingData

def get_all_xl_data():
    '''
    加載所有excel數據
    '''
    pass

def convert_to(raw_data, rule):
    '''
    excel數據按規則轉化
    '''
    pass

def output(data):
    '''
    數據輸出
    '''
    pass

def main(setting_fp):
    '''
    主流程
    '''
    setting_data = SettingData(setting_fp)
    print(f'setting loaded: {setting_fp}')
    # print(setting_data.get('convert_style'))
    
    return
    raw_data = get_all_xl_data()
    use_data = convert_to(raw_data)
    output(use_data)

if __name__ == '__main__':
    # main('xlConverter.ini')
    # 實際調用，ini應放置在項目固定目録下，sh腳本應指定固定的python文件位置
    parser = argparse.ArgumentParser(description = 'setting')
    parser.add_argument('--fp', type = str, required = True, help = 'the path of setting file')
    args = parser.parse_args()
    main(args.fp)