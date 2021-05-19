#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging import DEBUG
import subprocess
import os
import requests
import logging
import sys
from autologging import logged, traced
import telebot
from decouple import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)



API_TOKEN = config('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
users_files = {}



@bot.message_handler(commands=['start'])
def start_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           '👨‍💻My owner👨‍💻', url='telegram.me/doreamonfans1'
       )
   )   
   bot.send_message(
       message.chat.id,
       'Hi I am disney team Video Merge Bot Here 🤗 project by @disneygrou\n\n' +
       'To Get Help Press /help',
       reply_markup=keyboard
   )

@bot.message_handler(content_types=['video'])
def handle_video(message):
    """Add sent video to user's video list."""

    chat_id = message.chat.id
    if chat_id in users_files:
        users_files[chat_id].append(message.video.file_id)
    else:
        users_files[chat_id] = [message.video.file_id]


@bot.message_handler(commands=['merge'])
def merge(message):
    """Merge user's videos."""

    chat_id = message.chat.id

    # Stops method if user hasn't sent any videos
    if chat_id not in users_files:
        bot.send_message(chat_id, 
        'You Haven\'t Send Any Video For Merge 🥺\n\n'
        'Please Send Me Videos First and Press! /merge 🤗'
        )
        return None

    inputs = list()
    for i, file_id in enumerate(users_files[chat_id]):
        file_info = bot.get_file(file_id)

        response = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(
                API_TOKEN, file_info.file_path
            )
        )
        inputs.append("file '{}'".format(i))
        with open(str(i), 'wb') as arq:
            arq.write(response.content)

    with open('inputs.txt', 'w') as arq:
        arq.write('\n'.join(inputs))

    subprocess.call(
        ['ffmpeg', '-f', 'concat', '-i', 'inputs.txt', '-c', 'copy', 'out.mp4']
    )

    with open('out.mp4', 'rb') as video:
        bot.send_video(chat_id, video)
    users_files[chat_id] = []


@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           ' 👨‍💻Developer👨‍💻', url='telegram.me/doreamonfans1'
           ' 👨‍🔧Updates channel👨‍🔧', url='https://t.me/disneygrou'
           ' 🤖support group🤖', url='https://t.me/disneyteamchat'
       )
   )
   bot.send_message(
       message.chat.id,
       '1) Send Two Of Your MP4 Videos (Which You Want To Merge)\n\n' +
       '2) After That Press Me! /merge ☺️',
       reply_markup=keyboard
   )

logger.info("Yeah I'm running!")

bot.polling()
