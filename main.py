from config import TOKEN

from cls.card import Card
from cls.cards import Cards
from cls.deck import Deck
from fun.cards import *

from telegram import Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes

# Local test (using socks5 proxy)
#   - install with 'pip install Pysocks'
# import socks
# import socket
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
# socket.socket = socks.socksocket
# -------------------------------

'''
    Global entrance
'''

async def new_game() -> None:
    return

async def join_game() -> None:
    return

async def kill_game() -> None:
    return

async def help() -> None:
    return

async def inline_query() -> None:
    return


if __name__ == '__main__':
    '''
    bot_app = Application.builder().token(TOKEN).build()

    bot_app.add_handler(CommandHandler("new", new_game))
    bot_app.add_handler(CommandHandler("join", join_game))
    bot_app.add_handler(CommandHandler("kill", kill_game))
    bot_app.add_handler(CommandHandler("help", help))

    bot_app.add_handler(InlineQueryHandler(inline_query))

    bot_app.run_polling()
    '''

    d = Deck()
    print([repr(i) for i in d.pcards])
    print(repr(d.tcards))
    d.decide_lord(2)
    while True:
        print(f'player {d.get_cur()} card {repr(d.get_cards())}')
        c = Cards.from_cardlist(input(f'Play{d.get_cur()} > '), d.get_cards())
        while c is False or not d.check_playable(c):
            c =  Cards.from_cardlist(input(f'Play{d.get_cur()} > '), d.get_cards())
        d.do_play(c); print(f'player {d.get_lastcur()} left {d.get_lastleft()}')
        if not d.get_lastleft():
            break
    print('Finished')
