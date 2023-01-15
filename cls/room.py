from uuid import uuid4
from cls.deck import Deck

class Room:
    '''
        A room in the game.
    '''
    __slots__ = ('_id', '_chatid', '_state', '_users', '_deck', )
    
    (
        STATE_CREATE,  # should not appear
        STATE_JOINING, # waiting for players to join
        STATE_DECIDING,# deciding lord
        STATE_PLAYING, # playing
        STATE_END,     # should not appear
    ) = range(5)
    
    class User:
        __slots__ = ('_id', '_name', )
        
        def __init__(self, userid: int, name: str):
            self._id = userid
            self._name = name
        
        @property
        def id(self) -> int:
            return self._id
        
        @property
        def name(self) -> str:
            return self._name

    class Robot:
        __slots__ = ('_hard', )
        
        hard_list = ('Stupid', 'Easy', 'Hard', 'Hell', )
        
        def __init__(self, hard:int = 0):
            self._hard = hard
        
        @property
        def hard(self) -> int:
            return self._hard
        
        @property # compatibility
        def id(self) -> int:
            return -1

        @property
        def name(self) -> str:
            hard = self.hard_list[self._hard]
            return f"Robot (mode: {hard})"

    def __init__(self, chatid: int, owner: User):
        self._id = str(uuid4())
        self._chatid = chatid
        self._state = Room.STATE_CREATE
        self._users = [owner, None, None]
        self._deck = Deck()
    
    @property
    def id(self) -> str:
        '''
            get room id
        '''
        return self._id
    
    @property
    def chatid(self) -> int:
        '''
            get chat id
        '''
        return self._chatid
    
    @property
    def owner(self) -> User:
        '''
            get owner
        '''
        return self._users[0]
    
    @property
    def users(self) -> list[None|User|Robot]:
        '''
            get all users
        '''
        return self._users

    @property
    def user1(self) -> None|User|Robot:
        '''
            get user 1
        '''
        return self._users[1]
    
    @property
    def user2(self) -> None|User|Robot:
        '''
            get user 2
        '''
        return self._users[2]

    @property
    def state(self) -> int:
        '''
            get room state
        '''
        return self._state
    
    @state.setter
    def state(self, v: int) -> None:
        '''
            set room state
        '''
        self._state = v
    
    def start(self) -> bool|str:
        '''
            start the room
            return True if succeed otherwise error message
        '''
        if self.state != Room.STATE_JOINING:
            return f'Room state mismatch, STATE_JOINING expected, int:{self.state} given'
        if self.user1 is None or self.user2 is None:
            return 'Not enough players'
        self.state = Room.STATE_DECIDING
        return True
    
    
