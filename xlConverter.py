# -*- coding: utf-8 -*-
# python3.7+

version='1.4.0'
__author__='gamefang'

CFG_FILE_PATH='xlConverter.ini'

__doc__='''
INI配置文件说明
    配置文件可调整部分功能，需要严格遵循json格式。
    @xl_dir: Excel文件的存放目录，会自动搜寻目录下所有Excel文件。路径分隔符必须用“/”！
    @json_dir: 输出json文件的目录。路径分隔符必须用“/”！
    @recursive_xl_files: 是否采用递归形式搜索Excel文件目录。
    @output_in_one: 如果为false或0，则分别输出json文件，文件名为Excel对应sheet名；
                    如果为字符串，则输出至一个文件，例如填写config.json，则将所有Excel文件内容输出至该文件中。
    @file_exts: 搜寻的Excel文件後缀。另外默认以'~$','__'开头的excel文件不会被搜寻。
    @sheet_name_prefix: Excel文件中，加此前缀的sheet会被导出，可支持多个。前缀只允许一个字符。
    @bound_tag: Excel一个sheet中配置的边界符号，只有边界内的配置内容才会被导出。
    @note_signs: Excel配置中单行、单列注释的前缀，被注释则不会被导出。
    @allow_inner_note: 是否允许Excel配置中使用内容注释（可能导致字段不统一）。    
    @var_type_pre: Excel配置中字段名前缀字符串，用以区分数据类型，需严格按照以下顺序：
        0-python的int，对应json中的数字num；
        1-python的float，对应json中的数字num；
        2-python的string，对应json中的字符串string；
        3-借用python的tuple，对应json中的全字符串数组（自动补全双引号）;
        4-python的list，对应json中的普通数组array（全数字或数串混合自补双引号）；
        5-python的dict，对应json中的对象object（自补双引号）；
        6-python的boolean，对应json中的布尔值bool；
        暂不包括json中的null类型。
    @keep_var_type: 是否在json的key中保留字段名前缀。
    @read_me_mode: 是否查看说明。
Excel文件格式说明
    1.[工作簿]需要导出的所有Excel文件必须放在配置文件夹中。
    2.[工作表]需要导出的sheet页前需加前缀，如分开导出则json文件名为前缀後的sheet名。
    3.[导出区域]需要导出的区域要用边界符号框住，位置为右上和左下。
    4.[字段名称]右上边界符号所在行必须为表头，第一个字符表示字段的数据类型，详见@var_type_pre说明。
    5.[数据规范]同列Excel数据需要遵循字段的数据类型，否则会产生错误。
        数字：Excel所见即所得；
        字符串：无需添加两侧""；
        数组：无需添加两侧[]，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        对象：无需添加两侧{}，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        布尔值：Excel所见即所得。
        不导出数据：由note_signs开头的数据不被导出，需要打开allow_inner_note开关。
'''

import cfgLoader
import xlLoader
import dataConverter
import jsonParser
import mdParser
    
def show_readme():
    '''
    show doc.
    '''
    try:
        import win32api
        import win32con
        win32api.MessageBox(win32con.NULL,__doc__,'xlConverter by %s' % __author__,win32con.MB_OK)
    except:
        print(__doc__)
        
def main():
    #加载配置
    cfg=cfgLoader.get_cfg(CFG_FILE_PATH)
    if cfg['read_me_mode']:show_readme()
    #excel原始数据导入
    raw_data=xlLoader.get_data(cfg['xlloader'])
    print(raw_data)
    # input_files=file_list(cfg['xl_dir'],cfg['file_exts'],cfg['recursive_xl_files'])
    # raw_data={}
    # for fn in input_files:  #文件循环
        # global FILENAME
        # FILENAME=fn
        # raw_data.update(workbook_handle(fn,cfg))
    #数据转化
    #data=dataConverter.get_data(cfg['dataConverter'])
    #输出
    # if cfg['output_in_one']:
        # fn=os.path.join(cfg['json_dir'],cfg['output_in_one'])
        # json_output(fn,data)
    # else:
        # for k,v in data.items():
            # fn=os.path.join(cfg['json_dir'],'%s.json' % k)
            # json_output(fn,v)

if __name__ == '__main__':
    main()
