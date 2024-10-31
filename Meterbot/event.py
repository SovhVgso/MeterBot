import asyncio
import re

class Event():
    def __init__(self,Bot) -> None:
        self.Bot = Bot
        self.determine = event_determine(Bot)
        if Bot == None:
            print("错误")
    
    def register_decorator(self, decorator):
            self.Bot.register_decorator(decorator)
    
    def on_message(self, message, position=-1, msg_at=False):
        def inner(func):
            func_address = self.determine.is_message(func, message, position, msg_at)
            self.register_decorator(func_address)
            return func_address
        return inner
    
    def key_message(self, message, position=-1, msg_at=False):
        def inner(func):
            func_address = self.determine.in_message(func, message, position, msg_at)
            self.register_decorator(func_address)
            return func_address
        return inner
    
    def re_message(self, message, position=-1, msg_at=False):
        def inner(func):
            func_address = self.determine.match_message(func, message, position, msg_at)
            self.register_decorator(func_address)
            return func_address
        return inner
    
    def type_message(self, message, msg_at=False):
        def inner(func):
            func_address = self.determine.mtype_message(func, message)
            self.register_decorator(func_address)
            return func_address
        return inner

    #临时消息注册，可以将消息事件临时注册在函数注册列表中等待响应，如果在给定时间内注册函数得到得到响应则返回true，否则返回false
    async def temp_register_message(self,decorator,timeout: int=0,func=None, func_args:dict=None,deregister: bool=True,temp_data=None):
        @decorator
        async def message_handler(msg_data):
            if not temp_data or (temp_data['user_id'] != msg_data['user_id'] and temp_data):
                global return_result
                return_result = None
                if func is not None:
                    if func_args:
                        return_result = await func(**func_args)
                    else:
                        return_result = await func()
                if not return_result:
                    return_result = True
                if deregister:
                    self.Bot.deregister_decorator(message_handler)
        for i in range(timeout*10):
            if message_handler not in self.event_list():
                return return_result
            await asyncio.sleep(0.1)
        self.Bot.deregister_decorator(message_handler)
        return False       
        
    def reply(self, decorator,reply_message,message_type="text",msg_at=False,reply_at=False):
        async def func(data):
            if message_type=="text":
                msg_data = {
                        "text":reply_message
                    }
            elif message_type=="image":
                msg_data = {
                        "file": reply_message
                    }
            elif message_type=="video":
                msg_data = {
                        "file": reply_message
                    }
            elif message_type=="json":
                msg_data = {
                        "data": reply_message
                    }
            elif message_type=="at":
                msg_data = {
                        "qq": reply_message
                    }
            msg  = {
                "type": message_type,
                "data": msg_data}
            if reply_at:
                at_info =  [{"type": "at","data": {"qq": data.get("user_id", None)}}]
                at_info.append(msg)
                msg = at_info
            head =  {
        "action": "send_msg",
        "params": {
        "message_type": data["message_type"],
        "group_id":data.get("group_id", None),
        "user_id":data.get("user_id", None),
        "discuss_id":data.get("discuss_id", None),
        "message":msg}
                    }
            await self.Bot.all_action(head)
        if type(decorator) == str:
            func_address = self.determine.is_message(func, decorator, position=-2,msg_at=msg_at)
            self.register_decorator(func_address)
        else:
            @decorator
            async def message_handler(data):
                await func(data)

    def all_event(self,func):
        func_address = self.determine.is_event(func)
        self.register_decorator(func_address)
        return func_address

    def event_list(self):
        return self.Bot.decorators

class event_determine(): 
    def __init__(self,Bot) -> None:
        self.Bot = Bot
    
    def mtype_message(self, func, message):
        def wrapper(event_structure):
            data = event_structure.msgdata
            if data.get("post_type") != "message":
                return self.type_skip()
            messages = data.get("message", [])
            if messages == message:
                return func(event_structure)
            return self.type_skip()
        return wrapper

    def is_message(self, func, message, position, msg_at):
        def wrapper(event_structure):
            data = event_structure.msgdata
            if data.get("post_type") != "message":
                return self.type_skip()
            messages = data.get("message", [])
            # if msg_at and not any((msg.get("type") == "at" and int(msg.get("data").get("qq")) == data.get("self_id")) for msg in messages):
            #     return self.type_skip()
            if msg_at:
                at_info = False
                for msg in messages:
                    if msg.get("type") == "at" and int(msg.get("data").get("qq")) == data.get("self_id"):
                        messages.remove(msg)
                        at_info = True
                        break
                if not at_info:
                    return self.type_skip()
            if position == -1:
                if any(msg.get("type") == "text" and msg.get("data", {}).get("text") == message for msg in messages):
                    return func(event_structure)
                return self.type_skip()
            if (position <= -2 and len(messages) == 1 and 
                messages[0].get("type") == "text" and 
                messages[0].get("data", {}).get("text") == message):
                return func(event_structure)
            if (0 <= position < len(messages) and 
                messages[position].get("type") == "text" and 
                messages[position].get("data", {}).get("text") == message):
                return func(event_structure)
            return self.type_skip()
        return wrapper

    def in_message(self, func, message, position, msg_at):
        def wrapper(event_structure):
            data = event_structure.msgdata
            if data.get("post_type") != "message":
                return self.type_skip()
            messages = data.get("message", [])
            if msg_at:
                at_info = False
                for msg in messages:
                    if msg.get("type") == "at" and int(msg.get("data").get("qq")) == data.get("self_id"):
                        messages.remove(msg)
                        at_info = True
                        break
                if not at_info:
                    return self.type_skip()
            if position == -1:
                for msg in messages:
                    if msg.get("type") == "text" and message in msg.get("data", {}).get("text", ""):
                        return func(event_structure)
                return self.type_skip()
            if (position <= -2 and len(messages) == 1 and 
                messages[0].get("type") == "text" and 
                message in messages[0].get("data", {}).get("text", "")):
                return func(event_structure)  
            if (0 <= position < len(messages) and 
                messages[position].get("type") == "text" and 
                message in messages[position].get("data", {}).get("text", "")):
                return func(event_structure)
            return self.type_skip()
        return wrapper
    
    def match_message(self, func, message, position, msg_at):
        def wrapper(event_structure):
            data = event_structure.msgdata
            if data.get("post_type") != "message":
                return self.type_skip()
            messages = data.get("message", [])
            if msg_at:
                at_info = False
                for msg in messages:
                    if msg.get("type") == "at" and int(msg.get("data").get("qq")) == data.get("self_id"):
                        messages.remove(msg)
                        at_info = True
                        break
                if not at_info:
                    return self.type_skip()
            if position == -1:
                for msg in messages:
                    if msg.get("type") == "text":
                        match_msg = re.search(message, msg.get("data", {}).get("text", ""))
                        if match_msg:
                            data["match_msg"] = match_msg.group()
                            data["match_groups"] = match_msg.groups()
                            event_structure.msgdata=data
                            return func(event_structure)
                return self.type_skip()
            if (position <= -2 and len(messages) == 1 and 
                messages[0].get("type") == "text"):
                match_msg = re.search(message, messages[0].get("data", {}).get("text", ""))
                if match_msg:
                    data["match_msg"] = match_msg.group()
                    data["match_groups"] = match_msg.groups()
                    event_structure.msgdata=data
                    return func(event_structure)
                return self.type_skip()
            if (0 <= position < len(messages) and 
                messages[position].get("type") == "text"):
                match_msg = re.search(message, messages[position].get("data", {}).get("text", ""))
                if match_msg:
                    data["match_msg"] = match_msg.group()
                    data["match_groups"] = match_msg.groups()
                    event_structure.msgdata=data
                    return func(event_structure)
                return self.type_skip()
            return self.type_skip()
        return wrapper

    def is_event(self,func):
        def wrapper(event_structure):
            return func(event_structure)
        return wrapper
    
    async def type_skip(self):
        pass
