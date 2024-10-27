import logging
import os
import sqlite3 as sqlite
import threading
import pymongo
import pymongo.errors as mongo_error


class Store:

    def __init__(self, db_url):
        self.myclient = pymongo.MongoClient(db_url)
        self.database = self.myclient["bookstore_db"]
        self.init_tables()

    def init_tables(self):
        try:

            self.database["user"].drop()
            self.col_user = self.database["user"]
            self.col_user.create_index([("user_id", 1)], unique=True)

            self.database["store"].drop()
            self.col_store = self.database["store"]
            self.col_store.create_index([("store_id", 1)], unique=True)

            self.database["book"].drop()
            self.col_book = self.database['books']
            self.col_book.create_index(
                [("title", "text"), ("tags", "text"), ("book_intro", "text"), ("content", "text")])

            self.database["order_detail"].drop()
            self.col_order_detail = self.database['order_detail']

            self.database["order"].drop()
            self.col_order = self.database['order']

        except mongo_error.PyMongoError as e:
            logging.error(e)

    def get_db_conn(self):
        return self


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
