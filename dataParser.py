# -*- coding: utf-8 -*-
# python3.7+

import os
import codecs
import json

def json_output(fn,data,cfg):
    '''
    output json file.
    @param fn: full file path.
    @param data: json data.
    '''
    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        jsonstr=json.dumps(
                            data,
                            ensure_ascii=False,
                            indent=cfg.json_indent,
                            separators=eval(cfg.json_separators),
                            )
        jsonstr=jsonstr.replace(r'\\n',r'\n')   #2018/9/6 解决转义字符多次转义错误
        f.write(jsonstr)
    print('<%s> Done!' % fn)

def md_output(fn,data,cfg):
    '''
    output markdown file.
    @param fn: full file path.
    @param data: markdown data.
    '''    
    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        column_num=len(data[0])
        for i,entire_row in enumerate(data):
            output_row=''
            for item in entire_row:
                output_row+='|' + str(item)
            f.write( output_row + '|\n' )
            if i==0:f.write( '|:--'*column_num + '|\n' )   #输出表分割符
    print('<%s> Done!' % fn)
    
def parse(data,cfg):
    if not os.path.exists(cfg.output_dir):
        os.makedirs(cfg.output_dir)
        print(f'{cfg.output_dir}:输出文件夹不存在，已自动创建！')
    myparser={
                0:json_output,
                1:md_output,
                }[cfg.output_type]
    myext={
            0:'json',
            1:'md',
            }[cfg.output_type]
    if cfg.output_in_one:
        fn=os.path.join(cfg.output_dir,cfg.output_in_one_fn)
        fn=os.path.abspath(fn)
        myparser(fn,data,cfg)
    else:
        for k,v in data.items():
            fn=os.path.join(cfg.output_dir,f'{k}.{myext}')
            fn=os.path.abspath(fn)
            myparser(fn,v,cfg)