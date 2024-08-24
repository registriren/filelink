#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

from botapitamtam import BotHandler
# from bitlyshortener import Shortener  #для использования требуется python3.7
import json
import requests
import logging
from yt_dlp import YoutubeDL
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

config = 'config.json'
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    # token_bitly = [conf['bitly_token']]

# shortener = Shortener(tokens=token_bitly, max_cache_size=8192)
bot = BotHandler(token)
url_all = {}
mid_all = {}
mid_reply_all = {}


def clck(url):
    params = {'url': url}
    res_clck = requests.get('https://clck.ru/--', params)
    link = res_clck.text
    return link


def url_encode(txt):
    return urllib.parse.quote(txt)


def short_link(url, mid, chat_id):
    link_clck = clck(url)
    bot.send_reply_message(link_clck, mid, chat_id, dislinkprev=True)


def main():
    while True:
        last_update = bot.get_updates()
        # тут можно вставить любые действия которые должны выполняться во время ожидания события
        if last_update:  # проверка на пустое событие, если пусто - возврат к началу цикла
            chat_id = bot.get_chat_id(last_update)
            user_id = bot.get_user_id(last_update)
            payload = bot.get_payload(last_update)
            url_cont = bot.get_url(last_update)
            url_txt = bot.get_text(last_update)
            mid_url = bot.get_message_id(last_update)
            callback_id = bot.get_callback_id(last_update)
            att_type = bot.get_attach_type(last_update)
            attach = bot.get_attachments(last_update)
            flag = True
            if att_type == 'share':
                url_txt = url_cont
                url_cont = None
            if url_txt is None:
                url_txt = ''
            PTR = '(|.+://)(|[A-Za-z0-9-.]+\.)[A-Za-z0-9-]+\.[A-Za-z0-9-]+(|.+)'  # регулярное выражение для проверки ссылки
            try:
                if re.fullmatch(PTR, url_txt) and not url_cont and not payload:
                    try:
                        upd = bot.send_message('Обрабатываю контент...', chat_id)
                        mid = bot.get_message_id(upd)
                        # url_txt = re.search("(?P<url>https?://[^\s]+)", url_txt).group("url")
                        if url_txt: #"youtu" in
                            with YoutubeDL({'format': 'best'}) as ydl:
                                dat = ydl.extract_info(url_txt, download=False)
                                url_vid = dat['url']
                            protocol = dat['protocol']
                            title = dat['title']
                            with YoutubeDL({'format': 'bestaudio'}) as ydl:
                                dat = ydl.extract_info(url_txt, download=False)
                                url_aud = dat['url']
                            if protocol == 'http' or protocol == 'https':
                                link_vid = clck(url_vid + '&title=' + url_encode(title))
                                link_aud = clck(url_aud + '&title=' + url_encode(title))
                                button1 = bot.button_link('Скачать видео', link_vid)
                                button2 = bot.button_link('Скачать аудио', link_aud)
                                buttons = [[button1, button2]]
                                link = bot.link_reply(mid_url)
                                key = bot.attach_buttons(buttons)
                                text = '{}\nVIDEO: {}\nAUDIO: {}'.format(title, link_vid, link_aud)
                                bot.delete_message(mid)
                                bot.send_message(text, chat_id, attachments=key, link=link)
                                logger.info('user_id {} used youtube-dl'.format(user_id))
                        else:
                            bot.delete_message(mid)
                            short_link(url_txt, mid_url, chat_id)
                            logger.info('user_id {} recived filelink (clck.ru)'.format(user_id))
                    except Exception as e:
                        logger.error("Error download youtube-dl: %s.", e)
                        bot.delete_message(mid)
                        short_link(url_txt, mid_url, chat_id)
                        logger.info('user_id {} recived filelink (clck.ru)'.format(user_id))
                elif url_cont:
                    mid_reply = bot.get_message_id(last_update)
                    bot.delete_message(mid_all.get(chat_id))
                    button1 = bot.button_callback('Короткая', 'short')
                    button2 = bot.button_callback('Исходная', 'long')
                    buttons = [[button1, button2]]
                    upd = bot.send_buttons("Тип ссылки", buttons, chat_id)
                    mid = bot.get_message_id(upd)
                    url_all.update({chat_id: attach})
                    mid_all.update({chat_id: mid})
                    mid_reply_all.update({chat_id: mid_reply})
                    flag = None
            except Exception as e:
                logger.error("Error input data: %s.", e)
                flag = None
            mid_ = mid_all.get(chat_id)
            url_ = 'tamtam.chat'
            if url_all.get(chat_id) and flag:
                for att in url_all.get(chat_id):
                    if 'payload' in att.keys():
                        att = att.get('payload')
                        if 'url' in att.keys():
                            url_ = att.get('url')
                    if payload == 'short':
                        bot.send_answer_callback(callback_id, 'получаю ссылку...')
                        bot.delete_message(mid_)
                        short_link(url_, mid_reply_all.get(chat_id), chat_id)
                        logger.info('user_id {} recived filelink (clck.ru)'.format(user_id))
                    elif payload == 'long':
                        bot.send_answer_callback(callback_id, 'получаю ссылку...')
                        bot.delete_message(mid_)
                        bot.send_reply_message(str(url_), mid_reply_all.get(chat_id), chat_id, dislinkprev=True)
                        logger.info('user_id {} recived filelink (TT)'.format(user_id))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
