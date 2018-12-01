# -*- coding: utf-8 -*-
# python3.7+

import os

import xlrd

FILENAME=None
SHEETNAME=None
ROW=None
COLUMN=None

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
                if f.startswith( ('~$','__') ):continue
                if os.path.splitext(f)[1][1:] in tExt:
                    lFiles.append(os.path.join(root,f))
    else:
        for f in os.listdir(sDir):
            if f.startswith( ('~$','__') ):continue
            if os.path.splitext(f)[1][1:] in tExt:
                lFiles.append(os.path.join(sDir,f))
    return lFiles

def workbook_handle(fn,cfg):
    '''
    处理某一个excel文件。
    @param fn: excel文件完整路径。
    @param cfg: xlloader配置对象。
    @return: 整个工作簿的数据。
    '''
    wb=xlrd.open_workbook(fn)
    datas={}
    for sn in wb.sheet_names(): #sheet循环
        SHEETNAME=sn
        if sn.startswith(cfg.sheet_name_prefix):  #是否需导出检测
            sheet=wb.sheet_by_name(sn)
        else:
            continue
        datas[ sn[len(cfg.sheet_name_prefix):] ]=worksheet_handle(sheet,cfg)
    return datas

def worksheet_handle(sheet,cfg):
    '''
    处理一个excel工作表。
    @param sheet: sheet对象
    @param cfg: xlloader配置对象。
    @return: 工作表的数据。
    '''
    bounds=get_sheet_bounds(sheet,cfg)
    this_data=[]
    note_cols=[]
    note_rows=[]
    types={}
    for r in range(bounds[1][0],bounds[0][0]):
        ROW=r
        if r in note_rows:continue   #跳过注释行
        this_row=[]
        for c in range(bounds[0][1],bounds[1][1]):
            COLUMN=c
            if c in note_cols:continue   #跳过注释列
            v=str(sheet.cell(r,c).value)    #获取字符串形式原始数据
            if v.lstrip().startswith( cfg.note_signs ):  #注释排查（裁剪左端空字符）
                if r==bounds[1][0]: #列注释
                    note_cols.append(c)
                    continue   #下一列
                elif c==bounds[0][1]:   #行注释
                    note_rows.append(r)
                    break   #跳出列循环，开始下一行
                else:  #内容注释
                    if not cfg.allow_inner_note:
                        raise Exception(f'<FILE>{FILENAME} <SHEET>{SHEETNAME} <ROW>{ROW+1} <COLUMN>{COLUMN+1}:Inner Note not allowed!')
            else:
                if r==bounds[1][0]: #第一行存储类型信息
                    types[c]=get_type_pre(v,cfg)
                    cv=v
                else:
                    cv=clean_cell_data(sheet.cell(r,c),types[c])    #Cell对象数据清洗并保存为实际类型
                    if cv==None:print(f'<FILE>{FILENAME} <SHEET>{SHEETNAME} <ROW>{ROW+1} <COLUMN>{COLUMN+1}:Value Error!')
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
            if sheet.cell(r,c).value==cfg.bound_tag:
                bounds.append([r,c])
    if len(bounds)!=2 or \
       bounds[0][0]==bounds[1][0] or \
       bounds[0][1]==bounds[1][1]:  #标记!=2个 or 标记坐标的rc有一样的，返回错误。
        raise Exception(f"<FILE>{FILENAME} <SHEET>{SHEETNAME}:bound tags error!\nNeed exactly 2 tags,and can't be in the same row or column!")
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
    for i,pre in enumerate(cfg.var_type_pre):
        if val.startswith(pre):return i
    return 2    #特殊情况均视为str
    
def clean_cell_data(cell,type_value):
    '''
    Get a python type variable,from Excel-Cell-Object in xlrd.
        ctype0-empty str
        ctype1-str
        ctype2-float
        ctype3-datetime
        ctype4-int
        ctype5-excel error
        ctype6-empty
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
        print(f'###WARNING!NOT A BOOL!<FILE>{FILENAME} <SHEET>{SHEETNAME} cell.value:{cell.value},cell.ctype:{cell.ctype}')
    elif t==3:  #Excel中的日期或时间
        if type_value==2:   #只接受字符串形式时间
            timetuple=xlrd.xldate_as_tuple(cell.value, 0)
            if timetuple[3]==0: #只有日期
                return '/'.join( [ str(item) for item in timetuple[:3] ] )
            else:
                return '/'.join( [ str(item) for item in timetuple[:3] ] ) + \
                       ' ' + \
                       ':'.join( [ str(item) for item in timetuple[3:] ] )
        print('###WARNING!DATETIME TYPE ONLY STRING OUTPUT SUPPORTED!<FILE>{FILENAME} <SHEET>{SHEETNAME} cell.value:{cell.value},cell.ctype:{cell.ctype}')
    else:   #其余异常情况
        print('###WARNING!ERROR!<FILE>{FILENAME} <SHEET>{SHEETNAME} cell.value:{cell.value},cell.ctype:{cell.ctype}')
    return str(cell.value)
        
#Excel中对ctype2,3的特殊处理
def clean_int(cell):    
    return int(cell.value)
def clean_float(cell):
    return float('%.8f' % cell.value)
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
        
def get_data(cfg):
    input_files=file_list(cfg.xl_dir,cfg.file_exts,cfg.recursive_xl_files)
    raw_data={}
    for fn in input_files:  #文件循环
        FILENAME=fn
        raw_data.update(workbook_handle(fn,cfg))
    return raw_data