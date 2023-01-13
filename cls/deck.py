import random
from cls.error import InternalError
from cls.card import Card
from cls.cards import Cards

class Deck:
    '''
        Card deck
    '''
    __slots__ = ('tcards', 'pcards', 'cur', 'last', 'must', )

    # initial card deck
    deck_cardstr = '34567890JQKA2'
    deck_cards = [Card(c, j) for c in deck_cardstr for j in range(4)]
    deck_cards.extend([Card('B'), Card('R')])

    def __init__(self):
        '''
            initialize card deck
        '''
        cards = Deck.deck_cards.copy()
        random.seed(); random.shuffle(cards); random.shuffle(cards)
        self.tcards = Cards(cards[:3]); cards = cards[3:]
        self.pcards = [Cards(cards[:17]), Cards(cards[17:34]), Cards(cards[34:])]
        self.cur = 0; self.last = Cards([]); self.must = 2

    def get_cur(self) -> int:
        '''
            get current player index
        '''
        return self.cur

    def get_lastcur(self) -> int:
        '''
            get last player index
        '''
        return (self.cur + 2) % 3

    def get_left(self, cur:int|None = None) -> int:
        '''
            get player left cards
        '''
        if cur is None:
            cur = self.cur
        return self.pcards[cur].get_left()

    def get_lastleft(self) -> int:
        '''
            get last player left cards
        '''
        return self.pcards[self.get_lastcur()].get_left()

    def get_cards(self, cur:int|None = None) -> Cards:
        '''
            get player cards
            cur: int index; None (default) for current
        '''
        if cur is None:
            cur = self.cur
        return self.pcards[cur]

    def decide_lord(self, idx:int) -> None:
        '''
            allocate top cards to player lord
        '''
        if self.lord_decided() or not (0 <= idx < 3):
            raise InternalError('Invalid call or parameter given')
        self.cur = idx
        self.pcards[idx].do_add(self.tcards)
        self.tcards = None

    def check_playable(self, cards:Cards) -> bool:
        '''
            check whether cards are legal and playable
        '''
        if len(cards) == 0:
            return bool(self.must < 2) # skip
        return (cards in self.pcards[self.cur]) and self.last < cards

    def lord_decided(self) -> bool:
        '''
            whether lord is decided
        '''
        return self.tcards is None

    def do_play(self, cards:Cards) -> None:
        '''
            play cards and move to next player
            (must be called after check_playable())
        '''
        if not self.lord_decided():
            raise InternalError('Lord is not decided')
        if len(cards) == 0: # skip
            self.must += 1
            if self.must == 2:
                self.last = Cards([]) # reset last
        else:
            self.must = 0
            self.pcards[self.cur].do_remove(cards)
            self.last = cards
        self.cur = (self.cur + 1) % 3
