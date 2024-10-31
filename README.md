# 数据库大作业

| **课程名称：当代数据管理系统** | **指导教师：周烜**    | **上机实践名称：** **Bookstore** |
| ------------------------------ | --------------------- | -------------------------------- |
| **姓名**：邓博昊               | **学号**：10225501432 | **年级：2022**                   |
| **姓名**：余明阳               |                       | **年级：2022**                   |
| **姓名**：左庭宇               |                       | **年级：2022**                   |

## 一、实验目的与要求

**功能概况**

- 实现一个提供网上购书功能的网站后端。<br>

- 网站支持书商在上面开商店，购买者可以通过网站购买。<br>
- 买家和卖家都可以注册自己的账号。<br>
- 一个卖家可以开一个或多个网上商店。
- 买家可以为自已的账户充值，在任意商店购买图书。<br>
- 支持 下单->付款->发货->收货 流程。<br>

**1.实现对应接口的功能，见项目的 doc 文件夹下面的 .md 文件描述 （60%）<br>**

其中包括：

1)用户权限接口，如注册、登录、登出、注销<br>

2)买家用户接口，如充值、下单、付款<br>

3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br>

通过对应的功能测试，所有 test case 都 pass <br>

**2.为项目添加其它功能 ：（40%）<br>**

1)实现后续的流程 ：发货 -> 收货

2)搜索图书 <br>

- 用户可以通过关键字搜索，参数化的搜索方式；
- 如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
- 如果显示结果较大，需要分页
- (使用全文索引优化查找)

3)订单状态，订单查询和取消订单<br>

- 用户可以查自已的历史订单，用户也可以取消订单。<br>
- 取消订单可由买家主动地取消，或者买家下单后，经过一段时间超时仍未付款，订单也会自动取消。 <br>



**其他要求：**

* 要求大家创建本地 MongoDB 数据库，将`bookstore/fe/data/book.db`中的内容以合适的形式存入本地数据库，后续所有数据读写都在本地的 MongoDB 数据库中进行
* 在完成前60%功能的基础上，继续实现后40%功能，要有接口、后端逻辑实现、数据库操作、代码测试。对所有接口都要写 test case，通过测试并计算测试覆盖率（尽量提高测试覆盖率）。
* 尽量使用索引，对程序与数据库执行的性能有考量
* 尽量使用 git 等版本管理工具
* 不需要实现界面，只需通过代码测试体现功能与正确性

## 二、文档数据库的设计

### 1. 数据库逻辑设计

![image-20241031193039413](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031193039413.png)

以上这个便是bookstore整体的业务逻辑图。

### 2. 数据库的结构设计 

根据数据库的业务逻辑，为了展现文档数据库相对于关系数据库而言模型灵活、凸显关系、便于查询的优势，我们最开始设想的文档集设计是——user,store,book,order.

但是在之后完成项目的过程中，我们发现只有面对查询历史订单时，我们才真的需要知道这笔订单具体的内容是什么；然而其他关于订单的场景（比如支付、发书、收书）我们并不需要这么多的信息，只要知道这是哪笔订单就行。因此，我们将order的一些信息拆分了出来，设计了两个文档集——order和order_detail.

还有一个问题，就是对于实验所给的sqlite代码而言，它设置了一个user_store表，但是这个在文档数据库中真的适用吗？经过小组成员的讨论和思考，我们觉得这个表的存在没有意义——store,user作为两大类而建集合无可厚非；在此基础上，store文档集中的一个文档完全可以存储user_id。因为一个store一定只被一个用户所有，但是一个用户可以拥有多个商店，这样做既满足了实际情况，又不增加冗余，不会每次查找一个商店属于哪个用户时多此一举地再用中间的user_store 文档集来查询。由此，我们的文档数据库具体结构如下所示：

```
user{
    user_id
    password
    balance
    token
    terminal
}
store{
    store_id
    user_id
    books[]{
        book_id
        stock_level
}
}
book{
    id
    title
    author
    ......
    content
    tags
    picture
}
order{
    order_id
    store_id
    user_id
    status // 0:未付款;1:付款但是未发货;2:付款发货但是还没被接受;3:付款发货接受了;4:取消
    price
}
order_detail{
    order_id
    book_id
    count
    price
}
```



### 3索引设计 

众所周知，采用索引对于“频繁查找，不常更改”的数据项之查找功能来说起到了十分好的性能增益作用。结合整体的实验设计，考虑各文档集的实际情况，我们最终这样设置的索引：

1. store文档集的store_id上设置了升序索引，并且保证了其唯一性

2. user文档集的user_id上设置了升序索引，并且保证了其唯一性

3. 为了允许对文本字段进行全文搜索，books文档集上设置了多个索引，分别是在字段title,tags,book_intro,content上（这些字段的内容都是文本，所以类型都设置为了text）

本来我们还期望在order和order_detail上设置索引，但这两个文档集经常在变化，虽然它们查询的场景还算广泛（下单、查询订单等），但是权衡之后我们最终还是放弃了在此设置索引。

## 三、前期分析

以下为初见分析

### 1. 文件树分析

```cmd
(.venv) ~\Desktop\大三上\当代数据管理系统\Homework\大作业\CDMS.Xuan_ZHOU.2024Fall.DaSE\project1\bookstore git:[dev-dbh]
tree /A
Folder PATH listing for volume Win11ProW X64
Volume serial number is 16B4-98DD
C:.
+---be	# 后端文件夹，处理实际的业务逻辑
|   +---model	# 数据模型，主要为实际运行时的内部逻辑与sqlite数据库读写，需要重构为操作Mongodb
|   |   \---__pycache__
|   +---view	# flask的后端逻辑
|   |   \---__pycache__
|   \---__pycache__
+---doc
+---fe	# 前端文件夹，主要存放测试和调用后端相关函数(模拟浏览器行为)
|   +---access	# 规定了前端如何调用后端，基本上不需要改动了
|   |   \---__pycache__
|   +---bench	# 测试打分相关
|   |   \---__pycache__
|   +---data	# 存放的sqlite数据，需要后面转到Mongodb上
|   +---test	# 用于pytest框架的测试函数
|   |   \---__pycache__
|   \---__pycache__
\---script	# 存放测试脚本
```

### 2. 业务逻辑分析

一次测试中标准的业务流程如下

1. 搜索测试文件
   - Flask 框架
     - 搜索当前文件树下的测试文件
       - 规则：
         - 以 `test_` 开头
         - 以 `_test` 结尾
       - 包含特定目录中的测试：
         - `/fe/bench`

2. 测试文件执行逻辑
   - 测试文件调用
     - `/fe/access` 中的前端逻辑
     - 前端执行逻辑：
       - 向后端发送 HTTP 指令

3. 后端逻辑
   - 接收前端 HTTP 指令
     - 后端通过 `/be/view` 中的函数解析 HTTP 参数
     - 执行解析包含的指令

4. 后端调用
   - `/be/model` 中的对应函数

### 3. 对比分析

SQLite和MongoDB对比



1. MongoDB URI

   ```
   mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]
   ```

2. 术语对比

   | MySQL 术语          | MongoDB 术语                                                 | 解释                                                         |
   | ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | Database（数据库）  | Database（数据库）                                           | 两者中都使用相同术语，表示数据库的集合。                     |
   | Table（表）         | Collection（集合）                                           | 在MySQL中称为表，在MongoDB中称为集合，存储数据记录的容器。   |
   | Row（行）           | Document（文档）                                             | 在MySQL中每行代表一条记录，而在MongoDB中每个文档是类似的概念，包含数据的键值对。 |
   | Column（列）        | Field（字段）                                                | MySQL的列对应MongoDB的字段，字段表示文档中键值对的键。       |
   | Primary Key（主键） | `_id`（唯一标识符）                                          | MySQL中的主键在MongoDB中对应每个文档的`_id`字段，默认由MongoDB生成唯一ID。 |
   | Index（索引）       | Index（索引）                                                | 两者都用索引来加速查询，但MongoDB的索引可以是嵌套的字段或数组。 |
   | Schema（模式）      | Schema-less（无模式）                                        | MySQL有固定模式，MongoDB是无模式的，即文档的结构不必一致。   |
   | JOIN（连接）        | Embedded Documents（嵌入文档） 或 `$lookup`                  | MongoDB没有直接的JOIN，但可以通过嵌入文档或`$lookup`操作实现类似的功能。 |
   | SQL（查询语言）     | MongoDB Query（MongoDB查询）或 Aggregation Pipeline（聚合管道） | MySQL使用SQL语言，MongoDB有自己的查询语法和聚合框架。        |
   | Transaction（事务） | Transaction（事务）                                          | MongoDB 4.0+版本支持多文档ACID事务，类似MySQL的事务。        |
   | Foreign Key（外键） | Reference（引用）                                            | MongoDB没有明确的外键概念，但可以通过引用文档的方式实现类似的功能。 |
   | View（视图）        | View（视图）                                                 | MongoDB 3.4+版本支持视图，与MySQL的视图类似。                |

### 4. 初次运行

请将Flask降级到2.0.0

将`~/script/test.sh`改成`test.bat`

运行提示，请在项目根目录下运行

```bat
@echo off
setlocal

echo 设置当前目录为 PYTHONPATH
set PYTHONPATH=%cd%

echo 运行 coverage，并指定路径和参数
coverage run --timid --branch --source=fe,be --concurrency=thread -m pytest -v --ignore=fe\data

echo 合并覆盖率数据
coverage combine

echo 生成覆盖率报告
coverage report

echo 生成 HTML 覆盖率报告
coverage html

endlocal
```

然后运行

可以看到`./be/model/user.py`中的`jwt_encode`出了问题

![image-20241012110839105](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241012110839105.png)

查看`jwt_encode`

```py
def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")
```

查询网络后发现，在 `pyjwt` 的较早版本中，`jwt.encode` 返回的是字节对象，需要通过 `.decode("utf-8")` 将其转换为字符串。

从2.0版本开始，`jwt.encode` 直接返回字符串，因此不再需要进行解码。

只需要将 `jwt_encode` 函数中的 `.decode("utf-8")` 移除。修改后的函数如下：

```python
def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded  # 不再需要 decode
```

可以看到上述问题已解决

![image-20241012111337535](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241012111337535.png)





同时整体修改思路如下(仅基础功能)

* 前端`fe`不需要更改，其模拟的是浏览器行为，存放设计好的测试函数
* 后端`be/view`不需要更改，其为后端`Flask`处理HTTP请求并调用处理核心`be/model`部分
* 后端`be/model/error.py`不需要更改，预先设计好的错误代码
* 其余`be/model/`下的文件需要更改



#### 4.1 修改后端`model/db_conn.py`

该py文件为后端连接使用数据库的核心

继承小组左庭宇同学已经修改后的`db_conn.py`

已将原有SQL语句替换为MongoDB语句



但是原代码文件里有关键错误，即`self.database`变量从来没被声明

原版本

![image-20241026182311281](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026182311281.png)

修改后

![image-20241026234538324](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026234538324.png)

#### 4.2 修改后端`model/buyer.py`

继承小组余明阳同学已经修改后的`buyer.py`

无更改

![image-20241026182719700](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026182719700.png)

#### 4.3 修改后端`model/seller.py`

继承小组左庭宇同学已经修改后的`model/seller.py`

修改必要错误：

* 将`self.database`的调用改成`self.conn.database`
* 修复add_book()
* 修复add_stock_level()

需要添加的功能：

* 还差deliver发货函数

![image-20241026183528356](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026183528356.png)

#### 4.4 修改后端`model/user.py`

我需要实现的功能如下：

* 基础功能：
  * 注册(register)
  * 登录(login)
  * 登出(logout)
  * 注销(unregister)
  * 改密(change_password)
* 额外功能：
  * 物流状态查询
    * 发货
    * 收货
  * 搜索图书
  * 订单状态

##### 4.4.1 注册

原函数

![image-20241026184623082](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026184623082.png)

将其简单更改为`MongoDB`形式即可（注意，此时`store.py`还未修改，`self.conn`连接的是SQLite数据库，注意后续修改数据库连接）

![image-20241026220942862](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026220942862.png)





##### 4.4.2 登录

原函数

![image-20241026184858630](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026184858630.png)

修改为

![image-20241026221100509](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221100509.png)



注意`login`函数，调用了`check_password`函数

同理，需要修改`check_password`函数

原函数

![image-20241026221223080](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221223080.png)

修改为

![image-20241026221413913](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221413913.png)

##### 4.4.3 登出

原函数

![image-20241026221601403](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221601403.png)

修改为

![image-20241026221642700](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221642700.png)



注意，调用了`check_token`函数

原函数

**![image-20241026221729998](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20241026221729998.png)**

修改为

##### 4.4.4 注销

原函数

![image-20241026221905600](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221905600.png)

修改为

![image-20241026221925214](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221925214.png)



`check_password`函数已经修改，直接跳过



##### 4.4.5 改密

原函数

![image-20241026222216893](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222216893.png)

修改为

![image-20241026222237212](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222237212.png)



#### 4.5 修改后端`model/store.py`

原有`store.py`关联的是SQLite数据库

##### 4.5.1 被调用链

1. `be/model/`中的类初始化时

​	调用`db_conn.DBConn`的初始化函数

![image-20241026222717814](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222717814.png)

2. `be/model/db_conn.DBConn`初始化时

   调用`store.get_db_conn()`函数

3. `store.get_db_conn()`调用`database_instance.get_db_conn()`函数
   `database_instance`为`Store`类的一个实例

   

![image-20241026223137663](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026223137663.png)

![image-20241026223208964](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026223208964.png)

##### 4.5.2 修改方向

1. 全部改为self.xxx，作为类的属性，方便调用
2. 删除database: str，因为不再是SQLite,显然返回的类型应该为`Map`类型
3. `get_db_conn(self)`返回类自己即可
4. `db_path`改为`db_url`
5. `init_database`在`serve.py`里被调用，原来参数为父文件夹目录，现在更改为`mongodb_url`
   ![image-20241026235115526](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026235115526.png)
6. 额外添加`get_db_conn()`在数据库实例未初始化时被调用，则初始化实例
   ![image-20241031191408151](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031191408151.png)
7. 创建关于图书标题，标签，简洁，内容的索引

```python
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

```



#### 4.6 再次运行

注意将`fe/conf.py`里的`Use_Large_DB = True`改为False

因为是本地测试，还未用助教所提的超大数据库

运行结果如下

![image-20241027025601617](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241027025601617.png)

### 5.额外功能

#### 5.1发货 -> 收货

##### 5.1.1修改后端be/model/sell.py

```
def deliver(self,user_id:str,order_id:str) -> (int, str):
        try:            
            col_order = self.conn.database["order"]
            deliver = {  
                "$or": [
                    {"order_id": order_id, "status": 1},
                    {"order_id": order_id, "status": 2},
                    {"order_id": order_id, "status": 3},
                ]   
            }
            result = col_order.find_one(deliver)

            if result == None:
                return error.error_invalid_order_id(order_id)
            store_id = result.get("store_id")
            status = result.get("status")

            result = col_order.find_one({"store_id": store_id})
            seller_id = result.get("user_id")
            if seller_id != user_id:
                return error.error_authorization_fail()
            if status == 2 or status == 3:
                return error.error_books_repeat_sent()

            col_order.update_one({"order_id": order_id}, {"$set": {"status": 2}})
            
            
            
        except sqlite.Error as e:
            return 528,"{}".format(str(e))
        except BaseException as e:
            return 530,"{}".format(str(e))
        
        return 200,"ok"
```

##### 5.1.2修改后端be/view/sell.py

```
@bp_seller.route("/deliver",methods=['POST'])
def deliver():
    user_id:str=request.json.get("user_id")
    order_id:str=request.json.get("order_id")

    s = seller.Seller()
    code,message=s.deliver(user_id,order_id)

    return jsonify({"message":message}) , code
```

##### 5.1.3修改前端fe/access/sell.py

```
def deliver(self, seller_id: str, order_id: str) -> int:
        json = {"user_id": seller_id, "order_id": order_id}
        url = urljoin(self.url_prefix, "send_books")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
```

##### 5.1.4添加fe/test/test_deliver.py

```python
import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid

class TestDeliver:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_deliver_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_deliver_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_deliver_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.buyer_id)
        self.buyer = b
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price + 1000000)
        assert code == 200

        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200
        yield

    def test_ok(self):
        code = self.seller.deliver(self.seller_id, self.order_id)
        assert code == 200

    def test_order_error(self):
        code = self.seller.deliver(self.seller_id, self.order_id + 'x')
        assert code != 200
    
    def test_books_repeat_deliver(self):
        code = self.seller.deliver(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller.deliver(self.seller_id, self.order_id)
        assert code != 200

```

#### 5.2 图书查询

根据前文业务流程分析依次需要实现的

* 添加`fe/test/search.py`
* 添加`fe/access/search.py`
* 添加`be/view/search.py`(记得在serve.py里注册蓝图)
* 添加`be/model/book.py`

将在后期分析中进行详细讲解，这里不过多赘述

#### 5.3 订单状态，订单查询和取消订单

根据前文业务流程分析依次需要实现的

* 添加`fe/test/*`
  * `test_cancel_auto.py`测试自动取消订单
  * `test_cancel_order.py`测试手动取消订单
  * `test_history_order.py`测试订单状态，订单查询
* 修改`fe/access/buyer.py`
* 修改`be/view/search.py`
* 修改`be/model/book.py`

将在后期分析中进行详细讲解，这里不过多赘述



### 6.完整运行

实现基础功能+额外功能后，进行测试

#### 6.1 小数据库`book.db`

最终HTML 覆盖率报告储存在`results/book_db`中

![image-20241031190725300](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031190725300.png)

#### 6.2 大数据库`booklx.db`

最终HTML 覆盖率报告储存在`results/book_lx_db`中

详细终端输出将`results/console.log`

![image-20241031191831366](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031191831366.png)

![image-20241031191844575](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031191844575.png)



从你提供的文件内容和格式要求来看，需要将整个文档按照统一格式重新排版，同时修正所有的*号使用。让我先开始格式化文档：

## **四、后期分析**

### **1.基本功能的实现**

#### **1.1 用户**

##### **1.1.1 用户注册与注销（register,unregister）**

:one:register函数接受以下参数：

* user_id: 表示要注册的用户ID。 
* password: 表示用户的密码。

该函数的返回值是一个元组，包含两个值：
* 一个整数：代表操作的状态码。200 表示成功，528表示某种错误。 
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。

函数主要流程：
1. 尝试生成一个唯一的终端标识，格式为 "terminal_<当前时间戳>"。 
2. 利用用户提供的 user_id 和生成的终端标识，使用 jwt_encode 函数生成一个 token。
3. 将用户的信息插入到数据库的 user_col 集合中，包括user_id、password、balance、token 和 terminal。 
4. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息。
5. 如果操作成功，函数返回状态码 200 和 "ok" 作为成功消息。

:two:unregister函数接受以下参数：

* user_id: 表示要注销的用户ID。 
* password: 表示用户的密码。 

该函数的返回值是一个元组，包含两个值：
* 一个整数：代表操作的状态码。200 表示成功，530表示异常，以及其他可能的状态码。 
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。 

函数主要流程：
1. 调用 check_password 函数验证用户提供的密码是否正确。 
2. 如果密码验证失败，返回相应的错误代码和消息。 
3. 如果密码验证成功，尝试从数据库中删除具有指定 user_id 和 password 的用户信息。 
4. 检查删除操作的结果，如果成功删除了一个用户，返回状态码 200 和 "ok" 作为成功消息。
5. 如果删除操作未成功（deleted_count 不为 1），返回授权失败的错误消息。
6. 如果在上述过程中发生任何异常，捕获异常并返回状态码 530，以及异常的字符串表示作为错误消息。

##### **1.1.2 检验用户的token/password是否正确（check_token,check_password）**

check_token函数接受以下参数：

* user_id: 表示要验证令牌的用户ID。
* token: 表示要验证的令牌。

该函数的返回值是一个元组，包含两个值：
* 一个整数：代表操作的状态码。200 表示成功，528表示某种错误，以及其他可能的状态码。
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。

函数主要流程：
1. 通过查询数据库获取指定 user_id 的用户信息。
2. 如果用户不存在，返回授权失败的错误消息。
3. 确保查询结果只有一个用户。
4. 从查询结果中获取用户的存储的令牌 token1。
5. 使用 __check_token 函数验证提供的 token 是否与存储的 token1 一致。
6. 如果令牌验证失败，返回授权失败的错误消息。
7. 如果令牌验证成功，返回状态码 200 和 "ok" 作为成功消息。

check_password与check_token类似，主要运行流程：

1. 通过查询数据库获取指定 user_id 的用户信息。
2. 如果用户不存在，返回授权失败的错误消息。
3. 检查查询结果中存储的密码是否与提供的密码一致。
4. 如果密码验证失败，返回授权失败的错误消息。
5. 如果密码验证成功，返回状态码 200 和 "ok" 作为成功消息。



##### **1.1.3 用户登录与登出（login,logout）**

login函数接受以下参数：
* user_id: 表示要登录的用户ID。
* password: 表示用户的密码。
* terminal: 表示登录的终端标识。

该函数的返回值是一个元组，包含三个值：
* 一个整数：代表操作的状态码。200 表示成功，528表示某种错误，以及其他可能的状态码。
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。
* 一个字符串：如果操作成功，代表生成的令牌 token；如果操作失败，为空字符串。

函数主要流程：
1. 调用 check_password 函数验证用户提供的密码是否正确。
2. 如果密码验证失败，返回相应的错误代码和消息。
3. 如果密码验证成功，尝试生成一个新的令牌 token。
4. 更新数据库中存储的用户信息，包括更新 token 和 terminal。
5. 检查更新操作是否成功，如果不成功，返回授权失败的错误消息。
6. 如果在上述过程中发生任何异常，捕获异常并返回状态码 528，以及异常的字符串表示作为错误消息。
7. 如果操作成功，返回状态码 200、"ok" 以及生成的令牌 token。

logout函数接受以下参数：
* user_id: 表示要注销的用户ID。
* token: 表示用户的令牌。

该函数的返回值是一个元组，包含两个值：
* 一个整数：代表操作的状态码。200 表示成功，528表示某种错误，以及其他可能的状态码。
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。

函数主要流程：
1. 调用 check_token 函数验证用户提供的令牌是否有效。
2. 如果令牌验证失败，返回相应的错误代码和消息。
3. 生成一个新的终端标识和虚拟令牌。
4. 更新数据库中存储的用户信息，将令牌和终端更新为虚拟值。
5. 检查更新操作是否成功，如果不成功，返回授权失败的错误消息。
6. 如果在上述过程中发生任何异常，捕获异常并返回状态码 528，以及异常的字符串表示作为错误消息。
7. 如果操作成功，返回状态码 200 和 "ok" 作为成功消息。

##### **1.1.4 修改密码（change_password）**

该函数接受以下参数：
* user_id: 表示要更改密码的用户ID。
* old_password: 表示用户的旧密码。
* new_password: 表示用户的新密码。

该函数的返回值是一个元组，包含两个值：
* 一个整数：代表操作的状态码。200 表示成功，528表示某种错误，以及其他可能的状态码。
* 一个字符串：描述操作的结果，通常是一个消息或错误消息。

函数主要流程：
1. 调用 check_password 函数验证用户提供的旧密码是否正确。
2. 如果旧密码验证失败，返回相应的错误代码和消息。
3. 生成一个新的终端标识和令牌。
4. 更新数据库中存储的用户信息，将密码更新为新密码，并更新令牌和终端。
5. 检查更新操作是否成功，如果不成功，返回授权失败的错误消息。
6. 如果在上述过程中发生任何异常，捕获异常并返回状态码 528，以及异常的字符串表示作为错误消息。
7. 如果操作成功，返回状态码 200 和 "ok" 作为成功消息。



#### 1.2 卖家

##### 1.2.1 添加书籍（add_new_book）

该函数接受以下参数：
- user_id: 表示执行此操作的用户的ID
- store_id: 表示要将书籍添加到的商店的ID
- book_id: 表示要添加的书籍的ID
- book_json_str: 表示包含书籍信息的 JSON 字符串
- stock_level: 表示书籍的库存水平

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数主要流程：
1. 函数首先检查用户是否存在。如果用户不存在，它返回一个非存在用户ID的错误消息
2. 然后，函数检查商店是否存在。如果商店不存在，它返回一个非存在商店ID的错误消息
3. 接下来，函数检查书籍是否已经存在于商店中。如果书籍已经存在，它返回一个书籍已存在的错误消息
4. 然后，函数将书籍信息插入到商店集合中，包括商店ID、书籍ID和库存水平
5. 同时，函数还将书籍信息插入到书籍集合中
6. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

##### 1.2.2 创建商铺（create_store）

该函数接受以下参数：
- user_id: 表示执行此操作的用户的ID
- store_id: 表示要创建的商店的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先检查用户是否存在。如果用户不存在，它返回一个非存在用户ID的错误消息
2. 然后，函数检查要创建的商店ID是否已存在。如果商店ID已经存在，它返回一个商店已存在的错误消息
3. 接着，函数使用 insert_one 方法，将新商店的信息插入到 store_col 集合中，包括商店ID和用户ID，以关联用户与商店
4. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

##### 1.2.3 添加书籍库存（add_stock_level）

该函数接受以下参数：
- user_id: 表示执行此操作的用户的ID
- store_id: 表示书籍所属的商店的ID
- book_id: 表示要增加库存的书籍的ID
- add_stock_level: 表示要增加的库存数量

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先检查用户是否存在。如果用户不存在，它返回一个非存在用户ID的错误消息
2. 然后，函数检查商店是否存在。如果商店不存在，它返回一个非存在商店ID的错误消息
3. 接着，函数检查书籍是否已经存在于商店中。如果书籍不存在，它返回一个非存在书籍ID的错误消息
4. 然后，函数使用 MongoDB 的 update_one 方法，根据商店ID和书籍ID，将库存水平增加 add_stock_level 个单位
5. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

#### 1.3 买家

##### 1.3.1 创建新订单（new_order）

这个函数接受以下参数：
- user_id：一个字符串，代表用户的ID
- store_id：一个字符串，代表商店的ID
- id_and_count：一个列表，其中包含元组，每个元组包含两个元素：书本的ID（字符串）和数量（整数）

函数的返回值是一个元组，包含三个值：
- 一个整数：代表操作的状态码。200 表示成功，528 表示某种错误
- 一个字符串：描述操作的结果，是一个消息或错误消息
- 一个字符串：订单ID



函数的主要流程：
1. 首先，函数定义了一个空字符串 order_id，稍后将用于存储订单的ID
2. 然后，函数执行了一系列检查，以确保用户和商店的存在。如果用户或商店不存在，函数会返回相应的错误消息和空的订单ID
3. 接下来，函数创建了一个唯一的订单ID uid，这个ID包括了用户ID、商店ID以及一个基于时间的唯一标识符
4. 函数开始遍历 id_and_count 列表中的每个书本ID和数量。对于每个书本，它会执行以下步骤：
   - 查询商店库存，检查书本是否存在。如果书本不存在，它将返回相应的错误消息和空的订单ID
   - 检查库存水平，如果库存不足，它将返回库存不足的错误消息和空的订单ID
   - 如果库存足够，它将更新库存，减少相应数量的书本库存
   - 将书本的订单详细信息插入到订单详细信息集合中，并计算总价格
5. 计算总价格后，函数获取当前时间，并将订单的详细信息插入到订单集合中，包括订单ID、商店ID、用户ID、创建时间、总价格和订单状态
6. 最后，如果一切顺利，函数返回状态码 200 表示成功、一个 "ok" 消息以描述成功，以及生成的订单ID
7. 如果任何异常被捕获，函数会记录日志，并返回状态码 528 表示错误，附带异常信息作为错误消息，以及一个空的订单ID

##### 1.3.2 支付（payment）

该函数接受以下参数：
- user_id: 表示用户的ID
- password: 表示用户的密码
- order_id: 表示订单的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528 表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先在订单集合中查找订单信息，使用给定的订单ID和状态为0（表示订单未付款）。如果没有找到相应的订单信息，它会返回一个无效的订单ID的错误消息
2. 如果找到订单信息，它提取了订单的买家ID、商店ID和总价
3. 函数检查用户ID是否与订单的买家ID匹配，以确保用户有权限支付这个订单。如果用户ID与买家ID不匹配，它会返回一个授权失败的错误消息
4. 然后，函数在用户集合中查找买家的信息，验证用户是否存在，同时检查输入的密码是否与用户的密码匹配。如果用户不存在或密码不匹配，它会返回一个授权失败的错误消息
5. 接下来，函数查找商店信息，以确保商店存在。如果商店不存在，它会返回一个相应的错误消息
6. 函数提取卖家的ID，并检查卖家是否存在。如果卖家不存在，它会返回一个相应的错误消息
7. 接下来，函数检查用户的余额是否足够支付订单的总价。如果余额不足，它会返回一个余额不足的错误消息
8. 如果余额足够，函数首先从买家的账户中扣除订单的总价
9. 然后，它将订单的总价添加到卖家的账户中
10. 接下来，函数将订单的状态更新为1（表示订单已支付），并将订单信息插入订单集合中
11. 最后，函数尝试从订单集合中删除原始状态为0的订单，以确保订单支付成功。如果无法删除，它会返回一个无效的订单ID的错误消息
12. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

##### 1.3.3 添加资金（add_funds）

该函数接受以下参数：
- user_id: 表示用户的ID
- password: 表示用户的密码
- add_value: 表示要添加到用户账户余额的金额

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先尝试在用户集合中查找用户信息，使用给定的用户ID。如果没有找到相应的用户信息，它会返回一个授权失败的错误消息
2. 如果找到用户信息，函数将验证输入的密码是否与用户的密码匹配。如果密码不匹配，它会返回一个授权失败的错误消息
3. 接下来，函数使用 $inc 操作符更新用户账户的余额字段。它将给定的 add_value 添加到用户的余额中
4. 然后，函数检查是否成功匹配了一个用户，如果没有匹配到任何用户，它会返回一个用户不存在的错误消息
5. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息





### 2. 拓展功能的实现

#### 2.1 发货与收货

##### 2.1.1 卖家发货（send_books）

**文件位置：** be/model/seller.py

该函数接受以下参数：
- user_id: 表示执行此操作的用户的ID
- order_id: 表示要标记为已发货的订单的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先执行一个查询，查找具有以下条件的订单：
   - 订单ID等于给定的 order_id
   - 订单状态为1、2或3，表示订单已支付但尚未发货、已发货但尚未收到、或已收到
2. 如果找到符合条件的订单，说明订单可以被标记为已发货。如果没有找到符合条件的订单，函数返回一个无效订单ID的错误消息
3. 接下来，函数获取订单的商店ID和支付状态
4. 然后，函数检查执行此操作的用户是否是商店的所有者。如果不是，它返回一个授权失败的错误消息，表示只有商店的所有者才能标记订单为已发货
5. 接着，函数检查订单的支付状态是否为2或3。如果支付状态是2或3，表示订单已经被标记为已发货或已收到，函数返回一个重复发货的错误消息
6. 最后，函数使用 update_one 方法，将订单的状态标记为2，表示已发货
7. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

##### 2.1.2 买家收货（receive_books）

**文件位置：** be/model/buyer.py

该函数接受以下参数：
- user_id: 表示用户的ID
- order_id: 表示订单的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先在订单集合中查找订单信息，使用给定的订单ID和状态为1、2或3的订单。这里使用 $or 操作符来查找匹配的订单。如果没有找到相应的订单信息，它会返回一个无效的订单ID的错误消息
2. 如果找到订单信息，函数提取了订单的买家ID和订单的支付状态
3. 接下来，函数检查订单的买家ID是否与给定的用户ID匹配，以确保用户有权限接收这个订单。如果不匹配，它会返回一个授权失败的错误消息
4. 然后，函数根据支付状态检查订单是否可以接收：
   - 如果订单状态是1，表示订单已支付但书籍尚未发出，它会返回书籍未发出的错误消息
   - 如果订单状态是3，表示已经接收过一次，它会返回重复接收书籍的错误消息
5. 最后，如果一切正常，函数将更新订单的状态为3，表示书籍已经被接收
6. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

#### 2.2 搜索图书（包括优化）

##### 2.2.0 简单搜索

我们最开始是在buyer中实现了一个简单的search方法。这个函数接受四个参数：
- keyword: 表示搜索的关键字
- store_id: 表示商店的ID，用于限定搜索结果在特定商店中
- page: 表示页码，用于分页显示搜索结果，默认为1
- per_page: 表示每页的书籍数量，默认为10



该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，530表示某种错误
- 一个列表：包含搜索结果的书籍信息

函数的主要流程：
1. 首先，函数构建了一个基本查询 base_query，它使用 MongoDB 的 $text 操作符来执行全文本搜索，搜索的关键字是 keyword
2. 接下来，函数创建了一个查询 query，初始时等于基本查询 base_query
3. 如果提供了 store_id，函数会执行以下操作：
   - 在商店集合中查找匹配 store_id 的书籍ID，并将这些书籍ID存储在列表 books_id 中
   - 在查询中添加条件，要求书籍的ID必须在 books_id 列表中
4. 然后，函数执行查询操作，查找符合查询条件的书籍。它还使用 $meta 来获取每本书籍的文本分数，以便后续排序
5. 接着，函数执行分页操作，跳过前面 (page - 1) * per_page 个结果，然后限制每页显示 per_page 条结果
6. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 530，以及异常的字符串表示作为错误消息
7. 最后，函数返回状态码 200，以及包含搜索结果的书籍信息的列表

但是后来发现这样可能有点不太合理——首先，不仅买家，卖家作为用户理论上也应该可以搜索书籍；其次，我们这样设计的比较简陋，对于实验所要求的几大功能实现情况并没有那么好。因此，我们在be/model目录添加了一套查找的逻辑在book.py

##### 2.2.1 搜索指定标题的图书

```python
def search_title(self, title: str, page_num: int, page_size: int):
    return self.search_title_in_store(title, "", page_num, page_size)

def search_title_in_store(self, title: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "title": title
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

**search_title的运行逻辑：**
1. 在books集合中查询指定标题的图书，调用find方法指定title字段值为用户通过http请求传过来的参数title
2. 由于_id对于业务逻辑没有任何影响，用户也不需要_id值，因此指定_id为0，表示将查询结果中的_id字段舍弃
3. 最后将查询结果进行分页处理，这里的page_size和page_num都是前端在http请求中传过来的参数，分别表示页的大小以及页号
4. 接着将查询结果转化为list数组，并判断其长度是否为0：
   - 若查询结果的长度为0，表示没有指定标题的图书，返回执行码501以及错误信息（指定title的图书不存在），并返回一个空列表
   - 若查询结果长度不为0，即本次查询能够查到对应的图书，返回执行码200、消息ok以及对应的结果列表

**search_title_in_store的补充逻辑：**
1. 在分页处理之后、查询结果转化为list数组之前需要判断结果集中的图书是否在指定store_id的店铺中
2. 将结果集的图书id作为查询条件，查询store集合中的books数组是否有指定的book_id：
   - 若有指定的book_id，表明这本书是指定店铺中的，将其加入到返回列表中
   - 若没有，则这本书不是指定店铺中的，舍弃这条记录





##### 2.2.2 搜索指定标签的图书

```python
def search_tag(self, tag: str, page_num: int, page_size: int):
    return self.search_tag_in_store(tag, "", page_num, page_size)

def search_tag_in_store(self, tag: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "tags": {"$regex": tag}
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

**search_tag的运行逻辑：**
1. 在books集合中查询含有指定tag的图书，调用find方法指定tags数组中需要包含tag字段值，该tag值为用户通过http请求传过来的参数tag
2. 由于_id对于业务逻辑没有任何影响，用户也不需要_id值，因此指定_id为0，表示将查询结果中的_id字段舍弃
3. 将查询结果进行分页处理，这里的page_size和page_num都是前端在http请求中传过来的参数，分别表示页的大小以及页号
4. 接着将查询结果转化为list数组，并判断其长度是否为0：
   - 若查询结果的长度为0，表示没有满足条件的图书，返回执行码501以及错误信息（指定tag的图书不存在），并返回一个空列表
   - 若查询结果长度不为0，即本次查询能够查到对应的图书，返回执行码200、消息ok以及对应的结果列表

**search_tag_in_store的补充逻辑：**
1. 在分页处理之后，查询结果转化为list数组之前，需要判断结果集中的图书是否在指定store_id的店铺中
2. 将结果集的图书id作为查询条件，查询store集合中的books数组是否有指定的book_id：
   - 若有指定的book_id，表明这本书是指定店铺中的，将其加入到返回列表中
   - 若没有，则这本书不是指定店铺中的，舍弃这条记录

##### 2.2.3 搜索指定内容的图书

```python
def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "$text": {"$search": content}
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

**search_content的运行逻辑：**
1. 在books集合中查询含有指定content的图书，调用find方法，使用全文索引进行搜索，要求图书的book_intro或content字段需要包含用户指定的content值
2. 由于_id对于业务逻辑没有任何影响，用户也不需要_id值，因此指定_id为0，表示将查询结果中的_id字段舍弃
3. 将查询结果进行分页处理，这里的page_size和page_num都是前端在http请求中传过来的参数，分别表示页的大小以及页号
4. 接着将查询结果转化为list数组，并判断其长度是否为0：
   - 若查询结果的长度为0，表示没有满足条件的图书，返回执行码501以及错误信息（指定content的图书不存在），并返回一个空列表
   - 若查询结果长度不为0，即本次查询能够查到对应的图书，返回执行码200、消息ok以及对应的结果列表

**search_content_in_store的补充逻辑：**
1. 在分页处理之后，查询结果转化为list数组之前，需要判断结果集中的图书是否在指定store_id的店铺中
2. 将结果集的图书id作为查询条件，查询store集合中的books数组是否有指定的book_id：
   - 若有指定的book_id，表明这本书是指定店铺中的，将其加入到返回列表中
   - 若没有，则这本书不是指定店铺中的，舍弃这条记录



##### 2.2.4 搜索指定作者的图书

```python
def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "author": author
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

**search_author的运行逻辑：**
1. 在books集合中查询含有指定author的图书，调用find方法，指定author字段值为用户通过http请求传过来的参数author
2. 由于_id对于业务逻辑没有任何影响，用户也不需要_id值，因此指定_id为0，表示将查询结果中的_id字段舍弃
3. 将查询结果进行分页处理，这里的page_size和page_num都是前端在http请求中传过来的参数，分别表示页的大小以及页号
4. 接着将查询结果转化为list数组，并判断其长度是否为0：
   - 若查询结果的长度为0，表示没有满足条件的图书，返回执行码501以及错误信息（指定author的图书不存在），并返回一个空列表
   - 若查询结果长度不为0，即本次查询能够查到对应的图书，返回执行码200、消息ok以及对应的结果列表

**search_author_in_store的补充逻辑：**
1. 在分页处理之后，查询结果转化为list数组之前，需要判断结果集中的图书是否在指定store_id的店铺中
2. 将结果集的图书id作为查询条件，查询store集合中的books数组是否有指定的book_id：
   - 若有指定的book_id，表明这本书是指定店铺中的，将其加入到返回列表中
   - 若没有，则这本书不是指定店铺中的，舍弃这条记录

可以发现，其实上述的逻辑是类似的，只不过查询的范围存在差异，我们有希望包装好合适的函数进行批处理操作。可惜时间有限，我们的相应的测试用例通过情况也不错，所以这里就没有进一步的包装，可能算是一个小小的遗憾。

#### 2.3 查询、取消订单

##### 2.3.1 查询订单历史（check_hist_order）

**文件位置：** be/model/buyer.py

这个函数接受一个参数：
- user_id: 表示用户的ID

该函数没有返回值，而是在内部构建了一个包含历史订单信息的列表 ans，并在最后返回这个列表。

函数的主要流程：
1. 函数首先检查用户是否存在。如果用户不存在，它将返回一个非存在用户ID的错误消息
2. 接下来，函数初始化一个空列表 ans，该列表将用于存储历史订单的信息
3. 然后，函数开始检查不同状态的订单：
   - 首先，它查找未付款的订单（status=0），并将这些订单的信息添加到 ans 列表中
   - 然后，它查找已支付但尚未发货、已支付但未收到、已收到的订单（status=1, 2, 3），并将这些订单的信息添加到 ans 列表中
   - 最后，它查找已取消的订单（status=4），并将这些订单的信息添加到 ans 列表中
4. 对于每个订单状态，函数执行以下操作：
   - 查找匹配用户ID和订单状态的订单信息
   - 对于每个订单，它查找与订单相关的书籍详细信息
   - 为每个订单构建一个字典，包含订单的状态、订单ID、买家ID、商店ID、总价和书籍详细信息。然后将该字典添加到 ans 列表中
5. 最后，如果没有找到任何历史订单，函数将返回一个成功的消息，指示没有找到订单。否则，它将返回一个成功的消息和包含历史订单信息的 ans 列表
6. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息



##### 2.3.2 取消订单（cancel_order）

**文件位置：** be/model/buyer.py

该函数接受以下参数：
- user_id: 表示用户的ID
- order_id: 表示订单的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 首先，函数尝试在订单集合中查找订单信息，使用给定的订单ID和状态为0（表示订单未付款）。如果找到相应的订单信息，它提取了订单的买家ID、商店ID和订单价格，然后从订单集合中删除该订单
2. 如果在第一步没有找到匹配的订单，函数继续寻找订单状态为1、2或3的订单，使用 $or 操作符来查找匹配的订单。如果找到相应的订单信息，它提取了订单的买家ID、商店ID和订单价格，并继续执行以下操作：
   - 检查买家ID是否与给定的用户ID匹配，以确保用户有权限取消订单。如果不匹配，它返回一个授权失败的错误消息
   - 查找卖家ID，然后从卖家账户中扣除订单的价格，同时将相同金额添加到买家账户中
   - 最后，从订单集合中删除匹配的订单
3. 如果在上述步骤中没有找到匹配的订单，函数返回一个无效的订单ID的错误消息
4. 接下来，函数通过查询订单详细信息集合来获取已购书籍的信息。它遍历订单详细信息，对于每本书籍，将库存还原，增加相应数量的库存
5. 最后，函数将创建一个新订单，状态设置为4，表示订单已取消，包括订单ID、用户ID、商店ID、订单价格和状态，并插入到订单集合中
6. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息

##### 2.3.3 自动取消订单（auto_cancel_order）

**文件位置：** be/model/buyer.py

该函数没有传入参数，但在内部执行一系列操作来自动取消未支付的订单。该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，528表示某种错误
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先定义了一个等待时间 wait_time，这个时间表示多久未支付的订单将被自动取消，这里设置为20秒
2. 接着，函数获取当前的UTC时间 now，然后计算出一个时间间隔 interval，该间隔是当前时间减去 wait_time 秒后的时间
3. 接下来，函数构建了一个查询条件 cursor，用于查找满足以下条件的订单：
   - 订单状态为0（未支付）
   - 订单创建时间早于 interval
4. 然后，函数执行查询，查找待取消的订单，将这些订单的信息存储在 orders_to_cancel 中
5. 如果找到待取消的订单，函数遍历这些订单，依次执行以下操作：
   - 获取订单的相关信息，包括订单ID、用户ID、商店ID和订单价格
   - 从订单集合中删除这个订单，取消订单
   - 查询被取消订单的书籍详细信息，并遍历这些书籍
   - 对每本书籍，将库存还原，增加相应数量的库存
   - 如果库存还原失败（update_result.modified_count == 0），则返回一个库存不足的错误消息
6. 最后，对于每个已取消的订单，函数构建一个新的订单文档 canceled_order，将其状态设置为4（已取消），然后插入到订单集合中
7. 如果在上述过程中发生任何异常，函数会捕获异常，并返回状态码 528，以及异常的字符串表示作为错误消息



#### 2.4 检查订单是否已被取消（is_order_cancelled）

该函数接受以下参数：
- order_id: 表示要检查的订单的ID

该函数的返回值是一个元组，包含两个值：
- 一个整数：代表操作的状态码。200 表示成功，而其他状态码表示不同的错误情况
- 一个字符串：描述操作的结果，通常是一个消息或错误消息

函数的主要流程：
1. 函数首先在订单集合中执行一个查询，查找订单ID等于给定的 order_id，且状态等于4（表示已取消）的订单
2. 如果找到符合条件的订单，说明订单已经被取消，函数返回一个成功的状态码 200 和消息 "ok"
3. 如果没有找到符合条件的订单，说明订单未被取消，函数返回一个指示自动取消失败的错误消息

### 3. 接口与测试

#### 3.1 接口

后端接口在 be/view/，前端接口则在 fe/access

##### 3.1.1 后端接口

**基础接口**

- be/view/auth.py 中的接口未做修改，包含:
  - login：登录
  - logout：登出
  - register：注册
  - unregister：注销
  - password：修改密码

- be/view/buyer.py 中的基本接口包含：
  - new_order：发起新订单
  - payment：支付
  - add_funds：增加余额

- be/view/seller.py 中的基本接口包含：
  - create_store：创建商店
  - add_book：增加书目
  - add_stock_level：增加库存

**新增功能接口**
- be/view/buyer.py 中新增接口：
  - receive_books：收书
  - cancel_order：取消订单
  - auto_cancel_order：自动取消订单
  - is_order_cancelled：检验订单是否已被取消
  - check_hist_order：查询订单历史
  - search：简单查找

- be/view/seller.py 中新增接口：
  - send_books：发书功能

##### 3.1.2 精细化搜索功能的接口

**位置：** be/view/search.py

基本的流程如下：
1. 接口路由为"/search/tag_in_store"，请求方法为get请求
2. 由flask的内置对象request，获取请求参数title、page_num、page_size，分别表示标题，请求页的大小
3. 判断上述请求参数是否为None，若为None，则为这些变量赋上默认值
4. 调用be.model.book的对应方法
5. 将返回值封装到字典中，调用json的jsonify方法序列化并返回给前端，返回结构如下：
```json
{
    "data": books,
    "message": message,
    "code": code
}
```

基于此模板实现了以下搜索接口：
- 搜索指定标题的图书接口（search_title）
- 搜索指定tag的图书接口（search_tag）
- 搜索指定content的图书接口（search_content）
- 搜索指定author的图书接口（search_author）
- 在店铺内搜索指定标题的图书接口（search_title_in_store）
- 在店铺内搜索指定tag的图书接口（search_tag_in_store）
- 在店铺内搜索指定content的图书接口（search_content_in_store）
- 在店铺内搜索指定author的图书接口（search_author_in_store）



### 3.1.3 前端接口
在修改完后端的接口后，我们在 `fe/access` 实现了与之对应的前端接口。因为实在是过度模式化，没什么亮点，此处就不赘述了，这里主要来谈一下这个模式化吧：

1. 先拼接得到相应的接口路由
2. 再调用 `requests` 库的 `get` 方法，对该接口发送一个 `get` 请求，指定 `params` 为上述请求参数
3. 得到 `response` 后，调用 `json.loads` 方法解析返回的 JSON 字符串，返回执行码（即 JSON 对象的 `code`）

```json
{
  "data": books,
  "message": message,
  "code": code
}
```

```markdown
### 3.1.3 前端接口
在修改完后端的接口后，我们在 `fe/access` 实现了与之对应的前端接口。因为实在是过度模式化，没什么亮点，此处就不赘述了，这里主要来谈一下这个模式化吧：

1. 先拼接得到相应的接口路由
2. 再调用 `requests` 库的 `get` 方法，对该接口发送一个 `get` 请求，指定 `params` 为上述请求参数
3. 得到 `response` 后，调用 `json.loads` 方法解析返回的 JSON 字符串，返回执行码（即 JSON 对象的 `code`）

```json
{
  "data": books,
  "message": message,
  "code": code
}
```

### 3.2 测试
在 `fe/test` 文件夹下，除了基础的 33 个测试点，我们还对补充的功能添加了许多额外的测试。这些新添加的测试类都要先进行初始化，使用 `uuid` 构造一个 `xx_id`（比如 `seller_id`）、`password`，并调用相应接口注册，注册之后进行诸如创建店铺这样的操作。

#### 3.2.1 test_cancel_order
在初始化测试类之后，有几个具体的测试：

1. **test_paid**
   - 情况：已付款的订单。
   - 操作：创建订单，付款，取消订单。
   - 预期结果：取消订单成功。

2. **test_unpaid**
   - 情况：未付款的订单。
   - 操作：创建订单，取消订单。
   - 预期结果：取消订单成功。

3. **test_invalid_order_id_paid**
   - 情况：已付款的订单，使用不存在的订单 ID 取消。
   - 操作：创建订单，付款，使用不存在的订单 ID 取消订单。
   - 预期结果：取消订单失败。

4. **test_invalid_order_id_unpaid**
   - 情况：未付款的订单，使用不存在的订单 ID 取消。
   - 操作：创建订单，使用不存在的订单 ID 取消订单。
   - 预期结果：取消订单失败。

5. **test_authorization_error_paid**
   - 情况：已付款的订单，用户 ID 不存在。
   - 操作：创建订单，付款，使用不存在的用户 ID 取消订单。
   - 预期结果：取消订单失败。

6. **test_authorization_error_unpaid**
   - 情况：未付款的订单，用户 ID 不存在。
   - 操作：创建订单，使用不存在的用户 ID 取消订单。
   - 预期结果：取消订单失败。

7. **test_repeat_cancel_paid**
   - 情况：已付款的订单，尝试重复取消。
   - 操作：创建订单，付款，取消订单，再次取消订单。
   - 预期结果：第一次取消成功，第二次取消失败。

8. **test_repeat_cancel_not_paid**
   - 情况：未付款的订单，尝试重复取消。
   - 操作：创建订单，取消订单，再次取消订单。
   - 预期结果：第一次取消成功，第二次取消失败。

#### 3.2.2 test_cancel_auto
这个测试文件主要测试了自动取消订单的不同情况，以下是各个测试点的用法解释：

1. **test_overtime**
   - 情况：订单在规定时间内未付款，自动取消。
   - 操作：创建订单，等待超过规定时间，检查订单是否被取消。
   - 预期结果：订单应该被取消，返回码为 200。

2. **test_overtime_paid**
   - 情况：订单在规定时间内已付款，超时后检查订单状态。
   - 操作：创建订单，付款，等待超过规定时间，检查订单是否被取消。
   - 预期结果：由于订单已付款，所以不应该被取消，返回码不为 200。

3. **test_overtime_canceled_by_buyer**
   - 情况：订单在规定时间内被买家取消，超时后检查订单状态。
   - 操作：创建订单，买家取消订单，等待超过规定时间，检查订单是否被取消。
   - 预期结果：由于订单在规定时间内被买家取消，所以应该被取消，返回码为 200。

#### 3.2.3 test_history_order
1. **test_have_orders**
   - 情况：有历史订单的情况。
   - 操作：创建 10 个订单，其中可能包含取消、已付款、发货和收货的情况，然后调用 `check_hist_order` 检查历史订单。
   - 预期结果：检查历史订单返回码为 200。

2. **test_non_exist_user_id**
   - 情况：使用不存在的用户 ID 检查历史订单。
   - 操作：调用 `check_hist_order` 检查历史订单。
   - 预期结果：检查历史订单返回码不为 200。

3. **test_no_orders**
   - 情况：没有历史订单的情况。
   - 操作：调用 `check_hist_order` 检查历史订单。
   - 预期结果：检查历史订单返回码为 200。

#### 3.2.4 test_receive
1. **test_ok**
   - 情况：正常收货。
   - 操作：卖家发货，买家收货。
   - 预期结果：收货成功，返回码为 200。

2. **test_order_error**
   - 情况：订单 ID 不存在的情况下尝试收货。
   - 操作：卖家发货，使用不存在的订单 ID 尝试收货。
   - 预期结果：收货失败，返回码不为 200。

3. **test_authorization_error**
   - 情况：使用不存在的买家 ID 尝试收货。
   - 操作：卖家发货，使用不存在的买家 ID 尝试收货。
   - 预期结果：收货失败，返回码不为 200。

4. **test_books_not_send**
   - 情况：未发货的订单尝试收货。
   - 操作：未发货的订单尝试收货。
   - 预期结果：收货失败，返回码不为 200。

5. **test_books_repeat_receive**
   - 情况：重复收货。
   - 操作：卖家发货，买家收货，再次尝试收货。
   - 预期结果：第一次收货成功，第二次收货失败，返回码不为 200。

#### 3.2.5 test_send
1. **test_ok**
   - 情况：正常发货。
   - 操作：卖家发货。
   - 预期结果：发货成功，返回码为 200。

2. **test_order_error**
   - 情况：订单 ID 不存在的情况下尝试发货。
   - 操作：使用不存在的订单 ID 尝试发货。
   - 预期结果：发货失败，返回码不为 200。

3. **test_authorization_error**
   - 情况：使用不存在的卖家 ID 尝试发货。
   - 操作：使用不存在的卖家 ID 尝试发货。
   - 预期结果：发货失败，返回码不为 200。

4. **test_books_repeat_send**
   - 情况：重复发货。
   - 操作：卖家发货，再次尝试发货。
   - 预期结果：第一次发货成功，第二次发货失败，返回码不为 200。



#### 3.2.6 test_search
在初始化 `TestSearch` 类之后，有几个具体的测试：

1. **测试图书全属性搜索**（`test_all_field_search`）
   - 调用 `buyer` 的 `search` 方法查找指定 `keyword` 的图书。
   - 调用 `json.loads` 方法解析返回的 JSON 字符串，并打印返回内容。
   - 由于 `keyword` 存在，接口逻辑正确的情况下返回的 `code` 应该为 200。
   - 因此断言 `code` 为 200，若不为 200 则测试失败，接口错误。

2. **测试图书分页搜索**（`test_pagination`）
   - 调用 `buyer` 的 `search` 方法查找指定 `keyword` 的图书。
   - 由于 `keyword` 存在，接口逻辑正确的情况下返回的 `code` 应该为 200。
   - 因此断言 `code` 为 200，若不为 200 则测试失败，接口错误。

3. **测试根据指定 title 搜索图书**（`test_search_title`）
   - 使用 `uuid` 构造一个数据库中不存在的 `title` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_title` 方法，传入的 `title` 值为之前构造的 `title`，断言 `code` 为 200。
   - 接着调用 `request_search_title` 方法，传入的 `title` 值为一个不存在的 `title`，断言 `code` 为 501（即查询失败，指定图书不存在）。

4. **测试在店铺内根据指定 title 搜索图书**（`test_search_title_in_store`）
   - 使用 `uuid` 构造一个数据库中不存在的 `title` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_title_in_store` 方法，传入的 `title` 值为之前构造的 `title`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 200。
   - 接着调用 `request_search_title_in_store` 方法，传入的 `title` 值为一个不存在的 `title`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 501（即查询失败，指定图书不存在）。

5. **测试根据指定 tag 搜索图书**（`test_search_tag`）
   - 使用 `uuid` 构造一个数据库中不存在的 `tag` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_tag` 方法，传入的 `tag` 值为之前构造的 `tag`，断言 `code` 为 200。
   - 接着调用 `request_search_tag` 方法，传入的 `tag` 值为一个不存在的 `tag`，断言 `code` 为 501（即查询失败，指定图书不存在）。

6. **测试在店铺内根据指定 tag 搜索图书**（`test_search_tag_in_store`）
   - 使用 `uuid` 构造一个数据库中不存在的 `tag` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_tag_in_store` 方法，传入的 `tag` 值为之前构造的 `tag`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 200。
   - 接着调用 `request_search_tag_in_store` 方法，传入的 `tag` 值为一个不存在的 `tag`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 501（即查询失败，指定图书不存在）。

7. **测试根据指定 content 搜索图书**（`test_search_content`）
   - 使用 `uuid` 构造一个数据库中不存在的 `content` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_content` 方法，传入的 `content` 值为之前构造的 `content`，断言 `code` 为 200。
   - 接着调用 `request_search_content` 方法，传入的 `content` 值为一个不存在的 `content`，断言 `code` 为 501（即查询失败，指定图书不存在）。

8. **测试在店铺内根据指定 content 搜索图书**（`test_search_content_in_store`）
   - 使用 `uuid` 构造一个数据库中不存在的 `content` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_content_in_store` 方法，传入的 `content` 值为之前构造的 `content`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 200。
   - 接着调用 `request_search_content_in_store` 方法，传入的 `content` 值为一个不存在的 `content`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 501（即查询失败，指定图书不存在）。

9. **测试根据指定 author 搜索图书**（`test_search_author`）
   - 使用 `uuid` 构造一个数据库中不存在的 `author` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
   - 调用 `fe.access.TestRequest` 类的 `request_search_author` 方法，传入的 `author` 值为之前构造的 `author`，断言 `code` 为 200。
   - 接着调用 `request_search_author` 方法，传入的 `author` 值为一个不存在的 `author`，断言 `code` 为 501（即查询失败，指定图书不存在）。

10. **测试在店铺内根据指定 author 搜索图书**（`test_search_author_in_store`）
    - 使用 `uuid` 构造一个数据库中不存在的 `author` 的图书，并调用 `seller` 的 `add_book` 方法加入此图书，断言 `code` 为 200。
    - 调用 `fe.access.TestRequest` 类的 `request_search_author_in_store` 方法，传入的 `author` 值为之前构造的 `author`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 200。
    - 接着调用 `request_search_author_in_store` 方法，传入的 `author` 值为一个不存在的 `author`，`store_id` 为 `seller` 的 `store_id`，断言 `code` 为 501（即查询失败，指定图书不存在）。

### 4. 遇到的主要问题展示
#### 4.1 store 的 books 插入了太多的信息以致于突破了 MongoDB 限制
最初我们的想法是一个 `store` 对应多本书，在 `store` 中存放一个 `books` 列表，列表中的每一个元素都是一本具体的书。每一个元素都包含 `book_id`、`book_info` 和 `stock_level`。但是这种设计最后的结果会出现如下报错：

> MongoDB 的默认大小为 16MB，而我们在不断往 `store` 中添加书籍的过程中超出了这个大小限制。

在这种设计下，我们最终能通过除了 `test_bench` 之外的所有测试，唯独 `test_bench` 无法通过。经过思考，我们决定将 `book_info` 字段从 `store` 当中移除。因为首先 `book_info` 就是出现上述报错的罪魁祸首，实在是太大了。但是去掉之后，我们就无法直接从 `store` 中获得书籍信息了。但这其实无伤大雅，我们想要获得书籍的具体信息只要从 `book_col` 当中寻找即可。

#### 4.2 fe/access/book.py 修改的问题
最开始我们采用的是自己修改过后的 `fe/access/book.py`，将本地的 `book.db` 导入到了本地 MongoDB 中。在修改之后，除了 `test_bench` 这个测试点以外都能 PASS。后来去看水杉上助教学长的发帖：

文档中说明所有对 SQL 的操作都要替换成对 MongoDB 的操作，这是一个错误，`fe/access/book.py` 中的 SQL 不需要更改，因为这里是读取 `book.db`（或者 `book_lx.db`）中的数据，并调用 `add_book` 函数来插入到自定义的数据库中用于测试插入数据



#### 五、版本管理

我们使用git作为版本管理的工具，团队协作的效率大大提升了。分模块地完成、优化、测试项目，分工更加明的同时也对项目的快速推进贡献了力量。这个项目的Github链接为：https://github.com/yyy53449599/bookstore

然而我们在完成实验时是在现实中聚在一起讨论的，有的同学可能完成了某模块主体的功能之后碰到了各种各样的问题，但是在一起的探讨中由其他同学发现并解决了问题，并率先地在github中提交了。我们仓库的commit和贡献情况参考性不大，这个在未来还是需要多多改进。
