"""
AI对话模块: 实现与AI的自动对话功能
"""

from PyQt5.QtCore import QThread, pyqtSignal
from openai import OpenAI
import pyttsx3
from src.config.settings import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    AI_SYSTEM_PROMPT,
    THREAD_CHECK_INTERVAL
)
from src.utils.wechat import WeChatOperation
import logging
import time
from tenacity import retry, stop_after_attempt, wait_fixed

class AIChat(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, contact_name: str):
        super().__init__()
        self.contact_name = contact_name
        self.running = True
        self.last_message = ""
        self.last_ai_response = ""
        self.wechat = WeChatOperation(contact_name)

        # 初始化语音引擎
        self.voice_engine = pyttsx3.init()
        # 设置语音属性（可选）
        self.voice_engine.setProperty('rate', 180)    # 语速
        self.voice_engine.setProperty('volume', 1.0)  # 音量

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )

    def stop(self):
        """停止线程"""
        self.running = False
        self.log_signal.emit("AI对话已停止")
        # 停止语音引擎
        self.voice_engine.stop()

    def speak_text(self, text: str):
        """语音播报文本"""
        try:
            self.voice_engine.say(text)
            self.voice_engine.runAndWait()
        except Exception as e:
            self.log_signal.emit(f"语音播报错误: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_ai_response(self, message: str) -> str:
        """获取AI回复，添加重试机制"""
        try:
            # 添加请求前的延迟
            time.sleep(1.5)  # 确保请求间隔至少1.5秒

            completion = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
            )
            response = completion.choices[0].message.content
            response = response.encode('ascii', 'ignore').decode('ascii')
            return response

        except Exception as e:
            self.log_signal.emit(f"AI调用错误: {str(e)}")
            raise  # 让重试装饰器捕获异常

    def run(self):
        """线程运行函数"""
        try:
            window = self.wechat.find_chat_window(self.contact_name)
            self.log_signal.emit(f"已找到与 {self.contact_name} 的聊天窗口")

            last_request_time = 0  # 记录上次请求时间
            min_interval = 2  # 最小请求间隔（秒）

            while self.running:
                try:
                    latest_msg = self.wechat.get_last_message(window)

                    if (latest_msg and
                        latest_msg != self.last_message and
                        latest_msg != self.last_ai_response):

                        # 检查是否需要等待
                        current_time = time.time()
                        if current_time - last_request_time < min_interval:
                            wait_time = min_interval - (current_time - last_request_time)
                            time.sleep(wait_time)

                        self.log_signal.emit(f"收到新消息: {latest_msg}")

                        # 获取AI回复
                        ai_response = self.get_ai_response(latest_msg)
                        if ai_response:
                            self.wechat.send_message(window, ai_response)
                            self.log_signal.emit(f"AI回复: {ai_response}")
                            self.speak_text(ai_response)

                            self.last_message = latest_msg
                            self.last_ai_response = ai_response
                            last_request_time = time.time()  # 更新请求时间

                except Exception as e:
                    self.log_signal.emit(f"处理消息时出错: {str(e)}")

                # 增加检查间隔
                self.msleep(THREAD_CHECK_INTERVAL)

        except Exception as e:
            self.log_signal.emit(f"AI对话发生错误: {str(e)}")
