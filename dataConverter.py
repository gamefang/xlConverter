# -*- coding: utf-8 -*-
# python3.7+

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
    elif len(oridata)==2: #横向键值对组合
        resultd={}
        if cfg['keep_var_type']:
            for colnum in range(len(oridata[0])):
                resultd[oridata[0][colnum]]=oridata[1][colnum]
        else:
            for colnum in range(len(oridata[0])):
                pre_len=len(cfg['var_type_pre'][get_type_pre(oridata[0][colnum],cfg)])
                resultd[ oridata[0][colnum][pre_len:] ]=oridata[1][colnum]
        return resultd
    listdata=oridata.copy()
    result={}
    pro_names=listdata.pop(0)
    for item in listdata:
        subdic={}
        for i in range(1,len(item)):
            if bool(cfg['allow_inner_note']) and \
                isinstance(item[i],str) and \
                item[i].startswith( cfg['note_signs'] ):
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
    elif len(oridata)==2: #横向键值对组合
        resultd={}
        if cfg['keep_var_type']:
            for colnum in range(len(oridata[0])):
                resultd[oridata[0][colnum]]=oridata[1][colnum]
        else:
            for colnum in range(len(oridata[0])):
                pre_len=len(cfg['var_type_pre'][get_type_pre(oridata[0][colnum],cfg)])
                resultd[ oridata[0][colnum][pre_len:] ]=oridata[1][colnum]
        return resultd                
    listdata=oridata.copy()
    result=[]
    if cfg['begin_with_null']:result=[None]    #特殊的补null情况(RMMV)
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