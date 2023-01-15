from cls.error import InternalError

class Card:
    '''
        A single card
    ''' 
    __slots__ = ('_idx', '_suit', )
    
    def __init__(self, idx:int|str, suit:int|str|None = None):
        '''
            initialize a card
            
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
                    raise InternalError('Invalid card index given')
                self._idx = idx
            case str():
                if len(idx) < 1:
                    raise InternalError('Invalid card string given')
                match c:=idx[0].upper():
                    case c if c in [str(i) for i in range(3, 9+1)]:
                        self._idx = int(idx[0])
                    case '0':
                        self._idx = 10
                    case '1' if len(idx) > 1 and idx[:2] == '10':
                        self._idx = 10
                    case 'J' | 'Q' | 'K':
                        self._idx = 11 if c == 'J' else 12 if c == 'Q' else 13
                    case 'A' | '2':
                        self._idx = 21 if c == 'A' else 22
                    case 'B':
                        self._idx = 31
                    case 'R':
                        self._idx = 32
                    case _:
                        raise InternalError('Invalid card string given')
            case _:
                raise InternalError('Invalid parameter type')
        match suit:
            case int():
                if suit not in range(4):
                    raise InternalError('Invalid card suit given')
                self._suit = ['S', 'H', 'C', 'D'][suit]
            case str():
                self._suit = suit.upper()
            case None if not self.is_king:
                if type(idx) is not str or len(idx) < 2:
                    raise InternalError('Missing card suit')
                self._suit = idx[-1].upper()
            case None if self.is_king:
                self._suit = None
            case _:
                raise InternalError('Invalid parameter type')
        if self._suit not in ['S', 'H', 'C', 'D', None] or (self.is_king and self._suit is not None):
            raise InternalError('Invalid card suit given')
    
    @property
    def is_king(self) -> bool:
        '''
            whether is king card
        '''
        return self._idx in [31, 32]

    def __lt__(self, other):
        '''
            card sorting
        '''
        if type(other) is not Card:
            raise InternalError('Invalid comparsion')
        if self._idx != other.idx:
            return self._idx < other.idx
        return self._suit < other.suit

    def __eq__(self, other):
        '''
            card equality
        '''
        if type(other) is not Card:
            raise InternalError('Invalid comparsion')
        return self._idx == other.idx and self._suit == other.suit
    
    @property
    def idx(self) -> int:
        '''
            get card index
        '''
        return self._idx
    
    @property
    def idx_str(self) -> str:
        '''
            get card index string
            format: 'A'; '0'; 'B'
        '''
        return self.__str__()

    @property
    def suit(self) -> str:
        '''
            get card suit
            format: 'S'; 'H'; 'C'; 'D'
        '''
        return self._suit

    def __int__(self):
        '''
            get card index
        '''
        return self._idx

    def __str__(self):
        '''
            card shown
            format: 'A'; '0'; 'B'
        '''
        idx = self._idx
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
                raise InternalError('Internal error')
        return idx
    
    def __repr__(self):
        '''
            card shown (full)
            format: 'AS'; '10C'; 'B'
        '''
        s = '10' if self._idx == 10 else self.__str__()
        if self._suit is not None:
            s += self._suit
        return s
