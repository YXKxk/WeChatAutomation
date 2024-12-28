"""
群发消息模块: 实现批量发送消息功能
"""

from PyQt5.QtCore import QThread, pyqtSignal
from ..utils.wechat import WeChatOperation
import logging

class MassSender(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, contacts: list, message: str):
        super().__init__()
        self.contacts = contacts
        self.message = message
        self.running = True
        self.wechat = WeChatOperation(contacts[0])

    def stop(self):
        """停止发送"""
        self.running = False
        self.log_signal.emit("群发消息已停止")

    def run(self):
        """线程运行函数"""
        try:
            self.log_signal.emit("开始群发消息")
            total = len(self.contacts)

            for i, contact in enumerate(self.contacts):
                if not self.running:
                    break

                try:
                    # 查找并打开聊天窗口
                    window = self.wechat.find_chat_window(contact)

                    # 发送消息
                    self.wechat.send_message(window, self.message)

                    # 更新进度
                    progress = int((i + 1) / total * 100)
                    self.progress_signal.emit(progress)
                    self.log_signal.emit(f"已发送给 {contact} ({i + 1}/{total})")

                except Exception as e:
                    self.log_signal.emit(f"发送给 {contact} 失败: {str(e)}")

                # 短暂延时，避免发送过快
                if self.running and i < total - 1:
                    self.msleep(1000)

            self.log_signal.emit("群发消息完成")

        except Exception as e:
            self.log_signal.emit(f"群发消息发生错误: {str(e)}")

        finally:
            self.finished_signal.emit()
