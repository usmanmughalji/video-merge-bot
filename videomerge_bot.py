#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

import telebot
import requests
from decouple import config


API_TOKEN = config('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
users_files = {}


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
        bot.send_message(chat_id, 'You didn\'t send any videos to merge')
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


@bot.message_handler(func=lambda message: True)
def help(message):
    """Responde any other messages with help."""

    help_msg = (
        'Send the videos you want to merge (preferably in MP4) and use '
        '/merge command to receive merged video.'
    )
    bot.send_message(message.chat.id, help_msg)


bot.polling()
