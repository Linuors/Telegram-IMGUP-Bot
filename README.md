# Telegram-IMGUP-Bot
Telegram图片上传机器人，转发到大厂非公开接口，国内CDN加速

# 介绍
- 发送图片至机器人自动上传
- 默认自带58同城、金投网、大众点评三个接口，国内CDN加速
- 支持多接口选择
- 支持URL、BBCode和Markdown格式，点击对应内容自动复制

# 演示
![image](https://image.p6y.cn/api/images/3bb94deec0f19a0de69e745d9536a842.jpg)
![image](https://image.p6y.cn/api/images/ead834cafcf6743c32a245e52a60a9d1.jpg)
测试地址：[@LinuorsBot](https://t.me/LinuorsBot)

# 部署教程
环境：Debian 12 + Python 3.9 + PIP 20.3.4

- # **第一步** 新建机器人并获取Token
Telegram搜索[@BotFather](https://t.me/BotFather)新建对话
发送命令 /newbot 开始新建机器人
![image](https://image.p6y.cn/api/images/4b9a8faac590c05cc26e32194b6e8545.jpg)
保存好获取到的API Token

- # **第二步** 调整机器人设置(可选，主要是为了设置机器人聊天时的菜单)
在@BotFather处发送命令 /mybots ，在弹出的按钮选择新建的机器人，然后点击"Edit Bot" - "Edit Commands"
发送：
```
start - 开始使用
type - 选择上传接口
help - 显示帮助信息
```
![image](https://image.p6y.cn/api/images/b4277be916b3ed35b5b67bfc548992cf.jpg)
设置完后可以在"Edit Bot" - "Edit Botpic"处设置机器人头像

- # **第三步** 安装Requests和Python-Telegram-Bot
服务器运行以下命令安装环境
```
pip install --upgrade requests python-telegram-bot
```
然后在任意目录上传main.py，在第12行填入刚才获取到的Token
**注意**：Token要全部复制上去，格式应为 Num:Key

然后执行
```
python main.py
```
如果出现以下显示则运行成功
```
root@Linuors:/www/test# python main.py
2024-11-09 15:31:17,777 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot**********:****************************************/getMe "HTTP/1.1 200 OK"
2024-11-09 15:31:17,939 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot**********:****************************************/deleteWebhook "HTTP/1.1 200 OK"
2024-11-09 15:31:17,941 - apscheduler.scheduler - INFO - Scheduler started
2024-11-09 15:31:17,941 - telegram.ext.Application - INFO - Application started
```
运行成功后把它扔后台就行
```
nohup python main.py > output.log 2>&1 &
```
或者用Systemd设置开机自启
```
sudo nano /etc/systemd/system/tgbot_imgup_service.service
```
```
[Unit]
Description=My Python Service

[Service]
ExecStart=/usr/bin/python /脚本存放的目录/main.py
WorkingDirectory=/脚本存放的目录
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
保存后执行以下命令，查看是否设置成功
**重载 systemd 管理器配置**：
```
sudo systemctl daemon-reload
```
**启动服务**：
```
sudo systemctl start tgbot_imgup_service
```
**设置开机自启**：
```
sudo systemctl enable tgbot_imgup_service
```
**检查服务状态**：
```
sudo systemctl status tgbot_imgup_service
```
