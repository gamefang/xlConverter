# -*- coding: utf-8 -*-
#不能完美支持python2。
#2018/8/24 实现excel策划配置文件批量导出为json。
#2018/8/30 添加全字符串数组类型，类型前缀可配置。
#2018/10/10 添加只有一列自动导出为列表的功能
#2018/11/6 添加内容注释功能，可选择性屏蔽部分key的部分字段

version='1.3.1'

CONF_FILE='xl2json_conf.json'   #配置文件路径

__doc__='''
配置文件说明(%s)
    配置文件可调整部分功能，需要严格遵循json格式。
    @xl_dir: Excel文件的存放目录，会自动搜寻目录下所有Excel文件。
    @json_dir: 输出json文件的目录。
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
''' % CONF_FILE

__author__='gamefang'

import xlrd

import os
import json
import codecs

import argparse

parser = argparse.ArgumentParser(description='generate json from xlsx.')
parser.add_argument('--style', type=int, default=0, required=False,
                    help='output style')
args = parser.parse_args()

def file_list(sDir,tExt,bRecursive=False):
    '''
    Get custom filelist in some direction.
    @param sDir: the full direction to handle.
    @param tExt: a tuple of file extensions.
    @param bRecursive: search files recursive.
    @return: list of filenames.
    '''
    lFiles=[]
    if bRecursive:
        for root, dirs, files in os.walk(sDir):
            for f in files:
                if f.startswith( ('~$','__') ):continue    #2017/11/20 避免加入隐藏文件 2018/4/23 双下划线文件不导出
                if os.path.splitext(f)[1][1:] in tExt:
                    lFiles.append(os.path.join(root,f))
    else:
        for f in os.listdir(sDir):
            if f.startswith( ('~$','__') ):continue    #2017/11/20 避免加入隐藏文件 2018/4/23 双下划线文件不导出
            if os.path.splitext(f)[1][1:] in tExt:
                lFiles.append(os.path.join(sDir,f))
    return lFiles

def workbook_handle(fn,cfg):
    '''
    处理某一个excel文件。
    @param fn: excel文件完整路径。
    @param cfg: 全局配置对象。
    @return: 整个工作簿的数据。
    '''
    wb=xlrd.open_workbook(fn)
    datas={}
    for sn in wb.sheet_names(): #sheet循环
        global SHEETNAME
        SHEETNAME=sn
        if sn.startswith(cfg['sheet_name_prefix']):  #是否需导出检测
            sheet=wb.sheet_by_name(sn)
        else:
            continue
        datas[sn]=worksheet_handle(sheet,cfg)
    return datas

def worksheet_handle(sheet,cfg):
    '''
    处理一个excel工作表。
    @param sheet: sheet对象
    @param cfg: 全局配置对象。
    @return: 工作表的数据。
    '''
    bounds=get_sheet_bounds(sheet,cfg)
    this_data=[]
    note_cols=[]
    note_rows=[]
    types={}
    for r in range(bounds[1][0],bounds[0][0]):
        global ROW
        ROW=r
        if r in note_rows:continue   #跳过注释行
        this_row=[]
        for c in range(bounds[0][1],bounds[1][1]):
            global COLUMN
            COLUMN=c
            if c in note_cols:continue   #跳过注释列
            v=str(sheet.cell(r,c).value)    #获取字符串形式原始数据
            if v.lstrip().startswith( tuple(cfg['note_signs']) ):  #注释排查（裁剪左端空字符）
                if r==bounds[1][0]: #列注释
                    note_cols.append(c)
                    continue   #下一列
                elif c==bounds[0][1]:   #行注释
                    note_rows.append(r)
                    break   #跳出列循环，开始下一行
                else:  #内容注释
                    if not bool(cfg['allow_inner_note']):
                        raise Exception("<FILE>%s <SHEET>%s <ROW>%s <COLUMN>%s:Inner Note not allowed!" % (FILENAME,SHEETNAME,ROW+1,COLUMN+1) )
            else:
                if r==bounds[1][0]: #第一行存储类型信息
                    types[c]=get_type_pre(v,cfg)
                    cv=v
                else:
                    cv=clean_cell_data(sheet.cell(r,c),types[c])    #Cell对象数据清洗并保存为实际类型
                    if cv==None:print("<FILE>%s <SHEET>%s <ROW>%s <COLUMN>%s:Value Error!" % (FILENAME,SHEETNAME,ROW+1,COLUMN+1) )
                this_row.append(cv)
        if this_row:
            this_data.append(this_row)
    return this_data   #装入公用数据字典

def get_sheet_bounds(sheet,cfg):
    '''
    获取一个工作表的有效边界。
    @param sheet: sheet对象
    @param cfg: 全局配置对象。
    @return: [[左下边界r,左下边界c],[右上边界r,右上边界c]]。
    '''
    #Row/Column循环
    bounds=[]
    for c in range(sheet.ncols):    #遍历row、column，找出值为"#"的单元格2个，记录rc坐标。保持先row标再col标
        for r in range(sheet.nrows):
            if sheet.cell(r,c).value==cfg['bound_tag']:
                bounds.append([r,c])
    if len(bounds)!=2 or \
       bounds[0][0]==bounds[1][0] or \
       bounds[0][1]==bounds[1][1]:  #标记!=2个 or 标记坐标的rc有一样的，返回错误。
        raise Exception("<FILE>%s <SHEET>%s:bound tags error!\nNeed exactly 2 tags,and can't be in the same row or column!" % (FILENAME,SHEETNAME))
    else:   #标记正常，开始遍历取值
        return bounds
        
def get_type_pre(val,cfg):
    '''
    获取表头字段中含有的数据类型信息。
    @param val: 字段名字符串。
    @param cfg: 全局配置对象。
    @return: 数值型类型值：
        0-int
        1-float
        2-string
        3-tuple(string array in json)
        4-list
        5-dict
        6-boolean
    '''
    if val.lower()=='key':return 2    #json的key必须是string
    for i,pre in enumerate(cfg['var_type_pre']):
        if val.startswith(pre):return i
    return 2    #特殊情况均视为str

def clean_cell_data(cell,type_value):
    '''
    Get a python type variable,from Excel-Cell-Object in xlrd.
    Need RE.
    @param cell: cell object in xlrd.
    @param type_value: the value of type:
        0-int
        1-float
        2-string
        3-tuple(string array in json)
        4-list
        5-dict
        6-boolean
    @return: exact type of data.
    '''
    t=cell.ctype
    if t==0 or not cell.value:    #空，或Excel中残留的'型单元格等情况
        if type_value==2 and cell.ctype:    #2018/9/11需求字符串且填写数字0用作键的情况
            return clean_string(cell)
        return {
            0:0,    #int
            1:0.0,  #float
            2:'',   #str
            3:[],   #string array
            4:[],   #normal array
            5:{},   #object
            6:False,    #bool
            }.get(type_value,str(cell.value))
    elif t in [1,2]:    #文本和数字，特殊处理
        return clean_dic[type_value](cell)
    elif t==4:  #Excel中的TRUE和FALSE
        if type_value==6:
            return bool(cell.value)  #TRUE实际等于1.0
        print('###WARNING!NOT A BOOL! cell.value:{self.value},cell.ctype:{self.ctype}'.format(self=cell))
        return str(cell.value)
    else:   #其余异常情况
        print('###WARNING!ERROR! cell.value:{self.value},cell.ctype:{self.ctype}'.format(self=cell))
        return str(cell.value)
        
#Excel中对ctype2,3的特殊处理
def clean_int(cell):    
    return int(cell.value)
def clean_float(cell):
    return float(cell.value)
def clean_string(cell):
    if cell.ctype==1:
        return str(cell.value)
    return str(int(cell.value))
def clean_strarray(cell):
    return str(cell.value).split(',')
def clean_array(cell):
    if cell.ctype==1:
        return eval( '[%s,]' % str(cell.value) )
    return eval( '[%s,]' % int(cell.value) )
def clean_object(cell):
    if cell.ctype==1:
        return eval( '{%s,}' % str(cell.value) )
    return eval( '{%s,}' % int(cell.value) )    
def clean_bool(cell):
    if cell.ctype==1:
        return str(cell.value) in ('True','TRUE','true','t','T','1')
    return bool(cell.value)
clean_dic={
        0:clean_int,
        1:clean_float,
        2:clean_string,
        3:clean_strarray,
        4:clean_array,
        5:clean_object,
        6:clean_bool,
        }

def convertion_default(oridata,cfg,**kw):
    '''
    From:
    [['sId', 'sName', 'sTip', 'iFulfill_value'],
     ['test', '成就', '一个测试成就', 100],
     ['testhide', '隐藏成就', '又一个测试成就', 100]]
    To:
    {'test': {'Name': '成就', 'Tip': '一个测试成就', 'Fulfill_value': 100},
     'testhide': {'Name': '隐藏成就', 'Tip': '又一个测试成就', 'Fulfill_value': 100}}
    Or:
    From:
    [['skey'],
     ['a'],
     ['b'],
     ['c']]
    To:
    ['a','b','c']
    @param oridata: original 2-dimensional list.
    @param cfg: global config object.
    @return: a copy of new styled data.
    '''
    if len(oridata[0])==1:  #如果只有一列，自动导出成列表
        return [
                oridata[i][0]
                for i in range(1,len(oridata))
                ]    
    listdata=oridata.copy()
    result={}
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(1,len(item)):
            if bool(cfg['allow_inner_note']) and \
                isinstance(item[i],str) and \
                item[i].startswith( tuple(cfg['note_signs']) ):
                    continue  #自定义不输出某key的某些字段
            if cfg['keep_var_type']:
                subdic[ pro_names[i] ]=item[i]
            else:
                pre_len=len(cfg['var_type_pre'][get_type_pre(pro_names[i],cfg)])
                subdic[ pro_names[i][pre_len:] ]=item[i]
        result[ item[0] ]=subdic
    return result
    
def convertion_1(oridata,cfg,**kw):
    '''
    From:
    [
        ['sKey','iParam1','iParam2'],
        ['1',10,20],
        ['2',15,25],
        ['3',25,35]
    ]
    To:
    [
        {
          "Key":"1",
          "Param1": 10,
          "Param2": 20
        },
        {
          "Key":"2", 
          "Param1": 15,
          "Param2": 25
        },
        {
          "Key":"3",
          "Param1": 25,
          "Param2": 35
        }
    ]
    Or:
    From:
    [['skey'],
     ['a'],
     ['b'],
     ['c']]
    To:
    ['a','b','c']
    @param oridata: original 2-dimensional list.
    @param cfg: global config object.
    @return: a copy of new styled result.
    '''
    if len(oridata[0])==1:  #如果只有一列，自动导出成列表
        return [
                oridata[i][0]
                for i in range(1,len(oridata))
                ]
    listdata=oridata.copy()
    result=[]
    if kw['begin_with_null']:result=[None]    #特殊的补null情况(RMMV)
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(0,len(item)):
            if bool(cfg['allow_inner_note']) and \
                isinstance(item[i],str) and \
                item[i].startswith( tuple(cfg['note_signs']) ):
                    continue  #自定义不输出某key的某些字段        
            if cfg['keep_var_type']:
                subdic[ pro_names[i] ]=item[i]
            else:
                pre_len=len(cfg['var_type_pre'][get_type_pre(pro_names[i],cfg)])
                subdic[ pro_names[i][pre_len:] ]=item[i]
        result.append(subdic)
    return result  
    
def json_output(fn,data):
    '''
    output json file.
    @param fn: full file path.
    @param data: json data.
    '''
    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        jsonstr=json.dumps(data,ensure_ascii=False,indent=2)
        jsonstr=jsonstr.replace(r'\\n',r'\n')   #2018/9/6 解决转义字符多次转义错误
        f.write(jsonstr)
    print('<%s> Done!' % fn)

def show_readme():
    '''
    show doc.
    '''
    try:
        import win32api
        import win32con
        win32api.MessageBox(win32con.NULL,__doc__,'xl2json by %s' % __author__,win32con.MB_OK)
    except:
        print(__doc__)
    
def main(style=0):
    #载入配置
    with open(CONF_FILE) as json_file:
        cfg=json.load(json_file)
    if cfg['read_me_mode']:show_readme()
    #从Excel文件中输入原始数据，转为python二维列表
    input_files=file_list(cfg['xl_dir'],cfg['file_exts'],cfg['recursive_xl_files'])
    raw_data={}
    for fn in input_files:  #文件循环
        global FILENAME
        FILENAME=fn
        raw_data.update(workbook_handle(fn,cfg))
    #python原始数据转化处理
    if not style:
        data={
            k[1:]:convertion_default(v,cfg)
            for k,v in raw_data.items()
            }
    elif style==1:
        data={
            k[1:]:convertion_1(v,cfg,begin_with_null=True)
            for k,v in raw_data.items()
            }
    else:
        print('style not existed!')
    #输出为json
    if cfg['output_in_one']:
        fn=os.path.join(cfg['json_dir'],cfg['output_in_one'])
        json_output(fn,data)
    else:
        for k,v in data.items():
            fn=os.path.join(cfg['json_dir'],'%s.json' % k)
            json_output(fn,v)

if __name__ == '__main__':
    main(args.style)
