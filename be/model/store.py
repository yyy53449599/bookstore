import logging
import os
import sqlite3 as sqlite
import threading
import pymongo


class Store:
    database: str

    def __init__(self, db_path):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = myclient["bookstore_db"]
        self.init_tables()

    def init_tables(self):
        try:
            '''
            conn = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.commit()
            '''
            
            self.database["user"].drop()
            col_user = self.database["user"]
            col_user.create_index([("user_id", 1)], unique=True)
            
            self.database["store"].drop()
            col_store = self.database["store"]
            col_store.create_index([("store_id", 1)], unique=True)
            
            self.database["book"].drop()
            self.col_book = self.db['books']
            
            #索引？ order表
            
            
            
        except sqlite.Error as e:
            logging.error(e)

    def get_db_conn(self) -> sqlite.Connection:
        return sqlite.connect(self.database)


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
