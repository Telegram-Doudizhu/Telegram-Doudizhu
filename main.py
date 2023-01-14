from cls.card import Card
from cls.cards import Cards
from cls.deck import Deck
from fun.cards import *

import config
from fun.bot import start_bot

import logging
logging.basicConfig(level = logging.DEBUG,format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
logger = logging.getLogger(__name__)

'''
    Global entrance
'''
if __name__ == '__main__':
    logger.warning('TGDDZ preparing to start......')
    
    # TODO: argparse
    
    # start_bot(config.TOKEN, config.PROXY)

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
