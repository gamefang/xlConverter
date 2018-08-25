# -*- coding: utf-8 -*-
#2018/8/24 实现excel策划配置文件批量导出为json。
#不能完美支持python2。

CONF_FILE='xl2json_conf.json'   #配置文件路径

__doc__='''
配置文件说明(%s)
    配置文件可调整部分功能，需要严格遵循json格式。
    @xl_dir: Excel文件的存放目录，会自动搜寻目录下所有Excel文件。
    @json_dir: 输出json文件的目录。
    @output_in_one: 如果为false或0，则分别输出json文件，文件名为Excel对应sheet名；
                    如果为字符串，则输出至一个文件，例如填写config.json，则将所有Excel文件内容输出至该文件中。
    @file_exts: 搜寻的Excel文件後缀。另外默认以'~$','__'开头的excel文件不会被搜寻。
    @sheet_name_prefix: Excel文件中，加此前缀的sheet会被导出，可支持多个。前缀只允许一个字符。
    @bound_tag: Excel一个sheet中配置的边界符号，只有边界内的配置内容才会被导出。
    @note_signs: Excel配置中单行、单列注释的前缀，被注释则不会被导出。
    @keep_var_type: 是否在json的key中保留字段名前缀。
    @read_me_mode: 是否查看说明。
Excel文件格式说明
    1.[工作簿]需要导出的所有Excel文件必须放在配置文件夹中。
    2.[工作表]需要导出的sheet页前需加前缀，如分开导出则json文件名为前缀後的sheet名。
    3.[导出区域]需要导出的区域要用边界符号框住，位置为右上和左下。
    4.[字段名称]右上边界符号所在行必须为表头，第一个字符表示字段的数据类型，需遵循以下规则：
        i-python的int，对应json中的数字num；
        f-python的float，对应json中的数字num；
        s-python的string，对应json中的字符串string；
        t-python的tuple，json无需使用。
        l-python的list，对应json中的数组array；
        d-python的dict，对应json中的对象object；
        b-python的boolean，对应json中的布尔值bool；
        暂不包括json中的null类型。
    5.[数据规范]同列Excel数据需要遵循字段的数据类型，否则会产生错误。
        数字：Excel所见即所得；
        字符串：无需添加两侧""；
        数组：无需添加两侧[]，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        对象：无需添加两侧{}，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        布尔值：Excel所见即所得。
''' % CONF_FILE

__author__='gamefang'

import xlrd

import os
import re
import json
import codecs

def file_list(sDir,tExt):
    '''
    Get custom filelist in some direction.
    @param sDir: the full direction to handle.
    @param tExt: a tuple of file extensions.
    @return: list of filenames.
    '''
    lFiles=[]
    for root, dirs, files in os.walk(sDir):
        for f in files:
            if f.startswith( ('~$','__') ):continue    #2017/11/20 避免加入隐藏文件 2018/4/23 双下划线文件不导出
            if os.path.splitext(f)[1][1:] in tExt:
                lFiles.append(os.path.join(root,f))
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
                else:
                    raise Exception("<FILE>%s <SHEET>%s <ROW>%s <COLUMN>%s:Note Error!" % (FILENAME,SHEETNAME,ROW+1,COLUMN+1) )
            else:
                if r==bounds[1][0]: #第一行存储类型信息（字符串首字符）
                    types[c]=v[0]
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
    
def clean_cell_data(cell,typ):
    '''
    Get a python type variable,from Excel-Cell-Object in xlrd.
    Need RE.
    #cell:cell object in xlrd.
    #typ:
        i-int
        f-float
        s-string
        t-tuple
        l-list
        d-dict
        b-boolean
    '''
    t=cell.ctype
    if t==0 or not cell.value:    #空，或Excel中残留的'型单元格等情况
        if typ=='i':
            return 0
        elif typ=='f':
            return 0.0
        elif typ=='s':
            return ""
        elif typ=='t':
            return ()
        elif typ=='l':
            return []
        elif typ=='d':
            return {}
        elif typ=='b':
            return False
    elif t==1:  #非数字
        v=str(cell.value)
        if typ=='i' and re.match('^(\-|\+)?\d$',v):    #文本形式保存的整数
            return int(v)
        elif typ=='f' and re.match('^(-?\d+)(\.\d+)?$',v): #文本形式保存的符点数
            return float(v)
        elif typ=='s':
            return v
        elif typ=='t':
            return eval('(%s,)'%v)
        elif typ=='l':
            return eval('[%s,]'%v)
        elif typ=='d':
            return eval('{%s,}'%v)
        elif typ=='b':
            return (v in ('True','TRUE','true','t','T','1'))    #可以当True用的字符串
    elif t==2:  #数字
        if typ=='i':
            return int(cell.value)
        elif typ=='f':
            return float(cell.value)
        elif typ=='s':
            return str(int(cell.value))  #整数字符串（通常为设计问题）
        elif typ=='t':
            return eval( '(%s,)' % int(cell.value) )    #容器里面暂时只存整数
        elif typ=='l':
            return eval( '[%s,]' % int(cell.value) )    #容器里面暂时只存整数
        elif typ=='d':
            return eval( '{%s,}' % int(cell.value) )    #容器里面暂时只存整数
        elif typ=='b':
            return bool(cell.value)  #有值就算True
    elif t==4:  #Excel中的TRUE和FALSE
        if typ=='b':
            if cell.value:  #TRUE实际等于1.0
                return True
            else:
                return False
        else:
            print('###WARNING!NOT A BOOL! cell.value:{self.value},cell.ctype:{self.ctype}'.format(self=cell))
            return str(cell.value)
    else:   #其余异常情况
        print('###WARNING!ERROR! cell.value:{self.value},cell.ctype:{self.ctype}'.format(self=cell))
        return str(cell.value)
    
def dic_convert(oridata,keep_var_type=False):
    '''
    From:
    [['sId', 'sName', 'sTip', 'iFulfill_value'],
     ['test', '成就', '一个测试成就', 100],
     ['testhide', '隐藏成就', '又一个测试成就', 100]]
    To:
    {'test': {'Name': '成就', 'Tip': '一个测试成就', 'Fulfill_value': 100},
     'testhide': {'Name': '隐藏成就', 'Tip': '又一个测试成就', 'Fulfill_value': 100}}
    @param oridata: original 2-dimensional list.
    @param keep_var_type: whether keep the variable type prefix in dic keys.
    @return: a copy of new styled dic.
    '''
    listdata=oridata.copy()
    dic={}
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(1,len(item)):
            if keep_var_type:
                subdic[ pro_names[i] ]=item[i]
            else:
                subdic[ pro_names[i][1:] ]=item[i]
        dic[ item[0] ]=subdic
    return dic

def json_output(fn,data):
    '''
    output json file.
    @param fn: full file path.
    @param data: json data.
    '''
    with codecs.open(fn,'w','utf8') as f:
        jsonstr=json.dumps(data,ensure_ascii=False,indent=2)
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
    
def main():
    #载入配置
    with open(CONF_FILE) as json_file:
        cfg=json.load(json_file)
    if cfg['read_me_mode']:show_readme()
    #从Excel文件中输入原始数据
    input_files=file_list(cfg['xl_dir'],cfg['file_exts'])
    raw_data={}
    for fn in input_files:  #文件循环
        global FILENAME
        FILENAME=fn
        raw_data.update(workbook_handle(fn,cfg))
    #原始数据转化
    data={
        k[1:]:dic_convert(v,cfg['keep_var_type'])
        for k,v in raw_data.items()
        }
    #输出为json
    if cfg['output_in_one']:
        fn=os.path.join(cfg['json_dir'],cfg['output_in_one'])
        json_output(fn,data)
    else:
        for k,v in data.items():
            fn=os.path.join(cfg['json_dir'],'%s.json' % k)
            json_output(fn,v)
            
if __name__ == '__main__':
    main()
