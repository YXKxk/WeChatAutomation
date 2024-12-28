"""
数据统计模块: 实现聊天记录的数据分析
"""

from PyQt5.QtCore import QThread, pyqtSignal
import pythoncom
import uiautomation as auto
import logging

class ChatAnalytics(QThread):
    """聊天数据统计线程"""
    log_signal = pyqtSignal(str)
    update_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()  # 添加完成信号

    def __init__(self, contact: str):
        super().__init__()
        self.contact = contact
        self.running = True

    def stop(self):
        """停止统计"""
        self.running = False
        self.log_signal.emit("正在停止数据统计...")

    def run(self):
        """执行数据统计"""
        pythoncom.CoInitialize()
        try:
            stats = {
                "total_messages": 0,
                "message_types": {},
                "activity": {
                    "total_messages": 0,
                    "avg_length": 0,
                    "max_length": 0
                }
            }

            self.log_signal.emit(f"开始统计 {self.contact} 的聊天数据...")
            wechat = auto.WindowControl(searchDepth=1, Name='微信')

            if not wechat.Exists(3):
                self.log_signal.emit("未找到微信窗口")
                return

            search = wechat.EditControl(Name='搜索')
            if search.Exists(3):
                search.Click()
                auto.SendKeys('{Ctrl}a')
                search.SendKeys(self.contact + '{Enter}')

                msg_list = wechat.ListControl(Name='消息')
                if msg_list.Exists(3):
                    messages = msg_list.GetChildren()
                    total_length = 0
                    max_length = 0

                    for msg in messages:
                        if not self.running:
                            break

                        msg_text = msg.Name
                        msg_length = len(msg_text)
                        total_length += msg_length
                        max_length = max(max_length, msg_length)

                        if "[图片]" in msg_text:
                            stats["message_types"]["图片"] = stats["message_types"].get("图片", 0) + 1
                        elif "[表情]" in msg_text:
                            stats["message_types"]["表情"] = stats["message_types"].get("表情", 0) + 1
                        else:
                            stats["message_types"]["文本"] = stats["message_types"].get("文本", 0) + 1

                    stats["total_messages"] = len(messages)
                    stats["activity"]["total_messages"] = len(messages)
                    stats["activity"]["avg_length"] = total_length / len(messages) if messages else 0
                    stats["activity"]["max_length"] = max_length

                    self.update_signal.emit(stats)
                    self.log_signal.emit("数据统计完成")
                else:
                    self.log_signal.emit("未找到消息列表")
            else:
                self.log_signal.emit("未找到搜索框")

        except Exception as e:
            self.log_signal.emit(f"统计过程出错: {str(e)}")
            logging.error(f"数据统计错误: {str(e)}")

        finally:
            pythoncom.CoUninitialize()
            self.finished_signal.emit()  # 发送完成信号
