import logging
import requests
import os
import base64
import json
import hashlib
from random import randint
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 填写你的TG机器人Token
TELEGRAM_BOT_TOKEN = ''

# 图床配置
image_hosts = {
    'jtw': {
        'name': '金投网',
        'upload_function': 'upload_to_jtw',
    },
    'dzdp': {
        'name': '大众点评',
        'upload_function': 'upload_to_dzdp',
    },
    '58tc': {
        'name': '58同城',
        'upload_function': 'upload_to_58tc',
    },
}

# 默认上传图床
current_endpoint = 'jtw'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 金投网
def upload_to_jtw(photo_path):
    url = 'https://feedback.cngold.org/img/upload.htm'
    with open(photo_path, 'rb') as f:
        files = {'imgFile': f}
        response = requests.post(url, files=files)
        responsed = response.json()

    if responsed.get('code') == 0:
        return {'code': 200, 'url': 'https://res.cngoldres.com' + responsed['data']}
    else:
        return {'code': 400, 'msg': 'Upload Failed.'}

# 大众点评
def upload_to_dzdp(photo_path):
    url = 'https://trust.dianping.com/upload.action'
    new_file_name = hashlib.md5(os.urandom(16)).hexdigest() + '.' + os.path.splitext(photo_path)[1][1:]

    with open(photo_path, 'rb') as f:
        files = {
            'file': (new_file_name, f, 'application/octet-stream')
        }
        data = {'name': new_file_name}
        response = requests.post(url, files=files, data=data)
        responseData = response.json()

    if 'isSuccess' in responseData and responseData['isSuccess']:
        url = responseData['url']
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        return {'code': 200, 'url': url}
    else:
        return {'code': 400, 'msg': 'Upload Failed.'}

# 58同城
def upload_to_58tc(photo_path):
    url = 'https://upload.58cdn.com.cn/json'
    with open(photo_path, 'rb') as f:
        imgdata = base64.b64encode(f.read()).decode('utf-8')
        
    params = {
        'Pic-Data': imgdata,
        'Pic-Encoding': 'base64',
        'Pic-Path': '/nowater/webim/big/',
        'Pic-Size': '0*0'
    }

    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://ai.58.com/pc/'
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)
    responseText = response.text

    if 'n_v2' in responseText:
        rand_pic_number = str(randint(1, 8))
        img_url = f"https://pic{rand_pic_number}.58cdn.com.cn/nowater/webim/big/{responseText}"
        return {'code': 200, 'url': img_url}
    else:
        return {'code': 400, 'msg': 'Upload Failed.'}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('欢迎使用图床Bot！请直接发送图片以获取返回链接，或使用 /type 更改上传接口，使用 /help 查看所有命令。')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands_text = (
        "/start - 开始使用\n"
        "/type - 选择上传接口\n"
        "/help - 显示帮助信息\n"
    )
    await update.message.reply_text(commands_text)

async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(config['name'], callback_data=f'select_{key}')] for key, config in image_hosts.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('请选择图床接口:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query_data = query.data

    global current_endpoint
    if query_data.startswith("select_"):
        current_endpoint = query_data.split("_", 1)[1]

        if current_endpoint in image_hosts:
            await query.edit_message_text(
                text=f"已选择接口：{image_hosts[current_endpoint]['name']}"
            )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)

    # 保存文件路径
    photo_path = os.path.basename(photo_file.file_path)
    await photo_file.download_to_drive(photo_path)

    try:
        if current_endpoint in image_hosts:
            upload_function_name = image_hosts[current_endpoint]['upload_function']
            upload_function = globals()[upload_function_name]
            result = upload_function(photo_path)
        else:
            result = {'code': 400, 'msg': '未知图床接口选择。'}

        if result['code'] == 200:
            url = result['url']
            markdown_link = f"![image]({url})"
            forum_link = f"[img]{url}[/img]"

            await update.message.reply_text(
                f"上传成功！\n\n"
                f"图片链接：[{url}]({url})\n\n"
                f"Markdown：`{markdown_link}`\n\n"
                f"论坛链接：`{forum_link}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"图片上传失败：{result.get('msg', 'Unknown error.')}")
    except Exception as e:
        logging.error(f'Error during image uploading: {e}')
        await update.message.reply_text('图片上传过程中出现错误。')
    finally:
        if os.path.exists(photo_path):
            os.remove(photo_path)

async def handle_non_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.delete()

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.delete()

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("type", select_type))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(~filters.PHOTO & ~filters.VOICE & ~filters.COMMAND, handle_non_photo))

    application.run_polling()

if __name__ == '__main__':
    main()
