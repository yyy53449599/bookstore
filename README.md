# 数据库大作业

## 一、前期分析

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

:: 设置当前目录为 PYTHONPATH
set PYTHONPATH=%cd%

:: 运行 coverage，并指定路径和参数
coverage run --timid --branch --source=fe,be --concurrency=thread -m pytest -v --ignore=fe\data

:: 合并覆盖率数据
coverage combine

:: 生成覆盖率报告
coverage report

:: 生成 HTML 覆盖率报告
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
6. 创建关于图书标题，标签，简洁，内容的索引

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
