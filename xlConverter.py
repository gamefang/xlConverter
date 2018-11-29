# -*- coding: utf-8 -*-
# python3.7+

version='1.4.0'
__author__='gamefang'

import xlLoader
import dataConverter
import jsonParser
import mdParser

def get_cfg():
    '''
    加载ini配置
    '''
    import configparser
    cfg=configparser.ConfigParser()
    cfg.read('xlConverter.ini',encoding='utf8')
    cfg={ **cfg._defaults,**cfg._sections }
    return cfg

def main():
    #加载配置
    cfg=get_cfg()
    #excel原始数据导入
    #raw_data=xlLoader.get_raw_data(cfg['xlLoader'])
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
