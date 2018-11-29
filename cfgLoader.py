# -*- coding: utf-8 -*-
# python3.7+

def s2b(str):
    '''
    字符串转bool
    '''
    return True if str.lower() in ('true','1') else False
    
def s2ls(str):
    '''
    字符串分割为字符串list
    '''
    return str.split(',')
    
def s2ts(str):
    '''
    字符串分割为字符串tuple
    '''
    return tuple(str.split(','))
    
def get_cfg():
    '''
    加载ini配置
    '''
    import configparser
    cfg=configparser.ConfigParser()
    cfg.read('xlConverter.ini',encoding='utf8')
    cfg={ **cfg._defaults,**cfg._sections }
    return cfg