# -*- coding: utf-8 -*-
# python3.7+

class Dobj(object):
    '''
    将嵌套的字典转为嵌套的对象
    用法：
        myDic={'a':1,'b':{'c':2,'d':{'e':3,'f':4}}}
        myDicObj=Dobj(myDic)
        print(myDicObj) #  {'a':1,'b':{'c':2,'d':{'e':3,'f':4}}}
        print(myDicObj.b.d.e)   #  3
    '''
    def __init__(self, dic):
        for k, v in dic.items():
            if isinstance(v, list):
                setattr(self, k, [Dobj(x) if isinstance(x, dict) else x for x in v])
            elif isinstance(v, tuple):
                setattr( self, k, tuple([Dobj(x) if isinstance(x, dict) else x for x in v]) )
            else:
                setattr(self, k, Dobj(v) if isinstance(v, dict) else v)
    def __repr__(self):
        return repr(self.__dict__)

def s2b(str):   #字符串转bool
    return True if str.lower() in ('true','1') else False
def s2ls(str):  #字符串分割为字符串list
    return str.split(',')
def s2ts(str):  #字符串分割为字符串tuple
    return tuple(str.split(','))

dic_type={  #类型前缀，默认为字符串
        '<b>':s2b,
        '<ts>':s2ts,
        '<i>':int,
        '<f>':float,
        }

def odic_clean(odic):
    '''
    清洗ini文件的配置字典
    @param odic: ini文件解析的default或sections的有序字典数据
    @return: 常规字典
    '''
    result={}
    for k,v in odic.items():
        if not k.startswith( tuple(dic_type.keys()) ):
            myk,myv=k,v
        else:
            for pre in dic_type.keys():
                if k.startswith(pre):
                    myk=k[len(pre):]
                    if v=='None':   #所有非字符串的None均为None
                        myv=None
                    else:
                        myv=dic_type[pre](v)
        result[myk]=myv
    return result
        
def get_cfg(cfg_file_path,get_obj=True):
    '''
    加载ini配置
    @param cfg_file_path: ini配置文件路径
    @param get_obj: 是否获取为Dobj对象
    @return: 整理后的配置字典或Dobj对象
    '''
    import configparser
    cfg=configparser.ConfigParser()
    cfg.read(cfg_file_path,encoding='utf8')
    result=odic_clean(cfg._defaults)   #DEFAULT节点解析
    for sec,odic in cfg._sections.items():   #其它节点解析
        result[sec]=odic_clean(odic)
    if get_obj:
        return Dobj(result)
    return result