#!/usr/bin/python
# coding:utf-8

# Telegram message handle function.
__author__ = '@Kinnto'
__credits__ = '@AK Tech Studio'

import os
import time
import requests
import emoji
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

import config

from __init__ import __author__, __version__, __credits__, __website__, BANNER
# from utils import msg_logger
from timer import checker
from telegram.ext import CallbackContext
from telegram import ChatPermissions

import time
import json
import telegram.ext
import telegram
import sys
import datetime
import os
import logging
import threading
import chardet
import re
from telegram import Update
from telegram.ext import CallbackContext
import pandas as pd

TOKEN = os.environ.get('TOKEN') or config.TOKEN
TURING_KEY = os.environ.get('TURING') or config.TURING_KEY

bot = telebot.TeleBot(TOKEN)

Version_Code = 'poll test'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

CONFIG = json.loads(open(PATH + 'config.json', 'r').read())

DATA_LOCK = False

submission_list = json.loads(open(PATH + 'data.json', 'r').read())

updater = telegram.ext.Updater(token=CONFIG['Token'], use_context=True)
dispatcher = updater.dispatcher

me = updater.bot.get_me()
CONFIG['ID'] = me.id
CONFIG['Username'] = '@' + me.username

print('Starting... (UserID: ' + str(CONFIG['ID']) + ', Username: ' + CONFIG['Username'] + ')')


def save_data():
    global DATA_LOCK
    while DATA_LOCK:
        time.sleep(0.05)
    DATA_LOCK = True
    f = open(PATH + 'data.json', 'a')
    f.write(json.dumps(submission_list, ensure_ascii=False))
    f.close()
    DATA_LOCK = False


def save_config():
    f = open(PATH + 'config.json', 'w')
    f.write(json.dumps(CONFIG, indent=4))
    f.close()




status = {}  # userid: step
user_answer = {}

step_to_column_map = {
    1.1: 'if_fullmembership',
    1.2: 'if_membership_three_months',
    1: 'TG用户名(用户填写)',
    2: '奖品类型',
    3: '居住地：国内/国外',
    4: '是否邮寄至国内',
    5: '是否付费邮寄海外',
    6: '邮寄地址',
    7: '收件人',
    8: '联系电话',
    9: 'Youtube_email',
    10: 'Youtube用户名'


}


def question(update, step):
    if step == 0:
        send_message = bot.send_message(chat_id=update.message.chat_id,
                                        text="欢迎填写AK Tech Studio *完全体电丸会员* 第一次领奖问卷",
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
        send_message = bot.send_message(chat_id=update.message.chat_id,
                                        text="在填写问卷的过程中，如果需要*修改信息*：\n"
                                             "请在*填写完问卷*之后私聊机器人， 或者在*填写完问卷*之后回复任意字符重新开始",
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 1:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + ".请提供您在TG会员群的用户名")

    elif step == 1.1:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text="您是*完全体会员*吗？",
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 1.2:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text="您的完全体电丸会员时常达到*三个月*了吗？\n"
                                         "可通过在Youtube会员资格页面查看您的粉丝徽章的颜色确认",
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 2:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.您想要什么礼品，回复*礼品代码*即可\n\n'
                                                     '*CS*\: CS热血永恒（书）\n'
                                                     '*Ti*\: Tilted\n'
                                                     '*sweet1*\: K嫂甜品（牛轧酥）\n'
                                                     '*sweet2*\: K嫂甜品（牛轧糖）\n'
                                                     '*sweet3*\: K嫂甜品（蛋黄酥）\n'
                                                     '*sweet4*\: K嫂甜品（凤梨酥）\n',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 3:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + "\.您目前的居住地位于海外（包括港澳台）还是国内？\n"
                                                     "请填写 “*国内*” 或者 “*海外*” 。\n",
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 4:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.若居住海外的话，是否选择将礼品邮寄至国内地址？',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)
    elif step == 5:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.是否接受邮寄海外邮费自理？（发国内包邮）',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 6:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.请填写邮寄地址（仅填写地址，越详细越好）\n'
                                                     '\*邮寄国内已经自动忽略4、5两题',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 7:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.请填写快递联系人姓名',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 8:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.请填写快递联系人电话，请在电话前加区域号，中国大陆手机前\+86',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 9:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.请填写联系邮箱（即注册Youtube会员的邮箱，以便确认兑换资格）',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)

    elif step == 10:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text=str(step) + '\.请填写您的YouTube账户昵称，以便确认兑换资格',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)


def mypoll(update, step):
    text = update.message.text
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    if step == 0:
        # question(update, step)
        if update.message.text:
        #todo 问题之前的答案
            return 1.1

    if step == 1:
        if text:
            return 2
    # todo wrong answer won't be recorded

    if step == 1.1:
        if text == '否':
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='很抱歉，您不符合此次参加活动的条件，兑奖仅限于完全体电丸会员，'
                                             '您可以通过升级的方式加入*完全体电丸会员*，感谢您的参与',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 11
        elif text == '是' or text == 'yes' or text == 'Yes' or text == 'shi':
            return 1.2
        else:
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='回复格式有误，请输入*是*或者*否*',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 1.1

    if step == 1.2:
        if text == '是' or text == 'yes' or text == 'Yes' or text == 'shi':
            return 1
        elif text == '否':
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='很抱歉，您还不满*三个月*完全体电丸会员，不符合参加活动条件，继续加油哦💪',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 11
        else:
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='回复格式有误，请回复*是*或者*否*',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 1.2

    if step == 2:
        step2_answer = ['cs', 'ti', 'sweet1', '*sweet2', 'sweet3', 'sweet4',
                        'CS', 'Cs',
                        'Sweet1', 'Sweet2', 'Sweet3', 'Sweet4',
                        'Ti', 'TI']
        step2_text = re.match(r'^[A-Za-z]+[0-9]*$', text, re.M|re.I).group() # ignore the case of answer
        if step2_text not in step2_answer:
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='回复格式有误，请输入回复礼品代码：\n'
                                             'CS  '
                                             'Ti  '
                                             'sweet1  '
                                             'sweet2  '
                                             'sweet3  '
                                             'sweet4  ',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 2
        else:
            return 3

    if step == 3:
        if text == '海外' or text == 'haiwai' or text == 'overseas':
            return 4
        elif text == '国内' or text == 'mainland' or text == 'guonei' or text == '國內'or text =='國内':
            return 6
        else:
            return 3

    if step == 4:
        if text == '否' or text == '没有' or text == 'no' or text == 'No':
            return 5
        elif text == '是' or text == '有':
            return 6
        else:
            return 4

    if step == 5:
        if text == '是':
            return 6
        elif text == '否':
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='由于您的情况特殊，请联系会员群管理员，谢谢\n'                                             
                                             '如果要重新填写，回复 /poll1 重新开始',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 11
        else:
            response = bot.send_message(chat_id=update.message.chat_id,
                                        text='回复格式有误，请输入*是*或者*否*',
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return 5

    if step == 6:
        if text:
            return 7

    if step == 7:
        if text:
            return 8

    if step == 8:
        if text:
            return 9

    if step == 9:
        if text:
            return 10

    if step == 10:
        response = bot.send_message(chat_id=update.message.chat_id,
                                    text='资料填写完毕，*点击 /done 提交信息。*\n'
                                         '~防止误触\n~'
                                         '~防止误触\n~'
                                         '~防止误触\n~'
                                         '如果要重新填写，回复 /poll1 重新开始',
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)
        response = bot.send_message(chat_id= update.message.chat_id, text = user_answer[user_id])
        response = bot.send_message(chat_id=update.message.chat_id,  text='领奖秘籍（为了方便确认您的信息，请务必千万就现在马上设置TG用户名，即@后面的username，不然很难找到您啊）')
        return 11


def process_msg(update: Update, context: CallbackContext):
    if update.message.text :
        if update.message.from_user.id == update.message.chat_id:
            user_id = update.message.from_user.id
            matchObj = re.search(r'备注', update.message.text)
            if matchObj != None:
                file11 = open("备注.csv", 'a', encoding='utf8')
                filewrite111 = (str(user_id) + '-' + str(update.message.from_user.first_name) + '-' + str(
                    update.message.text) + '-' + time.ctime() + "\n")
                file11.write(filewrite111)
                send_message = bot.send_message(chat_id=update.message.chat_id,
                                                text=
                                                "已经收到您的备注\n", parse_mode='Markdown')
            else:
                pass
            if update.message.text == '/poll1':
                if user_id not in status:  # if id not in status: statsus[id] = 0
                    dff = pd.DataFrame({
                        'TG_id': [update.message.from_user.id],
                        'tg_firstname(自动生成))': [update.message.from_user.first_name],
                        'TG用户名(用户填写)': [None],
                        '奖品类型': [None],
                        '居住地：国内/国外': [None],
                        '是否邮寄至国内': [None],
                        '付费邮寄海外': [None],
                        '邮寄地址': [None],
                        '收件人': [None],
                        '联系电话': [None],
                        'Youtube email': [None],
                        'Youtube用户名': [None],
                        'if_fullmembership': [None],
                        'if_membership_three_months': [None],
                        'time': [time.ctime()]})
                    dff['id'] = update.message.from_user.id
                    # TODO
                    user_answer[user_id] = dff
                    status[user_id] = 0
                    question(update, status[user_id])  # welcome
                    cur_status = status[user_id]
                    new_status = mypoll(update, cur_status)
                    status[user_id] = new_status
                    question(update, status[user_id])  # q1
            elif user_id in status:
                text_answer = update.message.text
                user_answer[user_id][step_to_column_map[status[user_id]]] = text_answer
                cur_status = status[user_id]
                status[user_id] = mypoll(update, cur_status)
                question(update, status[user_id])
                if status[user_id] == 11:
                    user_answer[user_id].to_csv('第一次领奖记录1.csv', mode='a', encoding= 'gbk', header=0)

                    status.pop(user_id, None)
                    user_answer.pop(user_id, None)
            elif update.message.text == '/done':
                send_message = bot.send_message(chat_id=update.message.chat_id,
                                                text="提交成功，感谢您的支持。")
                # print('user_answer[user_id]:', user_answer[user_id])
                # user_answer[user_id].to_csv('第一次领奖记录.csv', mode='a')
                # answer_csv = pd.read_csv('第一次领奖记录.csv')
                # answer_csv.append(user_answer[user_id]).drop_duplicates(keep='last', inplace=True, ignore_index=True)
                # answer_csv.to_csv('第一次领奖记录.csv')
                status.pop(user_id, None)
                user_answer.pop(user_id, None)
            elif update.message.text == '/start':
                send_message = bot.send_message(chat_id=update.message.chat_id,
                                                text="尊敬的会员，胖(A)虎(K)欢迎你。 \n回复 /poll1 "
                                                     "即可参加第一次会员完全体礼物信息登记。")
        else:
            return
    else:
        print('')
        return



def process_command(update: Update, context: CallbackContext):
    print(update.message.text)
    if update.channel_post:
        return
    command = update.message.text[1:].replace(CONFIG['Username'], ''
                                              ).lower()
    print('command', command)

def process_callback(update: Update, context: CallbackContext):
    if update.channel_post:
        return
    global submission_list
    query = update.callback_query

dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text
                                                   | telegram.ext.Filters.audio
                                                   | telegram.ext.Filters.photo
                                                   | telegram.ext.Filters.video
                                                   | telegram.ext.Filters.voice
                                                   | telegram.ext.Filters.status_update
                                                   | telegram.ext.Filters.document, process_msg))

dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command,
                                                   process_command))

dispatcher.add_handler(telegram.ext.CallbackQueryHandler(process_callback))

updater.start_polling()
print('Started')
updater.idle()
print('Stopping...')
save_data()
print('Data saved.')
print('Stopped.')

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone="US/Eastern")
    scheduler.add_job(checker, 'interval', minutes=config.INTERVAL)
    scheduler.start()
    print('''Welcome to ExpressBot, Version %s\n%sAuthor: %s\nCredits:%s\nWebsite:%s\n%s'''
          % (__version__, BANNER, __author__, __credits__, __website__, '--' * 10 + 'Bot is running' + '--' * 10))
    bot.polling(none_stop=True)
