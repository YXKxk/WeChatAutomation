"""
主窗口类: 实现主界面和所有功能的控制逻辑
"""

import logging
import os

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QLabel, QTextEdit, QLineEdit, QPushButton, QComboBox
from PyQt5.uic import loadUi

from src.config.settings import (
    UI_FILE_PATH,
    DEFAULT_AUTO_REPLY_START_TIME,
    DEFAULT_AUTO_REPLY_END_TIME
)
from src.core.ai_chat import AIChat
from src.core.analytics import ChatAnalytics
from src.core.auto_reply import AutoReply
from src.core.backup import ChatBackup
from src.core.mass_sender import MassSender
from src.core.monitor import KeywordMonitor
from src.utils.decorators import handle_ui_exception


class ChatAutomationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.threads = {
            'auto_reply': None,
            'mass_sender': None,
            'ai_chat': None,
            'analytics': None,
            'monitor': None,
            'backup': None
        }
        self.setupThreads()
        self.connect_signals()
        self.setup_logging()

    @handle_ui_exception
    def init_ui(self):
        """初始化UI"""
        try:
            loadUi(UI_FILE_PATH, self)

            # 立即验证主题选择器
            self.themeSelector = self.findChild(QComboBox, "themeSelector")
            if not self.themeSelector:
                logging.error("找不到主题选择器控件")
                raise ValueError("找不到主题选择器控件")
            logging.info("成功找到主题选择器")

            # 直接在这里连接信号
            self.themeSelector.currentIndexChanged.connect(self.on_theme_changed)

            self.setup_default_values()

            # 查找或创建状态标签
            self.status_reply = self.findChild(QLabel, "status_reply")
            self.status_ai = self.findChild(QLabel, "status_ai")
            self.status_mass = self.findChild(QLabel, "status_mass")
            self.status_analytics = self.findChild(QLabel, "status_analytics")

            # 查找数据统计相关控件
            self.analytics_log = self.findChild(QTextEdit, "analytics_log")
            self.analytics_contact = self.findChild(QLineEdit, "analytics_contact")
            self.btn_analyze = self.findChild(QPushButton, "btn_analyze")

            # 如果找不到则创建
            if not self.status_analytics:
                self.status_analytics = QLabel("就绪")
                self.tab_analytics.layout().addWidget(self.status_analytics)

            if not self.analytics_log:
                self.analytics_log = QTextEdit()
                self.analytics_log.setReadOnly(True)
                self.tab_analytics.layout().addWidget(self.analytics_log)

            if not self.analytics_contact:
                self.analytics_contact = QLineEdit()
                self.analytics_contact.setPlaceholderText("请输入联系人")
                self.tab_analytics.layout().addWidget(self.analytics_contact)

        except Exception as e:
            logging.error(f"加载UI文件失败: {str(e)}")
            raise

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setupThreads(self):
        """初始化线程"""
        # 预创建线程对象
        self.threads['auto_reply'] = None
        self.threads['mass_sender'] = None
        self.threads['ai_chat'] = None

    def setup_default_values(self):
        """设置默认值"""
        # 设置默认时间
        start_time = QTime.fromString(DEFAULT_AUTO_REPLY_START_TIME, "HH:mm")
        end_time = QTime.fromString(DEFAULT_AUTO_REPLY_END_TIME, "HH:mm")
        self.time_start.setTime(start_time)
        self.time_end.setTime(end_time)

        # 设置进度条初始值
        self.progress_bar.setValue(0)
        self.backup_progress.setValue(0)

    def connect_signals(self):
        """连接信号槽"""
        # AI对话标签页
        self.btn_start.clicked.connect(self.toggle_ai_chat)

        # 群发消息标签页
        self.btn_send_mass.clicked.connect(self.start_mass_message)

        # 定时回复标签页
        self.btn_auto_reply.clicked.connect(self.toggle_auto_reply)

        # 聊天备份标签页
        self.btn_select_path.clicked.connect(self.select_backup_path)
        self.btn_backup.clicked.connect(self.start_backup)

        # 关键词监控标签页
        self.btn_monitor.clicked.connect(self.toggle_monitor)

        # 数据统计标签页
        self.btn_analyze.clicked.connect(self.start_analytics)

        # 群发消息相关信号
        self.btn_add_contact.clicked.connect(self.add_contact)
        self.btn_remove_contact.clicked.connect(self.remove_selected_contacts)
        self.btn_clear_contacts.clicked.connect(self.clear_contacts)
        self.edit_contact.returnPressed.connect(self.add_contact)  # 支持回车添加

    @handle_ui_exception
    def toggle_ai_chat(self, checked=None):
        """切换AI对话状态"""
        if self.threads['ai_chat'] and self.threads['ai_chat'].isRunning():
            self.threads['ai_chat'].stop()
            self.btn_start.setText("启动")
            self.edit_name.setEnabled(True)
            self.status_ai.setText("AI对话已停止")
        else:
            contact = self.edit_name.text().strip()
            if not contact:
                raise ValueError("请输入联系人")

            self.threads['ai_chat'] = AIChat(contact)
            self.threads['ai_chat'].log_signal.connect(self.text_area.append)
            self.threads['ai_chat'].start()

            self.btn_start.setText("停止")
            self.edit_name.setEnabled(False)
            self.status_ai.setText(f"AI对话运行中 - {contact}")

    @handle_ui_exception
    def start_mass_message(self, checked=None):
        """开始群发消息"""
        if self.threads['mass_sender'] and self.threads['mass_sender'].isRunning():
            self.threads['mass_sender'].stop()
            self.btn_send_mass.setText("开始发送")
            self.enable_mass_inputs(True)
            self.status_mass.setText("群发消息已停止")
            return

        contacts = [
            self.list_contacts.item(i).text()
            for i in range(self.list_contacts.count())
        ]
        message = self.message_content.toPlainText().strip()

        if not contacts:
            raise ValueError("请添加至少一个联系人")
        if not message:
            raise ValueError("请输入消息内容")

        self.threads['mass_sender'] = MassSender(
            contacts=contacts,
            message=message
        )

        self.threads['mass_sender'].progress_signal.connect(self.progress_bar.setValue)
        self.threads['mass_sender'].log_signal.connect(self.mass_log_area.append)
        self.threads['mass_sender'].finished_signal.connect(self.on_mass_message_finished)

        self.btn_send_mass.setText("停止发送")
        self.enable_mass_inputs(False)
        self.status_mass.setText("群发消息运行中...")

        self.threads['mass_sender'].start()

    def enable_mass_inputs(self, enabled: bool):
        """启用/禁用群发消息的输入控件"""
        self.edit_contact.setEnabled(enabled)
        self.btn_add_contact.setEnabled(enabled)
        self.btn_remove_contact.setEnabled(enabled)
        self.btn_clear_contacts.setEnabled(enabled)
        self.list_contacts.setEnabled(enabled)
        self.message_content.setEnabled(enabled)

    def on_checkbox_infinite_changed(self, state):
        """处理无限次数复选��状态改变"""
        self.spinBox_repeat.setEnabled(not state)

    @handle_ui_exception
    def toggle_auto_reply(self, checked=None):
        """切换定时回复状态"""
        if self.threads['auto_reply'] and self.threads['auto_reply'].isRunning():
            self.threads['auto_reply'].stop()
            self.btn_auto_reply.setText("启动定时回复")
            self.enable_auto_reply_inputs(True)
            self.status_reply.setText("定时回复已停止")
            self.threads['auto_reply'].wait()
            self.threads['auto_reply'] = None
            return

        # 获取输入
        contact = self.auto_reply_contact.text().strip()
        message = self.auto_reply_content.toPlainText().strip()
        start_time = self.time_start.time()
        end_time = self.time_end.time()

        # 验证输入
        if not contact or not message:
            raise ValueError("请输入联系人和回复内容")

        # 获取回复设置
        is_infinite = self.checkBox_infinite_reply.isChecked()
        repeat_count = -1 if is_infinite else self.spinBox_reply_count.value()
        interval = self.spinBox_reply_interval.value()

        # 创建并启动线程
        self.threads['auto_reply'] = AutoReply(
            contact=contact,
            message=message,
            start_time=start_time,
            end_time=end_time,
            repeat_count=repeat_count,
            interval=interval
        )

        # 连接信号
        self.threads['auto_reply'].log_signal.connect(self.auto_reply_log.append)
        self.threads['auto_reply'].finished_signal.connect(self.on_auto_reply_finished)

        # 更新UI状态
        self.btn_auto_reply.setText("停止定时回复")
        self.enable_auto_reply_inputs(False)
        self.status_reply.setText("定时回复运行中...")

        # 启动线程
        self.threads['auto_reply'].start()

    def enable_auto_reply_inputs(self, enabled: bool):
        """启用/禁用定时回复的输入控件"""
        self.auto_reply_contact.setEnabled(enabled)
        self.auto_reply_content.setEnabled(enabled)
        self.time_start.setEnabled(enabled)
        self.time_end.setEnabled(enabled)
        self.spinBox_reply_count.setEnabled(enabled and not self.checkBox_infinite_reply.isChecked())
        self.checkBox_infinite_reply.setEnabled(enabled)
        self.spinBox_reply_interval.setEnabled(enabled)

    def on_checkbox_infinite_reply_changed(self, state):
        """处理无限次数复选框状态改变"""
        if self.auto_reply_contact.isEnabled():  # 只在未运行时改变状态
            self.spinBox_reply_count.setEnabled(not state)

    @handle_ui_exception
    def select_backup_path(self, checked=None):
        """选择备份保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if path:
            self.backup_path = path
            self.btn_select_path.setText(f"已选择: {os.path.basename(path)}")
            self.status_bar.setText(f"已选择备份保存路径: {path}")

    @handle_ui_exception
    def start_backup(self, checked=None):
        """开始备份聊天记录"""
        if not hasattr(self, 'backup_path'):
            raise ValueError("请先选择保存路径")

        contact = self.backup_contact.text().strip()
        if not contact:
            raise ValueError("请输入要备份的联系人")

        self.threads['backup'] = ChatBackup(contact, self.backup_path)
        self.threads['backup'].progress_signal.connect(self.backup_progress.setValue)
        self.threads['backup'].log_signal.connect(self.backup_log.append)
        self.threads['backup'].finished_signal.connect(self.on_backup_finished)

        self.btn_backup.setEnabled(False)
        self.backup_contact.setEnabled(False)
        self.btn_select_path.setEnabled(False)
        self.status_bar.setText(f"正在备份 {contact} 的聊天记录...")

        self.threads['backup'].start()

    @handle_ui_exception
    def toggle_monitor(self, checked=None):
        """切换关键词监控状态"""
        if self.threads['monitor'] and self.threads['monitor'].isRunning():
            self.threads['monitor'].stop()
            self.btn_monitor.setText("开启监控")
            self.monitor_contact.setEnabled(True)
            self.keywords_list.setEnabled(True)
            self.status_monitor.setText("关键词监控已停止")
        else:
            # 先获取联系人
            contact = self.monitor_contact.text().strip()
            # 再获取关键词列表
            keywords = self.keywords_list.toPlainText().strip().split('\n')

            if not contact or not keywords:
                raise ValueError("请输入联系人和关键词")

            # 创建监控线程时，先传入关键词列表，再传入联系人列表
            self.threads['monitor'] = KeywordMonitor(keywords, [contact])  # 修改参数顺序
            self.threads['monitor'].alert_signal.connect(self.monitor_log.append)
            self.threads['monitor'].log_signal.connect(self.monitor_log.append)

            self.btn_monitor.setText("停止监控")
            self.monitor_contact.setEnabled(False)
            self.keywords_list.setEnabled(False)
            self.status_monitor.setText("关键词监控运行中...")

            self.threads['monitor'].start()

    @handle_ui_exception
    def start_analytics(self, checked=None):
        """开始/停止数据统计"""
        if self.threads['analytics'] and self.threads['analytics'].isRunning():
            self.threads['analytics'].stop()
            self.btn_analyze.setText("开始统计")
            self.enable_analytics_inputs(True)
            self.status_analytics.setText("��据统计已停止")
            self.threads['analytics'].wait()
            self.threads['analytics'] = None
            return

        contact = self.analytics_contact.text().strip()
        if not contact:
            raise ValueError("请输入联系人")

        self.threads['analytics'] = ChatAnalytics(contact)
        self.threads['analytics'].log_signal.connect(self.analytics_log.append)
        self.threads['analytics'].update_signal.connect(self.update_analytics_data)
        self.threads['analytics'].finished_signal.connect(self.on_analytics_finished)

        self.btn_analyze.setText("停止统计")
        self.enable_analytics_inputs(False)
        self.status_analytics.setText("数据统计运行中...")

        self.threads['analytics'].start()

    def on_analytics_finished(self):
        """数据统计完成的回调"""
        if self.threads['analytics']:
            self.btn_analyze.setText("开始统计")
            self.enable_analytics_inputs(True)
            self.status_analytics.setText("数据统计已完成")
            try:
                self.threads['analytics'].log_signal.disconnect()
                self.threads['analytics'].update_signal.disconnect()
                self.threads['analytics'].finished_signal.disconnect()
            except:
                pass
            self.threads['analytics'].deleteLater()
            self.threads['analytics'] = None

    def enable_analytics_inputs(self, enabled: bool):
        """启用/禁用数据统计输入控件"""
        if hasattr(self, 'analytics_contact'):
            self.analytics_contact.setEnabled(enabled)
        if hasattr(self, 'btn_analyze'):
            self.btn_analyze.setEnabled(enabled)

    def update_analytics_data(self, data: dict):
        """更新数据统计结果"""
        try:
            if 'error' in data:
                self.analytics_log.append(f"错误: {data['error']}")
                return

            # 格式化统计数据
            self.analytics_log.append("\n=== 统计结果 ===")

            # 消息类型统计
            if 'message_types' in data:
                self.analytics_log.append("\n消息类型分布:")
                for msg_type, count in data['message_types'].items():
                    self.analytics_log.append(f"{msg_type}: {count}")

            # 活跃度统计
            if 'activity' in data:
                self.analytics_log.append("\n活跃度统计:")
                activity = data['activity']
                self.analytics_log.append(f"总消息数: {activity['total_messages']}")
                self.analytics_log.append(f"平均长��: {activity['avg_length']:.2f}")
                self.analytics_log.append(f"最长消息: {activity['max_length']}")

            # 时间戳
            if 'timestamp' in data:
                self.analytics_log.append(f"\n统计时间: {data['timestamp']}")

        except Exception as e:
            logging.error(f"更新数据统计结果时出错: {str(e)}")
            self.analytics_log.append(f"更新数据时出错: {str(e)}")

    def on_mass_message_finished(self):
        """群发消息完成回调"""
        try:
            self.btn_send_mass.setText("开始发送")
            self.enable_mass_inputs(True)
            self.status_mass.setText("群发消息已完成")
            self.progress_bar.setValue(0)

            # 确保线程正确清理
            if self.threads['mass_sender']:
                self.threads['mass_sender'].quit()
                self.threads['mass_sender'].wait()
                self.threads['mass_sender'] = None

        except Exception as e:
            logging.error(f"群发消息完成处理出错: {str(e)}")

    def on_auto_reply_finished(self):
        """自动回复完成的回调"""
        if self.threads['auto_reply']:
            self.btn_auto_reply.setText("启动定时回复")
            self.enable_auto_reply_inputs(True)
            self.status_reply.setText("定时回复已完成")
            try:
                self.threads['auto_reply'].log_signal.disconnect()
                self.threads['auto_reply'].finished_signal.disconnect()
            except:
                pass
            self.threads['auto_reply'].deleteLater()
            self.threads['auto_reply'] = None

    def on_backup_finished(self):
        """备份完成回调"""
        self.btn_backup.setEnabled(True)
        self.backup_contact.setEnabled(True)
        self.btn_select_path.setEnabled(True)
        self.backup_progress.setValue(0)
        self.status_bar.setText("聊天记录备份已完成")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止所有运行中的线程
        for thread_name, thread in self.threads.items():
            if thread and thread.isRunning():
                thread.stop()
                thread.wait()
                try:
                    thread.log_signal.disconnect()
                    if hasattr(thread, 'update_signal'):
                        thread.update_signal.disconnect()
                    thread.finished_signal.disconnect()
                except:
                    pass
                thread.deleteLater()
                self.threads[thread_name] = None
        event.accept()

    @handle_ui_exception
    def add_contact(self, checked=None):
        """添加联系人到列表"""
        contact = self.edit_contact.text().strip()
        if not contact:
            return

        # existing_items = [
        #     self.list_contacts.item(i).text()
        #     for i in range(self.list_contacts.count())
        # ]
        # if contact in existing_items:
        #     QMessageBox.warning(self, "提示", "联系人已在列表中")
        #     return

        self.list_contacts.addItem(contact)
        self.edit_contact.clear()
        self.status_mass.setText(f"已添加联系人：{contact}")

    @handle_ui_exception
    def remove_selected_contacts(self, checked=None):
        """删除选中的联系人"""
        selected_items = self.list_contacts.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.list_contacts.takeItem(self.list_contacts.row(item))

        self.status_mass.setText("已删除选中的联系人")

    @handle_ui_exception
    def clear_contacts(self, checked=None):
        """清空联系人列表"""
        if self.list_contacts.count() == 0:
            return

        reply = QMessageBox.question(
            self, "确认", "确定要清空联系人列表吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.list_contacts.clear()
            self.status_mass.setText("已清空联系人列表")

    def on_ai_chat_finished(self):
        """AI对话完成的回调"""
        if self.threads['ai_chat']:
            self.btn_start_ai.setText("开始对话")
            self.enable_ai_inputs(True)
            self.status_ai.setText("AI对话已完成")
            # ... 其他清理代码 ...

    def on_mass_sender_finished(self):
        """群发完成的回调"""
        if self.threads['mass_sender']:
            self.btn_start_mass.setText("开始发送")
            self.enable_mass_inputs(True)
            self.status_mass.setText("群发消息已完成")

    def on_theme_changed(self, index):
        """处理主题切换"""
        try:
            logging.info(f"正在切换主题，选择的索引: {index}")

            if index == 1:  # 深色主题
                logging.info("正在应用深色主题")
                style = """
                    QWidget {
                        background-color: #2D2D2D;
                        color: #FFFFFF;
                    }
                    QPushButton {
                        background-color: #0D47A1;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px;
                    }
                    QLineEdit, QTextEdit {
                        background-color: #424242;
                        color: white;
                        border: 1px solid #616161;
                        padding: 4px;
                    }
                    QLabel[objectName*="status_"] {
                        background-color: #424242;
                        color: white;
                        border: 1px solid #616161;
                        padding: 4px;
                    }
                    QTabWidget::pane {
                        border: 1px solid #616161;
                        background-color: #2D2D2D;
                        margin: 0px;
                        padding: 0px;
                    }
                    QTabWidget {
                        background-color: #2D2D2D;
                        min-height: 500px;
                    }
                    QTabBar::tab {
                        background-color: #424242;
                        color: white;
                        border: 1px solid #616161;
                        padding: 6px 16px;
                        margin: 0px;
                    }
                    QTabBar::tab:selected {
                        background-color: #2D2D2D;
                    }
                    QGroupBox {
                        border: 1px solid #616161;
                        margin-top: 6px;
                        padding-top: 6px;
                    }
                    QComboBox {
                        background-color: #424242;
                        color: white;
                        border: 1px solid #616161;
                        padding: 4px;
                    }
                """
            else:  # 浅色主题
                logging.info("正在应用浅色主题")
                style = """
                    QWidget {
                        background-color: white;
                        color: black;
                    }
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px;
                    }
                    QLineEdit, QTextEdit {
                        background-color: white;
                        color: black;
                        border: 1px solid #BDBDBD;
                        padding: 4px;
                    }
                    QLabel[objectName*="status_"] {
                        background-color: #F5F5F5;
                        color: black;
                        border: 1px solid #BDBDBD;
                        padding: 4px;
                    }
                    QTabWidget::pane {
                        border: 1px solid #BDBDBD;
                        background-color: white;
                        margin: 0px;
                        padding: 0px;
                    }
                    QTabWidget {
                        background-color: white;
                        min-height: 500px;
                    }
                    QTabBar::tab {
                        background-color: #F5F5F5;
                        color: black;
                        border: 1px solid #BDBDBD;
                        padding: 6px 16px;
                        margin: 0px;
                    }
                    QTabBar::tab:selected {
                        background-color: white;
                    }
                    QGroupBox {
                        border: 1px solid #BDBDBD;
                        margin-top: 6px;
                        padding-top: 6px;
                    }
                    QComboBox {
                        background-color: white;
                        color: black;
                        border: 1px solid #BDBDBD;
                        padding: 4px;
                    }
                """

            # 应用样式
            self.setStyleSheet(style)

            # 强制刷新
            self.repaint()

            # 记录主题切换完成
            theme_name = "深色" if index == 1 else "浅色"
            logging.info(f"主题切换完成: {theme_name}")

        except Exception as e:
            logging.error(f"主题切换失败: {str(e)}")
            raise
