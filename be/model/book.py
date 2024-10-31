from be.model import db_conn


class Book(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_title_in_store(self, title: str, store_id: str, page_num: int, page_size: int):
        book = self.conn.col_book
        condition = {
            "title": title
        }
        result = book.find(condition,{"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
        result_list = list(result)
        if store_id != "":
            store = self.conn.col_store
            books_in_store = []
            for b in result_list:
                condition1 = {"store_id": store_id, "books.book_id": b.get('id')}
                book_id = list(store.find(condition1, {"books.book_id": 1}))
                if len(book_id) != 0:
                    books_in_store.append(b)
            result_list = books_in_store
        if len(result_list) == 0:
            return 501, f"{title} book not exist", []
        return 200, "ok", result_list

    def search_title(self, title: str, page_num: int, page_size: int):
        return self.search_title_in_store(title, "", page_num, page_size)

    def search_tag_in_store(self, tag: str, store_id: str, page_num: int, page_size: int):
        book = self.conn.col_book
        condition = {
            "tags": {"$regex": tag}
        }
        result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
        result_list = list(result)
        if store_id != "":
            store = self.conn.col_store
            books_in_store = []
            for b in result_list:
                condition1 = {"store_id": store_id, "books.book_id": b.get('id')}
                book_id = list(store.find(condition1, {"books.book_id": 1}))
                if len(book_id) != 0:
                    books_in_store.append(b)
            result_list = books_in_store
        if len(result_list) == 0:
            return 501, f"{tag} book not exist", []
        return 200, "ok", result_list

    def search_tag(self, tag: str, page_num: int, page_size: int):
        return self.search_tag_in_store(tag, "", page_num, page_size)

    def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
        book = self.conn.col_book
        condition = {
            "$text": {"$search": content}
        }
        result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
        result_list = list(result)
        if store_id != "":
            store = self.conn.col_store
            books_in_store = []
            for b in result_list:
                condition1 = {"store_id": store_id, "books.book_id": b.get('id')}
                book_id = list(store.find(condition1, {"books.book_id": 1}))
                if len(book_id) != 0:
                    books_in_store.append(b)
            result_list = books_in_store
        if len(result_list) == 0:
            return 501, f"{content} book not exist", []
        return 200, "ok", result_list

    def search_content(self, content: str, page_num: int, page_size: int):
        return self.search_content_in_store(content, "", page_num, page_size)

    def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
        book = self.conn.col_book
        condition = {
            "author": author
        }
        result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
        result_list = list(result)
        if store_id != "":
            store = self.conn.col_store
            books_in_store = []
            for b in result_list:
                condition1 = {"store_id": store_id, "books.book_id": b.get('id')}
                book_id = list(store.find(condition1, {"books.book_id": 1}))
                if len(book_id) != 0:
                    books_in_store.append(b)
            result_list = books_in_store
        if len(result_list) == 0:
            return 501, f"{author} book not exist", []
        return 200, "ok", result_list

    def search_author(self, author: str, page_num: int, page_size: int):
        return self.search_author_in_store(author, "", page_num, page_size)
