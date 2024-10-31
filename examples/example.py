from Meterbot import Event,_Bot

bot = _Bot._bot
event = Event(bot)

#固定回复
@event.on_message(r'测试')
async def message_handler(event_structure):
    event_structure.reply("测试")

#关键词检测
@event.key_message(r'测试')
async def message_handler(event_structure):
    event_structure.reply("测试")

#使用正则表达式匹配
@event.re_message(r'测试(.*)')
async def message_handler(event_structure):
    data = event_structure.msgdata
    event_structure.reply(data["match_msg"])#回复测试加后面的任意匹配内容
    event_structure.reply(data["match_groups"])#回复所有被匹配到的组

#延时回复
@event.on_message(r'测试')
async def message_handler(event_structure):
    async def abc():
        await event_structure.reply(event_structure.msgdata)
    a =  await event.temp_register_message(event.on_message("123"),5,abc)#在五秒内回复123，则执行函数abc并返回True，如果函数abc有返回值，则返回该返回值，否则返回False
    print(a)

#使用自定义action
@event.on_message(r'测试')
async def message_handler(event_structure):
    data = event_structure.msgdata
    head =  {
            "action": "send_msg",
            "params": {
                "message_type": data["message_type"],
                "group_id": data.get("group_id", None),
                "user_id": data.get("user_id", None),
                "discuss_id": data.get("discuss_id", None),
                "message": "测试"
            }
        }
    await bot.all_action(head)