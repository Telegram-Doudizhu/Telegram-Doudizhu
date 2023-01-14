from cls.room import Room

run_context_roomid: dict[int, Room] = {}
run_context_userid: dict[int, Room] = {}

@classmethod
def from_roomid(cls, roomid: int) -> None|Room:
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

def create_room(chatid: int, players: list[int]) -> Room:
    '''
        create a room
    '''
    room = Room(chatid)
    run_context_roomid[room.id] = room
    # TODO, not simple like this
    for player in players:
        run_context_userid[player] = room
    return room

__all__ = ('create_room', )
