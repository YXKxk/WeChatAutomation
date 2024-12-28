"""
程序入口: 启动应用程序
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import ChatAutomationApp
import logging

def main():
    # 设置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wechat_automation.log'),
            logging.StreamHandler()
        ]
    )

    # 启动应用
    app = QApplication(sys.argv)
    window = ChatAutomationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
