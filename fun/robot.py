import random
from cls.error import InternalError
from cls.cards import Cards
from cls.room import Room

def will_robot_bid(room: Room) -> bool:
    '''
        return whether the robot will bid
    '''
    if type(room.user) is not Room.Robot:
        raise InternalError(f'User type mismatch, Robot expected, {type(room.user)} found')
    return random.random() < 0.5

def what_robot_play(room: Room) -> Cards:
    '''
        return what the robot will play
    '''
    if type(room.user) is not Room.Robot:
        raise InternalError(f'User type mismatch, Robot expected, {type(room.user)} found')
    if room.must:
        return Cards([room.cards[0]])
    return Cards([])

__all__ = ('will_robot_bid', 'what_robot_play', )