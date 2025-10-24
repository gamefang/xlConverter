# 通用日志模块

# std
from __future__ import annotations
import logging
import logging.handlers
import os
import inspect
from pathlib import Path

class gLog:
    '''
    通用日志模块
    ```
    # 入口脚本，将以下内容置于最前
    from gLog import gLog   # 导入日志
    gLog.LOG_FILENAME = 'test'  # 调整全局默认值，可影响所有后续脚本，如设置全局日志文件名
    log = gLog.fetch(level=gLog.INFO)    # 启用log并调整设置
    log.info('xxxx')    # 写日志

    # 其余脚本只需使用前创建log对象即可
    from gLog import gLog
    log = gLog.fetch(log_to_file=False) # 单独调节log设置
    log.info('xxxx')    # 写日志
    ```
    '''
    # ---------- 日志等级常量 ----------
    DEBUG    = logging.DEBUG     # 10
    INFO     = logging.INFO      # 20
    WARNING  = logging.WARNING   # 30
    ERROR    = logging.ERROR     # 40
    CRITICAL = logging.CRITICAL  # 50

    # 日志字典
    dic_log: dict[str, logging.Logger] = {}

#region 全局默认值
    # 日志格式化
    ## 总格式化样式
    FMT = '[%(asctime)s][%(levelname)s][%(script)s] - %(message)s'
    ## 日期格式化样式
    DATE_FMT = '%Y-%m-%d %H:%M:%S'

    # 日志文档
    ## 日志等级
    LOG_LEVEL = INFO
    ## 是否记录日志到文件
    LOG_TO_FILE = True
    ## 日志文件目录
    LOG_DIR = './__logs'
    ## 日志文件名
    LOG_FILENAME = __name__
    ## 日志文件后缀
    LOG_EXT = 'log'
    ## 日志文件写入方式
    LOG_FILE_MODE = 'w'
    ## 日志分隔线样式
    LOG_SPLIT = '\n' + '-' * 30 + '\n\n'
    ## 单条日志截断最大长度
    MAX_MSG_LEN = 500
#endregion

#region 过滤器
    class _TruncateFilter(logging.Filter):
        '''按最大长度截断日志消息'''
        def __init__(self, max_len: int = 0) -> None:
            super().__init__()
            self.max_len = max(max_len, 0)

        def filter(self, record: logging.LogRecord) -> bool:
            if self.max_len > 0 and isinstance(record.msg, str) and len(record.msg) > self.max_len:
                record.msg = record.msg[:self.max_len] + '...'
            return True

    class _ContextFilter(logging.Filter):
        '''把脚本名注入日志记录'''
        def __init__(self, script: str) -> None:
            super().__init__()
            self.script = script

        def filter(self, record: logging.LogRecord) -> bool:
            record.script = self.script
            return True
#endregion

    @classmethod
    def fetch(cls,
            *,
            level: int = LOG_LEVEL,
            log_to_file: bool = LOG_TO_FILE,
            log_dir: str = LOG_DIR,
            file_mode: str = LOG_FILE_MODE,
            max_msg_len: int = MAX_MSG_LEN,
        ) -> logging.Logger:
        '''
        获取日志对象，参数均可为空而使用默认值

        :param level: 日志等级
        :param log_to_file: 是否记录日志至文件
        :param log_dir: 日志文件夹路径
        :param file_mode: a-同文件日志追加并添加分割线，w-每次清空新建日志，其余情况均为同文件日志追加且不处理
        :param max_msg_len: 日志最多字数，0为不限制
        '''
        frame = inspect.stack()[1]
        script_path = Path(frame.filename).resolve()
        script_name = script_path.stem
        if script_name in cls.dic_log:
            cls.dic_log[script_name].setLevel(level)
            return cls.dic_log[script_name]
        logger = logging.getLogger(script_name)
        logger.setLevel(level)
        # console
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(cls.FMT, cls.DATE_FMT))
        logger.addHandler(console)
        # file
        if log_to_file:
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, f'{cls.LOG_FILENAME}.{cls.LOG_EXT}')  # 日志完整路径
            if file_mode == 'w' and os.path.isfile(filename):
                open(filename, 'w', encoding='utf-8').close()
            elif file_mode == 'a' and os.path.isfile(filename):
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(cls.LOG_SPLIT)
            file_hdl = logging.handlers.RotatingFileHandler(
                filename=filename,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_hdl.setFormatter(logging.Formatter(cls.FMT, cls.DATE_FMT))
            logger.addHandler(file_hdl)
        # 添加过滤器
        logger.addFilter(cls._TruncateFilter(max_msg_len))
        logger.addFilter(cls._ContextFilter(script_name))
        cls.dic_log[script_name] = logger
        return logger