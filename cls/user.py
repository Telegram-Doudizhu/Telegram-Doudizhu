import sqlite3

class User:
    '''
        A single user
    '''
    __slots__ = ('_id', '_beans', '_win', '_played', '_db', '_cur', )

    def __init__(self, id):
        self._id = id
        self._beans = 1000
        self._win = 0
        self._played = 0

        self._db = sqlite3.connect('users.db')
        self._cur = self._db.cursor()

        self._create_table()

        self._cur.execute("SELECT * FROM users WHERE id=?", (id,))
        result = self._cur.fetchone()
        if result is not None:
            self._beans = result[1]
            self._win = result[2]
            self._played = result[3]
        else:
            self._cur.execute("INSERT INTO users (id, beans, win, played) VALUES (?, ?, ?, ?)", (id, 1000, 0, 0))
            self._db.commit()

    def __del__(self):
        self._db.close()

    def _create_table(self):
        '''
            create a table that includes the user's telegram id,
            the number of beans they have, the number of games they have won,
            and the total number of games they have played.

            id (telegram id - unique) -> INT
            beans (the number of beans they have) -> INT
            win (the number of games they have won) -> INT
            played (the total games they have played) -> INT
        '''
        self._cur.execute('''CREATE TABLE IF NOT EXISTS users
                            (id    INT PRIMARY KEY NOT NULL,
                            beans  INT             NOT NULL,
                            win    INT             NOT NULL,
                            played INT             NOT NULL);''')
        self._db.commit()

    @property
    def id(self) -> int:
        '''
            user's telegram id
        '''
        return self._id

    @property
    def beans(self) -> int:
        '''
            user's beans
        '''
        return self._beans
    @beans.setter
    def beans(self, value: int):
        self._beans = value

    @property
    def win(self) -> int:
        '''
            the number of games the user have won
        '''
        return self._win
    @win.setter
    def win(self, value: int):
        self._win = value

    @property
    def played(self) -> int:
        '''
            the total games the user have played
        '''
        return self._played
    @played.setter
    def played(self, value: int):
        self._played = value

    def _update_user_data(self, beans: int = None, win: int = None, played: int = None) -> None:
        '''
            update user's data in database
        '''
        if beans is not None:
            self._beans = beans
        if win is not None:
            self._win = win
        if played is not None:
            self._played = played
        self._cur.execute("UPDATE users SET beans=?, win=?, played=? WHERE id=?", (self._beans, self._win, self._played, self._id))
        self._db.commit()