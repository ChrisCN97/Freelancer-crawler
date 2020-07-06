"""import pymysql

# 打开数据库连接
db = pymysql.connect("localhost", "root", "19971002", "freelancer")

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询
cursor.execute("SELECT LAST_INSERT_ID()")

print(cursor.fetchall())

# 关闭数据库连接
db.close()"""

for i in range(2,3):
    print(i)