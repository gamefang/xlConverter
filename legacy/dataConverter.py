# -*- coding: utf-8 -*-
# python3.7+

from xlLoader import get_type_pre

def common_convertion(oridata,cfg):
    '''
    常规的转化模式
        单列列表：
            From:
            [['skey'],
             ['a'],
             ['b'],
             ['c']]
            To:
            ['a','b','c']
        横向键值对组合
            From:
            [['k1','k2','k3'],['v1','v2','v3']]
            To:
            {'k1':'v1','k2':'v2','k3':'v3'}
    @param oridata: original 2-dimensional list.
    @param cfg: global config object.
    @return: [是否被常规转化,原数据]
    '''
    if len(oridata[0])==1:  #如果只有一列，自动导出成列表
        return [True,
                [
                oridata[i][0]
                for i in range(1,len(oridata))
                ]
                ]
    elif len(oridata)==2: #横向键值对组合
        resultd={}
        if cfg.keep_var_type:
            for colnum in range(len(oridata[0])):
                resultd[oridata[0][colnum]]=oridata[1][colnum]
        else:
            for colnum in range(len(oridata[0])):
                pre_len=len(cfg.var_type_pre[get_type_pre(oridata[0][colnum],cfg)])
                resultd[ oridata[0][colnum][pre_len:] ]=oridata[1][colnum]
        return [True,resultd]
    return [False,oridata]

def convertion_0(oridata,cfg):
    '''
    大对象内的 主键 - 键值对
    From:
    [['sId', 'sName', 'sTip', 'iFulfill_value'],
     ['test', '成就', '一个测试成就', 100],
     ['testhide', '隐藏成就', '又一个测试成就', 100]]
    To:
    {'test': {'Name': '成就', 'Tip': '一个测试成就', 'Fulfill_value': 100},
     'testhide': {'Name': '隐藏成就', 'Tip': '又一个测试成就', 'Fulfill_value': 100}}
    @param oridata: original 2-dimensional list.
    @param cfg: global config object.
    @return: a copy of new styled data.
    '''
    isCommon,oridata=common_convertion(oridata,cfg)
    if isCommon:return oridata
    listdata=oridata.copy()
    result={}
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(1,len(item)):
            if __is_continue(i,item,cfg):continue
            if cfg.keep_var_type:
                subdic[ pro_names[i] ]=item[i]
            else:
                pre_len=len(cfg.var_type_pre[get_type_pre(pro_names[i],cfg)])
                subdic[ pro_names[i][pre_len:] ]=item[i]
        result[ item[0] ]=subdic
    return result
    
def convertion_1(oridata,cfg,**kw):
    '''
    数组内的键值对对象
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
    @param oridata: original 2-dimensional list.
    @param cfg: global config object.
    @return: a copy of new styled result.
    '''
    isCommon,oridata=common_convertion(oridata,cfg)
    if isCommon:return oridata             
    listdata=oridata.copy()
    result=[]
    if cfg.begin_with_null:result=[None]    #特殊的补null情况(RMMV)
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(0,len(item)):
            if __is_continue(i,item,cfg):continue     
            if cfg.keep_var_type:
                subdic[ pro_names[i] ]=item[i]
            else:
                pre_len=len(cfg.var_type_pre[get_type_pre(pro_names[i],cfg)])
                subdic[ pro_names[i][pre_len:] ]=item[i]
        result.append(subdic)
    return result

def __is_continue(i,item,cfg):
    #不输出所有空数据
    if cfg.remove_blank_params and \
        item[i]==None:
            return True
    #行内注释，不输出某key的某些字段
    if cfg.allow_inner_note and \
        isinstance(item[i],str) and \
        item[i].startswith( cfg.note_signs ):
            return True
    return False
    
def convert(raw_data,cfg):
    if cfg.output_type in (1,4):return raw_data   #输出md或csv文件使用原格式
    if not cfg.convert_style:
        data={
            k[:]:convertion_0(v,cfg)
            for k,v in raw_data.items()
            }
    elif cfg.convert_style==1:
        data={
            k[:]:convertion_1(v,cfg)
            for k,v in raw_data.items()
            }
    else:
        print('convert_style not existed!')
    return data