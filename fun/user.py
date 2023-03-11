from cls.user import User

def update_user_data(user: User, result: bool, multiple: int):
    '''
        update user data based on user, result (win or lose) and multiplier
    '''
    beans, win, played = user.beans, user.win, user.played
    played += 1
    if result is True:
        win += 1
        beans += 100 * multiple
    else:
        beans -= 100 * multiple
    user._update_user_data(beans, win, played)

__all__ = ()
