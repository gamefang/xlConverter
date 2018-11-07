# -*- coding: utf-8 -*-
#不能完美支持python2。
#2018/10/26
#输出markdown文件。

from xl2json import *

def md_output(fn,data):
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
    
def main():
    #载入配置
    with open(CONF_FILE) as json_file:
        cfg=json.load(json_file)
    if cfg['read_me_mode']:show_readme()
    #从Excel文件中输入原始数据，转为python二维列表
    input_files=file_list(cfg['xl_dir'],cfg['file_exts'],cfg['recursive_xl_files'])
    raw_data={}
    for fn in input_files:  #文件循环
        global FILENAME
        FILENAME=fn
        raw_data.update(workbook_handle(fn,cfg))
    #python原始数据转化处理
    data=raw_data
    #输出为markdown（只能分开输出）
    for k,v in data.items():
        fn=os.path.join(cfg['json_dir'],'%s.md' % k[1:])
        md_output(fn,v)

if __name__ == '__main__':
    main()
