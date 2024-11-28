# -*- coding: utf-8 -*-
# python3.7+

import os
import codecs
import json
from datetime import datetime

def json_output(fn,data,cfg):
    '''
    output json file.
    @param fn: full file path.
    @param data: json data.
    @param cfg: global config.
    '''
    if cfg.json_wrapper_name != "":
        data = {cfg.json_wrapper_name : data}
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
    @param cfg: global config.
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
    
def pickle_output(fn,data,cfg):
    '''
    output pickle file.
    get config:
        with open(fn,'rb') as f:
            cfg=pickle.load(f)
    @param fn: full file path.
    @param data: pickle data.    
    @param cfg: global config.
    '''
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    with open(os.path.normpath(fn),'wb') as f:
        pickle.dump(data,f,protocol=cfg.pickle_protocol)
    print('<%s> Done!' % fn)
    
def lua_output(fn,data,cfg):
    '''
    output lua table file.
    @param fn: full file path.
    @param data: lua table data.
    @param cfg: global config.
    '''
    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        lua_table = "{\n"
        for key, value in data.items():
            if isinstance(key, int):
                lua_table += f'    [{key}] = '
            else:
                lua_table += f'    ["{key}"] = '
            if isinstance(value, dict):
                lua_table += '{\n'
                for k, v in value.items():
                    if isinstance(v, str):
                        lua_table += f'        ["{k}"] = "{v}",\n'
                    elif isinstance(v, list):   # 表格中嵌套list，字符串数值混用需加""
                        lua_str = '{'
                        for num,item in enumerate(v):
                            if isinstance(item, str):
                                lua_str += f'{item}'
                            else:
                                lua_str += str(item)
                            if num != len(v) - 1:
                                lua_str += ','
                        lua_str += '}'
                        lua_table += f'        ["{k}"] = {lua_str},\n'
                    else:
                        lua_table += f'        ["{k}"] = {json.dumps(v)},\n'
                lua_table += '    },\n'
            elif isinstance(value, str):
                lua_table += f'{{ text = "{value}" }},\n'
            else:
                lua_table += f'{json.dumps(value)},\n'
        lua_table += "}"
        name = get_sheetname(fn)
        f.write(f'{cfg.lua_template.format(name=name, luastr=lua_table)}')
    print('<%s> Done!' % fn)
    
def csv_output(fn,data,cfg):
    '''
    output csv file.
    @param fn: full file path.
    @param data: csv data.
    @param cfg: global config.
    '''
    sep = cfg.csv_separator
    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        column_num=len(data[0])
        for i,entire_row in enumerate(data):
            output_row=''
            for item in entire_row:
                output_row += str(item) + sep
            f.write( output_row[:-1] + '\n' )
    print('<%s> Done!' % fn)
    
def get_sheetname(fn):
   '''
   根据文件路径获取文件名字符串
   @param fn: 完整文件路径
   @return: 文件名字符串
   '''
   fnext = os.path.basename(fn)
   li = fnext.split('.')
   return li[0]
   
def parse(data,cfg,table_info):
    if not os.path.exists(cfg.output_dir):
        os.makedirs(cfg.output_dir)
        print(f'{cfg.output_dir}:输出文件夹不存在，已自动创建！')
    myparser={
                0:json_output,
                1:md_output,
                2:pickle_output,
                3:lua_output,
                4:csv_output,
                }[cfg.output_type]
    myext={
            0:'json',
            1:'md',
            2:'data',
            3:'lua',
            4:'csv',
            }[cfg.output_type]
    if cfg.output_ext:myext=cfg.output_ext
    if cfg.output_in_one:
        fn=os.path.join(cfg.output_dir,cfg.output_in_one_fn)
        fn=os.path.abspath(fn)
        myparser(fn,data,cfg)
    else:
        for k,v in data.items():
            fn=os.path.join(cfg.output_dir,f'{k}.{myext}')
            fn=os.path.abspath(fn)
            myparser(fn,v,cfg)
            if cfg.cs_class_gen:    # 额外输出cs类
                cs_class_gen(fn,v,cfg,table_info)

def cs_class_gen(fn,data,cfg,table_info):
    '''
    生成unity使用的类定义
    '''
    # 确定sheet名
    sheet_name = get_sheetname(fn)
    infos = table_info[sheet_name]
    # 确定key类型
    key_type = cfg.cs_type_name[infos["key"]]
    # 确定参数列表
    params_list = list(infos.keys())[1:] 
    # 确定参数数据类型
    param_type_names = [cfg.cs_type_name[item] for item in list(infos.values())[1:]]
    
    # 文本生成 Start
    result = '''// xlConverter自动生成的脚本
using System;
using System.Collections.Generic;

namespace gamefang
{
    [Serializable]
    public class Conf''' + sheet_name.capitalize()
    result += '''
    {
        public ''' + key_type + ''' key;'''
    for num,param_name in enumerate(params_list):
        result += '''
        public ''' + param_type_names[num] + ''' ''' + param_name + ''';'''
    result += '''

        public Conf''' + sheet_name.capitalize() + '''(''' + key_type + ''' key)
        {
            this.key = key;
            if (ConfigManager.GetTable("''' + sheet_name + '''") is not Conf''' + sheet_name.capitalize() + '''List list_conf)
                return;
            foreach (var item in list_conf.data)
            {
                if (item.key == key)
                {'''
    for num,param_name in enumerate(params_list):
        result += '''
                    this.''' + param_name + ''' = item.''' + param_name + ''';'''
    result += '''
                    return;
                }
            }
        }

        public static List<''' + key_type + '''> list_keys{get{
            List<''' + key_type + '''> result = new();
            var table = ConfigManager.GetTable("'''
    result += sheet_name + '''") as Conf''' + sheet_name.capitalize() + '''List;
            foreach (var conf in table.data)
                result.Add(conf.key);
            return result;
        }''' + '''}
    }

    [Serializable]
    public class Conf'''
    result += sheet_name.capitalize() + '''List : IConfList
    {
        public List<Conf''' + sheet_name.capitalize() + '''> data;

        public object GetList()
        {
            return data;
        }
    }
}'''
    fn = os.path.join(cfg.cs_output_dir, f'Conf{sheet_name.capitalize()}.cs')
    # 文本生成 End

    with codecs.open(os.path.normpath(fn),'w','utf8') as f:
        f.write(result)
    print(f'cs gen: <{fn}>')

    # 一次性文件
    fn2 = fn.replace('/Config', '/Data').replace(f'Conf{sheet_name.capitalize()}.cs', f'Data{sheet_name.capitalize()}.cs')
    result2 = f'''using gamefang;

namespace gu
{{
    public class Data{sheet_name.capitalize()} : Conf{sheet_name.capitalize()}
    {{
        // 存檔數據

        // 擴展數據

        // 構造函數
        public Data{sheet_name.capitalize()}({key_type} key) : base(key)
        {{
        }}
    }}
}}'''

    # 寫入一次性文件
    if not os.path.exists(fn2):
        with codecs.open(os.path.normpath(fn2), 'w', 'utf8') as f:
            f.write(result2)
            print(f'cs gen: <{fn2}>')






# ------------------------------------------------------
# 模板1
'''
// xlConverter自动生成的脚本
using gamefang;

public partial class DataMelody
{
    public int key {get;}
    public bool artpiece {get;}
    public float time {get;}

    public DataMelody(int key)
    {
        this.key = key;
        this.artpiece = ConfigManager.GetData<bool>("melody",key,"artpiece");
        this.time = ConfigManager.GetData<float>("melody",key,"time");
    }

}
'''
# 模板1文本生成代码
#     # 文本生成 Start
#     result = '''// xlConverter自动生成的脚本: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''
# using gamefang;

# public partial class Data''' + sheet_name.capitalize()
#     result += '''
# {
#     public ''' + key_type + ''' key {get;}'''
#     for num,param_name in enumerate(params_list):
#         result += '''
#     public ''' + param_type_names[num] + ''' ''' + param_name + ''' {get;}'''
#     result += '''

#     public Data''' + sheet_name.capitalize() + '''(''' + key_type + ''' key)
#     {
#         this.key = key;'''
#     for num,param_name in enumerate(params_list):
#         result += '''
#         this.''' + param_name + ''' = ConfigManager.GetData<''' + param_type_names[num] + '''>("''' + sheet_name + '''",key,"''' + param_name + '''");'''
#     result += '''
#     }

# }
# '''
#     fn = os.path.join(cfg.cs_output_dir, f'Data{sheet_name.capitalize()}.cs')
#     # 文本生成 End

# ------------------------------------------------------
# 模板2
'''
// xlConverter自动生成的脚本
using System;
using System.Collections.Generic;

namespace gamefang
{
    [Serializable]
    public class ConfQuest
    {
        public int key;
        public string name;
        public string tip;
        public string con;
        public bool repeatable;
        public string reward;
        public int[] show_reward;
        public int[] item_need;
        public bool cost_item;

        public ConfQuest(int key)
        {
            this.key = key;
            if (ConfigManager.GetTable("quest") is not ConfQuestList list_conf)
                return;
            foreach (var item in list_conf.data)
            {
                if (item.key == key)
                {
                    this.name = item.name;
                    this.tip = item.tip;
                    this.con = item.con;
                    this.repeatable = item.repeatable;
                    this.reward = item.reward;
                    this.show_reward = item.show_reward;
                    this.item_need = item.item_need;
                    this.cost_item = item.cost_item;
                    return;
                }
            }
        }

        public static List<int> list_keys{get{
            List<int> result = new();
            var table = ConfigManager.GetTable("quest") as ConfQuestList;
            foreach (var conf in table.data)
                result.Add(conf.key);
            return result;
        }}
    }

    [Serializable]
    public class ConfQuestList : IConfList
    {
        public List<ConfQuest> data;

        public object GetList()
        {
            return data;
        }
    }
}

'''
# 模板2文本生成代码
#     # 文本生成 Start
#     result = '''// xlConverter自动生成的脚本
# using System;
# using System.Collections.Generic;

# namespace gamefang
# {
#     [Serializable]
#     public class Conf''' + sheet_name.capitalize()
#     result += '''
#     {
#         public ''' + key_type + ''' key;'''
#     for num,param_name in enumerate(params_list):
#         result += '''
#         public ''' + param_type_names[num] + ''' ''' + param_name + ''';'''
#     result += '''

#         public Conf''' + sheet_name.capitalize() + '''(''' + key_type + ''' key)
#         {
#             this.key = key;
#             if (ConfigManager.GetTable("''' + sheet_name + '''") is not Conf''' + sheet_name.capitalize() + '''List list_conf)
#                 return;
#             foreach (var item in list_conf.data)
#             {
#                 if (item.key == key)
#                 {'''
#     for num,param_name in enumerate(params_list):
#         result += '''
#                     this.''' + param_name + ''' = item.''' + param_name + ''';'''
#     result += '''
#                     return;
#                 }
#             }
#         }

#         public static List<''' + key_type + '''> list_keys{get{
#             List<''' + key_type + '''> result = new();
#             var table = ConfigManager.GetTable("'''
#     result += sheet_name + '''") as Conf''' + sheet_name.capitalize() + '''List;
#             foreach (var conf in table.data)
#                 result.Add(conf.key);
#             return result;
#         }''' + '''}
#     }

#     [Serializable]
#     public class Conf'''
#     result += sheet_name.capitalize() + '''List : IConfList
#     {
#         public List<Conf''' + sheet_name.capitalize() + '''> data;

#         public object GetList()
#         {
#             return data;
#         }
#     }
# }'''
#     fn = os.path.join(cfg.cs_output_dir, f'Conf{sheet_name.capitalize()}.cs')
#     # 文本生成 End

# 模版2額外模版
# using gamefang;

# namespace gu
# {
#     public class DataMsg : ConfMsg
#     {
#         // 存檔數據

#         // 擴展數據

#         // 構造函數
#         public DataMsg(string key) : base(key)
#         {
#         }
#     }
# }