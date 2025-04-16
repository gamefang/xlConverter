# -*- coding: utf-8 -*-
# 設置模塊

from configparser import ConfigParser

class SettingData:
    # 類型標記分隔符
    TYPE_SEP = ':'

    def __init__(self, setting_fp, default_section = None):
        '''
        加載配置文件并初始化，可設置默認節點

        :param setting_fp: 給出一個配置文件路徑
        :param default_section: 可指定默認節點名稱，沒有則尋找DEFAULT，
        還沒有則找所有節點中的第一個
        '''
        self.data = ConfigParser()
        # 加載
        result = self.data.read(setting_fp, encoding='utf8')
        if not result:
            raise AssertionError(f'setting file not exist: {setting_fp}')
        # 確定默認section
        if default_section: # 指定了默認section
            if self.data.has_section(default_section):
                self.default_section = default_section
                return
        if self.data.defaults():
            self.default_section = self.data.default_section
        elif self.data.sections():
            self.default_section = self.data.sections()[0]
        else:
            raise AssertionError(f'not a valid ini setting file: {setting_fp}')

    def get_at(self, section, name):
        '''
        獲取指定section的用戶配置，可根據前綴定義自動轉化類型
        '''
        if self.data is None: return None
        raw_value = self.data.get(section, name, fallback=None)
        if raw_value: return raw_value  # 默認字符串類型
        for pre in DIC_TYPE_PREFIX.keys():  # 嘗試檢索帶類型前綴的定義
            raw_value = self.data.get(section, pre + name, fallback = None)
            if raw_value:   # 使用各自的轉化方法
                parse_method = DIC_TYPE_PREFIX[pre]
                return parse_method(raw_value)
        return None # 找不到定義
    
    def get(self, name):
        '''
        獲取默認section的用戶配置，可根據前綴定義自動轉化類型
        '''
        return self.get_at(self.default_section, name)

# 類型轉化方法
def to_int(raw) -> int:
    try:
        return int(raw)
    except:
        return 0
def to_float(raw) -> float:
    try:
        return float(raw)
    except:
        return 0.0
def to_bool(raw) -> bool:
    return True if str(raw).lower() in ('true', '1') else False
def to_list_str(raw, sep = ',') -> list:
    raw = str(raw).strip()
    raw_list = raw.split(sep)
    return [item.strip() for item in raw_list]
# 類型前綴與對應的轉化方法
DIC_TYPE_PREFIX = {
    '<i>' : to_int,
    '<f>' : to_float,
    '<b>' : to_bool,
    '<ls>' : to_list_str,
}