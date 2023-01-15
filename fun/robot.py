import random
from cls.cards import Cards
from cls.room import Room

def will_robot_bid(room: Room) -> bool:
    '''
        return whether the robot will bid
    '''
    return random.random() < 0.5

def what_robot_play(room: Room) -> Cards:
    '''
        return what the robot will play
    '''
    return Cards([])

__all__ = ('will_robot_bid', 'what_robot_play', )