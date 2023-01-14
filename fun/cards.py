from cls.error import InternalError
from cls.card import Card
from cls.cards import Cards

_cardchar = '34567890JQKA2BR'
_suitchar = 'SHCD'

def split_cardstr(cardstr:str) -> bool|list[str]:
    '''
        split a complete card string into separate card strings
        return False if invalid
        example: '38C10S JQDR' -> ['3','8C','10S','J','QD','R']
    '''
    ret = []
    hs = ls = ''
    cardstr = ''.join(cardstr.split()).upper() # remove white characters
    valid_start = _cardchar + '1'
    valid_end = _suitchar + 'BR'
    for c in cardstr: # a DFA-like algorithm
        match ls:
            case '': # start state
                if c not in valid_start: # failed
                    return False
                ls = c
            case '1': # specialize for 10
                if c != '0': # failed
                    return False
                ls = '10'
            case ls if ls in valid_start or ls == '10': # intermediate
                match c: # single end state
                    case c if c in valid_start: # already end
                        ret.append(ls)
                        ls = c
                    case c if c in _suitchar: # with suit
                        ret.append(ls + c)
                        ls = ''
                    case _: # invalid
                        return False
            case _: # invalid
                 return False
    if ls != '': # append remaining
        ret.append(ls)
    return ret

@classmethod
def from_cardlist(cls:Cards, cardlist:list[str]|str, cards:Cards|None = None) -> bool|Cards:
    '''
        get cards from card string(s)
        choose the first one in {cards} if not precise
        return False if failed
    '''
    if type(cardlist) is str:
        cardlist = split_cardstr(cardlist)
        if cardlist is False:
            return False
    # by length descending, exact match first
    cardlist.sort(key = len, reverse = True)
    if cards is not None:
        cards = cards.get_cards().copy()
    ret = []
    for cardstr in cardlist:
        try:
            card = Card(cardstr)
        except InternalError as e: # invalid raw string
            if cardstr[-1] not in _suitchar: # without suit
                try:
                    card = Card(cardstr, 0) # assuming a suit
                    # find the first card with the same index
                    card = next(c for c in cards if int(card) == int(c))
                except (InternalError, StopIteration): # still invalid
                    return False
            else: # invalid string
                return False
        if card in ret: # duplicated, skip
            continue
        # ensure validity if cards is not None
        if cards is not None:
            try:
                cards.remove(card)
            except ValueError: # not found
                return False
        ret.append(card)
    return cls(ret)
Cards.from_cardlist = from_cardlist


__all__ = ()
