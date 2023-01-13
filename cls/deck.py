import random
from cls.card import Card
from cls.cards import Cards

'''
    Card deck
'''
class Deck:

    # initialize card deck
    def __init__(self):
        cards = [Card(i if i>=3 else i+20) for i in range(1, 13+1) for j in range(4)]
        cards.extend([Card(31), Card(32)])
        random.seed(); random.shuffle(cards); random.shuffle(cards)
        self.tcards = Cards(cards[:3]); cards = cards[3:]
        self.pcards = [Cards(cards[:17]), Cards(cards[17:34]), Cards(cards[34:])]
        self.cur = 0; self.last = Cards([]); self.must = 2

    # get current player index
    def get_cur(self) -> int:
        return self.cur

    # get last player index
    def get_lastcur(self) -> int:
        return (self.cur + 2) % 3

    # get player left cards
    def get_left(self, cur:int|None = None) -> int:
        if cur is None: cur = self.cur
        return self.pcards[cur].get_left()

    # get last player left cards
    def get_lastleft(self) -> int:
        return self.pcards[self.get_lastcur()].get_left()

    # get player cards
    def get_cards(self, cur:int|None = None) -> int:
        if cur is None: cur = self.cur
        return self.pcards[cur]

    # allocate top cards to player lord
    def decide_lord(self, idx:int) -> None:
        if not self.tcards or not (0 <= idx < 3):
            raise RuntimeError('Internal error')
        self.cur = idx
        self.pcards[idx].do_add(self.tcards)
        self.tcards = None

    # check whether cards are legal and playable
    def check_playable(self, cards) -> bool:
        if len(cards) == 0:
            return bool(self.must < 2) # skip
        return (cards in self.pcards[self.cur]) and self.last < cards

    # play cards
    def do_play(self, cards:Cards) -> None:
        if self.tcards:
            raise RuntimeError('Internal error')
        if len(cards) == 0: # skip
            self.must += 1
            if self.must == 2:
                self.last = Cards([]) # reset last
        else:
            self.must = 0
            self.pcards[self.cur].do_play(cards)
            self.last = cards
        self.cur = (self.cur + 1) % 3
