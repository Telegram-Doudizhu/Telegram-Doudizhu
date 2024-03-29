from uuid import uuid4
from random import randint
from cls.error import InternalError
from cls.cards import Cards
from cls.deck import Deck

class Room:
    '''
        A room in the game.
    '''
    __slots__ = ('_id', '_chatid', '_state', '_users', '_deck', '_bids', '_bidcount', '_lordcard', '_lastplayed', 'multiplier', )
    
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
        
        hard_list = ('Placeholder', 'Stupid', )
        
        def __init__(self, hard:int = -1):
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
        self._bids = [0, 0, 0]
        self._bidcount = 0
        self._lordcard = None
        self._lastplayed = Cards([])
        self.multiplier = 1 # controller outside
    
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
            return True if succeeded, otherwise error message
        '''
        if self.state != Room.STATE_JOINING:
            return f'Room state mismatch, STATE_JOINING expected, int:{self.state} found'
        if self.user1 is None or self.user2 is None:
            return 'Not enough players'
        self.state = Room.STATE_DECIDING
        self.cur = randint(0, 2) # randomly choose a beginner
        return True
    
    def reset(self) -> None:
        '''
            reset the room
        '''
        # state verification may be added here; TODO
        self._deck = Deck()
        self._bids = [0, 0, 0]
        self._bidcount = 0
        self._lordcard = None
        self._lastplayed = Cards([])
        self.state = Room.STATE_JOINING
        self.multiplier = 1 # controller outside

    @property
    def cur(self) -> int:
        '''
            get current player
        '''
        return self._deck.get_cur()
    
    @cur.setter
    def cur(self, idx: int) -> None:
        '''
            set current player
        '''
        if not 0 <= idx < 3:
            raise InternalError('Invalid player index int:{idx} given')
        while self._deck.get_cur() != idx:
            self.next()
    
    @property
    def lastcur(self) -> int:
        '''
            get last player
        '''
        return self._deck.get_lastcur()
    
    def next(self) -> None:
        '''
            move to next player
        '''
        self._deck.move_next()
    
    @property
    def user(self) -> User|Robot:
        '''
            get current user
        '''
        return self._users[self.cur]

    def user_index(self, user: User|int) -> int:
        '''
            get user index (by essentially userid)
            return -1 if not found
        '''
        if type(user) is Room.User:
            user = user.id
        elif type(user) is not int:
            raise InternalError(f'Invalid user type {type(user)} given')
        for i, u in enumerate(self._users):
            if u is not None and u.id == user:
                return i
        return -1

    @property
    def bid(self) -> int:
        '''
            get bid of current player
        '''
        return self._bids[self.cur]
    
    def decide_lord(self, idx: int) -> bool|str:
        '''
            decide lord and reset self.cur
            return True if succeeded, otherwise error message
        '''
        if not 0 <= idx < 3:
            raise InternalError('Invalid player index int:{idx} given')
        if self.state != Room.STATE_DECIDING:
            return f'Room state mismatch, STATE_DECIDING expected, int:{self.state} found'
        self._lordcard = self._deck.decide_lord(idx)
        self.state = Room.STATE_PLAYING
        return True

    @property
    def lord(self) -> bool|int:
        '''
            get lord index
            return False if not decided
        '''
        if 0 in self._bids:
            return False
        if 2 in self._bids:
            return self._bids.index(2)
        if self._bids.count(1) > 1:
            return False
        if max(self._bids) < 0:
            return False
        return self._bids.index(max(self._bids))

    @property
    def lord_cards(self) -> Cards:
        '''
            get three additional lord cards
        '''
        return self._lordcard

    def next_bid(self) -> bool:
        '''
            move to next available player for bidding
            return True if succeeded, False if all passed (needs a reset)
        '''
        if all(b < 0 for b in self._bids):
            return False
        self.next()
        while self.bid < 0:
            self.next()
        return True

    def bids(self, bid: bool) -> bool|str:
        '''
            bid for lord (current player)
            return True if succeeded, otherwise error message
        '''
        if self.state != Room.STATE_DECIDING:
            return f'Room state mismatch, STATE_DECIDING expected, int:{self.state} found'
        if self.bid < 0:
            raise InternalError(f'Invalid bid state, unexpected int:{self.bid}')
        if bid:
            self._bids[self.cur] += 1
        else:
            self._bids[self.cur] = self._bidcount - 10
        self._bidcount += 1
        return True
    
    @property
    def must(self) -> bool:
        '''
            check whether current player must play
        '''
        return self._deck.must_play()

    def playable(self, cards: Cards) -> bool:
        '''
            check whether cards are playable
        '''
        return self._deck.check_playable(cards)

    def play(self, cards: Cards) -> bool|str:
        '''
            play cards (current player)
            self.cur moves to the next player after calling this
            return True if succeeded, otherwise error message
        '''
        if self.state != Room.STATE_PLAYING:
            return f'Room state mismatch, STATE_PLAYING expected, int:{self.state} found'
        if not self._deck.check_playable(cards):
            return 'Unplayable cards'
        self._deck.do_play(cards)
        self._lastplayed = cards
        return True
    
    @property
    def cards(self) -> Cards:
        '''
            get cards of current player
        '''
        return self._deck.get_cards(self.cur)

    @property
    def lastcards(self) -> Cards:
        '''
            get last player's cards
        '''
        return self._deck.get_cards(self.lastcur)

    @property
    def lastvcards(self) -> Cards:
        '''
            get last valid played cards (notice: not last player's cards)
        '''
        return self._deck.get_lastvcards()

    @property
    def lastplayed(self) -> Cards:
        '''
            get last played cards
        '''
        return self._lastplayed

    def user_cards(self, idx:int) -> Cards|str:  
        '''
            get all cards in the player's hand
        '''
        if not 0 <= idx < 3:
            raise InternalError('Invalid player index int:{idx} given')
        if self.state != Room.STATE_DECIDING and self.state != Room.STATE_PLAYING:
            return f'Room state mismatch, STATE_DECIDING or STATE_PLAYING expected, int:{self.state} found'
        return self._deck.get_cards(idx)

    @property
    def lastwin(self) -> bool|int:
        '''
            check whether game is over
            must be called directly after self.play()
            return False if not, otherwise winner index
        '''
        lastcur = self._deck.get_lastcur()
        if self._deck.get_cards(lastcur).length == 0:
            return lastcur
        return False
    
    @property
    def win(self) -> bool|int:
        '''
            check whether game is over
            return False if not, otherwise winner index
        '''
        for i in range(3):
            if self._deck.get_cards(i).length == 0:
                return i
        return False

    @property
    def is_first(self) -> bool:
        '''
            check whether current player is first player
        '''
        return self._deck.is_first()
    

    