class Card:
    '''
        A single card
    ''' 
    __slots__ = ('idx', 'suit',)
    
    def __init__(self, idx:int|str, suit:int|str|None = None):
        '''
            Initialize a card
            
            idx mapping rules (natural)
            3..10 -> 3..10
            J,Q,K -> 11,12,13
            A,2 -> 21,22
            BlackKing -> 31
            RedKing -> 32
            suit mapping rules
            0 -> Spade
            1 -> Heart
            2 -> Club
            3 -> Diamond
        '''
        match idx:
            case int():
                if idx not in range(3, 32+1):
                    raise RuntimeError('Invalid card index given')
                self.idx = idx
            case str():
                match c:=idx[0].upper():
                    case c if c in [str(i) for i in range(3, 9+1)]:
                        self.idx = int(idx[0])
                    case '0':
                        self.idx = 10
                    case '1' if len(idx) > 1 and idx[:2] == '10':
                        self.idx = 10
                    case 'J' | 'Q' | 'K':
                        self.idx = 11 if idx == 'J' else 12 if idx == 'Q' else 13
                    case 'A' | '2':
                        self.idx = 21 if idx == 'A' else 22
                    case 'B':
                        self.idx = 31
                    case 'R':
                        self.idx = 32
                    case _:
                        raise RuntimeError('Invalid card str given')
            case _:
                raise RuntimeError('Invalid parameter type')
        match suit:
            case int():
                if suit not in range(4):
                    raise RuntimeError('Invalid card suit given')
                self.suit = ['S', 'H', 'C', 'D'][suit]
            case str():
                self.suit = suit.upper()
            case None if not self.is_king():
                if type(idx) is not str or len(idx) < 2:
                    raise RuntimeError('Missing card suit')
                self.suit = idx[-1].upper()
            case None if self.is_king():
                self.suit = None
            case _:
                raise RuntimeError('Invalid parameter type')
        if self.suit not in ['S', 'H', 'C', 'D', None] or (self.is_king() and self.suit is not None):
            raise RuntimeError('Invalid card suit given')
    
    def is_king(self) -> bool:
        '''
            whether is king
        '''
        return self.idx in [31, 32]

    def __lt__(self, other):
        '''
            card sorting
        '''
        if type(other) is not Card:
            raise RuntimeError('Invalid comparsion')
        if self.idx != other.idx:
            return self.idx < other.idx
        return self.suit < other.suit

    def __eq__(self, other):
        '''
            card equality
        '''
        if type(other) is not Card:
            raise RuntimeError('Invalid comparsion')
        return self.idx == other.idx and self.suit == other.suit

    def get_idx(self) -> int:
        '''
            get card index
        '''
        return self.idx
    
    def get_idx_str(self) -> str:
        '''
            get card index string
            format: A, 0, B
        '''
        return self.__str__()

    def get_suit(self) -> str:
        '''
            get card suit
            format: S, H, C, D
        '''
        return self.suit

    def __int__(self):
        '''
            get card index
        '''
        return self.idx

    def __str__(self):
        '''
            card shown
            format: A, 0, B
        '''
        idx = self.idx
        match idx:
            case idx if 3 <= idx < 10:
                idx = str(idx)
            case 10:
                idx = '0'
            case 11 | 12 | 13:
                idx = ['J', 'Q', 'K'][idx - 11]
            case 21 | 22:
                idx = ['A', '2'][idx - 21]
            case 31:
                idx = 'B'
            case 32:
                idx = 'R'
            case _:
                raise RuntimeError('Internal error')
        return idx
    
    def __repr__(self):
        '''
            card shown (full)
            format: AS, 10C, B
        '''
        s = '10' if self.idx == 10 else self.__str__()
        if self.suit is not None:
            s += self.suit
        return s
