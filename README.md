# REDME

# 说明

使用正向`websocket`​协议的qq机器人开发模板

# 依赖

​`pip install -r requirements.txt`​

# 快速开始

```undefined
from Meterbot import Bot,Event
#导入依赖
```

```undefined
bot = Bot("ws://localhost:5800")
event = Event(bot)
```

```undefined
@event.on_message("测试")
async def message_handler(event_structure):
    event_structure.reply("测试")
```

```undefined
if __name__ == "__main__":
    bot.run()
#运行程序
```

# 从文件夹加载

```undefined
from Meterbot import Bot,Plugin
#导入依赖
```

```undefined
bot = Bot("ws://localhost:5800")
plugin = Plugin(bot, pluginspath)
#pluginspath默认为`plugins`文件夹

plugin.load_plugin("test.py")
#或plugin.load_plugins()加载所有
```

```undefined
if __name__ == "__main__":
    bot.run()
#运行程序
```

```undefined
#test.py文件
from Meterbot import Event,_Bot

bot = _Bot._bot
event = Event(bot)

@event.on_message("测试")
async def message_handler(event_structure):
    event_structure.reply("测试")
```
在被加载文件夹的路径下，插件也可以文件夹形式存在，其中被运行的文件为main.py

示例：plugins/插件名/main.py
