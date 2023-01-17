import random
from cls.error import InternalError
from cls.card import Card
from cls.cards import Cards

class Deck:
    '''
        Card deck
    '''
    __slots__ = ('_tcards', '_pcards', '_cur', '_last', '_must', '_first', )

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
        self._tcards = Cards(cards[:3]); cards = cards[3:]
        self._pcards = [Cards(cards[:17]), Cards(cards[17:34]), Cards(cards[34:])]
        self._cur = 0; self._last = Cards([]); self._must = 2; self._first = True

    def get_cur(self) -> int:
        '''
            get current player index
        '''
        return self._cur

    def get_lastcur(self) -> int:
        '''
            get last player index
        '''
        return (self._cur + 2) % 3

    def get_left(self, cur:int|None = None) -> int:
        '''
            get player left cards
        '''
        if cur is None:
            cur = self._cur
        return self._pcards[cur].length

    def get_lastleft(self) -> int:
        '''
            get last player left cards
        '''
        return self._pcards[self.get_lastcur()].length

    def move_next(self) -> None:
        '''
            move to next player
        '''
        self._cur = (self._cur + 1) % 3

    def get_cards(self, cur:int|None = None) -> Cards:
        '''
            get player cards
            cur: int index; None (default) for current
        '''
        if cur is None:
            cur = self._cur
        return self._pcards[cur]

    def is_first(self) -> bool:
        '''
            check whether current player is first
        '''
        return self._first

    def decide_lord(self, idx:int) -> Cards:
        '''
            allocate top cards to player lord
            will reset self.cur
        '''
        if self.lord_decided() or not (0 <= idx < 3):
            raise InternalError('Invalid call or parameter given')
        self._cur = idx
        t = self._tcards
        self._pcards[idx].do_add(t)
        self._tcards = None
        return t

    def must_play(self) -> bool:
        '''
            check whether current player must play
        '''
        return bool(self._must == 2)
        
    def check_playable(self, cards:Cards) -> bool:
        '''
            check whether cards are legal and playable
        '''
        if len(cards) == 0:
            return not self.must_play() # skip
        return (cards in self._pcards[self._cur]) and self._last < cards

    def lord_decided(self) -> bool:
        '''
            whether lord is decided
        '''
        return self._tcards is None

    def do_play(self, cards:Cards) -> None:
        '''
            play cards and move to next player
            (must be called after check_playable())
        '''
        if not self.lord_decided():
            raise InternalError('Lord is not decided')
        self._first = False
        if len(cards) == 0: # skip
            self._must += 1
            if self._must == 2:
                self._last = Cards([]) # reset last
        else:
            self._must = 0
            self._pcards[self._cur].do_remove(cards)
            self._last = cards
        self.move_next()
