"""
装饰器工具: 提供通用的装饰器函数
"""

from functools import wraps
from PyQt5.QtWidgets import QMessageBox
import pythoncom
import logging

def handle_ui_exception(func):
    """处理UI操作异常的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"UI操作错误: {str(e)}")
            QMessageBox.warning(None, "错误", str(e))
    return wrapper

def ensure_thread_safe(func):
    """确保线程安全的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            pythoncom.CoInitialize()
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"线程操作错误: {str(e)}")
            raise e
        finally:
            pythoncom.CoUninitialize()
    return wrapper

def log_function_call(func):
    """记录函数调用的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug(f"调用函数: {func.__name__}")
        result = func(*args, **kwargs)
        logging.debug(f"函数 {func.__name__} 执行完成")
        return result
    return wrapper