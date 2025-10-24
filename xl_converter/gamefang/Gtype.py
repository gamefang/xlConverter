# -*- coding: utf-8 -*-

class gType:
    '''
    類型轉化模塊
    '''
    @staticmethod
    def to_int(raw) -> int:
        try:
            return int(raw)
        except:
            return 0
    @staticmethod
    def to_float(raw) -> float:
        try:
            return float(raw)
        except:
            return 0.0
    @staticmethod
    def to_bool(raw) -> bool:
        return True if str(raw).lower() in ('true', '1') else False
    @staticmethod
    def to_str(raw) -> str:
        if raw is None:
            return ''
        return str(raw)
    @staticmethod
    def _get_raw_list(raw, sep = ',', filter_none = False) -> list:
        raw = str(raw).strip()
        if raw in ('', '[]'): return []
        li = raw.split(sep)
        if filter_none:
            return [item.strip() for item in li if item]
        else:
            return li
    @staticmethod
    def to_list_int(raw, sep = ',') -> list:
        return [__class__.to_int(item.strip()) for item in __class__._get_raw_list(raw, sep)]
    @staticmethod
    def to_list_float(raw, sep = ',') -> list:
        return [__class__.to_float(item.strip()) for item in __class__._get_raw_list(raw, sep)]
    @staticmethod
    def to_list_bool(raw, sep = ',') -> list:
        return [__class__.to_bool(item.strip()) for item in __class__._get_raw_list(raw, sep)]
    @staticmethod
    def to_list_str(raw, sep = ',') -> list:
        return [__class__.to_str(item.strip()) for item in __class__._get_raw_list(raw, sep, filter_none=True)]
    @staticmethod
    def to_dict(raw) -> dict:
        try:
            return eval(str(raw))
        except:
            return {}
    @staticmethod
    def to_list_dict(raw, sep = ',') -> list:
        return [__class__.to_dict(item.strip()) for item in __class__._get_raw_list(raw, sep, filter_none=True)]