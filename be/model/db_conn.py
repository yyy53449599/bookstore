from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        result = self.conn.col_user.find_one({"user_id": user_id})
        if result is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        result = self.conn.col_store.find_one({"store_id": store_id, "books.book_id": book_id})
        if result is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        result = self.conn.col_store.find_one({"store_id": store_id})
        if result is None:
            return False
        else:
            return True