from typing import Self
from cls.error import InternalError
from cls.card import Card

class Cards:
    '''
        Cards consisting of Card
    '''
    __slots__ = ('_cards', )

    def __init__(self, cards: Self|list[Card]):
        '''
            initialize cards
        '''
        if all(type(card) is Card for card in cards):
            self._cards = sorted(cards)
        elif type(cards) is Cards:
            self._cards = sorted(cards.cards)
        else:
            raise InternalError('Invalid parameter type')

    # check card combination
    # see https://github.com/mnihyc/CCDDZ/blob/master/g_card.h

    def _check_equals(self, cnt:int = 99) -> bool:
        '''
            check if card idx all equals (at least 2)
        '''
        cards = self._cards
        if len(cards) < 2:
            raise InternalError('Cards not enough')
        for i in range(1, min(cnt, len(cards))):
            if int(cards[i-1]) != int(cards[i]):
                return False
        return True

    def _check_continuous(self, cnt:int = 99) -> bool:
        '''
            check if card idx is continuous (at least 2)
        '''
        cards = self._cards
        if len(cards) < 2:
            raise InternalError('Cards not enough')
        for i in range(1, min(cnt, len(cards))):
            # includes K A ; excludes A 2; excludes B R
            if int(cards[i-1])+1 != int(cards[i]) \
                 and not (str(cards[i-1])=='K' and str(cards[i])=='A') \
                 or (str(cards[i-1])=='A' and str(cards[i])=='2') \
                 or (str(cards[i])=='B' or str(cards[i])=='R'):
                return False
        return True

    def get_type(self) -> list[int, int, Card|int]:
        '''
            get card combination type, return [level, type, base]
            level: 0->Illegal, 1->Normal, 2->Bomb, 3->KingBomb
            base: first card of combination (including single)
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
        cards,lc = self._cards,len(self._cards)
        if lc == 0: return [0, 0, 0] # empty or invalid
        if lc == 4 and self._check_equals():
            return [2, 1, cards[0]] # Bomb
        if lc == 2 and cards[0].is_king and cards[1].is_king:
            return [3, 2, cards[0]] # KingBomb
        cnt,spt = 1,[[] for _ in range(5)]
        for i in range(1, lc):
            if int(cards[i-1]) != int(cards[i]):
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
        if len(spt[3])==2 and spt[3]._check_continuous(2):
            if lc==6:
                return [1, 8, spt[3][0]] # 2x Triple
            if lc==8 and (len(spt[1])==2 or len(spt[2])==1):
                return [1, 9, spt[3][0]] # 3/3/1+1
            if lc==10 and len(spt[2])==2:
                return [1, 10, spt[3][0]] # 3/3/2/2
        if len(spt[3])==3 and spt[3]._check_continuous(3):
            if lc==9:
                return [1, 11, spt[3][0]] # 3x Triple
            if lc==12 and (len(spt[1])==3 or (len(spt[2])==1 and len(spt[1])==1)):
                return [1, 12, spt[3][0]] # 3x 3 / 1+2|1+1+1
            if lc==15 and len(spt[2])==3:
                return [1, 13, spt[3][0]] # 3x 3 / 3x 2
        if len(spt[3])==4 and spt[3]._check_continuous(4):
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
            if spt[1]._check_continuous():
                return [1, 19+lc-5, spt[1][0]] # ~
        if lc>=6 and len(spt[1])==0 and len(spt[3])==0 and len(spt[4])==0:
            if spt[2]._check_continuous():
                return [1, 27+lc//2-3, spt[2][0]] # ~~
        return [0, 0, 0] # empty or invalid

    @property
    def multiplier(self) -> int:
        '''
            get multiplier of card combination
        '''
        return [0, 1, 2, 2][self.get_type()[0]]

    def __lt__(self, other: Self):
        '''
            compare cards
        '''
        t1,t2 = self.get_type(),other.get_type()
        match t1[0] - t2[0]:
            case -3|-2|-1:
                return True
            case 2|1:
                return False
        return t1[1] == t2[1] and int(t1[2]) < int(t2[2])

    def do_remove(self, cards: Self|list[Card]) -> Self:
        '''
            remove cards
        '''
        if type(cards) is list and all(type(card) is Card for card in cards):
            pass
        elif type(cards) is Cards:
            cards = cards.cards
        else:
            raise InternalError('Invalid parameter type')
        for card in cards:
            try:
                self._cards.remove(card)
            except ValueError:
                raise InternalError('Card not found')
        return self

    def do_add(self, cards: Self|list[Card]) -> Self:
        '''
            add new cards
        '''
        if type(cards) is list and all(type(card) is Card for card in cards):
            pass
        elif type(cards) is Cards:
            cards = cards.cards
        else:
            raise InternalError('Invalid parameter type')
        self._cards.extend(cards)
        self._cards.sort()
        return self
    
    @property
    def cards(self) -> list[Card]:
        '''
            get cards
        '''
        return self._cards

    def __contains__(self, cards: Self|list[Card]|Card) -> bool:
        '''
            whether contains (in self)
        '''
        if type(cards) is Card:
            return cards in self._cards
        elif type(cards) is Cards:
            cards = cards.cards
        if type(cards) is list:
            for card in cards:
                if card not in self._cards:
                    return False
        else:
            raise InternalError('Invalid parameter type')
        return True

    @property
    def length(self) -> int:
        '''
            get cards count
        '''
        return len(self._cards)

    def __str__(self):
        '''
            get cards string
            format: '390JB'
        '''
        return ''.join(self.cards_str)

    @property
    def cards_str(self) -> list[str]:
        '''
            get cards string list
            format: ['3','9','0','J','B']
        '''
        return [str(card) for card in self._cards]
    
    def __repr__(self):
        '''
            get cards string
            format: '3C 9H 10D JS B'
        '''
        return ' '.join(self.cards_repr)
    
    @property
    def cards_repr(self) -> list[str]:
        '''
            get cards string list
            format: ['3C','9H','10D','JS','B']
        '''
        return [repr(card) for card in self._cards]

    def __getitem__(self, idx):
        '''
            rewrite [] by index
        '''
        return self._cards[idx]

    def __len__(self):
        '''
            rewrite len()
        '''
        return len(self._cards)

    def __iter__(self):
        '''
            rewrite iter()
        '''
        return iter(self._cards)
