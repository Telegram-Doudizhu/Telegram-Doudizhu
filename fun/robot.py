from pickle import FALSE
import random
from cls.error import InternalError
from cls.card import Card
from cls.cards import Cards
from cls.room import Room

import logging
logger = logging.getLogger(__name__)

def will_robot_bid(room: Room) -> bool:
    '''
        return whether the robot will bid
    '''
    if type(room.user) is not Room.Robot:
        raise InternalError(f'User type mismatch, Robot expected, {type(room.user)} found')
    match room.user.hard:
        case 0:
            return random.random() < 0.3
        case 1:
            return random.random() < 0.7
        case _:
            raise InternalError(f'Invalid robot hard level int:{room.user.hard} found')

def what_robot_play(room: Room) -> Cards:
    '''
        return what the robot will play
    '''
    if type(room.user) is not Room.Robot:
        raise InternalError(f'User type mismatch, Robot expected, {type(room.user)} found')
    match room.user.hard:
        case 0:
            if room.must:
                return Cards([room.cards[0]])
            return Cards([])
        case 1:
            if room.must:
                seq = [*range(34, 27, -1), *range(26, 19, -1), 15, 16, 12, 13, 9, 10, 6, 7, 14, 11, 8, 5, 4, 3, 18, 17, 1, 2]
                base = 0
            else:
                ctype = room.lastvcards.get_type()
                seq = [ctype[1], 1, 2]
                base = ctype[2]
            if (r:= try_types(room.cards, seq, base)) is not False:
                logger.info(f'Bot hard int:1 decided: {repr(r)}, room {room.id}')
                return r
            return Cards([]) # should be all included if self.must
        case _:
            raise InternalError(f'Invalid robot hard level int:{room.user.hard} found')


def try_types(cards: Cards, types: list, base: int|Card) -> bool|Cards:
    '''
        check whether cards can be played with any of given types respectively
        base = 0 for no limits
    '''
    for t in types:
        if (r:= find_by_type(cards, t, base)) is not False:
            return r
    return False

def find_by_type(cards: Cards, type: int, base: int|Card) -> bool|Cards:
    '''
        find cards by type specified (definition see Cards.get_type())
        type:
            0 -> illegal
            1 -> normal bomb
            2 -> king bomb
            3 -> single
            4 -> double
            5 -> triple
            6 -> triple+1
            7 -> triple+double
            8 -> 2*triple~
            9 -> 2*(triple~+1)
            10 -> 2*(triple~+double)
            11 -> 3*triple~
            12 -> 3*(triple~+1)
            13 -> 3*(triple~+double)
            14 -> 4*triple~
            15 -> 4*(triple~+1)
            16 -> 4*(triple~+double)
            17 -> quadriple+2*single
            18 -> quadriple+double
            19+ -> ~
            27+ -> ~~
    '''
    def get_spt(cards: Cards, func) -> list[Cards]:
        cnt,spt = 1,[[] for _ in range(55)]
        for i in range(1, len(cards)):
            if not func(cards[i-1], cards[i]):
                spt[cnt].append(cards[i-1])
                cnt = 1
            else:
                cnt += 1
        spt[cnt].append(cards[len(cards)-1])
        spt = [Cards(e) for e in spt]
        return spt
    spt = get_spt(cards, lambda x, y: int(x) == int(y))
    cmp = lambda card: int(card) > int(base)
    equ = lambda base: lambda card: int(card) == int(base)
    lin = lambda base: lambda card: int(card) in base
    _filter = lambda x, y: list(filter(x, y))
    def find_cont(cts: Cards|list[Card], ctn: int):
        ltp = False
        for c, ts in enumerate(cts[ctn : 15]):
            if ltp is not False:
                break
            for t in ts:
                t = int(Card('K', 0)) + 1 if str(t) == 'A' else int(t)
                if int(t) - ctn + 1 > int(base):
                    ltp = max(int(base) + 1, int(t) - c - ctn + 1)
                    break
        return ltp
    match type:
        case 1:
            if len(r:= _filter(cmp, spt[4])) > 0:
                return Cards(_filter(equ(r[0]), cards))
        case 2:
            if len(r:= _filter(lambda card: card.is_king, spt[1])) == 2:
                return Cards(r)
        case 3:
            if len(r:= _filter(cmp, spt[1])) > 0:
                if r[0].is_king and int(base) == 0 and len(spt[2]) > 0:
                    return False # fallback to double
                else:
                   return Cards([r[0]])
            if len(cards) <= 2 and len(r:= _filter(cmp, spt[2])) > 0:
                return Cards([spt[2][0]])
        case 4:
            if len(r:= _filter(cmp, spt[2])) > 0:
                return Cards(_filter(equ(r[0]), cards))
            if len(cards) <= 3 and len(r:= _filter(cmp, spt[3])) > 0:
                return Cards(_filter(equ(spt[3][0]), cards)[:2])
        case 5:
            if len(r:= _filter(cmp, spt[3])) > 0:
                return Cards(_filter(equ(r[0]), cards))
        case 6 | 17:
            if len(r:= _filter(cmp, spt[3 if type == 6 else 4])) > 0 and len(spt[1]) > 0:
                return Cards(_filter(equ(r[0]), cards) + [spt[1][0]])
        case 7 | 18:
            if len(r:= _filter(cmp, spt[3 if type == 7 else 4])) > 0:
                pl = _filter(equ(r[0]), cards)
                if len(spt[2]) > 0:
                    pl += _filter(equ(spt[2][0]), cards)
                elif len(spt[1]) >= 2:
                    pl += spt[1][:2]
                else:
                    return False
                return Cards(pl)
        case type if type in range(8, 16+1):
            if len(r:= _filter(cmp, spt[3])) >= 2:
                cts = get_spt(r, lambda x, y: Cards([x, y])._check_continuous()) # spec for KA
                ctn = 2 if 8 <= type <= 10 else 3 if 11 <= type <= 13 else 4
                ltp = find_cont(cts, ctn)
                if ltp is False:
                    return False
                # spec for KA
                pl = _filter(lin([int(Card('A', 0)) if ltp + i == int(Card('K', 0)) + 1 else ltp + i for i in range(ctn)]), cards)
                match type:
                    case 9 | 12 | 15:
                        csn = 2 if type == 9 else 3 if type == 12 else 4
                        while True:
                            if len(spt[1]) >= csn:
                                pl += spt[1][:csn]
                                csn = 0
                                break
                            elif csn >= 2 and len(spt[2]) > 0:
                                pl += _filter(equ(spt[2][0]), cards)
                                spt[2].do_remove(spt[2][0])
                                csn -= 2
                            elif csn >= 3 and len(spt[3]) > 0:
                                pl += _filter(equ(spt[3][0]), cards)
                                spt[3].do_remove(spt[3][0])
                                csn -= 3
                            else:
                                break
                        if csn > 0:
                            return False
                    case 10 | 13 | 16:
                        csn = 2 if type == 10 else 3 if type == 13 else 4
                        if len(spt[2]) >= csn:
                            for c in spt[2][:csn]:
                                pl += _filter(equ(c), cards)
                return Cards(pl)
        case type if type in range(19, 35):
            if len(r:= _filter(cmp, spt[1].do_add(spt[2]).do_add(spt[3]) if type < 27 else spt[2].do_add(spt[3]))) >= (ctn:= (type - 19 + 5 if type < 27 else type - 27 + 3)):
                r = Cards({int(card): card for card in r}.values()) # unique
                cts = get_spt(r, lambda x, y: Cards([x, y])._check_continuous()) # spec for KA
                ltp = find_cont(cts, ctn)
                if ltp is False:
                    return False
                # spec for KA
                pl = _filter(lin([int(Card('A', 0)) if ltp + i == int(Card('K', 0)) + 1 else ltp + i for i in range(ctn)]), cards)
                if type < 27:
                    pl = {int(card): card for card in pl}.values() # unique
                else:
                    pl2 = []; plt = [] # unique 2
                    for card in pl: # a stupid implement here
                        if plt.count(int(card)) < 2:
                            pl2.append(card)
                            plt.append(int(card))
                    pl = pl2
                return Cards(pl)
        case _:
            raise InternalError(f'invalid cards type int:{type} given')
    return False



__all__ = ('will_robot_bid', 'what_robot_play', )