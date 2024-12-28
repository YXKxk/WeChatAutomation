"""
定时回复模块: 实现在指定时间段自动回复功能
"""

from PyQt5.QtCore import QThread, pyqtSignal, QTime
from ..utils.wechat import WeChatOperation
import logging

class AutoReply(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, contact: str, message: str, start_time: QTime, end_time: QTime,
                 repeat_count: int = 1, interval: int = 5):
        super().__init__()
        self.contact = contact
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.repeat_count = repeat_count
        self.interval = interval
        self.running = True
        self.wechat = WeChatOperation(contact)

    def stop(self):
        """停止自动回复"""
        self.running = False
        self.log_signal.emit("自动回复已停止")

    def is_valid_time(self) -> bool:
        """检查当前时间是否在有效时间段内"""
        current_time = QTime.currentTime()
        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        else:  # 跨越午夜的情况
            return current_time <= self.end_time or current_time >= self.start_time

    def run(self):
        """线程运行函数"""
        try:
            self.log_signal.emit(f"开始自动回复 - {self.contact}")
            count = 0

            while self.running and (self.repeat_count == -1 or count < self.repeat_count):
                if not self.is_valid_time():
                    self.msleep(1000)
                    continue

                try:
                    # 每次都重新获取窗口，不保存引用
                    window = self.wechat.find_chat_window(self.contact)
                    # 发送消息
                    self.wechat.send_message(window, self.message)
                    count += 1
                    self.log_signal.emit(f"已发送 ({count}): {self.message}")
                    # 释放窗口引用
                    window = None

                    # 等待指定间隔
                    if self.running and (self.repeat_count == -1 or count < self.repeat_count):
                        self.msleep(self.interval * 1000)

                except Exception as e:
                    self.log_signal.emit(f"发送消息时出错: {str(e)}")
                    self.msleep(1000)  # 出错时短暂等待
                    continue

        except Exception as e:
            self.log_signal.emit(f"自动回复发生错误: {str(e)}")

        finally:
            self.log_signal.emit("自动回复已完成")
            self.finished_signal.emit()
