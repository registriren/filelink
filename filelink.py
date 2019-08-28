#!/usr/bin/python
# -*- coding: utf-8 -*-


from botapitamtam import BotHandler
#from bitlyshortener import Shortener  #для использования требуется python3.7
import json
import requests

config = 'config.json'
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    #token_bitly = [conf['bitly_token']]

#shortener = Shortener(tokens=token_bitly, max_cache_size=8192)
bot = BotHandler(token)
url_all = {}
def main():
    marker = None
    while True:
        last_update = bot.get_updates(marker)
        #тут можно вставить любые действия которые должны выполняться во время ожидания события
        if last_update == None: #проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        marker = bot.get_marker(last_update)
        chat_id = bot.get_chat_id(last_update)
        payload = bot.get_payload(last_update)
        url = bot.get_url(last_update)

        if url != None:
            buttons = [{"type": 'callback',
                        "text": 'Короткая',
                        "payload": 'short'},
                       {"type": 'callback',
                        "text": 'Исходная',
                        "payload": 'long'
                        }]
            bot.send_buttons("Тип ссылки", buttons, chat_id)
            #url_short = [url]
            url_all.update({chat_id : url})
        #else:
        #    bot.send_message('Нет ссылки', chat_id)
        #if payload != None:
        if payload == 'short':
                    url_ = url_all.get(chat_id)
                    params = {'url': url_}
                    res_clck = requests.get('https://clck.ru/--', params)
                    link_clck = res_clck.text
                    #link_bitly = shortener.shorten_urls(url_short)[0]
                    #print(link_bitly)
                    #bot.send_message(link_bitly, chat_id)
                    bot.send_message(link_clck, chat_id)
        elif payload == 'long':
                    bot.send_message(str(url_), chat_id)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
