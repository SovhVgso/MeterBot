from Meterbot import pictob64,dbapi

#将图片直链转为base64
base64 = pictob64.url_to_64("pic_url")
#将图片转为base64
base64 = pictob64.image_to_64("pic_path")

#database是一个集成后的sql3数据库类
sql_path = "db.sqlite"
db = dbapi(sql_path)#实例化数据库类
data = db.select("tb1",{'id': 1})#从tb1表中读取id为1的数据
db.insert('tb1', data, ['id'], "user_id = EXCLUDED.user_id")#从tb1表中写入data数据条目，如果已存在则默认更新，第三个参数必须具有唯一性
db.disconnect()