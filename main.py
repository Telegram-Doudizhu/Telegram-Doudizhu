from cls.deck import Deck
from cls.card import Card
from cls.cards import Cards

'''
  Global entrance
'''
if __name__ == '__main__':
  d = Deck()
  print([str(i) for i in d.pcards])
  print(str(d.tcards))
  d.decide_lord(2)
  while True:
    print(f'player {d.get_cur()} card {d.get_cards()}')
    c = Cards([Card(s) for s in input(f'Play{d.get_cur()} > ')])
    while not d.check_playable(c):
      c = Cards([Card(s) for s in input(f'Play{d.get_cur()} > ')])
    d.do_play(c); print(f'player {d.get_lastcur()} left {d.get_lastleft()}')
    if not d.get_lastleft():
      break
  print('Finished')
