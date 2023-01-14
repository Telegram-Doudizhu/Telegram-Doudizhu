from uuid import uuid4
from cls.deck import Deck

class Room:
    '''
        A room in the game.
    '''
    __slots__ = ('id', 'state', 'deck', 'chatid', )
    
    STATE_CREATE = 0
    STATE_JOINING = 1
    STATE_DECIDING = 2
    STATE_WAITING = 3
    STATE_END = 4

    def __init__(self, chatid: int):
        self.id = uuid4()
        self.state = Room.STATE_CREATE
        self.deck = Deck()
        self.chatid = chatid
        
    # TODO
    
