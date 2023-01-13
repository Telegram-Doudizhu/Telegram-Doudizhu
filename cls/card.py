
'''
    A single card
'''
class Card:
    
    # idx mapping rules (natural)
    # 3..10 -> 3..10
    # J,Q,K -> 11,12,13
    # A,2 -> 21,22
    # BlackKing -> 31
    # RedKing -> 32
    def __init__(self, idx:int|str):
        if type(idx) is int:
            self.idx = idx
        elif type(idx) is str:
            idx = idx.upper()
            if idx in [str(i) for i in range(3, 9+1)]:
                self.idx = int(idx)
            elif idx == '0':
                self.idx = 10
            elif idx in ['J', 'Q', 'K']:
                self.idx = 11 if idx == 'J' else 12 if idx == 'Q' else 13
            elif idx in ['A', '2']:
                self.idx = 21 if idx == 'A' else 22
            elif idx in ['BK', 'B', 'XW']:
                self.idx = 31
            elif idx in ['RK', 'R', 'DW']:
                self.idx = 32
            else:
                raise RuntimeError('Internal error')
        else:
            raise RuntimeError('Internal error')

    # card sorting (NOT IDX)
    def __lt__(self, other):
        if type(other) is int:
            return self.idx < other.idx
        # color TODO
        return self.idx < other.idx

    # card equality (NOT IDX)
    def __eq__(self, other):
        if type(other) is int:
            return self.idx == other.idx
        # color TODO
        return self.idx == other.idx

    # get card idx
    def get_idx(self) -> int:
        return self.idx

    # get card idx
    def __int__(self):
        return self.idx

    # card shown
    def __str__(self):
        idx = self.idx
        if 3 <= idx < 10:
            return str(idx)
        elif idx == 10:
            return '0'
        elif 11 <= idx <= 13:
            return ['J', 'Q', 'K'][idx - 11]
        elif 21 <= idx <= 22:
            return ['A', '2'][idx - 21]
        elif idx == 31:
            return 'B'
        elif idx == 32:
            return 'R'
        else:
            raise RuntimeError('Internal error')
