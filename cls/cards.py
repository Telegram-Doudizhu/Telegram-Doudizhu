from cls.card import Card

'''
  Cards
'''
class Cards:
  pass

class Cards:

  # initialize cards
  def __init__(self, cards:Cards|list[Card]):
    if all(type(card) is Card for card in cards):
      self.cards = sorted(cards)
    elif type(cards) is Cards:
      self.cards = sorted(cards.cards)
    else:
      raise RuntimeError('Internal error')

  # check card combination
  # see https://github.com/mnihyc/CCDDZ/blob/master/g_card.h

  # check if card idx all equals (at least 2)
  def __check_equals(self) -> bool:
    if len(self.cards) < 2:
      raise RuntimeError('Internal error')
    for i in range(1, len(self.cards)):
      if self.cards[i-1].get_idx() != self.cards[i].get_idx():
        return False
    return True

  # check if card idx is continuous (at least 2)
  def __check_continuous(self) -> bool:
    if len(self.cards) < 2:
      raise RuntimeError('Internal error')
    for i in range(1, len(self.cards)):
      if self.cards[i-1].get_idx()+1 != self.cards[i].get_idx()\
         and not (self.cards[i-1].get_idx()==13 and self.cards[i].get_idx()==21)\
         or (self.cards[i-1].get_idx()==21 and self.cards[i].get_idx()==22):
        return False
    return True

  # get card combination type, return [level, type, base]
  # level: 0->Illegal, 1->Normal, 2->Bomb, 3->KingBomb
  # type,base: see comments below
  def __get_type(self) -> list[int, int, int]:
    pass #TODO

  # compare cards
  def __lt__(self, other:Cards):
    match self.get_level() - other.get_level():
      case -3|-2|-1:
        return True
      case 2|1:
        return False

  # play cards
  def do_play(self, cards:Cards|list[Card]) -> None:
    if all(type(card) is Card for card in cards):
      pass
    elif type(cards) is Cards:
      cards = cards.cards
    else:
      raise RuntimeError('Internal error')
    for card in cards:
      try:
        self.cards.remove(card)
      except ValueError:
        raise RuntimeError('Internal error')

  # add new cards
  def do_add(self, cards:Cards|list[Card]) -> None:
    if all(type(card) is Card for card in cards):
      pass
    elif type(cards) is Cards:
      cards = cards.cards
    else:
      raise RuntimeError('Internal error')
    self.cards.extend(cards)
    self.cards.sort()

  # whether legal cards
  def __contains__(self, cards:list[Card]|Card) -> bool:
    if type(cards) is Card:
      return cards in self.cards
    elif type(cards) is list:
      for card in cards:
        if card not in self.cards:
          return False
    else:
      raise RuntimeError('Internal error')
    return True

  # get left card numbers
  def get_left(self) -> int:
    return len(self.cards)

  # get cards string
  def __str__(self):
    return ''.join(self.get_cards_str())

  # get cards string
  def get_cards_str(self) -> list[str]:
    return [str(card) for card in self.cards]


