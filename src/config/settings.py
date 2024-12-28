"""
配置文件: 存储全局配置和常量
"""

import os

# 获取当前文件所在目录的父目录（src目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# OpenAI API配置
OPENAI_API_KEY = ""
OPENAI_BASE_URL = "https://api.moonshot.cn/v1"
OPENAI_MODEL = "moonshot-v1-8k"

# AI系统提示词
AI_SYSTEM_PROMPT = """你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。
你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。
Moonshot AI 为专有名词，不可翻译成其他语言,不要发情，不要发乱码的表情包。"""

# 微信自动化配置
WECHAT_WINDOW_NAME = "微信"
WECHAT_SEARCH_NAME = "搜索"
WECHAT_MESSAGE_LIST_NAME = "消息"

# 默认配置
DEFAULT_AUTO_REPLY_START_TIME = "09:00"
DEFAULT_AUTO_REPLY_END_TIME = "18:00"
DEFAULT_TEST_CONTACT = "文件传输助手"

# 线程配置
THREAD_CHECK_INTERVAL = 2000  # 消息检查间隔(毫秒)
MONITOR_CHECK_INTERVAL = 5000  # 监控检查间隔(毫秒)

# UI文件路径
UI_FILE_PATH = os.path.join(BASE_DIR, 'ui', 'resources', 'chat_automation.ui')
