#!/usr/bin/python
# -*- coding: utf-8 -*-


from botapitamtam import BotHandler
# from bitlyshortener import Shortener  #для использования требуется python3.7
import json
import requests
import logging
import youtube_dl


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


def main():
    marker = None
    while True:
        last_update = bot.get_updates(marker)
        # тут можно вставить любые действия которые должны выполняться во время ожидания события
        if last_update == None:  # проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        marker = bot.get_marker(last_update)
        chat_id = bot.get_chat_id(last_update)
        user_id = bot.get_user_id(last_update)
        payload = bot.get_payload(last_update)
        url_cont = bot.get_url(last_update)
        url_txt = bot.get_text(last_update)
        callback_id = bot.get_callback_id(last_update)
        if url_txt is not None and url_cont is None:
            with youtube_dl.YoutubeDL({'format': 'best',}) as ydl:
                file_dat = ydl.extract_info(url_txt, download=False)
                url = file_dat['url']
        else:
            url = url_cont
        if url != None:
            mid_reply = bot.get_message_id(last_update)
            bot.delete_message(mid_all.get(chat_id))
            buttons = [[{"type": 'callback',
                         "text": 'Короткая',
                         "payload": 'short'
                         },
                        {"type": 'callback',
                         "text": 'Исходная',
                         "payload": 'long'
                         }]]
            upd = bot.send_buttons("Тип ссылки", buttons, chat_id)
            mid = bot.get_message_id(upd)
            url_all.update({chat_id: url})
            mid_all.update({chat_id: mid})
            mid_reply_all.update({chat_id: mid_reply})

        mid_ = mid_all.get(chat_id)
        url_ = url_all.get(chat_id)

        if payload == 'short':
            bot.send_answer_callback(callback_id, 'получаю ссылку...')
            bot.delete_message(mid_)
            params = {'url': url_}
            res_clck = requests.get('https://clck.ru/--', params)
            link_clck = res_clck.text
            # link_bitly = shortener.shorten_urls(url_short)[0]
            # bot.send_message(link_bitly, chat_id)
            bot.send_reply_message(link_clck, mid_reply_all.get(chat_id), chat_id)
            logger.info('user_id ({}) recived filelink (clck.ru)'.format(user_id))
        elif payload == 'long':
            bot.send_answer_callback(callback_id, 'получаю ссылку...')
            bot.delete_message(mid_)
            bot.send_reply_message(str(url_), mid_reply_all.get(chat_id), chat_id)
            logger.info('user_id ({}) recived filelink (TT)'.format(user_id))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
