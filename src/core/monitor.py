"""
关键词监控模块: 实现对指定联系人消息的关键词监控
"""

from PyQt5.QtCore import QThread, pyqtSignal
from ..utils.wechat import WeChatOperation
from ..config.settings import MONITOR_CHECK_INTERVAL
import logging
from datetime import datetime

class KeywordMonitor(QThread):
    alert_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, keywords: list, contacts: list):
        super().__init__()
        self.keywords = keywords
        self.contacts = contacts
        self.running = True
        self.wechat = WeChatOperation(contacts[0])
        self.last_messages = {contact: "" for contact in contacts}

    def stop(self):
        """停止监控"""
        self.running = False
        self.log_signal.emit("关键词监控已停止")

    def check_keywords(self, message: str) -> list:
        """检查消息中的关键词"""
        found_keywords = []
        for keyword in self.keywords:
            if keyword in message:
                found_keywords.append(keyword)
        return found_keywords

    def format_alert(self, contact: str, message: str, keywords: list) -> str:
        """格式化告警消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (f"[{timestamp}] 检测到关键词\n"
                f"联系人: {contact}\n"
                f"关键词: {', '.join(keywords)}\n"
                f"消息内容: {message}\n")

    def run(self):
        """线程运行函数"""
        try:
            self.log_signal.emit("开始关键词监控...")
            self.log_signal.emit(f"监控联系人: {', '.join(self.contacts)}")
            self.log_signal.emit(f"监控关键词: {', '.join(self.keywords)}")


            while self.running:
                for contact in self.contacts:
                    if not self.running:
                        break

                    try:
                        # 查找并切换到联系人窗口
                        window = self.wechat.find_chat_window(contact)

                        # 获取最新消息
                        latest_msg = self.wechat.get_last_message(window)

                        # 检查是否是新消息
                        if latest_msg and latest_msg != self.last_messages[contact]:
                            # 检查关键词
                            found_keywords = self.check_keywords(latest_msg)

                            if found_keywords:
                                # 发送告警信息
                                alert = self.format_alert(contact, latest_msg, found_keywords)
                                self.alert_signal.emit(alert)

                            self.last_messages[contact] = latest_msg

                    except Exception as e:
                        self.log_signal.emit(f"监控 {contact} 时出错: {str(e)}")

                    # 短暂延时，避免频繁切换窗口
                    self.msleep(1000)

                # 监控间隔
                self.msleep(MONITOR_CHECK_INTERVAL)

        except Exception as e:
            self.log_signal.emit(f"关键词监控发生错误: {str(e)}")
