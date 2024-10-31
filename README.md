**华东师范大学数据科学与工程学院实验报告** 

| **课程名称：当代数据管理系统** | **指导教师：周烜**    | **上机实践名称：** **Bookstore** |
| ------------------------------ | --------------------- | -------------------------------- |
| **姓名**：邓博昊               | **学号**：10225501432 | **年级：2022**                   |
| **姓名**：余明阳               | **学号**：10225501456 | **年级：2022**                   |
| **姓名**：左庭宇               | **学号**：10225501453 | **年级：2022**                   |

# 1.实验要求

## 功能

- 实现一个提供网上购书功能的网站后端。
- 网站支持书商在上面开商店，购买者可以通过网站购买。
- 买家和卖家都可以注册自己的账号。
- 一个卖家可以开一个或多个网上商店。
- 买家可以为自已的账户充值，在任意商店购买图书。
- 支持 下单->付款->发货->收货 流程。

**1.实现对应接口的功能，见项目的 doc 文件夹下面的 .md 文件描述 （60%）
**

其中包括：

1)用户权限接口，如注册、登录、登出、注销

2)买家用户接口，如充值、下单、付款

3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存

通过对应的功能测试，所有 test case 都 pass

**2.为项目添加其它功能 ：（40%）
**

1)实现后续的流程 ：发货 -> 收货

2)搜索图书

- 用户可以通过关键字搜索，参数化的搜索方式；
- 如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
- 如果显示结果较大，需要分页
- (使用全文索引优化查找)

3)订单状态，订单查询和取消订单

- 用户可以查自已的历史订单，用户也可以取消订单。
- 取消订单可由买家主动地取消，或者买家下单后，经过一段时间超时仍未付款，订单也会自动取消。

## bookstore目录结构

```text
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```

# 2.实验分工

- 余明阳：基础部分中buyer部分设计，拓展部分中订单部分，撰写实验报告与整合实验报告
- 左庭宇：基本部分中的卖家功能、拓展部分中收货与发货、实验报告撰写与编写test测试不同功能
- 邓博昊：基本部分中的用户部分，拓展部分中的图书搜索，实验报告撰写与整合代码和全部代码debug 

# 3.前期分析与数据库设计与前期分析

### 3.1 数据库设计

#### 3.1.1 数据库逻辑设计

![5902e98de450373369ea44427a6799b](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/5902e98de450373369ea44427a6799b.png)

#### 3.1.2 数据库结构设计

我们设计数据库的结构的逻辑主要是根据现有的sqlite代码进行改进，先观察每一个接口的功能然后进行设计，主要可以分为user,store,book,order,order_detail这五个部分，其中有两个order部分值得注意，之所以我们这么设计是因为除了查询历史订单的时候需要知道订单的详细信息，其余的时候我们不需要知道这么多的信息，只需要知道这个订单哪一笔就可以了。

所以我们的数据库的基本架构如下所示：

```text
user{
	user_id
	password
	balance
	token
	terminal
}
book{
	id
    title
    author
    content
    tags
    picture
}
store{
	store_id
	user_id
	books{
		book_id
		stock_level
	}
}
order{
	order_id
	store_id
	user_id
	status 
	price
}
order_detail{
	book_id
	order_id
	price
	count
}
```

#### 3.1.3索引优化

为了对数据库进行优化，我们想到可以对那些不怎么更改，但是需要经常查找的项建立索引，有了索引的存在就可以加快查找速度，所以我们设置了以下索引。

- store中的store_id上设置了唯一升序索引
- user中的user_id上设置了唯一升序索引
- 在books中我们设置了多个索引，分别是在title,tags,book_intro和content上，这是为了文本能在全文上进行搜索

### 3.2 前期分析

#### 3.2.1 文件树分析

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

#### 3.2.2 业务逻辑分析

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

#### 3.2.3 对比分析

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

#### 3.2.4 初次运行

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





# 4.基本功能实现

### 4.1buyer部分实现

#### 4.1.1new_order

函数输入：

- `user_id`：字符串，用于表示用户的唯一标识
- `store_id`：字符串，用于标识商店的唯一ID
- `id_and_count`：列表，包含多个元组，每个元组由书本的ID和其对应的数量组成

函数输出：

- 整数：状态码，200表示操作成功，528表示错误
- 字符串：描述操作结果的消息，可能是成功或错误信息
- 字符串：表示订单的ID

函数流程：

1. 初始化一个空字符串 `order_id`，用于后续存储订单ID
2. 进行验证，确保用户和商店的存在性，如果任一不存在，函数将返回相应的错误消息和空的订单ID
3. 生成一个独特的订单ID `uid`，该ID由用户ID、商店ID及一个基于当前时间的唯一标识符组成
4. 接下来，id_and_count列表中的每个书本ID及其数量，执行以下操作：
   - 查询商店的库存，确认书本的存在性。如果书本未找到，将返回相应的错误信息和空的订单ID
   - 检查库存量，若库存不足，返回库存不足的错误信息和空的订单ID
   - 如果库存充足，更新库存，减少相应书本的数量
   - 将书本的订单详细信息记录到订单详细信息集合，并计算订单的总价
5. 在计算完总价格后，函数获取当前时间，将订单的详细信息更新到订单集合中，包括订单ID、商店ID、用户ID、创建时间、总价格及订单状态
6. 如果所有步骤均成功，函数返回状态码200表示成功以及生成的订单ID
7. 如果在执行过程中捕获到异常，会记录相关日志，并返回528表示错误，同时附带异常信息作为错误消息，并返回空的订单ID

#### 4.1.2payment

函数输入：

- `user_id`：用户标识
- `password`：用户密码
- `order_id`：订单唯一标识

函数输出：

- 一个整数：状态码，200表示成功，528表示发生错误
- 一个字符串：操作结果的描述

函数流程：

1. 函数在订单集合中查找与给定订单ID对应的订单信息状态为是否0（未付款）。如果未找到有效的订单，将返回一个错误消息，提示无效的订单ID
2. 如果找到订单信息，则提取买家的ID、商店ID和订单的总价
3. 函数验证用户ID是否与订单的买家ID一致，如果不匹配，返回授权失败的错误消息
4. 函数继续在用户集合中查找买家的信息，确认用户存在并核对密码，如果出现错误，返回授权失败的消息
5. 查找商店信息，确保商店存在，如果找不到，将返回相应的错误消息
6. 从商店信息中提取卖家的ID，检查卖家是否存在，如果未找到，返回错误消息
7. 函数检查用户余额，如果余额不足，返回余额不足的错误消息
8. 如果余额充足，函数从买家的账户中扣除订单总价，并将该金额添加到卖家的账户中
9. 更新订单状态为1也就是已支付，并将新的订单信息插入订单集合
10. 函数尝试删除原始状态为0的订单，以确认支付成功，如果删除失败，将返回无效订单ID的错误消息
11. 如果在执行过程中发生任何异常，返回状态码528

#### 4.1.3add_funds

函数输入：

- `user_id`：用户标识
- `password`：用户密码
- `add_value`：增加到账户余额的金额

函数输出：

- 一个整数：状态码，200表示成功，528表示发生错误
- 一个字符串：描述操作结果的消息

函数流程：

1. 函数在用户集合中查找与给定用户ID对应的用户信息，如果未找到，返回授权失败的错误消息
2. 如果找到信息，函数将验证输入的密码是否与密码一致，如果不匹配，返回授权失败的错误提示
3. 函数使用 `$inc` 操作符更新用户账户余额，将 `add_value` 添加到当前余额
4. 函数检查是否成功更新了用户信息，如果没有匹配到用户，将返回用户不存在的错误消息
5. 如果在执行过程中发生任何异常，函数将捕获并返回状态码528

### 4.2seller部分实现

#### 4.2.1创建商铺

函数输入：

user_id：卖家用户ID

store_id：商铺ID

函数功能解释：

1.检查给定的 `user_id` 是否存在。如果不存在，返回一个错误，表示用户 ID 不存在。

2.检查给定的 `store_id` 是否存在。如果不存在，返回一个错误，表示商店 ID 不存在。

3.使用  `insert_one` 方法来创建新商店。商店的基本信息：`store_id`: 新商店的唯一标识符。`user_id`: 关联的用户 ID。`"books": []`: 初始化一个空的书籍列表，表示该商店当前没有任何书籍。

4.如果在执行数据库操作时发生 `sqlite.Error` 异常，返回错误代码 `528` 和错误信息。如果发生其他类型的异常，返回错误代码 `530` 和错误信息。

5.如果所有操作成功完成，返回状态码 `200` 和消息 `"ok"`，表示操作成功。

#### 4.2.2添加书籍信息

函数输入：

user_id：卖家用户ID

store_id：商铺ID

book_id：书籍ID

book_json_str：表示包含书籍信息的 JSON 字符串。 

stock_level：库存

函数功能解释：

1.检查给定的 `user_id` 是否存在。如果不存在，返回一个错误，表示用户 ID 不存在。

2.检查给定的 `store_id` 是否存在。如果不存在，返回一个错误，表示商店 ID 不存在。

3.检查给定的 `book_id` 是否存在。如果存在，返回一个错误，表示书籍 ID 存在。

4.将书籍信息添加到指定的商店中。使用 `$push` 操作符将书籍 ID 和库存数量添加到商店的 `books` 列表中。

5.将书籍的详细信息（JSON 字符串）插入到 `col_book` 集合中。使用 `json.loads` 将 JSON 字符串转换为 Python 字典格式。

6.如果在执行数据库操作时发生 `sqlite.Error` 异常，返回错误代码 `528` 和错误信息。如果发生其他类型的异常，返回错误代码 `530` 和错误信息。

7.如果所有操作成功完成，返回状态码 `200` 和消息 `"ok"`，表示操作成功。

#### 4.2.3添加书籍库存

函数输入：

user_id：卖家用户ID

store_id：商铺ID

book_id：书籍ID 

add_stock_level：增加的库存量

函数功能解释：

1.检查给定的 `user_id` 是否存在。如果不存在，返回一个错误，表示用户 ID 不存在。

2.检查给定的 `store_id` 是否存在。如果不存在，返回一个错误，表示商店 ID 不存在。

3.检查给定的 `book_id` 是否存在。如果不存在，返回一个错误，表示书籍 ID 不存在。

4.找到特定商店中指定书籍的记录，并将找到的书籍的库存水平增加指定的数量。

5.如果在执行数据库操作时发生 `sqlite.Error` 异常，返回错误代码 `528` 和错误信息。如果发生其他类型的异常，返回错误代码 `530` 和错误信息。

6.如果所有操作成功完成，返回状态码 `200` 和消息 `"ok"`，表示操作成功。

### 4.3user部分实现

#### 修改后端`model/user.py`

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

##### 4.3.1注册

原函数

![image-20241026184623082](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026184623082.png)

将其简单更改为`MongoDB`形式即可（注意，此时`store.py`还未修改，`self.conn`连接的是SQLite数据库，注意后续修改数据库连接）

![image-20241026220942862](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026220942862.png)

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



#####  4.3.2登录

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

#####  4.3.3登出

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

原函数

![image-20241026221601403](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221601403.png)

修改为

![image-20241026221642700](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221642700.png)



注意，调用了`check_token`函数

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

原函数

**![image-20241026221729998](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20241026221729998.png)**

修改为

##### 4.3.4注销

原函数

![image-20241026221905600](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221905600.png)

修改为

![image-20241026221925214](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026221925214.png)



`check_password`函数已经修改，直接跳过



##### 4.3.5改密

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



原函数

![image-20241026222216893](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222216893.png)

修改为

![image-20241026222237212](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222237212.png)



#### 修改后端`model/store.py`

原有`store.py`关联的是SQLite数据库

##### 被调用链

1. `be/model/`中的类初始化时

​	调用`db_conn.DBConn`的初始化函数

![image-20241026222717814](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026222717814.png)

2. `be/model/db_conn.DBConn`初始化时

   调用`store.get_db_conn()`函数

3. `store.get_db_conn()`调用`database_instance.get_db_conn()`函数
   `database_instance`为`Store`类的一个实例

   

![image-20241026223137663](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026223137663.png)

![image-20241026223208964](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241026223208964.png)

##### 修改方向

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

#### 再次运行

注意将`fe/conf.py`里的`Use_Large_DB = True`改为False

因为是本地测试，还未用助教所提的超大数据库

运行结果如下

![image-20241027025601617](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241027025601617.png)

# 5.附加功能

### 5.1收货发货

#### 5.1.1发货

函数输入：

user_id：卖家用户ID

order_id：订单ID

函数功能解释：

1.使用 `$or` 操作符查找具有指定 `order_id` 并且状态为 `1`、`2` 或 `3` 的订单。`find_one` 方法用于查找符合条件的第一条记录，并将结果存储在 `result` 变量中。

2.如果查询结果为 `None`，表示没有找到符合条件的订单，函数会返回一个错误，表示示订单 ID 无效。

3.从查询结果中获取订单的状态。如果状态为 `2`（已交付）或 `3`（已完成），则返回一个错误，指示该订单已经被交付或完成，不能重复交付。

4.如果订单状态有效且可以交付，则使用 `update_one` 方法将订单的状态更新为 `2`（表示已交付）。

5.如果在执行数据库操作时发生 `sqlite.Error` 异常，返回错误代码 `528` 和错误信息。如果发生其他类型的异常，返回错误代码 `530` 和错误信息。

6.如果所有操作成功完成，返回状态码 `200` 和消息 `"ok"`，表示操作成功。

#### 5.1.2收货

函数输入：

user_id：卖家用户ID

store_id：商铺ID

book_id：书籍ID 

add_stock_level：增加的库存量

函数功能解释：

1.使用 `$or` 操作符查找具有指定 `order_id` 并且状态为 `1`、`2` 或 `3` 的订单。`find_one` 方法用于查找符合条件的第一条记录，并将结果存储在 `result` 变量中。

2.如果查询结果为 `None`，表示没有找到符合条件的订单，函数会返回一个错误，表示示订单 ID 无效。

3.从查询结果中提取买家的用户 ID 和订单状态。

4.检查请求的用户 ID 是否与订单的买家 ID 匹配。如果不匹配，返回授权失败的错误信息。

5.如果订单状态为 1，表示书籍尚未发货，返回相应的错误信息。如果订单状态为 3，表示书籍已经被重复接收，返回相应的错误信息。

6.如果以上检查都通过，更新订单状态为 3（已接收）。

7.如果在执行数据库操作时发生 `sqlite.Error` 异常，返回错误代码 `528` 和错误信息。如果发生其他类型的异常，返回错误代码 `530` 和错误信息。

8.如果所有操作成功完成，返回状态码 `200` 和消息 `"ok"`，表示操作成功。

#### 5.1.3发货测试

1.test_ok 发货成功

操作：卖家发货。 

预期结果：发货成功，返回码为200。 

2.test_order_error 订单不存在

操作：使用不存在的订单ID尝试发货。 

预期结果：发货失败，返回码不为200。 

3.test_books_repeat_deliver 重复发货

操作：卖家发货两次。 

预期结果：第一次发货成功，第二次发货失败，返回码不为200。

#### 5.1.4收货测试

1.test_ok 收货成功

操作：卖家发货，买家收货。 

预期结果：收货成功，返回码为200。 

2.test_order_error  订单不存在 

操作：卖家发货，使用不存在的订单ID尝试收货。 

预期结果：收货失败，返回码不为200。 

3.test_authorization_error 买家不存在 

操作：卖家发货，使用不存在的买家ID尝试收货。 

预期结果：收货失败，返回码不为200。

4.test_books_not_deliver  未发货 

操作：未发货的订单尝试收货。 

预期结果：收货失败，返回码不为200。 

5.test_books_repeat_receive 重复收货 

操作：卖家发货，买家收货两次。 

预期结果：第一次收货成功，第二次收货失败，返回码不为200。

#### 5.1.5前后端接口

be/view/seller.py

be/view/buyer.py

fe/access/seller.py

fe/access/buyer.py

这个几个文件都新增一个函数，就照着之前的写，改几个变量就好了。

#### 5.1.6error

新增三个对应发货和收获的错误

```
520: "books not deliver.",
521: "books deliver repeatedly.",
522: "books receive repeatedly.",
```

### 5.2搜索图书

根据前文业务流程分析依次需要实现的

* 添加`fe/test/search.py`
* 添加`fe/access/search.py`
* 添加`be/view/search.py`(记得在serve.py里注册蓝图)
* 添加`be/model/book.py`

#### 5.2.1

我们在 `buyer` 类中实现了一个基本的 `search` 方法，接受以下四个参数：

- `keyword`：搜索的关键字。
- `store_id`：商店的ID，用于限制搜索结果至特定商店。
- `page`：页码，默认为1，用于分页显示结果。
- `per_page`：每页显示的书籍数量，默认为10。

该方法的返回值是一个tuple，包含两个部分：

- 一个整数：状态码，200表示成功，530表示出现错误。
- 一个列表：包含搜索到的书籍信息。

方法的主要流程如下：

1. 首先，构建一个基础查询 `base_query`，利用MongoDB的 `$text` 操作符进行全文搜索，关键字为 `keyword`。
2. 随后，创建一个查询 `query`，初始值设为 `base_query`。
3. 如果提供了 store_id，则进行以下操作：
   - 在商店集合中查找与 `store_id` 匹配的书籍ID，并将其存入列表 `books_id`。
   - 更新查询条件，要求书籍的ID必须包含在 `books_id` 列表中。
4. 执行查询，寻找符合条件的书籍，同时使用 `$meta` 获取文本分数，以便后续排序。
5. 进行分页处理，跳过前 `(page - 1) * per_page` 个结果，并限制结果数量为 `per_page` 条。
6. 如果在处理过程中发生异常，捕获并返回状态码530以及异常信息作为错误提示。
7. 最终，返回状态码200和包含搜索结果的书籍信息列表。

然而，经过进一步的思考，我们发现这种实现方式存在一些局限性。首先，卖家同样作为用户，理应具备搜索书籍的能力。此外，原有设计较为基础，未能充分满足实验所需的各项功能。因此，我们决定在 `be/model` 目录中引入一套更为灵活和全面的查找逻辑，并将其移至 `book.py` 文件中，以提升搜索功能的扩展性和用户体验。

##### 5.2.2搜索指定标题的图书

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

### `search_title` 的运行逻辑：

1. 在 `books` 集合中，使用 `find` 方法查询符合指定标题的图书，条件为 `title` 字段等于用户通过 HTTP 请求传递的参数 `title`。
2. 由于 `_id` 字段对业务逻辑没有影响，且用户不需要此字段，因此在查询中指定 `_id: 0`，表示在结果中排除 `_id` 字段。
3. 对查询结果进行分页处理，使用前端通过 HTTP 请求传递的 `page_size` 和 `page_num` 参数，分别表示每页显示的记录数和当前页号。
4. 将查询结果转换为列表，并检查其长度：
   - 如果结果长度为 0，表示没有找到指定标题的图书，返回状态码 501 及错误信息（“指定标题的图书不存在”），并返回一个空列表。
   - 如果结果长度不为 0，说明找到了对应的图书，返回状态码 200、消息 “ok” 以及对应的图书列表。

### `search_title_in_store` 的补充逻辑：

1. 在分页处理后、将查询结果转换为列表之前，需要检查结果集中每本图书是否在指定的 `store_id` 店铺中。
2. 将结果集中每本图书的 ID 作为查询条件，检查 store集合中的 books 数组，确认是否包含指定的 book_id：
   - 如果找到指定的 `book_id`，则表明该书籍属于指定的店铺，将其加入到返回的结果列表中。
   - 如果未找到，则表示该书籍不在指定店铺中，将其从结果集中排除。

### 整体逻辑总结：

通过以上逻辑，`search_title` 方法能够有效地根据用户提供的标题进行书籍搜索，并结合店铺信息实现更精细化的结果过滤。这种设计不仅提高了用户体验，也增强了系统的灵活性与适应性。





##### 5.2.2 搜索指定标签的图书

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

##### 5.2.3搜索指定内容的图书

```python
def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "$text": {"$search": content}
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

search_content 的运行逻辑：

1. 在 `books` 集合中查询包含指定 `content` 的图书，使用 `find` 方法结合全文索引进行搜索，要求图书的 `book_intro` 或 `content` 字段包含用户指定的 `content` 值。
2. 由于 `_id` 字段对业务逻辑无关紧要且用户不需要此字段，因此在查询中指定 `_id: 0`，表示从结果中排除 `_id` 字段。
3. 对查询结果进行分页处理，使用前端通过 HTTP 请求传递的 `page_size` 和 `page_num` 参数，分别表示每页的记录数和当前页号。
4. 将查询结果转换为列表，并检查其长度：
   - 如果结果长度为 0，表示没有满足条件的图书，返回状态码 501 及错误信息（“指定内容的图书不存在”），并返回一个空列表。
   - 如果结果长度不为 0，说明找到了符合条件的图书，返回状态码 200、消息 “ok” 以及相应的图书列表。

search_content_in_store 的补充逻辑：

1. 在分页处理后、将查询结果转换为列表之前，需要检查每本图书是否在指定的 `store_id` 店铺中。
2. 将结果集中每本图书的 ID 作为查询条件，检查 store集合中的 books数组，确认是否包含指定的 book_id：
   - 如果找到指定的 `book_id`，则表明该书籍属于指定的店铺，将其加入到返回的结果列表中。
   - 如果未找到，则表示该书籍不在指定店铺中，将其从结果集中排除。

### 整体逻辑总结：

通过这些步骤，`search_content` 方法能够高效地根据用户提供的内容进行书籍搜索，并与店铺信息相结合，以实现更精确的结果过滤。这种设计增强了用户体验，并提升了系统的灵活性与适应性。



##### 5.2.3 搜索指定作者的图书

```python
def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
    book = self.conn.book_col
    condition = {
        "author": author
    }
    result = book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
    result_list = list(result)
```

search_author 的运行逻辑：

1. 在 `books` 集合中查询包含指定 `author` 的图书，调用 `find` 方法，条件为 `author` 字段等于用户通过 HTTP 请求传递的 `author` 参数。
2. 因为 `_id` 字段对业务逻辑没有影响，且用户不需要此字段，所以在查询中指定 `_id: 0`，以排除该字段。
3. 对查询结果进行分页处理，使用前端通过 HTTP 请求传递的 `page_size` 和 `page_num` 参数，分别表示每页的记录数和当前页号。
4. 将查询结果转换为列表，并检查其长度：
   - 如果结果长度为 0，表示没有找到满足条件的图书，返回状态码 501 及错误信息（“指定作者的图书不存在”），并返回一个空列表。
   - 如果结果长度不为 0，说明找到了符合条件的图书，返回状态码 200、消息 “ok” 以及对应的图书列表。



search_author_in_store 的补充逻辑：在分页处理后、将查询结果转换为列表之前，需要检查每本图书是否在指定的 `store_id` 店铺中。

1. 将结果集中每本图书的 ID 作为查询条件，检查 store集合中的 books数组，确认是否包含指定的 book_id：
   - 如果找到指定的 `book_id`，则表明该书籍属于指定的店铺，将其加入到返回的结果列表中。
   - 如果未找到，则表示该书籍不在指定店铺中，将其从结果集中排除。

整体逻辑总结：

可以看出，`search_author` 和 `search_author_in_store` 的逻辑非常相似，主要在于查询的范围和条件有所不同。为了提高代码的可重用性和维护性，理想情况下，我们可以将这些相似的逻辑提取到一个通用的函数中，以实现批处理操作。然而，由于时间限制，虽然我们在实现上没有进一步的封装，但现有的测试用例通过情况良好，这在一定程度上减轻了我们对未进一步优化的遗憾。未来的改进可能会集中在重构这些重复代码，以提升整体代码质量。

### 5.3 订单状态以及查询

#### 5.3.1check_hist_order

函数输入：

- `user_id`：用户标识

函数输出：

在内部创建一个包含历史订单信息的列表 `ans`，并在最后返回该列表

函数流程：

1. 检查用户是否存在。如果用户不存在，将返回一个错误消息，提示无效的用户ID
2. 如果存在，初始化一个空列表 `ans`，用于存储历史订单
3. 查询不同状态的订单，依次处理：
   - 查找未付款的订单，并将这些订单的信息添加到 `ans` 列表
   - 查找已支付但尚未发货、已支付但未收到和已收到的订单，并将相关信息也添加到 `ans` 列表
   - 查找已取消的订单，并将这些信息加入 `ans` 列表
4. 对于每种订单状态，执行以下操作：
   - 查询与用户ID和相应订单状态匹配的订单信息
   - 针对每个订单，获取与其相关的书籍详细信息
   - 为每个订单创建一个字典，包含状态、订单ID、买家ID、商店ID、总价及书籍详细信息，并将该字典添加到 `ans` 列表中
5. 在处理完所有状态后，检查 ans列表：
   - 如果列表为空，返回一条成功消息，指示没有找到任何历史订单
   - 如果列表非空，返回成功消息，并附上包含历史订单信息的 `ans` 列表
6. 如果在以上过程中发生任何异常，函数将捕获并返回状态码528

#### 5.3.2cancel_order

函数输入：

- `user_id`：用户标识
- `order_id`：订单标识

函数输出：

- 一个整数：状态码，200表示成功，528表示发生错误
- 一个字符串：描述操作结果的消息

函数流程：

1. 函数在订单集合中查找状态为0的订单，使用给定的订单ID，如果找到匹配的订单，提取买家ID、商店ID和订单价格，然后从订单集合中删除该订单
2. 如果未能找到未付款的订单，函数将使用 $or操作符查找状态为1、2或3的订单。如果找到相应订单，提取买家ID、商店ID和订单价格，并执行以下操作：
   - 验证买家ID是否与输入的用户ID匹配，以确保用户有权取消订单。如果不匹配，返回授权失败的错误消息
   - 提取卖家ID，从卖家的账户中扣除订单价格，同时将相同金额返还到买家的账户
   - 删除匹配的订单记录
3. 如果在上述步骤中未找到任何适用的订单，返回无效订单ID的错误消息
4. 查询订单详细信息集合，获取与该订单相关的已购书籍信息。遍历书籍信息，恢复库存，增加相应的库存数量
5. 创建一个新订单，状态设置为4，包括订单ID、用户ID、商店ID和订单价格，并将其插入到订单集合中
6. 如果在执行过程中发生任何异常，函数会捕获并返回状态码528

#### 5.3.3auto_cancel_order

函数输入：

该函数不接受任何参数，

函数输出：

- 一个整数：状态码，200表示成功，528表示发生错误
- 一个字符串：描述操作结果的消息

函数流程：

1. 定义一个等待时间 `wait_time`，设置为20秒，用于判断未支付订单的自动取消时限
2. 获取当前的UTC时间 `now`，计算出一个时间点 `interval`，表示当前时间减去 `wait_time` 秒后的时间
3. 构建查询条件 `cursor`，用于查找未支付（状态为0）且创建时间早于 `interval` 的订单
4. 将待取消的订单信息存储在 `orders_to_cancel` 中
5. 如果找到待取消的订单，遍历这些订单并执行以下操作：
   - 提取每个订单的相关信息，包括订单ID、用户ID、商店ID和订单价格
   - 从订单集合中删除该订单，以实现订单取消
   - 查询已取消订单的书籍详细信息，并遍历这些书籍
   - 对每本书籍，恢复库存，增加相应数量
   - 如果库存恢复失败（`update_result.modified_count == 0`），返回库存不足的错误消息
6. 对于每个成功取消的订单，函数创建一个新的订单文档 `canceled_order`，将状态设置已取消，然后将其插入到订单集合中
7. 如果在执行过程中发生任何异常，函数将捕获异常并返回状态码528

#### 5.3.4is_order_cancelled

函数输入：

- `self`：类实例的引用
- `order_id`：要检查的订单的唯一标识

函数输出：

- 一个整数：状态码，200表示成功，其他状态码表示不同的错误情况
- 一个字符串：描述操作结果的消息

函数流程：

1. 首先，在订单集合中查询，查找订单ID等于给定的 `order_id` 且已取消的订单
2. 如果找到符合条件的订单，说明该订单已被取消返回状态码200
3. 如果未找到符合条件的订单，返回错误消息

# 6.版本控制

我们使用git作为版本管理的工具，团队协作的效率大大提升了。分模块地完成、优化、测试项目，分工更加明的同时也对项目的快速推进贡献了力量。这个项目的Github链接为：https://github.com/yyy53449599/bookstore

然而我们在完成实验时是在现实中聚在一起讨论的，有的同学可能完成了某模块主体的功能之后碰到了各种各样的问题，但是在一起的探讨中由其他同学发现并解决了问题，并率先地在github中提交了。我们仓库的commit和贡献情况参考性不大，这个在未来还是需要多多改进。

### 6.1 分支

通过各自维护不同分支，实现分布式开发

![image-20241031215308242](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031215308242.png)

### 6.2 PR

通过PR，将不同分支合并至`main`分支，完成最终代码

![image-20241031215425279](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031215425279.png)

在PR内简单标注更改内容，可以简洁明了知晓各自更改的部分

![3002af8d1d5dc3122f34e18140eb3fc](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/3002af8d1d5dc3122f34e18140eb3fc.png)

# 7.运行测试结果

实现基础功能+额外功能后，进行测试

#### 7.1 小数据库`book.db`

最终HTML 覆盖率报告储存在`results/book_db`中

![image-20241031190725300](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031190725300.png)

#### 7.2 大数据库`booklx.db`

最终HTML 覆盖率报告储存在`results/book_lx_db`中

详细终端输出将`results/console.log`

![image-20241031191831366](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031191831366.png)

![image-20241031191844575](https://aquaoh.oss-cn-shanghai.aliyuncs.com/post/image-20241031191844575.png)
