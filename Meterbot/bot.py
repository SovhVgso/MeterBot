import asyncio
import websockets
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
# 设置日志格式和级别
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个按天分割的日志处理器
log_file_path = os.path.join(log_dir, 'bot.log')
log_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=7, encoding='utf8')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

class Bot:
    def __init__(self, ws_url) -> None:
        self.ws_url = ws_url
        self.decorators = []
        self.message_queue = asyncio.Queue()
        self.status = asyncio.Queue()
        self.logger = logger
    
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.ws_listen())
        finally:
            loop.close()

    async def ws_listen(self):
        self.logger.info(f"Connecting to {self.ws_url}")
        async with websockets.connect(self.ws_url) as self.websocket:
            receiver = asyncio.create_task(self.receive_message())
            processor = asyncio.create_task(self.process_message())
            await asyncio.gather(receiver, processor)

    async def receive_message(self):
        while True:
            try:
                data = json.loads(await self.websocket.recv())
                if "post_type" in data.keys():
                    self.logger.info(f"Received message: {data}")
                    await self.message_queue.put(data)
                else:
                    await self.status.put(data)
            except websockets.ConnectionClosed:
                self.logger.error("WebSocket connection closed unexpectedly.")
                break

    async def process_message(self):
        while True:
            data = await self.message_queue.get()
            if self.decorators:
                event_structure = handle_event(data,self.all_action)
                asyncio.create_task(self.handle_message(event_structure))
            self.message_queue.task_done()

    # async def event_structure(self,msgdata):
    #     handle_event = handle_event(msgdata,self.all_action)

    async def handle_message(self, event_structure: object) -> None:
        tasks = [asyncio.create_task(decorator(event_structure)) for decorator in self.decorators]
        # self.logger.info(f"Scheduled tasks: {tasks}")
        await asyncio.wait(tasks)

    async def all_action(self, head):
        self.logger.info(f"Sending action: {head}")
        await self.websocket.send(json.dumps(head))
        result_data = await self.status.get()
        self.logger.info(f"Received status: {result_data}")
        return result_data
    
    async def get_credentials(self, domain=None):
        head =  {
            "action": "get_credentials",
            "params": {
                "domain": domain
            }
        }
        return await self.all_action(head)

    def register_decorator(self, decorator):
        self.decorators.append(decorator)
        self.logger.info(f"Registered decorator: {decorator}")

    def deregister_decorator(self, decorator):
        if decorator in self.decorators:
            self.decorators.remove(decorator)
            self.logger.info(f"Deregistered decorator: {decorator}")
        else:
            self.logger.warning(f"Tried to deregister non-existent decorator: {decorator}")

    def event_list(self):
        return self.decorators

class handle_event:
    def __init__(self, msgdata, all_action):
        self.msgdata = msgdata
        self.all_action = all_action

    async def reply(self, reply_message, message_type="text", reply_at=False):
        data = self.msgdata
        head =  {
            "action": "send_msg",
            "params": {
                "message_type": data["message_type"],
                "group_id": data.get("group_id", None),
                "user_id": data.get("user_id", None),
                "discuss_id": data.get("discuss_id", None),
                "message": None
            }
        }

        # Construct the message based on the type
        if isinstance(reply_message, (list, dict)):
            head["params"]["message"] = reply_message
        else:
            head["params"]["message"] = {
                "type": message_type,
                "data": {
                    "text": reply_message if message_type == "text" else reply_message
                }
            }
        
        if reply_at:
            head["params"]["message"] = [
                {"type": "at", "data": {"qq": data.get("user_id", None)}},
                head["params"]["message"]
            ]
        
        result_data = await self.all_action(head)
        return result_data

class _Bot:
    _bot = None