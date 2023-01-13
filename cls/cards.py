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
    def __check_equals(self, cnt:int = 99) -> bool:
        cards = self.cards
        if len(cards) < 2:
            raise RuntimeError('Internal error')
        for i in range(1, min(cnt, len(cards))):
            if cards[i-1].get_idx() != cards[i].get_idx():
                return False
        return True

    # check if card idx is continuous (at least 2)
    def __check_continuous(self, cnt:int = 99) -> bool:
        cards = self.cards
        if len(cards) < 2:
            raise RuntimeError('Internal error')
        for i in range(1, min(cnt, len(cards))):
            # includes K A ; excludes A 2
            if cards[i-1].get_idx()+1 != cards[i].get_idx()\
                 and not (cards[i-1].get_idx()==13 and cards[i].get_idx()==21)\
                 or (cards[i-1].get_idx()==21 and cards[i].get_idx()==22):
                return False
        return True

    # get card combination type, return [level, type, base]
    # level: 0->Illegal, 1->Normal, 2->Bomb, 3->KingBomb
    # type,base: see comments below
    def __get_type(self) -> list[int, int, Card|int]:
        cards,lc = self.cards,len(self.cards)
        if lc == 0: return [0, 0, 0] # empty or invalid
        if lc == 4 and self.__check_equals():
            return [2, 1, cards[0]] # Bomb
        if lc == 2 and [cards[0].get_idx(),cards[1].get_idx()] == [31,32]:
            return [3, 2, 32] # KingBomb
        cnt,spt = 1,[[] for _ in range(5)]
        for i in range(1, lc):
            if cards[i-1].get_idx() != cards[i].get_idx():
                spt[cnt].append(cards[i-1])
                cnt = 1
            else:
                cnt += 1
        spt[cnt].append(cards[lc-1])
        spt = [Cards(e) for e in spt]
        if lc==1:
            return [1, 3, cards[0]] # Single
        if lc==2 and len(spt[2])==1:
            return [1, 4, cards[0]] # Double
        if len(spt[3])==1:
            if lc==3:
                return [1, 5, cards[0]] # Triple
            if lc==4 and len(spt[1])==1:
                return [1, 6, spt[3][0]] # 3/1
            if lc==5 and len(spt[2])==1:
                return [1, 7, spt[3][0]] # 3/2
        if len(spt[3])==2 and spt[3].__check_continuous(2):
            if lc==6:
                return [1, 8, spt[3][0]] # 2x Triple
            if lc==8 and (len(spt[1])==2 or len(spt[2])==1):
                return [1, 9, spt[3][0]] # 3/3/1+1
            if lc==10 and len(spt[2])==2:
                return [1, 10, spt[3][0]] # 3/3/2/2
        if len(spt[3])==3 and spt[3].__check_continuous(3):
            if lc==9:
                return [1, 11, spt[3][0]] # 3x Triple
            if lc==12 and (len(spt[1])==3 or (len(spt[2])==1 and len(spt[1])==1)):
                return [1, 12, spt[3][0]] # 3x 3 / 1+2|1+1+1
            if lc==15 and len(spt[2])==3:
                return [1, 13, spt[3][0]] # 3x 3 / 3x 2
        if len(spt[3])==4 and spt[3].__check_continuous(4):
            if lc==12:
                return [1, 14, spt[3][0]] # 4x Triple
            if lc==16 and (len(spt[1])==4 or len(spt[2])==2 or (len(spt[1])==1 and len(spt[3])==1)):
                return [1, 15, spt[3][0]] # 4x 3 / 1+3|2+2|1+1+1+1
            if lc==20 and len(spt[2])==4:
                return [1, 16, spt[3][0]] # 4x 3 / 4x 2
        if len(spt[4])==1:
            if lc==6 and (len(spt[1])==2 or len(spt[2])==1):
                return [1, 17, spt[4][0]] # 4/1+1
            if lc==8 and len(spt[2])==2:
                return [1, 18, spt[4][0]] # 4/2/2
        if len(spt[4])==2 and lc==8:
            return [1, 18, spt[4][1]] # 4/2/2
        if lc>=5 and len(spt[2])==0 and len(spt[3])==0 and len(spt[4])==0:
            if spt[1].__check_continuous():
                return [1, 19+lc-5, spt[1][0]] # ~
        if lc>=6 and len(spt[1])==0 and len(spt[3])==0 and len(spt[4])==0:
            if spt[2].__check_continuous():
                return [1, 27+lc//2-3, spt[2][0]] # ~~
        return [0, 0, 0] # empty or invalid

    # compare cards
    def __lt__(self, other:Cards):
        t1,t2 = self.__get_type(),other.__get_type()
        print(str(other), t2)
        match t1[0] - t2[0]:
            case -3|-2|-1:
                return True
            case 2|1:
                return False
        return t1[1] == t2[1] and int(t1[2]) < int(t2[2])

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
    def __contains__(self, cards:Cards|list[Card]|Card) -> bool:
        if type(cards) is Card:
            return cards in self.cards
        elif type(cards) is Cards:
            cards = cards.cards
        if type(cards) is list:
            rmcards = self.cards.copy() # TODO: slow
            for card in cards:
                if card not in rmcards:
                    return False
                else:
                    rmcards.remove(card) # identical TODO: color, style
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

    # rewrite []
    def __getitem__(self, idx):
        if not (0 <= idx <= len(self.cards)):
            raise RuntimeError('Internal error')
        return self.cards[idx]

    # rewrite len()
    def __len__(self):
        return len(self.cards)
