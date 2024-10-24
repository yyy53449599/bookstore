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
            
            self.database["user"].drop()
            col_user = self.database["user"]
            col_user.create_index([("user_id", 1)], unique=True)
            
            self.database["store"].drop()
            col_store = self.database["store"]
            col_store.create_index([("store_id", 1)], unique=True)
            
            self.database["book"].drop()
            self.col_book = self.db['books']
            
            self.database["order_detail"].drop()
            self.col_order_detail = self.db['order_detail']

            self.database["order"].drop()
            self.col_order = self.db['order']
            
            
            
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
