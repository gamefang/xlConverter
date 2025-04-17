# -*- coding: utf-8 -*-
# 雜類模塊

# 通用類型轉化方法
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
def to_str(raw) -> str:
    if raw is None:
        return ''
    return str(raw)
def _get_raw_list(raw, sep = ',') -> list:
    raw = str(raw).strip()
    return raw.split(sep)
def to_list_int(raw, sep = ',') -> list:
    return [to_int(item.strip()) for item in _get_raw_list(raw, sep)]
def to_list_float(raw, sep = ',') -> list:
    return [to_float(item.strip()) for item in _get_raw_list(raw, sep)]
def to_list_bool(raw, sep = ',') -> list:
    return [to_bool(item.strip()) for item in _get_raw_list(raw, sep)]
def to_list_str(raw, sep = ',') -> list:
    return [to_str(item.strip()) for item in _get_raw_list(raw, sep)]
def to_dict(raw) -> dict:
    try:
        return eval(str(raw))
    except:
        return None