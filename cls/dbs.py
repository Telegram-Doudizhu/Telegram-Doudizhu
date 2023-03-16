from typing import Any
from cls.error import InternalError

import logging
logging.basicConfig(level = logging.INFO, format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
logger = logging.getLogger(__name__)

import sqlite3
db = sqlite3.connect('users.db')
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users
               (uid    BIGINT PRIMARY KEY NOT NULL,
                beans  INT   NOT NULL DEFAULT 1000,
                win    INT   NOT NULL DEFAULT 0,
                played INT   NOT NULL DEFAULT 0);''')
db.commit()

class Database:
    '''
        Underlying database class
    '''
    
    def query(self, table: str, column: list[str], cond: list[list[str, str, Any]], return_map = False) -> list[list[Any]]|list[dict[str, Any]]:
        '''
            Query the database.
            defaults to AND for cond
        '''
        if not isinstance(table, str):
            raise InternalError(f'Invalid parameter type, str expected, {type(table)} found.')
        if not isinstance(column, list) or not all(isinstance(c, str) for c in column):
            raise InternalError('Invalid parameter type, list[str] expected.')
        if not isinstance(cond, list) or not all(isinstance(c, list) and len(c)==3 and isinstance(c[0], str) and isinstance(c[1], str) for c in cond):
            raise InternalError('Invalid parameter type, list[list[str, str, Any]] expected.')
        try:
            cur.execute(f'SELECT {", ".join(column)} FROM {table} WHERE {" AND ".join(f"{c[0]} {c[1]} ?" for c in cond)}', [c[2] for c in cond])
        except:
            logger.exception(f'Error while querying database, sql: {cur._last_executed}')
            return [] # empty when error
        return cur.fetchall() if not return_map else [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    
    def insert(self, table: str, value: dict[str, Any]) -> None:
        '''
            Insert a row into the database.
        '''
        if not isinstance(table, str):
            raise InternalError(f'Invalid parameter type, str expected, {type(table)} found.')
        if not isinstance(value, dict) or not all(isinstance(k, str) for k, _ in value.items()):
            raise InternalError(f'Invalid parameter type, dict[str, Any] expexted.')
        try:
            cur.execute(f'INSERT INTO {table} ({", ".join(value.keys())}) VALUES ({", ".join("?" for _ in value.keys())})', list(value.values()))
            db.commit()
        except sqlite3.IntegrityError:
            raise InternalError('Duplicate key.')
        except:
            logger.exception(f'Error while inserting into database, sql: {cur._last_executed}')
    
    def update(self, table: str, value: dict[str, Any], cond: list[list[str, str, Any]]) -> None:
        '''
            Update a row in the database.
            defaults to AND for cond
        '''
        if not isinstance(table, str):
            raise InternalError(f'Invalid parameter type, str expected, {type(table)} found.')
        if not isinstance(value, dict) or not all(isinstance(k, str) for k, _ in value.items()):
            raise InternalError(f'Invalid parameter type, dict[str, Any] expexted.')
        if not isinstance(cond, list) or not all(isinstance(c, list) and len(c)==3 and isinstance(c[0], str) and isinstance(c[1], str) for c in cond):
            raise InternalError('Invalid parameter type, list[list[str, str, Any]] expected.')
        try:
            cur.execute(f'UPDATE {table} SET {", ".join(f"{k} = ?" for k in value.keys())} WHERE {" AND ".join(f"{c[0]} {c[1]} ?" for c in cond)}', list(value.values()) + [c[2] for c in cond])
            db.commit()
        except:
            logger.exception(f'Error while updating database, sql: {cur._last_executed}')
                

