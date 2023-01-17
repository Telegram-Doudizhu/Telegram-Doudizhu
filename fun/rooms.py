from typing import Any
from cls.error import InternalError
from cls.room import Room

run_context_roomid: dict[str, Room] = {}
run_context_userid: dict[int, Room] = {}
run_context_roomdata: dict[str, list[Any]] = {}

@classmethod
def from_roomid(cls, roomid: str) -> None|Room:
    '''
        get room from roomid
        return None if not found
    '''
    return run_context_roomid.get(roomid, None)
Room.from_roomid = from_roomid

@classmethod
def from_userid(cls, userid: int) -> None|Room:
    '''
        get room from userid
        return None if not found
    '''
    return run_context_userid.get(userid, None)
Room.from_userid = from_userid

@property
def actionid(self: Room) -> None|str:
    '''
        get room actionid
    '''
    return run_context_roomdata.get(self.id, [None])[0]
Room.actionid = actionid

@property
def roomdata(self: Room) -> None|list[Any]:
    '''
        get room data
    '''
    return run_context_roomdata.get(self.id, None)
@roomdata.setter
def roomdata(self: Room, roomdata: None|list[Any]) -> None:
    '''
        set room data
    '''
    if type(roomdata) is not list:
        roomdata = [roomdata]
    run_context_roomdata[self.id] = roomdata
Room.roomdata = roomdata

@classmethod
def create(cls, chatid: int, owner: Room.User) -> bool|Room:
    '''
        create a new room (Room.STATE_CREATE, empty)
        return False if owner already in a room
    '''
    if Room.from_userid(owner.id) is not None:
        return False
    room = cls(chatid, owner)
    room.state = Room.STATE_JOINING
    run_context_roomid[room.id] = room
    run_context_userid[owner.id] = room
    return room
Room.create = create

def destroy(self: Room) -> None:
    '''
        destroy the room
    '''
    del run_context_roomid[self.id]
    for user in self._users:
        if type(user) is Room.User:
            del run_context_userid[user.id]
    self.state = Room.STATE_END
Room.destroy = destroy

def _join(self: Room, pos: int, user: Room.User|Room.Robot) -> bool|str:
    '''
        join a user to the room
        return True if succeeded, otherwise error message
    '''
    if self.state != Room.STATE_JOINING:
        return f'Room state mismatch, STATE_JOINING expected, int:{self.state} found'
    if self._users[pos] is not None:
        return f'Room position {pos} occupied'
    if type(user) is Room.User:
        if Room.from_userid(user.id) is not None:
            return 'You are already in a room'
        run_context_userid[user.id] = user
    self._users[pos] = user
    return True
Room._join = _join
Room.join1 = lambda self, user: self._join(1, user)
Room.join2 = lambda self, user: self._join(2, user)

def _leave(self: Room, pos: int) -> bool|str:
    '''
        leave a user from the room
        return True if succeeded, otherwise error message
    '''
    if self.state != Room.STATE_JOINING:
        return f'Room state mismatch, STATE_JOINING expected, int:{self.state} found'
    user = self._users[pos]
    if user is None:
        return f'Room position {pos} empty'
    self._users[pos] = None
    if type(user) is Room.User:
        del run_context_userid[user.id]
    return True
Room._leave = _leave
Room.leave1 = lambda self: self._leave(1)
Room.leave2 = lambda self: self._leave(2)
    
__all__ = ()
