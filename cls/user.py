from typing import Any
from cls.dbs import Database

class User(Database):
    '''
        A single user (without cache, immediate, allow multiple instances)
    '''
    __slots__ = ('_uid', )

    TABLE = 'users'
    
    def __init__(self, uid: int):
        '''
            initialize user
        '''
        self._uid = uid
        if len(self.query(self.TABLE, ['uid'], [['uid', '=', uid]])) == 0:
            self.insert(self.TABLE, {'uid': uid})
    
    def get(self, *args) -> list[Any]:
        '''
            get user info
        '''
        return self.query(self.TABLE, args, [['uid', '=', self._uid]])[0]
    
    def getall(self) -> dict[str, Any]:
        '''
            get user all info
        '''
        return self.query(self.TABLE, ['*'], [['uid', '=', self._uid]], return_map = True)[0]
    
    def set(self, **kwargs) -> None:
        '''
            set user info
        '''
        self.update(self.TABLE, kwargs, [['uid', '=', self._uid]])
    
