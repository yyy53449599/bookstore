import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            total_price = 0

            for book_id, count in id_and_count:
                result = self.conn.col_store.find_one({"store_id": store_id, "books.book_id": book_id}, {"books.$": 1})
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                result1 = self.conn.col_book.find_one({"id": book_id})
                stock_level = result["books"][0]["stock_level"]

                price = result1["price"]

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result = self.conn.col_store.update_one({"store_id": store_id, "books.book_id": book_id, "books.stock_level": {"$gte": count}},
                                                               {"$inc": {"books.$.stock_level": -count}})
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.conn.col_order_detail.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })
                total_price += price * count

            self.conn.col_order.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "price": total_price,
                "status": 0
            })
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            result = self.conn.col_order.find_one({"order_id": order_id, "status": 0})
            if result is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = result["user_id"]
            store_id = result["store_id"]
            total_price = result["price"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            result = self.conn.col_user.find_one({"user_id": buyer_id})
            if result is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = result.get("balance", 0)
            if password != result.get("password", ""):
                return error.error_authorization_fail()

            result = self.conn.col_store.find_one({"store_id": store_id})
            if result is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = result.get("user_id")

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            result = self.conn.col_user.update_one({"user_id": buyer_id, "balance": {"$gte": total_price}}, {"$inc": {"balance": -total_price}})
            if result.matched_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result = self.conn.col_user.update_one({"user_id": seller_id}, {"$inc": {"balance": total_price}})
            if result.matched_count == 0:
                return error.error_non_exist_user_id(buyer_id)

            self.conn.col_order.insert_one({
                "order_id": order_id,
                "store_id": store_id,
                "user_id": buyer_id,
                "status": 1,
                "price": total_price
            })
            result = self.conn.col_order.delete_one({"order_id": order_id, "status": 0})
            if result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)
        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            result = self.conn.col_user.find_one({"user_id": user_id})
            if result is None:
                return error.error_authorization_fail()
            if result.get("password") != password:
                return error.error_authorization_fail()

            result = self.conn.col_user.update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})
            if result.matched_count == 0:
                return error.error_non_exist_user_id(user_id)
        except BaseException as e:
            return 528, "{}".format(str(e))

        return 200, ""
