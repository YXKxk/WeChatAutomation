"""
聊天记录备份模块: 实现聊天记录的导出和保存
"""

from PyQt5.QtCore import QThread, pyqtSignal
from ..utils.wechat import WeChatOperation
import os
from datetime import datetime
import json
import logging

class ChatBackup(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, contact_name: str, save_path: str):
        super().__init__()
        self.contact_name = contact_name
        self.save_path = save_path
        self.running = True
        self.wechat = WeChatOperation(contact_name)

    def stop(self):
        """停止备份"""
        self.running = False
        self.log_signal.emit("备份已停止")

    def get_backup_filename(self) -> str:
        """生成备份文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_backup_{self.contact_name}_{timestamp}.txt"
        return os.path.join(self.save_path, filename)

    def save_messages(self, messages: list, filepath: str):
        """保存消息到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== 与 {self.contact_name} 的聊天记录 ===\n")
                f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for msg in messages:
                    f.write(f"{msg}\n")

            self.log_signal.emit(f"聊天记录已保存到: {filepath}")

        except Exception as e:
            self.log_signal.emit(f"保存文件失败: {str(e)}")
            raise

    def run(self):
        """线程运行函数"""
        try:
            # 查找聊天窗口
            window = self.wechat.find_chat_window(self.contact_name)
            self.log_signal.emit("正在获取聊天记录...")

            # 获取所有消息
            messages = self.wechat.get_all_messages(window)
            total_messages = len(messages)

            if total_messages == 0:
                self.log_signal.emit("未找到聊天记录")
                return

            self.log_signal.emit(f"共找到 {total_messages} 条消息")

            # 生成备份文件路径
            backup_file = self.get_backup_filename()

            # 保存消息
            self.save_messages(messages, backup_file)

            self.progress_signal.emit(100)
            self.log_signal.emit("备份完成")

        except Exception as e:
            self.log_signal.emit(f"备份过程发生错误: {str(e)}")

        finally:
            self.finished_signal.emit()
