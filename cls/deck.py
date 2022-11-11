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
    random.seed(); random.shuffle(cards)
    self.tcards = Cards(cards[:3]); cards = cards[3:]
    self.pcards = [Cards(cards[:17]), Cards(cards[17:34]), Cards(cards[34:])]
    self.cur = 0; self.last = Cards([])

  # get current player index
  def get_cur(self) -> int:
    return self.cur

  # get player left cards
  def get_left(self, cur:int|None = None) -> int:
    if cur is None: cur = self.cur
    return self.pcards[cur].get_left()

  # check whether cards are playable
  def check_playable(self) -> bool:
    return self.last < self.cards

  # play cards
  def do_play(self, cards:Cards) -> None:
    pass # TODO

