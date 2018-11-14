# -*- coding: utf-8 -*-
#2018/11/14
#切换json格式化形式。

import os
import json
import codecs

__author__='gamefang'
#json文件目录
JSON_FOLDER=r'./output/'
#缩进，None为无缩进
JSON_INDENT=2    #None
#分隔符，最紧缩形式：(',', ':')
JSON_SEPARATORS=None  #(',', ':')

def json_format(fn,**kwargs):
    with codecs.open(fn,'r','utf8') as json_file:
        data=json.load(json_file)
    with codecs.open(fn,'w','utf8') as json_file:
        jsonstr=json.dumps(data,**kwargs)
        jsonstr=jsonstr.replace(r'\\n',r'\n')
        json_file.write(jsonstr)

def main():
    for file in os.listdir(JSON_FOLDER):
        fn=os.path.join(JSON_FOLDER,file)
        if os.path.splitext(fn)[1][1:]=='json':
            json_format(
                        fn,
                        ensure_ascii=False,
                        indent=JSON_INDENT,
                        separators=JSON_SEPARATORS
                        )
            print('<%s> Done!' % fn)
            
if __name__ == '__main__':
    main()
