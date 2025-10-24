# -*- coding: utf-8 -*-
# 配置處理模塊

#region import
# 路径设置
ROOT_DISTANCE = 1   # 距离根目录文件夹层级
import sys
from pathlib import Path
root = str(Path(__file__).parents[ROOT_DISTANCE-1].resolve())
if root not in sys.path: sys.path.insert(0, root)
# std
import sys
# my
from Gfile import gFile
from Glog import gLog
#endregion

log = gLog.fetch(level=gLog.INFO)

class gConf:
    '''
    配置處理模塊
    '''
    pass
    @staticmethod
    def get_json(fp: str) -> dict | list:
        '''
        從json文件獲取數據為字典或列表
        '''
        import json
        fp = gFile.get_abspath(fp)
        if not gFile.is_file_exists(fp):
            log.error(f'file not exist:{fp}')
            return {}
        with open(fp, 'r', encoding='utf-8') as f:
            jsonstr = f.read()
            return json.loads(jsonstr)

    @staticmethod
    def get_toml(fp: str) -> dict:
        '''
        從toml文件獲取數據為字典
        '''
        if sys.version_info >= (3, 11):
            import tomllib as tomltool
        else:
            import tomli as tomltool
        fp = gFile.get_abspath(fp)
        if not gFile.is_file_exists(fp):
            log.error(f'file not exist:{fp}')
            return {}
        with open(fp, 'rb') as f:
            try:
                return tomltool.load(f)
            except Exception as e:
                log.error(str(e))
                return {}

if __name__ == '__main__':
    # result = get_toml('schema.toml')
    result = gConf.get_json('../res/server_conf.json')
    print(result)