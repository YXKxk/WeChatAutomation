"""
微信操作工具: 封装微信窗口操作相关功能
"""

import logging

import uiautomation as auto

from src.config.settings import (
    WECHAT_WINDOW_NAME,
    WECHAT_SEARCH_NAME,
    WECHAT_MESSAGE_LIST_NAME
)
from src.utils.decorators import ensure_thread_safe


class WeChatOperation:
    def __init__(self, contact: str):
        auto.SetGlobalSearchTimeout(15.0)
        self.contact = contact

    @ensure_thread_safe
    def find_wechat_window(self) -> auto.WindowControl:
        """查找微信主窗口"""
        wechat = auto.WindowControl(searchDepth=1, Name=WECHAT_WINDOW_NAME)
        if not wechat.Exists(3):
            raise Exception("未找到微信窗口")
        return wechat

    @ensure_thread_safe
    def find_chat_window(self, contact_name: str) -> auto.WindowControl:
        """查找并打开指定联系人的聊天窗口"""
        wechat = self.find_wechat_window()
        # 如果当前处于要搜索用户的对话页就跳过搜索操作
        edit = wechat.EditControl(Name=self.contact)
        if edit.Exists(3):
            edit.Click()
            return wechat
        # 查找搜索框
        search = wechat.EditControl(Name=WECHAT_SEARCH_NAME)
        if not search.Exists(3):
            raise Exception("未找到搜索框")

        # 搜索联系人
        search.Click()
        auto.SendKeys('{Ctrl}a')
        search.SendKeys(contact_name + '{Enter}')

        return wechat

    @ensure_thread_safe
    def get_message_list(self, window: auto.WindowControl) -> auto.ListControl:
        """获取消息列表控件"""
        msg_list = window.ListControl(Name=WECHAT_MESSAGE_LIST_NAME)
        if not msg_list.Exists(3):
            raise Exception("未找到消息列表")
        return msg_list

    @ensure_thread_safe
    def send_message(self, window: auto.WindowControl, message: str):
        """发送消息"""
        try:
            auto.SetClipboardText(message)
            auto.SendKeys('{Ctrl}v')
            auto.SendKeys('{Enter}')
            logging.debug(f"消息发送成功: {message[:20]}...")
        except Exception as e:
            logging.error(f"发送消息失败: {str(e)}")
            raise

    @ensure_thread_safe
    def get_last_message(self, window: auto.WindowControl) -> str:
        """获取最新消息"""
        msg_list = self.get_message_list(window)
        messages = msg_list.GetChildren()
        if messages:
            return messages[-1].Name
        return ""

    @ensure_thread_safe
    def get_all_messages(self, window: auto.WindowControl) -> list:
        """获取所有消息"""
        msg_list = self.get_message_list(window)
        return [msg.Name for msg in msg_list.GetChildren()]
