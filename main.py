from cls.deck import Deck

'''
  Global entrance
'''
if __name__ == '__main__':
  print([str(i) for i in Deck().pcards])
  print(Deck().get_left())
