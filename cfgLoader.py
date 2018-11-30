# -*- coding: utf-8 -*-
# python3.7+

def s2b(str):   #字符串转bool
    return True if str.lower() in ('true','1') else False
def s2ls(str):  #字符串分割为字符串list
    return str.split(',')
def s2ts(str):  #字符串分割为字符串tuple
    return tuple(str.split(','))

dic_type={  #默认为字符串类型
        'b_':s2b,
        'ts_':s2ts,
        'i_':int,
        'f_':float,
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
                    myv=dic_type[pre](v)
        result[myk]=myv
    return result
        
def get_cfg(cfg_file_path):
    '''
    加载ini配置
    @param cfg_file_path: ini配置文件路径
    @return: 整理后的配置字典
    '''
    import configparser
    cfg=configparser.ConfigParser()
    cfg.read(cfg_file_path,encoding='utf8')
    result=odic_clean(cfg._defaults)   #DEFAULT节点解析
    for sec,odic in cfg._sections.items():   #其它节点解析
        result[sec]=odic_clean(odic)
    return result