# WeChatAutomation

#### 介绍

一个基于 PyQt5 和 uiautomation 的微信自动化助手，提供图形界面操作，帮助用户自动化处理微信相关任务。

#### 软件架构
WeChatAutomation/
├── src/ # 源代码目录
│ ├── core/ # 核心功能模块
│ │ ├── init.py
│ │ ├── ai_chat.py # AI对话功能
│ │ ├── analytics.py # 数据统计功能
│ │ ├── auto_reply.py # 自动回复功能
│ │ ├── backup.py # 聊天记录备份
│ │ ├── mass_sender.py # 群发消息功能
│ │ └── monitor.py # 关键词监控功能
│ ├── ui/ # 界面相关
│ │ ├── init.py
│ │ ├── main_window.py # 主窗口
│ │ └── resources/ # UI资源文件
│ ├── utils/ # 工具类
│ │ ├── init.py
│ │ ├── decorators.py # 装饰器工具
│ │ ├── themes.py # 主题管理
│ │ └── wechat.py # 微信操作工具
│ ├── config/ # 配置文件
│ │ └── settings.py # 全局配置
│ └── main.py # 程序入口
#### 功能特点

1. AI对话功能
   - 基于 OpenAI API 的智能对话
   - 支持语音播报回复内容
   - 自定义系统提示词
   - 自动重试机制
   - 请求频率限制
2. 自动回复功能
   - 定时回复设置
   - 自定义回复内容
   - 支持无限循环
   - 时间段控制
   - 间隔时间设置
3. 群发消息功能
   - 批量发送消息
   - 进度显示
   - 支持中断操作
   - 发送状态日志
   - 联系人管理
4. 数据统计功能
   - 消息数量统计
   - 消息类型分析
   - 活跃度分析
   - 导出统计结果
   - 实时更新
5. 关键词监控
   - 多联系人监控
   - 关键词告警
   - 实时通知
   - 监控日志记录
   - 自定义关键词
6. 聊天记录备份
   - 导出聊天记录
   - 自动命名保存
   - 进度显示
   - 备份日志
   - 文件管理
7. 系统功能
   - 深色/浅色主题切换

#### 安装教程

1. 环境准备

   ​- configs/settngs中OPENAI_API_KEY = ""替换自己的 OpenAI API Key

   - 安装 Python 3.8 或更高版本
     pip install openai PyQt5 uiautomation pyttsx3 tenacity

#### 特别说明

1. 使用须知
   - 本项目仅供学习交流使用
   - 请勿用于非法用途
   - 遵守微信相关规则

2. 免责声明
   - 使用本软件造成的任何问题由使用者承担
   - 不对任何损失负责
   - 请合理使用自动化功能

✅️️ 打赏作者
作者是个人开发者，开发和写文档工作量繁重。

如果本项目对您有所帮助，不妨打赏一下 :)

<img src="./assets/支付宝收钱.jpg" style="zoom:20%;" />	<img src="./assets/微信收钱.jpg" style="zoom:20%;" />


#### 许可证

本项目采用 MIT 许可证